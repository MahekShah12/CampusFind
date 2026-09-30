export const HANDOVER_LOCATIONS = [
  "College Security Office",
  "Student Help Desk",
  "Main Reception",
  "Library Help Desk",
  "Other"
];

export const handoverStatusLabel = (s) =>
  ({
    NOT_ASSIGNED: "Not assigned",
    READY_FOR_PICKUP: "Ready for Pickup",
    COMPLETED: "Completed"
  }[s] || s);

export const FALLBACK_IMG =
  "https://images.unsplash.com/photo-1584438784894-089d6a62b8fa?auto=format&fit=crop&w=400&q=80";
