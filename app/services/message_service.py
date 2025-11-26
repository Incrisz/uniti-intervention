import json
from pathlib import Path
from typing import Optional, Dict, Any


# Load intervention library once at startup
LIBRARY_PATH = Path(__file__).resolve().parent.parent / "data" / "intervention_library.json"
with open(LIBRARY_PATH, "r") as f:
  INTERVENTION_LIBRARY = json.load(f)

def _fill_placeholders(data: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
  """Fill dynamic placeholders in intervention_id and template."""
  filled = data.copy()

  # Replace other placeholders from user_context
  if user_context:
    for key, value in user_context.items():
      if value is not None:
        filled["message_body"] = filled["message_body"].replace(f"{{{key}}}", str(value))

  return filled

def get_intervention_content_old(intervention_id: str, user_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
  """
  Retrieves the intervention content based on intervention_id.
  Fills in any placeholders using user_context (e.g., {"name": "Kojo", "goal": "fitness"}).
  """
  for entry in INTERVENTION_LIBRARY:
    if entry["data"]["intervention_id"] == intervention_id:
      return _fill_placeholders(entry["data"], user_context)

  return None

def get_intervention_content(intervention_id: str, user_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
  """
  Retrieves the intervention content based on intervention_id.
  Fills in any placeholders using user_context (e.g., {"name": "Kojo", "goal": "fitness"}).
  """
  for entry in INTERVENTION_LIBRARY:
    entry_id = entry["data"]["intervention_id"].split(".")
    entry_id = ".".join([entry_id[0], entry_id[1], entry_id[3]])
    if entry_id.lower() == intervention_id.lower():
      return _fill_placeholders(entry["data"], user_context)

  return None