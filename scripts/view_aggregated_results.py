#!/usr/bin/env python3
"""
Script per visualizzare i risultati dell'analisi dVth/dT aggregata.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def load_aggregated_results():
    """
    Carica i risultati dell'analisi aggregata.
    """
    
    # Verifica che i file esistano
    files_to_check = [
        'vth_aggregated_data.csv',
        'dvth_dt_aggregated_data.csv', 
        'aggregated_comparison_summary.csv'
    ]
    
    missing_files = [f for f in files_to_check if not os.path.exists(f)]
    if missing_files:
        print(f"File mancanti: {missing_files}")
        print("Esegui prima lo script compare_dvth_dt_aggregated.py")
        return None, None, None
    
    # Carica i dati
    print("Caricamento dati aggregati...")
    df_vth = pd.read_csv('vth_aggregated_data.csv')
    df_aggregated = pd.read_csv('dvth_dt_aggregated_data.csv')
    df_comparison = pd.read_csv('aggregated_comparison_summary.csv')
    
    print(f"Dati caricati:")
    print(f"- Vth data: {len(df_vth)} righe")
    print(f"- Aggregated data: {len(df_aggregated)} righe")
    print(f"- Comparison data: {len(df_comparison)} righe")
    
    return df_vth, df_aggregated, df_comparison

def plot_aggregated_vs_temperature(df_aggregated):
    """
    Grafico dVth/dT vs temperatura con error bars.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Colori per i metodi
    colors = {'traditional': 'blue', 'sqrt': 'red'}
    markers = {'traditional': 'o', 'sqrt': 's'}
    
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
    plt.show()

