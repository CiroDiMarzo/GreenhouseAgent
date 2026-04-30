from pathlib import Path
import logging
from Plant.plant_repository import PlantRepository
from PlantZone.plant_zone_repository import PlantZoneRepository
from gardener import Gardener
from globals import GARDENER_IDLE_TIME, LOG_FORMAT
from migration import load_data
import asyncio

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger('main')


async def main():
    BASE_PATH = Path(__file__).parent.parent
    
    db_file_path = BASE_PATH / 'data' / 'garden.db'
    plants_csv_file = BASE_PATH / 'plants_registry.csv'
    plants_zones_cvl_file = BASE_PATH / 'plants_zones_registry.csv'
    
    load_data(str(plants_csv_file), str(plants_zones_cvl_file), str(db_file_path))
    
    await start_gardening(db_file_path)

async def start_gardening(db_file_path):
    plant_repository = PlantRepository(str(db_file_path))
    my_garden = plant_repository.get_all()
    
    plant_zone_repository = PlantZoneRepository(str(db_file_path))
    plant_zones = plant_zone_repository.get_all()
    
    for plant_zone in plant_zones:
        plant_zone.plants = [p for p in my_garden if plant_zone.id == p.zone_id]
        
    gardner = Gardener("Silvano")
    logger.info(f"{gardner}")

    gardner.move_to_garden(my_garden)

    """Starts the gardener's main work cycle.

    Performs maintenance tasks continuously every 10 seconds.
    This method is asynchronous and can be interrupted with Ctrl+C.
    """
    while True:
        for plant_zone in plant_zones:
            plant_zone.read_sensors()
        
        await gardner.perform_maintenance()
        
        for plant_zone in plant_zones:
            if plant_zone.is_dirty:
                plant_zone_repository.save(plant_zone)
            
            for plant in plant_zone.plants:
                if plant.is_dirty:
                    plant_repository.save(plant)

        logger.info("Ciclo di manutenzione terminato.")
        await asyncio.sleep(GARDENER_IDLE_TIME)
        
if __name__ == "__main__":
    asyncio.run(main())
