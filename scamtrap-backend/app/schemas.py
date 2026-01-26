from pydantic import BaseModel
from typing import List

class ScamRequest(BaseModel):
    scam_message: str

class ScamResponse(BaseModel):
    reply: str
    scam_type: str
    extracted_data: List[str]
    risk_flag: bool
