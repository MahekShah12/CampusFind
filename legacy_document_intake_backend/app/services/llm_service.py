import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app import config
from app.models.llm import (
    LLMResponse,
    ExtractedInformation,
    ExtractedExecutor
)
from app.services.validator import validate_llm_response


logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    pass


class LLMConfigurationError(LLMServiceError):
    pass


class LLMProviderError(LLMServiceError):
    pass


class LLMResponseError(LLMServiceError):
    pass


class LLMService(ABC):

    @abstractmethod
    def process_message(
        self,
        message: str,
        current_state: dict,
        conversation_history: list,
        current_field: Optional[str] = None
    ) -> LLMResponse:
        pass


_CORRECTION_WORDS = re.compile(
    r"\b(actually|correction|i meant|i mean|it should be|should be|"
    r"instead|rather|change (?:it|that|my|the)|update (?:it|that|my|the))\b",
    re.IGNORECASE
)

_CORRECTION_PREFIX_RE = re.compile(
    r"^\s*(?:actually|correction|i meant|i mean|it should be|"
    r"should be|instead|rather)\b[:,]?\s*",
    re.IGNORECASE
)

_NOT_X_Y = re.compile(r"\b[Nn]ot\s+[A-Z][^,]*,\s*\S")

_UNCERTAIN = re.compile(
    r"\b(maybe|perhaps|might|possibly|probably|i think|i guess|"
    r"unsure|not certain|could be|kind of|sort of)\b",
    re.IGNORECASE
)

_NEGATIVE = re.compile(
    r"\b(no|not|none|never|nope|don't|dont|doesn't|doesnt|"
    r"do not|does not|without|isn't|aren't)\b",
    re.IGNORECASE
)

_POSITIVE_WORLDWIDE = re.compile(
    r"\b(yes|yeah|yep|yup|sure|cover|covers|covered|include|includes|"
    r"included|everything|all)\b",
    re.IGNORECASE
)

_WORLDWIDE_WORD = re.compile(
    r"\b(worldwide|world-wide|world wide|global|globally|overseas)\b",
    re.IGNORECASE
)

_CHILD_WORD = re.compile(
    r"\b(child|children|kid|kids|son|sons|daughter|daughters)\b",
    re.IGNORECASE
)

_YES_START = re.compile(
    r"^\s*(yes|yeah|yep|yup|sure|of course|correct|absolutely)\b",
    re.IGNORECASE
)
_NO_START = re.compile(
    r"^\s*(no|nope|nah|none|nothing)\b",
    re.IGNORECASE
)

_NAME_TOKEN = r"[A-Z][A-Za-z'’-]*(?:\s+[A-Z][A-Za-z'’-]*)*"
_NAME_ONLY = re.compile(rf"^{_NAME_TOKEN}$")
_LENIENT_NAME_ONLY = re.compile(
    r"^[A-Za-z][A-Za-z'’-]*(?:\s+[A-Za-z][A-Za-z'’-]*){0,3}$"
)

_PRONOUNS = {
    "this", "that", "he", "she", "it", "they", "who", "there",
    "what", "which", "my", "the"
}

_NON_NAME_WORDS = {
    "yes", "no", "hello", "hi", "hey", "ok", "okay", "thanks",
    "thank", "nothing", "none", "maybe"
}

_NAME_RE = re.compile(
    r"\b(?:my\s+(?:full\s+)?name\s+(?:is|should be)|"
    r"my\s+name's|call\s+me)\s+"
    r"(?:actually\s+)?"
    r"(.+?)(?=\s+(?:and|but)\s|\s*[,.;!?]|\s*$)",
    re.IGNORECASE
)

_BARE_NAME_IS_RE = re.compile(
    r"^\s*name\s+(?:is|should be)\s+"
    r"(.+?)(?=\s+(?:and|but)\s|\s*[,.;!?]|\s*$)",
    re.IGNORECASE
)

_NAME_IS_MY_NAME_RE = re.compile(
    rf"\b({_NAME_TOKEN})\s+is\s+my\s+name\b",
    re.IGNORECASE
)

_I_AM_RE = re.compile(
    rf"\b(?:I am|I'm)\s+({_NAME_TOKEN})(?=\s+(?:and|but)\s|\s*[,.;!?]|\s*$)"
)

_CHANGE_NAME_TO_RE = re.compile(
    r"\b(?:change|update)\s+(?:my\s+)?(?:full\s+)?name\s+to\s+"
    r"(.+?)(?=\s+(?:and|but)\s|\s*[,.;!?]|\s*$)",
    re.IGNORECASE
)

_CHANGE_IT_TO_RE = re.compile(
    r"\b(?:change|update)\s+(?:it|that|this)\s+to\s+"
    r"(.+?)(?=\s+(?:and|but)\s+(?:i|my|it|yes|no)\b|[;!?]|"
    r"\.\s+(?:i|my|yes|no)\b|\.\s*$|\s*$)",
    re.IGNORECASE
)

