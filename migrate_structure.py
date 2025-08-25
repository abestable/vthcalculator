#!/usr/bin/env python3
"""
Script per migrare la struttura del progetto VthCalculator alla nuova organizzazione.
Questo script crea la nuova struttura di cartelle e sposta i file esistenti.
"""

import os
import shutil
import glob
from pathlib import Path

def create_directory_structure():
    """Crea la nuova struttura di cartelle."""
    directories = [
        # Sorgente
        "src",
        "src/core",
        "src/gui", 
        "src/analysis",
        
        # Dati
        "data",
        "data/raw",
        "data/reference",
        
        # Output
        "output",
        "output/vth_extraction/csv",
        "output/vth_extraction/plots", 
        "output/vth_extraction/reports",
        "output/derivative_analysis/csv",
        "output/derivative_analysis/plots",
        "output/derivative_analysis/reports", 
        "output/vds_effect/csv",
        "output/vds_effect/plots",
        "output/vds_effect/reports",
        "output/temperature_analysis/csv",
        "output/temperature_analysis/plots",
        "output/temperature_analysis/reports",
        "output/comparisons/csv",
        "output/comparisons/plots",
        "output/comparisons/reports",
        
        # Configurazione
        "config",
        "config/analysis_configs",
        
        # Test
        "tests",
        "tests/test_data",
        
        # Documentazione
        "docs",
        "docs/examples",
        "docs/images"
    ]
    
    print("Creazione della nuova struttura di cartelle...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")

def create_init_files():
    """Crea i file __init__.py necessari per i moduli Python."""
    init_files = [
        "src/__init__.py",
        "src/core/__init__.py", 
        "src/gui/__init__.py",
        "src/analysis/__init__.py",
        "tests/__init__.py"
    ]
    
    print("\nCreazione dei file __init__.py...")
    for init_file in init_files:
        Path(init_file).touch()
        print(f"  ✓ {init_file}")

def move_scripts():
    """Sposta gli script dalla cartella scripts/ a src/analysis/."""
    print("\nSpostamento degli script...")
    
    if os.path.exists("scripts"):
        for script in glob.glob("scripts/*.py"):
            dest = f"src/analysis/{os.path.basename(script)}"
            shutil.move(script, dest)
            print(f"  ✓ {script} → {dest}")
        
        # Rimuovi la cartella scripts se vuota
        if not os.listdir("scripts"):
            os.rmdir("scripts")
            print("  ✓ Cartella scripts/ rimossa (vuota)")

def move_data_files():
    """Sposta i file di dati nelle nuove posizioni."""
    print("\nSpostamento dei file di dati...")
    
    # Sposta le cartelle dei chip
    for chip_dir in ["chip3", "chip4", "chip5"]:
        if os.path.exists(chip_dir):
            dest = f"data/raw/{chip_dir}"
            shutil.move(chip_dir, dest)
            print(f"  ✓ {chip_dir} → {dest}")
    
    # Sposta DanieleResults
    if os.path.exists("DanieleResults"):
        dest = "data/raw/DanieleResults"
        shutil.move("DanieleResults", dest)
        print(f"  ✓ DanieleResults → {dest}")
    
    # Sposta RisultatiDaniele.csv
    if os.path.exists("RisultatiDaniele.csv"):
        dest = "data/reference/RisultatiDaniele.csv"
        shutil.move("RisultatiDaniele.csv", dest)
        print(f"  ✓ RisultatiDaniele.csv → {dest}")

