from datetime import datetime
from Plant.plant_status import PlantStatus
from BaseEntity.base_entity import BaseEntity
from globals import (
    DATE_FORMAT,
    MOISTURE_THRESHOLD
)


class Plant(BaseEntity):
    """Represents a plant with health monitoring capabilities."""
    
    # Probability (0-100) that a plant transitions to unhealthy status
    # when time thresholds are exceeded
    CHANGE_STATUS_PERCENT = 75

    def __init__(
        self,
        id: int,
        specie: str,
        date_added: datetime,
        date_watered: datetime,
        date_fertilized: datetime,
        date_cured: datetime,
        status: list[PlantStatus],
        zone_id: int
    ):
        self.specie = specie
        self.id = id
        self.date_added = date_added
        self.date_watered = date_watered
        self.date_fertilized = date_fertilized
        self.date_cured = date_cured
        self.status = status
        self.zone_id = zone_id
            
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
        return f"ID: {self.id}, Specie: {self.specie}, Data inserimento: {self.date_added.strftime(DATE_FORMAT)}, Ultima innaffiatura: {self.date_watered.strftime(DATE_FORMAT)}, Data applicazione nutrienti: {self.date_fertilized}, Data applicazione pesticida: {self.date_cured}, Salute: {", ".join(s_status.value for s_status in self.status)}, Zona: {self.zone_id}"
