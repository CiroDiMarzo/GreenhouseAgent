import logging

from Plant.plant import Plant
from PlantZone.plant_zone import PlantZone
from globals import LOG_FORMAT, MOISTURE_THRESHOLD

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


class Gardener:
    """It represents a gardener caring for plants in a vegetable garden.

    The gardener regularly inspects the plants and performs maintenance tasks
    (watering, fertilizing, pesticide application) based on the health status
    of each plant. Changes are persisted in the database via PlantRepository.
    """

    # Logger for tracking gardener operations
    logger = logging.getLogger("Gardener")

    def __init__(self, name: str):
        """Initialize a new gardener.

                Args:
                    name: Gardener's name
        plant_repository: Repository for plant persistence in the database
        """
        self.name: str = name
        """Identifier name of the gardener"""
        self.garden: list[Plant] = []
        """List of plants currently under this gardener's care"""

    def __str__(self) -> str:
        """Returns a text representation of the gardener.

        Returns:
            Gardener's introduction string
        """
        return f"Hello, I'm {self.name}"

    def move_to_garden(self, garden: list[Plant]) -> None:
        """Assign a garden to the gardener.

        Args:
            garden: List of plants that make up the garden
        """
        self.garden = garden
        self.logger.info(f"{self.name} moves in the garden.")

    def leave_garden(self) -> None:
        """Removes the gardener from the garden."""
        self.garden = []
        self.logger.info(f"{self.name} leaves the garden.")

    async def perform_maintenance(self, plant_zone: PlantZone) -> None:
        """Performs the maintenance cycle on all plants in the garden.

        Identifies plants that need watering and proceeds with irrigation.
        If the gardener is not assigned to any garden, the cycle is skipped.
        """
        if not self.garden:
            self.logger.warning(f"{self.name} is not in a garden")
            return

        if plant_zone.moisture <= MOISTURE_THRESHOLD:
            await self.open_faucet(plant_zone, 0.2)

    async def open_faucet(self, plant_zone: PlantZone, water_qty: float) -> None:
        """Opens the faucet to water the zone and updates the last watering date.

        Note: This method will update the plant database and in the future will drop
        a message in a queue that will be read by another async system to
        open the corresponding electro-magnetic valve.
        """
        plant_zone.moisture = MOISTURE_THRESHOLD * 1.3
        self.logger.info(f"Watering zone {plant_zone.name}: {plant_zone.moisture}")
