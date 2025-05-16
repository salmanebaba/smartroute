from datetime import datetime
from models import Bin

bins = [
    Bin(id="1", latitude=33.981631, longitude= -6.864980, fill_level=20, last_updated=datetime.now()),
    Bin(id="2", latitude=33.979715, longitude= -6.872097, fill_level=40, last_updated=datetime.now()),
    Bin(id="3", latitude=33.973603, longitude=-6.872058, fill_level=30, last_updated=datetime.now()),
    Bin(id="4", latitude=33.970374, longitude=-6.864405, fill_level=90, last_updated=datetime.now()),
    Bin(id="5", latitude=33.982799, longitude=-6.856251, fill_level=10, last_updated=datetime.now()),
]

CAMION_START = (33.979448, -6.866329)