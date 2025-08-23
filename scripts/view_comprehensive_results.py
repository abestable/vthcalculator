#!/usr/bin/env python3
"""
Script interattivo per visualizzare i risultati completi del confronto dVth/dT per NMOS e PMOS.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def load_comprehensive_results():
    """
    Carica i risultati dell'analisi completa.
    """
    
    # Verifica che i file esistano
    files_to_check = [
        'vth_comparison_all_devices.csv',
        'dvth_dt_all_devices.csv', 
        'comprehensive_comparison_summary.csv'
    ]
    
    missing_files = [f for f in files_to_check if not os.path.exists(f)]
    if missing_files:
        print(f"File mancanti: {missing_files}")
        print("Esegui prima lo script compare_dvth_dt_all_devices.py")
        return None, None, None
    
    # Carica i dati
    print("Caricamento dati completi...")
    df_vth = pd.read_csv('vth_comparison_all_devices.csv')
    df_dvth_dt = pd.read_csv('dvth_dt_all_devices.csv')
    df_comparison = pd.read_csv('comprehensive_comparison_summary.csv')
    
    print(f"Dati caricati:")
    print(f"- Vth data: {len(df_vth)} righe")
    print(f"- dVth/dT data: {len(df_dvth_dt)} righe")
    print(f"- Comparison data: {len(df_comparison)} righe")
    
    return df_vth, df_dvth_dt, df_comparison

def plot_device_overview(df_vth, df_dvth_dt):
    """
    Grafico overview completo per NMOS e PMOS.
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Converti temperature in numeri
    df_vth['temp_k'] = df_vth['temperature'].str.replace('K', '').astype(float)
    
    # Colori e marker per i metodi
    colors = {'traditional': 'blue', 'sqrt': 'red'}
    markers = {'traditional': 'o', 'sqrt': 's'}
    
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
    plt.show()

def plot_scatter_comparison(df_dvth_dt):
    """
    Scatter plot confronto metodi per NMOS e PMOS.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS scatter
    nmos_dvth = df_dvth_dt[df_dvth_dt['device_type'] == 'nmos']
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
    pmos_dvth = df_dvth_dt[df_dvth_dt['device_type'] == 'pmos']
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
    plt.show()

def plot_boxplot_comparison(df_dvth_dt):
    """
    Boxplot confronto distribuzioni per NMOS e PMOS.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS boxplot
    nmos_dvth = df_dvth_dt[df_dvth_dt['device_type'] == 'nmos']
    nmos_traditional = nmos_dvth[nmos_dvth['method'] == 'traditional']['dvth_dt']
    nmos_sqrt = nmos_dvth[nmos_dvth['method'] == 'sqrt']['dvth_dt']
    
    ax1.boxplot([nmos_traditional, nmos_sqrt], 
                labels=['Traditional\n(Vds=0.1V)', 'Sqrt\n(Vds=1.2V)'])
    ax1.set_ylabel('dVth/dT (V/K)')
    ax1.set_title('NMOS: Distribuzione dVth/dT per metodo')
    ax1.grid(True, alpha=0.3)
    
    # PMOS boxplot
    pmos_dvth = df_dvth_dt[df_dvth_dt['device_type'] == 'pmos']
    pmos_traditional = pmos_dvth[pmos_dvth['method'] == 'traditional']['dvth_dt']
    pmos_sqrt = pmos_dvth[pmos_dvth['method'] == 'sqrt']['dvth_dt']
    
    ax2.boxplot([pmos_traditional, pmos_sqrt], 
                labels=['Traditional\n(Vds=1.1V)', 'Sqrt\n(Vds=0.1V)'])
    ax2.set_ylabel('dVth/dT (V/K)')
    ax2.set_title('PMOS: Distribuzione dVth/dT per metodo')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def plot_difference_vs_temperature(df_dvth_dt):
    """
    Grafico differenza vs temperatura per NMOS e PMOS.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS differenza
    nmos_dvth = df_dvth_dt[df_dvth_dt['device_type'] == 'nmos']
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
    pmos_dvth = df_dvth_dt[df_dvth_dt['device_type'] == 'pmos']
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
    plt.show()

def print_comprehensive_statistics(df_vth, df_dvth_dt, df_comparison):
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
    nmos_data = df_comparison[df_comparison['device_type'] == 'NMOS']
    if len(nmos_data) > 0:
        print(f"\nNMOS - Confronto diretto tra metodi:")
        print(f"Numero di confronti diretti: {len(nmos_data)}")
        print(f"Differenza media: {nmos_data['difference'].mean():.6f} V/K")
        print(f"Differenza percentuale media: {nmos_data['percent_diff'].mean():.2f}%")
        print(f"Deviazione standard della differenza: {nmos_data['difference'].std():.6f} V/K")
    
    # Confronto diretto per PMOS
    pmos_data = df_comparison[df_comparison['device_type'] == 'PMOS']
    if len(pmos_data) > 0:
        print(f"\nPMOS - Confronto diretto tra metodi:")
        print(f"Numero di confronti diretti: {len(pmos_data)}")
        print(f"Differenza media: {pmos_data['difference'].mean():.6f} V/K")
        print(f"Differenza percentuale media: {pmos_data['percent_diff'].mean():.2f}%")
        print(f"Deviazione standard della differenza: {pmos_data['difference'].std():.6f} V/K")

def interactive_menu():
    """
    Menu interattivo per visualizzare i risultati.
    """
    results = load_comprehensive_results()
    if results[0] is None:
        return
    
    df_vth, df_dvth_dt, df_comparison = results
    
    while True:
        print("\n" + "="*60)
        print("MENU VISUALIZZAZIONE RISULTATI COMPLETI")
        print("="*60)
        print("1. Overview Completo (Vth + dVth/dT per NMOS e PMOS)")
        print("2. Scatter Plot Confronto Metodi")
        print("3. Boxplot Distribuzioni")
        print("4. Differenza vs Temperatura")
        print("5. Statistiche Complete")
        print("6. Tutti i Grafici")
        print("0. Esci")
        
        choice = input("\nScegli un'opzione (0-6): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            plot_device_overview(df_vth, df_dvth_dt)
        elif choice == '2':
            plot_scatter_comparison(df_dvth_dt)
        elif choice == '3':
            plot_boxplot_comparison(df_dvth_dt)
        elif choice == '4':
            plot_difference_vs_temperature(df_dvth_dt)
        elif choice == '5':
            print_comprehensive_statistics(df_vth, df_dvth_dt, df_comparison)
        elif choice == '6':
            plot_device_overview(df_vth, df_dvth_dt)
            plot_scatter_comparison(df_dvth_dt)
            plot_boxplot_comparison(df_dvth_dt)
            plot_difference_vs_temperature(df_dvth_dt)
            print_comprehensive_statistics(df_vth, df_dvth_dt, df_comparison)
        else:
            print("Opzione non valida!")

def main():
    """
    Funzione principale.
    """
    print("Visualizzatore Risultati Completi - NMOS e PMOS")
    print("="*60)
    print("Configurazione:")
    print("- NMOS: Vds=0.1V (traditional) vs Vds=1.2V (sqrt)")
    print("- PMOS: Vds=1.1V (traditional) vs Vds=0.1V (sqrt)")
    print("="*60)
    
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\nInterruzione da tastiera. Uscita...")
    except Exception as e:
        print(f"\nErrore: {e}")
        print("Assicurati di aver eseguito prima lo script compare_dvth_dt_all_devices.py")

if __name__ == "__main__":
    main()


