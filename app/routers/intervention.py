from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.intervention_service import resolve_intervention, llm_intervention, get_all_messages, fill_message_templates
from app.services.message_service import get_intervention_content, get_intervention_content_old

router = APIRouter(prefix="/intervention", tags=["Intervention"])


class InterventionSelectRequest(BaseModel):
  user_state: str
  service_category: str
  user_context: Optional[Dict[str, Any]] = None

class SignalRecord(BaseModel):
  signalId: str  
  serviceCategory: str
  appId : str
  createdAt: str

class MilestoneRecord(BaseModel):
  milestoneId: str
  serviceCategory: str
  appId : str
  createdAt: str

class InterventionRecord(BaseModel):
  interventionId: str
  appId: str
  createdAt: str

class MetaData(BaseModel):
  id: Optional[str] = None
  name: Optional[str] = None

class UsageDataRequest(BaseModel):
  current: List[MilestoneRecord]
  pastMilestones: List[MilestoneRecord]
  pastSignals: List[SignalRecord]
  pastInterventions: List[InterventionRecord]
  metadata: MetaData


# @router.post("/select")
# def select_interventions(requests: List[InterventionSelectRequest]):
#   """
#   Given a list of user_state and service_category objects, 
#   return the matching interventions.
#   """
#   results = []
#   for req in requests:
#     intervention_id = resolve_intervention(
#       user_state=req.user_state,
#       service_category=req.service_category,
#     ) or "UNKNOWN"

#     result = get_intervention_content_old(
#       intervention_id=intervention_id,
#       user_context=req.user_context or {}
#     )
    
#     results.append(result)

#   return {"success": True, "result": results}

@router.post("/llm-select")
def llm_select_intervention(usage_data: UsageDataRequest):
  """
  Given usage data, select the most appropriate interventions using LLM.
  """
  interventionIds, appIds = llm_intervention(usage_data.model_dump())
  # message_content = get_all_messages(interventionIds)
  # result = fill_message_templates(message_content, appIds, usage_data.model_dump())
  result = []
  for a,b in zip(interventionIds, appIds):
    result.append({"interventionId": a.lower(), "appId": b.lower()})
  result = result if result else None

  return {"success": True, "result": result}
