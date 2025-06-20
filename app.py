import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime

from models.capex_calculator import CapExCalculator
from models.sensitivity_analyzer import SensitivityAnalyzer
from utils.financial_utils import FinancialUtils
from utils.visualization import VisualizationUtils

# Page configuration
st.set_page_config(
    page_title="Renewable Energy CapEx Forecasting Model",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'calculator' not in st.session_state:
    st.session_state.calculator = CapExCalculator()
if 'sensitivity_analyzer' not in st.session_state:
    st.session_state.sensitivity_analyzer = SensitivityAnalyzer()

# Main title
st.title("⚡ Renewable Energy CapEx Forecasting Model")
st.markdown("Multi-scenario capital expenditure analysis for renewable energy projects")

# Sidebar for input parameters
st.sidebar.header("Project Parameters")

# Project basic information
st.sidebar.subheader("Project Details")
project_name = st.sidebar.text_input("Project Name", value="Solar Farm Project Alpha")
project_capacity = st.sidebar.number_input("Project Capacity (MW)", min_value=1.0, max_value=1000.0, value=100.0, step=1.0)
technology_type = st.sidebar.selectbox("Technology Type", ["Solar PV", "Wind", "Battery Storage", "Hybrid Solar+Storage"])

# Key cost parameters
st.sidebar.subheader("Cost Parameters")
equipment_cost_per_mw = st.sidebar.number_input(
    "Equipment Cost ($/MW)", 
    min_value=100000, 
    max_value=5000000, 
    value=1200000, 
    step=10000,
    help="Base equipment cost per MW capacity"
)

labor_cost_per_mw = st.sidebar.number_input(
    "Labor Cost ($/MW)", 
    min_value=10000, 
    max_value=500000, 
    value=150000, 
    step=5000,
    help="Labor cost per MW capacity"
)

permitting_cost = st.sidebar.number_input(
    "Permitting & Legal Costs ($)", 
    min_value=50000, 
    max_value=5000000, 
    value=500000, 
    step=25000
)

# Financial parameters
st.sidebar.subheader("Financial Parameters")
interest_rate = st.sidebar.slider(
    "Interest Rate (%)", 
    min_value=1.0, 
    max_value=15.0, 
    value=5.5, 
    step=0.1,
    help="Annual interest rate for project financing"
)

inflation_rate = st.sidebar.slider(
    "Inflation Rate (%)", 
    min_value=0.0, 
    max_value=10.0, 
    value=2.5, 
    step=0.1
)

# Timeline parameters
st.sidebar.subheader("Timeline Parameters")
permitting_delay_months = st.sidebar.slider(
    "Permitting Delay (months)", 
    min_value=0, 
    max_value=36, 
    value=6,
    help="Additional months due to permitting delays"
)

construction_duration_months = st.sidebar.slider(
    "Construction Duration (months)", 
    min_value=6, 
    max_value=60, 
    value=18
)

# Scenario analysis section
st.header("📊 Scenario Analysis")

# Create scenarios
scenarios = {
    "Base Case": {
        "equipment_multiplier": 1.0,
        "labor_multiplier": 1.0,
        "delay_multiplier": 1.0,
        "interest_adjustment": 0.0
    },
    "Optimistic": {
        "equipment_multiplier": 0.85,
        "labor_multiplier": 0.90,
        "delay_multiplier": 0.5,
        "interest_adjustment": -0.5
    },
    "Pessimistic": {
        "equipment_multiplier": 1.25,
        "labor_multiplier": 1.30,
        "delay_multiplier": 2.0,
        "interest_adjustment": 1.5
    }
}

# Calculate costs for all scenarios and timelines
timelines = [3, 5, 10]
results_data = []

for timeline in timelines:
    for scenario_name, scenario_params in scenarios.items():
        # Adjust parameters based on scenario
        adj_equipment_cost = equipment_cost_per_mw * scenario_params["equipment_multiplier"]
        adj_labor_cost = labor_cost_per_mw * scenario_params["labor_multiplier"]
        adj_delay = int(permitting_delay_months * scenario_params["delay_multiplier"])
        adj_interest_rate = interest_rate + scenario_params["interest_adjustment"]
        
        # Calculate total project cost
        total_cost = st.session_state.calculator.calculate_total_capex(
            capacity=project_capacity,
            equipment_cost_per_mw=adj_equipment_cost,
            labor_cost_per_mw=adj_labor_cost,
            permitting_cost=permitting_cost,
            interest_rate=adj_interest_rate,
            timeline_years=timeline,
            delay_months=adj_delay,
            inflation_rate=inflation_rate,
            construction_months=construction_duration_months
        )
        
        # Calculate cost breakdown
        cost_breakdown = st.session_state.calculator.get_cost_breakdown(
            capacity=project_capacity,
            equipment_cost_per_mw=adj_equipment_cost,
            labor_cost_per_mw=adj_labor_cost,
            permitting_cost=permitting_cost,
            interest_rate=adj_interest_rate,
            timeline_years=timeline,
            delay_months=adj_delay,
            inflation_rate=inflation_rate,
            construction_months=construction_duration_months
        )
        
        results_data.append({
            "Timeline (Years)": timeline,
            "Scenario": scenario_name,
            "Total Cost ($M)": total_cost / 1_000_000,
            "Cost per MW ($K)": total_cost / project_capacity / 1_000,
            "Equipment Cost ($M)": cost_breakdown["equipment"] / 1_000_000,
            "Labor Cost ($M)": cost_breakdown["labor"] / 1_000_000,
            "Financing Cost ($M)": cost_breakdown["financing"] / 1_000_000,
            "Other Costs ($M)": cost_breakdown["other"] / 1_000_000
        })

# Create results DataFrame
results_df = pd.DataFrame(results_data)

# Display scenario comparison table
st.subheader("Scenario Comparison Summary")
pivot_table = results_df.pivot_table(
    index="Scenario", 
    columns="Timeline (Years)", 
    values="Total Cost ($M)", 
    aggfunc="mean"
)
st.dataframe(pivot_table.round(2), use_container_width=True)

# Visualization section
col1, col2 = st.columns(2)

with col1:
    # Scenario comparison chart
    fig_scenarios = px.bar(
        results_df, 
        x="Timeline (Years)", 
        y="Total Cost ($M)", 
        color="Scenario",
        title="Total Project Cost by Scenario and Timeline",
        barmode="group"
    )
    fig_scenarios.update_layout(height=400)
    st.plotly_chart(fig_scenarios, use_container_width=True)

with col2:
    # Cost breakdown chart for base case
    base_case_data = results_df[
        (results_df["Scenario"] == "Base Case") & 
        (results_df["Timeline (Years)"] == 5)
    ].iloc[0]
    
    cost_categories = ["Equipment Cost ($M)", "Labor Cost ($M)", "Financing Cost ($M)", "Other Costs ($M)"]
    cost_values = [base_case_data[cat] for cat in cost_categories]
    
    fig_breakdown = px.pie(
        values=cost_values,
        names=[cat.replace(" ($M)", "") for cat in cost_categories],
        title="Cost Breakdown - Base Case (5 Years)"
    )
    fig_breakdown.update_layout(height=400)
    st.plotly_chart(fig_breakdown, use_container_width=True)

# Sensitivity Analysis section
st.header("🔍 Sensitivity Analysis")

# Sensitivity analysis parameters
st.subheader("Sensitivity Analysis Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    sensitivity_timeline = st.selectbox("Analysis Timeline", [3, 5, 10], index=1)

with col2:
    base_scenario = st.selectbox("Base Scenario", list(scenarios.keys()), index=0)

with col3:
    sensitivity_range = st.slider("Sensitivity Range (%)", min_value=5, max_value=50, value=20)

# Perform sensitivity analysis
sensitivity_params = {
    "Equipment Cost": equipment_cost_per_mw,
    "Labor Cost": labor_cost_per_mw,
    "Interest Rate": interest_rate,
    "Permitting Delay": permitting_delay_months,
    "Inflation Rate": inflation_rate
}

sensitivity_results = st.session_state.sensitivity_analyzer.perform_sensitivity_analysis(
    base_params={
        "capacity": project_capacity,
        "equipment_cost_per_mw": equipment_cost_per_mw,
        "labor_cost_per_mw": labor_cost_per_mw,
        "permitting_cost": permitting_cost,
        "interest_rate": interest_rate,
        "timeline_years": sensitivity_timeline,
        "delay_months": permitting_delay_months,
        "inflation_rate": inflation_rate,
        "construction_months": construction_duration_months
    },
    sensitivity_range=sensitivity_range,
    calculator=st.session_state.calculator
)

# Display sensitivity analysis results
st.subheader("Sensitivity Analysis Results")

# Create tornado chart
fig_tornado = VisualizationUtils.create_tornado_chart(sensitivity_results)
st.plotly_chart(fig_tornado, use_container_width=True)

# Sensitivity data table
sensitivity_df = pd.DataFrame(sensitivity_results).T
sensitivity_df.columns = ["Low Impact ($M)", "High Impact ($M)", "Range ($M)", "Base Cost ($M)"]
sensitivity_df = sensitivity_df.round(2)
st.dataframe(sensitivity_df, use_container_width=True)

# Advanced Analysis section
st.header("📈 Advanced Analysis")

col1, col2 = st.columns(2)

with col1:
    # Cost escalation over time
    years = list(range(1, 11))
    base_cost = st.session_state.calculator.calculate_total_capex(
        capacity=project_capacity,
        equipment_cost_per_mw=equipment_cost_per_mw,
        labor_cost_per_mw=labor_cost_per_mw,
        permitting_cost=permitting_cost,
        interest_rate=interest_rate,
        timeline_years=5,
        delay_months=permitting_delay_months,
        inflation_rate=inflation_rate,
        construction_months=construction_duration_months
    )
    
    escalated_costs = []
    for year in years:
        escalated_cost = base_cost * ((1 + inflation_rate/100) ** (year - 1))
        escalated_costs.append(escalated_cost / 1_000_000)
    
    fig_escalation = px.line(
        x=years,
        y=escalated_costs,
        title="Cost Escalation Over Time",
        labels={"x": "Year", "y": "Total Cost ($M)"}
    )
    st.plotly_chart(fig_escalation, use_container_width=True)

with col2:
    # Risk assessment
    risk_factors = {
        "Low Risk": len([s for s in scenarios.values() if s["equipment_multiplier"] <= 1.0]),
        "Medium Risk": len([s for s in scenarios.values() if 1.0 < s["equipment_multiplier"] <= 1.15]),
        "High Risk": len([s for s in scenarios.values() if s["equipment_multiplier"] > 1.15])
    }
    
    fig_risk = px.pie(
        values=list(risk_factors.values()),
        names=list(risk_factors.keys()),
        title="Risk Assessment Distribution"
    )
    st.plotly_chart(fig_risk, use_container_width=True)

# Export functionality
st.header("📁 Export Analysis")

# Prepare export data
export_data = {
    "Project Summary": {
        "Project Name": project_name,
        "Capacity (MW)": project_capacity,
        "Technology": technology_type,
        "Analysis Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    "Scenario Results": results_df,
    "Sensitivity Analysis": sensitivity_df
}

col1, col2, col3 = st.columns(3)

with col1:
    # Export to CSV
    csv_buffer = io.StringIO()
    results_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📊 Download CSV Report",
        data=csv_buffer.getvalue(),
        file_name=f"{project_name.replace(' ', '_')}_capex_analysis.csv",
        mime="text/csv"
    )

with col2:
    # Export summary report
    summary_report = f"""
    RENEWABLE ENERGY CAPEX ANALYSIS REPORT
    =====================================
    
    Project: {project_name}
    Capacity: {project_capacity} MW
    Technology: {technology_type}
    Analysis Date: {datetime.now().strftime("%Y-%m-%d")}
    
    BASE CASE RESULTS (5-Year Timeline):
    Total Cost: ${base_cost/1_000_000:.2f}M
    Cost per MW: ${base_cost/project_capacity/1_000:.0f}K
    
    SCENARIO COMPARISON:
    {pivot_table.to_string()}
    
    KEY SENSITIVITY FACTORS:
    {sensitivity_df.to_string()}
    """
    
    st.download_button(
        label="📄 Download Summary Report",
        data=summary_report,
        file_name=f"{project_name.replace(' ', '_')}_summary_report.txt",
        mime="text/plain"
    )

with col3:
    # Export detailed analysis
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        results_df.to_excel(writer, sheet_name='Scenario Analysis', index=False)
        sensitivity_df.to_excel(writer, sheet_name='Sensitivity Analysis')
        pd.DataFrame([export_data["Project Summary"]]).to_excel(writer, sheet_name='Project Summary', index=False)
    
    st.download_button(
        label="📈 Download Excel Analysis",
        data=excel_buffer.getvalue(),
        file_name=f"{project_name.replace(' ', '_')}_detailed_analysis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Footer
st.markdown("---")
st.markdown("*Renewable Energy CapEx Forecasting Model - Built for Utility Finance Analysis*")
