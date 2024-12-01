import numpy as np
from typing import Dict, Any
from Channel import Channel
from Queue import Queue
from Statistics import Statistics
from Message import Message

class Model:
    """Main simulation class"""
    def __init__(self, t_mod: float, params: Dict[str, Any]):
        self.current_time = 0
        self.t_mod = t_mod
        
        self.main_channel = Channel("Main")
        self.reserve_channel = Channel("Reserve")
        self.queue = Queue()
        
        self.messages_generated = 0
        self.failures = 0
        self.failure_times: list[int] = [] 
        self.statistics = Statistics()
        
        self.message_arrival_mean = params.get('arrival_mean', 9)
        self.message_arrival_std = params.get('arrival_std', 4)
        self.message_transmission_mean = params.get('transmission_mean', 7) 
        self.message_transmission_std = params.get('transmission_std', 3)
        self.failure_interval_mean = params.get('failure_mean', 200)
        self.failure_interval_std = params.get('failure_std', 35)
        self.recovery_interval_mean = params.get('recovery_mean', 23)
        self.recovery_interval_std = params.get('recovery_std', 7)
        
        self.next_message = self._generate_arrival_time()
        self.next_failure = self._generate_failure_time()
        
    def run(self):
        """Run simulation"""
        while self.current_time < self.t_mod:
            next_time = min(
                self.next_message,
                self.next_failure,
                self.main_channel.transmission_end,
                self.main_channel.recovery_time,
                self.reserve_channel.transmission_end
            )
            
            self.current_time = next_time
            
            if self.current_time == self.next_message:
                self._process_message_arrival()
                
            if self.current_time == self.next_failure:
                self._process_channel_failure()
                
            if self.current_time == self.main_channel.recovery_time:
                self._process_channel_recovery()
                
            if self.current_time == self.main_channel.transmission_end:
                self._process_main_transmission_end()
                
            if self.current_time == self.reserve_channel.transmission_end:
                self._process_reserve_transmission_end()
            
        self.statistics.update(self)
        
    def run_to_next_event(self):
        """Run until next event"""
        next_time = min(
            self.next_message,
            self.next_failure,
            self.main_channel.transmission_end,
            self.main_channel.recovery_time,
            self.reserve_channel.transmission_end
        )
        
        self.current_time = next_time
        
        if self.current_time == self.next_message:
            self._process_message_arrival()
            
        if self.current_time == self.next_failure:
            self._process_channel_failure()
            
        if self.current_time == self.main_channel.recovery_time:
            self._process_channel_recovery()
            
        if self.current_time == self.main_channel.transmission_end:
            self._process_main_transmission_end()
            
        if self.current_time == self.reserve_channel.transmission_end:
            self._process_reserve_transmission_end()
        
    def _process_message_arrival(self):
        """Process new message arrival"""
        message = Message(arrival_time=self.current_time)
        self.messages_generated += 1
        
        if self.main_channel.is_free():
            transmission_time = self._generate_transmission_time()
            self.main_channel.start_transmission(
                message, self.current_time, transmission_time
            )
        else:
            self.queue.put(message)
            
        self.next_message = self.current_time + self._generate_arrival_time()
        
    def _process_channel_failure(self):
        """Process main channel failure"""
        self.failures += 1
        self.failure_times.append(self.current_time)
        
        if self.main_channel.is_busy():
             
            message = self.main_channel.interrupt(self.current_time)
            
             
            if message:
                transmission_time = self._generate_transmission_time()
                self.reserve_channel.start_transmission(
                    message, self.current_time, transmission_time
                )
        
        self.main_channel.fail(self.current_time)
        
         
        recovery_time = self._generate_recovery_time()
        self.main_channel.schedule_recovery(self.current_time + recovery_time)
        
         
        self.next_failure = self.current_time + self._generate_failure_time()
        
    def _process_channel_recovery(self):
        """Process main channel recovery"""
        self.main_channel.recover(self.current_time)
        
         
        if self.queue:
            message = self.queue.get()
            if message:
                transmission_time = self._generate_transmission_time()
                self.main_channel.start_transmission(
                    message, self.current_time, transmission_time
                )
                
    def _process_main_transmission_end(self):
        """Process main channel transmission completion"""
        self.main_channel.complete_transmission(self.current_time)
        
         
        if self.queue:
            message = self.queue.get()
            if message:
                transmission_time = self._generate_transmission_time()
                self.main_channel.start_transmission(
                    message, self.current_time, transmission_time
                )
                
    def _process_reserve_transmission_end(self):
        """Process reserve channel transmission completion"""
        self.reserve_channel.complete_transmission(self.current_time)
        
    def _generate_arrival_time(self) -> float:
        """Generate message inter-arrival time"""
        return np.random.normal(self.message_arrival_mean, self.message_arrival_std)
    
    def _generate_transmission_time(self) -> float:
        """Generate message transmission time"""
        return np.random.normal(self.message_transmission_mean, self.message_transmission_std)
    
    def _generate_failure_time(self) -> float:
        """Generate time until next failure"""
        return np.random.normal(self.failure_interval_mean, self.failure_interval_std)
    
    def _generate_recovery_time(self) -> float:
        """Generate channel recovery time"""
        return np.random.normal(self.recovery_interval_mean, self.recovery_interval_std)

 
if __name__ == "__main__":
     
    sim = Model(t_mod=1000, params={})
    sim.run()
    
     
    sim.statistics.print_report()