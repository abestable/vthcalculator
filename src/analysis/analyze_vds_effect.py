#!/usr/bin/env python3
"""
Analyze the effect of Vds on Vth extraction methods.

This script analyzes how Vds affects the difference between traditional
and square root methods for Vth extraction. It processes multiple Vds
values for each device to understand the relationship.
"""

import argparse
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


def analyze_vds_effect_for_file(file_path: str) -> List[Dict]:
    """Analyze Vds effect for a single file with multiple Vds values."""
    try:
        blocks = parse_measurement_file(file_path)
        device = infer_device_type_from_path(file_path)
        
        # Filter out Vd=0 blocks
        candidates = [b for b in blocks if abs(b.vd_volts) > 1e-12]
        if not candidates:
            return []
        
        results = []
        for block in candidates:
            try:
                vth_traditional, gm_traditional, idx_traditional = compute_vth_linear_extrapolation(
                    block.vg_volts, block.id_amps, device_type=device
                )
            except Exception as e:
                vth_traditional, gm_traditional, idx_traditional = np.nan, np.nan, -1
                
            try:
                vth_sqrt, gm_sqrt, idx_sqrt = compute_vth_sqrt_method(
                    block.vg_volts, block.id_amps, device_type=device
                )
            except Exception as e:
                vth_sqrt, gm_sqrt, idx_sqrt = np.nan, np.nan, -1
            
            if not (np.isnan(vth_traditional) or np.isnan(vth_sqrt)):
                results.append({
                    "file_path": file_path,
                    "temperature": extract_temperature_from_path(file_path),
                    "device": device,
                    "device_index": infer_device_index_from_path(file_path),
                    "vd_V": block.vd_volts,
                    "vth_traditional_V": vth_traditional,
                    "vth_sqrt_V": vth_sqrt,
                    "gm_traditional_A_per_V": gm_traditional,
                    "gm_sqrt_A_per_V": gm_sqrt,
                    "vth_diff_V": vth_sqrt - vth_traditional,
                    "vth_diff_percent": ((vth_sqrt - vth_traditional) / abs(vth_traditional) * 100) if vth_traditional != 0 else np.nan,
                    "num_points": block.vg_volts.size
                })
        
        return results
        
    except Exception as e:
        return []


def plot_vds_analysis(df: pd.DataFrame, output_dir: str):
    """Create Vds analysis plots."""
    os.makedirs(output_dir, exist_ok=True)
    
    if df.empty:
        print("No valid data for plotting")
        return
    
    # Convert to numeric
    df["vth_diff_V"] = pd.to_numeric(df["vth_diff_V"], errors="coerce")
    df["vth_diff_percent"] = pd.to_numeric(df["vth_diff_percent"], errors="coerce")
    df["vd_V"] = pd.to_numeric(df["vd_V"], errors="coerce")
    
    # 1. Vth difference vs Vds scatter plot
    plt.figure(figsize=(12, 8))
    
    for device in ["nmos", "pmos"]:
        mask = df["device"] == device
        if mask.any():
            device_data = df[mask]
            plt.scatter(
                device_data["vd_V"],
                device_data["vth_diff_V"],
                alpha=0.6,
                label=f"{device.upper()}",
                s=50
            )
    
    plt.xlabel('Vds (V)')
    plt.ylabel('Vth Difference (√Id - Traditional) (V)')
    plt.title('Vth Difference vs Vds - All Data Points')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vth_diff_vs_vds_all.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Mean Vth difference vs Vds by device type
    plt.figure(figsize=(12, 8))
    
    for device in ["nmos", "pmos"]:
        mask = df["device"] == device
        if mask.any():
            device_data = df[mask]
            
            # Group by Vds and calculate mean and std
            vds_stats = device_data.groupby("vd_V").agg({
                "vth_diff_V": ["mean", "std", "count"],
                "vth_diff_percent": ["mean", "std"]
            }).reset_index()
            
            vds_stats.columns = ["vd_V", "mean_diff", "std_diff", "count", "mean_percent", "std_percent"]
            
            # Only plot Vds values with sufficient data
            vds_stats = vds_stats[vds_stats["count"] >= 3]
            
            if not vds_stats.empty:
                plt.errorbar(
                    vds_stats["vd_V"],
                    vds_stats["mean_diff"],
                    yerr=vds_stats["std_diff"],
                    marker='o',
                    label=f"{device.upper()}",
                    capsize=5,
                    markersize=8
                )
    
    plt.xlabel('Vds (V)')
    plt.ylabel('Mean Vth Difference (√Id - Traditional) (V)')
    plt.title('Mean Vth Difference vs Vds by Device Type')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vth_diff_vs_vds_mean.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Percentage difference vs Vds
    plt.figure(figsize=(12, 8))
    
    for device in ["nmos", "pmos"]:
        mask = df["device"] == device
        if mask.any():
            device_data = df[mask]
            
            # Group by Vds and calculate mean and std
            vds_stats = device_data.groupby("vd_V").agg({
                "vth_diff_percent": ["mean", "std", "count"]
            }).reset_index()
            
            vds_stats.columns = ["vd_V", "mean_percent", "std_percent", "count"]
            
            # Only plot Vds values with sufficient data
            vds_stats = vds_stats[vds_stats["count"] >= 3]
            
            if not vds_stats.empty:
                plt.errorbar(
                    vds_stats["vd_V"],
                    vds_stats["mean_percent"],
                    yerr=vds_stats["std_percent"],
                    marker='s',
                    label=f"{device.upper()}",
                    capsize=5,
                    markersize=8
                )
    
    plt.xlabel('Vds (V)')
    plt.ylabel('Mean Vth Difference (%)')
    plt.title('Mean Vth Difference Percentage vs Vds')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vth_diff_percent_vs_vds.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Box plot by Vds ranges
    plt.figure(figsize=(14, 8))
    
    # Create Vds ranges
    df["vds_range"] = pd.cut(df["vd_V"], bins=[0, 0.5, 1.0, 1.5, 2.0, 2.5], 
                            labels=["0-0.5V", "0.5-1.0V", "1.0-1.5V", "1.5-2.0V", "2.0-2.5V"])
    
    # Create subplots for each device type
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # NMOS
    nmos_data = df[df["device"] == "nmos"]
    if not nmos_data.empty:
        nmos_data.boxplot(column="vth_diff_V", by="vds_range", ax=ax1)
        ax1.set_title("NMOS: Vth Difference by Vds Range")
        ax1.set_ylabel("Vth Difference (√Id - Traditional) (V)")
        ax1.set_xlabel("Vds Range")
    
    # PMOS
    pmos_data = df[df["device"] == "pmos"]
    if not pmos_data.empty:
        pmos_data.boxplot(column="vth_diff_V", by="vds_range", ax=ax2)
        ax2.set_title("PMOS: Vth Difference by Vds Range")
        ax2.set_ylabel("Vth Difference (√Id - Traditional) (V)")
        ax2.set_xlabel("Vds Range")
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vth_diff_boxplot_by_vds.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 5. Summary statistics by Vds
    vds_summary = df.groupby(["vd_V", "device"]).agg({
        "vth_diff_V": ["mean", "std", "count"],
        "vth_diff_percent": ["mean", "std"]
    }).round(4)
    
    vds_summary.to_csv(os.path.join(output_dir, 'vds_analysis_summary.csv'))


