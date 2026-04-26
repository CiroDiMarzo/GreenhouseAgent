import sqlite3
import logging
from datetime import datetime

from Plant.plant import Plant
from Plant.plant_status import PlantStatus
from globals import DATE_FORMAT, LOG_FORMAT

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
# Configurazione logging
logger = logging.getLogger(__name__)


class PlantRepository:
    def __init__(self, db_path: str):
        """Inizializza il repository con il percorso del database.

        Args:
            db_path: Percorso del file database SQLite

        Raises:
            ValueError: Se db_path è vuoto o None
            sqlite3.Error: Se non è possibile connettersi al database
        """
        if not db_path:
            raise ValueError("db_path non può essere vuoto")

        self.db_path = db_path
        try:
            self._init_db()
            logger.info(f"Repository inizializzato correttamente con db: {db_path}")
        except sqlite3.Error as e:
            logger.error(f"Errore durante l'inizializzazione del database: {e}")
            raise

    def _init_db(self):
        """Inizializza la tabella Plant nel database se necessario.

        Raises:
            sqlite3.Error: Se si verifica un errore durante la creazione della tabella
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
                        date_watered TEXT,
                        date_fertilized TEXT,
                        date_cured TEXT,
                        status TEXT
                    )
                """
                )
                connection.commit()
                logger.debug("Tabella plants creata o già esistente")
        except sqlite3.Error as e:
            logger.error(f"Errore nella inizializzazione del database: {e}")
            raise

    def save(self, plant: Plant):
        """Salva o aggiorna una pianta nel database.

        Args:
            plant: Istanza di Plant da salvare

        Raises:
            TypeError: Se plant non è un'istanza di Plant
            ValueError: Se plant non contiene dati validi
            sqlite3.Error: Se si verifica un errore durante il salvataggio
        """
        if not isinstance(plant, Plant):
            raise TypeError(f"Expected Plant object, got {type(plant).__name__}")

        try:
            # Convertiamo la lista di Enum in una stringa separata da virgole
            status_str = ",".join(s.value for s in plant.status) if plant.status else ""

            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO plants 
                    (id, specie, date_added, date_watered, date_fertilized, date_cured, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        plant.id,
                        plant.specie,
                        plant.date_added.strftime(DATE_FORMAT),
                        plant.date_watered.strftime(DATE_FORMAT),
                        plant.date_fertilized.strftime(DATE_FORMAT),
                        plant.date_cured.strftime(DATE_FORMAT),
                        status_str,
                    ),
                )
                connection.commit()
                logger.info(f"Pianta con id {plant.id} salvata correttamente")
        except AttributeError as e:
            logger.error(f"Errore: Pianta mancante di attributo obbligatorio: {e}")
            raise ValueError(f"Plant non contiene tutti gli attributi necessari: {e}")
        except sqlite3.Error as e:
            logger.error(f"Errore durante il salvataggio della pianta: {e}")
            raise
        except Exception as e:
            logger.error(f"Errore inaspettato durante il salvataggio: {e}")
            raise

    def get_all(self) -> list[Plant]:
        """Recupera tutte le piante dal database.

        Returns:
            Lista di piante. Lista vuota se nessuna pianta trovata.

        Raises:
            sqlite3.Error: Se si verifica un errore durante la lettura dal database
            ValueError: Se i dati nel database sono corrotti
        """
        plant_list: list[Plant] = []
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("""SELECT * FROM plants""")
                rows = cursor.fetchall()

                for idx, row in enumerate(rows):
                    try:
                        status_list = [PlantStatus(s) for s in row[6].split(",") if s]
                        plant = Plant(
                            id=int(row[0]),
                            specie=row[1],
                            date_added=datetime.strptime(row[2], DATE_FORMAT),
                            date_watered=datetime.strptime(row[3], DATE_FORMAT),
                            date_fertilized=datetime.strptime(row[4], DATE_FORMAT),
                            date_cured=datetime.strptime(row[5], DATE_FORMAT),
                            status=status_list,
                        )
                        plant_list.append(plant)
                    except (ValueError, KeyError) as e:
                        logger.warning(
                            f"Errore nel parsing della riga {idx}: {e}. Riga saltata."
                        )
                        continue
                    except Exception as e:
                        logger.error(
                            f"Errore inaspettato nel parsing della riga {idx}: {e}"
                        )
                        raise

                logger.info(f"Recuperate {len(plant_list)} piante dal database")
        except sqlite3.Error as e:
            logger.error(f"Errore durante la lettura dal database: {e}")
            raise
        except Exception as e:
            logger.error(f"Errore inaspettato durante get_all: {e}")
            raise

        return plant_list

    def get_by_id(self, plant_id: int) -> Plant:
        """Recupera una pianta per ID dal database.

        Args:
            plant_id: ID della pianta da recuperare

        Returns:
            Istanza di Plant corrispondente all'ID

        Raises:
            TypeError: Se plant_id non è un intero
            ValueError: Se pianta con questo ID non esiste o dati corrotti
            sqlite3.Error: Se si verifica un errore durante la lettura dal database
        """
        if not isinstance(plant_id, int):
            raise TypeError(
                f"plant_id deve essere un intero, ricevuto {type(plant_id).__name__}"
            )

        if plant_id <= 0:
            raise ValueError(f"plant_id deve essere positivo, ricevuto {plant_id}")

        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("""SELECT * FROM plants WHERE id = ?""", (plant_id,))
                row = cursor.fetchone()

                if row is None:
                    logger.warning(f"Pianta con id {plant_id} non trovata")
                    raise ValueError(f"Plant with id {plant_id} not found")

                try:
                    status_list = [PlantStatus(s) for s in row[6].split(",") if s]
                    plant = Plant(
                        id=int(row[0]),
                        specie=row[1],
                        date_added=datetime.strptime(row[2], DATE_FORMAT),
                        date_watered=datetime.strptime(row[3], DATE_FORMAT),
                        date_fertilized=datetime.strptime(row[4], DATE_FORMAT),
                        date_cured=datetime.strptime(row[5], DATE_FORMAT),
                        status=status_list,
                    )
                    logger.info(f"Pianta con id {plant_id} recuperata correttamente")
                    return plant
                except (ValueError, KeyError) as e:
                    logger.error(
                        f"Errore nel parsing dei dati della pianta con id {plant_id}: {e}"
                    )
                    raise ValueError(
                        f"Dati corrotti per la pianta con id {plant_id}: {e}"
                    )
        except sqlite3.Error as e:
            logger.error(
                f"Errore durante la lettura della pianta con id {plant_id}: {e}"
            )
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Errore inaspettato durante get_by_id({plant_id}): {e}")
            raise
