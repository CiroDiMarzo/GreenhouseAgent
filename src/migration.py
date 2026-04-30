from datetime import datetime, timedelta
from pathlib import Path
from csv import DictReader
import logging
import random
import sqlite3

from Plant.plant import Plant
from Plant.plant_repository import PlantRepository
from PlantZone.plant_zone import PlantZone
from PlantZone.plant_zone_repository import PlantZoneRepository
from globals import DATE_FORMAT, LOG_FORMAT

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger('migration')


def load_data(
    csv_file_path: str, csv_zone_file_path: str, db_file_path: str
) -> None:
    """Migrate plants from CSV files to SQLite database.

    Args:
        csv_file_path: Path to the plants CSV file
        csv_zone_file_path: Path to the zones CSV file
        db_file_path: Path to the SQLite database file

    Raises:
        FileNotFoundError: If CSV or database files do not exist
        ImportError: If no zones are found in the zones CSV file
        ValueError: If CSV data format is invalid
        sqlite3.Error: If an error occurs during database operations
    """
    try:
        zones_list = read_zones(csv_zone_file_path)

        if not zones_list:
            raise ImportError(f"No zones found in {csv_zone_file_path}. Ensure the file contains zone data.")

        write_zones(db_file_path, zones_list)
        plant_list = read_garden(csv_file_path)
    except (FileNotFoundError, PermissionError, OSError, ValueError, ImportError) as e:
        logger.error(f"Error reading CSV files: {e}")
        raise

    write_garden(db_file_path, plant_list)


def write_garden(db_file_path: str, plant_list: list[Plant]) -> None:
    """Write plants to the database.

    Args:
        db_file_path: Path to the SQLite database file
        plant_list: List of Plant objects to save

    Raises:
        FileNotFoundError: If the database file does not exist
        sqlite3.Error: If a database error occurs during operation
    """
    if not Path(db_file_path).exists():
        logger.error(f"Database file not found: {db_file_path}")
        raise FileNotFoundError(f"Database file not found: {db_file_path}")

    try:
        plant_repository = PlantRepository(db_file_path)
    except sqlite3.Error as e:
        logger.error(f"Error initializing plant repository: {e}")
        raise

    plants_saved = 0
    plants_failed = 0

    for row_number, row in enumerate(plant_list, start=1):
        try:
            plant_repository.save(row)
            plants_saved += 1
        except (TypeError, ValueError, AttributeError) as e:
            plants_failed += 1
            species_name = row.specie if hasattr(row, 'specie') else 'unknown'
            logger.error(
                f"Error saving plant at row {row_number}: {e} - Species: {species_name}"
            )
        except sqlite3.Error as e:
            plants_failed += 1
            logger.error(
                f"Database error while saving plant at row {row_number}: {e}"
            )

    logger.info(
        f"Migration completed: {plants_saved} plants saved, {plants_failed} errors"
    )

def write_zones(db_file_path: str, zone_list: list[PlantZone]) -> None:
    """Write plant zones to the database.

    Args:
        db_file_path: Path to the SQLite database file
        zone_list: List of PlantZone objects to save

    Raises:
        sqlite3.Error: If a database error occurs during operation
        TypeError: If zone data types are invalid
    """
    try:
        plant_zone_repository = PlantZoneRepository(db_file_path)
    except sqlite3.Error as e:
        logger.error(f"Error initializing plant zone repository: {e}")
        raise

    plants_zones_saved = 0
    plants_zones_failed = 0
    
    for row_number, row in enumerate(zone_list, start=1):
        try:
            plant_zone_repository.save(row)
            plants_zones_saved += 1
        except (TypeError, ValueError, AttributeError) as e:
            plants_zones_failed += 1
            zone_name = row.name if hasattr(row, 'name') else 'unknown'
            logger.error(
                f"Error saving plant zone at row {row_number}: {e} - Zone: {zone_name}"
            )
        except sqlite3.Error as e:
            plants_zones_failed += 1
            logger.error(
                f"Database error while saving plant zone at row {row_number}: {e}"
            )

    logger.info(
        f"Migration completed: {plants_zones_saved} plant zones saved, {plants_zones_failed} errors"
    )

