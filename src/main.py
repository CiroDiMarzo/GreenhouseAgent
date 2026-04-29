from pathlib import Path
from csv import DictReader
from datetime import datetime, timedelta
import logging
from Plant.plant_repository import PlantRepository
from PlantZone.plant_zone_repository import PlantZoneRepository
from gardener import Gardener
from Plant.plant import Plant
from globals import DATE_FORMAT, LOG_FORMAT
from migration import migrate_plants
import random
import asyncio

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


async def main():
    BASE_PATH = Path(__file__).parent.parent
    db_file_path = BASE_PATH / 'data' / 'garden.db'
    
    plants_csv_file = BASE_PATH / 'plants_registry.csv'
    plants_zones_cvl_file = BASE_PATH / 'plants_zones_registry.csv'
    
    migrate_plants(str(plants_csv_file), str(plants_zones_cvl_file), str(db_file_path))
    
    #await start_gardening(db_file_path)

async def start_gardening(db_file_path):
    plant_repository = PlantRepository(str(db_file_path))
    plant_zone_repository = PlantZoneRepository(str(db_file_path))
    
    my_garden = plant_repository.get_all()

    logger.info(f"The garden has {len(my_garden)} plants.")
        
    gardner = Gardener("Silvano", plant_repository)
    logger.info(f"{gardner}")

    gardner.move_to_garden(my_garden)

    await gardner.start_working()
            
    for plant in my_garden:
        logger.info(f"{plant}")
        
if __name__ == "__main__":
    asyncio.run(main())