_OFF_TOPIC_VERBS = {
    "love", "like", "enjoy", "hate", "prefer", "play", "playing",
    "watch", "watching", "dislike", "adore"
}


def _looks_off_topic(text: str) -> bool:
    """
    Detects a generic first-person statement of preference/interest
    (e.g. "I love playing cricket.", "I like painting.") so it is
    never mistaken for a name, executor name, gift, or child name
    just because it happens to be a short run of alphabetic words.
    """

    tokens = re.findall(r"[A-Za-z']+", text.lower())

    if not tokens:
        return False

    return (
        tokens[0] in ("i", "we")
        and any(token in _OFF_TOPIC_VERBS for token in tokens[1:])
    )

_ADDRESS_RE = re.compile(
    r"\b(?:i\s+(?:now\s+)?live\s+(?:at|in|on)|"
    r"i\s+reside\s+(?:at|in)|"
    r"i\s+am\s+living\s+(?:at|in)|"
    r"my\s+(?:home\s+|new\s+)?address\s+(?:is|should be))\s+"
    r"(.+?)"
    r"(?=\s+(?:and|but)\s+(?:i|my|it|yes|no)\b|[;!?]|"
    r"\.\s+(?:i|my|yes|no)\b|\.\s*$|\s*$)",
    re.IGNORECASE
)

_EXECUTOR_IS_RE = re.compile(
    r"\bexecutor\s+(?:is|will be|should be|would be|to be)\s+"
    r"(?:actually\s+)?(.+?)(?=[.;!?]|\s+(?:and|but)\s|\s*$)",
    re.IGNORECASE
)

_APPOINT_RE = re.compile(
    rf"\b(?:appoint|choose|name|nominate|want|like|pick)\s+"
    rf"({_NAME_TOKEN})\s+(?:as|to be)\s+my\s+executor",
)

_REL_NAME_EXECUTOR_RE = re.compile(
    rf"\bmy\s+([a-z][a-z-]*)\s+({_NAME_TOKEN})\s+"
    rf"(?:is|will be|would be|shall be|to be)\s+my\s+executor\b",
    re.IGNORECASE
)

_NON_RELATIONSHIP_WORDS = {
    "executor", "beneficiary", "witness", "heir", "trustee", "name"
}

_NAME_IS_MY_RE = re.compile(
    r"\b([A-Z][A-Za-z'’-]*(?:\s[A-Z][A-Za-z'’-]*)?)\s+"
    r"(?:is|will be|would be)\s+my\s+([a-z][a-z-]*)\b"
)

_NAME_IS_MY_EXECUTOR_RE = re.compile(
    rf"\b({_NAME_TOKEN})\s+(?:is|will be|would be|shall be)\s+my\s+executor\b",
    re.IGNORECASE
)

_PRONOUN_IS_MY_RE = re.compile(
    r"\b(?:he|she|they)(?:'s|\s+is)\s+my\s+([a-z][a-z-]*)\b",
    re.IGNORECASE
)

_RELATIONSHIP_RE = re.compile(
    r"\brelationship\s+(?:is|:)\s*(?:my\s+)?([a-z][a-z-]*)\b",
    re.IGNORECASE
)

_ADDRESS_KEYWORDS_RE = re.compile(
    r"\b(street|st|road|rd|avenue|ave|lane|ln|drive|dr|way|court|ct|"
    r"place|pl|boulevard|blvd|circle|square|sq|path|marg|chowk|"
    r"nagar|colony|society|layout|extension|sector|block|phase|"
    r"apartment|apt|flat|floor|heights|building|bldg|tower|city|town|"
    r"village|district|county|state|province|pin|zip|postcode)\b",
    re.IGNORECASE
)


def _is_plausible_address(candidate: str) -> bool:
    if not candidate:
        return False

    tokens = [t for t in re.split(r"[\s,]+", candidate) if t]

    if len(tokens) < 2:
        return False

    has_number = bool(re.search(r"\d", candidate))
    has_keyword = bool(_ADDRESS_KEYWORDS_RE.search(candidate))

    return has_number or has_keyword


_VOWEL_RE = re.compile(r"[aeiouAEIOU]")


def _is_plausible_name(candidate: str) -> bool:
    if not candidate:
        return False

    tokens = candidate.split()

    if not tokens:
        return False

    for token in tokens:
        letters = re.sub(r"[^A-Za-z]", "", token)

        if not letters or not _VOWEL_RE.search(letters):
            return False

    return True


_NO_GIFTS_RE = re.compile(
    r"\bno\s+(?:specific\s+)?(?:gifts?|bequests?)\b|"
    r"\bnothing\s+specific\b|"
    r"\bwithout\s+(?:any\s+)?(?:specific\s+)?gifts?\b|"
    r"\b(?:don't|do\s+not|dont)\s+have\s+(?:any\s+)?"
    r"(?:specific\s+)?gifts?\b",
    re.IGNORECASE
)

