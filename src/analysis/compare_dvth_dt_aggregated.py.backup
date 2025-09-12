#!/usr/bin/env python3
"""
Script per confrontare dVth/dT con aggregazione statistica.
Calcola Vth e dVth/dT con entrambi i metodi, raggruppa per device/temperatura
con media e stddev, e confronta i metodi sui dati aggregati.

Configurazione:
- NMOS: Vds=0.1V (traditional) vs Vds=1.2V (sqrt)
- PMOS: Vds=1.1V (traditional) vs Vds=0.0V (sqrt)
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
from typing import Dict, List, Tuple, Optional
from extract_vth import parse_measurement_file, compute_vth_linear_extrapolation, compute_vth_sqrt_method, infer_device_type_from_path, extract_temperature_from_path, infer_device_index_from_path


def extract_vth_for_aggregation(root_dir: str) -> pd.DataFrame:
    """
    Estrae Vth per tutti i device NMOS e PMOS usando configurazioni corrette.
    """
    results = []
    
    # Trova tutti i file NMOS e PMOS
    pattern = os.path.join(root_dir, "**", "*.txt")
    files = sorted(glob(pattern, recursive=True))
    device_files = [f for f in files if ("nmos" in f.lower() or "pmos" in f.lower()) and os.path.basename(f).lower() in {"1.txt", "2.txt", "3.txt", "4.txt"}]
    
    print(f"Trovati {len(device_files)} file totali")
    
    for file_path in device_files:
        try:
            # Parsing del file
            blocks = parse_measurement_file(file_path)
            
            # Estrai informazioni dal path
            temperature = extract_temperature_from_path(file_path)
            device_index = infer_device_index_from_path(file_path)
            device_type = infer_device_type_from_path(file_path)
            chip = re.search(r"chip\d+", file_path).group(0) if re.search(r"chip\d+", file_path) else "unknown"
            
            # Configurazione corretta per NMOS e PMOS
            if device_type.lower() == "nmos":
                # NMOS: Vds=0.1V (traditional) vs Vds=1.2V (sqrt)
                vd_traditional = 0.1
                vd_sqrt = 1.2
            else:  # PMOS
                # PMOS: Vds=1.1V (traditional) vs Vds=0.0V (sqrt) - CORRETTO
                vd_traditional = 1.1
                vd_sqrt = 0.0
            
            # Trova i blocchi per i Vds specificati
            vd_traditional_block = None
            vd_sqrt_block = None
            
            for block in blocks:
                if abs(block.vd_volts - vd_traditional) < 0.01:  # Tolleranza di 10mV
                    vd_traditional_block = block
                elif abs(block.vd_volts - vd_sqrt) < 0.01:  # Tolleranza di 10mV
                    vd_sqrt_block = block
            
            # Calcola Vth per metodo traditional
            if vd_traditional_block is not None:
                try:
                    vth_traditional, gm_max_traditional, idx_traditional = compute_vth_linear_extrapolation(
                        vd_traditional_block.vg_volts, vd_traditional_block.id_amps, device_type=device_type
                    )
                    if not np.isnan(vth_traditional):
                        results.append({
                            'file_path': file_path,
                            'chip': chip,
                            'temperature': temperature,
                            'device_type': device_type,
                            'device_index': device_index,
                            'vds': vd_traditional,
                            'method': 'traditional',
                            'vth': vth_traditional,
                            'gm_max': gm_max_traditional,
                            'idx': idx_traditional,
                            'num_points': len(vd_traditional_block.vg_volts)
                        })
                except Exception as e:
                    print(f"Errore nel calcolo Vth per {file_path} Vds={vd_traditional}V: {e}")
            
            # Calcola Vth per metodo sqrt
            if vd_sqrt_block is not None:
                try:
                    vth_sqrt, gm_max_sqrt, idx_sqrt = compute_vth_sqrt_method(
                        vd_sqrt_block.vg_volts, vd_sqrt_block.id_amps, device_type=device_type
                    )
                    if not np.isnan(vth_sqrt):
                        results.append({
                            'file_path': file_path,
                            'chip': chip,
                            'temperature': temperature,
                            'device_type': device_type,
                            'device_index': device_index,
                            'vds': vd_sqrt,
                            'method': 'sqrt',
                            'vth': vth_sqrt,
                            'gm_max': gm_max_sqrt,
                            'idx': idx_sqrt,
                            'num_points': len(vd_sqrt_block.vg_volts)
                        })
                except Exception as e:
                    print(f"Errore nel calcolo Vth per {file_path} Vds={vd_sqrt}V: {e}")
                    
        except Exception as e:
            print(f"Errore nel parsing del file {file_path}: {e}")
    
    return pd.DataFrame(results)


def calculate_dvth_dt_aggregated(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcola dVth/dT e raggruppa per device/temperatura con media e stddev.
    """
    # Converti temperature in numeri
    df['temp_k'] = df['temperature'].str.replace('K', '').astype(float)
    
    # Raggruppa per chip, device_type, device_index e metodo
    dvth_dt_results = []
    
    for (chip, device_type, device_idx, method), group in df.groupby(['chip', 'device_type', 'device_index', 'method']):
        if len(group) < 2:
            continue  # Serve almeno 2 punti per calcolare la derivata
            
        # Ordina per temperatura
        group_sorted = group.sort_values('temp_k')
        
        # Calcola dVth/dT usando differenze finite
        temps = group_sorted['temp_k'].values
        vths = group_sorted['vth'].values
        
        # Calcola dVth/dT per ogni coppia di punti consecutivi
        for i in range(len(temps) - 1):
            dtemp = temps[i+1] - temps[i]
            dvth = vths[i+1] - vths[i]
            dvth_dt = dvth / dtemp
            
            # Usa la temperatura media per il punto
            temp_avg = (temps[i] + temps[i+1]) / 2
            
            dvth_dt_results.append({
                'chip': chip,
                'device_type': device_type,
                'device_index': device_idx,
                'method': method,
                'vds': group_sorted.iloc[0]['vds'],
                'temp_low': temps[i],
                'temp_high': temps[i+1],
                'temp_avg': temp_avg,
                'vth_low': vths[i],
                'vth_high': vths[i+1],
                'dvth': dvth,
                'dtemp': dtemp,
                'dvth_dt': dvth_dt
            })
    
    df_dvth_dt = pd.DataFrame(dvth_dt_results)
    
    # Ora raggruppa per device e temperatura media con statistica
    aggregated_results = []
    
    for (device_type, device_idx, temp_avg), group in df_dvth_dt.groupby(['device_type', 'device_index', 'temp_avg']):
        # Calcola media e stddev per ogni metodo
        for method in ['traditional', 'sqrt']:
            method_data = group[group['method'] == method]
            if len(method_data) > 0:
                aggregated_results.append({
                    'device_type': device_type,
                    'device_index': device_idx,
                    'temp_avg': temp_avg,
                    'method': method,
                    'vds': method_data['vds'].iloc[0],
                    'dvth_dt_mean': method_data['dvth_dt'].mean(),
                    'dvth_dt_std': method_data['dvth_dt'].std(),
                    'dvth_dt_count': len(method_data),
                    'vth_low_mean': method_data['vth_low'].mean(),
                    'vth_high_mean': method_data['vth_high'].mean(),
                    'temp_low_mean': method_data['temp_low'].mean(),
                    'temp_high_mean': method_data['temp_high'].mean()
                })
    
    return pd.DataFrame(aggregated_results)


