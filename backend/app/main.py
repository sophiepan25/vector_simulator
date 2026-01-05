from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.sim_core.engine import Simulator

app = FastAPI(title="Vector Simulator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SIM = Simulator()

class FieldReq(BaseModel):
    x: str
    y: str

class AddParticleReq(BaseModel):
    x: float
    y: float
    charge: int  # +1 or -1

class StepReq(BaseModel):
    n: int = 1

@app.get("/api/state")
def state():
    return SIM.snapshot()

@app.post("/api/field")
def set_field(req: FieldReq):
    SIM.set_field(req.x, req.y)
    return SIM.snapshot()

@app.post("/api/particle")
def add_particle(req: AddParticleReq):
    SIM.add_particle(req.x, req.y, 1 if req.charge >= 0 else -1)
    return SIM.snapshot()

@app.post("/api/step")
def step(req: StepReq):
    return SIM.step(req.n)

@app.post("/api/pause")
def pause():
    SIM.paused = True
    return SIM.snapshot()

@app.post("/api/play")
def play():
    SIM.paused = False
    return SIM.snapshot()

@app.post("/api/reset")
def reset():
    global SIM
    SIM = Simulator()
    return SIM.snapshot()
