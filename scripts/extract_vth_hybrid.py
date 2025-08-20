#!/usr/bin/env python3
"""
Hybrid Vth extraction method that automatically chooses between traditional and sqrt methods.

This script implements a hybrid approach that selects the most appropriate Vth extraction
method based on the Vds value:
- For Vds < 0.5V: Use traditional method (linear region)
- For Vds >= 0.5V: Use sqrt method (saturation region)
"""

import argparse
import csv
import os
import sys
from glob import glob
from typing import Dict, List, Tuple

import numpy as np
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


def compute_vth_hybrid(vg: np.ndarray,
                      id_a: np.ndarray,
                      vd: float,
                      device_type: str,
                      window: int = 7,
                      criterion: str = "max-gm",
                      vds_threshold: float = 0.5) -> Tuple[float, float, int, str]:
    """Compute Vth using hybrid method based on Vds value.
    
    Args:
        vg: Gate voltage array
        id_a: Drain current array
        vd: Drain voltage
        device_type: 'nmos' or 'pmos'
        window: Window size for local fit
        criterion: 'max-gm' or 'max-dgm'
        vds_threshold: Vds threshold to switch between methods
        
    Returns:
        (vth_signed, gm_max, idx_gm_max, method_used)
    """
    if abs(vd) < vds_threshold:
        # Use traditional method for low Vds (linear region)
        vth, gm, idx = compute_vth_linear_extrapolation(
            vg, id_a, device_type=device_type, window=window, criterion=criterion
        )
        method = "traditional"
    else:
        # Use sqrt method for high Vds (saturation region)
        vth, gm, idx = compute_vth_sqrt_method(
            vg, id_a, device_type=device_type, window=window, criterion=criterion
        )
        method = "sqrt"
    
    return vth, gm, idx, method


def extract_vth_hybrid_for_file(file_path: str, vds_threshold: float = 0.5) -> Dict:
    """Extract Vth using hybrid method for a single file."""
    try:
        blocks = parse_measurement_file(file_path)
        device = infer_device_type_from_path(file_path)
        
        # Find the closest Vd block to target
        candidates = [b for b in blocks if abs(b.vd_volts) > 1e-12]
        if not candidates:
            return {"error": "no_valid_blocks"}
        
        vd_target_actual = 0.1 if device == "nmos" else 1.1
        closest = min(candidates, key=lambda b: abs(b.vd_volts - vd_target_actual))
        
        # Extract Vth using hybrid method
        try:
            vth_hybrid, gm_hybrid, idx_hybrid, method_used = compute_vth_hybrid(
                closest.vg_volts, closest.id_amps, closest.vd_volts, 
                device_type=device, vds_threshold=vds_threshold
            )
        except Exception as e:
            vth_hybrid, gm_hybrid, idx_hybrid, method_used = np.nan, np.nan, -1, "error"
        
        # Also extract using both methods for comparison
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
            "vth_hybrid_V": vth_hybrid,
            "vth_traditional_V": vth_traditional,
            "vth_sqrt_V": vth_sqrt,
            "gm_hybrid_A_per_V": gm_hybrid,
            "method_used": method_used,
            "vds_threshold": vds_threshold,
            "num_points": closest.vg_volts.size,
            "vth_hybrid_vs_traditional_V": vth_hybrid - vth_traditional if not (np.isnan(vth_hybrid) or np.isnan(vth_traditional)) else np.nan,
            "vth_hybrid_vs_sqrt_V": vth_hybrid - vth_sqrt if not (np.isnan(vth_hybrid) or np.isnan(vth_sqrt)) else np.nan
        }
        
    except Exception as e:
        return {"error": f"processing_error: {e}"}


