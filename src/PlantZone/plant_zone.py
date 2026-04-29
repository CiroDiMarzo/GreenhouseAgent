from Plant.plant import Plant
from globals import DATE_FORMAT, LOG_FORMAT
import logging

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT
)

logger = logging.getLogger(__name__)

class PlantZone:
    def __init__(self, id: int, name: str, moisture_level: float):
        self.id = id
        self.name = name
        self.moisture_level = moisture_level
        self.plants: list[Plant] = []
        
    def add_plant(self, plant: Plant):
        self.plants.append(plant)
        # It will be the caller to persist to the database
        
    def update_moisture(self, value: float):
        self.moisture_level = value
        # It will be the caller to persist to the database
        
        if self.plants:
            for row_num, plant in enumerate(self.plants):
                plant.inspect_self(value)