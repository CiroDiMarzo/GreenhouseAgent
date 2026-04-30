from BaseEntity.base_entity import BaseEntity
from Plant.plant import Plant
from globals import LOG_FORMAT
import logging

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


class PlantZone(BaseEntity):
    logger = logging.getLogger("PlantZone")

    def __init__(self, id: int, name: str, moisture_level: float):
        self.id = id
        self.name = name
        self.moisture_level = moisture_level
        self.plants: list[Plant] = []

    def add_plant(self, plant: Plant):
        self.plants.append(plant)
        # It will be the caller to persist to the database

    def read_sensors(self):
        """
        Gets the latest reading from all the sensors.
        """
        try:
            self.update_moisture(max(0, self.moisture_level - 0.05))
        except:
            self.logger.error(f"Error while reading moisture sensor")
            raise ValueError(f"Error while reading moisture sensor")

    def update_moisture(self, value: float):
        self.is_dirty = True
        self.moisture_level = value
        # It will be the caller to persist to the database

        if self.plants:
            for row_num, plant in enumerate(self.plants):
                plant.inspect_self(value)
