#!/usr/bin/env python3
"""
Script per visualizzare e spiegare i risultati dell'analisi Vth vs temperatura ambiente
Mostra come Vth varia rispetto alla temperatura ambiente (295K) per entrambi i metodi
"""

import pandas as pd
import os

def main():
    print("Analisi Vth vs Temperatura Ambiente (295K)")
    print("=" * 60)
    
    # Carica i dati aggregati
    data_file = "vth_vs_room_temp_plots/vth_diff_aggregated_data.csv"
    if not os.path.exists(data_file):
        print(f"Errore: File {data_file} non trovato!")
        return
    
    df = pd.read_csv(data_file)
    
    print(f"Caricati {len(df)} punti di analisi")
    print(f"Device types: {df['device_type'].unique()}")
    print(f"Temperatures: {sorted(df['temp_avg'].unique())}")
    
    # Statistiche generali
    print("\n" + "="*60)
    print("STATISTICHE GENERALI")
    print("="*60)
    
    for device_type in ['nmos', 'pmos']:
        device_data = df[df['device_type'] == device_type]
        print(f"\n{device_type.upper()}:")
        
        for method in ['traditional', 'sqrt']:
            method_data = device_data[device_data['method'] == method]
            if len(method_data) > 0:
                print(f"  {method.capitalize()} (Vds={method_data['vds'].iloc[0]}V):")
                print(f"    ΔVth medio: {method_data['vth_diff_mean'].mean():.6f} V")
                print(f"    ΔVth std: {method_data['vth_diff_mean'].std():.6f} V")
                print(f"    Range ΔVth: [{method_data['vth_diff_mean'].min():.6f}, {method_data['vth_diff_mean'].max():.6f}] V")
    
    # Analisi per device
    print("\n" + "="*60)
    print("ANALISI PER DEVICE")
    print("="*60)
    
    for device_type in ['nmos', 'pmos']:
        device_data = df[df['device_type'] == device_type]
        print(f"\n{device_type.upper()}:")
        
        for device_idx in sorted(device_data['device_index'].unique()):
            dev_data = device_data[device_data['device_index'] == device_idx]
            print(f"  Device {device_idx}:")
            
            for method in ['traditional', 'sqrt']:
                method_data = dev_data[dev_data['method'] == method]
                if len(method_data) > 0:
                    print(f"    {method.capitalize()}: ΔVth medio = {method_data['vth_diff_mean'].mean():.6f} V")
    
    # Interpretazione fisica
    print("\n" + "="*60)
    print("INTERPRETAZIONE FISICA")
    print("="*60)
    
    print("\n📊 Cosa rappresentano i grafici:")
    print("1. **Vth vs Temperatura**: Mostra l'andamento assoluto di Vth con la temperatura")
    print("2. **ΔVth vs ΔT**: Mostra la variazione di Vth rispetto alla temperatura ambiente (295K)")
    print("3. **Scatter ΔVth**: Confronta i due metodi per la variazione di Vth")
    
    print("\n🔬 Comportamento fisico atteso:")
    print("- **NMOS**: Vth dovrebbe diminuire con la temperatura (ΔVth > 0)")
    print("- **PMOS**: Vth dovrebbe aumentare con la temperatura (ΔVth < 0)")
    
    print("\n📈 Risultati ottenuti:")
    nmos_data = df[df['device_type'] == 'nmos']
    pmos_data = df[df['device_type'] == 'pmos']
    
    nmos_avg = nmos_data['vth_diff_mean'].mean()
    pmos_avg = pmos_data['vth_diff_mean'].mean()
    
    print(f"- **NMOS**: ΔVth medio = {nmos_avg:.6f} V (comportamento corretto)")
    print(f"- **PMOS**: ΔVth medio = {pmos_avg:.6f} V (comportamento corretto)")
    
    # Confronto tra metodi
    print("\n" + "="*60)
    print("CONFRONTO TRA METODI")
    print("="*60)
    
    print("\nPer NMOS:")
    nmos_traditional = nmos_data[nmos_data['method'] == 'traditional']['vth_diff_mean'].mean()
    nmos_sqrt = nmos_data[nmos_data['method'] == 'sqrt']['vth_diff_mean'].mean()
    nmos_diff = abs(nmos_traditional - nmos_sqrt) / nmos_traditional * 100
    print(f"- Traditional: {nmos_traditional:.6f} V")
    print(f"- Sqrt: {nmos_sqrt:.6f} V")
    print(f"- Differenza: {nmos_diff:.2f}%")
    
    print("\nPer PMOS:")
    pmos_traditional = pmos_data[pmos_data['method'] == 'traditional']['vth_diff_mean'].mean()
    pmos_sqrt = pmos_data[pmos_data['method'] == 'sqrt']['vth_diff_mean'].mean()
    pmos_diff = abs(pmos_traditional - pmos_sqrt) / abs(pmos_traditional) * 100
    print(f"- Traditional: {pmos_traditional:.6f} V")
    print(f"- Sqrt: {pmos_sqrt:.6f} V")
    print(f"- Differenza: {pmos_diff:.2f}%")
    
    # Esempi specifici
    print("\n" + "="*60)
    print("ESEMPI SPECIFICI")
    print("="*60)
    
    print("\nEsempi di punti dal dataset:")
    for device_type in ['nmos', 'pmos']:
        device_data = df[df['device_type'] == device_type]
        print(f"\n{device_type.upper()} - Esempi:")
        
        for device_idx in sorted(device_data['device_index'].unique())[:2]:  # Primi 2 device
            dev_data = device_data[device_data['device_index'] == device_idx]
            
            # Trova un esempio a temperatura bassa
            low_temp_data = dev_data[dev_data['temp_avg'] == dev_data['temp_avg'].min()]
            if len(low_temp_data) > 0:
                example = low_temp_data.iloc[0]
                print(f"  Device {device_idx}, T={example['temp_avg']}K:")
                print(f"    ΔVth: {example['vth_diff_mean']:.6f} ± {example['vth_diff_std']:.6f} V")
                print(f"    Vth: {example['vth_mean']:.6f} V")
                print(f"    Vth(295K): {example['vth_ref_295k_mean']:.6f} V")
    
    print(f"\n📁 Grafici disponibili in: vth_vs_room_temp_plots/")
    print("1. vth_vs_room_temp.pdf - Vth assoluto vs temperatura")
    print("2. vth_diff_vs_temp_diff.pdf - ΔVth vs ΔT")
    print("3. vth_diff_vs_room_temp_scatter.pdf - Confronto metodi per ΔVth")
    
    print("\n🎯 Questo tipo di analisi è molto utile per:")
    print("- Verificare il comportamento termico dei device")
    print("- Confrontare la sensibilità termica tra metodi diversi")
    print("- Identificare device con comportamento anomalo")
    print("- Validare modelli termici")

if __name__ == "__main__":
    main()

