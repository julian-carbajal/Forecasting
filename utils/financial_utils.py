import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta

class FinancialUtils:
    """
    Utility functions for financial calculations and analysis
    in renewable energy project modeling.
    """
    
    @staticmethod
    def calculate_npv(cash_flows: List[float], discount_rate: float) -> float:
        """
        Calculate Net Present Value of cash flows.
        
        Args:
            cash_flows: List of cash flows (negative for costs, positive for revenues)
            discount_rate: Discount rate as percentage
            
        Returns:
            Net Present Value
        """
        npv = 0
        rate = discount_rate / 100
        
        for i, cash_flow in enumerate(cash_flows):
            npv += cash_flow / ((1 + rate) ** i)
        
        return npv
    
    @staticmethod
    def calculate_irr(cash_flows: List[float], initial_guess: float = 0.1) -> float:
        """
        Calculate Internal Rate of Return using Newton-Raphson method.
        
        Args:
            cash_flows: List of cash flows
            initial_guess: Initial guess for IRR
            
        Returns:
            Internal Rate of Return as decimal
        """
        def npv_function(rate):
            return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))
        
        def npv_derivative(rate):
            return sum(-i * cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cash_flows))
        
        rate = initial_guess
        for _ in range(100):  # Maximum iterations
            npv = npv_function(rate)
            derivative = npv_derivative(rate)
            
            if abs(derivative) < 1e-12:
                break
                
            new_rate = rate - npv / derivative
            
            if abs(new_rate - rate) < 1e-8:
                return new_rate
                
            rate = new_rate
        
        return rate
    
    @staticmethod
    def calculate_payback_period(cash_flows: List[float]) -> float:
        """
        Calculate payback period for investment.
        
        Args:
            cash_flows: List of cash flows (first should be negative investment)
            
        Returns:
            Payback period in years
        """
        cumulative = 0
        for i, cash_flow in enumerate(cash_flows):
            cumulative += cash_flow
            if cumulative >= 0:
                # Linear interpolation for fractional year
                if i > 0 and cash_flows[i] != 0:
                    fraction = (cumulative - cash_flows[i]) / cash_flows[i]
                    return i - fraction
                return i
        
        return float('inf')  # No payback
    
    @staticmethod
    def escalate_cost(base_cost: float, escalation_rate: float, years: int) -> float:
        """
        Escalate cost with compound growth.
        
        Args:
            base_cost: Base cost amount
            escalation_rate: Annual escalation rate as percentage
            years: Number of years to escalate
            
        Returns:
            Escalated cost
        """
        return base_cost * ((1 + escalation_rate / 100) ** years)
    
    @staticmethod
    def calculate_real_discount_rate(nominal_rate: float, inflation_rate: float) -> float:
        """
        Calculate real discount rate from nominal rate and inflation.
        
        Args:
            nominal_rate: Nominal discount rate as percentage
            inflation_rate: Inflation rate as percentage
            
        Returns:
            Real discount rate as percentage
        """
        return ((1 + nominal_rate / 100) / (1 + inflation_rate / 100) - 1) * 100
    
    @staticmethod
    def create_cash_flow_schedule(capex: float, annual_revenue: float,
                                annual_opex: float, project_life: int,
                                construction_years: int = 2) -> Dict[str, List[float]]:
        """
        Create cash flow schedule for project analysis.
        
        Args:
            capex: Total capital expenditure
            annual_revenue: Annual revenue
            annual_opex: Annual operating expenses
            project_life: Project lifetime in years
            construction_years: Construction period in years
            
        Returns:
            Dictionary with cash flow components
        """
        total_years = construction_years + project_life
        years = list(range(total_years + 1))
        
        # Initialize cash flow arrays
        capex_flows = [0] * (total_years + 1)
        revenue_flows = [0] * (total_years + 1)
        opex_flows = [0] * (total_years + 1)
        
        # Distribute CapEx during construction years
        annual_capex = capex / construction_years
        for year in range(1, construction_years + 1):
            capex_flows[year] = -annual_capex
        
        # Revenue and OpEx during operational years
        for year in range(construction_years + 1, total_years + 1):
            revenue_flows[year] = annual_revenue
            opex_flows[year] = -annual_opex
        
        # Calculate net cash flows
        net_flows = [capex_flows[i] + revenue_flows[i] + opex_flows[i] 
                    for i in range(total_years + 1)]
        
        return {
            "years": years,
            "capex": capex_flows,
            "revenue": revenue_flows,
            "opex": opex_flows,
            "net": net_flows
        }
    
    @staticmethod
    def calculate_debt_service(principal: float, interest_rate: float,
                             term_years: int, payment_type: str = "equal") -> Dict[str, List[float]]:
        """
        Calculate debt service schedule.
        
        Args:
            principal: Loan principal amount
            interest_rate: Annual interest rate as percentage
            term_years: Loan term in years
            payment_type: "equal" for equal payments, "interest_only" for interest-only
            
        Returns:
            Dictionary with debt service components
        """
        rate = interest_rate / 100
        
        if payment_type == "equal":
            # Equal payment calculation
            payment = principal * (rate * (1 + rate) ** term_years) / ((1 + rate) ** term_years - 1)
            
            years = list(range(term_years + 1))
            balances = [principal]
            interest_payments = [0]
            principal_payments = [0]
            total_payments = [0]
            
            for year in range(1, term_years + 1):
                interest = balances[year - 1] * rate
                principal_payment = payment - interest
                new_balance = balances[year - 1] - principal_payment
                
                balances.append(max(0, new_balance))
                interest_payments.append(interest)
                principal_payments.append(principal_payment)
                total_payments.append(payment)
        
        else:  # interest_only
            annual_interest = principal * rate
            
            years = list(range(term_years + 1))
            balances = [principal] * (term_years + 1)
            balances[-1] = 0  # Principal repaid at end
            
            interest_payments = [0] + [annual_interest] * term_years
            principal_payments = [0] * term_years + [principal]
            total_payments = [0] + [annual_interest] * (term_years - 1) + [annual_interest + principal]
        
        return {
            "years": years,
            "balances": balances,
            "interest": interest_payments,
            "principal": principal_payments,
            "total": total_payments
        }
    
    @staticmethod
    def format_currency(amount: float, decimals: int = 0) -> str:
        """
        Format currency with appropriate units (K, M, B).
        
        Args:
            amount: Amount to format
            decimals: Number of decimal places
            
        Returns:
            Formatted currency string
        """
        if abs(amount) >= 1e9:
            return f"${amount/1e9:.{decimals}f}B"
        elif abs(amount) >= 1e6:
            return f"${amount/1e6:.{decimals}f}M"
        elif abs(amount) >= 1e3:
            return f"${amount/1e3:.{decimals}f}K"
        else:
            return f"${amount:.{decimals}f}"
    
    @staticmethod
    def calculate_tax_depreciation(asset_cost: float, depreciation_method: str = "macrs",
                                 asset_life: int = 7) -> List[float]:
        """
        Calculate tax depreciation schedule.
        
        Args:
            asset_cost: Cost of asset to depreciate
            depreciation_method: Depreciation method ("macrs", "straight_line")
            asset_life: Asset life in years
            
        Returns:
            List of annual depreciation amounts
        """
        if depreciation_method == "straight_line":
            annual_depreciation = asset_cost / asset_life
            return [annual_depreciation] * asset_life
        
        elif depreciation_method == "macrs":
            # MACRS percentages for different asset lives
            macrs_schedules = {
                5: [0.2, 0.32, 0.192, 0.1152, 0.1152, 0.0576],
                7: [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446],
                10: [0.1, 0.18, 0.144, 0.1152, 0.0922, 0.0737, 0.0655, 0.0655, 0.0656, 0.0655, 0.0328]
            }
            
            if asset_life in macrs_schedules:
                percentages = macrs_schedules[asset_life]
                return [asset_cost * pct for pct in percentages]
            else:
                # Default to straight line if MACRS schedule not available
                annual_depreciation = asset_cost / asset_life
                return [annual_depreciation] * asset_life
        
        else:
            raise ValueError(f"Unknown depreciation method: {depreciation_method}")
