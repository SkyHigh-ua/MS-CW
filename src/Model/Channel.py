from enum import Enum
from typing import Optional
from Message import Message

class ChannelState(Enum):
    """Enum for channel states"""
    FREE = 1
    BUSY = 2
    FAILED = 3

class Channel:
    """Class representing transmission channel"""
    def __init__(self, name: str):
        self.name = name
        self.state = ChannelState.FREE
        self.current_message: Optional[Message] = None
        self.transmission_end = float('inf')
        self.recovery_time = float('inf')
        
         
        self.messages_processed: list[Message] = []
        self.total_busy_time = 0
        self.last_state_change = 0
        
    def is_free(self) -> bool:
        """Check if channel is free"""
        return self.state == ChannelState.FREE
        
    def is_busy(self) -> bool:
        """Check if channel is busy"""
        return self.state == ChannelState.BUSY
        
    def start_transmission(self, message: Message, current_time: float,
                         transmission_time: float):
        """Start message transmission"""
        self.state = ChannelState.BUSY
        self.current_message = message
        message.transmission_start = current_time
        self.transmission_end = current_time + transmission_time
        self._update_statistics(current_time)
        
    def complete_transmission(self, current_time: float):
        """Complete current transmission"""
        if self.current_message:
            self.current_message.transmission_end = current_time
            self.current_message.transmitted = True
            self.messages_processed.append(self.current_message)
            
        self.state = ChannelState.FREE
        self.current_message = None
        self.transmission_end = float('inf')
        self._update_statistics(current_time)
        
    def interrupt(self, current_time: float) -> Optional[Message]:
        """Interrupt current transmission"""
        message = self.current_message
        self.current_message = None
        self.transmission_end = float('inf')
        self._update_statistics(current_time)
        return message
        
    def fail(self, current_time: float):
        """Channel failure"""
        self.state = ChannelState.FAILED
        self._update_statistics(current_time)
        
    def schedule_recovery(self, recovery_time: float):
        """Schedule channel recovery"""
        self.recovery_time = recovery_time
        
    def recover(self, current_time: float):
        """Recover channel after failure"""
        self.state = ChannelState.FREE
        self.recovery_time = float('inf')
        self._update_statistics(current_time)
        
    def _update_statistics(self, current_time):
        """Update channel statistics"""
        if self.state == ChannelState.BUSY:
            self.total_busy_time += current_time - self.last_state_change
        self.last_state_change = current_time