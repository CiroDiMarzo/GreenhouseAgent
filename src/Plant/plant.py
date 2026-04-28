from datetime import datetime, timedelta
import random
from Plant.plant_status import PlantStatus
from globals import (
    DATE_FORMAT,
    PLANT_TIME_DELTA_THIRSTY,
    PLANT_TIME_DELTA_HUNGRY,
    PLANT_TIME_DELTA_SICK,
    roll_dice
)


class Plant:
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
    ):
        self.specie = specie
        self.id = id
        self.date_added = date_added
        self.date_watered = date_watered
        self.date_fertilized = date_fertilized
        self.date_cured = date_cured
        self.status = status

    def inspect(self):
        """Inspect plant health status based on time since last maintenance.
        
        Evaluates if plant is thirsty, hungry, or sick based on time thresholds,
        using probabilistic evaluation with CHANGE_STATUS_PERCENT chance.
        If none of the negative statuses apply, marks plant as HEALTHY.
        """
        time_passed_since_water = datetime.now() - self.date_watered
        time_passed_since_fertilized = datetime.now() - self.date_fertilized
        time_passed_since_cured = datetime.now() - self.date_cured
        self.status.clear()

        if time_passed_since_water >= timedelta(seconds=PLANT_TIME_DELTA_THIRSTY):
            if roll_dice(self.CHANGE_STATUS_PERCENT):
                self.status.append(PlantStatus.THIRSTY)

        if time_passed_since_fertilized >= timedelta(seconds=PLANT_TIME_DELTA_HUNGRY):
            if roll_dice(self.CHANGE_STATUS_PERCENT):
                self.status.append(PlantStatus.HUNGRY)

        if time_passed_since_cured >= timedelta(seconds=PLANT_TIME_DELTA_SICK):
            if roll_dice(self.CHANGE_STATUS_PERCENT):
                self.status.append(PlantStatus.SICK)

        if (
            PlantStatus.THIRSTY not in self.status
            and PlantStatus.HUNGRY not in self.status
            and PlantStatus.SICK not in self.status
        ):
            self.status.append(PlantStatus.HEALTHY)
            
    def inspect_environment(self, moisture: float):
        raise NotImplementedError(f"Not implemented")        

    def __str__(self):
        return f"ID: {self.id}) - Specie: {self.specie} - Salute: {", ".join(s_status.value for s_status in self.status)}"

    def full_print(self):
        return f"ID: {self.id}, Specie: {self.specie}, Data inserimento: {self.date_added.strftime(DATE_FORMAT)}, Ultima innaffiatura: {self.date_watered.strftime(DATE_FORMAT)}, Data applicazione nutrienti: {self.date_fertilized}, Data applicazione pesticida: {self.date_cured}, Salute: {", ".join(s_status.value for s_status in self.status)}"
