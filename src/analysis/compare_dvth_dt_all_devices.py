#!/usr/bin/env python3
"""
Script per confrontare i risultati di dVth/dT per tutti i device NMOS e PMOS a tutte le temperature.
Confronta:
- NMOS: Vds=0.1V (traditional) vs Vds=1.2V (sqrt)
- PMOS: Vds=1.1V (traditional) vs Vds=0.1V (sqrt)
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
from typing import Dict, List, Tuple, Optional
from extract_vth import parse_measurement_file, compute_vth_linear_extrapolation, compute_vth_sqrt_method, infer_device_type_from_path, extract_temperature_from_path, infer_device_index_from_path


def extract_vth_for_comparison_all_devices(root_dir: str) -> pd.DataFrame:
    """
    Estrae Vth per tutti i device NMOS e PMOS a tutte le temperature usando entrambi i metodi.
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
            
            # Configurazione per NMOS e PMOS
            if device_type.lower() == "nmos":
                # NMOS: Vds=0.1V (traditional) vs Vds=1.2V (sqrt)
                vd_traditional = 0.1
                vd_sqrt = 1.2
            else:  # PMOS
                # PMOS: Vds=1.1V (traditional) vs Vds=0.1V (sqrt)
                vd_traditional = 1.1
                vd_sqrt = 0.1
            
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


