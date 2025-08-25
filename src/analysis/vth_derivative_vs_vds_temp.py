#!/usr/bin/env python3
"""
Script per analizzare la derivata della Vth rispetto alla temperatura al variare della Vds.
Genera un grafico 3D o a colori con temperatura, Vds e dVth/dT.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import os
import glob
from typing import Dict, List, Tuple
import argparse

def extract_vth_for_all_vds(root_dir: str, output_csv: str = "vth_all_vds.csv"):
    """
    Estrae Vth per tutte le Vds disponibili usando lo script extract_vth.py
    Esclude Vds=0 per NMOS e Vds=1.2V per PMOS
    """
    print("Extracting Vth for all available Vds...")
    
    # Usa lo script esistente con --all-vd per ottenere tutte le Vds
    cmd = f"python3 scripts/extract_vth.py {root_dir} --all-vd --out {output_csv}"
    os.system(cmd)
    
    print(f"Extraction completed. Results saved in: {output_csv}")

def calculate_derivative_vs_temp_vds(csv_file: str, device_type: str = "both"):
    """
    Calcola la derivata dVth/dT per ogni combinazione di device e Vds.
    
    Args:
        csv_file: File CSV con i risultati Vth
        device_type: "nmos", "pmos", o "both"
    
    Returns:
        DataFrame con temperature, Vds, device e dVth/dT
    """
    print(f"Calculating derivative for {device_type}...")
    
    # Leggi i dati
    df = pd.read_csv(csv_file)
    
    # Filtra righe con errori e righe vuote
    df = df[df['notes'].isna() | (df['notes'] == '')].copy()
    
    # Filtra righe con temperatura valida
    df = df[df['temperature'].notna() & (df['temperature'] != '')].copy()
    
    # Converti temperatura da stringa a numerico
    df['temp_numeric'] = df['temperature'].str.replace('K', '').astype(float)
    
    # Filtra per tipo di device
    if device_type == "nmos":
        df = df[df['device'].str.startswith('nmos')].copy()
    elif device_type == "pmos":
        df = df[df['device'].str.startswith('pmos')].copy()
    # else "both" - usa tutti i dati
    
    # Escludi sempre Vds=0 per NMOS e Vds=1.2 per PMOS
    nmos_data = df[df['device'].str.startswith('nmos') & (df['vd_V'] > 0.001)].copy()
    pmos_data = df[df['device'].str.startswith('pmos') & (df['vd_V'] < 1.19)].copy()
    
    # Ricombina i dati filtrati
    if device_type == "nmos":
        df = nmos_data
    elif device_type == "pmos":
        df = pmos_data
    else:  # "both"
        df = pd.concat([nmos_data, pmos_data], ignore_index=True)
    
    # Raggruppa per device e Vds
    derivative_data = []
    
    for (device, vds), group in df.groupby(['device', 'vd_V']):
        if len(group) < 2:
            continue
            
        # Ordina per temperatura
        group = group.sort_values('temp_numeric')
        
        # Rimuovi duplicati di temperatura (media dei valori)
        group_clean = group.groupby('temp_numeric').agg({
            'vth_V': 'mean',
            'device': 'first'
        }).reset_index()
        
        temps = group_clean['temp_numeric'].values
        vth_values = group_clean['vth_V'].values
        
        # Calcola derivata numerica solo se abbiamo almeno 2 temperature diverse
        if len(temps) > 1 and len(np.unique(temps)) > 1:
            try:
                dVth_dT = np.gradient(vth_values, temps)
                
                # Filtra valori infiniti o NaN
                valid_mask = np.isfinite(dVth_dT)
                
                # Aggiungi solo i punti validi
                for i, (temp, deriv) in enumerate(zip(temps, dVth_dT)):
                    if valid_mask[i]:
                        derivative_data.append({
                            'device': device,
                            'temperature': temp,
                            'vds': vds,
                            'vth': vth_values[i],
                            'dvth_dt': deriv
                        })
            except Exception as e:
                print(f"Errore nel calcolo derivata per {device} Vds={vds}: {e}")
                continue
    
    return pd.DataFrame(derivative_data)

def create_3d_plot(derivative_df: pd.DataFrame, output_pdf: str, device_type: str = "both"):
    """
    Crea un grafico 3D con temperatura, Vds e dVth/dT
    """
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Colori diversi per ogni device
    devices = derivative_df['device'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(devices)))
    
    for i, device in enumerate(devices):
        device_data = derivative_df[derivative_df['device'] == device]
        
        x = device_data['temperature'].values
        y = device_data['vds'].values
        z = device_data['dvth_dt'].values
        
        scatter = ax.scatter(x, y, z, c=[colors[i]], label=device, s=50, alpha=0.7)
    
    ax.set_xlabel('Temperature (K)', fontsize=12)
    ax.set_ylabel('Vds (V)', fontsize=12)
    ax.set_zlabel('dVth/dT (V/K)', fontsize=12)
    ax.set_title(f'Vth Derivative vs Temperature and Vds - {device_type.upper()}', fontsize=14)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_pdf, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"3D plot saved in: {output_pdf}")

def create_heatmap_plot(derivative_df: pd.DataFrame, output_pdf: str, device_type: str = "both"):
    """
    Crea un grafico a colori (heatmap) con temperatura, Vds e dVth/dT
    """
    # Crea una griglia per il heatmap
    temp_range = np.sort(derivative_df['temperature'].unique())
    vds_range = np.sort(derivative_df['vds'].unique())
    
    # Crea subplot per ogni device
    devices = derivative_df['device'].unique()
    n_devices = len(devices)
    
    if n_devices <= 3:
        cols = n_devices
        rows = 1
    else:
        cols = 3
        rows = (n_devices + 2) // 3
    
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
    if n_devices == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    for i, device in enumerate(devices):
        if i >= len(axes):
            break
            
        ax = axes[i]
        device_data = derivative_df[derivative_df['device'] == device]
        
        # Crea matrice per il heatmap
        heatmap_data = np.full((len(temp_range), len(vds_range)), np.nan)
        
        for _, row in device_data.iterrows():
            temp_idx = np.where(temp_range == row['temperature'])[0][0]
            vds_idx = np.where(vds_range == row['vds'])[0][0]
            heatmap_data[temp_idx, vds_idx] = row['dvth_dt']
        
        # Crea heatmap
        im = ax.imshow(heatmap_data, cmap='RdBu_r', aspect='auto', 
                      extent=[vds_range[0], vds_range[-1], temp_range[0], temp_range[-1]],
                      origin='lower')
        
        # Aggiungi colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('dVth/dT (V/K)', fontsize=10)
        
        # Labels
        ax.set_xlabel('Vds (V)', fontsize=10)
        ax.set_ylabel('Temperatura (K)', fontsize=10)
        ax.set_title(f'{device}', fontsize=12)
        
        # Aggiungi valori sui punti
        for temp_idx, temp in enumerate(temp_range):
            for vds_idx, vds in enumerate(vds_range):
                if not np.isnan(heatmap_data[temp_idx, vds_idx]):
                    ax.text(vds, temp, f'{heatmap_data[temp_idx, vds_idx]:.3f}', 
                           ha='center', va='center', fontsize=8, color='black')
    
    # Nascondi subplot vuoti
    for i in range(n_devices, len(axes)):
        axes[i].set_visible(False)
    
    plt.suptitle(f'Vth Derivative vs Temperature and Vds - {device_type.upper()}', fontsize=16)
    plt.tight_layout()
    plt.savefig(output_pdf, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Heatmap saved in: {output_pdf}")

def create_contour_plot(derivative_df: pd.DataFrame, output_pdf: str, device_type: str = "both"):
    """
    Crea un grafico a contorni con temperatura, Vds e dVth/dT
    """
    devices = derivative_df['device'].unique()
    n_devices = len(devices)
    
    if n_devices <= 3:
        cols = n_devices
        rows = 1
    else:
        cols = 3
        rows = (n_devices + 2) // 3
    
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
    if n_devices == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    for i, device in enumerate(devices):
        if i >= len(axes):
            break
            
        ax = axes[i]
        device_data = derivative_df[derivative_df['device'] == device]
        
        # Crea griglia per interpolazione
        temp_range = np.sort(device_data['temperature'].unique())
        vds_range = np.sort(device_data['vds'].unique())
        
        if len(temp_range) < 2 or len(vds_range) < 2:
            ax.text(0.5, 0.5, 'Dati insufficienti', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f'{device}', fontsize=12)
            continue
        
        # Crea griglia (scambia X e Y)
        X, Y = np.meshgrid(temp_range, vds_range)
        Z = np.full_like(X, np.nan)
        
        # Popola la griglia
        for _, row in device_data.iterrows():
            temp_idx = np.where(temp_range == row['temperature'])[0][0]
            vds_idx = np.where(vds_range == row['vds'])[0][0]
            Z[vds_idx, temp_idx] = row['dvth_dt']
        
        # Crea contour plot
        contour = ax.contourf(X, Y, Z, levels=20, cmap='RdBu_r')
        ax.contour(X, Y, Z, levels=10, colors='black', alpha=0.3, linewidths=0.5)
        
        # Aggiungi colorbar
        cbar = plt.colorbar(contour, ax=ax)
        cbar.set_label('dVth/dT (V/K)', fontsize=10)
        
        # Labels (scambiati)
        ax.set_xlabel('Temperature (K)', fontsize=10)
        ax.set_ylabel('Vds (V)', fontsize=10)
        ax.set_title(f'{device}', fontsize=12)
        
        # Aggiungi punti dati (scambiati)
        ax.scatter(device_data['temperature'], device_data['vds'], 
                  c='black', s=20, alpha=0.7, marker='o')
    
    # Nascondi subplot vuoti
    for i in range(n_devices, len(axes)):
        axes[i].set_visible(False)
    
    plt.suptitle(f'Vth Derivative vs Temperature and Vds - {device_type.upper()}', fontsize=16)
    plt.tight_layout()
    plt.savefig(output_pdf, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Contour plot saved in: {output_pdf}")

def main():
    parser = argparse.ArgumentParser(description="Analizza derivata Vth vs temperatura e Vds")
    parser.add_argument("root_dir", help="Directory root con i dati di misura")
    parser.add_argument("--device-type", choices=["nmos", "pmos", "both"], default="both",
                       help="Tipo di device da analizzare")
    parser.add_argument("--skip-extraction", action="store_true",
                       help="Salta l'estrazione Vth se il CSV esiste già")
    parser.add_argument("--output-prefix", default="vth_derivative_vds_temp",
                       help="Prefisso per i file di output")
    
    args = parser.parse_args()
    
    # File di output
    vth_csv = f"{args.output_prefix}_data.csv"
    derivative_csv = f"{args.output_prefix}_derivative.csv"
    
    # Estrai Vth se necessario
    if not args.skip_extraction or not os.path.exists(vth_csv):
        extract_vth_for_all_vds(args.root_dir, vth_csv)
    else:
        print(f"Using existing file: {vth_csv}")
    
    # Calcola derivata
    derivative_df = calculate_derivative_vs_temp_vds(vth_csv, args.device_type)
    
    if derivative_df.empty:
        print("No valid data found for derivative analysis")
        return
    
    # Salva dati derivata
    derivative_df.to_csv(derivative_csv, index=False)
    print(f"Derivative data saved in: {derivative_csv}")
    
    # Crea grafici
    create_3d_plot(derivative_df, f"{args.output_prefix}_3d.pdf", args.device_type)
    create_heatmap_plot(derivative_df, f"{args.output_prefix}_heatmap.pdf", args.device_type)
    create_contour_plot(derivative_df, f"{args.output_prefix}_contour.pdf", args.device_type)
    
    # Statistiche
    print("\nStatistics:")
    print(f"Number of devices: {len(derivative_df['device'].unique())}")
    print(f"Temperature range: {derivative_df['temperature'].min():.1f} - {derivative_df['temperature'].max():.1f} K")
    print(f"Vds range: {derivative_df['vds'].min():.3f} - {derivative_df['vds'].max():.3f} V")
    print(f"dVth/dT range: {derivative_df['dvth_dt'].min():.6f} - {derivative_df['dvth_dt'].max():.6f} V/K")
    
    print(f"\nGenerated files:")
    print(f"- {vth_csv}")
    print(f"- {derivative_csv}")
    print(f"- {args.output_prefix}_3d.pdf")
    print(f"- {args.output_prefix}_heatmap.pdf")
    print(f"- {args.output_prefix}_contour.pdf")

if __name__ == "__main__":
    main()