_NO_WISHES_RE = re.compile(
    r"\bno\s+(?:other\s+|further\s+|more\s+)?(?:additional\s+)?wishes\b|"
    r"\bnothing\s+(?:else|more|additional)\b|"
    r"\b(?:don't|do\s+not|dont)\s+have\s+(?:any\s+)?"
    r"(?:other\s+|further\s+|more\s+)?(?:additional\s+)?wishes\b",
    re.IGNORECASE
)

_GIFT_VERB_RE = re.compile(
    r"\b(?:leave|give|gift|bequeath)\s+(.+?)(?=[.;!?]|\s*$)",
    re.IGNORECASE
)

_GIVE_PERSON_RE = re.compile(
    r"\bgive\s+([A-Z][A-Za-z'’-]*)\s+(?:my|the)\s+(.+?)(?=[.;!?]|\s*$)"
)

_WISH_START_RE = re.compile(
    r"^(?:also,?\s+)?(?:i\s+want|i\s+would\s+like|i'd\s+like|i\s+wish|"
    r"my\s+wish\s+is|i\s+would\s+prefer|please)\b",
    re.IGNORECASE
)

_WISH_ADD_PREFIX_RE = re.compile(
    r"^(?:i\s+want\s+to\s+add\s+that|i\s+would\s+like\s+to\s+add\s+that|"
    r"i'd\s+like\s+to\s+add\s+that|i\s+also\s+want\s+to\s+add\s+that|"
    r"i\s+want\s+to\s+add)\s+",
    re.IGNORECASE
)


def _strip_wish_lead_in(sentence: str) -> str:
    stripped = _WISH_ADD_PREFIX_RE.sub("", sentence, count=1).strip()
    return stripped or sentence


_WISH_SPLIT_RE = re.compile(
    r"(?<=[.!?])\s+|;\s*|\s+and\s+(?=(?:i|yes|no|my)\b)|\s+but\s+",
    re.IGNORECASE
)

_SEGMENT_SPLIT_RE = re.compile(
    r"\s+(?:and|but)\s+|;|(?<=[.!?])\s+",
    re.IGNORECASE
)

_EXECUTOR_FIELD_CLARIFICATIONS = {
    "executor_name": (
        "I'm currently asking for your executor's name. Could you "
        "provide the name, or say \"I don't know\" if you're unsure?"
    ),
    "executor_relationship": (
        "I'm currently asking for your executor's relationship to "
        "you. Could you provide the relationship, or say \"I don't "
        "know\" if you're unsure?"
    ),
}

_FIELD_PHRASES = {
    "full_name": "your full name is {}",
    "home_address": "your home address is {}",
    "executor_name": "your executor is {}",
    "executor_relationship": "your executor is your {}",
}


def _strip_end(text: str) -> str:
    return text.strip().rstrip(".!?;,").strip()


def _clean_name(text: str) -> str:
    text = _strip_end(text).strip("\"'")

    if text.islower():
        text = text.title()

    return text


def _segments(text: str) -> List[str]:
    return [
        part.strip()
        for part in _SEGMENT_SPLIT_RE.split(text)
        if part and part.strip()
    ]


def _last_assistant_text(history: list) -> str:
    for item in reversed(history or []):
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content", "")
        else:
            role = getattr(item, "role", None)
            content = getattr(item, "content", "")

        if role == "assistant":
            return content or ""

    return ""


def _asked_field(history: list) -> Optional[str]:
    text = _last_assistant_text(history).lower()

    if not text or "which is correct" in text:
        return None

    for field, phrase in (
        ("children_names", "names of your children"),
        ("executor_relationship", "relationship to you"),
        ("executor_name", "your executor"),
        ("covers_worldwide_assets", "worldwide"),
        ("has_children", "children"),
        ("full_name", "full name"),
        ("home_address", "home address"),
        ("specific_gifts", "specific gifts"),
        ("additional_wishes", "additional wishes"),
    ):
        if phrase in text:
            return field

    return None


def _parse_names(text: str, lenient: bool = False) -> List[str]:
    names: List[str] = []

    text = re.split(r"[.;!?]", text)[0]

    for part in re.split(r"\s*,\s*|\s+and\s+|\s*&\s*", text):
        part = part.strip()

        if not part:
            continue

        if lenient:
            if (
                _LENIENT_NAME_ONLY.match(part)
                and part.lower() not in _NON_NAME_WORDS
            ):
                names.append(part.title() if part.islower() else part)
                continue
        elif _NAME_ONLY.match(part):
            names.append(part)
            continue

        break

    return names


_CHILD_NAMES_RE = re.compile(
    r"\b(?:children|kids)\s*(?:are|is|:|-|,|named|called)\s*(.+)$|"
    r"\b(?:their|the)\s+names?\s+(?:are|is)\s+(.+)$",
    re.IGNORECASE
)


