from pathlib import Path
from csv import DictReader
from datetime import datetime, timedelta
from gardener import Gardener
from Plant.plant import Plant
from globals import DATE_FORMAT
import random
import asyncio


def init_from_file(file_name: str) -> list[Plant]:
    garden: list[Plant] = []

    file_path = Path(__file__).parent / file_name

    try:
        with open(file_path, "r", encoding="UTF-8") as plants_file:
            plants_reader = DictReader(plants_file)
            current_time = datetime.now()
            for stored_plant in plants_reader:
                try:
                    date_added = datetime.strptime(
                        stored_plant["Data inserimento"], DATE_FORMAT
                    )
                    plant = Plant(
                            int(stored_plant["ID"]),
                            stored_plant["Specie"],
                            date_added,
                            current_time - timedelta(minutes=random.randint(0, 8)),
                            current_time - timedelta(minutes=random.randint(0, 8)),
                            current_time - timedelta(minutes=random.randint(0, 8)),
                            [],
                        )
                    plant.inspect()
                    garden.append(plant)
                except (KeyError, ValueError) as e:
                    print(f"Skipping invalid row: {e}")
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"Error reading file {file_name}: {e}")

    return garden

async def main():
    my_garden = init_from_file("plants_registry.csv")

    print(f"The garden has {len(my_garden)} plants.")
        
    gardner = Gardener("Silvano")
    print(f"{gardner}")

    gardner.move_to_garden(my_garden)

    await gardner.start_working()
            
    for plant in my_garden:
        print(f"{plant}")
        
if __name__ == "__main__":
    asyncio.run(main())
