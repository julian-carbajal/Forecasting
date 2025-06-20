import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any

class VisualizationUtils:
    """
    Utility class for creating financial visualizations and charts
    for renewable energy project analysis.
    """
    
    @staticmethod
    def create_tornado_chart(sensitivity_data: Dict[str, Dict[str, float]]) -> go.Figure:
        """
        Create a tornado chart for sensitivity analysis.
        
        Args:
            sensitivity_data: Dictionary with sensitivity analysis results
            
        Returns:
            Plotly figure object
        """
        parameters = []
        low_values = []
        high_values = []
        ranges = []
        
        for param, data in sensitivity_data.items():
            param_display = param.replace("_", " ").title()
            parameters.append(param_display)
            low_values.append(data["low"])
            high_values.append(data["high"])
            ranges.append(abs(data["high"] - data["low"]))
        
        # Sort by range (largest impact first)
        sorted_data = sorted(zip(parameters, low_values, high_values, ranges), 
                           key=lambda x: x[3], reverse=True)
        parameters, low_values, high_values, ranges = zip(*sorted_data)
        
        # Create tornado chart
        fig = go.Figure()
        
        # Base case line (assuming base case is approximately the midpoint)
        base_values = [(low + high) / 2 for low, high in zip(low_values, high_values)]
        base_line = sum(base_values) / len(base_values)
        
        # Add bars for low and high scenarios
        fig.add_trace(go.Bar(
            y=parameters,
            x=[high - base_line for high in high_values],
            orientation='h',
            name='High Scenario',
            marker_color='lightcoral',
            base=base_line
        ))
        
        fig.add_trace(go.Bar(
            y=parameters,
            x=[base_line - low for low in low_values],
            orientation='h',
            name='Low Scenario',
            marker_color='lightblue',
            base=[low for low in low_values]
        ))
        
        # Add vertical line for base case
        fig.add_vline(x=base_line, line_dash="dash", line_color="black", 
                     annotation_text="Base Case")
        
        fig.update_layout(
            title="Sensitivity Analysis - Tornado Chart",
            xaxis_title="Total Project Cost ($M)",
            yaxis_title="Parameters",
            barmode='overlay',
            height=400,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_scenario_waterfall(base_cost: float, scenario_adjustments: Dict[str, float]) -> go.Figure:
        """
        Create waterfall chart showing cost build-up from base case to scenario.
        
        Args:
            base_cost: Base case total cost
            scenario_adjustments: Dictionary of cost adjustments by category
            
        Returns:
            Plotly figure object
        """
        categories = ["Base Case"] + list(scenario_adjustments.keys()) + ["Total"]
        values = [base_cost] + list(scenario_adjustments.values()) + [base_cost + sum(scenario_adjustments.values())]
        
        # Create cumulative values for positioning
        cumulative = [base_cost]
        running_total = base_cost
        for adj in scenario_adjustments.values():
            running_total += adj
            cumulative.append(running_total)
        cumulative.append(running_total)
        
        fig = go.Figure(go.Waterfall(
            name="Cost Build-up",
            orientation="v",
            measure=["absolute"] + ["relative"] * len(scenario_adjustments) + ["total"],
            x=categories,
            textposition="outside",
            text=[f"${v/1e6:.1f}M" for v in values],
            y=values,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title="Cost Build-up: Base Case to Scenario",
            xaxis_title="Cost Components",
            yaxis_title="Cost ($M)",
            height=500
        )
        
        return fig
    
    @staticmethod
    def create_cost_breakdown_sunburst(cost_breakdown: Dict[str, float]) -> go.Figure:
        """
        Create sunburst chart for hierarchical cost breakdown.
        
        Args:
            cost_breakdown: Dictionary with cost breakdown by category
            
        Returns:
            Plotly figure object
        """
        # Prepare data for sunburst chart
        ids = ["Total"] + list(cost_breakdown.keys())
        parents = [""] + ["Total"] * len(cost_breakdown)
        values = [sum(cost_breakdown.values())] + list(cost_breakdown.values())
        labels = ["Total Project Cost"] + [k.replace("_", " ").title() for k in cost_breakdown.keys()]
        
        fig = go.Figure(go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total"
        ))
        
        fig.update_layout(
            title="Project Cost Breakdown",
            font_size=12,
            height=500
        )
        
        return fig
    
    @staticmethod
    def create_timeline_gantt(project_phases: Dict[str, Dict[str, str]]) -> go.Figure:
        """
        Create Gantt chart for project timeline.
        
        Args:
            project_phases: Dictionary with phase information (start, end dates)
            
        Returns:
            Plotly figure object
        """
        df_phases = []
        for phase, dates in project_phases.items():
            df_phases.append({
                "Task": phase,
                "Start": dates["start"],
                "Finish": dates["end"],
                "Resource": "Project Team"
            })
        
        df = pd.DataFrame(df_phases)
        
        fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Resource")
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            title="Project Timeline",
            xaxis_title="Date",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_cash_flow_chart(cash_flow_data: Dict[str, List[float]]) -> go.Figure:
        """
        Create cash flow visualization.
        
        Args:
            cash_flow_data: Dictionary with cash flow components over time
            
        Returns:
            Plotly figure object
        """
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Annual Cash Flows", "Cumulative Cash Flow"),
            vertical_spacing=0.1
        )
        
        years = cash_flow_data["years"]
        
        # Annual cash flows (stacked bar)
        if "capex" in cash_flow_data:
            fig.add_trace(
                go.Bar(x=years, y=cash_flow_data["capex"], name="CapEx", 
                      marker_color="red"),
                row=1, col=1
            )
        
        if "revenue" in cash_flow_data:
            fig.add_trace(
                go.Bar(x=years, y=cash_flow_data["revenue"], name="Revenue", 
                      marker_color="green"),
                row=1, col=1
            )
        
        if "opex" in cash_flow_data:
            fig.add_trace(
                go.Bar(x=years, y=cash_flow_data["opex"], name="OpEx", 
                      marker_color="orange"),
                row=1, col=1
            )
        
        # Cumulative cash flow
        cumulative = np.cumsum(cash_flow_data["net"])
        fig.add_trace(
            go.Scatter(x=years, y=cumulative, mode="lines+markers", 
                      name="Cumulative Cash Flow", line_color="blue"),
            row=2, col=1
        )
        
        # Add break-even line
        fig.add_hline(y=0, line_dash="dash", line_color="black", row=2, col=1)
        
        fig.update_layout(
            height=600,
            title="Project Cash Flow Analysis",
            barmode="relative"
        )
        
        fig.update_xaxes(title_text="Year", row=2, col=1)
        fig.update_yaxes(title_text="Cash Flow ($M)", row=1, col=1)
        fig.update_yaxes(title_text="Cumulative Cash Flow ($M)", row=2, col=1)
        
        return fig
    
    @staticmethod
    def create_monte_carlo_distribution(monte_carlo_results: np.ndarray) -> go.Figure:
        """
        Create histogram of Monte Carlo simulation results.
        
        Args:
            monte_carlo_results: Array of simulation results
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        # Histogram
        fig.add_trace(go.Histogram(
            x=monte_carlo_results,
            nbinsx=50,
            name="Cost Distribution",
            opacity=0.7
        ))
        
        # Add statistical lines
        mean_val = np.mean(monte_carlo_results)
        p5 = np.percentile(monte_carlo_results, 5)
        p95 = np.percentile(monte_carlo_results, 95)
        
        fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                     annotation_text=f"Mean: ${mean_val:.1f}M")
        fig.add_vline(x=p5, line_dash="dot", line_color="orange", 
                     annotation_text=f"P5: ${p5:.1f}M")
        fig.add_vline(x=p95, line_dash="dot", line_color="orange", 
                     annotation_text=f"P95: ${p95:.1f}M")
        
        fig.update_layout(
            title="Monte Carlo Simulation Results",
            xaxis_title="Total Project Cost ($M)",
            yaxis_title="Frequency",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_comparison_radar(scenarios: Dict[str, Dict[str, float]]) -> go.Figure:
        """
        Create radar chart comparing different scenarios.
        
        Args:
            scenarios: Dictionary with scenario data
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        # Get categories from first scenario
        categories = list(next(iter(scenarios.values())).keys())
        
        for scenario_name, values in scenarios.items():
            fig.add_trace(go.Scatterpolar(
                r=list(values.values()),
                theta=categories,
                fill='toself',
                name=scenario_name
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(max(values.values()) for values in scenarios.values())]
                )),
            showlegend=True,
            title="Scenario Comparison Radar Chart",
            height=500
        )
        
        return fig
