from datetime import datetime

class MoistureSensor:
    def __init__(self, id: int, last_reading_time: datetime, last_reading: float = 0.6):
        self.id = id
        self.last_reading = last_reading
        self.last_reading_time = last_reading_time
        
    def get_reading(self) -> float:
        # Qui in futuro ci sarà:
        # value = bus.read_adc(CHANNEL_0)
        # self.last_reading = translate_to_percentage(value)
        
        self.last_reading = max(0, self.last_reading - 0.05)
        self.last_reading_time = datetime.now()
        
        return self.last_reading