def _extract_children(text: str, asked: Optional[str]) -> Dict[str, Any]:
    found: Dict[str, Any] = {}

    for segment in _segments(text):
        if not _CHILD_WORD.search(segment):
            continue

        if _NEGATIVE.search(segment):
            found["has_children"] = False
        else:
            found["has_children"] = True

        break

    match = _CHILD_NAMES_RE.search(text)

    if match:
        tail = match.group(1) or match.group(2)
        names = _parse_names(tail)

        if names:
            found["has_children"] = True
            found["children"] = names

    if (
        not found
        and asked == "children_names"
        and not _looks_off_topic(text)
    ):
        names = _parse_names(text, lenient=True)

        if names:
            found["has_children"] = True
            found["children"] = names

    return found


def _extract_generic_change(
    text: str, asked: Optional[str]
) -> Dict[str, Any]:
    """
    Handles a context-dependent correction phrase such as
    "Change it to Mahek." or "Update that to Rahul.". The target
    field is not named in the sentence, so it is resolved from the
    field currently being collected or clarified (``asked``).
    """

    if not asked:
        return {}

    match = _CHANGE_IT_TO_RE.search(text)
    if not match:
        return {}

    raw_value = _strip_end(match.group(1))

    if not raw_value:
        return {}

    if asked == "full_name":
        candidate = _clean_name(raw_value)
        if _is_plausible_name(candidate) and not _looks_off_topic(raw_value):
            return {"full_name": candidate}
        return {}

    if asked == "home_address":
        if _is_plausible_address(raw_value):
            return {"home_address": raw_value}
        return {}

    if asked == "executor_name":
        candidate = _clean_name(raw_value)
        if not _looks_off_topic(raw_value):
            return {"executor": {"name": candidate}}
        return {}

    if asked == "executor_relationship":
        return {"executor": {"relationship": raw_value.lower()}}

    return {}


def _extract_worldwide(text: str) -> Dict[str, Any]:
    for segment in _segments(text):
        if not _WORLDWIDE_WORD.search(segment):
            continue

        if _NEGATIVE.search(segment):
            return {"covers_worldwide_assets": False}

        if _POSITIVE_WORLDWIDE.search(segment):
            return {"covers_worldwide_assets": True}

    return {}


def _executor_from_tail(tail: str) -> Dict[str, Optional[str]]:
    tail = _strip_end(tail)

    match = re.match(
        rf"^my\s+([a-z][a-z-]*)\s+({_NAME_TOKEN})$",
        tail
    )
    if match:
        return {"name": match.group(2), "relationship": match.group(1)}

    match = re.match(
        rf"^({_NAME_TOKEN})\s*,\s*my\s+([a-z][a-z-]*)$",
        tail
    )
    if match:
        return {"name": match.group(1), "relationship": match.group(2)}

    match = re.match(r"^my\s+([a-z][a-z-]*)$", tail, re.IGNORECASE)
    if match:
        return {"name": None, "relationship": match.group(1).lower()}

    if tail and not tail.lower().startswith("my ") and len(tail.split()) <= 4:
        return {"name": _clean_name(tail), "relationship": None}

    return {}


def _extract_executor(text: str, asked: Optional[str]) -> Dict[str, Any]:
    result: Dict[str, Optional[str]] = {}

    match = _EXECUTOR_IS_RE.search(text)
    if match:
        result = _executor_from_tail(match.group(1))

    if not result:
        match = _REL_NAME_EXECUTOR_RE.search(text)
        if match:
            result = {
                "name": match.group(2),
                "relationship": match.group(1).lower()
            }

    if not result:
        match = _APPOINT_RE.search(text)
        if match:
            result = {"name": match.group(1), "relationship": None}

    if not result:
        match = _NAME_IS_MY_EXECUTOR_RE.search(text)
        if match:
            result = {"name": match.group(1), "relationship": None}

    if not result:
        match = _NAME_IS_MY_RE.search(text)
        if (
            match
            and match.group(1).lower() not in _PRONOUNS
            and match.group(2).lower() not in _NON_RELATIONSHIP_WORDS
        ):
            result = {
                "name": match.group(1),
                "relationship": match.group(2).lower()
            }

    if not result:
        match = _PRONOUN_IS_MY_RE.search(text) or _RELATIONSHIP_RE.search(text)
        if match:
            result = {"name": None, "relationship": match.group(1).lower()}

    if not result and asked == "executor_name":
        candidate = _strip_end(text)
        if (
            candidate
            and _LENIENT_NAME_ONLY.match(candidate)
            and candidate.lower() not in _NON_NAME_WORDS
            and not _NO_START.match(candidate)
            and not _NO_GIFTS_RE.search(candidate)
            and not _NO_WISHES_RE.search(candidate)
            and not _looks_off_topic(candidate)
            and not _CHANGE_IT_TO_RE.search(text)
            and not _CHANGE_NAME_TO_RE.search(text)
        ):
            result = {"name": _clean_name(candidate), "relationship": None}

    if not result and asked == "executor_relationship":
        candidate = _strip_end(text).lower()
        candidate = re.sub(r"^(?:he|she|they)(?:'s|\s+is)\s+", "", candidate)
        candidate = re.sub(r"^my\s+", "", candidate)
        if (
            re.match(r"^[a-z][a-z-]*(?:\s[a-z][a-z-]*)?$", candidate)
            and not _NO_START.match(candidate)
        ):
            result = {"name": None, "relationship": candidate}

    result = {k: v for k, v in result.items() if v}

    return {"executor": result} if result else {}