def plot_aggregated_scatter(df_aggregated):
    """
    Scatter plot confronto metodi con error bars.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS scatter
    nmos_data = df_aggregated[df_aggregated['device_type'] == 'nmos']
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
        
        # Scatter plot con error bars
        ax1.errorbar(nmos_comp_df['traditional_mean'], nmos_comp_df['sqrt_mean'],
                    xerr=nmos_comp_df['traditional_std'], yerr=nmos_comp_df['sqrt_std'],
                    fmt='o', alpha=0.7, capsize=3)
        
        # Linea di identità
        min_val = min(nmos_comp_df['traditional_mean'].min(), nmos_comp_df['sqrt_mean'].min())
        max_val = max(nmos_comp_df['traditional_mean'].max(), nmos_comp_df['sqrt_mean'].max())
        ax1.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x')
        
        ax1.set_xlabel('dVth/dT Traditional (V/K)')
        ax1.set_ylabel('dVth/dT Sqrt (V/K)')
        ax1.set_title('NMOS: Confronto Metodi (Aggregato)\nVds=0.1V vs Vds=1.2V')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    # PMOS scatter
    pmos_data = df_aggregated[df_aggregated['device_type'] == 'pmos']
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
        
        # Scatter plot con error bars
        ax2.errorbar(pmos_comp_df['traditional_mean'], pmos_comp_df['sqrt_mean'],
                    xerr=pmos_comp_df['traditional_std'], yerr=pmos_comp_df['sqrt_std'],
                    fmt='o', alpha=0.7, capsize=3)
        
        # Linea di identità
        min_val = min(pmos_comp_df['traditional_mean'].min(), pmos_comp_df['sqrt_mean'].min())
        max_val = max(pmos_comp_df['traditional_mean'].max(), pmos_comp_df['sqrt_mean'].max())
        ax2.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x')
        
        ax2.set_xlabel('dVth/dT Traditional (V/K)')
        ax2.set_ylabel('dVth/dT Sqrt (V/K)')
        ax2.set_title('PMOS: Confronto Metodi (Aggregato)\nVds=1.1V vs Vds=0.0V')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def plot_aggregated_boxplot(df_aggregated):
    """
    Boxplot delle distribuzioni aggregate.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS boxplot
    nmos_data = df_aggregated[df_aggregated['device_type'] == 'nmos']
    nmos_traditional = nmos_data[nmos_data['method'] == 'traditional']['dvth_dt_mean']
    nmos_sqrt = nmos_data[nmos_data['method'] == 'sqrt']['dvth_dt_mean']
    
    ax1.boxplot([nmos_traditional, nmos_sqrt], 
                labels=['Traditional\n(Vds=0.1V)', 'Sqrt\n(Vds=1.2V)'])
    ax1.set_ylabel('dVth/dT (V/K)')
    ax1.set_title('NMOS: Distribuzione dVth/dT (Aggregato)')
    ax1.grid(True, alpha=0.3)
    
    # PMOS boxplot
    pmos_data = df_aggregated[df_aggregated['device_type'] == 'pmos']
    pmos_traditional = pmos_data[pmos_data['method'] == 'traditional']['dvth_dt_mean']
    pmos_sqrt = pmos_data[pmos_data['method'] == 'sqrt']['dvth_dt_mean']
    
    ax2.boxplot([pmos_traditional, pmos_sqrt], 
                labels=['Traditional\n(Vds=1.1V)', 'Sqrt\n(Vds=0.0V)'])
    ax2.set_ylabel('dVth/dT (V/K)')
    ax2.set_title('PMOS: Distribuzione dVth/dT (Aggregato)')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def plot_aggregated_difference(df_aggregated):
    """
    Grafico differenza vs temperatura con error bars.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # NMOS differenza
    nmos_data = df_aggregated[df_aggregated['device_type'] == 'nmos']
    nmos_comparison = []
    for (device_idx, temp_avg), group in nmos_data.groupby(['device_index', 'temp_avg']):
        if len(group) == 2:
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
    pmos_data = df_aggregated[df_aggregated['device_type'] == 'pmos']
    pmos_comparison = []
    for (device_idx, temp_avg), group in pmos_data.groupby(['device_index', 'temp_avg']):
        if len(group) == 2:
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
    plt.show()

def print_aggregated_statistics(df_vth, df_aggregated, df_comparison):
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
    nmos_data = df_comparison[df_comparison['device_type'] == 'NMOS']
    if len(nmos_data) > 0:
        print(f"\nNMOS - Confronto diretto tra metodi (aggregato):")
        print(f"Numero di confronti diretti: {len(nmos_data)}")
        print(f"Differenza media: {nmos_data['difference'].mean():.6f} V/K")
        print(f"Differenza percentuale media: {nmos_data['percent_diff'].mean():.2f}%")
        print(f"Deviazione standard della differenza: {nmos_data['difference'].std():.6f} V/K")
    
    # Confronto diretto per PMOS
    pmos_data = df_comparison[df_comparison['device_type'] == 'PMOS']
    if len(pmos_data) > 0:
        print(f"\nPMOS - Confronto diretto tra metodi (aggregato):")
        print(f"Numero di confronti diretti: {len(pmos_data)}")
        print(f"Differenza media: {pmos_data['difference'].mean():.6f} V/K")
        print(f"Differenza percentuale media: {pmos_data['percent_diff'].mean():.2f}%")
        print(f"Deviazione standard della differenza: {pmos_data['difference'].std():.6f} V/K")

def interactive_menu():
    """
    Menu interattivo per visualizzare i risultati.
    """
    results = load_aggregated_results()
    if results[0] is None:
        return
    
    df_vth, df_aggregated, df_comparison = results
    
    while True:
        print("\n" + "="*60)
        print("MENU VISUALIZZAZIONE RISULTATI AGGREGATI")
        print("="*60)
        print("1. dVth/dT vs Temperatura (con error bars)")
        print("2. Scatter Plot Confronto Metodi (con error bars)")
        print("3. Boxplot Distribuzioni Aggregate")
        print("4. Differenza vs Temperatura (con error bars)")
        print("5. Statistiche Aggregate")
        print("6. Tutti i Grafici")
        print("0. Esci")
        
        choice = input("\nScegli un'opzione (0-6): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            plot_aggregated_vs_temperature(df_aggregated)
        elif choice == '2':
            plot_aggregated_scatter(df_aggregated)
        elif choice == '3':
            plot_aggregated_boxplot(df_aggregated)
        elif choice == '4':
            plot_aggregated_difference(df_aggregated)
        elif choice == '5':
            print_aggregated_statistics(df_vth, df_aggregated, df_comparison)
        elif choice == '6':
            plot_aggregated_vs_temperature(df_aggregated)
            plot_aggregated_scatter(df_aggregated)
            plot_aggregated_boxplot(df_aggregated)
            plot_aggregated_difference(df_aggregated)
            print_aggregated_statistics(df_vth, df_aggregated, df_comparison)
        else:
            print("Opzione non valida!")

def main():
    """
    Funzione principale.
    """
    print("Visualizzatore Risultati Aggregati - NMOS e PMOS")
    print("="*60)
    print("Configurazione CORRETTA:")
    print("- NMOS: Vds=0.1V (traditional) vs Vds=1.2V (sqrt)")
    print("- PMOS: Vds=1.1V (traditional) vs Vds=0.0V (sqrt)")
    print("="*60)
    
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\nInterruzione da tastiera. Uscita...")
    except Exception as e:
        print(f"\nErrore: {e}")
        print("Assicurati di aver eseguito prima lo script compare_dvth_dt_aggregated.py")

if __name__ == "__main__":
    main()

