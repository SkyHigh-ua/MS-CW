from dataclasses import dataclass

@dataclass
class Message:
    """Class representing a message in the system"""
    arrival_time: float
    transmission_start: float = 0
    transmission_end: float = 0
    transmitted: bool = False
    
    def get_transmission_time(self) -> float:
        """Get total transmission time"""
        if not self.transmitted:
            return -1
        return self.transmission_end - self.transmission_start