def move_output_files():
    """Sposta i file di output nelle nuove posizioni."""
    print("\nSpostamento dei file di output...")
    
    # File CSV di output
    csv_patterns = {
        "vth_extraction": ["vth_*.csv", "vth_by_*.csv", "vth_summary.csv"],
        "derivative_analysis": ["*_derivative_*.csv", "dvth_dt_*.csv", "all_chips_*.csv"],
        "vds_effect": ["vds_effect_*.csv"],
        "temperature_analysis": ["vth_vs_room_temp_*.csv", "vth_diff_vs_*.csv"],
        "comparisons": ["vth_compare_*.csv", "vth_comparison_*.csv"]
    }
    
    for category, patterns in csv_patterns.items():
        for pattern in patterns:
            for file in glob.glob(pattern):
                if os.path.isfile(file):
                    dest = f"output/{category}/csv/{file}"
                    shutil.move(file, dest)
                    print(f"  ✓ {file} → {dest}")
    
    # File PDF (plot)
    pdf_patterns = {
        "vth_extraction": ["vth_*_vs_temp.pdf", "vth_*_vs_temp.png"],
        "derivative_analysis": ["*_derivative_*.pdf", "dvth_dt_*.pdf", "all_chips_*.pdf"],
        "vds_effect": ["vds_effect_*.pdf", "vth_diff_vs_vds_*.pdf"],
        "temperature_analysis": ["vth_vs_room_temp_*.pdf", "vth_diff_vs_*.pdf"],
        "comparisons": ["vth_compare_*.pdf", "vth_comparison_*.pdf"]
    }
    
    for category, patterns in pdf_patterns.items():
        for pattern in patterns:
            for file in glob.glob(pattern):
                if os.path.isfile(file):
                    dest = f"output/{category}/plots/{file}"
                    shutil.move(file, dest)
                    print(f"  ✓ {file} → {dest}")
    
    # File di report
    report_patterns = {
        "vth_extraction": ["vth_*_report.md"],
        "derivative_analysis": ["*_derivative_*_report.md", "dvth_dt_*_report.md"],
        "vds_effect": ["vds_effect_*_report.md"],
        "temperature_analysis": ["vth_vs_room_temp_*_report.md"],
        "comparisons": ["vth_compare_*_report.md"]
    }
    
    for category, patterns in report_patterns.items():
        for pattern in patterns:
            for file in glob.glob(pattern):
                if os.path.isfile(file):
                    dest = f"output/{category}/reports/{file}"
                    shutil.move(file, dest)
                    print(f"  ✓ {file} → {dest}")

def move_plot_directories():
    """Sposta le cartelle di plot nelle nuove posizioni."""
    print("\nSpostamento delle cartelle di plot...")
    
    plot_dirs = {
        "vds_effect_plots": "output/vds_effect/plots",
        "vth_vs_room_temp_plots": "output/temperature_analysis/plots", 
        "sqrt_method_plots": "output/vth_extraction/plots",
        "aggregated_plots": "output/derivative_analysis/plots"
    }
    
    for old_dir, new_dir in plot_dirs.items():
        if os.path.exists(old_dir):
            shutil.move(old_dir, new_dir)
            print(f"  ✓ {old_dir} → {new_dir}")

def create_config_file():
    """Crea il file di configurazione di default."""
    config_content = """# Configurazioni di default per l'analisi Vth
vth_extraction:
  default_vd_nmos: 0.1
  default_vd_pmos: 1.1
  window_size: 7
  include_vd0: false

output:
  base_path: "output"
  create_dirs: true
  save_plots: true
  save_csv: true

gui:
  default_device: "nmos"
  plot_style: "default"
  window_size: [1200, 800]

analysis:
  derivative:
    temperature_range: [-40, 125]
    vds_range: [0.05, 0.2]
  vds_effect:
    reference_vds: 0.1
    comparison_vds: [0.05, 0.15, 0.2]
"""
    
    config_path = "config/default_settings.yaml"
    with open(config_path, 'w') as f:
        f.write(config_content)
    print(f"\n  ✓ Creato {config_path}")

def create_requirements_file():
    """Crea il file requirements.txt se non esiste."""
    if not os.path.exists("requirements.txt"):
        requirements_content = """# Dependencies for VthCalculator
numpy<2
pandas
matplotlib
pyyaml
"""
        with open("requirements.txt", 'w') as f:
            f.write(requirements_content)
        print("  ✓ Creato requirements.txt")

def update_gitignore():
    """Aggiorna il .gitignore per la nuova struttura."""
    gitignore_additions = """

# Output directories
output/*/csv/
output/*/plots/
output/*/reports/

# Temporary files
*.tmp
*.temp

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db
"""
    
    with open(".gitignore", 'a') as f:
        f.write(gitignore_additions)
    print("  ✓ Aggiornato .gitignore")

def main():
    """Esegue la migrazione completa."""
    print("=== Migrazione Struttura Progetto VthCalculator ===\n")
    
    # Backup warning
    print("⚠️  ATTENZIONE: Questo script modificherà la struttura del progetto.")
    print("   Assicurati di avere un backup o di aver committato le modifiche in git.\n")
    
    response = input("Procedere con la migrazione? (y/N): ")
    if response.lower() != 'y':
        print("Migrazione annullata.")
        return
    
    try:
        create_directory_structure()
        create_init_files()
        move_scripts()
        move_data_files()
        move_output_files()
        move_plot_directories()
        create_config_file()
        create_requirements_file()
        update_gitignore()
        
        print("\n✅ Migrazione completata con successo!")
        print("\nProssimi passi:")
        print("1. Aggiornare i path negli script in src/analysis/")
        print("2. Modificare il Makefile per la nuova struttura")
        print("3. Testare tutte le funzionalità")
        print("4. Aggiornare la documentazione")
        
    except Exception as e:
        print(f"\n❌ Errore durante la migrazione: {e}")
        print("Ripristina il backup se necessario.")

if __name__ == "__main__":
    main()

