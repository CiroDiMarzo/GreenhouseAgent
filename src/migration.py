from datetime import datetime, timedelta
from pathlib import Path
from csv import DictReader
import logging
import random
import sqlite3

from Plant.plant import Plant
from Plant.plant_repository import PlantRepository
from globals import DATE_FORMAT, LOG_FORMAT

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

def migrate_plants(csv_file_path: str, db_file_path: str) -> None:
    """Migra le piante dal file CSV al database SQLite.
    
    Args:
        csv_file_path: Percorso del file CSV di origine
        db_file_path: Percorso del database SQLite di destinazione
        
    Raises:
        FileNotFoundError: Se il file CSV non esiste
        sqlite3.Error: Se si verifica un errore durante il salvataggio nel database
    """
    try:
        plant_list = read_garden(csv_file_path)
    except (FileNotFoundError, PermissionError, OSError, ValueError) as e:
        logger.error(f"Errore nella lettura del file CSV: {e}")
        raise
    
    write_garden(db_file_path, plant_list)

def write_garden(db_file_path, plant_list):
    if not Path(db_file_path).exists():
        logger.error(f"File database non trovato: {db_file_path}")
        raise FileNotFoundError(f"File database non trovato: {db_file_path}")
    
    try:
        plant_repository = PlantRepository(db_file_path)
    except sqlite3.Error as e:
        logger.error(f"Errore nell'inizializzazione del repository: {e}")
        raise
    
    plants_saved = 0
    plants_failed = 0
    
    for row_number, row in enumerate(plant_list, start=1):
        try:
            plant_repository.save(row)
            plants_saved += 1
        except (TypeError, ValueError, AttributeError) as e:
            plants_failed += 1
            logger.error(f"Errore nel salvataggio della pianta alla riga {row_number}: {e} - Pianta: {row.specie if hasattr(row, 'specie') else 'sconosciuta'}")
        except sqlite3.Error as e:
            plants_failed += 1
            logger.error(f"Errore database durante il salvataggio della pianta alla riga {row_number}: {e}")
    
    logger.info(f"Migrazione completata: {plants_saved} piante salvate, {plants_failed} errori")
    

def read_garden(csv_file_path: str) -> list[Plant]:
    """Legge le piante dal file CSV e le converte in oggetti Plant.
    
    Args:
        csv_file_path: Percorso del file CSV
        
    Returns:
        Lista di oggetti Plant letti dal CSV
        
    Raises:
        FileNotFoundError: Se il file CSV non esiste
        PermissionError: Se non ci sono permessi di lettura
        ValueError: Se il formato dei dati non è valido
        OSError: Se si verifica un errore nel sistema dei file
    """
    if not Path(csv_file_path).exists():
        logger.error(f"File CSV non trovato: {csv_file_path}")
        raise FileNotFoundError(f"File CSV non trovato: {csv_file_path}")
    
    plant_list: list[Plant] = []
    current_time = datetime.now()
    
    try:
        with open(csv_file_path, 'r', encoding='UTF-8') as csv_file:
            reader = DictReader(csv_file)
            for line_number, line in enumerate(reader, start=2):
                try:
                    # Parsing della data
                    date_added = datetime.strptime(line['Data inserimento'], DATE_FORMAT)
                    
                    # Parsing dell'ID
                    plant_id = int(line['ID'])
                    
                    # Validazione dei campi obbligatori
                    specie = line.get('Specie', '').strip()
                    if not specie:
                        raise ValueError("Campo 'Specie' vuoto o mancante")
                    
                    new_plant = Plant(
                        id=plant_id,
                        specie=specie,
                        date_added=date_added,
                        date_watered=current_time - timedelta(minutes=random.randint(0, 8)),
                        date_cured=current_time - timedelta(minutes=random.randint(0, 8)),
                        date_fertilized=current_time - timedelta(minutes=random.randint(0, 8)),
                        status=[]
                    )
                    new_plant.inspect()
                    plant_list.append(new_plant)
                    
                except ValueError as e:
                    logger.error(f"Errore nel parsing della riga {line_number}: {e} - Dati: {line}")
                    raise ValueError(f"Dati invalidi alla riga {line_number}: {e}") from e
                except KeyError as e:
                    logger.error(f"Campo mancante alla riga {line_number}: {e} - Dati: {line}")
                    raise ValueError(f"Campo mancante alla riga {line_number}: {e}") from e
                    
    except (FileNotFoundError, PermissionError, OSError) as exc:
        logger.error(f"Errore nell'accesso al file CSV: {exc}")
        raise
    except ValueError as exc:
        logger.error(f"Errore nel parsing del CSV: {exc}")
        raise
    
    logger.info(f"Lettura completata: {len(plant_list)} piante caricate dal CSV")
    return plant_list

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
                    logger.warning(f"Skipping invalid row: {e}")
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f"Error reading file {file_name}: {e}")

    return garden