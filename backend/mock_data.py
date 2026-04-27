from datetime import datetime, timedelta
from models import Bin
import random

bins = [
    Bin(id="1", name="Bin Agdal-01", latitude=33.981631, longitude=-6.864980,
        fill_level=20, battery=92, temperature=28.3,
        last_updated=datetime.now() - timedelta(minutes=5),
        last_collected=datetime.now() - timedelta(hours=6)),
    Bin(id="2", name="Bin Hay Riad-02", latitude=33.979715, longitude=-6.872097,
        fill_level=65, battery=78, temperature=31.1,
        last_updated=datetime.now() - timedelta(minutes=2),
        last_collected=datetime.now() - timedelta(hours=12)),
    Bin(id="3", name="Bin Souissi-03", latitude=33.973603, longitude=-6.872058,
        fill_level=30, battery=95, temperature=26.7,
        last_updated=datetime.now() - timedelta(minutes=8),
        last_collected=datetime.now() - timedelta(hours=3)),
    Bin(id="4", name="Bin Médina-04", latitude=33.970374, longitude=-6.864405,
        fill_level=90, battery=45, temperature=34.2,
        last_updated=datetime.now() - timedelta(minutes=1),
        last_collected=datetime.now() - timedelta(hours=18)),
    Bin(id="5", name="Bin Hassan-05", latitude=33.982799, longitude=-6.856251,
        fill_level=10, battery=99, temperature=24.8,
        last_updated=datetime.now() - timedelta(minutes=15),
        last_collected=datetime.now() - timedelta(hours=2)),
]

CAMION_START = (33.979448, -6.866329)


def generate_fill_history(hours: int = 24) -> list[dict]:
    """Generate simulated fill-level history for all bins over the last N hours."""
    history = []
    now = datetime.now()
    for b in bins:
        base = max(5, b.fill_level - random.randint(20, 50))
        for h in range(hours, -1, -1):
            ts = now - timedelta(hours=h)
            noise = random.randint(-3, 5)
            level = min(100, max(0, base + int((b.fill_level - base) * (hours - h) / hours) + noise))
            history.append({
                "bin_id": b.id,
                "bin_name": b.name,
                "fill_level": level,
                "timestamp": ts.isoformat(),
            })
    return history