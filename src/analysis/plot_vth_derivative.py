#!/usr/bin/env python3
"""
Script per calcolare e visualizzare la derivata della Vth rispetto alla temperatura.
Mostra come varia la sensibilità della tensione di soglia con la temperatura.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_vth_derivative_pmos(csv_file, output_pdf):
    """Calcola la derivata per i PMOS e genera un grafico."""
    
    # Leggi i dati dal CSV
    df = pd.read_csv(csv_file)
    
    # Converti la temperatura da stringa (es. "85K") a numeri
    df['temp_numeric'] = df['temperature'].str.replace('K', '').astype(float)
    
    # Filtra solo i PMOS
    pmos_data = df[df['device_label'].str.startswith('pmos')].copy()
    devices = pmos_data['device_label'].unique()
    
    # Crea il grafico
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    
    for i, device in enumerate(devices):
        device_data = pmos_data[pmos_data['device_label'] == device].copy()
        device_data = device_data.sort_values('temp_numeric')
        
        if len(device_data) < 2:
            continue
            
        temps = device_data['temp_numeric'].values
        vth_values = device_data['avg_vth_V'].values
        
        # Calcola la derivata numerica usando differenze finite
        if len(temps) > 1:
            dVth_dT = np.gradient(vth_values, temps)
            
            # Plot della derivata
            color = colors[i % len(colors)]
            ax.plot(temps, dVth_dT, 'o-', color=color, linewidth=2, markersize=6, 
                   label=f'{device}')
    
    ax.set_xlabel('Temperatura (K)', fontsize=14)
    ax.set_ylabel('dVth/dT (V/K)', fontsize=14)
    ax.set_title('Derivata della Tensione di Soglia rispetto alla Temperatura - PMOS', fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=12)
    
    # Aggiungi una linea orizzontale a zero per riferimento
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_pdf, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Grafico della derivata PMOS salvato in: {output_pdf}")

def calculate_vth_derivative_nmos(csv_file, output_pdf):
    """Calcola la derivata per gli NMOS e genera un grafico."""
    
    # Leggi i dati dal CSV
    df = pd.read_csv(csv_file)
    
    # Converti la temperatura da stringa (es. "85K") a numeri
    df['temp_numeric'] = df['temperature'].str.replace('K', '').astype(float)
    
    # Filtra solo gli NMOS
    nmos_data = df[df['device_label'].str.startswith('nmos')].copy()
    devices = nmos_data['device_label'].unique()
    
    # Crea il grafico
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    
    for i, device in enumerate(devices):
        device_data = nmos_data[nmos_data['device_label'] == device].copy()
        device_data = device_data.sort_values('temp_numeric')
        
        if len(device_data) < 2:
            continue
            
        temps = device_data['temp_numeric'].values
        vth_values = device_data['avg_vth_V'].values
        
        # Calcola la derivata numerica usando differenze finite
        if len(temps) > 1:
            dVth_dT = np.gradient(vth_values, temps)
            
            # Plot della derivata
            color = colors[i % len(colors)]
            ax.plot(temps, dVth_dT, 'o-', color=color, linewidth=2, markersize=6, 
                   label=f'{device}')
    
    ax.set_xlabel('Temperatura (K)', fontsize=14)
    ax.set_ylabel('dVth/dT (V/K)', fontsize=14)
    ax.set_title('Derivata della Tensione di Soglia rispetto alla Temperatura - NMOS', fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=12)
    
    # Aggiungi una linea orizzontale a zero per riferimento
    ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_pdf, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Grafico della derivata NMOS salvato in: {output_pdf}")

def calculate_vth_derivative_both_types(csv_file, output_pdf):
    """Calcola la derivata per entrambi i tipi di transistor (NMOS e PMOS)."""
    
    # Leggi i dati dal CSV
    df = pd.read_csv(csv_file)
    
    # Converti la temperatura da stringa (es. "85K") a numeri
    df['temp_numeric'] = df['temperature'].str.replace('K', '').astype(float)
    
    # Crea due subplot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    
    # PMOS
    pmos_data = df[df['device_label'].str.startswith('pmos')].copy()
    devices_pmos = pmos_data['device_label'].unique()
    
    for i, device in enumerate(devices_pmos):
        device_data = pmos_data[pmos_data['device_label'] == device].copy()
        device_data = device_data.sort_values('temp_numeric')
        
        if len(device_data) < 2:
            continue
            
        temps = device_data['temp_numeric'].values
        vth_values = device_data['avg_vth_V'].values
        
        # Calcola la derivata numerica
        if len(temps) > 1:
            dVth_dT = np.gradient(vth_values, temps)
            
            color = colors[i % len(colors)]
            ax1.plot(temps, dVth_dT, 'o-', color=color, linewidth=2, markersize=6, 
                    label=f'{device}')
    
    ax1.set_xlabel('Temperatura (K)', fontsize=12)
    ax1.set_ylabel('dVth/dT (V/K)', fontsize=12)
    ax1.set_title('Derivata Vth vs Temperatura - PMOS', fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # NMOS
    nmos_data = df[df['device_label'].str.startswith('nmos')].copy()
    devices_nmos = nmos_data['device_label'].unique()
    
    for i, device in enumerate(devices_nmos):
        device_data = nmos_data[nmos_data['device_label'] == device].copy()
        device_data = device_data.sort_values('temp_numeric')
        
        if len(device_data) < 2:
            continue
            
        temps = device_data['temp_numeric'].values
        vth_values = device_data['avg_vth_V'].values
        
        # Calcola la derivata numerica
        if len(temps) > 1:
            dVth_dT = np.gradient(vth_values, temps)
            
            color = colors[i % len(colors)]
            ax2.plot(temps, dVth_dT, 'o-', color=color, linewidth=2, markersize=6, 
                    label=f'{device}')
    
    ax2.set_xlabel('Temperatura (K)', fontsize=12)
    ax2.set_ylabel('dVth/dT (V/K)', fontsize=12)
    ax2.set_title('Derivata Vth vs Temperatura - NMOS', fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_pdf, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Grafico della derivata per entrambi i tipi salvato in: {output_pdf}")

if __name__ == "__main__":
    # Usa il file CSV generato dall'analisi principale
    csv_file = "vth_by_chip.csv"
    
    try:
        # Genera PDF separati per PMOS e NMOS
        calculate_vth_derivative_pmos(csv_file, "vth_derivative_pmos_vs_temp.pdf")
        calculate_vth_derivative_nmos(csv_file, "vth_derivative_nmos_vs_temp.pdf")
        
        # Genera anche il PDF combinato (opzionale)
        calculate_vth_derivative_both_types(csv_file, "vth_derivative_vs_temp.pdf")
        
        print("Analisi della derivata completata con successo!")
        print("File generati:")
        print("- vth_derivative_pmos_vs_temp.pdf")
        print("- vth_derivative_nmos_vs_temp.pdf") 
        print("- vth_derivative_vs_temp.pdf (combinato)")
        
    except Exception as e:
        print(f"Errore durante l'analisi: {e}")
