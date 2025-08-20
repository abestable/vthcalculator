
# Vth Calculator (Linear Extrapolation at Max gm)

Tooling to extract MOS threshold voltage (Vth) from measured Id–Vg sweeps and analyze its temperature and Vds dependence.

- **Method**: linear extrapolation at the point of extreme transconductance gm
  - NMOS: choose Vg at maximum gm, draw tangent to Id–Vg at that point, Vth is intercept with Id=0
  - PMOS: choose Vg at minimum gm (gm is negative), same tangent rule, Vth negative
- **Features**: 
  - Per-file visualization (GUI) and batch processing (CLI) across all chips/temperatures
  - **NEW**: Vth derivative analysis vs temperature and Vds with 3D plots, heatmaps, and contour plots
  - **NEW**: Automated analysis with Makefile

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
python3 scripts/extract_vth.py --gui
```
Notes:
- The GUI auto-selects the closest Vd to 0.1 V for NMOS and 1.1 V for PMOS.
- Hover the cursor over plots to read `(Vg, Id)` or `(Vg, gm)`.
- Close the window to free the shell.

### Automated Analysis (Recommended)
Use the Makefile for automated Vth analysis and derivative analysis:

```bash
# Show available commands
make help

# === BASIC VTH EXTRACTION ===
make gui          # Interactive GUI for single file analysis
make batch        # Standard batch processing (all chips, summary, plots)
make batch-daniele # Batch processing with Daniele comparison

# === DERIVATIVE ANALYSIS ===
make derivative   # Derivative analysis for all devices (NMOS + PMOS)
make derivative-nmos # Derivative analysis for NMOS only
make derivative-pmos # Derivative analysis for PMOS only
make english      # English version of all derivative plots

# === UTILITY ===
make quick-all    # Quick derivative analysis (uses existing data)
make list         # List all generated files
make clean        # Clean all generated files
```

## Batch Processing (CLI)

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
The new derivative analysis feature calculates dVth/dT (threshold voltage derivative with respect to temperature) for different Vds values and generates comprehensive visualizations.

### Features
- **3D Plots**: Interactive 3D visualization of dVth/dT vs temperature and Vds
- **Heatmaps**: Color-coded 2D representation showing sensitivity regions
- **Contour Plots**: Level curves for detailed analysis
- **Data Filtering**: Automatically excludes Vds=0 for NMOS and Vds=1.2V for PMOS
- **Multi-language**: Support for both Italian and English plot labels

### Generated Files
For each analysis, you get:
- `*_data.csv`: Complete Vth data for all Vds values
- `*_derivative.csv`: Calculated dVth/dT values
- `*_3d.pdf`: 3D scatter plot
- `*_heatmap.pdf`: 2D heatmap visualization
- `*_contour.pdf`: Contour plot with temperature on X-axis, Vds on Y-axis

### Key Results
- **NMOS**: Generally negative dVth/dT (Vth decreases with temperature)
- **PMOS**: Always positive dVth/dT (Vth increases with temperature)
- **Vds Dependence**: Sensitivity varies significantly with drain-source voltage

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
- Uses numerical differentiation with `np.gradient()`
- Groups data by device and Vds value
- Calculates dVth/dT for each temperature point
- Filters out infinite and NaN values
- Averages duplicate temperature measurements

## Tips / Troubleshooting

- If the GUI doesn’t start, ensure `python3-tk` is installed.
- If batch plots or summaries don’t appear, verify `pandas` and `matplotlib` are installed.
- Non-canonical files under `chip*` are ignored by git on purpose; the extractor still reads them if present locally.
- For derivative analysis, ensure you have sufficient temperature points (at least 2) for each device/Vds combination.
- Use `make clean` to remove all generated files if you need to start fresh.
- The Makefile automatically handles data extraction and analysis workflow.


