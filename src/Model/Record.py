from dataclasses import dataclass

@dataclass
class TransmissionRecord:
    """Record of single message transmission"""
    start_time: float
    end_time: float = 0
    channel: str = ''
    completed: bool = False
    
    @property
    def transmission_time(self) -> float:
        """Get total transmission time if completed"""
        if not self.completed:
            return -1
        return self.end_time - self.start_time