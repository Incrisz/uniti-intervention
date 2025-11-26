import json
from ..config import get_settings
from .llm_service import prompt_llm
from ..utils.prompts import INTERVENTION_PROMPT, INTERVENTION_TYPES, PRIORITIZATION_GUIDELINES, ENGAGEMENT_FLOW
from pathlib import Path
from typing import Optional, Dict, Any
import psycopg2

# Load intervention library once at startup
LIBRARY_PATH = Path(__file__).resolve().parent.parent / "data" / "intervention_library.json"
with open(LIBRARY_PATH, "r") as f:
  INTERVENTION_LIBRARY = json.load(f)


def resolve_intervention(user_state: str, service_category: str) -> Optional[Dict[str, Any]]:
  """
  Resolves an intervention based on user_state and service_category.
  - If service_category = UNITI → fixed.
  - If service_category placeholder → substitute with actual value.
  - Templates also support {name}, {goal}, {service_category}.
  """

  for entry in INTERVENTION_LIBRARY:
    trigger = entry["trigger"]

    if (trigger["user_state"] == user_state) and (trigger["service_category"] == service_category):
      return entry["data"]["intervention_id"]

  return None

def get_intervention_for_reward_milestones(milestones, m_to_i):
  reward_interventions = []
  residual_milestones = []
  for milestone in milestones:
    if "REWARD" in m_to_i.get(milestone["milestoneId"], []):
      reward_interventions.append((f"{milestone['serviceCategory']}.{milestone['milestoneId']}.reward", milestone['appId']))
    else:
      residual_milestones.append(milestone)
  return reward_interventions, residual_milestones

def llm_intervention(usage_data: Any) -> str:
  settings = get_settings()
  interventions, residuals = get_intervention_for_reward_milestones(usage_data["current"], settings.milestones_to_intervention)
  usage_data["current"] = residuals
  params = {
    "usage_data" : usage_data,
    "intervention_ids" : settings.intervention_ids,
    "intervention_types" : INTERVENTION_TYPES,
    "prioritization_guidelines" : PRIORITIZATION_GUIDELINES,
    "engagement_flow" : ENGAGEMENT_FLOW
    }
  interventions.append(prompt_llm(INTERVENTION_PROMPT,params))
  interventions, app_ids = zip(*interventions)
  return interventions, app_ids


def get_message(intervention_id: str, conn, cur):
  data = {"interventionId": intervention_id}
  cols = ["subject", "content", "category"]
  for col in cols: data[col] = None
  query = f"SELECT {', '.join(cols)} FROM message_templates WHERE LOWER(title)='{intervention_id}'"
  cur.execute(query)
  row = cur.fetchone()
  if row:
    for i,cell in enumerate(row):
      data[cols[i]] = row[i]
  return data

def get_all_messages(intervention_ids):
  settings = get_settings()
  conn = psycopg2.connect(settings.db_url)
  cur = conn.cursor()
  results = []
  for intervention_id in intervention_ids:
    results.append(get_message(intervention_id, conn, cur))
  cur.close(), conn.close()
  return results

def fill_message_templates(messages, appIds,usage_data):
  filled_messages = []
  for message, appID in zip(messages, appIds):
    subject = message["subject"].format(**usage_data["metadata"]) if message["subject"] else None
    content = message["content"].format(**usage_data["metadata"]) if message["content"] else None
    filled_messages.append({
      "appId": appID,
      "interventionId": message["interventionId"],
      "subject": subject,
      "content": content,
      "category": message["category"]
    })
  return filled_messages