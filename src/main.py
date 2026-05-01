from pathlib import Path
import logging
from Plant.plant_repository import PlantRepository
from PlantZone.plant_zone_repository import PlantZoneRepository
from gardener import Gardener
from globals import (
    GARDENER_IDLE_TIME,
    LOG_FORMAT,
    DB_FILE_PATH,
    PLANTS_CVS_FILE,
    PLANT_ZONES_CVS_FILE
)
from migration import load_data
import asyncio

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger('main')


async def main():
    
    load_data(str(PLANTS_CVS_FILE), str(PLANT_ZONES_CVS_FILE), str(DB_FILE_PATH))
    
    await start_gardening(DB_FILE_PATH)

async def start_gardening(DB_FILE_PATH):
    plant_repository = PlantRepository(str(DB_FILE_PATH))
    my_garden = plant_repository.get_all()
    
    plant_zone_repository = PlantZoneRepository(str(DB_FILE_PATH))
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
            await plant_zone.read_sensors()
        
        for plant_zone in plant_zones:
            await gardner.perform_maintenance(plant_zone)
        
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
