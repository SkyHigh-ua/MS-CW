from collections import deque
from typing import Optional
from Message import Message

class Queue:
    """Class representing message queue"""
    def __init__(self):
        self.messages = deque()
        self.max_length = 0
        self.total_wait_time = 0
        
    def put(self, message: Message):
        """Add message to queue"""
        self.messages.append(message)
        self.max_length = max(self.max_length, len(self.messages))
        
    def get(self) -> Optional[Message]:
        """Get next message from queue"""
        if self.messages:
            return self.messages.popleft()
        return None
        
    def __len__(self):
        return len(self.messages)