from typing import Dict, Set, Tuple, Optional, Callable, Any
from Position import Position
import numpy as np

class Transition:
    """Class representing Petri net transition"""
    def __init__(self, 
                name: str,
                input_arcs: Dict[str, Tuple[int, bool]],
                output_arcs: Dict[str, int],
                delay: Optional[Callable[[], float]] = None,
                priority: int = 0,
                on_start: Optional[Callable[[float], Any]] = None,
                on_complete: Optional[Callable[[float, Any], Any]] = None):
        """
        Initialize transition
        Args:
            name: transition name
            input_arcs: dict of input positions with arc weights and info flag
            output_arcs: dict of output positions with arc weights
            delay: function that returns time delay (None for immediate)
            priority: transition priority (higher number = higher priority)
            probability: probability of firing when in conflict
        """
        self.name = name
        self.input_arcs = input_arcs
        self.output_arcs = output_arcs
        self.delay = delay if delay else lambda: 0
        self.priority = priority
        self.output_times: Set[float] = set()
        self.on_start = on_start
        self.on_complete = on_complete
        self.record = None

    def is_enabled(self, positions: Dict[str, 'Position'], all_transitions: Dict[str, 'Transition']) -> bool:
        """Check if transition is enabled"""
        if not self.check_input_conditions(positions):
            return False

        for other in all_transitions.values():
            if other.name == self.name:
                continue
            if other.priority > self.priority and other.check_input_conditions(positions):
                return False
            
        return True
    
    def check_input_conditions(self, positions: Dict[str, 'Position']) -> bool:
        """Check basic enabling conditions without priorities"""
        for pos_name, (weight, is_info) in self.input_arcs.items():
            if not positions[pos_name].has_tokens(weight):
                return False
        return True

    def fire_input(self, positions: Dict[str, 'Position'], current_time: float):
        """Process input marking change and schedule output"""
        for pos_name, (weight, is_info) in self.input_arcs.items():
            if not is_info:
                positions[pos_name].remove_tokens(weight, current_time)
        
        if self.delay:
            delay = self.delay()
            if delay > 0:
                self.output_times.add(current_time + delay)
            else:
                self.output_times.add(current_time)
        
        if self.on_start:
            self.record = self.on_start(current_time)

    def fire_output(self, positions: Dict[str, 'Position'], current_time: float):
        """Process output marking change"""
        for pos_name, weight in self.output_arcs.items():
            positions[pos_name].add_tokens(weight, current_time)
            
        if self.on_complete:
            self.on_complete(current_time, self.record)

    def cancel_scheduled_outputs(self):
        """Cancel all scheduled outputs"""
        self.output_times.clear()

    def get_next_output_time(self) -> float:
        """Get earliest scheduled output time"""
        return min(self.output_times) if self.output_times else float('inf')

    def remove_output_time(self, time: float):
        """Remove specific output time"""
        if time in self.output_times:
            self.output_times.remove(time)