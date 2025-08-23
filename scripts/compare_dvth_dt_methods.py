#!/usr/bin/env python3
"""
Script per confrontare i risultati di dVth/dT per tutti i device NMOS a tutte le temperature.
Confronta:
- Vds=0.1V con metodo traditional 
- Vds=1.2V con metodo sqrt
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
from typing import Dict, List, Tuple, Optional
from extract_vth import parse_measurement_file, compute_vth_linear_extrapolation, compute_vth_sqrt_method, infer_device_type_from_path, extract_temperature_from_path, infer_device_index_from_path


def extract_vth_for_comparison(root_dir: str) -> pd.DataFrame:
    """
    Estrae Vth per tutti i device NMOS a tutte le temperature usando entrambi i metodi.
    """
    results = []
    
    # Trova tutti i file NMOS
    pattern = os.path.join(root_dir, "**", "*.txt")
    files = sorted(glob(pattern, recursive=True))
    nmos_files = [f for f in files if "nmos" in f.lower() and os.path.basename(f).lower() in {"1.txt", "2.txt", "3.txt", "4.txt"}]
    
    print(f"Trovati {len(nmos_files)} file NMOS")
    
    for file_path in nmos_files:
        try:
            # Parsing del file
            blocks = parse_measurement_file(file_path)
            
            # Estrai informazioni dal path
            temperature = extract_temperature_from_path(file_path)
            device_index = infer_device_index_from_path(file_path)
            chip = re.search(r"chip\d+", file_path).group(0) if re.search(r"chip\d+", file_path) else "unknown"
            
            # Trova i blocchi per Vds=0.1V e Vds=1.2V
            vd_01_block = None
            vd_12_block = None
            
            for block in blocks:
                if abs(block.vd_volts - 0.1) < 0.01:  # Tolleranza di 10mV
                    vd_01_block = block
                elif abs(block.vd_volts - 1.2) < 0.01:  # Tolleranza di 10mV
                    vd_12_block = block
            
            # Calcola Vth per Vds=0.1V con metodo traditional
            if vd_01_block is not None:
                try:
                    vth_01, gm_max_01, idx_01 = compute_vth_linear_extrapolation(
                        vd_01_block.vg_volts, vd_01_block.id_amps, device_type="nmos"
                    )
                    if not np.isnan(vth_01):
                        results.append({
                            'file_path': file_path,
                            'chip': chip,
                            'temperature': temperature,
                            'device_index': device_index,
                            'vds': 0.1,
                            'method': 'traditional',
                            'vth': vth_01,
                            'gm_max': gm_max_01,
                            'idx': idx_01,
                            'num_points': len(vd_01_block.vg_volts)
                        })
                except Exception as e:
                    print(f"Errore nel calcolo Vth per {file_path} Vds=0.1V: {e}")
            
            # Calcola Vth per Vds=1.2V con metodo sqrt
            if vd_12_block is not None:
                try:
                    vth_12, gm_max_12, idx_12 = compute_vth_sqrt_method(
                        vd_12_block.vg_volts, vd_12_block.id_amps, device_type="nmos"
                    )
                    if not np.isnan(vth_12):
                        results.append({
                            'file_path': file_path,
                            'chip': chip,
                            'temperature': temperature,
                            'device_index': device_index,
                            'vds': 1.2,
                            'method': 'sqrt',
                            'vth': vth_12,
                            'gm_max': gm_max_12,
                            'idx': idx_12,
                            'num_points': len(vd_12_block.vg_volts)
                        })
                except Exception as e:
                    print(f"Errore nel calcolo Vth per {file_path} Vds=1.2V: {e}")
                    
        except Exception as e:
            print(f"Errore nel parsing del file {file_path}: {e}")
    
    return pd.DataFrame(results)


def calculate_dvth_dt(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcola dVth/dT per ogni device e metodo.
    """
    # Converti temperature in numeri
    df['temp_k'] = df['temperature'].str.replace('K', '').astype(float)
    
    # Raggruppa per chip, device_index e metodo
    dvth_dt_results = []
    
    for (chip, device_idx, method), group in df.groupby(['chip', 'device_index', 'method']):
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


