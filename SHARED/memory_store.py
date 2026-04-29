from collections import defaultdict
from typing import Dict, Any, List

# Simple in-memory store
# Later you can replace this with SQLite / MongoDB / Redis
USER_MEMORY: Dict[str, Dict[str, Any]] = defaultdict(
    lambda: {
        "language": "English",
        "trimester": None,
        "symptom_history": [],
        "nutrition_history": [],
        "preferences": {
            "diet_type": None,      # vegetarian / non-vegetarian
            "budget": None,         # low / medium / high
            "food_notes": None      # e.g. nausea, anemia, dislikes, etc.
        }
    }
)


def get_user_memory(user_id: str) -> Dict[str, Any]:
    return USER_MEMORY[user_id]


def update_user_memory(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    memory = USER_MEMORY[user_id]

    for key, value in updates.items():
        if key == "preferences" and isinstance(value, dict):
            memory["preferences"].update(value)
        else:
            memory[key] = value

    return memory


def add_symptom_entry(user_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
    memory = USER_MEMORY[user_id]
    memory["symptom_history"].append(entry)

    # keep only last 5
    memory["symptom_history"] = memory["symptom_history"][-5:]
    return memory


def add_nutrition_entry(user_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
    memory = USER_MEMORY[user_id]
    memory["nutrition_history"].append(entry)

    # keep only last 5
    memory["nutrition_history"] = memory["nutrition_history"][-5:]
    return memory