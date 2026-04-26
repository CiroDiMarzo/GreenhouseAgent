from pathlib import Path
from csv import DictReader
from datetime import datetime, timedelta
from Plant.plant_repository import PlantRepository
from gardener import Gardener
from Plant.plant import Plant
from globals import DATE_FORMAT
import random
import asyncio

async def main():
    BASE_PATH = Path(__file__).parent.parent
    db_file_path = BASE_PATH / 'data' / 'garden.db'
    
    plant_repository = PlantRepository(str(db_file_path))
    
    my_garden = plant_repository.get_all()

    print(f"The garden has {len(my_garden)} plants.")
        
    gardner = Gardener("Silvano", plant_repository)
    print(f"{gardner}")

    gardner.move_to_garden(my_garden)

    await gardner.start_working()
            
    for plant in my_garden:
        print(f"{plant}")
        
if __name__ == "__main__":
    asyncio.run(main())
