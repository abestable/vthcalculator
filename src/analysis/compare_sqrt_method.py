#!/usr/bin/env python3
"""
Compare Vth extraction methods: traditional vs square root method.

This script compares the traditional method (using Id directly) with the
new square root method (using √Id) for Vth extraction. The square root
method is theoretically more appropriate for higher Vds values where
the transistor operates in saturation region.
"""

import argparse
import csv
import os
import sys
from glob import glob
from typing import Dict, List, Tuple

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Add the current directory to the path to import extract_vth
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from extract_vth import (
    parse_measurement_file, 
    compute_vth_linear_extrapolation,
    compute_vth_sqrt_method,
    infer_device_type_from_path,
    extract_temperature_from_path,
    infer_device_index_from_path
)


def compare_methods_for_file(file_path: str, vd_target: float = 0.1) -> Dict:
    """Compare traditional and sqrt methods for a single file."""
    try:
        blocks = parse_measurement_file(file_path)
        device = infer_device_type_from_path(file_path)
        
        # Find the closest Vd block to target
        candidates = [b for b in blocks if abs(b.vd_volts) > 1e-12]
        if not candidates:
            return {"error": "no_valid_blocks"}
        
        vd_target_actual = 0.1 if device == "nmos" else 1.1
        closest = min(candidates, key=lambda b: abs(b.vd_volts - vd_target_actual))
        
        # Extract Vth using both methods
        try:
            vth_traditional, gm_traditional, idx_traditional = compute_vth_linear_extrapolation(
                closest.vg_volts, closest.id_amps, device_type=device
            )
        except Exception as e:
            vth_traditional, gm_traditional, idx_traditional = np.nan, np.nan, -1
            
        try:
            vth_sqrt, gm_sqrt, idx_sqrt = compute_vth_sqrt_method(
                closest.vg_volts, closest.id_amps, device_type=device
            )
        except Exception as e:
            vth_sqrt, gm_sqrt, idx_sqrt = np.nan, np.nan, -1
        
        return {
            "file_path": file_path,
            "temperature": extract_temperature_from_path(file_path),
            "device": device,
            "device_index": infer_device_index_from_path(file_path),
            "vd_V": closest.vd_volts,
            "vth_traditional_V": vth_traditional,
            "vth_sqrt_V": vth_sqrt,
            "gm_traditional_A_per_V": gm_traditional,
            "gm_sqrt_A_per_V": gm_sqrt,
            "idx_traditional": idx_traditional,
            "idx_sqrt": idx_sqrt,
            "num_points": closest.vg_volts.size,
            "vth_diff_V": vth_sqrt - vth_traditional if not (np.isnan(vth_sqrt) or np.isnan(vth_traditional)) else np.nan,
            "vth_diff_percent": ((vth_sqrt - vth_traditional) / abs(vth_traditional) * 100) if not (np.isnan(vth_sqrt) or np.isnan(vth_traditional) or vth_traditional == 0) else np.nan
        }
        
    except Exception as e:
        return {"error": f"processing_error: {e}"}


