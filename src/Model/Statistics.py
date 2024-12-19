import numpy as np
from Record import TransmissionRecord

class Statistics:
    """Class for collecting simulation statistics"""
    def __init__(self):
        self.total_messages = 0
        self.transmitted_messages = 0
        self.failures = 0
        self.failure_times = []
        self.max_queue_length = 0
        self.channels_utilization = {}
        self.main_channel_failure_rate = 0
        self.transmission_records: List[TransmissionRecord] = []
        self.transmission_statistics = {
            'mean': 0,
            'std_dev': 0,
            'min': 0,
            'max': 0
        }
        
    def add_transmission(self, record: TransmissionRecord):
        """Add transmission record"""
        self.transmission_records.append(record)
        
    def update(self, model: any):
        """Update statistics from model state"""
        total_time = model.current_time
        for pos in model.positions.values():
            pos.update_busy_time(total_time)
            
        self.total_messages = model.positions['P1'].total_tokens
        self.transmitted_messages = model.positions['P5'].tokens
        self.failures = model.positions['P7'].total_tokens
        self.max_queue_length = model.positions['P2'].max_tokens
        
        self.channels_utilization = {
            'main': len([r.transmission_time for r in self.transmission_records 
                         if r.completed and r.channel == 'main']) / self.transmitted_messages,
            'reserve': len([r.transmission_time for r in self.transmission_records 
                         if r.completed and r.channel == 'reserve']) / self.transmitted_messages
        }
        
        self.max_queue_length = model.positions['P3'].max_tokens + model.positions['P4'].max_tokens
        self.main_channel_failure_rate = self.failures / total_time if total_time > 0 else 0
        
        self._calculate_transmission_statistics()
        
    def _calculate_transmission_statistics(self):
        """Calculate statistical characteristics of transmission times"""
        completed_times = [r.transmission_time for r in self.transmission_records 
                         if r.completed and r.transmission_time > 0]
        
        if not completed_times:
            return
            
        self.transmission_statistics = {
            'mean': np.mean(completed_times),
            'std_dev': np.std(completed_times),
            'min': np.min(completed_times),
            'max': np.max(completed_times)
        }
        
    def print_report(self):
        """Print simulation statistics report"""
        print("\nSimulation Statistics:")
        print(f"Total messages: {self.total_messages}")
        print(f"Transmitted messages: {self.transmitted_messages}")
        print(f"Failures: {self.failures}")
        print(f"Max queue length: {self.max_queue_length}")
        print("\nChannel utilization:")
        for channel, util in self.channels_utilization.items():
            print(f"{channel}: {util:.2%}")
        print(f"\nMain channel failure rate: {self.main_channel_failure_rate:.6f}")
        print("\nTransmission time statistics:")
        print(f"  Mean: {self.transmission_statistics['mean']:.2f}")
        print(f"  Std. Dev.: {self.transmission_statistics['std_dev']:.2f}")
        print(f"  Min: {self.transmission_statistics['min']:.2f}")
        print(f"  Max: {self.transmission_statistics['max']:.2f}")