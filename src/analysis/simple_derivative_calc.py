#!/usr/bin/env python3
"""
Script semplice per calcolare la derivata della Vth rispetto alla temperatura.
Mostra il comando base e come usarlo.
"""

import pandas as pd
import numpy as np

def simple_derivative_calculation():
    """Calcolo semplice della derivata."""
    
    # COMANDO 1: Leggi i dati
    df = pd.read_csv("vth_by_chip.csv")
    
    # COMANDO 2: Converti temperatura in numeri
    df['temp_numeric'] = df['temperature'].str.replace('K', '').astype(float)
    
    # COMANDO 3: Filtra i dati che ti interessano (es. pmos1)
    pmos1_data = df[df['device_label'] == 'pmos1'].copy()
    pmos1_data = pmos1_data.sort_values('temp_numeric')
    
    # COMANDO 4: Estrai i vettori
    temps = pmos1_data['temp_numeric'].values
    vth_values = pmos1_data['avg_vth_V'].values
    
    # COMANDO 5: CALCOLA LA DERIVATA (questo è il comando principale!)
    dVth_dT = np.gradient(vth_values, temps)
    
    print("=== COMANDO PER CALCOLARE LA DERIVATA ===")
    print("import numpy as np")
    print("dVth_dT = np.gradient(vth_values, temps)")
    print()
    
    print("=== RISULTATI ===")
    print("Temperatura (K) | Vth (V) | dVth/dT (V/K)")
    print("-" * 40)
    for i in range(len(temps)):
        print(f"{temps[i]:12.0f} | {vth_values[i]:8.3f} | {dVth_dT[i]:12.6f}")
    
    return temps, vth_values, dVth_dT

def manual_derivative_example():
    """Esempio di calcolo manuale per un punto."""
    
    print("\n=== CALCOLO MANUALE PER UN PUNTO ===")
    print("Per calcolare la derivata a 140K:")
    print()
    print("1. Trova i punti adiacenti:")
    print("   T[1] = 115K, Vth[1] = -0.639V")
    print("   T[2] = 140K, Vth[2] = -0.621V")
    print("   T[3] = 185K, Vth[3] = -0.584V")
    print()
    print("2. Usa la formula delle differenze finite centrali:")
    print("   dVth/dT = (Vth[3] - Vth[1]) / (T[3] - T[1])")
    print("   dVth/dT = (-0.584 - (-0.639)) / (185 - 115)")
    print("   dVth/dT = 0.054 / 70 = 0.000778 V/K")
    print()
    print("3. Questo è esattamente quello che fa np.gradient()!")

if __name__ == "__main__":
    temps, vth_values, dVth_dT = simple_derivative_calculation()
    manual_derivative_example()
    
    print("\n=== COMANDI RAPIDI ===")
    print("Per calcolare la derivata di qualsiasi dispositivo:")
    print()
    print("1. Filtra i dati:")
    print("   device_data = df[df['device_label'] == 'pmos1']")
    print()
    print("2. Ordina per temperatura:")
    print("   device_data = device_data.sort_values('temp_numeric')")
    print()
    print("3. Estrai vettori:")
    print("   temps = device_data['temp_numeric'].values")
    print("   vth_values = device_data['avg_vth_V'].values")
    print()
    print("4. Calcola derivata:")
    print("   dVth_dT = np.gradient(vth_values, temps)")
    print()
    print("5. Risultato: dVth_dT è un array con la derivata per ogni punto!")
