# Vth Derivative Analysis

## Overview

This document describes the Vth derivative analysis feature that calculates dVth/dT (threshold voltage derivative with respect to temperature) for different Vds values and generates comprehensive visualizations.

## Quick Start

### Using Makefile (Recommended)

```bash
# Show all available commands
make help

# Run complete analysis (NMOS + PMOS)
make all

# Run analysis for specific device type
make nmos
make pmos

# Generate English version of all plots
make english

# Quick analysis (uses existing data if available)
make quick-all

# List generated files
make list

# Clean generated files
make clean
```

### Manual Commands

```bash
# Extract Vth data for all chips
python3 scripts/extract_vth.py chip3 --all-vd --out chip3_vth_all_vds.csv
python3 scripts/extract_vth.py chip4 --all-vd --out chip4_vth_all_vds.csv
python3 scripts/extract_vth.py chip5 --all-vd --out chip5_vth_all_vds.csv

# Combine data
head -1 chip3_vth_all_vds.csv > all_chips_vth_all_vds.csv
tail -n +2 chip3_vth_all_vds.csv >> all_chips_vth_all_vds.csv
tail -n +2 chip4_vth_all_vds.csv >> all_chips_vth_all_vds.csv
tail -n +2 chip5_vth_all_vds.csv >> all_chips_vth_all_vds.csv

# Run derivative analysis
python3 scripts/vth_derivative_vs_vds_temp.py . --device-type both --output-prefix my_analysis --skip-extraction
```

## Generated Files

For each analysis, the following files are generated:

### Data Files
- `*_data.csv`: Complete Vth data for all Vds values
- `*_derivative.csv`: Calculated dVth/dT values with columns:
  - `device`: nmos/pmos
  - `temperature`: temperature in K
  - `vds`: drain-source voltage in V
  - `vth`: threshold voltage in V
  - `dvth_dt`: derivative dVth/dT in V/K

### Visualization Files
- `*_3d.pdf`: 3D scatter plot showing dVth/dT vs temperature and Vds
- `*_heatmap.pdf`: 2D heatmap with color-coded dVth/dT values
- `*_contour.pdf`: Contour plot with temperature on X-axis, Vds on Y-axis

## Key Results

### NMOS Behavior
- **Range**: -0.000579 to 0.000192 V/K
- **General Trend**: Negative dVth/dT (Vth decreases with temperature)
- **Vds Dependence**: Becomes less negative (more positive) with higher Vds
- **Exceptions**: Some positive values at low Vds and low temperatures

### PMOS Behavior
- **Range**: 0.000143 to 0.000771 V/K
- **General Trend**: Always positive dVth/dT (Vth increases with temperature)
- **Vds Dependence**: Increases with higher Vds

### Data Filtering
- **NMOS**: Vds=0 excluded
- **PMOS**: Vds=1.2V excluded
- **Temperature Range**: 85K - 295K

## Algorithm Details

### Derivative Calculation
1. **Data Grouping**: Groups data by device type and Vds value
2. **Temperature Averaging**: Averages Vth values for duplicate temperatures
3. **Numerical Differentiation**: Uses `np.gradient()` to calculate dVth/dT
4. **Filtering**: Removes infinite and NaN values
5. **Validation**: Ensures at least 2 temperature points per device/Vds combination

### Visualization Features
- **3D Plots**: Interactive scatter plots with different colors for each device
- **Heatmaps**: Color-coded matrices with RdBu_r colormap
- **Contour Plots**: Level curves with black dots showing actual data points
- **Multi-language**: Support for Italian and English labels

## Interpretation

### Physical Meaning
- **Negative dVth/dT**: Vth decreases with temperature (typical for NMOS)
- **Positive dVth/dT**: Vth increases with temperature (typical for PMOS)
- **Vds Dependence**: Shows how temperature sensitivity varies with operating conditions

### Design Implications
- **Temperature Compensation**: Understanding dVth/dT helps design temperature-compensated circuits
- **Process Variation**: Different devices may show different temperature sensitivity
- **Operating Conditions**: Vds affects temperature sensitivity significantly

## Troubleshooting

### Common Issues
1. **No data found**: Ensure sufficient temperature points (at least 2) for each device/Vds
2. **Infinite values**: Check for duplicate temperature measurements
3. **Missing plots**: Verify matplotlib is installed and working
4. **Empty files**: Check that data extraction completed successfully

### Debug Commands
```bash
# Check data extraction
ls -la *_vth_all_vds.csv

# Check derivative calculation
head -10 *_derivative.csv

# Verify plot generation
ls -la *.pdf

# Clean and restart
make clean
make all
```

## Advanced Usage

### Custom Analysis
```bash
# Analyze specific Vds range
python3 scripts/vth_derivative_vs_vds_temp.py . --device-type nmos --output-prefix custom_nmos --skip-extraction

# Compare different chips
python3 scripts/extract_vth.py chip3 --all-vd --out chip3_only.csv
python3 scripts/vth_derivative_vs_vds_temp.py . --device-type both --output-prefix chip3_analysis --skip-extraction
```

### Data Analysis
```bash
# View derivative statistics
python3 -c "
import pandas as pd
df = pd.read_csv('all_chips_complete_derivative.csv')
print('NMOS statistics:')
print(df[df['device']=='nmos']['dvth_dt'].describe())
print('\nPMOS statistics:')
print(df[df['device']=='pmos']['dvth_dt'].describe())
"
```
