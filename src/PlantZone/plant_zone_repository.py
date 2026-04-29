import sqlite3
import logging
from datetime import datetime

from PlantZone.plant_zone import PlantZone
from globals import DATE_FORMAT, LOG_FORMAT

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT
)

class PlantZoneRepository:
    logger = logging.getLogger('PlantZoneRepository')
    
    def __init__(self, db_path: str):
        
        if not db_path:
            raise ValueError(
                "Database path cannot be empty or None. Please provide a valid path to the SQLite database file."
            )
        
        self.db_path = db_path
        
        try:
            self.__init__db()
        except sqlite3.Error as e:
            self.logger.error(f"Failed to initialize database at {db_path}: {e}")
            raise sqlite3.Error(
                f"Unable to initialize PlantRepository with database file '{db_path}'. "
                f"Database error: {str(e)}"
            )
        
    def __init__db(self):
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS plant_zones (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        moisture_level REAL DEFAULT 0.0
                    );
                    """
                )
                connection.commit()
                self.logger.debug("plant_zones table created or already exists")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create plant_zones table in database: {e}")
            raise sqlite3.Error(
                f"Unable to initialize database schema. Failed to create 'plant_zones' table. "
                f"Database error: {str(e)}"
            )
            
    def save(self, plant_zone: PlantZone):
        if not isinstance(plant_zone, PlantZone):
            raise TypeError(
                f"Expected {self.__class__.__name__} instance, got {type(plant_zone).__name__}. "
                f"Please ensure you are passing a valid {self.__class__.__name__} object."
            )
        
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO plant_zones 
                    (id, name, moisture_level)
                    VALUES (?, ?, ?)
                    """,
                    (
                        plant_zone.id,
                        plant_zone.name,
                        plant_zone.moisture_level
                    ),
                )
                connection.commit()
                self.logger.info(f"Plant zone with id {plant_zone.id} saved successfully")
        except AttributeError as e:
            self.logger.error(f"Error: {self.__class__.__name__} missing required attribute: {e}")
            raise ValueError(f"{self.__class__.__name__} does not contain all necessary attributes: {e}")
        except sqlite3.Error as e:
            self.logger.error(f"Error during {self.__class__.__name__} saving: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during saving: {e}")
            raise

    def get_by_id(self, zone_id: int) -> PlantZone:
        """Retrieves a plant zone by ID from the database.

        Args:
            zone_id: ID of the plant zone to retrieve

        Returns:
            PlantZone instance corresponding to the ID

        Raises:
            TypeError: If zone_id is not an integer
            ValueError: If plant zone with this ID does not exist or data is corrupted
            sqlite3.Error: If an error occurs during reading from the database
        """
        if not isinstance(zone_id, int):
            raise TypeError(
                f"zone_id must be an integer, received {type(zone_id).__name__}"
            )

        if zone_id <= 0:
            raise ValueError(f"zone_id must be positive, received {zone_id}")

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("""SELECT * FROM plant_zones WHERE id = ?""", (zone_id,))
                row = cursor.fetchone()

                if row is None:
                    logger.warning(f"Plant zone with id {zone_id} not found")
                    raise ValueError(f"Plant zone with id {zone_id} not found")

                try:
                    plant_zone = PlantZone(
                        id=int(row[0]),
                        name=row[1],
                        moisture_level=float(row[2])
                    )
                    logger.info(f"Plant zone with id {zone_id} retrieved successfully")
                    return plant_zone
                except (ValueError, KeyError) as e:
                    logger.error(
                        f"Error parsing data for plant zone with id {zone_id}: {e}"
                    )
                    raise ValueError(
                        f"Corrupted data for plant zone with id {zone_id}: {e}"
                    )
        except sqlite3.Error as e:
            logger.error(
                f"Error during reading plant zone with id {zone_id}: {e}"
            )
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during get_by_id({zone_id}): {e}")
            raise

    def get_by_name(self, zone_name: str) -> PlantZone:
        """Retrieves a plant zone by name from the database.

        Args:
            zone_name: Name of the plant zone to retrieve

        Returns:
            PlantZone instance corresponding to the name

        Raises:
            TypeError: If zone_name is not a string
            ValueError: If plant zone with this name does not exist or data is corrupted
            sqlite3.Error: If an error occurs during reading from the database
        """
        if not isinstance(zone_name, str):
            raise TypeError(
                f"zone_name must be a string, received {type(zone_name).__name__}"
            )

        if not zone_name or not zone_name.strip():
            raise ValueError(
                f"zone_name cannot be empty or contain only whitespace"
            )

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("""SELECT * FROM plant_zones WHERE name = ?""", (zone_name,))
                row = cursor.fetchone()

                if row is None:
                    logger.warning(f"Plant zone with name '{zone_name}' not found")
                    raise ValueError(f"Plant zone with name '{zone_name}' not found")

                try:
                    plant_zone = PlantZone(
                        id=int(row[0]),
                        name=row[1],
                        moisture_level=float(row[2])
                    )
                    logger.info(f"Plant zone with name '{zone_name}' retrieved successfully")
                    return plant_zone
                except (ValueError, KeyError) as e:
                    logger.error(
                        f"Error parsing data for plant zone with name '{zone_name}': {e}"
                    )
                    raise ValueError(
                        f"Corrupted data for plant zone with name '{zone_name}': {e}"
                    )
        except sqlite3.Error as e:
            logger.error(
                f"Error during reading plant zone with name '{zone_name}': {e}"
            )
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during get_by_name('{zone_name}'): {e}")
            raise