class Statistics:
    """Class for collecting simulation statistics"""
    def __init__(self):
        self.total_messages = 0
        self.transmitted_messages = 0
        self.failures = 0
        self.transmission_times = []
        self.max_queue_length = 0
        self.channels_utilization = {}
        self.main_channel_failure_rate = 0
        self.transmission_statistics = {}
        
    def update(self, simulation):
        """Update statistics from simulation state"""
        self.total_messages = simulation.messages_generated
        self.transmitted_messages = (
            simulation.main_channel.messages_processed + 
            simulation.reserve_channel.messages_processed
        )
        self.failures = simulation.failures
        self.max_queue_length = simulation.queue.max_length
        
         
        self.channels_utilization = {
            'main': len(simulation.main_channel.messages_processed) / simulation.messages_generated,
            'reserve': len(simulation.reserve_channel.messages_processed) / simulation.messages_generated
        }
        
        self.main_channel_failure_rate = simulation.failures / simulation.t_mod

         
        self.transmission_times = [
            t for t in [
                msg.get_transmission_time()
                for msg in simulation.main_channel.messages_processed + simulation.reserve_channel.messages_processed
            ] if t > 0
        ]
        self.transmission_statistics = self._calculate_transmission_statistics()
        
    
    def _calculate_transmission_statistics(self):
        """Calculate statistical characteristics of transmission times"""
        if not self.transmission_times:
            return {
                'mean': 0,
                'std_dev': 0,
                'min': 0,
                'max': 0,
            }

        n = len(self.transmission_times)
        mean = sum(self.transmission_times) / n
        variance = sum((t - mean) ** 2 for t in self.transmission_times) / (n - 1)
        std_dev = variance ** 0.5
        min_time = min(self.transmission_times)
        max_time = max(self.transmission_times)

        return {
            'mean': mean,
            'std_dev': std_dev,
            'min': min_time,
            'max': max_time,
        }
        
    def print_report(self):
        """Print simulation statistics report"""
        print("\nSimulation Statistics:")
        print(f"Total messages generated: {self.total_messages}")
        print(f"Messages transmitted: {len(self.transmitted_messages)}")
        print(f"Channel failures: {self.failures}")
        print(f"Max queue length: {self.max_queue_length}")
        print("\nChannel utilization:")
        for channel, util in self.channels_utilization.items():
            print(f"{channel}: {util:.2%}")

        print(f"\nMain channel failure rate: {self.main_channel_failure_rate:.6f} failures per time unit")
        print("\nTransmission time statistics:")
        print(f"  Mean: {self.transmission_statistics['mean']:.2f}")
        print(f"  Std. Dev.: {self.transmission_statistics['std_dev']:.2f}")
        print(f"  Min: {self.transmission_statistics['min']:.2f}")
        print(f"  Max: {self.transmission_statistics['max']:.2f}")