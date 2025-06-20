# Forecasting

# ⚡ CapitalGreenModel - Renewable Energy CapEx Forecasting Model

A comprehensive web-based application for analyzing capital expenditure (CapEx) forecasting in renewable energy projects. Built with Streamlit and Python, this tool provides multi-scenario analysis, interactive visualizations, and detailed cost breakdowns for solar, wind, battery storage, and hybrid energy projects.

## 🎯 Overview

CapitalGreenModel is designed for renewable energy project developers, financial analysts, and investment decision-makers who need to:
- Model capital expenditures across different scenarios
- Analyze cost sensitivity to various parameters
- Compare project economics across different timelines
- Generate professional reports and visualizations

## ✨ Key Features

### 📊 Multi-Scenario Analysis
- **Base Case**: Standard project assumptions
- **Optimistic**: Reduced costs and faster timelines
- **Pessimistic**: Increased costs and extended delays
- **Custom Scenarios**: User-defined parameter adjustments

### 🏗️ Technology Support
- **Solar PV**: Photovoltaic solar farm projects
- **Wind**: Onshore and offshore wind projects
- **Battery Storage**: Energy storage systems
- **Hybrid Solar+Storage**: Combined solar and storage projects

### 💰 Comprehensive Cost Modeling
- **Equipment Costs**: Solar panels, wind turbines, batteries, inverters
- **Labor Costs**: Construction, installation, commissioning
- **Financing Costs**: Interest, delay penalties, carrying costs
- **Other Costs**: Permitting, legal, interconnection, contingencies

### 📈 Interactive Visualizations
- Scenario comparison charts
- Cost breakdown pie charts
- Timeline analysis graphs
- Sensitivity analysis tornado charts
- Export capabilities (Excel format)

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Installation

1. **Clone or download the project**
   ```bash
   cd CapitalGreenModel
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit plotly pandas numpy xlsxwriter
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:8501`
   - The application will load automatically

## 📖 Usage Guide

### 1. Project Setup
- **Project Name**: Enter a descriptive name for your project
- **Capacity**: Set project capacity in MW (1-1000 MW range)
- **Technology Type**: Select from Solar PV, Wind, Battery Storage, or Hybrid

### 2. Cost Parameters
- **Equipment Cost ($/MW)**: Base equipment cost per megawatt
- **Labor Cost ($/MW)**: Labor and construction costs per megawatt
- **Permitting & Legal Costs ($)**: Administrative and regulatory costs

### 3. Financial Parameters
- **Interest Rate (%)**: Annual financing rate (1-15%)
- **Inflation Rate (%)**: Annual inflation assumption (0-10%)

### 4. Timeline Parameters
- **Permitting Delay (months)**: Additional time for regulatory approval
- **Construction Duration (months)**: Project construction timeline

### 5. Analysis Results
The application automatically generates:
- Scenario comparison tables
- Cost breakdown visualizations
- Timeline analysis charts
- Sensitivity analysis results

## 🏗️ Project Structure

```
CapitalGreenModel/
├── app.py                          # Main Streamlit application
├── models/
│   ├── capex_calculator.py         # Core financial calculations
│   └── sensitivity_analyzer.py     # Sensitivity analysis engine
├── utils/
│   ├── financial_utils.py          # Financial utility functions
│   └── visualization.py            # Visualization utilities
├── .streamlit/                     # Streamlit configuration
├── attached_assets/                # Additional resources
├── pyproject.toml                  # Project dependencies
└── README.md                       # This file
```

## 🔧 Technical Details

### Core Components

#### CapExCalculator Class
- Handles all financial calculations
- Supports inflation adjustments
- Includes delay penalty calculations
- Provides detailed cost breakdowns

#### SensitivityAnalyzer Class
- Performs parameter sensitivity analysis
- Generates tornado charts
- Identifies key cost drivers

#### Financial Models
- **Equipment Cost Model**: Inflation-adjusted equipment costs
- **Labor Cost Model**: Duration and inflation-adjusted labor costs
- **Financing Cost Model**: Interest and delay penalty calculations
- **Other Costs Model**: Permitting, legal, and contingency costs

### Key Calculations

1. **Total CapEx = Equipment + Labor + Other + Financing**
2. **Cost per MW = Total CapEx / Project Capacity**
3. **Inflation Adjustment = Base Cost × (1 + Inflation Rate)^Timeline**
4. **Delay Penalty = Principal × Interest Rate × (Delay Months / 12) × 0.5**

## 📊 Output Examples

### Scenario Comparison Table
| Scenario | 3 Years | 5 Years | 10 Years |
|----------|---------|---------|----------|
| Base Case | $125.4M | $138.2M | $165.8M |
| Optimistic | $108.6M | $119.7M | $143.9M |
| Pessimistic | $156.7M | $172.4M | $207.1M |

### Cost Breakdown (Typical)
- **Equipment**: 65-75% of total cost
- **Labor**: 15-20% of total cost
- **Financing**: 5-10% of total cost
- **Other**: 5-10% of total cost

## 🎛️ Advanced Features

### Sensitivity Analysis
- Identify most impactful parameters
- Quantify risk factors
- Optimize project parameters

### Export Functionality
- Download results as Excel files
- Generate professional reports
- Share analysis with stakeholders

### Real-time Updates
- Instant recalculation on parameter changes
- Dynamic visualization updates
- Interactive parameter exploration

## 🔍 Use Cases

### Project Development
- Feasibility studies
- Budget planning
- Investment analysis
- Risk assessment

### Financial Analysis
- Cost optimization
- Sensitivity testing
- Scenario planning
- Due diligence

### Stakeholder Communication
- Executive presentations
- Investor reports
- Regulatory submissions
- Team collaboration

## 🛠️ Customization

### Adding New Technologies
1. Modify the technology selection in `app.py`
2. Add technology-specific cost parameters
3. Update calculation methods in `capex_calculator.py`

### Custom Scenarios
1. Define new scenario parameters
2. Add scenario multipliers
3. Update visualization logic

### Additional Cost Components
1. Extend the `CapExCalculator` class
2. Add new calculation methods
3. Update cost breakdown functions

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
streamlit run app.py --server.port 8501
```

**Dependencies Not Found**
```bash
pip install -r requirements.txt
```

**Performance Issues**
```bash
pip install watchdog
```

### Performance Optimization
- Install Watchdog for better file monitoring
- Use appropriate browser (Chrome/Firefox recommended)
- Close unnecessary browser tabs

## 📝 License

This project is provided as-is for educational and professional use. Please ensure compliance with your organization's policies and applicable regulations.

## 🤝 Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For questions or support:
- Check the troubleshooting section
- Review the code comments
- Examine the calculation methods
- Test with different parameters

## 🔄 Version History

- **v1.0**: Initial release with basic CapEx modeling
- **v1.1**: Added sensitivity analysis
- **v1.2**: Enhanced visualizations and export features
- **v1.3**: Improved user interface and performance

---

**Built with ❤️ for the renewable energy industry**
