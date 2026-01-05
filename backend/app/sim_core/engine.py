from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from app.sim_core.polynomial import eval_polynomial


@dataclass
class Field:
    x_comp: str = "0"
    y_comp: str = "0"


@dataclass
class Particle:
    # store particles in "graph coordinates" (not pixels)
    x: float
    y: float
    charge: int  # +1 or -1


class Simulator:
    def __init__(self):
        self.field = Field("0", "0")
        self.particles: List[Particle] = []
        self.paused: bool = False
        self.dt: float = 0.2  # equivalent to your /5 scaling
        self.bounds: Dict[str, float] = {"xmin": -10, "xmax": 10, "ymin": -10, "ymax": 10}

    def set_field(self, x_comp: str, y_comp: str) -> None:
        self.field = Field((x_comp or "0").strip() or "0", (y_comp or "0").strip() or "0")

    def add_particle(self, x: float, y: float, charge: int) -> None:
        # normalize to +1 / -1
        c = 1 if int(charge) >= 0 else -1
        self.particles.append(Particle(x=float(x), y=float(y), charge=c))

    def step(self, n: int = 1) -> Dict[str, Any]:
        if self.paused:
            return self.snapshot()

        for _ in range(max(1, int(n))):
            new_particles: List[Particle] = []

            for p in self.particles:
                # Evaluate field components at current particle position
                try:
                    dx = float(eval_polynomial(self.field.x_comp, p.x, p.y))
                except Exception:
                    dx = 0.0

                try:
                    dy = float(eval_polynomial(self.field.y_comp, p.x, p.y))
                except Exception:
                    dy = 0.0

                # + charge moves WITH vector; - charge moves AGAINST vector
                p.x += p.charge * (dx * self.dt)
                p.y += p.charge * (dy * self.dt)

                if self.in_bounds(p.x, p.y):
                    new_particles.append(p)

            self.particles = new_particles

        return self.snapshot()

    def in_bounds(self, x: float, y: float) -> bool:
        b = self.bounds
        return (b["xmin"] <= x <= b["xmax"]) and (b["ymin"] <= y <= b["ymax"])

    def snapshot(self) -> Dict[str, Any]:
        return {
            "field": {"x": self.field.x_comp, "y": self.field.y_comp},
            "paused": self.paused,
            "dt": self.dt,
            "bounds": dict(self.bounds),
            "particles": [{"x": p.x, "y": p.y, "charge": p.charge} for p in self.particles],
        }
