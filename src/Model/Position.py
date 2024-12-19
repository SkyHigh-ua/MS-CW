class Position:
    """Class representing Petri net position"""
    def __init__(self, name: str, tokens: int = 0):
        self.name = name
        self.tokens = tokens
        self.total_tokens = tokens
        self.total_busy_time = 0.0
        self.last_change_time = 0.0
        self.max_tokens = tokens
    
    def add_tokens(self, count: int, current_time: float):
        """
        Add tokens to position and update statistics
        Args:
            count: number of tokens to add
            current_time: current simulation time
        """
        self.update_busy_time(current_time)
        self.tokens += count
        self.total_tokens += count
        self.max_tokens = max(self.max_tokens, self.tokens)
        
    def remove_tokens(self, count: int, current_time: float):
        """
        Remove tokens from position and update statistics
        Args:
            count: number of tokens to remove
            current_time: current simulation time
        """
        self.update_busy_time(current_time)
        self.tokens -= count
        
    def has_tokens(self, count: int) -> bool:
        """Check if position has required number of tokens"""
        return self.tokens >= count if count > 0 else False
    
    def update_busy_time(self, current_time: float):
        """Update busy time statistics"""
        if self.tokens > 0:
            self.total_busy_time += current_time - self.last_change_time
        self.last_change_time = current_time
        
    def get_busy_ratio(self, total_time: float) -> float:
        """
        Calculate position busy ratio
        Args:
            total_time: total simulation time
        Returns:
            ratio of time position had tokens
        """
        return self.total_busy_time / total_time if total_time > 0 else 0