def _split_gift_clause(clause: str) -> List[str]:
    gifts = []

    for part in re.split(
        r"\s*;\s*|\s+and\s+(?=(?:my|the)\s)|,\s*(?=(?:my|the)\s)",
        clause
    ):
        part = _strip_end(part)
        part = re.sub(r"\s+instead$", "", part, flags=re.IGNORECASE)
        part = re.sub(r"^(?:my|the)\s+", "", part, flags=re.IGNORECASE)

        if part:
            gifts.append(part[0].upper() + part[1:])

    return gifts


def _extract_gifts(text: str, asked: Optional[str]) -> Dict[str, Any]:
    if _NO_GIFTS_RE.search(text):
        return {"specific_gifts": []}

    match = _GIVE_PERSON_RE.search(text)
    if match:
        item = match.group(2)
        return {
            "specific_gifts": _split_gift_clause(
                f"{item} to {match.group(1)}"
            )
        }

    match = _GIFT_VERB_RE.search(text)
    if match:
        gifts = _split_gift_clause(match.group(1))
        if gifts:
            return {"specific_gifts": gifts}

    if asked == "specific_gifts":
        if _NO_START.match(text):
            return {"specific_gifts": []}

        candidate = _strip_end(text)
        if candidate and not _looks_off_topic(candidate):
            return {"specific_gifts": _split_gift_clause(candidate)}

    return {}


def _extract_wishes(
    text: str,
    asked: Optional[str],
    other_found: bool,
    intake_complete: bool = False
) -> Dict[str, Any]:
    if _NO_WISHES_RE.search(text):
        return {"additional_wishes": []}

    wishes = []

    for sentence in _WISH_SPLIT_RE.split(text):
        sentence = _strip_end(sentence)

        if not sentence or not _WISH_START_RE.match(sentence):
            continue

        if re.search(
            r"\b(leave|give|gift|bequeath|executor)\b",
            sentence,
            re.IGNORECASE
        ):
            continue

        wishes.append(_strip_wish_lead_in(sentence))

    if wishes:
        return {"additional_wishes": wishes}

    if asked == "additional_wishes" and not other_found:
        if _NO_START.match(text):
            return {"additional_wishes": []}

        candidate = _strip_end(text)
        if candidate:
            return {"additional_wishes": [_strip_wish_lead_in(candidate)]}

    if (
        intake_complete
        and not other_found
        and "?" not in text
    ):
        candidate = _strip_end(text)

        if (
            candidate
            and len(candidate.split()) >= 2
            and not _YES_START.match(candidate)
            and not _NO_START.match(candidate)
            and candidate.lower() not in _NON_NAME_WORDS
        ):
            return {
                "additional_wishes": [_strip_wish_lead_in(candidate)]
            }

    return {}


