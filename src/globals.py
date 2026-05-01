"""Global configuration and utilities for the GreenhouseAgent application.

This module contains application-wide constants, logging configuration,
and utility functions used throughout the project.
"""

from pathlib import Path
import random
import logging

# ============================================================================
# Physical paths to database and CSV files
# ============================================================================

BASE_PATH = Path(__file__).parent.parent
DB_FILE_PATH = BASE_PATH / 'data' / 'garden.db'
PLANTS_CVS_FILE = BASE_PATH / 'plants_registry.csv'
PLANT_ZONES_CVS_FILE = BASE_PATH / 'plants_zones_registry.csv'

# ============================================================================
# Date and Logging Format Constants
# ============================================================================

# Format string for datetime objects throughout the application
DATE_FORMAT = '%d/%m/%Y %H:%M:%S.%f'

# Format string for logging output (timestamp - level - class name - message)
LOG_FORMAT = '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'

# ============================================================================
# Timing Constants (in seconds)
# ============================================================================

# How long the gardener waits between maintenance cycles
GARDENER_IDLE_TIME = 5

# ============================================================================
# Biological thresholds of the plants
# ============================================================================

MOISTURE_THRESHOLD = 0.4

# ============================================================================
# Logging Configuration
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

def roll_dice(percent: int) -> bool:
    """Simulates a dice roll with a given probability of success.
    
    Generates a random number between 0 and 100 and returns True if it's
    less than or equal to the given percentage, False otherwise.
    
    Args:
        percent: Probability percentage (0-100). Values > 100 return False
                 and log a warning.
    
    Returns:
        True if random roll is <= percent, False otherwise
        
    Example:
        >>> if roll_dice(75):  # 75% chance of True
        ...     print("Success!")
    """
    if percent > 100:
        logger.warning(f"percent cannot be greater than 100: {percent}. Returning False.")
        return False
    
    result = random.randint(0, 100)
    
    return result <= percent