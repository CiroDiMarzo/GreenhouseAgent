from enum import Enum

class PlantStatus(Enum):
    """Enumeration of possible plant health statuses."""
    THIRSTY = 'thirsty'
    HUNGRY = 'hungry'
    HEALTHY = 'healthy'
    SICK = 'sick'