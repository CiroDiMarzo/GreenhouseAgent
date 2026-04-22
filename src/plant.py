from datetime import datetime, timedelta
from plant_status import PlantStatus
from globals import date_format


class Plant:
    """Represents a plant with health monitoring capabilities."""

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
        time_passed_since_water = datetime.now() - self.date_watered
        time_passed_since_fertilized = datetime.now() - self.date_fertilized
        time_passed_since_cured = datetime.now() - self.date_cured
        self.status.clear()

        if time_passed_since_water >= timedelta(seconds=30):
            self.status.append(PlantStatus.THIRSTY)
        
        if time_passed_since_fertilized >= timedelta(seconds=40):
            self.status.append(PlantStatus.HUNGRY)
            
        if time_passed_since_cured >= timedelta(seconds=50):
            self.status.append(PlantStatus.SICK)
            
        if PlantStatus.THIRSTY not in self.status and PlantStatus.HUNGRY not in self.status and PlantStatus.SICK not in self.status:
            self.status.append(PlantStatus.HEALTHY)

    def __str__(self):
        return f"ID: {self.id}) - Specie: {self.specie} - Salute: {", ".join(s_status.value for s_status in self.status)}"

    def full_print(self):
        return f"ID: {self.id}, Specie: {self.specie}, Data inserimento: {self.date_added.strftime(date_format)}, Ultima innaffiatura: {self.date_watered.strftime(date_format)}, Data applicazione nutrienti: {self.date_fertilized}, Data applicazione pesticida: {self.date_cured}, Salute: {", ".join(s_status.value for s_status in self.status)}"
