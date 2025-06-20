import numpy as np
from typing import Dict, Tuple

class CapExCalculator:
    """
    Capital Expenditure Calculator for Renewable Energy Projects
    
    This class handles the core financial calculations for renewable energy
    project capital expenditure modeling across different scenarios and timelines.
    """
    
    def __init__(self):
        """Initialize the CapEx calculator with default parameters."""
        self.escalation_factors = {
            "equipment": 0.02,  # 2% annual escalation
            "labor": 0.035,     # 3.5% annual escalation
            "materials": 0.025  # 2.5% annual escalation
        }
    
    def calculate_equipment_cost(self, capacity: float, cost_per_mw: float, 
                               timeline_years: int, inflation_rate: float) -> float:
        """
        Calculate total equipment cost with inflation adjustment.
        
        Args:
            capacity: Project capacity in MW
            cost_per_mw: Equipment cost per MW
            timeline_years: Project timeline in years
            inflation_rate: Annual inflation rate as percentage
            
        Returns:
            Total equipment cost adjusted for inflation
        """
        base_cost = capacity * cost_per_mw
        # Apply inflation over the timeline
        inflation_multiplier = (1 + inflation_rate / 100) ** timeline_years
        return base_cost * inflation_multiplier
    
    def calculate_labor_cost(self, capacity: float, labor_cost_per_mw: float,
                           timeline_years: int, inflation_rate: float,
                           construction_months: int) -> float:
        """
        Calculate total labor cost with inflation and construction duration adjustments.
        
        Args:
            capacity: Project capacity in MW
            labor_cost_per_mw: Labor cost per MW
            timeline_years: Project timeline in years
            inflation_rate: Annual inflation rate as percentage
            construction_months: Construction duration in months
            
        Returns:
            Total labor cost adjusted for inflation and construction duration
        """
        base_labor_cost = capacity * labor_cost_per_mw
        
        # Adjust for construction duration (longer construction = higher labor costs)
        duration_multiplier = 1 + (construction_months - 12) * 0.02  # 2% increase per additional month beyond 12
        duration_multiplier = max(0.8, min(2.0, duration_multiplier))  # Cap between 80% and 200%
        
        # Apply inflation
        inflation_multiplier = (1 + inflation_rate / 100) ** timeline_years
        
        return base_labor_cost * duration_multiplier * inflation_multiplier
    
    def calculate_financing_cost(self, principal: float, interest_rate: float,
                               timeline_years: int, delay_months: int) -> float:
        """
        Calculate financing costs including interest and delay penalties.
        
        Args:
            principal: Principal amount to finance
            interest_rate: Annual interest rate as percentage
            timeline_years: Project timeline in years
            delay_months: Permitting delay in months
            
        Returns:
            Total financing cost
        """
        # Convert interest rate to decimal
        annual_rate = interest_rate / 100
        
        # Calculate interest over the timeline
        interest_cost = principal * annual_rate * timeline_years
        
        # Add delay costs (additional carrying costs)
        delay_penalty = principal * annual_rate * (delay_months / 12) * 0.5
        
        return interest_cost + delay_penalty
    
    def calculate_other_costs(self, permitting_cost: float, capacity: float,
                            timeline_years: int, delay_months: int) -> float:
        """
        Calculate other project costs including permitting, legal, and contingencies.
        
        Args:
            permitting_cost: Base permitting and legal costs
            capacity: Project capacity in MW
            timeline_years: Project timeline in years
            delay_months: Permitting delay in months
            
        Returns:
            Total other costs
        """
        # Base other costs (permitting, legal, environmental, etc.)
        base_other_costs = permitting_cost
        
        # Add capacity-based costs (interconnection, transmission, etc.)
        capacity_based_costs = capacity * 25000  # $25K per MW for interconnection
        
        # Add delay-related costs
        delay_costs = delay_months * 10000  # $10K per month of delay
        
        # Add contingency (5% of total other costs)
        total_other = base_other_costs + capacity_based_costs + delay_costs
        contingency = total_other * 0.05
        
        return total_other + contingency
    
    def calculate_total_capex(self, capacity: float, equipment_cost_per_mw: float,
                            labor_cost_per_mw: float, permitting_cost: float,
                            interest_rate: float, timeline_years: int,
                            delay_months: int, inflation_rate: float,
                            construction_months: int) -> float:
        """
        Calculate total capital expenditure for the renewable energy project.
        
        Args:
            capacity: Project capacity in MW
            equipment_cost_per_mw: Equipment cost per MW
            labor_cost_per_mw: Labor cost per MW
            permitting_cost: Permitting and legal costs
            interest_rate: Annual interest rate as percentage
            timeline_years: Project timeline in years
            delay_months: Permitting delay in months
            inflation_rate: Annual inflation rate as percentage
            construction_months: Construction duration in months
            
        Returns:
            Total project capital expenditure
        """
        # Calculate individual cost components
        equipment_cost = self.calculate_equipment_cost(
            capacity, equipment_cost_per_mw, timeline_years, inflation_rate
        )
        
        labor_cost = self.calculate_labor_cost(
            capacity, labor_cost_per_mw, timeline_years, inflation_rate, construction_months
        )
        
        other_costs = self.calculate_other_costs(
            permitting_cost, capacity, timeline_years, delay_months
        )
        
        # Calculate financing costs on the total project cost
        principal = equipment_cost + labor_cost + other_costs
        financing_cost = self.calculate_financing_cost(
            principal, interest_rate, timeline_years, delay_months
        )
        
        return equipment_cost + labor_cost + other_costs + financing_cost
    
    def get_cost_breakdown(self, capacity: float, equipment_cost_per_mw: float,
                          labor_cost_per_mw: float, permitting_cost: float,
                          interest_rate: float, timeline_years: int,
                          delay_months: int, inflation_rate: float,
                          construction_months: int) -> Dict[str, float]:
        """
        Get detailed cost breakdown for the project.
        
        Returns:
            Dictionary with cost breakdown by category
        """
        equipment_cost = self.calculate_equipment_cost(
            capacity, equipment_cost_per_mw, timeline_years, inflation_rate
        )
        
        labor_cost = self.calculate_labor_cost(
            capacity, labor_cost_per_mw, timeline_years, inflation_rate, construction_months
        )
        
        other_costs = self.calculate_other_costs(
            permitting_cost, capacity, timeline_years, delay_months
        )
        
        principal = equipment_cost + labor_cost + other_costs
        financing_cost = self.calculate_financing_cost(
            principal, interest_rate, timeline_years, delay_months
        )
        
        return {
            "equipment": equipment_cost,
            "labor": labor_cost,
            "financing": financing_cost,
            "other": other_costs,
            "total": equipment_cost + labor_cost + financing_cost + other_costs
        }
    
    def calculate_levelized_cost(self, total_capex: float, capacity: float,
                               capacity_factor: float, lifetime_years: int,
                               discount_rate: float) -> float:
        """
        Calculate Levelized Cost of Energy (LCOE).
        
        Args:
            total_capex: Total capital expenditure
            capacity: Project capacity in MW
            capacity_factor: Capacity factor as decimal (0.0 to 1.0)
            lifetime_years: Project lifetime in years
            discount_rate: Discount rate as percentage
            
        Returns:
            LCOE in $/MWh
        """
        # Annual energy generation in MWh
        annual_generation = capacity * 8760 * capacity_factor
        
        # Calculate present value of total generation
        discount_rate_decimal = discount_rate / 100
        pv_generation = 0
        
        for year in range(1, lifetime_years + 1):
            pv_generation += annual_generation / ((1 + discount_rate_decimal) ** year)
        
        # LCOE = Total CapEx / PV of Total Generation
        return total_capex / pv_generation if pv_generation > 0 else 0
