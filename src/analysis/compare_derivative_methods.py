#!/usr/bin/env python3
"""
Script per confrontare diversi metodi di calcolo della derivata.
Mostra le differenze tra differenze finite centrali, forward e backward.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_derivatives_comparison(csv_file):
    """Confronta diversi metodi di calcolo della derivata."""
    
    # Leggi i dati
    df = pd.read_csv(csv_file)
    df['temp_numeric'] = df['temperature'].str.replace('K', '').astype(float)
    
    # Prendi i dati di pmos1 come esempio
    pmos1_data = df[df['device_label'] == 'pmos1'].copy()
    pmos1_data = pmos1_data.sort_values('temp_numeric')
    
    temps = pmos1_data['temp_numeric'].values
    vth_values = pmos1_data['avg_vth_V'].values
    
    print("=== DATI ORIGINALI ===")
    print("Temperatura (K) | Vth (V)")
    print("-" * 25)
    for t, v in zip(temps, vth_values):
        print(f"{t:12.0f} | {v:8.3f}")
    
    print("\n=== CALCOLO DERIVATA ===")
    
    # Metodo 1: Differenze finite centrali (np.gradient)
    dVth_dT_central = np.gradient(vth_values, temps)
    
    # Metodo 2: Differenze finite forward
    dVth_dT_forward = np.zeros_like(vth_values)
    for i in range(len(vth_values) - 1):
        dVth_dT_forward[i] = (vth_values[i+1] - vth_values[i]) / (temps[i+1] - temps[i])
    dVth_dT_forward[-1] = dVth_dT_forward[-2]  # Ultimo punto
    
    # Metodo 3: Differenze finite backward
    dVth_dT_backward = np.zeros_like(vth_values)
    for i in range(1, len(vth_values)):
        dVth_dT_backward[i] = (vth_values[i] - vth_values[i-1]) / (temps[i] - temps[i-1])
    dVth_dT_backward[0] = dVth_dT_backward[1]  # Primo punto
    
    print("T(K) | Vth(V) | dVth/dT Central (V/K) | dVth/dT Forward (V/K) | dVth/dT Backward (V/K)")
    print("-" * 85)
    
    for i in range(len(temps)):
        print(f"{temps[i]:4.0f} | {vth_values[i]:6.3f} | {dVth_dT_central[i]:20.6f} | {dVth_dT_forward[i]:20.6f} | {dVth_dT_backward[i]:20.6f}")
    
    # Spiegazione dettagliata per un punto
    print("\n=== SPIEGAZIONE DETTAGLIATA ===")
    print("Per il punto a 140K (indice 2):")
    print(f"T[1] = {temps[1]}K, Vth[1] = {vth_values[1]:.3f}V")
    print(f"T[2] = {temps[2]}K, Vth[2] = {vth_values[2]:.3f}V")
    print(f"T[3] = {temps[3]}K, Vth[3] = {vth_values[3]:.3f}V")
    
    # Calcolo manuale della derivata centrale
    dVth_central = (vth_values[3] - vth_values[1]) / (temps[3] - temps[1])
    print(f"\nDerivata centrale a 140K:")
    print(f"dVth/dT = (Vth[3] - Vth[1]) / (T[3] - T[1])")
    print(f"dVth/dT = ({vth_values[3]:.3f} - {vth_values[1]:.3f}) / ({temps[3]:.0f} - {temps[1]:.0f})")
    print(f"dVth/dT = {vth_values[3] - vth_values[1]:.3f} / {temps[3] - temps[1]:.0f}")
    print(f"dVth/dT = {dVth_central:.6f} V/K")
    
    # Calcolo manuale della derivata forward
    dVth_forward = (vth_values[2] - vth_values[1]) / (temps[2] - temps[1])
    print(f"\nDerivata forward a 140K:")
    print(f"dVth/dT = (Vth[2] - Vth[1]) / (T[2] - T[1])")
    print(f"dVth/dT = ({vth_values[2]:.3f} - {vth_values[1]:.3f}) / ({temps[2]:.0f} - {temps[1]:.0f})")
    print(f"dVth/dT = {vth_values[2] - vth_values[1]:.3f} / {temps[2] - temps[1]:.0f}")
    print(f"dVth/dT = {dVth_forward:.6f} V/K")
    
    # Crea grafico di confronto
    fig, ax = plt.subplots(figsize=(12, 8))
    
    ax.plot(temps, dVth_dT_central, 'o-', label='Differenze finite centrali (np.gradient)', linewidth=2, markersize=8)
    ax.plot(temps, dVth_dT_forward, 's-', label='Differenze finite forward', linewidth=2, markersize=8)
    ax.plot(temps, dVth_dT_backward, '^-', label='Differenze finite backward', linewidth=2, markersize=8)
    
    ax.set_xlabel('Temperatura (K)', fontsize=14)
    ax.set_ylabel('dVth/dT (V/K)', fontsize=14)
    ax.set_title('Confronto Metodi di Calcolo Derivata - PMOS1', fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=12)
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('derivative_methods_comparison.pdf', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nGrafico di confronto salvato in: derivative_methods_comparison.pdf")

if __name__ == "__main__":
    csv_file = "vth_by_chip.csv"
    calculate_derivatives_comparison(csv_file)
