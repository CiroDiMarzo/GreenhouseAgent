from datetime import datetime
import asyncio

from Plant.plant_status import PlantStatus
from Plant.plant import Plant


class Gardener :
    def __init__(self, name: str):
        self.name = name
        self.garden: list[Plant] = []
        
    def __str__(self):
        return f"Hello, I'm {self.name}"
    
    def move_to_garden(self, garden: list[Plant]):
        self.garden = garden
        print(f"{self.name} moves in the garden.")
        
    def leave_garden(self):
        self.garden = []
        print(f"{self.name} leaves the garden.")
        
    async def start_working(self):
        while True:
            print(f"-- Start working")
            await self.perform_maintenance()
            print(f"-- Work concluded")
            await asyncio.sleep(10)
        
    async def perform_maintenance(self):
        if not self.garden:
            print(f"{self.name} is not in a garden")
            return
        
        for plant in self.garden:
            plant.inspect()
            if(PlantStatus.THIRSTY in plant.status):
                await self.water_plant(plant)
            if(PlantStatus.HUNGRY in plant.status):
                await self.fertilize_plant(plant)
            if(PlantStatus.SICK in plant.status):
                await self.apply_pesticide(plant)
            plant.inspect()
    
    async def water_plant(self, plant: Plant):
        plant.date_watered = datetime.now()
        print(f"Watering plant {plant}")
        
    async def fertilize_plant(self, plant: Plant):
        plant.date_fertilized = datetime.now()
        print(f"Fertilizing plant {plant}")
        
    async def apply_pesticide(self, plant: Plant):
        plant.date_cured = datetime.now()
        print(f"Applying pesticide to plant {plant}")