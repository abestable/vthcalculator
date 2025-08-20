
# Vth Calculator (Linear Extrapolation at Max gm)

Tooling to extract MOS threshold voltage (Vth) from measured Id–Vg sweeps and analyze its temperature and Vds dependence.

- **Method**: linear extrapolation at the point of extreme transconductance gm
  - NMOS: choose Vg at maximum gm, draw tangent to Id–Vg at that point, Vth is intercept with Id=0
  - PMOS: choose Vg at minimum gm (gm is negative), same tangent rule, Vth negative
- **Features**: 
  - Per-file visualization (GUI) and batch processing (CLI) across all chips/temperatures
  - **NEW**: Vth derivative analysis vs temperature and Vds with 3D plots, heatmaps, and contour plots
  - **NEW**: Automated analysis with comprehensive Makefile

## Table of Contents

- [Get the code](#get-the-code)
- [Requirements and installation](#requirements-and-installation)
- [Dataset layout](#dataset-layout)
- [Quick Start](#quick-start)
- [Makefile Guide](#makefile-guide)
- [Basic Vth Extraction](#basic-vth-extraction)
- [Vth Derivative Analysis](#vth-derivative-analysis)
- [Algorithm Details](#algorithm-details)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Get the code

```bash
git clone https://github.com/abestable/vthcalculator.git
cd vthcalculator
```

## Requirements and installation (venv recommended)

- Python 3.8+
- Create a virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
# Use numpy < 2 to avoid ABI issues with some distro matplotlib builds
pip install "numpy<2" pandas matplotlib
# For GUI on Debian/Ubuntu systems, if missing:
# sudo apt-get install -y python3-tk
```

## Dataset layout

The repo includes only canonical measurement files to keep it lean:
- Under `chip*/.../{Nmos,Pmos}/` only `1.txt`, `2.txt`, `3.txt`, `4.txt` and their `*.bmp` are tracked.
- The script accepts any folder hierarchy; it scans recursively.
- Each `.txt` must be tab-separated with header: `Index	Vg	Id	Time	Vd` and blocks of constant `Vd`.

## Quick Start

### GUI Mode
Launch interactive viewer to inspect a single file, select block Vd, and see Id/gm, tangent and Vth:
```bash
make gui
```
Notes:
- The GUI auto-selects the closest Vd to 0.1 V for NMOS and 1.1 V for PMOS.
- Hover the cursor over plots to read `(Vg, Id)` or `(Vg, gm)`.
- Close the window to free the shell.

### Automated Analysis (Recommended)
Use the Makefile for automated Vth analysis and derivative analysis:

```bash
# Show all available commands
make help

# === BASIC VTH EXTRACTION ===
make gui          # Interactive GUI for single file analysis
make batch        # Standard batch processing (all chips, summary, plots)
make batch-daniele # Batch processing with Daniele comparison

# === DERIVATIVE ANALYSIS ===
make derivative   # Derivative analysis for all devices (NMOS + PMOS)
make derivative-nmos # Derivative analysis for NMOS only
make derivative-pmos # Derivative analysis for PMOS only
make plots        # English version of all derivative plots

# === UTILITY ===
make quick-all    # Quick derivative analysis (uses existing data)
make list         # List all generated files
make clean        # Clean all generated files
```

## Makefile Guide

The Makefile provides comprehensive automation for all Vth analysis workflows.

### Available Targets

#### Basic Vth Extraction

**`make gui`**
- **Use case**: Inspect individual measurement files
- **Features**: Select Vd blocks, visualize Id/gm curves, see tangent and Vth
- **Output**: Interactive plots

**`make batch`**
- **Use case**: Standard Vth extraction for all devices
- **Output files**:
  - `vth_all.csv`: Per-file results
  - `vth_summary.csv`: Summary by device
  - `vth_by_chip.csv`: Pivot by chip
  - `vth_nmos_vs_temp.png`: NMOS plots
  - `vth_pmos_vs_temp.png`: PMOS plots

**`make batch-daniele`**
- **Use case**: Compare results with reference measurements
- **Additional outputs**:
  - `vth_compare_clean.csv`: Comparison results
  - `vth_compare_clean_status.csv`: PASS/FAIL status

#### Derivative Analysis

**`make derivative`**
- **Use case**: Analyze dVth/dT vs temperature and Vds
- **Output files**:
  - `all_chips_complete_data.csv`: Complete Vth data
  - `all_chips_complete_derivative.csv`: Calculated derivatives
  - `all_chips_complete_3d.pdf`: 3D scatter plot
  - `all_chips_complete_heatmap.pdf`: 2D heatmap
  - `all_chips_complete_contour.pdf`: Contour plot

**`make derivative-nmos`** / **`make derivative-pmos`**
- **Output prefix**: `nmos_derivative` / `pmos_derivative`

**`make plots`**
- **Output prefix**: `*_english`

#### Legacy Targets (Backward Compatibility)
- `make all` → `make derivative`
- `make nmos` → `make derivative-nmos`
- `make pmos` → `make derivative-pmos`

#### Utility Targets

**`make quick-all`**
- **Use case**: Fast re-analysis without re-extracting data
- **Behavior**: Uses existing `all_chips_vth_all_vds.csv` if present

**`make list`**
- **Output**: Shows basic Vth files and derivative analysis files

**`make clean`** / **`make clean-data`**
- **Removes**: All files / CSV files only
- **Keeps**: Nothing / PDF and PNG visualization files

### Workflow Examples

#### Complete Analysis Workflow
```bash
# 1. Start with basic Vth extraction
make batch

# 2. Run derivative analysis
make derivative

# 3. Generate English plots
make plots

# 4. View results
make list
```

#### Quick Iteration Workflow
```bash
# 1. First run (extracts data)
make derivative

# 2. Subsequent runs (uses existing data)
make quick-all

# 3. Clean and start over
make clean
make derivative
```

#### Comparison Workflow
```bash
# 1. Run with Daniele comparison
make batch-daniele

# 2. Check comparison results
ls -la vth_compare_clean*.csv

# 3. Run derivative analysis
make derivative
```

## Basic Vth Extraction

### Using Makefile (Recommended)
```bash
# Standard batch processing
make batch

# Batch processing with Daniele comparison
make batch-daniele
```

### Manual Commands
Run over all chips/temperatures, extract Vth at low/high drain bias and produce CSVs and plots (from repo root):
```bash
python3 scripts/extract_vth.py . \
  --run_all \
  --vd 0.1 \
  --out ./vth_all.csv \
  --summary-out ./vth_summary.csv \
  --plots-outdir .
```

**Outputs:**
- `vth_all.csv`: one row per input file (and closest block to target Vd)
- `vth_summary.csv`: grouped by `temperature, device (nmos/pmos), device_index` with count/mean/std/min/max
- `vth_by_chip.csv`: pivot by chip per `(temperature, device_label)` with per-chip values and overall avg/std
- `vth_nmos_vs_temp.png`, `vth_pmos_vs_temp.png`: mean ± std vs temperature, one series per device index

### Comparison against a reference CSV (e.g., Daniele)

If you have a reference table with columns like `temperature, device, avg, stdev` (temperature in K, `device` such as `nmos1`, `pmos4`), pass it to produce comparison files automatically:

**Using Makefile:**
```bash
make batch-daniele
```

**Manual command:**
```bash
python3 scripts/extract_vth.py . \
  --run_all \
  --out ./vth_all.csv \
  --summary-out ./vth_summary.csv \
  --plots-outdir . \
  --daniele-csv ./RisultatiDaniele.csv \
  --compare-threshold 0.01
```

**Additional outputs:**
- `vth_compare_clean.csv`: columns `temperature, device_label, abe_avg_V, abe_std_V, daniele_avg_V, daniele_std_V, delta_avg_V, delta_std_V`
- `vth_compare_clean_status.csv`: same plus `status` with PASS/FAIL if any absolute delta exceeds the threshold (default 0.01 V)

## Vth Derivative Analysis

### Overview
The derivative analysis feature calculates dVth/dT (threshold voltage derivative with respect to temperature) for different Vds values and generates comprehensive visualizations.

### Features
- **3D Plots**: Interactive 3D visualization of dVth/dT vs temperature and Vds
- **Heatmaps**: Color-coded 2D representation showing sensitivity regions
- **Contour Plots**: Level curves for detailed analysis
- **Data Filtering**: Automatically excludes Vds=0 for NMOS and Vds=1.2V for PMOS
- **Multi-language**: Support for both Italian and English plot labels

### Generated Files
For each analysis, you get:
- `*_data.csv`: Complete Vth data for all Vds values
- `*_derivative.csv`: Calculated dVth/dT values with columns:
  - `device`: nmos/pmos
  - `temperature`: temperature in K
  - `vds`: drain-source voltage in V
  - `vth`: threshold voltage in V
  - `dvth_dt`: derivative dVth/dT in V/K
- `*_3d.pdf`: 3D scatter plot
- `*_heatmap.pdf`: 2D heatmap visualization
- `*_contour.pdf`: Contour plot with temperature on X-axis, Vds on Y-axis

### Key Results

#### NMOS Behavior
- **Range**: -0.000579 to 0.000192 V/K
- **General Trend**: Negative dVth/dT (Vth decreases with temperature)
- **Vds Dependence**: Becomes less negative (more positive) with higher Vds
- **Exceptions**: Some positive values at low Vds and low temperatures

#### PMOS Behavior
- **Range**: 0.000143 to 0.000771 V/K
- **General Trend**: Always positive dVth/dT (Vth increases with temperature)
- **Vds Dependence**: Increases with higher Vds

#### Data Filtering
- **NMOS**: Vds=0 excluded
- **PMOS**: Vds=1.2V excluded
- **Temperature Range**: 85K - 295K

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

## Algorithm Details

### Vth Extraction
- Id units are parsed from `pA/nA/uA/mA/A`; Vg/Vd from `mV/V` and normalized to SI units.
- gm is computed numerically via `np.gradient(|Id|, Vg)` with a floor to avoid subthreshold noise.
- Selection of the tangent point:
  - NMOS: index of maximum gm
  - PMOS: index of minimum gm
- Tangent slope is `gm(Vg*)` and passes through `(Vg*, |Id|(Vg*))`; `Vth = Vg* − |Id|/gm` (sign applied: NMOS +, PMOS −).
- Target Vd for extraction: NMOS 0.1 V, PMOS 1.1 V (closest block is chosen per file).

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

#### "No data found" in derivative analysis
- **Cause**: Insufficient temperature points (at least 2) for each device/Vds
- **Solution**: Ensure sufficient temperature measurements

#### "Infinite values" in derivative calculation
- **Cause**: Duplicate temperature measurements
- **Solution**: Check for duplicate temperature points

### Debug Commands
```bash
# Check file structure
ls -la chip*/

# Check Python dependencies
python3 -c "import pandas, matplotlib, numpy; print('OK')"

# Check generated files
make list

# Check data extraction
ls -la *_vth_all_vds.csv

# Check derivative calculation
head -10 *_derivative.csv

# Verify plot generation
ls -la *.pdf

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
print('NMOS dVth/dT range:', df[df['device']=='nmos']['dvth_dt'].min(), 'to', df[df['device']=='nmos']['dvth_dt'].max())
print('PMOS dVth/dT range:', df[df['device']=='pmos']['dvth_dt'].min(), 'to', df[df['device']=='pmos']['dvth_dt'].max())
"

# View detailed statistics
python3 -c "
import pandas as pd
df = pd.read_csv('all_chips_complete_derivative.csv')
print('NMOS statistics:')
print(df[df['device']=='nmos']['dvth_dt'].describe())
print('\nPMOS statistics:')
print(df[df['device']=='pmos']['dvth_dt'].describe())
"
```

### Performance Tips
1. **Use `make quick-all`** for iterative analysis
2. **Use `make clean-data`** to keep plots but remove large CSV files
3. **Use `make derivative-nmos`** or `make derivative-pmos`** for device-specific analysis
4. **Use `make list`** to check what files are generated

### Integration with Git
The Makefile is designed to work well with Git:
- Generated files are not tracked by Git (add to `.gitignore`)
- Use `make clean` before commits to remove temporary files
- The Makefile itself is tracked and versioned

### Physical Interpretation

#### Physical Meaning
- **Negative dVth/dT**: Vth decreases with temperature (typical for NMOS)
- **Positive dVth/dT**: Vth increases with temperature (typical for PMOS)
- **Vds Dependence**: Shows how temperature sensitivity varies with operating conditions

#### Design Implications
- **Temperature Compensation**: Understanding dVth/dT helps design temperature-compensated circuits
- **Process Variation**: Different devices may show different temperature sensitivity
- **Operating Conditions**: Vds affects temperature sensitivity significantly


