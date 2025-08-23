#!/usr/bin/env python3
"""
Script per visualizzare i risultati del confronto dVth/dT in modo interattivo.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def load_and_display_results():
    """
    Carica e visualizza i risultati del confronto dVth/dT.
    """
    
    # Verifica che i file esistano
    files_to_check = [
        'vth_comparison_data.csv',
        'dvth_dt_data.csv', 
        'dvth_dt_comparison_summary.csv'
    ]
    
    missing_files = [f for f in files_to_check if not os.path.exists(f)]
    if missing_files:
        print(f"File mancanti: {missing_files}")
        print("Esegui prima lo script compare_dvth_dt_methods.py")
        return
    
    # Carica i dati
    print("Caricamento dati...")
    df_vth = pd.read_csv('vth_comparison_data.csv')
    df_dvth_dt = pd.read_csv('dvth_dt_data.csv')
    df_comparison = pd.read_csv('dvth_dt_comparison_summary.csv')
    
    print(f"Dati caricati:")
    print(f"- Vth data: {len(df_vth)} righe")
    print(f"- dVth/dT data: {len(df_dvth_dt)} righe")
    print(f"- Comparison data: {len(df_comparison)} righe")
    
    return df_vth, df_dvth_dt, df_comparison

def plot_vth_vs_temperature(df_vth):
    """
    Grafico Vth vs temperatura per entrambi i metodi.
    """
    plt.figure(figsize=(12, 8))
    
    # Converti temperature in numeri
    df_vth['temp_k'] = df_vth['temperature'].str.replace('K', '').astype(float)
    
    # Colori e marker per i metodi
    colors = {'traditional': 'blue', 'sqrt': 'red'}
    markers = {'traditional': 'o', 'sqrt': 's'}
    
    for (chip, device_idx), group in df_vth.groupby(['chip', 'device_index']):
        for method in ['traditional', 'sqrt']:
            method_data = group[group['method'] == method]
            if len(method_data) > 0:
                plt.plot(method_data['temp_k'], method_data['vth'], 
                        marker=markers[method], color=colors[method], 
                        label=f'{chip}_NMOS{device_idx}_{method}' if method == 'traditional' else "",
                        alpha=0.7, markersize=6)
    
    plt.xlabel('Temperatura (K)')
    plt.ylabel('Vth (V)')
    plt.title('Vth vs Temperatura: Traditional (Vds=0.1V) vs Sqrt (Vds=1.2V)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_dvth_dt_comparison(df_dvth_dt):
    """
    Grafico dVth/dT vs temperatura per entrambi i metodi.
    """
    plt.figure(figsize=(12, 8))
    
    # Colori e marker per i metodi
    colors = {'traditional': 'blue', 'sqrt': 'red'}
    markers = {'traditional': 'o', 'sqrt': 's'}
    
    for (chip, device_idx), group in df_dvth_dt.groupby(['chip', 'device_index']):
        for method in ['traditional', 'sqrt']:
            method_data = group[group['method'] == method]
            if len(method_data) > 0:
                plt.plot(method_data['temp_avg'], method_data['dvth_dt'], 
                        marker=markers[method], color=colors[method], 
                        label=f'{chip}_NMOS{device_idx}_{method}' if method == 'traditional' else "",
                        alpha=0.7, markersize=6)
    
    plt.xlabel('Temperatura (K)')
    plt.ylabel('dVth/dT (V/K)')
    plt.title('dVth/dT vs Temperatura: Traditional (Vds=0.1V) vs Sqrt (Vds=1.2V)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_scatter_comparison(df_comparison):
    """
    Scatter plot: dVth/dT traditional vs sqrt.
    """
    plt.figure(figsize=(10, 8))
    
    plt.scatter(df_comparison['traditional'], df_comparison['sqrt'], alpha=0.7, s=60)
    
    # Aggiungi etichette per i punti
    for _, row in df_comparison.iterrows():
        plt.annotate(f"{row['chip']}_NMOS{row['device_index']}\n{row['temp_avg']:.0f}K", 
                    (row['traditional'], row['sqrt']), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # Linea di identità
    min_val = min(df_comparison['traditional'].min(), df_comparison['sqrt'].min())
    max_val = max(df_comparison['traditional'].max(), df_comparison['sqrt'].max())
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='y=x')
    
    plt.xlabel('dVth/dT Traditional (V/K)')
    plt.ylabel('dVth/dT Sqrt (V/K)')
    plt.title('Confronto dVth/dT: Traditional vs Sqrt')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_difference_vs_temperature(df_comparison):
    """
    Grafico della differenza vs temperatura.
    """
    plt.figure(figsize=(12, 8))
    
    # Colori per chip
    colors = {'chip3': 'red', 'chip4': 'blue', 'chip5': 'green'}
    
    for chip in ['chip3', 'chip4', 'chip5']:
        chip_data = df_comparison[df_comparison['chip'] == chip]
        if len(chip_data) > 0:
            plt.scatter(chip_data['temp_avg'], chip_data['difference'], 
                       color=colors[chip], label=chip, alpha=0.7, s=60)
            
            # Aggiungi etichette per i device
            for _, row in chip_data.iterrows():
                plt.annotate(f"NMOS{row['device_index']}", 
                            (row['temp_avg'], row['difference']), 
                            xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    plt.xlabel('Temperatura (K)')
    plt.ylabel('Differenza dVth/dT (Sqrt - Traditional) (V/K)')
    plt.title('Differenza tra metodi vs Temperatura')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_boxplot_comparison(df_dvth_dt):
    """
    Boxplot per confrontare le distribuzioni.
    """
    plt.figure(figsize=(10, 6))
    
    traditional_data = df_dvth_dt[df_dvth_dt['method'] == 'traditional']['dvth_dt']
    sqrt_data = df_dvth_dt[df_dvth_dt['method'] == 'sqrt']['dvth_dt']
    
    plt.boxplot([traditional_data, sqrt_data], 
                labels=['Traditional (Vds=0.1V)', 'Sqrt (Vds=1.2V)'])
    plt.ylabel('dVth/dT (V/K)')
    plt.title('Distribuzione dVth/dT per metodo')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def print_statistics(df_vth, df_dvth_dt, df_comparison):
    """
    Stampa statistiche riassuntive.
    """
    print("\n" + "="*60)
    print("STATISTICHE RIASSUNTIVE")
    print("="*60)
    
    # Statistiche per metodo
    print("\nStatistiche dVth/dT per metodo:")
    stats = df_dvth_dt.groupby('method')['dvth_dt'].agg(['count', 'mean', 'std', 'min', 'max'])
    print(stats.round(6))
    
    # Statistiche per chip
    print("\nStatistiche dVth/dT per chip:")
    chip_stats = df_dvth_dt.groupby(['chip', 'method'])['dvth_dt'].agg(['count', 'mean', 'std'])
    print(chip_stats.round(6))
    
    # Confronto diretto
    print(f"\nConfronto diretto tra metodi:")
    print(f"Numero di confronti diretti: {len(df_comparison)}")
    print(f"Differenza media: {df_comparison['difference'].mean():.6f} V/K")
    print(f"Differenza percentuale media: {df_comparison['percent_diff'].mean():.2f}%")
    print(f"Deviazione standard della differenza: {df_comparison['difference'].std():.6f} V/K")
    
    # Statistiche per device
    print("\nStatistiche per device (confronto diretto):")
    device_stats = df_comparison.groupby(['chip', 'device_index'])['difference'].agg(['count', 'mean', 'std'])
    print(device_stats.round(6))

def interactive_menu():
    """
    Menu interattivo per visualizzare i risultati.
    """
    df_vth, df_dvth_dt, df_comparison = load_and_display_results()
    
    while True:
        print("\n" + "="*50)
        print("MENU VISUALIZZAZIONE RISULTATI dVth/dT")
        print("="*50)
        print("1. Vth vs Temperatura")
        print("2. dVth/dT vs Temperatura")
        print("3. Scatter plot: Traditional vs Sqrt")
        print("4. Differenza vs Temperatura")
        print("5. Boxplot delle distribuzioni")
        print("6. Statistiche riassuntive")
        print("7. Tutti i grafici")
        print("0. Esci")
        
        choice = input("\nScegli un'opzione (0-7): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            plot_vth_vs_temperature(df_vth)
        elif choice == '2':
            plot_dvth_dt_comparison(df_dvth_dt)
        elif choice == '3':
            plot_scatter_comparison(df_comparison)
        elif choice == '4':
            plot_difference_vs_temperature(df_comparison)
        elif choice == '5':
            plot_boxplot_comparison(df_dvth_dt)
        elif choice == '6':
            print_statistics(df_vth, df_dvth_dt, df_comparison)
        elif choice == '7':
            plot_vth_vs_temperature(df_vth)
            plot_dvth_dt_comparison(df_dvth_dt)
            plot_scatter_comparison(df_comparison)
            plot_difference_vs_temperature(df_comparison)
            plot_boxplot_comparison(df_dvth_dt)
            print_statistics(df_vth, df_dvth_dt, df_comparison)
        else:
            print("Opzione non valida!")

def main():
    """
    Funzione principale.
    """
    print("Visualizzatore Risultati Confronto dVth/dT")
    print("="*50)
    
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\nInterruzione da tastiera. Uscita...")
    except Exception as e:
        print(f"\nErrore: {e}")
        print("Assicurati di aver eseguito prima lo script compare_dvth_dt_methods.py")

if __name__ == "__main__":
    main()


