#!/usr/bin/env python3
"""
Script per calcolare la derivata direttamente sui valori medi del CSV.
Applica np.gradient() sui dati aggregati per dispositivo.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_derivative_on_averages():
    """Calcola la derivata sui valori medi per ogni dispositivo."""
    
    # Leggi i dati
    df = pd.read_csv("vth_by_chip.csv")
    df['temp_numeric'] = df['temperature'].str.replace('K', '').astype(float)
    
    # Raggruppa per device_label
    devices = df['device_label'].unique()
    
    print("=== CALCOLO DERIVATA SUI VALORI MEDI ===")
    print("Applicando np.gradient() direttamente sui dati aggregati:")
    print()
    
    # Crea grafici separati per PMOS e NMOS
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    
    # PMOS
    pmos_devices = [d for d in devices if d.startswith('pmos')]
    print("=== PMOS ===")
    
    for i, device in enumerate(pmos_devices):
        device_data = df[df['device_label'] == device].copy()
        device_data = device_data.sort_values('temp_numeric')
        
        temps = device_data['temp_numeric'].values
        avg_vth = device_data['avg_vth_V'].values
        
        # CALCOLO DIRETTO DELLA DERIVATA SUI VALORI MEDI
        dVth_dT = np.gradient(avg_vth, temps)
        
        print(f"\n{device}:")
        print("T(K) | avg_Vth(V) | dVth/dT (V/K)")
        print("-" * 35)
        for j in range(len(temps)):
            print(f"{temps[j]:4.0f} | {avg_vth[j]:9.3f} | {dVth_dT[j]:12.6f}")
        
        # Plot
        color = colors[i % len(colors)]
        ax1.plot(temps, dVth_dT, 'o-', color=color, linewidth=2, markersize=6, label=device)
    
    ax1.set_xlabel('Temperatura (K)', fontsize=12)
    ax1.set_ylabel('dVth/dT (V/K)', fontsize=12)
    ax1.set_title('Derivata Vth vs Temperatura - PMOS (valori medi)', fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # NMOS
    nmos_devices = [d for d in devices if d.startswith('nmos')]
    print("\n=== NMOS ===")
    
    for i, device in enumerate(nmos_devices):
        device_data = df[df['device_label'] == device].copy()
        device_data = device_data.sort_values('temp_numeric')
        
        temps = device_data['temp_numeric'].values
        avg_vth = device_data['avg_vth_V'].values
        
        # CALCOLO DIRETTO DELLA DERIVATA SUI VALORI MEDI
        dVth_dT = np.gradient(avg_vth, temps)
        
        print(f"\n{device}:")
        print("T(K) | avg_Vth(V) | dVth/dT (V/K)")
        print("-" * 35)
        for j in range(len(temps)):
            print(f"{temps[j]:4.0f} | {avg_vth[j]:9.3f} | {dVth_dT[j]:12.6f}")
        
        # Plot
        color = colors[i % len(colors)]
        ax2.plot(temps, dVth_dT, 'o-', color=color, linewidth=2, markersize=6, label=device)
    
    ax2.set_xlabel('Temperatura (K)', fontsize=12)
    ax2.set_ylabel('dVth/dT (V/K)', fontsize=12)
    ax2.set_title('Derivata Vth vs Temperatura - NMOS (valori medi)', fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('derivative_on_avg_values.pdf', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nGrafico salvato in: derivative_on_avg_values.pdf")
    
    # Salva anche i risultati in CSV
    results = []
    for device in devices:
        device_data = df[df['device_label'] == device].copy()
        device_data = device_data.sort_values('temp_numeric')
        
        temps = device_data['temp_numeric'].values
        avg_vth = device_data['avg_vth_V'].values
        dVth_dT = np.gradient(avg_vth, temps)
        
        for i in range(len(temps)):
            results.append({
                'device_label': device,
                'temperature': temps[i],
                'avg_vth_V': avg_vth[i],
                'derivative_V_per_K': dVth_dT[i]
            })
    
    results_df = pd.DataFrame(results)
    results_df.to_csv('derivative_results.csv', index=False)
    print(f"Risultati salvati in: derivative_results.csv")
    
    return results_df

def show_simple_command():
    """Mostra il comando semplice per calcolare la derivata."""
    
    print("\n=== COMANDO SEMPLICE PER CALCOLARE LA DERIVATA ===")
    print("Per qualsiasi dispositivo, usa questo comando:")
    print()
    print("import pandas as pd")
    print("import numpy as np")
    print()
    print("# Leggi i dati")
    print("df = pd.read_csv('vth_by_chip.csv')")
    print("df['temp_numeric'] = df['temperature'].str.replace('K', '').astype(float)")
    print()
    print("# Filtra il dispositivo")
    print("device_data = df[df['device_label'] == 'pmos1'].sort_values('temp_numeric')")
    print()
    print("# Estrai vettori")
    print("temps = device_data['temp_numeric'].values")
    print("avg_vth = device_data['avg_vth_V'].values")
    print()
    print("# CALCOLA LA DERIVATA (comando principale!)")
    print("dVth_dT = np.gradient(avg_vth, temps)")
    print()
    print("# Risultato: dVth_dT contiene la derivata per ogni punto!")

if __name__ == "__main__":
    results_df = calculate_derivative_on_averages()
    show_simple_command()