def _norm(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().casefold()

    if isinstance(value, list):
        return sorted(_norm(item) for item in value)

    return value


def _same(old: Any, new: Any) -> bool:
    return _norm(old) == _norm(new)


def _describe(field: str, value: Any) -> str:
    if field in _FIELD_PHRASES:
        return _FIELD_PHRASES[field].format(value)

    if field == "covers_worldwide_assets":
        return (
            "this document covers your worldwide assets"
            if value
            else "this document does not cover your worldwide assets"
        )

    if field == "has_children":
        return "you have children" if value else "you have no children"

    if field == "children":
        return "your children are " + ", ".join(value)

    if field == "specific_gifts":
        if value:
            return "your specific gifts are " + "; ".join(value)
        return "you have no specific gifts"

    if field == "additional_wishes":
        if value:
            return "your additional wishes are " + "; ".join(value)
        return "you have no additional wishes"

    return f"{field} is {value}"


class MockLLMService(LLMService):

    def process_message(
        self,
        message: str,
        current_state: dict,
        conversation_history: list,
        current_field: Optional[str] = None
    ) -> LLMResponse:

        text = (message or "").strip()
        state = current_state or {}
        executor_state = state.get("executor") or {}

        normalized_current_field = (
            "children_names" if current_field == "children"
            else current_field
        )
        asked = (
            normalized_current_field
            or _asked_field(conversation_history)
        )

        intake_complete = current_field is None

        if _UNCERTAIN.search(text):
            return LLMResponse(
                extracted=ExtractedInformation(),
                clarification_needed=True,
                clarification_question=self._clarification_question(
                    text, asked
                )
            )

        found: Dict[str, Any] = {}

        name_match = (
            _NAME_RE.search(text)
            or _I_AM_RE.search(text)
            or _NAME_IS_MY_NAME_RE.search(text)
            or _BARE_NAME_IS_RE.search(text)
            or _CHANGE_NAME_TO_RE.search(text)
        )
        if name_match:
            name_candidate = _clean_name(name_match.group(1))

            if _is_plausible_name(name_candidate):
                found["full_name"] = name_candidate
            else:
                return LLMResponse(
                    extracted=ExtractedInformation(),
                    clarification_needed=True,
                    clarification_question=(
                        "I couldn't identify a valid full name from "
                        "that. Could you provide your full name?"
                    )
                )

        addr_match = _ADDRESS_RE.search(text)
        if addr_match:
            address_candidate = _strip_end(addr_match.group(1))

            if _is_plausible_address(address_candidate):
                found["home_address"] = address_candidate
            else:
                return LLMResponse(
                    extracted=ExtractedInformation(),
                    clarification_needed=True,
                    clarification_question=(
                        "I couldn't identify a valid home address "
                        "from that. Could you provide your home "
                        "address?"
                    )
                )

        found.update(_extract_worldwide(text))
        found.update(_extract_children(text, asked))
        found.update(_extract_executor(text, asked))
        found.update(_extract_gifts(text, asked))
        found.update(
            _extract_wishes(
                text,
                asked,
                other_found=bool(found),
                intake_complete=intake_complete
            )
        )

        for key, value in _extract_generic_change(text, asked).items():
            if key == "executor":
                existing_executor = found.get("executor") or {}
                merged_executor = {**value, **existing_executor}
                found["executor"] = merged_executor
            else:
                found.setdefault(key, value)

        if asked in ("executor_name", "executor_relationship"):
            executor_found = found.get("executor") or {}
            executor_subfield = (
                "name" if asked == "executor_name" else "relationship"
            )

            if (
                executor_subfield not in executor_found
                and found
                and set(found) <= {"specific_gifts", "additional_wishes"}
            ):
                return LLMResponse(
                    extracted=ExtractedInformation(),
                    clarification_needed=True,
                    clarification_question=_EXECUTOR_FIELD_CLARIFICATIONS[
                        asked
                    ]
                )

        if not found and "?" not in text:

            if asked == "full_name":
                bare_candidate = _strip_end(text)

                if (
                    bare_candidate
                    and _LENIENT_NAME_ONLY.match(bare_candidate)
                    and bare_candidate.lower() not in _NON_NAME_WORDS
                    and not _looks_off_topic(bare_candidate)
                ):
                    name_candidate = _clean_name(bare_candidate)

                    if _is_plausible_name(name_candidate):
                        found["full_name"] = name_candidate
                    else:
                        return LLMResponse(
                            extracted=ExtractedInformation(),
                            clarification_needed=True,
                            clarification_question=(
                                "I couldn't identify a valid full "
                                "name from that. Could you provide "
                                "your full name?"
                            )
                        )

            elif asked == "home_address":
                bare_candidate = _strip_end(text)

                if bare_candidate:
                    if _is_plausible_address(bare_candidate):
                        found["home_address"] = bare_candidate
                    else:
                        return LLMResponse(
                            extracted=ExtractedInformation(),
                            clarification_needed=True,
                            clarification_question=(
                                "I couldn't identify a valid home "
                                "address from that. Could you "
                                "provide your home address?"
                            )
                        )

            else:
                found.update(self._bare_answer(text, asked))

        if (
            not found
            and state.get("full_name")
            and _CORRECTION_WORDS.search(text)
        ):
            remainder = _strip_end(
                _CORRECTION_PREFIX_RE.sub("", text, count=1)
            )

            if (
                remainder
                and _LENIENT_NAME_ONLY.match(remainder)
                and remainder.lower() not in _NON_NAME_WORDS
                and not _looks_off_topic(remainder)
            ):
                name_candidate = _clean_name(remainder)

                if _is_plausible_name(name_candidate):
                    found["full_name"] = name_candidate

        if not found:
            if _CORRECTION_WORDS.search(text) or _NOT_X_Y.search(text):
                return LLMResponse(
                    extracted=ExtractedInformation(),
                    clarification_needed=True,
                    clarification_question=(
                        "Which detail would you like to correct, "
                        "and what should it be?"
                    )
                )

            return LLMResponse(extracted=ExtractedInformation())

        is_correction = bool(
            _CORRECTION_WORDS.search(text) or _NOT_X_Y.search(text)
        )
        is_clarification_answer = (
            "which is correct"
            in _last_assistant_text(conversation_history).lower()
        )

        changes = []

        def compare(field: str, old: Any, new: Any):
            if old in (None, "", []):
                return
            if not _same(old, new):
                changes.append((field, old, new))

        if "full_name" in found:
            compare("full_name", state.get("full_name"), found["full_name"])

        if "home_address" in found:
            compare(
                "home_address",
                state.get("home_address"),
                found["home_address"]
            )

        if "covers_worldwide_assets" in found:
            compare(
                "covers_worldwide_assets",
                state.get("covers_worldwide_assets"),
                found["covers_worldwide_assets"]
            )

        if "has_children" in found:
            compare(
                "has_children",
                state.get("has_children"),
                found["has_children"]
            )

        if "children" in found:
            compare("children", state.get("children"), found["children"])

        if "executor" in found:
            new_exec = found["executor"]

            if "name" in new_exec:
                compare(
                    "executor_name",
                    executor_state.get("name"),
                    new_exec["name"]
                )

            if "relationship" in new_exec:
                compare(
                    "executor_relationship",
                    executor_state.get("relationship"),
                    new_exec["relationship"]
                )

        if found.get("specific_gifts") == [] and state.get("specific_gifts"):
            changes.append(
                ("specific_gifts", state["specific_gifts"], [])
            )

        if (
            found.get("additional_wishes") == []
            and state.get("additional_wishes")
        ):
            changes.append(
                ("additional_wishes", state["additional_wishes"], [])
            )

        if changes and not (is_correction or is_clarification_answer):
            field, old, new = changes[0]

            return LLMResponse(
                extracted=ExtractedInformation(),
                detected_contradiction=True,
                contradiction_explanation=(
                    f"Earlier you told me {_describe(field, old)}, "
                    f"but now you've said {_describe(field, new)}. "
                    "Which is correct? If you would like to change "
                    "it, just tell me."
                ),
                contradiction_field=field
            )

        for field in ("specific_gifts", "additional_wishes"):
            new_items = found.get(field)
            old_items = state.get(field) or []

            if new_items and old_items and not is_correction:
                merged = list(old_items)
                existing = {_norm(item) for item in merged}

                for item in new_items:
                    if _norm(item) not in existing:
                        merged.append(item)

                found[field] = merged

        return LLMResponse(extracted=self._to_extracted(found))

    @staticmethod
    def _to_extracted(found: Dict[str, Any]) -> ExtractedInformation:
        data = dict(found)

        if "executor" in data:
            data["executor"] = ExtractedExecutor(**data["executor"])

        return ExtractedInformation(**data)

    @staticmethod
    def _clarification_question(text: str, asked: Optional[str]) -> str:
        if _CHILD_WORD.search(text) or asked in (
            "has_children", "children_names"
        ):
            return "Could you clarify whether you have children?"

        if _WORLDWIDE_WORD.search(text) or asked == "covers_worldwide_assets":
            return (
                "Could you clarify whether this document should cover "
                "your worldwide assets?"
            )

        return (
            "I'm not completely sure I understood that. "
            "Could you please confirm the information?"
        )

    @staticmethod
    def _bare_answer(text: str, asked: Optional[str]) -> Dict[str, Any]:
        candidate = _strip_end(text)

        if not candidate or "?" in text:
            return {}

        if asked == "covers_worldwide_assets":
            if _YES_START.match(text):
                return {"covers_worldwide_assets": True}
            if _NO_START.match(text):
                return {"covers_worldwide_assets": False}

        if asked == "has_children":
            if _YES_START.match(text):
                return {"has_children": True}
            if _NO_START.match(text):
                return {"has_children": False}

        return {}


GROQ_SYSTEM_PROMPT = """
You are the extraction engine for a fictional Personal Wishes Document
intake assistant. You do NOT chat with the user. You read the user's
latest message and return structured JSON only.

FIELDS
- full_name (string)
- home_address (string)
- covers_worldwide_assets (true / false)
- has_children (true / false)
- children (list of names)
- executor: { "name": string, "relationship": string }
- specific_gifts (list of strings)
- additional_wishes (list of strings)

CORE RULES
1. Extract ONLY information the user explicitly stated in the latest
   message. Never invent, infer, guess or complete information.
   (Do not add a city, country, surname or relationship that the user
   did not say.)
2. The CURRENT STRUCTURED STATE is the source of truth. Preserve it:
   return null for every field the latest message does not mention.
   Do not repeat values that are already in the state.
3. One message may contain several fields. Extract all of them.
4. Do not ask again for information that is already confirmed.
5. Unknown or guessed information is NOT confirmed. If the user is
   unsure ("maybe", "I think", "possibly", "probably", "not sure"),
   do not extract that field. Set clarification_needed = true and
   write a short clarification_question.
6. For list fields, null means "not mentioned" and [] means "the user
   explicitly said there are none". Use [] ONLY when the user clearly
   says so (e.g. "No specific gifts", "No additional wishes",
   "I have no children" -> has_children false).
   For specific_gifts and additional_wishes, when the user adds an
   item, return the COMPLETE updated list (existing items + new item).

CORRECTIONS vs CONTRADICTIONS
A value that differs from the state is a CORRECTION when the user's
wording clearly signals it: "actually", "correction", "I meant",
"it should be", "instead", "not X, Y", "change it to", "sorry, ...".
Apply corrections: return the new value in extracted and keep
detected_contradiction = false.

A value that differs from the state WITHOUT such wording, or where it
is unclear which version is right, is a CONTRADICTION. Then set
detected_contradiction = true, write contradiction_explanation as a
short question that quotes both versions and ends with "Which is
correct?", and return every field in extracted as null so the state
is NOT overwritten until the user clarifies. If the user's next
message clearly answers that question, apply the answer.

EXAMPLES
State: full_name = "Jane Smith"
User: "Actually, my name is Jane Brown."
-> correction: extracted.full_name = "Jane Brown".

State: has_children = false
User: "Actually, I have two children."
-> correction: extracted.has_children = true.

State: has_children = false
User: "I have children."
-> contradiction (no correction wording): detected_contradiction =
true, all extracted fields null, explanation asks which is correct.

State: has_children = null
User: "Maybe I have children."
-> clarification_needed = true, question "Could you clarify whether
you have children?", all extracted fields null.

User: "My name is Jane Smith and I live at 12 Oxford Street."
-> full_name "Jane Smith", home_address "12 Oxford Street" (nothing
else).

User: "Yes, it covers worldwide assets and I have no children."
-> covers_worldwide_assets true, has_children false.

User: "James is my brother."
-> executor { "name": "James", "relationship": "brother" }.

User: "No specific gifts."
-> specific_gifts [] (explicitly none).

OUTPUT FORMAT
Return ONLY one valid JSON object, no markdown, no commentary:

{
  "extracted": {
    "full_name": null,
    "home_address": null,
    "covers_worldwide_assets": null,
    "has_children": null,
    "children": null,
    "executor": null,
    "specific_gifts": null,
    "additional_wishes": null
  },
  "clarification_needed": false,
  "clarification_question": null,
  "detected_contradiction": false,
  "contradiction_explanation": null
}

When executor information is present use:
"executor": { "name": "...", "relationship": "..." }
(use null for whichever of the two was not stated).
""".strip()


def _strip_code_fences(content: str) -> str:
    content = content.strip()

    if content.startswith("```"):
        content = re.sub(r"^```[a-zA-Z]*\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

    return content.strip()


class GroqLLMService(LLMService):

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        client: Any = None,
        timeout: float = 30
    ):
        self.api_key = (
            api_key if api_key is not None else config.GROQ_API_KEY
        )
        self.model = model or config.GROQ_MODEL
        self.timeout = timeout
        self.client = client

        if self.client is None:
            if self.api_key:
                self.client = self._build_client()
            else:
                logger.warning(
                    "LLM_PROVIDER=groq but GROQ_API_KEY is not set. "
                    "Requests will fail safely until a key is added."
                )

    def _build_client(self):
        try:
            from groq import Groq
        except ImportError:
            logger.error(
                "The 'groq' package is not installed. "
                "Run: pip install -r requirements.txt"
            )
            return None

        return Groq(api_key=self.api_key, timeout=self.timeout)

    def _redact(self, text: str) -> str:
        if self.api_key:
            text = text.replace(self.api_key, "***")
        return text

    def process_message(
        self,
        message: str,
        current_state: dict,
        conversation_history: list,
        current_field: Optional[str] = None
    ) -> LLMResponse:

        if self.client is None:
            raise LLMConfigurationError(
                "Groq is not configured (missing API key or SDK)."
            )

        current_field_note = (
            f"\nFIELD CURRENTLY BEING COLLECTED: {current_field}\n"
            if current_field
            else ""
        )

        user_prompt = f"""
CURRENT STRUCTURED STATE (source of truth):

{json.dumps(current_state, indent=2)}

RECENT CONVERSATION (context only, NOT the source of truth):

{json.dumps(conversation_history[-10:], indent=2)}
{current_field_note}
LATEST USER MESSAGE:

{message}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": GROQ_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                timeout=self.timeout
            )
        except Exception as exc:
            logger.error(
                "Groq request failed: %s: %s",
                type(exc).__name__,
                self._redact(str(exc))
            )
            raise LLMProviderError(
                f"Groq request failed ({type(exc).__name__})"
            ) from None

        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError):
            raise LLMResponseError(
                "Groq returned an unexpected response shape."
            ) from None

        if not content or not content.strip():
            raise LLMResponseError("Groq returned an empty response.")

        try:
            data = json.loads(_strip_code_fences(content))
        except json.JSONDecodeError:
            logger.error("Groq returned malformed JSON.")
            raise LLMResponseError(
                "Groq returned malformed JSON."
            ) from None

        if not isinstance(data, dict):
            raise LLMResponseError("Groq JSON was not an object.")

        return validate_llm_response(data)


def create_llm_service(provider: Optional[str] = None) -> LLMService:
    provider = (provider or config.LLM_PROVIDER or "mock")
    provider = provider.strip().lower()

    if provider == "mock":
        return MockLLMService()

    if provider == "groq":
        return GroqLLMService()

    raise ValueError(
        f"Unsupported LLM_PROVIDER '{provider}'. "
        "Use 'mock' or 'groq'."
    )