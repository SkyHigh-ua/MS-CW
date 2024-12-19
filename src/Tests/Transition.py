import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
from Model import Model

def collect_statistics_over_time(t_mod: float, sample_points: int = 100) -> Dict[str, List[float]]:
    """
    Run simulation and collect statistics at regular intervals
    """
    stats = {
        'main_channel_utilization': np.zeros(sample_points),
        'reserve_channel_utilization': np.zeros(sample_points),
        'avg_transmission_time': np.zeros(sample_points),
        'queue_length': np.zeros(sample_points)
    }
    
    time_points = np.linspace(0, t_mod, sample_points)
    time_step = t_mod / sample_points
    n_runs = 20
    for run in range(n_runs):
        print(f"Running simulation {run + 1}/{n_runs}")
        
        model = Model(t_mod=t_mod, params={})
        current_index = 0
        next_sample_time = time_step
        
        while model.current_time < t_mod and current_index < sample_points:
            while model.current_time < next_sample_time and model.current_time < t_mod:
                next_time = model._find_next_event_time()

                if next_time == float('inf'):
                    break
                    
                model.current_time = next_time
                
                model._process_outputs()
                
                while model._process_enabled_transitions():
                    pass
            if model.positions['P1'].total_tokens > 0:
                main_util = (len([r.transmission_time for r in model.statistics.transmission_records 
                         if r.completed and r.channel == 'main']) / 
                           model.positions['P1'].total_tokens)
                reserve_util = (len([r.transmission_time for r in model.statistics.transmission_records 
                         if r.completed and r.channel == 'reserve']) / model.positions['P1'].total_tokens)
            else:
                main_util = reserve_util = 0
                
            transmission_times = [msg 
                               for msg in ([r.transmission_time for r in model.statistics.transmission_records 
                         if r.completed and r.channel == 'reserve'] + 
                                         [r.transmission_time for r in model.statistics.transmission_records 
                         if r.completed and r.channel == 'main'])]
            avg_time = np.mean(transmission_times) if transmission_times else 0
            
            stats['main_channel_utilization'][current_index] += main_util / n_runs
            stats['reserve_channel_utilization'][current_index] += reserve_util / n_runs
            stats['avg_transmission_time'][current_index] += avg_time / n_runs
            stats['queue_length'][current_index] += (model.positions['P2'].max_tokens + model.positions['P3'].max_tokens + model.positions['P4'].max_tokens) / n_runs
            
            current_index += 1
            next_sample_time += time_step
            
    return stats, time_points

def plot_transition_period(stats: Dict[str, List[float]], time_points: List[float], 
                         transition_times: Dict[str, float], steady_values: Dict[str, float]):
    """
    Plot statistics with transition period marked according to guidelines:
    - Horizontal line showing steady state value
    - Vertical lines marking transition period boundaries
    - Shaded area for transition period
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
    
    metrics = ['main_channel_utilization', 'reserve_channel_utilization', 
              'avg_transmission_time', 'queue_length']
    axes = [ax1, ax2, ax3, ax4]
    titles = ['Main Channel Utilization', 'Reserve Channel Utilization',
             'Average Transmission Time', 'Queue Length']
    
    for ax, metric, title in zip(axes, metrics, titles):
        ax.plot(time_points, stats[metric], 'b-', label='Measured value')
        
        transition_time = transition_times[metric]
        steady_value = steady_values[metric]
        
        ax.axhline(y=steady_value, color='g', linestyle='--', alpha=0.5, 
                  label='Steady state value')
        
        ax.axvline(x=0, color='r', linestyle='-', alpha=0.3)
        ax.axvline(x=transition_time, color='r', linestyle='-', alpha=0.3)
        
        ax.axvspan(0, transition_time, alpha=0.1, color='r', 
                  label='Transition period')
        
        ax.text(transition_time + 20, ax.get_ylim()[0],
                f'T = {transition_time:.1f}',
                verticalalignment='bottom')
        
        ax.text(time_points[-1] * 0.7, steady_value,
                f'y = {steady_value:.3f}',
                verticalalignment='bottom')
        
        ax.set_title(title)
        ax.set_xlabel('Time')
        ax.grid(True, alpha=0.3)
        
        ax.legend(loc='upper right', fontsize='small')
    
    axes[0].set_ylabel('Utilization')
    axes[1].set_ylabel('Utilization')
    axes[2].set_ylabel('Time units')
    axes[3].set_ylabel('Messages')
    
    plt.tight_layout()
    plt.show()
    
def calculate_transition_period(values: np.ndarray, time_points: np.ndarray, 
                             window_size: int = 10, epsilon: float = 0.01) -> Tuple[float, float]:
    """
    Calculate transition period using statistical criteria
    
    Args:
        values: Array of metric values
        time_points: Array of time points
        window_size: Size of moving window for calculations
        epsilon: Maximum allowed relative variation
        
    Returns:
        transition_time: Estimated transition period
        steady_value: Estimated steady state value
    """
    moving_avg = np.convolve(values, np.ones(window_size)/window_size, mode='valid')
    moving_std = np.array([np.std(values[i:i+window_size]) 
                          for i in range(len(values)-window_size+1)])
    
    relative_variation = moving_std / (moving_avg + 1e-10) 
    steady_indices = np.where(relative_variation < epsilon)[0]
    if len(steady_indices) > 0:
        transition_idx = steady_indices[0] + window_size
        transition_time = time_points[transition_idx]
        steady_value = np.mean(values[transition_idx:])
    else:
        transition_time = time_points[-1]
        steady_value = np.mean(values)
        
    return transition_time, steady_value

def analyze_transition_period(t_mod: float = 1000):
    """Analyze transition period by looking at when statistics stabilize"""
    stats, time_points = collect_statistics_over_time(t_mod)
    
    transition_times = {}
    steady_values = {}
    
    for metric in stats.keys():
        trans_time, steady_val = calculate_transition_period(
            stats[metric], 
            time_points,
            window_size=10,
            epsilon=0.01
        )
        transition_times[metric] = trans_time
        steady_values[metric] = steady_val
    
    plot_transition_period(stats, time_points, transition_times, steady_values)
    
    print("\nTransition period analysis results:")
    print("-----------------------------------")
    for metric in stats.keys():
        print(f"\n{metric}:")
        print(f"  Transition period: {transition_times[metric]:.1f} time units")
        print(f"  Steady state value: {steady_values[metric]:.3f}")
    
    overall_transition = max(transition_times.values())
    print(f"\nOverall system transition period: {overall_transition:.1f} time units")
    print(f"Recommended simulation time: {overall_transition * 5:.1f} time units")
        
if __name__ == "__main__":
    analyze_transition_period(t_mod=1000)