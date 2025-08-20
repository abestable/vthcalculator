# Makefile Guide - Vth Calculator

## Overview

This Makefile provides a comprehensive automation system for Vth analysis, including both basic Vth extraction and advanced derivative analysis. It consolidates all the functionality available in the `extract_vth.py` script and the derivative analysis features.

## Quick Start

```bash
# Show all available commands
make help

# Basic Vth extraction
make batch

# Derivative analysis
make derivative

# Interactive GUI
make gui
```

## Available Targets

### Basic Vth Extraction

#### `make gui`
Launches the interactive GUI for single file analysis.
- **Use case**: Inspect individual measurement files
- **Features**: Select Vd blocks, visualize Id/gm curves, see tangent and Vth
- **Output**: Interactive plots

#### `make batch`
Runs standard batch processing across all chips.
- **Use case**: Standard Vth extraction for all devices
- **Output files**:
  - `vth_all.csv`: Per-file results
  - `vth_summary.csv`: Summary by device
  - `vth_by_chip.csv`: Pivot by chip
  - `vth_nmos_vs_temp.png`: NMOS plots
  - `vth_pmos_vs_temp.png`: PMOS plots

#### `make batch-daniele`
Runs batch processing with comparison against Daniele's reference data.
- **Use case**: Compare results with reference measurements
- **Additional outputs**:
  - `vth_compare_clean.csv`: Comparison results
  - `vth_compare_clean_status.csv`: PASS/FAIL status

### Derivative Analysis

#### `make derivative`
Runs derivative analysis for all devices (NMOS + PMOS).
- **Use case**: Analyze dVth/dT vs temperature and Vds
- **Output files**:
  - `all_chips_complete_data.csv`: Complete Vth data
  - `all_chips_complete_derivative.csv`: Calculated derivatives
  - `all_chips_complete_3d.pdf`: 3D scatter plot
  - `all_chips_complete_heatmap.pdf`: 2D heatmap
  - `all_chips_complete_contour.pdf`: Contour plot

#### `make derivative-nmos`
Runs derivative analysis for NMOS only.
- **Output prefix**: `nmos_derivative`

#### `make derivative-pmos`
Runs derivative analysis for PMOS only.
- **Output prefix**: `pmos_derivative`

#### `make english`
Generates English version of all derivative plots.
- **Output prefix**: `*_english`

### Legacy Targets (Backward Compatibility)

#### `make all`
Same as `make derivative` (all devices).

#### `make nmos`
Same as `make derivative-nmos`.

#### `make pmos`
Same as `make derivative-pmos`.

### Utility Targets

#### `make quick-all`
Quick derivative analysis using existing data if available.
- **Use case**: Fast re-analysis without re-extracting data
- **Behavior**: Uses existing `all_chips_vth_all_vds.csv` if present

#### `make list`
Lists all generated files organized by category.
- **Output**: Shows basic Vth files and derivative analysis files

#### `make clean`
Removes all generated files.
- **Removes**: All CSV, PDF, and PNG files created by the analysis

#### `make clean-data`
Removes only data files, keeps plots.
- **Removes**: CSV files only
- **Keeps**: PDF and PNG visualization files

## Workflow Examples

### Complete Analysis Workflow

```bash
# 1. Start with basic Vth extraction
make batch

# 2. Run derivative analysis
make derivative

# 3. Generate English plots
make english

# 4. View results
make list
```

### Quick Iteration Workflow

```bash
# 1. First run (extracts data)
make derivative

# 2. Subsequent runs (uses existing data)
make quick-all

# 3. Clean and start over
make clean
make derivative
```

### Comparison Workflow

```bash
# 1. Run with Daniele comparison
make batch-daniele

# 2. Check comparison results
ls -la vth_compare_clean*.csv

# 3. Run derivative analysis
make derivative
```

## File Organization

### Basic Vth Files
- `vth_all.csv`: Raw per-file results
- `vth_summary.csv`: Aggregated by device
- `vth_by_chip.csv`: Pivot table by chip
- `vth_*.png`: Temperature plots

### Derivative Analysis Files
- `*_data.csv`: Complete Vth data for all Vds
- `*_derivative.csv`: Calculated dVth/dT values
- `*_3d.pdf`: 3D scatter plots
- `*_heatmap.pdf`: 2D heatmaps
- `*_contour.pdf`: Contour plots

### Comparison Files
- `vth_compare_clean.csv`: Comparison results
- `vth_compare_clean_status.csv`: PASS/FAIL status

## Troubleshooting

### Common Issues

#### "No .txt files found"
- **Cause**: No measurement files in the expected locations
- **Solution**: Ensure `chip3/`, `chip4/`, `chip5/` directories exist with measurement files

#### "ModuleNotFoundError: No module named 'pandas'"
- **Cause**: Missing Python dependencies
- **Solution**: Install required packages: `pip install pandas matplotlib numpy`

#### "No existing data found"
- **Cause**: Running `make quick-all` without previous data extraction
- **Solution**: Run `make derivative` first to extract data

#### GUI doesn't start
- **Cause**: Missing tkinter
- **Solution**: Install `python3-tk` package

### Debug Commands

```bash
# Check file structure
ls -la chip*/

# Check Python dependencies
python3 -c "import pandas, matplotlib, numpy; print('OK')"

# Check generated files
make list

# Clean and restart
make clean
make batch
```

## Advanced Usage

### Custom Analysis

```bash
# Manual extraction for specific chip
python3 scripts/extract_vth.py chip3 --all-vd --out chip3_only.csv

# Manual derivative analysis
python3 scripts/vth_derivative_vs_vds_temp.py . --device-type nmos --output-prefix custom --skip-extraction
```

### Data Analysis

```bash
# View derivative statistics
python3 -c "
import pandas as pd
df = pd.read_csv('all_chips_complete_derivative.csv')
print('NMOS dVth/dT range:', df[df['device']=='nmos']['dvth_dt'].min(), 'to', df[df['device']=='nmos']['dvth_dt'].max())
print('PMOS dVth/dT range:', df[df['device']=='pmos']['dvth_dt'].min(), 'to', df[df['device']=='pmos']['dvth_dt'].max())
"
```

## Performance Tips

1. **Use `make quick-all`** for iterative analysis
2. **Use `make clean-data`** to keep plots but remove large CSV files
3. **Use `make derivative-nmos`** or `make derivative-pmos`** for device-specific analysis
4. **Use `make list`** to check what files are generated

## Integration with Git

The Makefile is designed to work well with Git:
- Generated files are not tracked by Git (add to `.gitignore`)
- Use `make clean` before commits to remove temporary files
- The Makefile itself is tracked and versioned
