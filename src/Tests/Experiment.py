import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from Model import Model

@dataclass
class ExperimentResult:
    """Class to store results of a single experiment"""
    main_channel_utilization: float
    reserve_channel_utilization: float 
    transmission_times: List[float]
    avg_transmission_time: float
    avg_queue_length: float
    failure_rate: float
    failure_times: List[float]

class ExperimentRunner:
    """Class for running simulation experiments"""
    def __init__(self, 
                 t_mod: float = 1000,
                 warmup_period: float = 600,
                 num_replications: int = 150,
                 params: Dict[str, float] = None):
        
        self.t_mod = t_mod
        self.warmup_period = warmup_period
        self.num_replications = num_replications
        self.params = params if params else {}
        self.results: List[ExperimentResult] = []
        
    def run_experiments(self) -> None:
        """Run specified number of experiment replications"""
        for _ in range(self.num_replications):
             
            np.random.seed()   
            model = Model(self.t_mod, self.params)
            model.run()
            
             
            result = self._calculate_statistics(model)
            self.results.append(result)
            
    def _calculate_statistics(self, model) -> ExperimentResult:
        """Calculate statistics for a single experiment"""
         
        main_messages = [r for r in model.statistics.transmission_records 
                         if r.completed and r.channel == 'main' and r.start_time >= self.warmup_period]
        reserve_messages = [r for r in model.statistics.transmission_records 
                         if r.completed and r.channel == 'reserve' and r.start_time >= self.warmup_period]
        
         
        total_time = self.t_mod - self.warmup_period
        total_messages = len(main_messages) + len(reserve_messages)
        
        main_utilization = len(main_messages) / total_messages if total_messages > 0 else 0
        reserve_utilization = len(reserve_messages) / total_messages if total_messages > 0 else 0
        
        transmission_times = [
                            msg.transmission_time
                            for msg in main_messages + reserve_messages if msg.completed
                            ]
        avg_transmission = np.mean(transmission_times) if transmission_times else 0
        
        failure_times = [
            time for time in model.statistics.failure_times
            if time >= self.warmup_period
        ]
        failure_rate = len(failure_times) / total_time
        
        return ExperimentResult(
            main_channel_utilization=main_utilization,
            reserve_channel_utilization=reserve_utilization, 
            transmission_times=transmission_times,
            avg_transmission_time=avg_transmission,
            avg_queue_length=model.positions['P3'].max_tokens + model.positions['P4'].max_tokens,
            failure_rate=failure_rate,
            failure_times=failure_times
        )
        
    def get_confidence_intervals(self, confidence: float = 0.95) -> Dict[str, Dict[str, float]]:
        """Calculate confidence intervals for all metrics"""
        metrics = {
            'main_utilization': [r.main_channel_utilization for r in self.results],
            'reserve_utilization': [r.reserve_channel_utilization for r in self.results],
            'transmission_time': [r.avg_transmission_time for r in self.results],
            'queue_length': [r.avg_queue_length for r in self.results],
            'failure_rate': [r.failure_rate for r in self.results]
        }
        
        intervals = {}
        alpha = 1 - confidence
        for metric, values in metrics.items():
            mean = np.mean(values)
            std = np.std(values)
            n = len(values)
            
             
            margin = std * (1 / (alpha * (n-1))) ** 0.5
            
            intervals[metric] = {
                'mean': mean,
                'std': std,
                'ci_lower': mean - margin,
                'ci_upper': mean + margin
            }
            
        return intervals
    
    def print_results(self) -> None:
        """Print experiment results"""
        intervals = self.get_confidence_intervals()
        
        print("\nExperiment Results (95% Confidence Intervals):")
        print("-" * 60)
        
        for metric, stats in intervals.items():
            print(f"\n{metric.replace('_', ' ').title()}:")
            print(f"  Mean: {stats['mean']:.4f}")
            print(f"  Std Dev: {stats['std']:.4f}")
            print(f"  95% CI: [{stats['ci_lower']:.4f}, {stats['ci_upper']:.4f}]")
            
    def save_results(self, filename: str) -> None:
        """Save results to file"""
        intervals = self.get_confidence_intervals()
        
        with open(filename, 'w') as f:
            f.write("Experiment Results (95% Confidence Intervals)\n")
            f.write("-" * 60 + "\n")
            
            for metric, stats in intervals.items():
                f.write(f"\n{metric.replace('_', ' ').title()}:\n")
                f.write(f"  Mean: {stats['mean']:.4f}\n")
                f.write(f"  Std Dev: {stats['std']:.4f}\n")
                f.write(f"  95% CI: [{stats['ci_lower']:.4f}, {stats['ci_upper']:.4f}]\n")