#!/usr/bin/env python3
"""
Script per confrontare la variazione di Vth rispetto alla temperatura ambiente (295K)
Mostra come Vth cambia con la temperatura per entrambi i metodi
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Aggiungi il path per l'import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.extract_vth import *

def extract_vth_for_room_temp_comparison():
    """Estrae Vth per tutti i device e metodi"""
    print("Estrazione Vth per confronto con temperatura ambiente...")
    
    # Configurazione corretta
    config = {
        'nmos': {
            'traditional': {'vds': 0.1, 'method': 'traditional'},
            'sqrt': {'vds': 1.2, 'method': 'sqrt'}
        },
        'pmos': {
            'traditional': {'vds': 1.1, 'method': 'traditional'},
            'sqrt': {'vds': 0.0, 'method': 'sqrt'}
        }
    }
    
    results = []
    
    # Cerca file in tutte le directory chip
    for chip_dir in ['chip3', 'chip4', 'chip5']:
        if not os.path.exists(chip_dir):
            continue
            
        for temp_dir in os.listdir(chip_dir):
            temp_path = os.path.join(chip_dir, temp_dir)
            if not os.path.isdir(temp_path):
                continue
                
            # Estrai temperatura
            temp_str = extract_temperature_from_path(temp_path)
            if not temp_str:
                continue
            temp = float(temp_str.replace('K', ''))
            
            # Cerca device NMOS e PMOS
            for device_type in ['nmos', 'pmos']:
                device_path = os.path.join(temp_path, device_type.capitalize())
                if not os.path.exists(device_path):
                    continue
                    
                # Cerca file di misura
                for filename in os.listdir(device_path):
                    if filename.endswith('.txt'):
                        file_path = os.path.join(device_path, filename)
                        
                        # Estrai device index
                        device_idx = infer_device_index_from_path(file_path)
                        if device_idx is None:
                            continue
                        
                        # Estrai Vth per entrambi i metodi
                        for method_name, method_config in config[device_type].items():
                            try:
                                # Parsa il file e trova il blocco con Vds corretto
                                blocks = parse_measurement_file(file_path)
                                target_vds = method_config['vds']
                                
                                # Trova il blocco con Vds più vicino al target
                                best_block = None
                                min_diff = float('inf')
                                for block in blocks:
                                    if abs(block.vd_volts - target_vds) < min_diff:
                                        min_diff = abs(block.vd_volts - target_vds)
                                        best_block = block
                                
                                if best_block is None or min_diff > 0.1:  # Tolleranza 0.1V
                                    continue
                                
                                # Usa le funzioni corrette dal modulo extract_vth
                                if method_config['method'] == 'traditional':
                                    vth, _, _ = compute_vth_linear_extrapolation(
                                        best_block.vg_volts,
                                        best_block.id_amps,
                                        device_type
                                    )
                                else:  # sqrt method
                                    vth, _, _ = compute_vth_sqrt_method(
                                        best_block.vg_volts,
                                        best_block.id_amps,
                                        device_type
                                    )
                                
                                results.append({
                                    'chip': chip_dir,
                                    'device_type': device_type,
                                    'device_index': device_idx,
                                    'temperature': temp,
                                    'method': method_name,
                                    'vds': method_config['vds'],
                                    'vth': vth
                                })
                            except Exception as e:
                                print(f"Errore nel file {file_path}: {e}")
                                continue
    
    return pd.DataFrame(results)

def calculate_vth_vs_room_temp(df):
    """Calcola la differenza di Vth rispetto alla temperatura ambiente (295K)"""
    print("Calcolo differenze Vth rispetto a 295K...")
    
    # Trova i valori di riferimento a 295K
    room_temp_data = df[df['temperature'] == 295.0].copy()
    
    # Calcola differenze
    vth_diff_results = []
    
    for (device_type, device_idx, method), group in df.groupby(['device_type', 'device_index', 'method']):
        # Trova il valore di riferimento a 295K
        ref_data = room_temp_data[
            (room_temp_data['device_type'] == device_type) &
            (room_temp_data['device_index'] == device_idx) &
            (room_temp_data['method'] == method)
        ]
        
        if len(ref_data) == 0:
            continue
            
        ref_vth = ref_data['vth'].iloc[0]
        
        # Calcola differenze per tutte le temperature
        for _, row in group.iterrows():
            if row['temperature'] != 295.0:  # Escludi il riferimento stesso
                vth_diff_results.append({
                    'device_type': device_type,
                    'device_index': device_idx,
                    'method': method,
                    'vds': row['vds'],
                    'temperature': row['temperature'],
                    'vth': row['vth'],
                    'vth_ref_295k': ref_vth,
                    'vth_diff': row['vth'] - ref_vth,
                    'temp_diff': row['temperature'] - 295.0
                })
    
    return pd.DataFrame(vth_diff_results)

def aggregate_vth_diff_data(df):
    """Aggrega i dati di differenza Vth per device e temperatura"""
    print("Aggregazione dati differenze Vth...")
    
    aggregated_results = []
    
    for (device_type, device_idx, temp_avg, method), group in df.groupby(['device_type', 'device_index', 'temperature', 'method']):
        aggregated_results.append({
            'device_type': device_type,
            'device_index': device_idx,
            'temp_avg': temp_avg,
            'method': method,
            'vds': group['vds'].iloc[0],
            'vth_diff_mean': group['vth_diff'].mean(),
            'vth_diff_std': group['vth_diff'].std(),
            'vth_diff_count': len(group),
            'temp_diff_mean': group['temp_diff'].mean(),
            'vth_mean': group['vth'].mean(),
            'vth_ref_295k_mean': group['vth_ref_295k'].mean()
        })
    
    return pd.DataFrame(aggregated_results)

def create_vth_vs_room_temp_plots(df_aggregated, output_dir):
    """Crea i plot per il confronto Vth vs temperatura ambiente"""
    print("Creazione grafici Vth vs temperatura ambiente...")
    
    # Configurazione grafica
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    
    # Colori per device
    device_colors = {1: '#1f77b4', 2: '#ff7f0e', 3: '#2ca02c', 4: '#d62728'}
    device_markers = {1: 'o', 2: 's', 3: '^', 4: 'D'}
    
    # 1. PLOT: Vth vs Temperatura (aggregato)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS
    nmos_data = df_aggregated[df_aggregated['device_type'] == 'nmos']
    for method in ['traditional', 'sqrt']:
        method_data = nmos_data[nmos_data['method'] == method]
        if len(method_data) > 0:
            ax1.errorbar(method_data['temp_avg'], method_data['vth_mean'], 
                        yerr=method_data['vth_diff_std'], 
                        marker='o', alpha=0.7, markersize=6, capsize=3,
                        label=f'{method.capitalize()} (Vds={method_data["vds"].iloc[0]}V)')
    
    ax1.set_xlabel('Temperatura (K)')
    ax1.set_ylabel('Vth (V)')
    ax1.set_title('NMOS: Vth vs Temperatura\nRiferimento: Vth a 295K')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # PMOS
    pmos_data = df_aggregated[df_aggregated['device_type'] == 'pmos']
    for method in ['traditional', 'sqrt']:
        method_data = pmos_data[pmos_data['method'] == method]
        if len(method_data) > 0:
            ax2.errorbar(method_data['temp_avg'], method_data['vth_mean'], 
                        yerr=method_data['vth_diff_std'], 
                        marker='o', alpha=0.7, markersize=6, capsize=3,
                        label=f'{method.capitalize()} (Vds={method_data["vds"].iloc[0]}V)')
    
    ax2.set_xlabel('Temperatura (K)')
    ax2.set_ylabel('Vth (V)')
    ax2.set_title('PMOS: Vth vs Temperatura\nRiferimento: Vth a 295K')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vth_vs_room_temp.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. PLOT: Scatter Vth_diff vs Temperatura (colorato per device)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS scatter
    nmos_comparison = []
    for (device_idx, temp_avg), group in nmos_data.groupby(['device_index', 'temp_avg']):
        if len(group) == 2:  # Deve avere entrambi i metodi
            traditional = group[group['method'] == 'traditional'].iloc[0]
            sqrt = group[group['method'] == 'sqrt'].iloc[0]
            nmos_comparison.append({
                'device_index': device_idx,
                'temp_avg': temp_avg,
                'traditional_vth_diff': traditional['vth_diff_mean'],
                'traditional_std': traditional['vth_diff_std'],
                'sqrt_vth_diff': sqrt['vth_diff_mean'],
                'sqrt_std': sqrt['vth_diff_std']
            })
    
    if nmos_comparison:
        nmos_comp_df = pd.DataFrame(nmos_comparison)
        
        # Scatter plot con error bars colorato per device
        for device_idx in nmos_comp_df['device_index'].unique():
            device_data = nmos_comp_df[nmos_comp_df['device_index'] == device_idx]
            ax1.errorbar(device_data['traditional_vth_diff'], device_data['sqrt_vth_diff'],
                        xerr=device_data['traditional_std'], yerr=device_data['sqrt_std'],
                        fmt=device_markers[device_idx], color=device_colors[device_idx], 
                        alpha=0.8, capsize=3, markersize=8,
                        label=f'NMOS{device_idx}')
        
        # Linea di identità (bisettrice)
        min_val = min(nmos_comp_df['traditional_vth_diff'].min(), nmos_comp_df['sqrt_vth_diff'].min())
        max_val = max(nmos_comp_df['traditional_vth_diff'].max(), nmos_comp_df['sqrt_vth_diff'].max())
        ax1.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x')
        
        # Imposta la stessa scala sugli assi e posiziona (0,0) nell'angolo
        ax1.set_xlabel('ΔVth Traditional Method (V)\nVds = 0.1V')
        ax1.set_ylabel('ΔVth Sqrt Method (V)\nVds = 1.2V')
        ax1.set_title('NMOS: ΔVth vs Room Temp (295K) Comparison')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # Stessa scala sugli assi e forza (0,0) nell'angolo
        ax1.set_aspect('equal', adjustable='box')
        # Per NMOS: tutti i dati sono positivi, quindi (0,0) va nell'angolo in basso a sinistra
        ax1.set_xlim(0, max_val * 1.1)
        ax1.set_ylim(0, max_val * 1.1)
    
    # PMOS scatter
    pmos_comparison = []
    for (device_idx, temp_avg), group in pmos_data.groupby(['device_index', 'temp_avg']):
        if len(group) == 2:  # Deve avere entrambi i metodi
            traditional = group[group['method'] == 'traditional'].iloc[0]
            sqrt = group[group['method'] == 'sqrt'].iloc[0]
            pmos_comparison.append({
                'device_index': device_idx,
                'temp_avg': temp_avg,
                'traditional_vth_diff': traditional['vth_diff_mean'],
                'traditional_std': traditional['vth_diff_std'],
                'sqrt_vth_diff': sqrt['vth_diff_mean'],
                'sqrt_std': sqrt['vth_diff_std']
            })
    
    if pmos_comparison:
        pmos_comp_df = pd.DataFrame(pmos_comparison)
        
        # Scatter plot con error bars colorato per device
        for device_idx in pmos_comp_df['device_index'].unique():
            device_data = pmos_comp_df[pmos_comp_df['device_index'] == device_idx]
            ax2.errorbar(device_data['traditional_vth_diff'], device_data['sqrt_vth_diff'],
                        xerr=device_data['traditional_std'], yerr=device_data['sqrt_std'],
                        fmt=device_markers[device_idx], color=device_colors[device_idx], 
                        alpha=0.8, capsize=3, markersize=8,
                        label=f'PMOS{device_idx}')
        
        # Linea di identità (bisettrice)
        min_val = min(pmos_comp_df['traditional_vth_diff'].min(), pmos_comp_df['sqrt_vth_diff'].min())
        max_val = max(pmos_comp_df['traditional_vth_diff'].max(), pmos_comp_df['sqrt_vth_diff'].max())
        ax2.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x')
        
        # Imposta la stessa scala sugli assi e posiziona (0,0) nell'angolo
        ax2.set_xlabel('ΔVth Traditional Method (V)\nVds = 1.1V')
        ax2.set_ylabel('ΔVth Sqrt Method (V)\nVds = 0.0V')
        ax2.set_title('PMOS: ΔVth vs Room Temp (295K) Comparison')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        # Stessa scala sugli assi e forza (0,0) nell'angolo
        ax2.set_aspect('equal', adjustable='box')
        # Per PMOS: tutti i dati sono negativi, quindi (0,0) va nell'angolo in alto a destra
        ax2.set_xlim(min_val * 1.1, 0)
        ax2.set_ylim(min_val * 1.1, 0)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vth_diff_vs_room_temp_scatter.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. PLOT: ΔVth vs ΔTemperatura
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS ΔVth vs ΔT
    for method in ['traditional', 'sqrt']:
        method_data = nmos_data[nmos_data['method'] == method]
        if len(method_data) > 0:
            ax1.errorbar(method_data['temp_diff_mean'], method_data['vth_diff_mean'],
                        yerr=method_data['vth_diff_std'], 
                        marker='o', alpha=0.7, markersize=6, capsize=3,
                        label=f'{method.capitalize()} (Vds={method_data["vds"].iloc[0]}V)')
    
    ax1.set_xlabel('ΔTemperatura (K)\nT - 295K')
    ax1.set_ylabel('ΔVth (V)\nVth - Vth(295K)')
    ax1.set_title('NMOS: ΔVth vs ΔTemperatura')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # PMOS ΔVth vs ΔT
    for method in ['traditional', 'sqrt']:
        method_data = pmos_data[pmos_data['method'] == method]
        if len(method_data) > 0:
            ax2.errorbar(method_data['temp_diff_mean'], method_data['vth_diff_mean'],
                        yerr=method_data['vth_diff_std'], 
                        marker='o', alpha=0.7, markersize=6, capsize=3,
                        label=f'{method.capitalize()} (Vds={method_data["vds"].iloc[0]}V)')
    
    ax2.set_xlabel('ΔTemperatura (K)\nT - 295K')
    ax2.set_ylabel('ΔVth (V)\nVth - Vth(295K)')
    ax2.set_title('PMOS: ΔVth vs ΔTemperatura')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vth_diff_vs_temp_diff.pdf'), dpi=300, bbox_inches='tight')
    plt.close()

def main():
    print("Analisi Vth vs Temperatura Ambiente (295K)")
    print("=" * 50)
    
    # Crea directory output
    output_dir = "vth_vs_room_temp_plots"
    os.makedirs(output_dir, exist_ok=True)
    
    # Estrazione dati
    df_vth = extract_vth_for_room_temp_comparison()
    print(f"Estratti {len(df_vth)} punti Vth")
    
    # Salva dati grezzi
    df_vth.to_csv('vth_vs_room_temp_data.csv', index=False)
    print("Dati Vth salvati in vth_vs_room_temp_data.csv")
    
    # Calcolo differenze rispetto a 295K
    df_diff = calculate_vth_vs_room_temp(df_vth)
    print(f"Calcolate {len(df_diff)} differenze Vth")
    
    # Salva differenze
    df_diff.to_csv('vth_diff_vs_room_temp_data.csv', index=False)
    print("Differenze Vth salvate in vth_diff_vs_room_temp_data.csv")
    
    # Aggregazione
    df_aggregated = aggregate_vth_diff_data(df_diff)
    print(f"Aggregati {len(df_aggregated)} punti")
    
    # Salva dati aggregati
    df_aggregated.to_csv(os.path.join(output_dir, 'vth_diff_aggregated_data.csv'), index=False)
    print("Dati aggregati salvati in vth_diff_aggregated_data.csv")
    
    # Creazione grafici
    create_vth_vs_room_temp_plots(df_aggregated, output_dir)
    print(f"Grafici salvati in directory {output_dir}/")
    
    # Statistiche
    print("\n" + "="*80)
    print("STATISTICHE Vth vs TEMPERATURA AMBIENTE")
    print("="*80)
    
    for device_type in ['nmos', 'pmos']:
        device_data = df_aggregated[df_aggregated['device_type'] == device_type]
        print(f"\n{device_type.upper()}:")
        
        for method in ['traditional', 'sqrt']:
            method_data = device_data[device_data['method'] == method]
            if len(method_data) > 0:
                print(f"  {method.capitalize()} (Vds={method_data['vds'].iloc[0]}V):")
                print(f"    ΔVth medio: {method_data['vth_diff_mean'].mean():.6f} V")
                print(f"    ΔVth std: {method_data['vth_diff_mean'].std():.6f} V")
                print(f"    Range ΔVth: [{method_data['vth_diff_mean'].min():.6f}, {method_data['vth_diff_mean'].max():.6f}] V")
    
    print(f"\nAnalisi completata! Grafici in: {output_dir}/")

if __name__ == "__main__":
    main()
