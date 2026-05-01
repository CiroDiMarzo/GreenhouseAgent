from datetime import datetime
from Plant.plant_status import PlantStatus
from BaseEntity.base_entity import BaseEntity
from globals import (
    DATE_FORMAT,
    MOISTURE_THRESHOLD
)


class Plant(BaseEntity):
    """Represents a plant with health monitoring capabilities."""

    def __init__(
        self,
        id: int,
        specie: str,
        date_added: datetime,
        status: list[PlantStatus],
        zone_id: int
    ):
        self.specie = specie
        self.id = id
        self.date_added = date_added
        self.status = status
        self.zone_id = zone_id
        self.is_dirty = False
            
    def inspect_self(self, moisture_level: float):
        self.is_dirty = True
        self.status.clear()
        
        if(moisture_level <= MOISTURE_THRESHOLD):
            self.status.append(PlantStatus.NEEDS_WATER)
        else:
            self.status.append(PlantStatus.HEALTHY)

    def __str__(self):
        return f"ID: {self.id}) - Specie: {self.specie} - Salute: {", ".join(s_status.value for s_status in self.status)}"

    def full_print(self):
        return f"ID: {self.id}, Specie: {self.specie}, Data inserimento: {self.date_added.strftime(DATE_FORMAT)}, Salute: {", ".join(s_status.value for s_status in self.status)}, Zona: {self.zone_id}"