def plot_comparison(df_dvth_dt: pd.DataFrame, output_dir: str = "."):
    """
    Crea grafici di confronto tra i due metodi.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Grafico dVth/dT vs temperatura per ogni device
    plt.figure(figsize=(12, 8))
    
    # Colori per i metodi
    colors = {'traditional': 'blue', 'sqrt': 'red'}
    markers = {'traditional': 'o', 'sqrt': 's'}
    
    for (chip, device_idx), group in df_dvth_dt.groupby(['chip', 'device_index']):
        for method in ['traditional', 'sqrt']:
            method_data = group[group['method'] == method]
            if len(method_data) > 0:
                plt.plot(method_data['temp_avg'], method_data['dvth_dt'], 
                        marker=markers[method], color=colors[method], 
                        label=f'{chip}_NMOS{device_idx}_{method}' if method == 'traditional' else "",
                        alpha=0.7)
    
    plt.xlabel('Temperatura (K)')
    plt.ylabel('dVth/dT (V/K)')
    plt.title('Confronto dVth/dT: Traditional (Vds=0.1V) vs Sqrt (Vds=1.2V)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'dvth_dt_comparison.pdf'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Grafico scatter plot: dVth/dT traditional vs sqrt
    plt.figure(figsize=(10, 8))
    
    # Raggruppa per device e temperatura media
    comparison_data = []
    for (chip, device_idx, temp_avg), group in df_dvth_dt.groupby(['chip', 'device_index', 'temp_avg']):
        if len(group) == 2:  # Deve avere entrambi i metodi
            traditional = group[group['method'] == 'traditional']['dvth_dt'].iloc[0]
            sqrt = group[group['method'] == 'sqrt']['dvth_dt'].iloc[0]
            comparison_data.append({
                'chip': chip,
                'device_index': device_idx,
                'temp_avg': temp_avg,
                'traditional': traditional,
                'sqrt': sqrt,
                'difference': sqrt - traditional
            })
    
    if comparison_data:
        comp_df = pd.DataFrame(comparison_data)
        
        plt.scatter(comp_df['traditional'], comp_df['sqrt'], alpha=0.7)
        
        # Aggiungi etichette per i punti
        for _, row in comp_df.iterrows():
            plt.annotate(f"{row['chip']}_NMOS{row['device_index']}\n{row['temp_avg']:.0f}K", 
                        (row['traditional'], row['sqrt']), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Linea di identità
        min_val = min(comp_df['traditional'].min(), comp_df['sqrt'].min())
        max_val = max(comp_df['traditional'].max(), comp_df['sqrt'].max())
        plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x')
        
        plt.xlabel('dVth/dT Traditional (V/K)')
        plt.ylabel('dVth/dT Sqrt (V/K)')
        plt.title('Confronto dVth/dT: Traditional vs Sqrt')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'dvth_dt_scatter.pdf'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Grafico della differenza vs temperatura
        plt.figure(figsize=(10, 6))
        plt.scatter(comp_df['temp_avg'], comp_df['difference'], alpha=0.7)
        
        for _, row in comp_df.iterrows():
            plt.annotate(f"{row['chip']}_NMOS{row['device_index']}", 
                        (row['temp_avg'], row['difference']), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        plt.xlabel('Temperatura (K)')
        plt.ylabel('Differenza dVth/dT (Sqrt - Traditional) (V/K)')
        plt.title('Differenza tra metodi vs Temperatura')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'dvth_dt_difference.pdf'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Salva i dati di confronto
        comp_df.to_csv(os.path.join(output_dir, 'dvth_dt_comparison_data.csv'), index=False)
    
    # 4. Grafico boxplot per confrontare le distribuzioni
    plt.figure(figsize=(10, 6))
    
    traditional_data = df_dvth_dt[df_dvth_dt['method'] == 'traditional']['dvth_dt']
    sqrt_data = df_dvth_dt[df_dvth_dt['method'] == 'sqrt']['dvth_dt']
    
    plt.boxplot([traditional_data, sqrt_data], labels=['Traditional (Vds=0.1V)', 'Sqrt (Vds=1.2V)'])
    plt.ylabel('dVth/dT (V/K)')
    plt.title('Distribuzione dVth/dT per metodo')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'dvth_dt_boxplot.pdf'), dpi=300, bbox_inches='tight')
    plt.close()


def main():
    """
    Funzione principale per eseguire l'analisi completa.
    """
    # Directory root dei dati
    root_dir = "."  # Assumiamo che lo script sia eseguito dalla directory root
    
    print("Estrazione Vth per tutti i device NMOS...")
    df_vth = extract_vth_for_comparison(root_dir)
    
    if df_vth.empty:
        print("Nessun dato trovato!")
        return
    
    print(f"Trovati {len(df_vth)} punti dati")
    print(f"Distribuzione per metodo:")
    print(df_vth['method'].value_counts())
    
    # Salva i dati Vth
    df_vth.to_csv('vth_comparison_data.csv', index=False)
    print("Dati Vth salvati in vth_comparison_data.csv")
    
    # Calcola dVth/dT
    print("Calcolo dVth/dT...")
    df_dvth_dt = calculate_dvth_dt(df_vth)
    
    if df_dvth_dt.empty:
        print("Nessun dato dVth/dT calcolato!")
        return
    
    print(f"Calcolati {len(df_dvth_dt)} punti dVth/dT")
    
    # Salva i dati dVth/dT
    df_dvth_dt.to_csv('dvth_dt_data.csv', index=False)
    print("Dati dVth/dT salvati in dvth_dt_data.csv")
    
    # Crea grafici
    print("Creazione grafici...")
    plot_comparison(df_dvth_dt, 'dvth_dt_plots')
    print("Grafici salvati in directory dvth_dt_plots/")
    
    # Statistiche riassuntive
    print("\n=== STATISTICHE RIASSUNTIVE ===")
    print("\nStatistiche per metodo:")
    stats = df_dvth_dt.groupby('method')['dvth_dt'].agg(['count', 'mean', 'std', 'min', 'max'])
    print(stats)
    
    print("\nStatistiche per chip:")
    chip_stats = df_dvth_dt.groupby(['chip', 'method'])['dvth_dt'].agg(['count', 'mean', 'std'])
    print(chip_stats)
    
    # Confronto diretto tra metodi per gli stessi device/temperature
    print("\nConfronto diretto tra metodi (dove disponibili entrambi):")
    comparison_summary = []
    for (chip, device_idx, temp_avg), group in df_dvth_dt.groupby(['chip', 'device_index', 'temp_avg']):
        if len(group) == 2:
            traditional = group[group['method'] == 'traditional']['dvth_dt'].iloc[0]
            sqrt = group[group['method'] == 'sqrt']['dvth_dt'].iloc[0]
            diff = sqrt - traditional
            comparison_summary.append({
                'chip': chip,
                'device_index': device_idx,
                'temp_avg': temp_avg,
                'traditional': traditional,
                'sqrt': sqrt,
                'difference': diff,
                'percent_diff': (diff / traditional) * 100 if traditional != 0 else float('inf')
            })
    
    if comparison_summary:
        comp_summary_df = pd.DataFrame(comparison_summary)
        print(f"\nNumero di confronti diretti: {len(comp_summary_df)}")
        print(f"Differenza media: {comp_summary_df['difference'].mean():.6f} V/K")
        print(f"Differenza percentuale media: {comp_summary_df['percent_diff'].mean():.2f}%")
        print(f"Deviazione standard della differenza: {comp_summary_df['difference'].std():.6f} V/K")
        
        comp_summary_df.to_csv('dvth_dt_comparison_summary.csv', index=False)
        print("Riepilogo confronto salvato in dvth_dt_comparison_summary.csv")


if __name__ == "__main__":
    main()
