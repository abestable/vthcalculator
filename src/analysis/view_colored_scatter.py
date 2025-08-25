#!/usr/bin/env python3
"""
Script per visualizzare il plot scatter colorato per device
Mostra la correlazione tra i metodi con identificazione dei device specifici
"""

import matplotlib.pyplot as plt
import pandas as pd
import os

def main():
    print("Visualizzazione Plot Scatter Colorato per Device")
    print("=" * 50)
    
    # Carica i dati di confronto
    comparison_file = "aggregated_plots/aggregated_comparison_summary.csv"
    if not os.path.exists(comparison_file):
        print(f"Errore: File {comparison_file} non trovato!")
        return
    
    df = pd.read_csv(comparison_file)
    
    print(f"Caricati {len(df)} punti di confronto")
    print(f"Device types: {df['device_type'].unique()}")
    print(f"Device indices: {sorted(df['device_index'].unique())}")
    
    # Mostra statistiche per device
    print("\nStatistiche per device:")
    for device_type in ['NMOS', 'PMOS']:
        device_data = df[df['device_type'] == device_type]
        print(f"\n{device_type}:")
        for device_idx in sorted(device_data['device_index'].unique()):
            dev_data = device_data[device_data['device_index'] == device_idx]
            print(f"  Device {device_idx}: {len(dev_data)} punti, "
                  f"diff_media={dev_data['percent_diff'].mean():.1f}%")
    
    # Legenda colori
    device_colors = {1: '#1f77b4', 2: '#ff7f0e', 3: '#2ca02c', 4: '#d62728'}
    device_markers = {1: 'o', 2: 's', 3: '^', 4: 'D'}
    
    print("\nLegenda colori e marker:")
    for device_idx in [1, 2, 3, 4]:
        print(f"  Device {device_idx}: {device_colors[device_idx]} ({device_markers[device_idx]})")
    
    print("\nInterpretazione del plot:")
    print("- Ogni punto rappresenta un confronto tra i due metodi per lo stesso device alla stessa temperatura")
    print("- Colori diversi = Device diversi")
    print("- Marker diversi = Device diversi (doppia identificazione)")
    print("- Punti sulla linea y=x = Metodi perfettamente correlati")
    print("- Error bars = Incertezza statistica (stddev)")
    
    # Mostra alcuni esempi specifici
    print("\nEsempi di punti dal dataset:")
    for device_type in ['NMOS', 'PMOS']:
        device_data = df[df['device_type'] == device_type]
        print(f"\n{device_type} - Esempi:")
        for device_idx in sorted(device_data['device_index'].unique())[:2]:  # Primi 2 device
            dev_data = device_data[device_data['device_index'] == device_idx]
            example = dev_data.iloc[0]  # Primo punto
            print(f"  Device {device_idx}, T={example['temp_avg']}K:")
            print(f"    Traditional: {example['traditional_mean']:.6f} ± {example['traditional_std']:.6f} V/K")
            print(f"    Sqrt: {example['sqrt_mean']:.6f} ± {example['sqrt_std']:.6f} V/K")
            print(f"    Differenza: {example['percent_diff']:.1f}%")
    
    print(f"\nPlot salvato in: aggregated_plots/dvth_dt_aggregated_scatter.pdf")
    print("Il plot mostra ora chiaramente quale device è ogni punto!")

if __name__ == "__main__":
    main()