def main():
    parser = argparse.ArgumentParser(description="Analyze Vds effect on Vth extraction methods")
    parser.add_argument("root", help="Root directory containing measurement files")
    parser.add_argument("--output", "-o", default="vds_effect_analysis.csv", 
                       help="Output CSV file (default: vds_effect_analysis.csv)")
    parser.add_argument("--plots", "-p", default="vds_effect_plots", 
                       help="Output directory for plots (default: vds_effect_plots)")
    
    args = parser.parse_args()
    
    # Find all measurement files
    pattern = os.path.join(args.root, "**", "*.txt")
    files = sorted(glob(pattern, recursive=True))
    files = [p for p in files if os.path.basename(p).lower() in {"1.txt", "2.txt", "3.txt", "4.txt"}]
    files = [p for p in files if (os.sep + "nmos" + os.sep).lower() in p.lower() or (os.sep + "pmos" + os.sep).lower() in p.lower()]
    
    print(f"Found {len(files)} measurement files")
    
    # Process each file
    all_results = []
    for i, file_path in enumerate(files):
        print(f"Processing {i+1}/{len(files)}: {os.path.basename(file_path)}")
        results = analyze_vds_effect_for_file(file_path)
        all_results.extend(results)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_results)
    
    # Save results
    df.to_csv(args.output, index=False)
    print(f"Results saved to {args.output}")
    
    # Create plots
    plot_vds_analysis(df, args.plots)
    print(f"Plots saved to {args.plots}/")
    
    # Print summary statistics
    if not df.empty:
        print("\nSummary Statistics:")
        print(f"Total data points: {len(df)}")
        print(f"Unique files: {df['file_path'].nunique()}")
        print(f"Vds range: {df['vd_V'].min():.3f}V to {df['vd_V'].max():.3f}V")
        
        print(f"\nVth Difference Statistics:")
        print(f"Mean difference: {df['vth_diff_V'].mean():.6f} V")
        print(f"Std difference: {df['vth_diff_V'].std():.6f} V")
        print(f"Min difference: {df['vth_diff_V'].min():.6f} V")
        print(f"Max difference: {df['vth_diff_V'].max():.6f} V")
        
        print(f"\nPercentage Difference Statistics:")
        print(f"Mean percentage: {df['vth_diff_percent'].mean():.2f}%")
        print(f"Std percentage: {df['vth_diff_percent'].std():.2f}%")
        
        # By device type
        for device in ["nmos", "pmos"]:
            mask = df["device"] == device
            if mask.any():
                device_data = df[mask]
                print(f"\n{device.upper()} Statistics:")
                print(f"Count: {len(device_data)}")
                print(f"Mean difference: {device_data['vth_diff_V'].mean():.6f} V")
                print(f"Std difference: {device_data['vth_diff_V'].std():.6f} V")
                print(f"Vds range: {device_data['vd_V'].min():.3f}V to {device_data['vd_V'].max():.3f}V")
        
        # By Vds ranges
        print(f"\nVds Range Analysis:")
        vds_ranges = [(0, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 2.0), (2.0, 2.5)]
        for vds_min, vds_max in vds_ranges:
            mask = (df["vd_V"] >= vds_min) & (df["vd_V"] < vds_max)
            if mask.any():
                range_data = df[mask]
                print(f"Vds {vds_min}-{vds_max}V: {len(range_data)} points, "
                      f"mean diff: {range_data['vth_diff_V'].mean():.6f}V, "
                      f"std: {range_data['vth_diff_V'].std():.6f}V")


if __name__ == "__main__":
    main()
