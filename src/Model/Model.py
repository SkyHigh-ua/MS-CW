from typing import Dict, Any
import numpy as np
from Position import Position 
from Transition import Transition
from Statistics import Statistics
from Record import TransmissionRecord

class Model:
    """Petri net simulation model"""
    def __init__(self, t_mod: float, params: Dict[str, Any]):
        self.message_arrival_mean = params.get('arrival_mean', 9)
        self.message_arrival_std = params.get('arrival_std', 4)
        self.message_transmission_mean = params.get('transmission_mean', 7) 
        self.message_transmission_std = params.get('transmission_std', 3)
        self.failure_interval_mean = params.get('failure_mean', 200)
        self.failure_interval_std = params.get('failure_std', 35)
        self.recovery_interval_mean = params.get('recovery_mean', 23)
        self.recovery_interval_std = params.get('recovery_std', 7)
        
        self.current_time = 0
        self.t_mod = t_mod
        
        self.positions = self._create_positions()
        
        self.transitions = self._create_transitions(params)
        
        self.statistics = Statistics()
        
        self.transitions['T1'].output_times.add(self._generate_arrival_time())
        self.transitions['T7'].output_times.add(self._generate_failure_time())
        
    def run(self):
        """Run simulation"""
        while self.current_time < self.t_mod:
            next_time = self._find_next_event_time()

            if next_time == float('inf'):
                break
                
            self.current_time = next_time
            
            self._process_outputs()
            
            while self._process_enabled_transitions():
                pass
            
        self.statistics.update(self)
    
    def _create_positions(self) -> Dict[str, Position]:
        """Create initial positions"""
        positions = {
            'P1': Position('P1', 1),
            'P2': Position('P2'),
            'P3': Position('P3'),
            'P4': Position('P4'),
            'P5': Position('P5'),
            'P6': Position('P6', 1),
            'P7': Position('P7', 1),
            'P8': Position('P8', 1),
            'P9': Position('P9'),
            'P10': Position('P10'),
            'P11': Position('P11'), 
            'P12': Position('P12'),
        }
        return positions

    def _create_transitions(self, params: Dict[str, Any]) -> Dict[str, Transition]:
        """Create transitions with their arcs"""
        transitions = {
            'T1': Transition('T1',
                            input_arcs={'P1': (1, False)},
                            output_arcs={'P2': 1, 'P1': 1},
                            delay=lambda: max(0, np.random.normal(self.message_arrival_mean, self.message_arrival_std))),
            
            'T2': Transition('T2',
                            input_arcs={'P2': (1, False), 'P8': (1, True)},
                            output_arcs={'P3': 1}),
            
            'T3': Transition('T3',
                            input_arcs={'P2': (1, False), 'P11': (1, True)},
                            output_arcs={'P4': 1}),
            
            'T4': Transition('T4',
                            input_arcs={'P3': (1, False), 'P6': (1, False), 'P8': (1, True)},
                            output_arcs={'P5': 1, 'P6': 1},
                            delay=lambda: max(0, np.random.normal(self.message_transmission_mean, self.message_transmission_std)),
                            priority=1,
                            on_start=lambda t: self._start_transmission(t, 'main'),
                            on_complete=lambda t,r: self._complete_transmission(t,r)),
            
            'T5': Transition('T5', 
                            input_arcs={'P4': (1, False), 'P6': (1, False)},
                            output_arcs={'P5': 1, 'P6': 1},
                            delay=lambda: max(0, np.random.normal(self.message_transmission_mean, self.message_transmission_std)),
                            on_start=lambda t: self._start_transmission(t, 'reserve'),
                            on_complete=lambda t,r: self._complete_transmission(t,r)),
            
            'T6': Transition('T6',
                            input_arcs={'P3': (1, False), 'P8': (0, True)},
                            output_arcs={'P2': 1}),
            
            'T7': Transition('T7',
                            input_arcs={'P7': (1, False)},
                            output_arcs={'P10': 1, 'P9': 1, 'P7': 1},
                            delay=lambda: max(0, np.random.normal(self.failure_interval_mean, self.failure_interval_std)),
                            on_start=lambda t: self.statistics.failure_times.append(t)),
            
            'T9': Transition('T9', 
                            input_arcs={'P10': (1, False), 'P8': (1, False)},
                            output_arcs={'P12': 1},
                            delay=lambda: max(0, np.random.normal(self.recovery_interval_mean, self.recovery_interval_std))),
            
            'T8': Transition('T8', 
                            input_arcs={'P9': (1, False)},
                            output_arcs={'P11': 1},
                            delay=lambda: 2),        
            
            'T10': Transition('T10',
                            input_arcs={'P11': (1, False), 'P12': (1, False)},
                            output_arcs={'P8': 1}),
        }
        return transitions
    
    def _find_next_event_time(self) -> float:
        """Find time of next transition output"""
        times = []
        for t in self.transitions.values():
            times.extend(t.output_times)
        return min(times) if times else float('inf')
    
    def _process_outputs(self):
        """Process all transition outputs at current time"""
        for t in self.transitions.values():
            if self.current_time in t.output_times:
                t.output_times.remove(self.current_time)
                t.fire_output(self.positions, self.current_time)
    
    def _process_enabled_transitions(self) -> bool:
        """Process one enabled transition, return True if any were enabled"""
        sorted_transitions = sorted(
            self.transitions.values(), 
            key=lambda t: (-t.priority, t.name)
        )
        for t in sorted_transitions:
            if t.is_enabled(self.positions, self.transitions):
                t.fire_input(self.positions, self.current_time)
                return True
        return False
    
    def _generate_arrival_time(self) -> float:
        """Generate next message arrival time"""
        return self.current_time + np.random.normal(self.message_arrival_mean, self.message_arrival_std)
    
    def _generate_failure_time(self) -> float:
        """Generate next failure time"""
        return self.current_time + np.random.normal(self.failure_interval_mean, self.failure_interval_std)
    
    def _start_transmission(self, time: float, channel: str):
        """Record start of transmission"""
        record = TransmissionRecord(start_time=time, channel=channel)
        self.statistics.add_transmission(record)
        return record

    def _complete_transmission(self, time: float, record: TransmissionRecord):
        """Record completion of transmission"""
        record.end_time = time
        record.completed = True
        
if __name__ == "__main__":
     
    sim = Model(t_mod=1000, params={
        'arrival_mean': 9,
        'arrival_std': 4,
        'transmission_mean': 7, 
        'transmission_std': 3,
        'failure_mean': 200,
        'failure_std': 35,
        'recovery_mean': 23,
        'recovery_std': 7
    })
    sim.run()
     
    sim.statistics.print_report()