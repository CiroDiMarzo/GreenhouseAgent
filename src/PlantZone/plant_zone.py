from BaseEntity.base_entity import BaseEntity
from Plant.plant import Plant
from Sensor.moisture_sensor import MoistureSensor
from globals import LOG_FORMAT, roll_dice
import logging

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


class PlantZone(BaseEntity):
    logger = logging.getLogger("PlantZone")

    def __init__(self, id: int, name: str, moisture_level: float):
        self.id = id
        self.name = name
        self.__moisture_level = moisture_level
        self.plants: list[Plant] = []
        self.sensors: list[MoistureSensor] = []
        self.is_dirty = False

    def add_plant(self, plant: Plant):
        self.plants.append(plant)
        
    def add_sensor(self, sensor: MoistureSensor):
        self.sensors.append(sensor)

    async def read_sensors(self):
        """
        Gets the latest reading from all the sensors.
        """
        try:
            self.moisture = max(0, self.moisture - 0.03)
            self.logger.info(F"Moisture changed in {self.name}: {self.moisture}")
        except Exception as exc:
            self.logger.error(f"Error while reading moisture sensor {exc}")
            raise ValueError(f"Error while reading moisture sensor {exc}")
    
    @property
    def moisture(self) -> float:
        return self.__moisture_level

    @moisture.setter
    def moisture(self, value: float):
        self.is_dirty = True
        self.__moisture_level = value

        if self.plants:
            for row_num, plant in enumerate(self.plants):
                plant.inspect_self(value)
