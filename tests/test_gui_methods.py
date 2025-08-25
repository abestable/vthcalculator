#!/usr/bin/env python3
"""
Test script to verify that the different Vth extraction methods work correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.extract_vth import (
    parse_measurement_file,
    compute_vth_linear_extrapolation,
    compute_vth_sqrt_method,
    infer_device_type_from_path
)

def test_methods_on_sample_file():
    """Test all three methods on a sample file."""
    
    # Find a sample file
    sample_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".txt") and ("nmos" in root.lower() or "pmos" in root.lower()):
                sample_files.append(os.path.join(root, file))
                if len(sample_files) >= 2:  # Get one NMOS and one PMOS
                    break
        if len(sample_files) >= 2:
            break
    
    if not sample_files:
        print("No sample files found!")
        return
    
    print("Testing Vth extraction methods on sample files:")
    print("=" * 60)
    
    for file_path in sample_files[:2]:  # Test first 2 files
        print(f"\nFile: {file_path}")
        print("-" * 40)
        
        try:
            blocks = parse_measurement_file(file_path)
            device = infer_device_type_from_path(file_path)
            
            # Find a suitable block (not Vd=0)
            suitable_blocks = [b for b in blocks if abs(b.vd_volts) > 1e-12]
            if not suitable_blocks:
                print("  No suitable Vd blocks found")
                continue
            
            block = suitable_blocks[0]
            print(f"  Device: {device}")
            print(f"  Vd: {block.vd_volts:.3f} V")
            print(f"  Points: {len(block.vg_volts)}")
            
            # Test Traditional method
            try:
                vth_trad, gm_trad, idx_trad = compute_vth_linear_extrapolation(
                    block.vg_volts, block.id_amps, device_type=device
                )
                print(f"  Traditional: Vth = {vth_trad:.6f} V, gm_max = {gm_trad:.6f} A/V")
            except Exception as e:
                print(f"  Traditional: ERROR - {e}")
            
            # Test Sqrt method
            try:
                vth_sqrt, gm_sqrt, idx_sqrt = compute_vth_sqrt_method(
                    block.vg_volts, block.id_amps, device_type=device
                )
                print(f"  Sqrt:       Vth = {vth_sqrt:.6f} V, gm_max = {gm_sqrt:.6f} √A/V")
            except Exception as e:
                print(f"  Sqrt:       ERROR - {e}")
            
            # Test Hybrid method
            try:
                vds_threshold = 0.5
                if abs(block.vd_volts) < vds_threshold:
                    vth_hybrid, gm_hybrid, idx_hybrid = compute_vth_linear_extrapolation(
                        block.vg_volts, block.id_amps, device_type=device
                    )
                    method_used = "Traditional"
                else:
                    vth_hybrid, gm_hybrid, idx_hybrid = compute_vth_sqrt_method(
                        block.vg_volts, block.id_amps, device_type=device
                    )
                    method_used = "Sqrt"
                print(f"  Hybrid:     Vth = {vth_hybrid:.6f} V, gm_max = {gm_hybrid:.6f} ({method_used})")
            except Exception as e:
                print(f"  Hybrid:     ERROR - {e}")
            
            # Calculate differences
            if 'vth_trad' in locals() and 'vth_sqrt' in locals():
                diff = vth_sqrt - vth_trad
                print(f"  Difference (Sqrt - Traditional): {diff:.6f} V")
            
        except Exception as e:
            print(f"  ERROR processing file: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    test_methods_on_sample_file()
