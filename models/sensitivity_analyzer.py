import numpy as np
from typing import Dict, List, Tuple, Any
from models.capex_calculator import CapExCalculator

class SensitivityAnalyzer:
    """
    Sensitivity Analysis for Renewable Energy CapEx Models
    
    This class performs sensitivity analysis to understand how changes in
    key input parameters affect the total project cost.
    """
    
    def __init__(self):
        """Initialize the sensitivity analyzer."""
        self.sensitivity_parameters = [
            "equipment_cost_per_mw",
            "labor_cost_per_mw", 
            "interest_rate",
            "delay_months",
            "inflation_rate"
        ]
    
    def perform_sensitivity_analysis(self, base_params: Dict[str, Any], 
                                   sensitivity_range: float,
                                   calculator: CapExCalculator) -> Dict[str, Dict[str, float]]:
        """
        Perform sensitivity analysis on key parameters.
        
        Args:
            base_params: Dictionary of base case parameters
            sensitivity_range: Percentage range for sensitivity analysis (e.g., 20 for ±20%)
            calculator: CapExCalculator instance
            
        Returns:
            Dictionary with sensitivity results for each parameter
        """
        results = {}
        
        # Calculate base case cost
        base_cost = calculator.calculate_total_capex(**base_params)
        
        for param in self.sensitivity_parameters:
            if param not in base_params:
                continue
                
            # Calculate low case (parameter decreased by sensitivity_range%)
            low_params = base_params.copy()
            if param in ["delay_months"]:
                # For delay months, ensure we don't go below 0
                low_params[param] = max(0, base_params[param] * (1 - sensitivity_range / 100))
            else:
                low_params[param] = base_params[param] * (1 - sensitivity_range / 100)
            
            low_cost = calculator.calculate_total_capex(**low_params)
            
            # Calculate high case (parameter increased by sensitivity_range%)
            high_params = base_params.copy()
            high_params[param] = base_params[param] * (1 + sensitivity_range / 100)
            high_cost = calculator.calculate_total_capex(**high_params)
            
            # Store results in millions
            results[param] = {
                "low": low_cost / 1_000_000,
                "high": high_cost / 1_000_000,
                "range": (high_cost - low_cost) / 1_000_000,
                "base": base_cost / 1_000_000
            }
        
        return results
    
    def calculate_parameter_impact(self, base_params: Dict[str, Any],
                                 parameter: str, change_percentage: float,
                                 calculator: CapExCalculator) -> Tuple[float, float]:
        """
        Calculate the impact of changing a single parameter.
        
        Args:
            base_params: Base case parameters
            parameter: Parameter to change
            change_percentage: Percentage change (positive or negative)
            calculator: CapExCalculator instance
            
        Returns:
            Tuple of (new_cost, cost_change)
        """
        base_cost = calculator.calculate_total_capex(**base_params)
        
        # Create modified parameters
        modified_params = base_params.copy()
        if parameter == "delay_months" and change_percentage < 0:
            # Ensure delay months doesn't go below 0
            modified_params[parameter] = max(0, base_params[parameter] * (1 + change_percentage / 100))
        else:
            modified_params[parameter] = base_params[parameter] * (1 + change_percentage / 100)
        
        new_cost = calculator.calculate_total_capex(**modified_params)
        cost_change = new_cost - base_cost
        
        return new_cost, cost_change
    
    def generate_tornado_data(self, base_params: Dict[str, Any],
                            sensitivity_range: float,
                            calculator: CapExCalculator) -> List[Dict[str, Any]]:
        """
        Generate data for tornado chart visualization.
        
        Args:
            base_params: Base case parameters
            sensitivity_range: Sensitivity range percentage
            calculator: CapExCalculator instance
            
        Returns:
            List of dictionaries with tornado chart data
        """
        tornado_data = []
        base_cost = calculator.calculate_total_capex(**base_params)
        
        # Parameter display names
        param_names = {
            "equipment_cost_per_mw": "Equipment Cost",
            "labor_cost_per_mw": "Labor Cost",
            "interest_rate": "Interest Rate",
            "delay_months": "Permitting Delay",
            "inflation_rate": "Inflation Rate"
        }
        
        for param in self.sensitivity_parameters:
            if param not in base_params:
                continue
            
            # Calculate low and high impacts
            low_cost, low_change = self.calculate_parameter_impact(
                base_params, param, -sensitivity_range, calculator
            )
            high_cost, high_change = self.calculate_parameter_impact(
                base_params, param, sensitivity_range, calculator
            )
            
            tornado_data.append({
                "parameter": param_names.get(param, param),
                "low_impact": low_change / 1_000_000,  # Convert to millions
                "high_impact": high_change / 1_000_000,
                "range": abs(high_change - low_change) / 1_000_000,
                "base_cost": base_cost / 1_000_000
            })
        
        # Sort by range (largest impact first)
        tornado_data.sort(key=lambda x: x["range"], reverse=True)
        
        return tornado_data
    
    def monte_carlo_analysis(self, base_params: Dict[str, Any],
                           num_simulations: int,
                           parameter_distributions: Dict[str, Dict[str, float]],
                           calculator: CapExCalculator) -> Dict[str, Any]:
        """
        Perform Monte Carlo simulation for risk analysis.
        
        Args:
            base_params: Base case parameters
            num_simulations: Number of Monte Carlo simulations
            parameter_distributions: Distribution parameters for each variable
            calculator: CapExCalculator instance
            
        Returns:
            Dictionary with Monte Carlo results
        """
        results = []
        
        for _ in range(num_simulations):
            # Generate random parameters based on distributions
            sim_params = base_params.copy()
            
            for param, distribution in parameter_distributions.items():
                if param in base_params:
                    if distribution["type"] == "normal":
                        # Normal distribution
                        value = np.random.normal(
                            distribution["mean"], 
                            distribution["std"]
                        )
                        # Ensure positive values for most parameters
                        if param != "interest_rate":
                            value = max(0, value)
                        sim_params[param] = value
                    
                    elif distribution["type"] == "uniform":
                        # Uniform distribution
                        value = np.random.uniform(
                            distribution["min"],
                            distribution["max"]
                        )
                        sim_params[param] = value
            
            # Calculate cost for this simulation
            sim_cost = calculator.calculate_total_capex(**sim_params)
            results.append(sim_cost / 1_000_000)  # Convert to millions
        
        # Calculate statistics
        results_array = np.array(results)
        
        return {
            "mean": np.mean(results_array),
            "std": np.std(results_array),
            "min": np.min(results_array),
            "max": np.max(results_array),
            "percentile_5": np.percentile(results_array, 5),
            "percentile_25": np.percentile(results_array, 25),
            "percentile_50": np.percentile(results_array, 50),
            "percentile_75": np.percentile(results_array, 75),
            "percentile_95": np.percentile(results_array, 95),
            "results": results_array
        }
    
    def calculate_break_even_analysis(self, base_params: Dict[str, Any],
                                    target_cost: float,
                                    parameter: str,
                                    calculator: CapExCalculator) -> float:
        """
        Calculate break-even value for a parameter to achieve target cost.
        
        Args:
            base_params: Base case parameters
            target_cost: Target total cost
            parameter: Parameter to adjust
            calculator: CapExCalculator instance
            
        Returns:
            Break-even value for the parameter
        """
        # Use binary search to find break-even value
        low_multiplier = 0.1
        high_multiplier = 5.0
        tolerance = 1000  # $1,000 tolerance
        
        for _ in range(100):  # Maximum iterations
            mid_multiplier = (low_multiplier + high_multiplier) / 2
            
            test_params = base_params.copy()
            test_params[parameter] = base_params[parameter] * mid_multiplier
            
            test_cost = calculator.calculate_total_capex(**test_params)
            
            if abs(test_cost - target_cost) < tolerance:
                return base_params[parameter] * mid_multiplier
            
            if test_cost < target_cost:
                low_multiplier = mid_multiplier
            else:
                high_multiplier = mid_multiplier
        
        # Return best estimate if convergence not achieved
        return base_params[parameter] * mid_multiplier
