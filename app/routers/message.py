from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.message_service import get_intervention_content

router = APIRouter(prefix="/message", tags=["Message Optimizer"])


class MessageOptimizeRequest(BaseModel):
  intervention_id: str
  user_context: Optional[Dict[str, Any]] = None


# @router.post("/optimize")
# def optimize_message(request: List[MessageOptimizeRequest]):
#   """
#   Given an intervention_id, return the optimized message content.
#   Accepts optional user_context (e.g., {"name": "Kojo", "goal": "fitness"}).
#   """
#   results = []
#   for req in request:
#     result = get_intervention_content(
#       intervention_id=req.intervention_id,
#       user_context=req.user_context or {}
#     )
#     results.append(result)

#   return {"success": True, "result": results}