import sqlite3
import logging
from datetime import datetime

from Plant.plant import Plant
from Plant.plant_status import PlantStatus
from globals import DATE_FORMAT, LOG_FORMAT

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


class PlantRepository:
    logger = logging.getLogger('PlantRepository')
    
    def __init__(self, db_path: str):
        """Initializes the repository with the database path.

        Args:
            db_path: Path to the SQLite database file

        Raises:
            ValueError: If db_path is empty or None
            sqlite3.Error: If unable to connect to the database
        """
        if not db_path:
            raise ValueError("db_path cannot be empty")

        self.db_path = db_path
        try:
            self._init_db()
        except sqlite3.Error as e:
            self.logger.error(f"Error during database initialization: {e}")
            raise

    def _init_db(self):
        """Initializes the Plant table in the database if necessary.

        Raises:
            sqlite3.Error: If an error occurs during table creation
        """
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS plants (
                        id INTEGER PRIMARY KEY,
                        specie TEXT NOT NULL,
                        date_added TEXT,
                        status TEXT
                    )
                    """
                )
                # Check if zone_id column already exists
                cursor.execute("PRAGMA table_info(plants)")
                columns = {row[1] for row in cursor.fetchall()}
                
                if "zone_id" not in columns:
                    cursor.execute(
                        """
                        ALTER TABLE plants ADD COLUMN zone_id INTEGER REFERENCES plant_zones(id);
                        """
                    )
                
                connection.commit()
                self.logger.debug("plants table created or already exists")
        except sqlite3.Error as e:
            self.logger.error(f"Error initializing the database: {e}")
            raise

    def save(self, plant: Plant):
        """Saves or updates a plant in the database, but only if the entity is dirty.

        Args:
            plant: Plant instance to save

        Raises:
            TypeError: If plant is not a Plant instance
            ValueError: If plant does not contain valid data
            sqlite3.Error: If an error occurs during saving
        """
        if not isinstance(plant, Plant):
            raise TypeError(f"Expected Plant object, got {type(plant).__name__}")

        try:
            # Convert the Enum list into a comma-separated string
            status_str = ",".join(s.value for s in plant.status) if plant.status else ""

            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO plants 
                    (id, specie, date_added, status, zone_id)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        plant.id,
                        plant.specie,
                        plant.date_added.strftime(DATE_FORMAT),
                        status_str,
                        plant.zone_id
                    ),
                )
                connection.commit()
                plant.is_dirty = False
                
                self.logger.info(f"Plant with id {plant.id} saved successfully")
        except AttributeError as e:
            self.logger.error(f"Error: {self.__class__.__name__} missing required attribute: {e}")
            raise ValueError(f"{self.__class__.__name__} does not contain all necessary attributes: {e}")
        except sqlite3.Error as e:
            self.logger.error(f"Error during {self.__class__.__name__} saving: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during saving: {e}")
            raise

    def get_all(self) -> list[Plant]:
        """Retrieves all plants from the database.

        Returns:
            List of plants. Empty list if no plants found.

        Raises:
            sqlite3.Error: If an error occurs during reading from the database
            ValueError: If data in the database is corrupted
        """
        plant_list: list[Plant] = []
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("""SELECT * FROM plants""")
                rows = cursor.fetchall()

                for idx, row in enumerate(rows):
                    try:
                        status_list = [PlantStatus(s) for s in row[3].split(",") if s]
                        plant = Plant(
                            id=int(row[0]),
                            specie=row[1],
                            date_added=datetime.strptime(row[2], DATE_FORMAT),
                            status=status_list,
                            zone_id=int(row[4])
                        )
                        plant_list.append(plant)
                    except (ValueError, KeyError) as e:
                        self.logger.warning(
                            f"Error parsing row {idx}: {e}. Row skipped."
                        )
                        continue
                    except Exception as e:
                        self.logger.error(
                            f"Unexpected error parsing row {idx}: {e}"
                        )
                        raise

                self.logger.info(f"Retrieved {len(plant_list)} plants from the database")
        except sqlite3.Error as e:
            self.logger.error(f"Error during reading from the database: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during get_all: {e}")
            raise

        return plant_list

    def get_by_id(self, plant_id: int) -> Plant:
        """Retrieves a plant by ID from the database.

        Args:
            plant_id: ID of the plant to retrieve

        Returns:
            Plant instance corresponding to the ID

        Raises:
            TypeError: If plant_id is not an integer
            ValueError: If plant with this ID does not exist or data is corrupted
            sqlite3.Error: If an error occurs during reading from the database
        """
        if not isinstance(plant_id, int):
            raise TypeError(
                f"plant_id must be an integer, received {type(plant_id).__name__}"
            )

        if plant_id <= 0:
            raise ValueError(f"plant_id must be positive, received {plant_id}")

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("""SELECT * FROM plants WHERE id = ?""", (plant_id,))
                row = cursor.fetchone()

                if row is None:
                    self.logger.warning(f"Plant with id {plant_id} not found")
                    raise ValueError(f"Plant with id {plant_id} not found")

                try:
                    status_list = [PlantStatus(s) for s in row[3].split(",") if s]
                    plant = Plant(
                        id=int(row[0]),
                        specie=row[1],
                        date_added=datetime.strptime(row[2], DATE_FORMAT),
                        status=status_list,
                        zone_id=int(row[4])
                    )
                    self.logger.info(f"Plant with id {plant_id} retrieved successfully")
                    return plant
                except (ValueError, KeyError) as e:
                    self.logger.error(
                        f"Error parsing data for plant with id {plant_id}: {e}"
                    )
                    raise ValueError(
                        f"Corrupted data for plant with id {plant_id}: {e}"
                    )
        except sqlite3.Error as e:
            self.logger.error(
                f"Error during reading plant with id {plant_id}: {e}"
            )
            raise
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during get_by_id({plant_id}): {e}")
            raise