def calculate_dvth_dt(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcola dVth/dT per ogni device e metodo.
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
    
    return pd.DataFrame(dvth_dt_results)


def create_comprehensive_plots(df_vth: pd.DataFrame, df_dvth_dt: pd.DataFrame, output_dir: str = "."):
    """
    Crea una serie completa di grafici per la discussione con i colleghi.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Configurazione per i plot
    plt.style.use('default')
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    
    # Colori e marker per i metodi
    colors = {'traditional': 'blue', 'sqrt': 'red'}
    markers = {'traditional': 'o', 'sqrt': 's'}
    
    # 1. PLOT 1: Vth vs Temperatura per NMOS e PMOS
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # NMOS - Vth vs T
    nmos_data = df_vth[df_vth['device_type'] == 'nmos']
    for (chip, device_idx), group in nmos_data.groupby(['chip', 'device_index']):
        for method in ['traditional', 'sqrt']:
            method_data = group[group['method'] == method]
            if len(method_data) > 0:
                ax1.plot(method_data['temp_k'], method_data['vth'], 
                        marker=markers[method], color=colors[method], 
                        label=f'{chip}_NMOS{device_idx}_{method}' if method == 'traditional' else "",
                        alpha=0.7, markersize=4)
    
    ax1.set_xlabel('Temperatura (K)')
    ax1.set_ylabel('Vth (V)')
    ax1.set_title('NMOS: Vth vs Temperatura\nTraditional (Vds=0.1V) vs Sqrt (Vds=1.2V)')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # PMOS - Vth vs T
    pmos_data = df_vth[df_vth['device_type'] == 'pmos']
    for (chip, device_idx), group in pmos_data.groupby(['chip', 'device_index']):
        for method in ['traditional', 'sqrt']:
            method_data = group[group['method'] == method]
            if len(method_data) > 0:
                ax2.plot(method_data['temp_k'], method_data['vth'], 
                        marker=markers[method], color=colors[method], 
                        label=f'{chip}_PMOS{device_idx}_{method}' if method == 'traditional' else "",
                        alpha=0.7, markersize=4)
    
    ax2.set_xlabel('Temperatura (K)')
    ax2.set_ylabel('Vth (V)')
    ax2.set_title('PMOS: Vth vs Temperatura\nTraditional (Vds=1.1V) vs Sqrt (Vds=0.1V)')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # NMOS - dVth/dT vs T
    nmos_dvth = df_dvth_dt[df_dvth_dt['device_type'] == 'nmos']
    for (chip, device_idx), group in nmos_dvth.groupby(['chip', 'device_index']):
        for method in ['traditional', 'sqrt']:
            method_data = group[group['method'] == method]
            if len(method_data) > 0:
                ax3.plot(method_data['temp_avg'], method_data['dvth_dt'], 
                        marker=markers[method], color=colors[method], 
                        label=f'{chip}_NMOS{device_idx}_{method}' if method == 'traditional' else "",
                        alpha=0.7, markersize=4)
    
    ax3.set_xlabel('Temperatura (K)')
    ax3.set_ylabel('dVth/dT (V/K)')
    ax3.set_title('NMOS: dVth/dT vs Temperatura')
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # PMOS - dVth/dT vs T
    pmos_dvth = df_dvth_dt[df_dvth_dt['device_type'] == 'pmos']
    for (chip, device_idx), group in pmos_dvth.groupby(['chip', 'device_index']):
        for method in ['traditional', 'sqrt']:
            method_data = group[group['method'] == method]
            if len(method_data) > 0:
                ax4.plot(method_data['temp_avg'], method_data['dvth_dt'], 
                        marker=markers[method], color=colors[method], 
                        label=f'{chip}_PMOS{device_idx}_{method}' if method == 'traditional' else "",
                        alpha=0.7, markersize=4)
    
    ax4.set_xlabel('Temperatura (K)')
    ax4.set_ylabel('dVth/dT (V/K)')
    ax4.set_title('PMOS: dVth/dT vs Temperatura')
    ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'vth_dvth_dt_overview.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. PLOT 2: Scatter plot confronto metodi
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS scatter
    nmos_comparison = []
    for (chip, device_idx, temp_avg), group in nmos_dvth.groupby(['chip', 'device_index', 'temp_avg']):
        if len(group) == 2:
            traditional = group[group['method'] == 'traditional']['dvth_dt'].iloc[0]
            sqrt = group[group['method'] == 'sqrt']['dvth_dt'].iloc[0]
            nmos_comparison.append({
                'traditional': traditional,
                'sqrt': sqrt,
                'chip': chip,
                'device_index': device_idx,
                'temp_avg': temp_avg
            })
    
    if nmos_comparison:
        nmos_comp_df = pd.DataFrame(nmos_comparison)
        ax1.scatter(nmos_comp_df['traditional'], nmos_comp_df['sqrt'], alpha=0.7, s=60)
        
        # Linea di identità
        min_val = min(nmos_comp_df['traditional'].min(), nmos_comp_df['sqrt'].min())
        max_val = max(nmos_comp_df['traditional'].max(), nmos_comp_df['sqrt'].max())
        ax1.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x')
        
        ax1.set_xlabel('dVth/dT Traditional (V/K)')
        ax1.set_ylabel('dVth/dT Sqrt (V/K)')
        ax1.set_title('NMOS: Confronto dVth/dT\nTraditional (Vds=0.1V) vs Sqrt (Vds=1.2V)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    # PMOS scatter
    pmos_comparison = []
    for (chip, device_idx, temp_avg), group in pmos_dvth.groupby(['chip', 'device_index', 'temp_avg']):
        if len(group) == 2:
            traditional = group[group['method'] == 'traditional']['dvth_dt'].iloc[0]
            sqrt = group[group['method'] == 'sqrt']['dvth_dt'].iloc[0]
            pmos_comparison.append({
                'traditional': traditional,
                'sqrt': sqrt,
                'chip': chip,
                'device_index': device_idx,
                'temp_avg': temp_avg
            })
    
    if pmos_comparison:
        pmos_comp_df = pd.DataFrame(pmos_comparison)
        ax2.scatter(pmos_comp_df['traditional'], pmos_comp_df['sqrt'], alpha=0.7, s=60)
        
        # Linea di identità
        min_val = min(pmos_comp_df['traditional'].min(), pmos_comp_df['sqrt'].min())
        max_val = max(pmos_comp_df['traditional'].max(), pmos_comp_df['sqrt'].max())
        ax2.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x')
        
        ax2.set_xlabel('dVth/dT Traditional (V/K)')
        ax2.set_ylabel('dVth/dT Sqrt (V/K)')
        ax2.set_title('PMOS: Confronto dVth/dT\nTraditional (Vds=1.1V) vs Sqrt (Vds=0.1V)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'dvth_dt_scatter_comparison.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. PLOT 3: Boxplot confronto distribuzioni
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS boxplot
    nmos_traditional = nmos_dvth[nmos_dvth['method'] == 'traditional']['dvth_dt']
    nmos_sqrt = nmos_dvth[nmos_dvth['method'] == 'sqrt']['dvth_dt']
    
    ax1.boxplot([nmos_traditional, nmos_sqrt], 
                labels=['Traditional\n(Vds=0.1V)', 'Sqrt\n(Vds=1.2V)'])
    ax1.set_ylabel('dVth/dT (V/K)')
    ax1.set_title('NMOS: Distribuzione dVth/dT per metodo')
    ax1.grid(True, alpha=0.3)
    
    # PMOS boxplot
    pmos_traditional = pmos_dvth[pmos_dvth['method'] == 'traditional']['dvth_dt']
    pmos_sqrt = pmos_dvth[pmos_dvth['method'] == 'sqrt']['dvth_dt']
    
    ax2.boxplot([pmos_traditional, pmos_sqrt], 
                labels=['Traditional\n(Vds=1.1V)', 'Sqrt\n(Vds=0.1V)'])
    ax2.set_ylabel('dVth/dT (V/K)')
    ax2.set_title('PMOS: Distribuzione dVth/dT per metodo')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'dvth_dt_boxplot_comparison.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. PLOT 4: Differenza vs temperatura
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS differenza
    if nmos_comparison:
        nmos_comp_df['difference'] = nmos_comp_df['sqrt'] - nmos_comp_df['traditional']
        colors_chip = {'chip3': 'red', 'chip4': 'blue', 'chip5': 'green'}
        
        for chip in ['chip3', 'chip4', 'chip5']:
            chip_data = nmos_comp_df[nmos_comp_df['chip'] == chip]
            if len(chip_data) > 0:
                ax1.scatter(chip_data['temp_avg'], chip_data['difference'], 
                           color=colors_chip[chip], label=chip, alpha=0.7, s=60)
        
        ax1.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax1.set_xlabel('Temperatura (K)')
        ax1.set_ylabel('Differenza dVth/dT (Sqrt - Traditional) (V/K)')
        ax1.set_title('NMOS: Differenza tra metodi vs Temperatura')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    # PMOS differenza
    if pmos_comparison:
        pmos_comp_df['difference'] = pmos_comp_df['sqrt'] - pmos_comp_df['traditional']
        
        for chip in ['chip3', 'chip4', 'chip5']:
            chip_data = pmos_comp_df[pmos_comp_df['chip'] == chip]
            if len(chip_data) > 0:
                ax2.scatter(chip_data['temp_avg'], chip_data['difference'], 
                           color=colors_chip[chip], label=chip, alpha=0.7, s=60)
        
        ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Temperatura (K)')
        ax2.set_ylabel('Differenza dVth/dT (Sqrt - Traditional) (V/K)')
        ax2.set_title('PMOS: Differenza tra metodi vs Temperatura')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'dvth_dt_difference_vs_temp.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Salva i dati di confronto
    if nmos_comparison:
        pd.DataFrame(nmos_comparison).to_csv(os.path.join(output_dir, 'nmos_comparison_data.csv'), index=False)
    if pmos_comparison:
        pd.DataFrame(pmos_comparison).to_csv(os.path.join(output_dir, 'pmos_comparison_data.csv'), index=False)


def print_comprehensive_statistics(df_vth: pd.DataFrame, df_dvth_dt: pd.DataFrame):
    """
    Stampa statistiche complete per NMOS e PMOS.
    """
    print("\n" + "="*80)
    print("STATISTICHE COMPLETE - NMOS E PMOS")
    print("="*80)
    
    # Statistiche per device type e metodo
    print("\nStatistiche dVth/dT per device type e metodo:")
    stats = df_dvth_dt.groupby(['device_type', 'method'])['dvth_dt'].agg(['count', 'mean', 'std', 'min', 'max'])
    print(stats.round(6))
    
    # Statistiche per chip
    print("\nStatistiche dVth/dT per chip e device type:")
    chip_stats = df_dvth_dt.groupby(['chip', 'device_type', 'method'])['dvth_dt'].agg(['count', 'mean', 'std'])
    print(chip_stats.round(6))
    
    # Confronto diretto per NMOS
    nmos_dvth = df_dvth_dt[df_dvth_dt['device_type'] == 'nmos']
    nmos_comparison = []
    for (chip, device_idx, temp_avg), group in nmos_dvth.groupby(['chip', 'device_index', 'temp_avg']):
        if len(group) == 2:
            traditional = group[group['method'] == 'traditional']['dvth_dt'].iloc[0]
            sqrt = group[group['method'] == 'sqrt']['dvth_dt'].iloc[0]
            nmos_comparison.append({
                'chip': chip,
                'device_index': device_idx,
                'temp_avg': temp_avg,
                'traditional': traditional,
                'sqrt': sqrt,
                'difference': sqrt - traditional,
                'percent_diff': (sqrt - traditional) / traditional * 100 if traditional != 0 else float('inf')
            })
    
    if nmos_comparison:
        nmos_comp_df = pd.DataFrame(nmos_comparison)
        print(f"\nNMOS - Confronto diretto tra metodi:")
        print(f"Numero di confronti diretti: {len(nmos_comp_df)}")
        print(f"Differenza media: {nmos_comp_df['difference'].mean():.6f} V/K")
        print(f"Differenza percentuale media: {nmos_comp_df['percent_diff'].mean():.2f}%")
        print(f"Deviazione standard della differenza: {nmos_comp_df['difference'].std():.6f} V/K")
    
    # Confronto diretto per PMOS
    pmos_dvth = df_dvth_dt[df_dvth_dt['device_type'] == 'pmos']
    pmos_comparison = []
    for (chip, device_idx, temp_avg), group in pmos_dvth.groupby(['chip', 'device_index', 'temp_avg']):
        if len(group) == 2:
            traditional = group[group['method'] == 'traditional']['dvth_dt'].iloc[0]
            sqrt = group[group['method'] == 'sqrt']['dvth_dt'].iloc[0]
            pmos_comparison.append({
                'chip': chip,
                'device_index': device_idx,
                'temp_avg': temp_avg,
                'traditional': traditional,
                'sqrt': sqrt,
                'difference': sqrt - traditional,
                'percent_diff': (sqrt - traditional) / traditional * 100 if traditional != 0 else float('inf')
            })
    
    if pmos_comparison:
        pmos_comp_df = pd.DataFrame(pmos_comparison)
        print(f"\nPMOS - Confronto diretto tra metodi:")
        print(f"Numero di confronti diretti: {len(pmos_comp_df)}")
        print(f"Differenza media: {pmos_comp_df['difference'].mean():.6f} V/K")
        print(f"Differenza percentuale media: {pmos_comp_df['percent_diff'].mean():.2f}%")
        print(f"Deviazione standard della differenza: {pmos_comp_df['difference'].std():.6f} V/K")


def main():
    """
    Funzione principale per eseguire l'analisi completa.
    """
    # Directory root dei dati
    root_dir = "."  # Assumiamo che lo script sia eseguito dalla directory root
    
    print("Analisi completa dVth/dT per NMOS e PMOS")
    print("="*50)
    print("Configurazione:")
    print("- NMOS: Vds=0.1V (traditional) vs Vds=1.2V (sqrt)")
    print("- PMOS: Vds=1.1V (traditional) vs Vds=0.1V (sqrt)")
    print("="*50)
    
    print("\nEstrazione Vth per tutti i device...")
    df_vth = extract_vth_for_comparison_all_devices(root_dir)
    
    if df_vth.empty:
        print("Nessun dato trovato!")
        return
    
    print(f"Trovati {len(df_vth)} punti dati")
    print(f"Distribuzione per device type:")
    print(df_vth['device_type'].value_counts())
    print(f"Distribuzione per metodo:")
    print(df_vth['method'].value_counts())
    
    # Salva i dati Vth
    df_vth.to_csv('vth_comparison_all_devices.csv', index=False)
    print("Dati Vth salvati in vth_comparison_all_devices.csv")
    
    # Calcola dVth/dT
    print("\nCalcolo dVth/dT...")
    df_dvth_dt = calculate_dvth_dt(df_vth)
    
    if df_dvth_dt.empty:
        print("Nessun dato dVth/dT calcolato!")
        return
    
    print(f"Calcolati {len(df_dvth_dt)} punti dVth/dT")
    
    # Salva i dati dVth/dT
    df_dvth_dt.to_csv('dvth_dt_all_devices.csv', index=False)
    print("Dati dVth/dT salvati in dvth_dt_all_devices.csv")
    
    # Crea grafici
    print("\nCreazione grafici per discussione...")
    create_comprehensive_plots(df_vth, df_dvth_dt, 'comprehensive_plots')
    print("Grafici salvati in directory comprehensive_plots/")
    
    # Statistiche riassuntive
    print_comprehensive_statistics(df_vth, df_dvth_dt)
    
    # Salva riepilogo confronto
    print("\nSalvataggio riepilogo confronto...")
    save_comparison_summary(df_dvth_dt, 'comprehensive_plots')
    print("Riepilogo salvato in comprehensive_plots/")


def save_comparison_summary(df_dvth_dt: pd.DataFrame, output_dir: str):
    """
    Salva un riepilogo del confronto per NMOS e PMOS.
    """
    summary_data = []
    
    for device_type in ['nmos', 'pmos']:
        device_data = df_dvth_dt[df_dvth_dt['device_type'] == device_type]
        
        for (chip, device_idx, temp_avg), group in device_data.groupby(['chip', 'device_index', 'temp_avg']):
            if len(group) == 2:
                traditional = group[group['method'] == 'traditional']['dvth_dt'].iloc[0]
                sqrt = group[group['method'] == 'sqrt']['dvth_dt'].iloc[0]
                diff = sqrt - traditional
                percent_diff = (diff / traditional) * 100 if traditional != 0 else float('inf')
                
                summary_data.append({
                    'device_type': device_type.upper(),
                    'chip': chip,
                    'device_index': device_idx,
                    'temp_avg': temp_avg,
                    'traditional': traditional,
                    'sqrt': sqrt,
                    'difference': diff,
                    'percent_diff': percent_diff
                })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(os.path.join(output_dir, 'comprehensive_comparison_summary.csv'), index=False)
        
        # Statistiche per device type
        device_stats = summary_df.groupby('device_type').agg({
            'difference': ['count', 'mean', 'std'],
            'percent_diff': ['mean', 'std']
        }).round(6)
        device_stats.to_csv(os.path.join(output_dir, 'device_type_statistics.csv'))


if __name__ == "__main__":
    main()