def plot_comparison(df: pd.DataFrame, output_dir: str):
    """Create comparison plots."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter out rows with errors (if error column exists)
    if "error" in df.columns:
        df_clean = df[df["error"].isna()].copy()
    else:
        df_clean = df.copy()
    
    if df_clean.empty:
        print("No valid data for plotting")
        return
    
    # Convert to numeric
    df_clean["vth_traditional_V"] = pd.to_numeric(df_clean["vth_traditional_V"], errors="coerce")
    df_clean["vth_sqrt_V"] = pd.to_numeric(df_clean["vth_sqrt_V"], errors="coerce")
    df_clean["vth_diff_V"] = pd.to_numeric(df_clean["vth_diff_V"], errors="coerce")
    df_clean["vth_diff_percent"] = pd.to_numeric(df_clean["vth_diff_percent"], errors="coerce")
    
    # 1. Scatter plot: Traditional vs Sqrt method
    plt.figure(figsize=(10, 8))
    
    # Separate by device type
    for device in ["nmos", "pmos"]:
        mask = df_clean["device"] == device
        if mask.any():
            plt.scatter(
                df_clean[mask]["vth_traditional_V"],
                df_clean[mask]["vth_sqrt_V"],
                alpha=0.6,
                label=f"{device.upper()}",
                s=50
            )
    
    # Add diagonal line
    min_val = min(df_clean["vth_traditional_V"].min(), df_clean["vth_sqrt_V"].min())
    max_val = max(df_clean["vth_traditional_V"].max(), df_clean["vth_sqrt_V"].max())
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x')
    
    plt.xlabel('Vth Traditional Method (V)')
    plt.ylabel('Vth √Id Method (V)')
    plt.title('Vth Comparison: Traditional vs √Id Method')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vth_comparison_scatter.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Difference histogram
    plt.figure(figsize=(10, 6))
    
    for device in ["nmos", "pmos"]:
        mask = df_clean["device"] == device
        if mask.any():
            diff_data = df_clean[mask]["vth_diff_V"].dropna()
            if not diff_data.empty:
                plt.hist(diff_data, bins=20, alpha=0.6, label=f"{device.upper()}", density=True)
    
    plt.xlabel('Vth Difference (√Id - Traditional) (V)')
    plt.ylabel('Density')
    plt.title('Distribution of Vth Differences')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vth_difference_histogram.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Difference vs Vds
    plt.figure(figsize=(10, 6))
    
    for device in ["nmos", "pmos"]:
        mask = df_clean["device"] == device
        if mask.any():
            plt.scatter(
                df_clean[mask]["vd_V"],
                df_clean[mask]["vth_diff_V"],
                alpha=0.6,
                label=f"{device.upper()}",
                s=50
            )
    
    plt.xlabel('Vds (V)')
    plt.ylabel('Vth Difference (√Id - Traditional) (V)')
    plt.title('Vth Difference vs Vds')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vth_diff_vs_vds.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Summary statistics by temperature
    if "temperature" in df_clean.columns:
        temp_stats = df_clean.groupby(["temperature", "device"]).agg({
            "vth_diff_V": ["mean", "std", "count"],
            "vth_diff_percent": ["mean", "std"]
        }).round(4)
        
        temp_stats.to_csv(os.path.join(output_dir, 'temperature_summary.csv'))
        
        # Plot mean difference by temperature
        plt.figure(figsize=(12, 6))
        
        for device in ["nmos", "pmos"]:
            mask = df_clean["device"] == device
            if mask.any():
                temp_means = df_clean[mask].groupby("temperature")["vth_diff_V"].mean()
                temp_stds = df_clean[mask].groupby("temperature")["vth_diff_V"].std()
                
                plt.errorbar(
                    temp_means.index,
                    temp_means.values,
                    yerr=temp_stds.values,
                    marker='o',
                    label=f"{device.upper()}",
                    capsize=5
                )
        
        plt.xlabel('Temperature')
        plt.ylabel('Mean Vth Difference (√Id - Traditional) (V)')
        plt.title('Mean Vth Difference by Temperature')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'vth_diff_vs_temperature.pdf'), dpi=300, bbox_inches='tight')
        plt.close()


def main():
    parser = argparse.ArgumentParser(description="Compare Vth extraction methods")
    parser.add_argument("root", help="Root directory containing measurement files")
    parser.add_argument("--output", "-o", default="sqrt_method_comparison.csv", 
                       help="Output CSV file (default: sqrt_method_comparison.csv)")
    parser.add_argument("--plots", "-p", default="sqrt_method_plots", 
                       help="Output directory for plots (default: sqrt_method_plots)")
    parser.add_argument("--vd", type=float, default=0.1,
                       help="Target Vds value (default: 0.1)")
    
    args = parser.parse_args()
    
    # Find all measurement files
    pattern = os.path.join(args.root, "**", "*.txt")
    files = sorted(glob(pattern, recursive=True))
    files = [p for p in files if os.path.basename(p).lower() in {"1.txt", "2.txt", "3.txt", "4.txt"}]
    files = [p for p in files if (os.sep + "nmos" + os.sep).lower() in p.lower() or (os.sep + "pmos" + os.sep).lower() in p.lower()]
    
    print(f"Found {len(files)} measurement files")
    
    # Process each file
    results = []
    for i, file_path in enumerate(files):
        print(f"Processing {i+1}/{len(files)}: {os.path.basename(file_path)}")
        result = compare_methods_for_file(file_path, args.vd)
        results.append(result)
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Save results
    df.to_csv(args.output, index=False)
    print(f"Results saved to {args.output}")
    
    # Create plots
    plot_comparison(df, args.plots)
    print(f"Plots saved to {args.plots}/")
    
    # Print summary statistics
    if "error" in df.columns:
        df_clean = df[df["error"].isna()].copy()
    else:
        df_clean = df.copy()
    if not df_clean.empty:
        df_clean["vth_diff_V"] = pd.to_numeric(df_clean["vth_diff_V"], errors="coerce")
        df_clean["vth_diff_percent"] = pd.to_numeric(df_clean["vth_diff_percent"], errors="coerce")
        
        print("\nSummary Statistics:")
        print(f"Total files processed: {len(df)}")
        print(f"Successful extractions: {len(df_clean)}")
        print(f"Failed extractions: {len(df) - len(df_clean)}")
        
        if not df_clean["vth_diff_V"].isna().all():
            print(f"\nVth Difference Statistics:")
            print(f"Mean difference: {df_clean['vth_diff_V'].mean():.6f} V")
            print(f"Std difference: {df_clean['vth_diff_V'].std():.6f} V")
            print(f"Min difference: {df_clean['vth_diff_V'].min():.6f} V")
            print(f"Max difference: {df_clean['vth_diff_V'].max():.6f} V")
            
            print(f"\nPercentage Difference Statistics:")
            print(f"Mean percentage: {df_clean['vth_diff_percent'].mean():.2f}%")
            print(f"Std percentage: {df_clean['vth_diff_percent'].std():.2f}%")
        
        # By device type
        for device in ["nmos", "pmos"]:
            mask = df_clean["device"] == device
            if mask.any():
                device_data = df_clean[mask]["vth_diff_V"].dropna()
                if not device_data.empty:
                    print(f"\n{device.upper()} Statistics:")
                    print(f"Count: {len(device_data)}")
                    print(f"Mean difference: {device_data.mean():.6f} V")
                    print(f"Std difference: {device_data.std():.6f} V")


if __name__ == "__main__":
    main()
