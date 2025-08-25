# Piano di Riorganizzazione del Progetto VthCalculator

## Struttura Proposta

```
vthcalculator/
├── README.md
├── Makefile
├── requirements.txt
├── .gitignore
│
├── src/                          # Codice sorgente principale
│   ├── __init__.py
│   ├── core/                     # Logica di business core
│   │   ├── __init__.py
│   │   ├── vth_extractor.py      # Estrazione Vth principale
│   │   ├── data_parser.py        # Parsing dei file di misura
│   │   ├── derivative_analyzer.py # Analisi delle derivate
│   │   └── utils.py              # Utility comuni
│   ├── gui/                      # Interfaccia grafica
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   └── plot_widgets.py
│   └── analysis/                 # Script di analisi specifici
│       ├── __init__.py
│       ├── vds_effect.py
│       ├── temperature_analysis.py
│       ├── sqrt_method.py
│       └── comparison_tools.py
│
├── data/                         # Dati di input
│   ├── raw/                      # Dati grezzi originali
│   │   ├── chip3/
│   │   ├── chip4/
│   │   ├── chip5/
│   │   └── DanieleResults/
│   └── reference/                # Dati di riferimento
│       └── RisultatiDaniele.csv
│
├── output/                       # Tutti i file generati
│   ├── vth_extraction/           # Risultati estrazione Vth
│   │   ├── csv/
│   │   ├── plots/
│   │   └── reports/
│   ├── derivative_analysis/      # Analisi derivate
│   │   ├── csv/
│   │   ├── plots/
│   │   └── reports/
│   ├── vds_effect/               # Analisi effetto Vds
│   │   ├── csv/
│   │   ├── plots/
│   │   └── reports/
│   ├── temperature_analysis/     # Analisi temperatura
│   │   ├── csv/
│   │   ├── plots/
│   │   └── reports/
│   └── comparisons/              # Confronti e validazioni
│       ├── csv/
│       ├── plots/
│       └── reports/
│
├── config/                       # File di configurazione
│   ├── default_settings.yaml
│   └── analysis_configs/
│
├── tests/                        # Test unitari e integrazione
│   ├── __init__.py
│   ├── test_vth_extractor.py
│   ├── test_data_parser.py
│   └── test_data/                # Dati di test
│
└── docs/                         # Documentazione
    ├── user_guide.md
    ├── api_reference.md
    ├── examples/
    └── images/
```

## Vantaggi della Nuova Struttura

### 1. Separazione delle Responsabilità
- **`src/`**: Tutto il codice sorgente organizzato per funzionalità
- **`data/`**: Dati di input separati da codice e output
- **`output/`**: Tutti i file generati in un unico posto
- **`config/`**: Configurazioni separate dal codice

### 2. Organizzazione Logica
- **`core/`**: Logica di business principale
- **`gui/`**: Interfaccia utente
- **`analysis/`**: Script specifici per diversi tipi di analisi

### 3. Gestione Output Strutturata
- Ogni tipo di analisi ha la sua cartella di output
- Sottocartelle per CSV, plot e report
- Facile pulizia e backup

### 4. Manutenibilità
- Codice modulare e testabile
- Configurazioni centralizzate
- Documentazione organizzata

## Piano di Migrazione

### Fase 1: Preparazione
1. Creare la nuova struttura di cartelle
2. Spostare i file esistenti nelle nuove posizioni
3. Aggiornare i path nei Makefile e script

### Fase 2: Refactoring del Codice
1. Dividere `extract_vth.py` in moduli più piccoli
2. Creare classi per le diverse funzionalità
3. Implementare sistema di configurazione

### Fase 3: Aggiornamento Script
1. Aggiornare tutti i path negli script
2. Modificare il Makefile per la nuova struttura
3. Testare tutte le funzionalità

### Fase 4: Documentazione
1. Aggiornare README e guide
2. Creare documentazione API
3. Aggiungere esempi di utilizzo

## Comandi per la Migrazione

```bash
# Creare la nuova struttura
mkdir -p src/{core,gui,analysis} data/{raw,reference} output/{vth_extraction,derivative_analysis,vds_effect,temperature_analysis,comparisons}/{csv,plots,reports} config/analysis_configs tests/test_data docs/{examples,images}

# Spostare i file esistenti
mv scripts/* src/analysis/
mv chip* data/raw/
mv DanieleResults data/raw/
mv RisultatiDaniele.csv data/reference/

# Spostare output esistenti
mv *_data.csv output/*/csv/
mv *.pdf output/*/plots/
mv *_report.md output/*/reports/
```

## Configurazione Proposta

### config/default_settings.yaml
```yaml
# Configurazioni di default per l'analisi Vth
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
```

## Benefici Attesi

1. **Manutenibilità**: Codice più modulare e facile da mantenere
2. **Scalabilità**: Facile aggiungere nuove funzionalità
3. **Testabilità**: Struttura che facilita i test
4. **Usabilità**: Organizzazione più intuitiva per nuovi utenti
5. **Collaborazione**: Struttura standard che facilita il lavoro di team

