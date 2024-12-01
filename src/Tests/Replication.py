import numpy as np
from Model import Model
from typing import Dict, List

def calculate_required_replications(
    model_time: float,
    n_preliminary: int = 10,
    confidence_level: float = 0.95,
    relative_error: float = 0.05
) -> Dict[str, Dict[str, float]]:
    """
    Calculate required number of replications for each metric
    
    Args:
        model_time: Simulation time for each replication
        n_preliminary: Number of preliminary runs
        confidence_level: Desired confidence level
        relative_error: Desired relative error
        
    Returns:
        Dictionary with statistics for each metric
    """
     
    metrics_data = {
        'main_channel_utilization': [],
        'reserve_channel_utilization': [],
        'avg_transmission_time': [],
        'queue_length': []
    }
    
    print(f"\nRunning {n_preliminary} preliminary experiments...")
    for i in range(n_preliminary):
        print(f"Experiment {i+1}/{n_preliminary}")
        model = Model(t_mod=model_time, params={})
        model.run()
        
         
        if model.messages_generated > 0:
            main_util = (len(model.main_channel.messages_processed) / 
                        model.messages_generated)
            reserve_util = (len(model.reserve_channel.messages_processed) / 
                          model.messages_generated)
        else:
            main_util = reserve_util = 0
            
        transmission_times = [msg.get_transmission_time() 
                            for msg in (model.main_channel.messages_processed + 
                                      model.reserve_channel.messages_processed)]
        avg_time = np.mean(transmission_times) if transmission_times else 0
        
        metrics_data['main_channel_utilization'].append(main_util)
        metrics_data['reserve_channel_utilization'].append(reserve_util)
        metrics_data['avg_transmission_time'].append(avg_time)
        metrics_data['queue_length'].append(len(model.queue))
    
     
    results = {}
    for metric, values in metrics_data.items():
        mean_value = np.mean(values)
        std_dev = np.std(values, ddof=1)   
        
         
        required_n = int(np.ceil(
            (std_dev**2 * (1/(1-confidence_level))) / 
            ((relative_error * mean_value)**2)
        ))
        
        results[metric] = {
            'mean': mean_value,
            'std_dev': std_dev,
            'required_replications': required_n
        }
    
    return results

def print_replications_analysis(results: Dict[str, Dict[str, float]]):
    """Print analysis results in a formatted way"""
    print("\nAnalysis of required number of replications:")
    print("-------------------------------------------")
    for metric, stats in results.items():
        print(f"\n{metric}:")
        print(f"  Mean value: {stats['mean']:.3f}")
        print(f"  Standard deviation: {stats['std_dev']:.3f}")
        print(f"  Required replications: {stats['required_replications']}")

if __name__ == "__main__":
     
    results = calculate_required_replications(
        model_time=1000,   
        n_preliminary=10,
        confidence_level=0.95,
        relative_error=0.05
    )
    
    print_replications_analysis(results)