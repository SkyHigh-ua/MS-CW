import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from typing import List, Tuple
from Experiment import ExperimentRunner

class RegressionAnalysis:
    """Class for regression analysis of the simulation results"""
    def __init__(self):
        self.X = None   
        self.y = None   
        self.model = None
        self.poly = None
        
    def collect_data(self, param_ranges: dict) -> None:
        """Collect data by running experiments with different parameters"""
        X_data = []
        y_data = []
        
         
        failure_means = np.linspace(param_ranges['failure_mean'][0], 
                                  param_ranges['failure_mean'][1], 
                                  param_ranges['failure_mean'][2])
        
        recovery_means = np.linspace(param_ranges['recovery_mean'][0],
                                   param_ranges['recovery_mean'][1],
                                   param_ranges['recovery_mean'][2])
        
        for f_mean in failure_means:
            for r_mean in recovery_means:
                params = {
                    'failure_mean': f_mean,
                    'recovery_mean': r_mean,
                    'failure_std': 35,
                    'recovery_std': 7
                }
                
                 
                runner = ExperimentRunner(params=params)
                runner.run_experiments()
                
                 
                intervals = runner.get_confidence_intervals()
                
                 
                X_data.append([f_mean, r_mean])
                
                 
                y_data.append([
                    intervals['reserve_utilization']['mean'],
                    intervals['failure_rate']['mean']
                ])
                
        self.X = np.array(X_data)
        self.y = np.array(y_data)
        
    def fit_model(self, degree: int = 2) -> None:
        """Fit polynomial regression model"""
         
        self.poly = PolynomialFeatures(degree=degree)
        X_poly = self.poly.fit_transform(self.X)
        
         
        self.model = []
        for i in range(self.y.shape[1]):
            reg = LinearRegression()
            reg.fit(X_poly, self.y[:, i])
            self.model.append(reg)
            
    def predict(self, X_new: np.ndarray) -> np.ndarray:
        """Make predictions with fitted model"""
        X_poly = self.poly.transform(X_new)
        y_pred = np.zeros((X_new.shape[0], len(self.model)))
        
        for i, reg in enumerate(self.model):
            y_pred[:, i] = reg.predict(X_poly)
            
        return y_pred
        
    def plot_results(self, characteristic_idx: int, 
                    title: str, zlabel: str) -> None:
        """Create 3D plot of regression results"""
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        
         
        X1, X2 = np.meshgrid(
            np.linspace(min(self.X[:, 0]), max(self.X[:, 0]), 50),
            np.linspace(min(self.X[:, 1]), max(self.X[:, 1]), 50)
        )
        
         
        X_plot = np.column_stack((X1.ravel(), X2.ravel()))
        y_plot = self.predict(X_plot)[:, characteristic_idx]
        Z = y_plot.reshape(X1.shape)
        
         
        surf = ax.plot_surface(X1, X2, Z, cmap='viridis', alpha=0.8)
        
         
        ax.scatter(self.X[:, 0], self.X[:, 1], 
                  self.y[:, characteristic_idx], 
                  c='r', marker='o')
        
         
        ax.set_xlabel('Mean Time Between Failures')
        ax.set_ylabel('Mean Recovery Time')
        ax.set_zlabel(zlabel)
        ax.set_title(title)
        
         
        fig.colorbar(surf)
        plt.show()
        
    def print_model_quality(self) -> None:
        """Print R² scores for fitted models"""
        characteristic_names = ['Reserve Channel Utilization', 'Failure Rate']
        X_poly = self.poly.transform(self.X)
        
        print("\nModel Quality (R² scores):")
        print("-" * 40)
        
        for name, reg in zip(characteristic_names, self.model):
            y_pred = reg.predict(X_poly)
            r2 = r2_score(self.y[:, 0], y_pred)
            print(f"{name}: {r2:.4f}")

 
if __name__ == "__main__":
     
    param_ranges = {
        'failure_mean': [100, 300, 5],   
        'recovery_mean': [15, 30, 4]     
    }
    
     
    analysis = RegressionAnalysis()
    analysis.collect_data(param_ranges)
    analysis.fit_model(degree=2)
    
     
    analysis.print_model_quality()
    
     
    analysis.plot_results(0, 'Reserve Channel Utilization', 'Utilization')
    analysis.plot_results(1, 'Failure Rate', 'Failures per time unit')