def create_aggregated_plots(df_aggregated: pd.DataFrame, output_dir: str = "."):
    """
    Crea grafici basati sui dati aggregati.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Configurazione per i plot
    plt.style.use('default')
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    
    # Colori per i metodi
    colors = {'traditional': 'blue', 'sqrt': 'red'}
    markers = {'traditional': 'o', 'sqrt': 's'}
    
    # 1. PLOT: dVth/dT vs Temperatura (aggregato)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS
    nmos_data = df_aggregated[df_aggregated['device_type'] == 'nmos']
    for method in ['traditional', 'sqrt']:
        method_data = nmos_data[nmos_data['method'] == method]
        if len(method_data) > 0:
            ax1.errorbar(method_data['temp_avg'], method_data['dvth_dt_mean'], 
                        yerr=method_data['dvth_dt_std'], 
                        marker=markers[method], color=colors[method], 
                        label=f'{method.capitalize()} (Vds={method_data["vds"].iloc[0]}V)',
                        alpha=0.7, markersize=6, capsize=3)
    
    ax1.set_xlabel('Temperatura (K)')
    ax1.set_ylabel('dVth/dT (V/K)')
    ax1.set_title('NMOS: dVth/dT vs Temperatura (Aggregato)\nMedia ± StdDev per device')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # PMOS
    pmos_data = df_aggregated[df_aggregated['device_type'] == 'pmos']
    for method in ['traditional', 'sqrt']:
        method_data = pmos_data[pmos_data['method'] == method]
        if len(method_data) > 0:
            ax2.errorbar(method_data['temp_avg'], method_data['dvth_dt_mean'], 
                        yerr=method_data['dvth_dt_std'], 
                        marker=markers[method], color=colors[method], 
                        label=f'{method.capitalize()} (Vds={method_data["vds"].iloc[0]}V)',
                        alpha=0.7, markersize=6, capsize=3)
    
    ax2.set_xlabel('Temperatura (K)')
    ax2.set_ylabel('dVth/dT (V/K)')
    ax2.set_title('PMOS: dVth/dT vs Temperatura (Aggregato)\nMedia ± StdDev per device')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'dvth_dt_aggregated_vs_temp.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. PLOT: Confronto diretto tra metodi (scatter con error bars) - COLORATO PER DEVICE
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Colori per device (4 device = 4 colori)
    device_colors = {1: '#1f77b4', 2: '#ff7f0e', 3: '#2ca02c', 4: '#d62728'}  # Blu, Arancione, Verde, Rosso
    device_markers = {1: 'o', 2: 's', 3: '^', 4: 'D'}  # Cerchio, Quadrato, Triangolo, Diamante
    
    # NMOS scatter
    nmos_comparison = []
    for (device_idx, temp_avg), group in nmos_data.groupby(['device_index', 'temp_avg']):
        if len(group) == 2:  # Deve avere entrambi i metodi
            traditional = group[group['method'] == 'traditional'].iloc[0]
            sqrt = group[group['method'] == 'sqrt'].iloc[0]
            nmos_comparison.append({
                'device_index': device_idx,
                'temp_avg': temp_avg,
                'traditional_mean': traditional['dvth_dt_mean'],
                'traditional_std': traditional['dvth_dt_std'],
                'sqrt_mean': sqrt['dvth_dt_mean'],
                'sqrt_std': sqrt['dvth_dt_std']
            })
    
    if nmos_comparison:
        nmos_comp_df = pd.DataFrame(nmos_comparison)
        
        # Scatter plot con error bars colorato per device
        for device_idx in nmos_comp_df['device_index'].unique():
            device_data = nmos_comp_df[nmos_comp_df['device_index'] == device_idx]
            ax1.errorbar(device_data['traditional_mean'], device_data['sqrt_mean'],
                        xerr=device_data['traditional_std'], yerr=device_data['sqrt_std'],
                        fmt=device_markers[device_idx], color=device_colors[device_idx], 
                        alpha=0.8, capsize=3, markersize=8,
                        label=f'Device {device_idx}')
        
        # Linea di identità
        min_val = min(nmos_comp_df['traditional_mean'].min(), nmos_comp_df['sqrt_mean'].min())
        max_val = max(nmos_comp_df['traditional_mean'].max(), nmos_comp_df['sqrt_mean'].max())
        ax1.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x')
        
        ax1.set_xlabel('dVth/dT Traditional Method (V/K)\nVds = 0.1V')
        ax1.set_ylabel('dVth/dT Sqrt Method (V/K)\nVds = 1.2V')
        ax1.set_title('NMOS: Method Comparison (Aggregated Data)')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
    
    # PMOS scatter
    pmos_comparison = []
    for (device_idx, temp_avg), group in pmos_data.groupby(['device_index', 'temp_avg']):
        if len(group) == 2:  # Deve avere entrambi i metodi
            traditional = group[group['method'] == 'traditional'].iloc[0]
            sqrt = group[group['method'] == 'sqrt'].iloc[0]
            pmos_comparison.append({
                'device_index': device_idx,
                'temp_avg': temp_avg,
                'traditional_mean': traditional['dvth_dt_mean'],
                'traditional_std': traditional['dvth_dt_std'],
                'sqrt_mean': sqrt['dvth_dt_mean'],
                'sqrt_std': sqrt['dvth_dt_std']
            })
    
    if pmos_comparison:
        pmos_comp_df = pd.DataFrame(pmos_comparison)
        
        # Scatter plot con error bars colorato per device
        for device_idx in pmos_comp_df['device_index'].unique():
            device_data = pmos_comp_df[pmos_comp_df['device_index'] == device_idx]
            ax2.errorbar(device_data['traditional_mean'], device_data['sqrt_mean'],
                        xerr=device_data['traditional_std'], yerr=device_data['sqrt_std'],
                        fmt=device_markers[device_idx], color=device_colors[device_idx], 
                        alpha=0.8, capsize=3, markersize=8,
                        label=f'Device {device_idx}')
        
        # Linea di identità
        min_val = min(pmos_comp_df['traditional_mean'].min(), pmos_comp_df['sqrt_mean'].min())
        max_val = max(pmos_comp_df['traditional_mean'].max(), pmos_comp_df['sqrt_mean'].max())
        ax2.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x')
        
        ax2.set_xlabel('dVth/dT Traditional Method (V/K)\nVds = 1.1V')
        ax2.set_ylabel('dVth/dT Sqrt Method (V/K)\nVds = 0.0V')
        ax2.set_title('PMOS: Method Comparison (Aggregated Data)')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'dvth_dt_aggregated_scatter.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. PLOT: Boxplot delle distribuzioni aggregate
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS boxplot
    nmos_traditional = nmos_data[nmos_data['method'] == 'traditional']['dvth_dt_mean']
    nmos_sqrt = nmos_data[nmos_data['method'] == 'sqrt']['dvth_dt_mean']
    
    ax1.boxplot([nmos_traditional, nmos_sqrt], 
                labels=['Traditional\n(Vds=0.1V)', 'Sqrt\n(Vds=1.2V)'])
    ax1.set_ylabel('dVth/dT (V/K)')
    ax1.set_title('NMOS: Distribuzione dVth/dT (Aggregato)')
    ax1.grid(True, alpha=0.3)
    
    # PMOS boxplot
    pmos_traditional = pmos_data[pmos_data['method'] == 'traditional']['dvth_dt_mean']
    pmos_sqrt = pmos_data[pmos_data['method'] == 'sqrt']['dvth_dt_mean']
    
    ax2.boxplot([pmos_traditional, pmos_sqrt], 
                labels=['Traditional\n(Vds=1.1V)', 'Sqrt\n(Vds=0.0V)'])
    ax2.set_ylabel('dVth/dT (V/K)')
    ax2.set_title('PMOS: Distribuzione dVth/dT (Aggregato)')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'dvth_dt_aggregated_boxplot.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. PLOT: Differenza vs temperatura (aggregato)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS differenza
    if nmos_comparison:
        nmos_comp_df['difference'] = nmos_comp_df['sqrt_mean'] - nmos_comp_df['traditional_mean']
        nmos_comp_df['difference_std'] = np.sqrt(nmos_comp_df['sqrt_std']**2 + nmos_comp_df['traditional_std']**2)
        
        ax1.errorbar(nmos_comp_df['temp_avg'], nmos_comp_df['difference'],
                    yerr=nmos_comp_df['difference_std'], fmt='o', alpha=0.7, capsize=3)
        
        ax1.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax1.set_xlabel('Temperatura (K)')
        ax1.set_ylabel('Differenza dVth/dT (Sqrt - Traditional) (V/K)')
        ax1.set_title('NMOS: Differenza tra Metodi vs Temperatura (Aggregato)')
        ax1.grid(True, alpha=0.3)
    
    # PMOS differenza
    if pmos_comparison:
        pmos_comp_df['difference'] = pmos_comp_df['sqrt_mean'] - pmos_comp_df['traditional_mean']
        pmos_comp_df['difference_std'] = np.sqrt(pmos_comp_df['sqrt_std']**2 + pmos_comp_df['traditional_std']**2)
        
        ax2.errorbar(pmos_comp_df['temp_avg'], pmos_comp_df['difference'],
                    yerr=pmos_comp_df['difference_std'], fmt='o', alpha=0.7, capsize=3)
        
        ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Temperatura (K)')
        ax2.set_ylabel('Differenza dVth/dT (Sqrt - Traditional) (V/K)')
        ax2.set_title('PMOS: Differenza tra Metodi vs Temperatura (Aggregato)')
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'dvth_dt_aggregated_difference.pdf'), dpi=300, bbox_inches='tight')
    plt.close()


def print_aggregated_statistics(df_aggregated: pd.DataFrame):
    """
    Stampa statistiche sui dati aggregati.
    """
    print("\n" + "="*80)
    print("STATISTICHE AGGREGATE - NMOS E PMOS")
    print("="*80)
    
    # Statistiche generali per device type e metodo
    print("\nStatistiche dVth/dT aggregate per device type e metodo:")
    stats = df_aggregated.groupby(['device_type', 'method']).agg({
        'dvth_dt_mean': ['count', 'mean', 'std'],
        'dvth_dt_std': 'mean'
    }).round(6)
    print(stats)
    
    # Confronto diretto per NMOS
    nmos_data = df_aggregated[df_aggregated['device_type'] == 'nmos']
    nmos_comparison = []
    for (device_idx, temp_avg), group in nmos_data.groupby(['device_index', 'temp_avg']):
        if len(group) == 2:
            traditional = group[group['method'] == 'traditional'].iloc[0]
            sqrt = group[group['method'] == 'sqrt'].iloc[0]
            diff = sqrt['dvth_dt_mean'] - traditional['dvth_dt_mean']
            percent_diff = (diff / traditional['dvth_dt_mean']) * 100 if traditional['dvth_dt_mean'] != 0 else float('inf')
            nmos_comparison.append({
                'device_index': device_idx,
                'temp_avg': temp_avg,
                'traditional': traditional['dvth_dt_mean'],
                'sqrt': sqrt['dvth_dt_mean'],
                'difference': diff,
                'percent_diff': percent_diff
            })
    
    if nmos_comparison:
        nmos_comp_df = pd.DataFrame(nmos_comparison)
        print(f"\nNMOS - Confronto diretto tra metodi (aggregato):")
        print(f"Numero di confronti diretti: {len(nmos_comp_df)}")
        print(f"Differenza media: {nmos_comp_df['difference'].mean():.6f} V/K")
        print(f"Differenza percentuale media: {nmos_comp_df['percent_diff'].mean():.2f}%")
        print(f"Deviazione standard della differenza: {nmos_comp_df['difference'].std():.6f} V/K")
    
    # Confronto diretto per PMOS
    pmos_data = df_aggregated[df_aggregated['device_type'] == 'pmos']
    pmos_comparison = []
    for (device_idx, temp_avg), group in pmos_data.groupby(['device_index', 'temp_avg']):
        if len(group) == 2:
            traditional = group[group['method'] == 'traditional'].iloc[0]
            sqrt = group[group['method'] == 'sqrt'].iloc[0]
            diff = sqrt['dvth_dt_mean'] - traditional['dvth_dt_mean']
            percent_diff = (diff / traditional['dvth_dt_mean']) * 100 if traditional['dvth_dt_mean'] != 0 else float('inf')
            pmos_comparison.append({
                'device_index': device_idx,
                'temp_avg': temp_avg,
                'traditional': traditional['dvth_dt_mean'],
                'sqrt': sqrt['dvth_dt_mean'],
                'difference': diff,
                'percent_diff': percent_diff
            })
    
    if pmos_comparison:
        pmos_comp_df = pd.DataFrame(pmos_comparison)
        print(f"\nPMOS - Confronto diretto tra metodi (aggregato):")
        print(f"Numero di confronti diretti: {len(pmos_comp_df)}")
        print(f"Differenza media: {pmos_comp_df['difference'].mean():.6f} V/K")
        print(f"Differenza percentuale media: {pmos_comp_df['percent_diff'].mean():.2f}%")
        print(f"Deviazione standard della differenza: {pmos_comp_df['difference'].std():.6f} V/K")


def main():
    """
    Funzione principale per eseguire l'analisi aggregata.
    """
    # Directory root dei dati
    root_dir = "."  # Assumiamo che lo script sia eseguito dalla directory root
    
    print("Analisi dVth/dT con Aggregazione Statistica")
    print("="*50)
    print("Configurazione CORRETTA:")
    print("- NMOS: Vds=0.1V (traditional) vs Vds=1.2V (sqrt)")
    print("- PMOS: Vds=1.1V (traditional) vs Vds=0.0V (sqrt)")
    print("="*50)
    
    print("\nEstrazione Vth per tutti i device...")
    df_vth = extract_vth_for_aggregation(root_dir)
    
    if df_vth.empty:
        print("Nessun dato trovato!")
        return
    
    print(f"Trovati {len(df_vth)} punti dati")
    print(f"Distribuzione per device type:")
    print(df_vth['device_type'].value_counts())
    print(f"Distribuzione per metodo:")
    print(df_vth['method'].value_counts())
    
    # Salva i dati Vth
    df_vth.to_csv('vth_aggregated_data.csv', index=False)
    print("Dati Vth salvati in vth_aggregated_data.csv")
    
    # Calcola dVth/dT e aggrega
    print("\nCalcolo dVth/dT e aggregazione statistica...")
    df_aggregated = calculate_dvth_dt_aggregated(df_vth)
    
    if df_aggregated.empty:
        print("Nessun dato dVth/dT aggregato calcolato!")
        return
    
    print(f"Calcolati {len(df_aggregated)} punti dVth/dT aggregati")
    
    # Salva i dati aggregati
    df_aggregated.to_csv('dvth_dt_aggregated_data.csv', index=False)
    print("Dati dVth/dT aggregati salvati in dvth_dt_aggregated_data.csv")
    
    # Crea grafici
    print("\nCreazione grafici aggregati...")
    create_aggregated_plots(df_aggregated, 'aggregated_plots')
    print("Grafici salvati in directory aggregated_plots/")
    
    # Statistiche riassuntive
    print_aggregated_statistics(df_aggregated)
    
    # Salva riepilogo confronto aggregato
    print("\nSalvataggio riepilogo confronto aggregato...")
    save_aggregated_comparison(df_aggregated, 'aggregated_plots')
    print("Riepilogo salvato in aggregated_plots/")


def save_aggregated_comparison(df_aggregated: pd.DataFrame, output_dir: str):
    """
    Salva un riepilogo del confronto aggregato.
    """
    summary_data = []
    
    for device_type in ['nmos', 'pmos']:
        device_data = df_aggregated[df_aggregated['device_type'] == device_type]
        
        for (device_idx, temp_avg), group in device_data.groupby(['device_index', 'temp_avg']):
            if len(group) == 2:
                traditional = group[group['method'] == 'traditional'].iloc[0]
                sqrt = group[group['method'] == 'sqrt'].iloc[0]
                diff = sqrt['dvth_dt_mean'] - traditional['dvth_dt_mean']
                percent_diff = (diff / traditional['dvth_dt_mean']) * 100 if traditional['dvth_dt_mean'] != 0 else float('inf')
                
                summary_data.append({
                    'device_type': device_type.upper(),
                    'device_index': device_idx,
                    'temp_avg': temp_avg,
                    'traditional_mean': traditional['dvth_dt_mean'],
                    'traditional_std': traditional['dvth_dt_std'],
                    'sqrt_mean': sqrt['dvth_dt_mean'],
                    'sqrt_std': sqrt['dvth_dt_std'],
                    'difference': diff,
                    'percent_diff': percent_diff
                })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(os.path.join(output_dir, 'aggregated_comparison_summary.csv'), index=False)
        
        # Statistiche per device type
        device_stats = summary_df.groupby('device_type').agg({
            'difference': ['count', 'mean', 'std'],
            'percent_diff': ['mean', 'std']
        }).round(6)
        device_stats.to_csv(os.path.join(output_dir, 'aggregated_device_statistics.csv'))


if __name__ == "__main__":
    main()

