
# Vth calculator (linear extrapolation at max gm)

Tooling to extract MOS threshold voltage (Vth) from measured Id–Vg sweeps.

- Method: linear extrapolation at the point of extreme transconductance gm
  - NMOS: choose Vg at maximum gm, draw tangent to Id–Vg at that point, Vth is intercept with Id=0
  - PMOS: choose Vg at minimum gm (gm is negative), same tangent rule, Vth negative
- Supports per-file visualization (GUI) and batch processing (CLI) across all chips/temperatures.

## Requirements

- Python 3.8+
- Packages:
  - numpy
  - pandas (batch summary/comparison)
  - matplotlib (GUI plots and batch plots)
  - tkinter (GUI; usually preinstalled on Linux; on Ubuntu: `sudo apt-get install python3-tk`)

Install packages (user local):
```bash
python3 -m pip install --user numpy pandas matplotlib
```

## Dataset layout

The repo includes only canonical measurement files to keep it lean:
- Under `chip*/.../{Nmos,Pmos}/` only `1.txt`, `2.txt`, `3.txt`, `4.txt` and their `*.bmp` are tracked.
- The script accepts any folder hierarchy; it scans recursively.
- Each `.txt` must be tab-separated with header: `Index	Vg	Id	Time	Vd` and blocks of constant `Vd`.

## Quick start (GUI)

Launch interactive viewer to inspect a single file, select block Vd, and see Id/gm, tangent and Vth:
```bash
python3 scripts/extract_vth.py --gui
```
Notes:
- The GUI auto-selects the closest Vd to 0.1 V for NMOS and 1.1 V for PMOS.
- Hover the cursor over plots to read `(Vg, Id)` or `(Vg, gm)`.
- Close the window to free the shell.

## Batch processing (CLI)

Run over all chips/temperatures, extract Vth at low/high drain bias and produce CSVs and plots:
```bash
python3 scripts/extract_vth.py /path/to/root   --run_all   --vd 0.1   --out /path/to/root/vth_all.csv   --summary-out /path/to/root/vth_summary.csv   --plots-outdir /path/to/root
```
Outputs:
- `vth_all.csv`: one row per input file (and closest block to target Vd)
- `vth_summary.csv`: grouped by `temperature, device (nmos/pmos), device_index` with count/mean/std/min/max
- `vth_by_chip.csv`: pivot by chip per `(temperature, device_label)` with per-chip values and overall avg/std
- `vth_nmos_vs_temp.png`, `vth_pmos_vs_temp.png`: mean ± std vs temperature, one series per device index

### Comparison against a reference CSV (e.g., Daniele)

If you have a reference table with columns like `temperature, device, avg, stdev` (temperature in K, `device` such as `nmos1`, `pmos4`), pass it to produce comparison files automatically:
```bash
python3 scripts/extract_vth.py /path/to/root   --run_all   --out /path/to/root/vth_all.csv   --summary-out /path/to/root/vth_summary.csv   --plots-outdir /path/to/root   --daniele-csv /path/to/RisultatiDaniele.csv   --compare-threshold 0.01
```
Additional outputs:
- `vth_compare_clean.csv`: columns `temperature, device_label, abe_avg_V, abe_std_V, daniele_avg_V, daniele_std_V, delta_avg_V, delta_std_V`
- `vth_compare_clean_status.csv`: same plus `status` with PASS/FAIL if any absolute delta exceeds the threshold (default 0.01 V)

## Algorithm details

- Id units are parsed from `pA/nA/uA/mA/A`; Vg/Vd from `mV/V` and normalized to SI units.
- gm is computed numerically via `np.gradient(|Id|, Vg)` with a floor to avoid subthreshold noise.
- Selection of the tangent point:
  - NMOS: index of maximum gm
  - PMOS: index of minimum gm
- Tangent slope is `gm(Vg*)` and passes through `(Vg*, |Id|(Vg*))`; `Vth = Vg* − |Id|/gm` (sign applied: NMOS +, PMOS −).
- Target Vd for extraction: NMOS 0.1 V, PMOS 1.1 V (closest block is chosen per file).

## Tips / Troubleshooting

- If the GUI doesn’t start, ensure `python3-tk` is installed.
- If batch plots or summaries don’t appear, verify `pandas` and `matplotlib` are installed.
- Non-canonical files under `chip*` are ignored by git on purpose; the extractor still reads them if present locally.