def run_hybrid_batch(root: str, vds_threshold: float = 0.5, output_csv: str = "hybrid_vth_results.csv"):
    """Run hybrid Vth extraction on all files in the directory."""
    pattern = os.path.join(root, "**", "*.txt")
    files = sorted(glob(pattern, recursive=True))
    files = [p for p in files if os.path.basename(p).lower() in {"1.txt", "2.txt", "3.txt", "4.txt"}]
    files = [p for p in files if (os.sep + "nmos" + os.sep).lower() in p.lower() or (os.sep + "pmos" + os.sep).lower() in p.lower()]
    
    print(f"Found {len(files)} measurement files")
    print(f"Using Vds threshold: {vds_threshold}V")
    
    # Process each file
    results = []
    for i, file_path in enumerate(files):
        print(f"Processing {i+1}/{len(files)}: {os.path.basename(file_path)}")
        result = extract_vth_hybrid_for_file(file_path, vds_threshold)
        results.append(result)
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Save results
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")
    
    # Print summary statistics
    if "error" in df.columns:
        df_clean = df[df["error"].isna()].copy()
    else:
        df_clean = df.copy()
    if not df_clean.empty:
        print("\nSummary Statistics:")
        print(f"Total files processed: {len(df)}")
        print(f"Successful extractions: {len(df_clean)}")
        print(f"Failed extractions: {len(df) - len(df_clean)}")
        
        # Method usage statistics
        method_counts = df_clean["method_used"].value_counts()
        print(f"\nMethod Usage:")
        for method, count in method_counts.items():
            percentage = (count / len(df_clean)) * 100
            print(f"  {method}: {count} ({percentage:.1f}%)")
        
        # Vth statistics
        if not df_clean["vth_hybrid_V"].isna().all():
            print(f"\nHybrid Vth Statistics:")
            print(f"Mean Vth: {df_clean['vth_hybrid_V'].mean():.6f} V")
            print(f"Std Vth: {df_clean['vth_hybrid_V'].std():.6f} V")
            print(f"Min Vth: {df_clean['vth_hybrid_V'].min():.6f} V")
            print(f"Max Vth: {df_clean['vth_hybrid_V'].max():.6f} V")
        
        # Comparison statistics
        if not df_clean["vth_hybrid_vs_traditional_V"].isna().all():
            print(f"\nHybrid vs Traditional:")
            print(f"Mean difference: {df_clean['vth_hybrid_vs_traditional_V'].mean():.6f} V")
            print(f"Std difference: {df_clean['vth_hybrid_vs_traditional_V'].std():.6f} V")
        
        if not df_clean["vth_hybrid_vs_sqrt_V"].isna().all():
            print(f"\nHybrid vs Sqrt:")
            print(f"Mean difference: {df_clean['vth_hybrid_vs_sqrt_V'].mean():.6f} V")
            print(f"Std difference: {df_clean['vth_hybrid_vs_sqrt_V'].std():.6f} V")
        
        # By device type
        for device in ["nmos", "pmos"]:
            mask = df_clean["device"] == device
            if mask.any():
                device_data = df_clean[mask]
                print(f"\n{device.upper()} Statistics:")
                print(f"Count: {len(device_data)}")
                print(f"Mean Vth: {device_data['vth_hybrid_V'].mean():.6f} V")
                print(f"Std Vth: {device_data['vth_hybrid_V'].std():.6f} V")
                
                device_method_counts = device_data["method_used"].value_counts()
                print(f"Method usage:")
                for method, count in device_method_counts.items():
                    percentage = (count / len(device_data)) * 100
                    print(f"  {method}: {count} ({percentage:.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Extract Vth using hybrid method")
    parser.add_argument("root", help="Root directory containing measurement files")
    parser.add_argument("--output", "-o", default="hybrid_vth_results.csv", 
                       help="Output CSV file (default: hybrid_vth_results.csv)")
    parser.add_argument("--vds-threshold", "-t", type=float, default=0.5,
                       help="Vds threshold to switch between methods (default: 0.5V)")
    
    args = parser.parse_args()
    
    run_hybrid_batch(args.root, args.vds_threshold, args.output)


if __name__ == "__main__":
    main()
