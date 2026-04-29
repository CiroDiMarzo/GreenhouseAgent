from datetime import datetime
import asyncio
import sqlite3
import logging

from Plant.plant_repository import PlantRepository
from Plant.plant_status import PlantStatus
from Plant.plant import Plant
from globals import LOG_FORMAT, GARDENER_IDLE_TIME

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


class Gardener:
    """Rappresenta un giardiniere che si prende cura delle piante in un orto.

    Il giardiniere ispeziona regolarmente le piante e esegue operazioni di manutenzione
    (innaffiatura, fertilizzazione, applicazione di pesticidi) in base allo stato di salute
    di ogni pianta. Le modifiche vengono persistite nel database tramite PlantRepository.
    """
    
    logger = logging.getLogger('Gardener')

    def __init__(self, name: str, plant_repository: PlantRepository):
        """Inizializza un nuovo giardiniere.

        Args:
            name: Nome del giardiniere
            plant_repository: Repository per la persistenza delle piante nel database
        """
        self.name = name
        self.garden: list[Plant] = []
        self.plant_repository = plant_repository

    def __str__(self) -> str:
        """Restituisce una rappresentazione testuale del giardiniere.

        Returns:
            Stringa di presentazione del giardiniere
        """
        return f"Hello, I'm {self.name}"

    def move_to_garden(self, garden: list[Plant]) -> None:
        """Assegna un orto al giardiniere.

        Args:
            garden: Lista di piante che compongono l'orto
        """
        self.garden = garden
        self.logger.info(f"{self.name} moves in the garden.")

    def leave_garden(self) -> None:
        """Rimuove il giardiniere dall'orto."""
        self.garden = []
        self.logger.info(f"{self.name} leaves the garden.")

    async def start_working(self) -> None:
        """Avvia il ciclo di lavoro principale del giardiniere.

        Esegue continuamente operazioni di manutenzione ogni 10 secondi.
        Questo metodo è asincrono e può essere interrotto con Ctrl+C.
        """
        while True:
            self.logger.info("-- Start working")
            await self.perform_maintenance()
            self.logger.info("-- Work concluded")
            # Attende un numero configurato secondi prima del prossimo ciclo di manutenzione
            await asyncio.sleep(GARDENER_IDLE_TIME)

    async def perform_maintenance(self) -> None:
        """Esegue ciclo di manutenzione su tutte le piante nell'orto.

        Per ogni pianta:
        1. Ispeziona lo stato di salute
        2. Esegue le operazioni necessarie (innaffiatura, fertilizzazione, pesticidi)
        3. Re-ispeziona lo stato
        4. Salva le modifiche nel database

        Se il giardiniere non è assegnato a nessun orto, la manutenzione viene saltata.
        Gli errori di salvataggio nel database vengono registrati ma non interrompono l'esecuzione.
        """
        # Verifica se il giardiniere è assegnato a un orto
        if not self.garden:
            self.logger.warning(f"{self.name} is not in a garden")
            return

        # Itera su tutte le piante nell'orto
        for row_num, plant in enumerate(self.garden):
            # Prima ispezione per valutare lo stato di salute
            plant.inspect()

            # Esecuzione delle operazioni di manutenzione in base allo stato
            if PlantStatus.THIRSTY in plant.status:
                await self.water_plant(plant)
            if PlantStatus.HUNGRY in plant.status:
                await self.fertilize_plant(plant)
            if PlantStatus.SICK in plant.status:
                await self.apply_pesticide(plant)

            # Re-ispezione dopo le operazioni di manutenzione
            plant.inspect()

            # Persistenza delle modifiche nel database
            try:
                self.plant_repository.save(plant)
            except (ValueError, sqlite3.Error) as exc:
                self.logger.error(
                    f"Errore durante il salvataggio della pianta {plant} alla riga {row_num}: {exc}"
                )

    async def water_plant(self, plant: Plant) -> None:
        """Innaffia una pianta e aggiorna la data dell'ultima innaffiatura.

        Args:
            plant: Pianta da innaffiare
        """
        plant.date_watered = datetime.now()
        self.logger.info(f"Watering plant {plant}")

    async def fertilize_plant(self, plant: Plant) -> None:
        """Fertilizza una pianta e aggiorna la data dell'ultima fertilizzazione.

        Args:
            plant: Pianta da fertilizzare
        """
        plant.date_fertilized = datetime.now()
        self.logger.info(f"Fertilizing plant {plant}")

    async def apply_pesticide(self, plant: Plant) -> None:
        """Applica pesticida a una pianta e aggiorna la data dell'ultima applicazione.

        Args:
            plant: Pianta da curare con pesticida
        """
        plant.date_cured = datetime.now()
        self.logger.info(f"Applying pesticide to plant {plant}")
