#!/usr/bin/env python3
"""
Vth extraction using the linear extrapolation at maximum transconductance (gm).

For each measurement file (tab-separated with columns: Index, Vg, Id, Time, Vd),
the script:
  - parses values with mixed units (V/mV for Vg,Vd and pA/nA/uA for Id)
  - groups measurements by drain bias Vd
  - for a chosen Vd (default: 0.1 V), computes |Id| vs Vg (NMOS: Id>=0, PMOS: |Id|)
  - finds the point of maximum first derivative gm = d|Id|/dVg
  - performs a local linear fit around that point and returns the intercept at |Id|=0

Output: a CSV table with one row per file (and per Vd if --all-vd) reporting Vth.

Notes:
  - PMOS Vth is returned negative (i.e., -|Vth|), while NMOS is positive.
  - Blocks with Vd == 0 are skipped by default unless --include-vd0 is passed.
  - A small window around the gm maximum is used for stability (default: 7 points).
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import re
from dataclasses import dataclass
from glob import glob
from typing import Dict, List, Tuple, Optional

import numpy as np


VGD_RE = re.compile(r"^\s*([+-]?[0-9]*\.?[0-9]+)\s*(mV|V)\s*$", re.IGNORECASE)
ID_RE = re.compile(r"^\s*([+-]?[0-9]*\.?[0-9]+)\s*(pA|nA|uA|µA|mA|A)\s*$",
                   re.IGNORECASE)


def _to_volts(token: str) -> float:
    m = VGD_RE.match(token)
    if not m:
        raise ValueError(f"Cannot parse voltage token: '{token}'")
    value = float(m.group(1))
    unit = m.group(2).lower()
    if unit == "v":
        return value
    if unit == "mv":
        return value * 1e-3
    raise ValueError(f"Unsupported voltage unit in token: '{token}'")


def _to_amperes(token: str) -> float:
    m = ID_RE.match(token)
    if not m:
        raise ValueError(f"Cannot parse current token: '{token}'")
    value = float(m.group(1))
    unit = m.group(2).lower()
    if unit in ("a",):
        return value
    if unit in ("ma",):
        return value * 1e-3
    if unit in ("ua", "µa"):
        return value * 1e-6
    if unit in ("na",):
        return value * 1e-9
    if unit in ("pa",):
        return value * 1e-12
    raise ValueError(f"Unsupported current unit in token: '{token}'")


@dataclass
class SweepBlock:
    vd_volts: float
    vg_volts: np.ndarray  # shape (N,)
    id_amps: np.ndarray   # shape (N,)


def parse_measurement_file(path: str) -> List[SweepBlock]:
    """Parse a measurement .txt file into blocks grouped by constant Vd.

    Assumes tab-separated columns with header: Index, Vg, Id, Time, Vd
    and mixed units for Vg/Id/Vd.
    """
    blocks: Dict[float, List[Tuple[float, float]]] = {}
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline()
        # lenient check but helpful for early failure
        if "Vg" not in header or "Id" not in header or "Vd" not in header:
            raise ValueError(f"Unexpected header in {path!r}: {header!r}")
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) < 5:
                # sometimes spaces may be used; try splitting on whitespace
                parts = line.strip().split()
                if len(parts) < 5:
                    continue
            try:
                # parts indices: 0 Index, 1 Vg, 2 Id, 3 Time, 4 Vd
                vg = _to_volts(parts[1])
                id_a = _to_amperes(parts[2])
                vd = _to_volts(parts[4])
            except Exception:
                # be robust to garbled lines
                continue
            blocks.setdefault(vd, []).append((vg, id_a))

    sweep_blocks: List[SweepBlock] = []
    for vd, rows in blocks.items():
        rows_sorted = sorted(rows, key=lambda t: t[0])
        vg = np.array([t[0] for t in rows_sorted], dtype=float)
        id_a = np.array([t[1] for t in rows_sorted], dtype=float)
        sweep_blocks.append(SweepBlock(vd_volts=vd, vg_volts=vg, id_amps=id_a))
    # sort blocks by Vd ascending
    sweep_blocks.sort(key=lambda b: b.vd_volts)
    return sweep_blocks


def compute_vth_linear_extrapolation(vg: np.ndarray,
                                     id_a: np.ndarray,
                                     device_type: str,
                                     window: int = 7,
                                     criterion: str = "max-gm") -> Tuple[float, float, int]:
    """Compute threshold voltage via linear extrapolation at maximum gm.

    Returns (vth_signed, gm_max, idx_gm_max).

    device_type: 'nmos' or 'pmos'. For PMOS we use |Id| for gm/vth and return
    a negative Vth value.
    """
    if vg.ndim != 1 or id_a.ndim != 1 or vg.size != id_a.size:
        raise ValueError("vg and id_a must be 1D arrays of equal length")

    # For PMOS, flip the Vg axis (0 becomes 1.2, 1.2 becomes 0, etc.)
    if device_type.lower() == "pmos":
        vg_flipped = 1.2 - vg  # Flip Vg axis around 1.2V
        y = np.abs(id_a)
        sign = 1.0  # PMOS threshold should be positive
    else:
        vg_flipped = vg
        # clip tiny negative currents caused by instrument offsets
        y = np.maximum(id_a, 0.0)
        sign = 1.0

    # numerical derivative gm = dy/dvg (using flipped Vg for PMOS)
    gm = np.gradient(y, vg_flipped, edge_order=1)
    # optional: derivative of gm (second derivative of |Id|)
    dgm = np.gradient(gm, vg_flipped, edge_order=1)

    # focus on region where current is above a tiny floor to avoid noise
    current_floor = max(1e-10, 0.001 * np.nanmax(y))  # at least 100 pA or 0.1% of max
    valid = y >= current_floor
    if np.count_nonzero(valid) < max(5, window):
        # not enough valid points; fall back to global
        valid = np.ones_like(y, dtype=bool)

    # find index based on criterion
    if criterion == "max-gm":
        if device_type.lower() == "pmos":
            # For PMOS with flipped Vg, we now look for maximum gm (not minimum)
            gm_masked = np.where(valid, gm, -np.inf)
            idx = int(np.nanargmax(gm_masked))
        else:
            gm_masked = np.where(valid, gm, -np.inf)
            idx = int(np.nanargmax(gm_masked))
    elif criterion == "max-dgm":
        dgm_masked = np.where(valid, dgm, -np.inf)
        idx = int(np.nanargmax(dgm_masked))
    else:
        raise ValueError(f"Unknown criterion: {criterion}")

    # local linear fit around idx to approximate tangent
    # Build true tangent at the selected point: slope = gm[idx],
    # and line passes through (vg_flipped[idx], y[idx]). This guarantees
    # alignment between displayed tangent slope and gm value.
    slope = gm[idx]
    intercept = y[idx] - slope * vg_flipped[idx]
    if abs(slope) < 1e-15:
        return math.nan, float(np.nanmax(gm)), idx

    vth_mag = -intercept / slope
    # For PMOS, the threshold is already correct from the flipped Vg calculation
    if device_type.lower() == "pmos":
        vth_signed = -1.0 * float(vth_mag)  # PMOS threshold should be negative
    else:
        vth_signed = sign * float(vth_mag)
    gm_max = float(np.nanmax(gm)) if criterion == "max-gm" else float(gm[idx])
    return vth_signed, gm_max, idx


def compute_vth_sqrt_method(vg: np.ndarray,
                           id_a: np.ndarray,
                           device_type: str,
                           window: int = 7,
                           criterion: str = "max-gm") -> Tuple[float, float, int]:
    """Compute threshold voltage using square root of current method.
    
    This method uses √Id instead of Id directly, which is more appropriate
    for higher Vds values where the transistor operates in saturation.
    For saturation region: Id ∝ (Vgs - Vth)², therefore √Id ∝ (Vgs - Vth)
    
    Returns (vth_signed, gm_max, idx_gm_max).
    
    device_type: 'nmos' or 'pmos'. For PMOS we use |Id| for gm/vth and return
    a negative Vth value.
    """
    if vg.ndim != 1 or id_a.ndim != 1 or vg.size != id_a.size:
        raise ValueError("vg and id_a must be 1D arrays of equal length")

    if device_type.lower() == "pmos":
        vd = 0.0  # Set vd to 0 for pmos
    else:
        vd = 1.2  # Set vd to 1.2 for nmos
    # For PMOS, flip the Vg axis (0 becomes 1.2, 1.2 becomes 0, etc.)
    if device_type.lower() == "pmos":
        vg_flipped = 1.2 - vg  # Flip Vg axis around 1.2V
        y = np.abs(id_a)
        sign = 1.0  # PMOS threshold should be positive
    else:
        vg_flipped = vg
        # clip tiny negative currents caused by instrument offsets
        y = np.maximum(id_a, 0.0)
        sign = 1.0

    # Apply square root to current: √Id
    y_sqrt = np.sqrt(y)
    
    # numerical derivative gm = d(√Id)/dvg (using flipped Vg for PMOS)
    gm = np.gradient(y_sqrt, vg_flipped, edge_order=1)
    # optional: derivative of gm (second derivative of √Id)
    dgm = np.gradient(gm, vg_flipped, edge_order=1)

    # focus on region where current is above a tiny floor to avoid noise
    current_floor = max(1e-10, 0.001 * np.nanmax(y))  # at least 100 pA or 0.1% of max
    valid = y >= current_floor
    if np.count_nonzero(valid) < max(5, window):
        # not enough valid points; fall back to global
        valid = np.ones_like(y, dtype=bool)

    # find index based on criterion
    if criterion == "max-gm":
        if device_type.lower() == "pmos":
            # For PMOS with flipped Vg, we now look for maximum gm (not minimum)
            gm_masked = np.where(valid, gm, -np.inf)
            idx = int(np.nanargmax(gm_masked))
        else:
            gm_masked = np.where(valid, gm, -np.inf)
            idx = int(np.nanargmax(gm_masked))
    elif criterion == "max-dgm":
        dgm_masked = np.where(valid, dgm, -np.inf)
        idx = int(np.nanargmax(dgm_masked))
    else:
        raise ValueError(f"Unknown criterion: {criterion}")

    # local linear fit around idx to approximate tangent
    # Build true tangent at the selected point: slope = gm[idx],
    # and line passes through (vg_flipped[idx], y_sqrt[idx]). This guarantees
    # alignment between displayed tangent slope and gm value.
    slope = gm[idx]
    intercept = y_sqrt[idx] - slope * vg_flipped[idx]
    if abs(slope) < 1e-15:
        return math.nan, float(np.nanmax(gm)), idx

    vth_mag = -intercept / slope
    # For PMOS, the threshold is already correct from the flipped Vg calculation
    if device_type.lower() == "pmos":
        vth_signed = -1.0 * float(vth_mag)  # PMOS threshold should be negative
    else:
        vth_signed = sign * float(vth_mag)
    gm_max = float(np.nanmax(gm)) if criterion == "max-gm" else float(gm[idx])
    return vth_signed, gm_max, idx


def infer_device_type_from_path(path: str) -> str:
    lower = path.lower()
    if os.sep + "pmos" + os.sep in lower:
        return "pmos"
    if os.sep + "nmos" + os.sep in lower:
        return "nmos"
    # default to NMOS if unknown
    return "nmos"


def infer_device_index_from_path(path: str) -> Optional[int]:
    base = os.path.basename(path)
    m = re.match(r"(\d+)\.txt$", base)
    if m:
        return int(m.group(1))
    return None


def extract_temperature_from_path(path: str) -> str:
    m = re.search(r"([^/\\]+)K", path)
    return m.group(0) if m else ""


def run_batch(root: str, vd: float, include_vd0: bool, window: int,
              results_csv: str, summary_csv: str, plots_outdir: str,
              pivot_csv: Optional[str] = None,
              daniele_csv: Optional[str] = None,
              compare_out: Optional[str] = None,
              compare_status_out: Optional[str] = None,
              compare_threshold: float = 0.01,
              methods: List[str] = ["traditional"]) -> None:
    pattern = os.path.join(root, "**", "*.txt")
    files = sorted(glob(pattern, recursive=True))
    files = [p for p in files if os.path.basename(p).lower() in {"1.txt", "2.txt", "3.txt", "4.txt"}]
    files = [p for p in files if (os.sep + "nmos" + os.sep).lower() in p.lower() or (os.sep + "pmos" + os.sep).lower() in p.lower()]
    os.makedirs(os.path.dirname(os.path.abspath(results_csv)) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(summary_csv)) or ".", exist_ok=True)
    os.makedirs(plots_outdir or ".", exist_ok=True)

    # Per-file extraction
    rows: List[List[str]] = []
    for path in files:
        try:
            blocks = parse_measurement_file(path)
        except Exception as e:
            rows.append([path, extract_temperature_from_path(path), infer_device_type_from_path(path), "", "", "", "", "", 0, f"parse_error: {e}"])
            continue
        device = infer_device_type_from_path(path)
        block_list: List[SweepBlock]
        candidates = [b for b in blocks if include_vd0 or abs(b.vd_volts) > 1e-12]
        if not candidates:
            rows.append([path, extract_temperature_from_path(path), device, "", "", "", "", "", 0, "no_valid_blocks"])
            continue
        # Calculate Vth for each requested method
        for method in methods:
            # Select the appropriate Vd block for each method
            if method.lower() == "sqrt":
                if device == "nmos":
                    # For NMOS sqrt, find block closest to 1.1V (symmetric with PMOS)
                    closest = min(candidates, key=lambda b: abs(b.vd_volts - 1.1))
                else:
                    # For PMOS sqrt, find block with Vd closest to 0.0V
                    closest = min(candidates, key=lambda b: abs(b.vd_volts - 0.0))
            else:
                vd_target = 0.1 if device == "nmos" else 1.1
                closest = min(candidates, key=lambda b: abs(b.vd_volts - vd_target))
            try:
                if method.lower() == "traditional":
                    vth, gm_max, idx = compute_vth_linear_extrapolation(
                        closest.vg_volts, closest.id_amps, device_type=device, window=window
                    )
                elif method.lower() == "sqrt":
                    vth, gm_max, idx = compute_vth_sqrt_method(
                        closest.vg_volts, closest.id_amps, device_type=device, window=window
                    )
                else:
                    raise ValueError(f"Unknown method: {method}")
                notes = ""
            except Exception as e:
                vth, gm_max, idx = math.nan, math.nan, -1
                notes = f"compute_error: {e}"
            
            # Use the actual Vd from the selected block
            vd_display = closest.vd_volts
            
            rows.append([
                path, extract_temperature_from_path(path), device, method, f"{vd_display:.6g}",
                ("" if math.isnan(vth) else f"{vth:.6g}"),
                ("" if math.isnan(gm_max) else f"{gm_max:.6g}"), idx,
                closest.vg_volts.size, notes,
            ])

    with open(results_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file_path", "temperature", "device", "method", "vd_V", "vth_V", "gm_max_A_per_V", "gm_max_index", "num_points", "notes"])
        w.writerows(rows)

    # Build summary by temperature, device, device_index across chips
    try:
        import pandas as pd
        df = pd.DataFrame(rows, columns=["file_path", "temperature", "device", "method", "vd_V", "vth_V", "gm_max_A_per_V", "gm_max_index", "num_points", "notes"])
        df = df[df["vth_V"] != ""].copy()
        df["vth_V"] = df["vth_V"].astype(float)
        df["device_index"] = df["file_path"].str.extract(r"/(\d+)\.txt$|\\(\d+)\.txt$", expand=True).fillna("").sum(axis=1)
        df["device_index"] = pd.to_numeric(df["device_index"], errors="coerce").astype("Int64")
        grp = (df.groupby(["temperature", "device", "method", "device_index"], dropna=False)
                 .agg(count=("vth_V", "size"),
                      mean_vth_V=("vth_V", "mean"),
                      std_vth_V=("vth_V", "std"),
                      min_vth_V=("vth_V", "min"),
                      max_vth_V=("vth_V", "max"))
                 .reset_index())
        grp.to_csv(summary_csv, index=False)

        # Build pivot by chip: columns per chip, rows per (temperature, device_label)
        df["chip"] = df["file_path"].str.extract(r"[\\/](chip\d+)[\\/]")
        df["device_index"] = df["device_index"].astype("Int64")
        df["device_label"] = df.apply(lambda r: (str(r["device"]) + ("" if pd.isna(r["device_index"]) else str(int(r["device_index"])))), axis=1)
        chip_mean = (df.groupby(["temperature", "device_label", "method", "chip"], dropna=False)
                       .agg(vth_V=("vth_V", "mean"))
                       .reset_index())
        pivot = chip_mean.pivot_table(index=["temperature", "device_label", "method"], columns="chip", values="vth_V", aggfunc="mean")
        # compute row-wise avg/std ignoring NaN
        pivot["avg_vth_V"] = pivot.mean(axis=1, skipna=True)
        pivot["std_vth_V"] = pivot.std(axis=1, ddof=1, skipna=True)
        pivot = pivot.reset_index()
        # helper used for sorting temperatures and device labels
        def k_to_num(s: str) -> float:
            try:
                return float(re.sub(r"K$", "", s))
            except Exception:
                return float("nan")
        # custom ordering: nmos1..nmosN, then pmos1..pmosN, each increasing T
        def dev_order(lbl: str) -> int:
            m = re.match(r"(nmos|pmos)(\d+)$", lbl or "")
            if not m:
                return 10_000
            base = 0 if m.group(1) == "nmos" else 1_000
            return base + int(m.group(2))
        pivot["T_K"] = pivot["temperature"].map(k_to_num)
        pivot["device_order"] = pivot["device_label"].map(dev_order)
        pivot = pivot.sort_values(["device_order", "T_K", "device_label", "method"])  # stable order
        pivot = pivot.drop(columns=["T_K", "device_order"])
        if pivot_csv:
            pivot.to_csv(pivot_csv, index=False)

        # Optional comparison with Daniele CSV
        if daniele_csv and os.path.exists(daniele_csv):
            try:
                ref = pd.read_csv(daniele_csv)
                ref = ref.rename(columns={
                    'avg': 'daniele_avg_V', 'stdev': 'daniele_std_V', 'device': 'device_label'
                })
                ref['device_label'] = ref['device_label'].astype(str).str.lower().str.strip()
                ref['temperature'] = ref['temperature'].astype(str).str.replace('K','', regex=False).astype(float)

                ours = grp.copy()
                # build device_label
                ours['device_label'] = ours.apply(lambda r: f"{r['device']}{'' if pd.isna(r['device_index']) else int(r['device_index'])}", axis=1)
                ours['temperature'] = ours['temperature'].astype(str).str.replace('K','', regex=False).astype(float)
                ours = ours.rename(columns={'mean_vth_V':'abe_avg_V','std_vth_V':'abe_std_V'})
                ours_red = ours[['temperature','device_label','abe_avg_V','abe_std_V']]

                cmp_df = ours_red.merge(ref[['temperature','device_label','daniele_avg_V','daniele_std_V']],
                                         on=['temperature','device_label'], how='outer')
                cmp_df['delta_avg_V'] = cmp_df['abe_avg_V'] - cmp_df['daniele_avg_V']
                cmp_df['delta_std_V'] = cmp_df['abe_std_V'] - cmp_df['daniele_std_V']
                if compare_out:
                    cmp_df.sort_values(['device_label','temperature']).to_csv(compare_out, index=False)
                if compare_status_out:
                    cmp_df['status'] = cmp_df.apply(
                        lambda r: 'FAIL' if (abs(r.get('delta_avg_V', 0)) > compare_threshold or abs(r.get('delta_std_V', 0)) > compare_threshold) else 'PASS',
                        axis=1
                    )
                    cmp_df.sort_values(['device_label','temperature']).to_csv(compare_status_out, index=False)
            except Exception:
                pass

        # Plots: error bars per device_index for NMOS and PMOS
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        def k_to_num(s: str) -> float:
            try:
                return float(re.sub(r"K$", "", s))
            except Exception:
                return float("nan")

        # Create separate plots for each method and device type
        for method in methods:
            for dtype, fname_base in (("nmos", "vth_nmos_vs_temp"), ("pmos", "vth_pmos_vs_temp")):
                d = grp[(grp["device"] == dtype) & (grp["method"] == method)].copy()
                if d.empty:
                    continue
                d["T_K"] = d["temperature"].map(k_to_num)
                
                # Create filename with method suffix
                fname = os.path.join(plots_outdir, f"{fname_base}_{method}.pdf")
                
                plt.figure(figsize=(7.5, 5.0), dpi=120)
                import math as _math
                for dev_idx, sub in d.groupby("device_index"):
                    sub = sub.sort_values("T_K")
                    # Legend label as NMOS1/PMOS1 etc.
                    try:
                        idx_int = int(dev_idx) if dev_idx is not None and not (hasattr(dev_idx, 'isna') and dev_idx.isna()) else None
                    except Exception:
                        idx_int = None
                    label = f"{dtype.upper()}{idx_int if idx_int is not None else ''}"
                    plt.errorbar(sub["T_K"].values, sub["mean_vth_V"].values, yerr=sub["std_vth_V"].fillna(0.0).values,
                                 marker="o", capsize=3, label=label)
                plt.xlabel("Temperature (K)")
                plt.ylabel("Vth (V)")
                plt.title(f"Vth vs T — {dtype.upper()} ({method.capitalize()} method, mean ± std across chips)")
                plt.legend(loc="best", ncol=2, fontsize=8)
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(fname)
                plt.close()
    except Exception as e:
        # Pandas/matplotlib might be missing; print error for debug
        try:
            import traceback
            print("Batch summary/plots error:")
            traceback.print_exc()
        except Exception:
            print(f"Batch summary/plots error: {e}")

    print(f"Wrote per-file CSV: {results_csv}")
    if os.path.exists(summary_csv):
        print(f"Wrote summary CSV: {summary_csv}")
    if plots_outdir and os.path.exists(os.path.join(plots_outdir, "vth_nmos_vs_temp.pdf")):
        print(f"Wrote plots in: {plots_outdir}")
    if 'pivot_csv' in locals() and pivot_csv and os.path.exists(pivot_csv):
        print(f"Wrote pivot CSV: {pivot_csv}")
    if compare_out and os.path.exists(compare_out):
        print(f"Wrote compare CSV: {compare_out}")
    if compare_status_out and os.path.exists(compare_status_out):
        print(f"Wrote compare-status CSV: {compare_status_out}")

def find_blocks_for_vd(blocks: List[SweepBlock], desired_vd: float,
                       include_vd0: bool) -> List[SweepBlock]:
    # Skip Vd == 0 unless explicitly requested
    candidates = [b for b in blocks if include_vd0 or abs(b.vd_volts) > 1e-12]
    if not candidates:
        return []
    # Find the block with Vd closest to desired_vd
    closest = min(candidates, key=lambda b: abs(b.vd_volts - desired_vd))
    return [closest]


def compute_gm_and_tangent(vg: np.ndarray,
                           id_a: np.ndarray,
                           device_type: str,
                           window: int = 7,
                           criterion: str = "max-gm") -> Tuple[np.ndarray, np.ndarray, np.ndarray, int, float, float, float]:
    """Return (|Id| array y, gm array, dgm array, idx, slope, intercept, vth_signed).

    Uses the same definition as compute_vth_linear_extrapolation.
    """
    # For PMOS, flip the Vg axis (0 becomes 1.2, 1.2 becomes 0, etc.)
    if device_type.lower() == "pmos":
        vg_flipped = 1.2 - vg  # Flip Vg axis around 1.2V
        y = np.abs(id_a)
        sign = 1.0  # PMOS threshold should be positive
    else:
        vg_flipped = vg
        y = np.maximum(id_a, 0.0)
        sign = 1.0

    gm = np.gradient(y, vg_flipped, edge_order=1)
    dgm = np.gradient(gm, vg_flipped, edge_order=1)
    current_floor = max(1e-10, 0.001 * np.nanmax(y))
    valid = y >= current_floor
    if np.count_nonzero(valid) < max(5, window):
        valid = np.ones_like(y, dtype=bool)

    if criterion == "max-gm":
        metric = gm
    elif criterion == "max-dgm":
        metric = dgm
    else:
        raise ValueError(f"Unknown criterion: {criterion}")
    if criterion == "max-gm" and device_type.lower() == "pmos":
        # For PMOS with flipped Vg, we now look for maximum gm (not minimum)
        metric_masked = np.where(valid, metric, -np.inf)
        idx = int(np.nanargmax(metric_masked))
    else:
        metric_masked = np.where(valid, metric, -np.inf)
        idx = int(np.nanargmax(metric_masked))

    # Tangent exactly at selected point (using flipped Vg for PMOS)
    slope = gm[idx]
    intercept = y[idx] - slope * vg_flipped[idx]
    vth_mag = -intercept / slope if abs(slope) > 1e-15 else math.nan
    # For PMOS, the threshold is already correct from the flipped Vg calculation
    if device_type.lower() == "pmos" and not math.isnan(vth_mag):
        vth_signed = -1.0 * float(vth_mag)  # PMOS threshold should be negative
    else:
        vth_signed = sign * float(vth_mag) if not math.isnan(vth_mag) else math.nan
    return y, gm, dgm, idx, float(slope), float(intercept), vth_signed


def run_gui() -> None:
    try:
        import tkinter as tk
        from tkinter import filedialog, ttk, messagebox
        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    except Exception as e:
        print("GUI dependencies missing (tkinter/matplotlib). Install and retry. Error:", e)
        return

    root = tk.Tk()
    root.title("Vth extractor — linear extrapolation at max gm")

    file_path_var = tk.StringVar(value="")
    device_var = tk.StringVar(value="")
    method_var = tk.StringVar(value="Traditional")
    vd_values: List[float] = []
    blocks_by_vd: Dict[float, SweepBlock] = {}

    frame_top = ttk.Frame(root)
    frame_top.pack(fill=tk.X, padx=8, pady=8)

    ttk.Label(frame_top, text="File:").pack(side=tk.LEFT)
    entry = ttk.Entry(frame_top, textvariable=file_path_var, width=80)
    entry.pack(side=tk.LEFT, padx=4)

    def on_browse():
        path = filedialog.askopenfilename(title="Select measurement file",
                                          filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        file_path_var.set(path)
        try:
            blocks = parse_measurement_file(path)
        except Exception as ex:
            tk.messagebox.showerror("Parse error", f"Failed to parse file:\n{ex}")
            return
        nonlocal blocks_by_vd, vd_values
        blocks_by_vd = {round(b.vd_volts, 6): b for b in blocks}
        vd_values = sorted(blocks_by_vd.keys())
        vd_combo["values"] = vd_values
        if vd_values:
            # default: select Vd closest to 0.1 V (valid for NMOS and PMOS datasets)
            target_vd = 0.1
            closest_vd = min(vd_values, key=lambda v: abs(v - target_vd))
            vd_combo.current(vd_values.index(closest_vd))
        dtype = infer_device_type_from_path(path)
        device_var.set(dtype)
        # default Vd selection per device: NMOS ~0.1 V, PMOS ~1.1 V
        if vd_values:
            target_vd = 0.1 if dtype == "nmos" else 1.1
            closest_vd = min(vd_values, key=lambda v: abs(v - target_vd))
            vd_combo.current(vd_values.index(closest_vd))
        update_plot()

    browse_btn = ttk.Button(frame_top, text="Browse…", command=on_browse)
    browse_btn.pack(side=tk.LEFT, padx=4)

    ttk.Label(frame_top, text="Device:").pack(side=tk.LEFT, padx=(12, 2))
    dev_entry = ttk.Entry(frame_top, textvariable=device_var, width=8)
    dev_entry.pack(side=tk.LEFT)

    ttk.Label(frame_top, text="Vd block:").pack(side=tk.LEFT, padx=(12, 2))
    vd_combo = ttk.Combobox(frame_top, state="readonly", width=10)
    vd_combo.pack(side=tk.LEFT)
    
    ttk.Label(frame_top, text="Method:").pack(side=tk.LEFT, padx=(12, 2))
    method_combo = ttk.Combobox(frame_top, textvariable=method_var, state="readonly", width=12)
    method_combo["values"] = ("Traditional", "Sqrt", "Hybrid")
    method_combo.pack(side=tk.LEFT)

    frame_fig = ttk.Frame(root)
    frame_fig.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(7.5, 7.5), dpi=100, sharex=True)
    plt.tight_layout(pad=1.5)
    canvas = FigureCanvasTkAgg(fig, master=frame_fig)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)

    status_var = tk.StringVar(value="")
    status = ttk.Label(root, textvariable=status_var, anchor="w")
    status.pack(fill=tk.X, padx=8, pady=(0, 8))

    # Graceful close to free the shell when the window is closed
    def on_close():
        try:
            plt.close('all')
        except Exception:
            pass
        try:
            root.quit()
            root.destroy()
        except Exception:
            pass
    root.protocol("WM_DELETE_WINDOW", on_close)

    # GUI is now for single-file inspection only (no batch controls)

    # Hover annotations (created on first plot)
    annot0 = None
    annot1 = None

    def on_move(event):
        # Update tooltip text near cursor with x,y in meaningful units
        if event.inaxes is ax0 and annot0 is not None:
            if event.xdata is None or event.ydata is None:
                return
            annot0.xy = (event.xdata, event.ydata)
            annot0.set_text(f"Vg={event.xdata:.4g} V\nId={event.ydata:.4g} A")
            annot0.set_visible(True)
            if annot1 is not None:
                annot1.set_visible(False)
            canvas.draw_idle()
        elif event.inaxes is ax1 and annot1 is not None:
            if event.xdata is None or event.ydata is None:
                return
            annot1.xy = (event.xdata, event.ydata)
            annot1.set_text(f"Vg={event.xdata:.4g} V\ngm={event.ydata:.4g} A/V")
            annot1.set_visible(True)
            if annot0 is not None:
                annot0.set_visible(False)
            canvas.draw_idle()
        else:
            # Hide when out of axes
            if annot0 is not None:
                annot0.set_visible(False)
            if annot1 is not None:
                annot1.set_visible(False)
            canvas.draw_idle()

    cid_motion = fig.canvas.mpl_connect('motion_notify_event', on_move)

    def compute_vth_with_method(vg, id_a, device_type, method, window=7, criterion="max-gm"):
        """Compute Vth using the selected method."""
        if method == "Traditional":
            return compute_vth_linear_extrapolation(vg, id_a, device_type, window, criterion)
        elif method == "Sqrt":
            return compute_vth_sqrt_method(vg, id_a, device_type, window, criterion)
        elif method == "Hybrid":
            # For hybrid, we need to determine Vds from the current block
            # This will be handled in update_plot
            return compute_vth_linear_extrapolation(vg, id_a, device_type, window, criterion)
        else:
            raise ValueError(f"Unknown method: {method}")

    def update_plot(*_args):
        ax0.clear()
        ax1.clear()
        path = file_path_var.get().strip()
        if not path or not os.path.isfile(path):
            status_var.set("Select a valid file…")
            canvas.draw()
            return
        if not vd_combo.get():
            status_var.set("Select a Vd block…")
            canvas.draw()
            return
        try:
            vd_selected = float(vd_combo.get())
        except Exception:
            status_var.set("Invalid Vd selected…")
            canvas.draw()
            return
        block = blocks_by_vd.get(round(vd_selected, 6))
        if block is None:
            status_var.set("Vd block not found in file…")
            canvas.draw()
            return

        device = (device_var.get() or infer_device_type_from_path(path)).lower()
        method = method_var.get()
        
        # Handle hybrid method
        if method == "Hybrid":
            vds_threshold = 0.5
            if abs(block.vd_volts) < vds_threshold:
                method = "Traditional"
            else:
                method = "Sqrt"
        
        # Compute Vth using selected method
        if method == "Traditional":
            y, gm, dgm, idx, slope, intercept, vth = compute_gm_and_tangent(
                block.vg_volts, block.id_amps, device_type=device, window=7,
                criterion="max-gm"
            )
        elif method == "Sqrt":
            # Use the same function as batch processing for consistency
            vth, gm_max, idx = compute_vth_sqrt_method(
                block.vg_volts, block.id_amps, device_type=device, window=7,
                criterion="max-gm"
            )
            # For GUI display, we need to compute gm and other values
            if device == "pmos":
                vg_flipped = 1.2 - block.vg_volts
                y = np.abs(block.id_amps)
            else:
                vg_flipped = block.vg_volts
                y = np.maximum(block.id_amps, 0.0)
            
            # Apply square root
            y_sqrt = np.sqrt(y)
            gm = np.gradient(y_sqrt, vg_flipped, edge_order=1)
            dgm = np.gradient(gm, vg_flipped, edge_order=1)
            
            # Compute slope and intercept for tangent line
            slope = gm[idx]
            intercept = y_sqrt[idx] - slope * vg_flipped[idx]
        else:
            raise ValueError(f"Unknown method: {method}")

        # For PMOS, use flipped Vg axis for display (more intuitive)
        if device == "pmos":
            vg_display = 1.2 - block.vg_volts  # Flip Vg axis for display
        else:
            vg_display = block.vg_volts

        # Plot i_D (blue) in amperes and tangent (black) on first axis
        if method == "Sqrt":
            # For sqrt method, plot √Id
            if device == "pmos":
                y_plot = np.sqrt(np.abs(block.id_amps))
            else:
                y_plot = np.sqrt(np.maximum(block.id_amps, 0.0))
            ax0.plot(vg_display, y_plot, color="blue", label="√i_D (√A)")
        else:
            # For traditional method, plot Id
            ax0.plot(vg_display, y, color="blue", label="i_D (A)")
        
        y_tan = slope * vg_display + intercept
        ax0.plot(vg_display, y_tan, color="black", linewidth=2.0, label="tangent")
        if not math.isnan(vth):
            vth_display = abs(vth)
            if device == "pmos":
                # For PMOS, flip Vth for display since we flipped the Vg axis
                vth_display = 1.2 - vth_display  # Flip Vth for display
            ax0.axvline(vth_display, color="k", linestyle=":")
            ax0.annotate("Vth", xy=(vth_display, 0), xytext=(vth_display, 0),
                         textcoords="data", ha="center")
        if method == "Sqrt":
            ax0.set_ylabel("√i_D (√A)")
            ax0.set_title(f"√IV — {os.path.basename(path)} @ Vd={block.vd_volts:.3g} V ({method})")
        else:
            ax0.set_ylabel("i_D (A)")
            ax0.set_title(f"IV — {os.path.basename(path)} @ Vd={block.vd_volts:.3g} V ({method})")
        ax0.legend(loc="best")

        # Plot gm (red) on second axis with its own scale; mark max
        if method == "Sqrt":
            ax1.plot(vg_display, gm, color="red", label="gm = d√|Id|/dVg (√A/V)")
        else:
            ax1.plot(vg_display, gm, color="red", label="gm = d|Id|/dVg (A/V)")
        ax1.plot(vg_display[idx], gm[idx], 'ro', ms=4, label='gm max')
        ax1.set_xlabel("v_GS (V)")
        if method == "Sqrt":
            ax1.set_ylabel("gm (√A/V)")
        else:
            ax1.set_ylabel("gm (A/V)")
        ax1.legend(loc="best")

        # (Re)create hover annotations after clearing axes
        nonlocal annot0, annot1
        annot0 = ax0.annotate(
            "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
            fontsize=9, bbox=dict(boxstyle="round", fc="white", alpha=0.8),
            arrowprops=dict(arrowstyle="-", color="grey"))
        annot0.set_visible(False)
        annot1 = ax1.annotate(
            "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
            fontsize=9, bbox=dict(boxstyle="round", fc="white", alpha=0.8),
            arrowprops=dict(arrowstyle="-", color="grey"))
        annot1.set_visible(False)

        status_var.set(
            f"Device={device.upper()}  Vd={block.vd_volts:.4g} V  Method={method}  Vth={vth:.5g} V  idx={idx}  criterion=max-gm"
        )
        fig.tight_layout(pad=2.0)
        canvas.draw()

    vd_combo.bind("<<ComboboxSelected>>", update_plot)
    method_combo.bind("<<ComboboxSelected>>", update_plot)

    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Vth (linear extrapolation at max gm)")
    parser.add_argument("root", nargs="?", default=".", help="Root directory to scan for measurement .txt files")
    parser.add_argument("--vd", type=float, default=0.1, help="Target Vd in volts (default: 0.1)")
    parser.add_argument("--all-vd", action="store_true", help="Compute Vth for all Vd blocks instead of the closest to --vd")
    parser.add_argument("--include-vd0", action="store_true", help="Include Vd=0 blocks")
    parser.add_argument("--window", type=int, default=7, help="Window size for local linear fit around gm max (odd number)")
    parser.add_argument("--out", default="vth_results.csv", help="Output CSV path")
    parser.add_argument("--gui", action="store_true", help="Launch a GUI to select file, Vd and visualize IV, gm, tangent and Vth")
    parser.add_argument("--run_all", action="store_true", help="Scan ricorsivamente e produce: per-file CSV, summary per device, pivot per chip e (opzionale) confronto con un CSV di riferimento")
    parser.add_argument("--summary-out", default="vth_summary.csv", help="Summary CSV path (used with --run_all)")
    parser.add_argument("--plots-outdir", default=".", help="Directory to save plots (used with --run_all)")
    parser.add_argument("--daniele-csv", default="", help="Path al CSV di riferimento (es. RisultatiDaniele.csv) per il confronto")
    parser.add_argument("--compare-threshold", type=float, default=0.01, help="Soglia assoluta per PASS/FAIL sulle delta (default 0.01)")
    parser.add_argument("--methods", nargs="+", default=["traditional"], choices=["traditional", "sqrt"], 
                        help="Metodi da utilizzare per l'estrazione Vth (default: traditional)")
    args = parser.parse_args()

    if args.gui:
        run_gui()
        return

    root = os.path.abspath(args.root)

    if args.run_all:
        # derive default outputs from summary-out directory
        _out_dir = os.path.dirname(os.path.abspath(args.summary_out)) or os.getcwd()
        _pivot = os.path.join(_out_dir, "vth_by_chip.csv")
        _cmp = os.path.join(_out_dir, "vth_compare_clean.csv") if args.daniele_csv else None
        _cmp_status = os.path.join(_out_dir, "vth_compare_clean_status.csv") if args.daniele_csv else None
        run_batch(root=root, vd=args.vd, include_vd0=args.include_vd0, window=args.window,
                  results_csv=os.path.abspath(args.out), summary_csv=os.path.abspath(args.summary_out),
                  plots_outdir=os.path.abspath(args.plots_outdir), pivot_csv=_pivot,
                  daniele_csv=(os.path.abspath(args.daniele_csv) if args.daniele_csv else None),
                  compare_out=_cmp, compare_status_out=_cmp_status,
                  compare_threshold=args.compare_threshold, methods=args.methods)
        return
    pattern = os.path.join(root, "**", "*.txt")
    files = sorted(glob(pattern, recursive=True))
    files = [p for p in files if os.path.basename(p).lower().endswith(".txt")]
    if not files:
        print(f"No .txt files found under {root}")
        return

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    with open(args.out, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "file_path", "temperature", "device", "method", "vd_V", "vth_V",
            "gm_max_A_per_V", "gm_max_index", "num_points", "notes",
        ])

        for path in files:
            try:
                blocks = parse_measurement_file(path)
            except Exception as e:
                writer.writerow([path, "", "", "", "", "", "", "", "", 0, f"parse_error: {e}"])
                continue

            device = infer_device_type_from_path(path)

            # temperature from dir name like '295K'
            temp_match = re.search(r"([^/\\]+)K", path)
            temperature = temp_match.group(0) if temp_match else ""

            block_list: List[SweepBlock]
            if args.all_vd:
                block_list = [b for b in blocks if args.include_vd0 or abs(b.vd_volts) > 1e-12]
            else:
                block_list = find_blocks_for_vd(blocks, desired_vd=args.vd, include_vd0=args.include_vd0)

            if not block_list:
                writer.writerow([path, temperature, device, "", "", "", "", "", 0, "no_valid_blocks"])
                continue

            for b in block_list:
                # Calculate Vth for each requested method
                for method in args.methods:
                    try:
                        if method.lower() == "traditional":
                            vth, gm_max, idx = compute_vth_linear_extrapolation(
                                b.vg_volts, b.id_amps, device_type=device, window=args.window
                            )
                        elif method.lower() == "sqrt":
                            vth, gm_max, idx = compute_vth_sqrt_method(
                                b.vg_volts, b.id_amps, device_type=device, window=args.window
                            )
                        else:
                            raise ValueError(f"Unknown method: {method}")
                        notes = ""
                    except Exception as e:
                        vth, gm_max, idx = math.nan, math.nan, -1
                        notes = f"compute_error: {e}"

                    # Adjust vd for sqrt method
                    if method.lower() == "sqrt":
                        if device == "nmos":
                            b.vd_volts = 1.2
                        elif device == "pmos":
                            b.vd_volts = 0.0
                    writer.writerow([
                        path, temperature, device, method, f"{b.vd_volts:.6g}",
                        ("" if math.isnan(vth) else f"{vth:.6g}"),
                        ("" if math.isnan(gm_max) else f"{gm_max:.6g}"), idx,
                        b.vg_volts.size, notes,
                    ])
    # end main


if __name__ == "__main__":
    main()