def read_garden(csv_file_path: str) -> list[Plant]:
    """Read plants from CSV file and convert to Plant objects.

    Args:
        csv_file_path: Path to the plants CSV file
        zone_id: Zone ID to assign to all plants

    Returns:
        List of Plant objects read from CSV

    Raises:
        FileNotFoundError: If the CSV file does not exist
        PermissionError: If file cannot be read due to permissions
        ValueError: If CSV data format is invalid or required fields are missing
        OSError: If a file system error occurs
    """
    if not Path(csv_file_path).exists():
        logger.error(f"CSV file not found: {csv_file_path}")
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

    plant_list: list[Plant] = []
    current_time = datetime.now()

    try:
        with open(csv_file_path, "r", encoding="UTF-8") as csv_file:
            reader = DictReader(csv_file)
            for line_number, line in enumerate(reader, start=2):
                try:
                    # Parse date added from CSV
                    date_added = datetime.strptime(
                        line["Data inserimento"], DATE_FORMAT
                    )

                    # Parse and validate plant ID
                    plant_id = int(line["ID"])

                    # Validate required 'Specie' field
                    specie = line.get("Specie", "").strip()
                    if not specie:
                        raise ValueError("'Specie' field is empty or missing")
                    
                    # Parse zone ID
                    zone_id = int(line["Zona"])

                    new_plant = Plant(
                        id=plant_id,
                        specie=specie,
                        date_added=date_added,
                        date_watered=current_time
                        - timedelta(minutes=random.randint(0, 8)),
                        date_cured=current_time
                        - timedelta(minutes=random.randint(0, 8)),
                        date_fertilized=current_time
                        - timedelta(minutes=random.randint(0, 8)),
                        status=[],
                        zone_id=int(zone_id),
                    )
                    plant_list.append(new_plant)

                except ValueError as e:
                    logger.error(
                        f"Error parsing row {line_number}: {e} - Data: {line}"
                    )
                    raise ValueError(
                        f"Invalid data at row {line_number}: {e}"
                    ) from e
                except KeyError as e:
                    logger.error(
                        f"Missing field at row {line_number}: {e} - Data: {line}"
                    )
                    raise ValueError(
                        f"Missing required field at row {line_number}: {e}"
                    ) from e

    except (FileNotFoundError, PermissionError, OSError) as exc:
        logger.error(f"Error accessing CSV file: {exc}")
        raise
    except ValueError as exc:
        logger.error(f"Error parsing CSV data: {exc}")
        raise

    logger.info(f"Plants read completed: {len(plant_list)} plants loaded")
    return plant_list


def read_zones(csv_zones_file_path: str) -> list[PlantZone]:
    """Read plant zones from CSV file and convert to PlantZone objects.

    Args:
        csv_zones_file_path: Path to the zones CSV file

    Returns:
        List of PlantZone objects read from CSV

    Raises:
        FileNotFoundError: If the CSV file does not exist
        ValueError: If CSV data format is invalid
        OSError: If a file system error occurs
    """
    plant_zone_list: list[PlantZone] = []

    if not Path(csv_zones_file_path).exists():
        logger.error(f"Zones CSV file not found: {csv_zones_file_path}")
        raise FileNotFoundError(f"Zones CSV file not found: {csv_zones_file_path}")

    try:
        with open(csv_zones_file_path, "r", encoding="UTF-8") as csv_file:
            reader = DictReader(csv_file)

            for row_number, row in enumerate(reader, start=2):
                try:
                    plant_zone_list.append(
                        PlantZone(
                            id=int(row["id"]),
                            name=row["name"],
                            moisture_level=float(row["moisture_level"]),
                        )
                    )
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing zone at row {row_number}: {e} - Data: {row}")
                    # Continue processing other zones if one fails
                    continue

    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f"Error reading zones CSV file: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading zones: {e}")
        raise

    logger.info(f"Zones read completed: {len(plant_zone_list)} zones loaded")
    return plant_zone_list