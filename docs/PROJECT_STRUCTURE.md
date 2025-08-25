# Struttura del Progetto VthCalculator

Questo documento descrive la nuova struttura organizzata del progetto VthCalculator.

## Panoramica della Struttura

```
vthcalculator/
├── README.md                 # Documentazione principale
├── Makefile                  # Automazione build e analisi
├── requirements.txt          # Dipendenze Python
├── setup.py                  # Configurazione pacchetto
├── .gitignore               # File ignorati da git
│
├── src/                     # Codice sorgente
│   ├── __init__.py
│   ├── core/                # Logica di business core
│   │   ├── __init__.py
│   │   ├── vth_extractor.py # Estrazione Vth principale
│   │   ├── data_parser.py   # Parsing dei file di misura
│   │   ├── derivative_analyzer.py # Analisi delle derivate
│   │   └── utils.py         # Utility comuni
│   ├── gui/                 # Interfaccia grafica
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   └── plot_widgets.py
│   └── analysis/            # Script di analisi specifici
│       ├── __init__.py
│       ├── extract_vth.py   # Script principale estrazione
│       ├── vds_effect.py    # Analisi effetto Vds
│       ├── temperature_analysis.py # Analisi temperatura
│       ├── sqrt_method.py   # Metodo sqrt
│       └── comparison_tools.py # Strumenti confronto
│
├── data/                    # Dati di input
│   ├── raw/                 # Dati grezzi originali
│   │   ├── chip3/           # Dati chip 3
│   │   ├── chip4/           # Dati chip 4
│   │   ├── chip5/           # Dati chip 5
│   │   └── DanieleResults/  # Risultati Daniele
│   └── reference/           # Dati di riferimento
│       └── RisultatiDaniele.csv
│
├── output/                  # Tutti i file generati
│   ├── vth_extraction/      # Risultati estrazione Vth
│   │   ├── csv/             # File CSV
│   │   ├── plots/           # Grafici e plot
│   │   └── reports/         # Report e documentazione
│   ├── derivative_analysis/ # Analisi derivate
│   │   ├── csv/
│   │   ├── plots/
│   │   └── reports/
│   ├── vds_effect/          # Analisi effetto Vds
│   │   ├── csv/
│   │   ├── plots/
│   │   └── reports/
│   ├── temperature_analysis/ # Analisi temperatura
│   │   ├── csv/
│   │   ├── plots/
│   │   └── reports/
│   └── comparisons/         # Confronti e validazioni
│       ├── csv/
│       ├── plots/
│       └── reports/
│
├── config/                  # File di configurazione
│   ├── default_settings.yaml # Configurazioni di default
│   └── analysis_configs/    # Configurazioni specifiche
│
├── tests/                   # Test unitari e integrazione
│   ├── __init__.py
│   ├── test_vth_extractor.py
│   ├── test_data_parser.py
│   ├── test_gui_methods.py
│   └── test_data/           # Dati di test
│
└── docs/                    # Documentazione
    ├── PROJECT_STRUCTURE.md # Questo file
    ├── GUI_Usage_Guide.md   # Guida GUI
    ├── GUI_Enhancement_Summary.md
    ├── examples/            # Esempi di utilizzo
    └── images/              # Immagini documentazione
```

## Descrizione delle Cartelle

### `src/` - Codice Sorgente
Contiene tutto il codice Python del progetto, organizzato in moduli logici:

- **`core/`**: Logica di business principale, funzioni core per l'estrazione Vth
- **`gui/`**: Interfaccia grafica utente e widget per la visualizzazione
- **`analysis/`**: Script specifici per diversi tipi di analisi

### `data/` - Dati di Input
Separazione chiara tra dati grezzi e di riferimento:

- **`raw/`**: Dati di misura originali organizzati per chip
- **`reference/`**: Dati di confronto e validazione

### `output/` - File Generati
Organizzazione strutturata di tutti i file di output:

- **`vth_extraction/`**: Risultati dell'estrazione Vth base
- **`derivative_analysis/`**: Analisi delle derivate vs temperatura/Vds
- **`vds_effect/`**: Analisi dell'effetto Vds
- **`temperature_analysis/`**: Analisi della dipendenza dalla temperatura
- **`comparisons/`**: Confronti tra metodi e validazioni

Ogni cartella di output contiene:
- **`csv/`**: File dati in formato CSV
- **`plots/`**: Grafici e visualizzazioni (PDF, PNG)
- **`reports/`**: Report di analisi e documentazione

### `config/` - Configurazioni
File di configurazione centralizzati:

- **`default_settings.yaml`**: Configurazioni di default per tutte le analisi
- **`analysis_configs/`**: Configurazioni specifiche per diversi tipi di analisi

### `tests/` - Test
Test unitari e di integrazione:

- Test per ogni modulo principale
- Dati di test per validazione
- Test della GUI

### `docs/` - Documentazione
Documentazione completa del progetto:

- Guide utente
- Esempi di utilizzo
- Immagini e diagrammi

## Vantaggi della Nuova Struttura

### 1. Separazione delle Responsabilità
- **Codice**: Tutto il codice sorgente in `src/`
- **Dati**: Input separato da output
- **Configurazione**: Impostazioni centralizzate
- **Documentazione**: Organizzata e accessibile

### 2. Manutenibilità
- Moduli piccoli e focalizzati
- Dipendenze chiare tra componenti
- Facile localizzazione di problemi
- Test strutturati

### 3. Scalabilità
- Facile aggiungere nuove funzionalità
- Struttura modulare
- Configurazioni flessibili
- Output organizzato

### 4. Collaborazione
- Struttura standard per team
- Separazione chiara dei ruoli
- Documentazione integrata
- Versioning semplificato

## Utilizzo della Nuova Struttura

### Comandi Makefile Principali

```bash
# Setup
make install          # Installa dipendenze
make test             # Esegue test

# Analisi Vth
make gui              # GUI interattiva
make batch            # Batch processing
make batch-daniele    # Con confronto Daniele

# Analisi derivate
make derivative       # Analisi completa
make derivative-nmos  # Solo NMOS
make derivative-pmos  # Solo PMOS

# Utility
make clean            # Pulisce output
make list             # Lista file generati
```

### Percorsi Importanti

- **Dati grezzi**: `data/raw/chip*/`
- **Risultati Vth**: `output/vth_extraction/`
- **Analisi derivate**: `output/derivative_analysis/`
- **Configurazioni**: `config/default_settings.yaml`

### Aggiungere Nuove Funzionalità

1. **Nuovo script di analisi**: Aggiungere in `src/analysis/`
2. **Nuova configurazione**: Aggiungere in `config/`
3. **Nuovi test**: Aggiungere in `tests/`
4. **Nuova documentazione**: Aggiungere in `docs/`

## Migrazione da Struttura Precedente

La migrazione è stata completata automaticamente. I file sono stati spostati nelle nuove posizioni mantenendo la funzionalità esistente.

### File di Backup
- `Makefile.old`: Vecchio Makefile per riferimento
- `REORGANIZATION_PLAN.md`: Piano di migrazione dettagliato

### Verifica Post-Migrazione
Per verificare che tutto funzioni correttamente:

```bash
make test             # Esegue test
make gui              # Testa GUI
make batch            # Testa batch processing
```

## Supporto e Manutenzione

Per problemi o domande sulla nuova struttura:

1. Consultare questo documento
2. Verificare la documentazione in `docs/`
3. Controllare i test in `tests/`
4. Rivedere le configurazioni in `config/`

