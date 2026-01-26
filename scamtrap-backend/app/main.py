from fastapi import FastAPI
from app.orchestrator import run_agents
from app.schemas import ScamRequest, ScamResponse

app = FastAPI(title="ScamTrap Agentic AI")

@app.post("/handover", response_model=ScamResponse)
def handover_scam(request: ScamRequest):
    result = run_agents(request.scam_message)
    return result
