import sqlite3
import logging
from datetime import datetime

from Sensor.moisture_sensor import MoistureSensor
from globals import DATE_FORMAT, LOG_FORMAT

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


class MoistureSensorRepository:
    logger = logging.getLogger("MoistureSensorRepository")

    def __init__(self, db_path: str):
        """Initializes the repository with the database path.

        Args:
            db_path: Path to the SQLite database file

        Raises:
            ValueError: If db_path is empty or None
            sqlite3.Error: If unable to connect to the database
        """
        if not db_path:
            raise ValueError(
                "Database path cannot be empty or None. Please provide a valid path to the SQLite database file."
            )

        self.db_path = db_path

        try:
            self._init_db()
        except sqlite3.Error as e:
            self.logger.error(f"Failed to initialize database at {db_path}: {e}")
            raise sqlite3.Error(
                f"Unable to initialize MoistureSensorRepository with database file '{db_path}'. "
                f"Database error: {str(e)}"
            )

    def _init_db(self):
        """Initializes the MoistureSensor table in the database if necessary.

        Raises:
            sqlite3.Error: If an error occurs during table creation
        """
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS moisture_sensors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        last_reading REAL DEFAULT 0.6,
                        last_reading_time TEXT NOT NULL
                    );
                    """)
                connection.commit()
                self.logger.debug("moisture_sensors table created or already exists")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create moisture_sensors table in database: {e}")
            raise sqlite3.Error(
                f"Unable to initialize database schema. Failed to create 'moisture_sensors' table. "
                f"Database error: {str(e)}"
            )

    def save(self, moisture_sensor: MoistureSensor):
        """Saves or updates a moisture sensor in the database.

        Args:
            moisture_sensor: MoistureSensor instance to save

        Raises:
            TypeError: If moisture_sensor is not a MoistureSensor instance
            ValueError: If moisture_sensor does not contain valid data
            sqlite3.Error: If an error occurs during saving
        """
        if not isinstance(moisture_sensor, MoistureSensor):
            raise TypeError(
                f"Expected {self.__class__.__name__} instance, got {type(moisture_sensor).__name__}. "
                f"Please ensure you are passing a valid {self.__class__.__name__} object."
            )

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO moisture_sensors 
                    (id, last_reading, last_reading_time)
                    VALUES (?, ?, ?)
                    """,
                    (
                        moisture_sensor.id,
                        moisture_sensor.last_reading,
                        moisture_sensor.last_reading_time.strftime(DATE_FORMAT),
                    ),
                )
                connection.commit()
                self.logger.info(
                    f"Moisture sensor with id {moisture_sensor.id} saved successfully"
                )
        except AttributeError as e:
            self.logger.error(
                f"Error: {self.__class__.__name__} missing required attribute: {e}"
            )
            raise ValueError(
                f"{self.__class__.__name__} does not contain all necessary attributes: {e}"
            )
        except sqlite3.Error as e:
            self.logger.error(f"Error during {self.__class__.__name__} saving: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during saving: {e}")
            raise

    def get_by_id(self, sensor_id: int) -> MoistureSensor:
        """Retrieves a moisture sensor by ID from the database.

        Args:
            sensor_id: ID of the moisture sensor to retrieve

        Returns:
            MoistureSensor instance corresponding to the ID

        Raises:
            TypeError: If sensor_id is not an integer
            ValueError: If moisture sensor with this ID does not exist or data is corrupted
            sqlite3.Error: If an error occurs during reading from the database
        """
        if not isinstance(sensor_id, int):
            raise TypeError(
                f"sensor_id must be an integer, received {type(sensor_id).__name__}"
            )

        if sensor_id <= 0:
            raise ValueError(f"sensor_id must be positive, received {sensor_id}")

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """SELECT * FROM moisture_sensors WHERE id = ?""", (sensor_id,)
                )
                row = cursor.fetchone()

                if row is None:
                    self.logger.warning(f"Moisture sensor with id {sensor_id} not found")
                    raise ValueError(f"Moisture sensor with id {sensor_id} not found")

                try:
                    moisture_sensor = MoistureSensor(
                        id=int(row[0]),
                        last_reading=float(row[1]),
                        last_reading_time=datetime.strptime(row[2], DATE_FORMAT),
                    )
                    self.logger.info(
                        f"Moisture sensor with id {sensor_id} retrieved successfully"
                    )
                    return moisture_sensor
                except (ValueError, KeyError) as e:
                    self.logger.error(
                        f"Error parsing data for moisture sensor with id {sensor_id}: {e}"
                    )
                    raise ValueError(
                        f"Corrupted data for moisture sensor with id {sensor_id}: {e}"
                    )
        except sqlite3.Error as e:
            self.logger.error(
                f"Error during reading moisture sensor with id {sensor_id}: {e}"
            )
            raise
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during get_by_id({sensor_id}): {e}")
            raise

    def get_all(self) -> list[MoistureSensor]:
        """Retrieves all moisture sensors from the database.

        Returns:
            List of moisture sensors. Empty list if no moisture sensors found.

        Raises:
            sqlite3.Error: If an error occurs during reading from the database
            ValueError: If data in the database is corrupted
        """

        moisture_sensors: list[MoistureSensor] = []

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("""SELECT * FROM moisture_sensors""")
                rows = cursor.fetchall()

                if not rows:
                    self.logger.warning(f"The moisture_sensors table is empty")
                    raise ValueError(f"The moisture_sensors table is empty")

                for idx, row in enumerate(rows):
                    try:
                        moisture_sensor = MoistureSensor(
                            id=int(row[0]),
                            last_reading=float(row[1]),
                            last_reading_time=datetime.strptime(row[2], DATE_FORMAT),
                        )
                        moisture_sensors.append(moisture_sensor)
                    except (ValueError, KeyError) as e:
                        self.logger.error(
                            f"Error parsing data for moisture sensor at row number '{idx}': {e}"
                        )
                        raise ValueError(
                            f"Corrupted data for moisture sensor at row number '{idx}': {e}"
                        )
                self.logger.info(
                    f"Retrieved {len(moisture_sensors)} moisture sensors from the database"
                )
        except sqlite3.Error as e:
            self.logger.error(f"Error during reading moisture sensors: {e}")
            raise
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during get_all(): {e}")
            raise

        return moisture_sensors
