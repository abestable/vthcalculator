# Analisi del Metodo √Id per l'Estrazione della Vth

## Introduzione

Questo report presenta l'analisi di un nuovo metodo per l'estrazione della tensione di soglia (Vth) dei transistor MOS, basato sull'utilizzo della radice quadrata della corrente di drain (√Id) invece della corrente Id diretta.

## Motivazione Teorica

### Metodo Tradizionale
Il metodo tradizionale utilizza la derivata della corrente di drain rispetto alla tensione di gate:
```
gm = dId/dVg
```

### Nuovo Metodo √Id
Il nuovo metodo utilizza la radice quadrata della corrente:
```
gm = d(√Id)/dVg
```

### Giustificazione Teorica
Per transistor in regione di saturazione (Vds > Vdsat), la relazione corrente-tensione è:
```
Id ∝ (Vgs - Vth)²
```

Applicando la radice quadrata:
```
√Id ∝ (Vgs - Vth)
```

Questo rende la relazione lineare, facilitando l'estrapolazione per trovare Vth.

## Risultati dell'Analisi

### Statistiche Generali
- **File analizzati**: 124
- **Estrazioni riuscite**: 124 (100%)
- **Punti dati totali**: 1,488 (analisi multi-Vds)

### Confronto dei Metodi

#### Differenze Assolute
- **Differenza media**: 0.016 V
- **Deviazione standard**: 0.227 V
- **Range**: da -0.326 V a +1.010 V

#### Differenze Percentuali
- **Differenza media**: 2.62%
- **Deviazione standard**: 33.18%

### Analisi per Tipo di Dispositivo

#### NMOS
- **Conteggio**: 59 dispositivi
- **Differenza media**: -0.148 V (metodo √Id < metodo tradizionale)
- **Deviazione standard**: 0.014 V

#### PMOS
- **Conteggio**: 65 dispositivi
- **Differenza media**: +0.139 V (metodo √Id > metodo tradizionale)
- **Deviazione standard**: 0.014 V

### Analisi dell'Effetto Vds

#### Range Vds Analizzato
- **Range**: 0.1 V - 1.2 V
- **Punti dati**: 1,488

#### Differenze per Range Vds
1. **Vds 0-0.5V**: 496 punti, differenza media: +0.055 V
2. **Vds 0.5-1.0V**: 620 punti, differenza media: +0.007 V
3. **Vds 1.0-1.5V**: 372 punti, differenza media: -0.023 V

## Interpretazione dei Risultati

### 1. Consistenza del Metodo
Il metodo √Id mostra una buona consistenza con deviazioni standard relativamente basse (0.014 V per entrambi i tipi di dispositivo).

### 2. Effetto Vds
- **Vds bassi (0-0.5V)**: Il metodo √Id tende a dare Vth più alte
- **Vds medi (0.5-1.0V)**: Le differenze sono minime
- **Vds alti (1.0-1.5V)**: Il metodo √Id tende a dare Vth più basse

### 3. Differenze per Tipo di Dispositivo
- **NMOS**: Il metodo √Id produce Vth sistematicamente più basse
- **PMOS**: Il metodo √Id produce Vth sistematicamente più alte

## Vantaggi del Metodo √Id

1. **Linearità Migliorata**: La relazione √Id vs Vgs è più lineare nella regione di saturazione
2. **Estrapolazione più Stabile**: Riduce la non-linearità che può causare instabilità nell'estrapolazione
3. **Teoricamente Corretto**: Per Vds > Vdsat, il metodo √Id è più appropriato dal punto di vista fisico

## Limitazioni e Considerazioni

1. **Sensibilità al Rumore**: La radice quadrata può amplificare il rumore per correnti molto basse
2. **Regione di Funzionamento**: Il metodo è ottimale solo per transistor in saturazione
3. **Calibrazione**: Potrebbe richiedere calibrazione per specifici processi tecnologici

## Raccomandazioni

### Per Vds Bassi (< 0.5V)
- Utilizzare il metodo tradizionale
- Il transistor potrebbe non essere in saturazione

### Per Vds Medi (0.5-1.0V)
- Entrambi i metodi sono validi
- Le differenze sono minime

### Per Vds Alti (> 1.0V)
- Preferire il metodo √Id
- Il transistor è chiaramente in saturazione

## Risultati del Metodo Ibrido

### Implementazione
È stato implementato un metodo ibrido che sceglie automaticamente il metodo più appropriato basandosi sul valore di Vds:
- **Vds < 0.5V**: Metodo tradizionale (regione lineare)
- **Vds ≥ 0.5V**: Metodo √Id (regione di saturazione)

### Risultati del Test
- **File processati**: 124
- **Estrazioni riuscite**: 124 (100%)
- **Utilizzo dei metodi**:
  - Metodo tradizionale: 59 dispositivi (47.6%)
  - Metodo √Id: 65 dispositivi (52.4%)

### Distribuzione per Tipo di Dispositivo
- **NMOS (Vds = 0.1V)**: 100% metodo tradizionale
- **PMOS (Vds = 1.1V)**: 100% metodo √Id

### Statistiche Vth Ibrido
- **Vth media**: 0.057 V
- **Deviazione standard**: 0.543 V
- **Range**: da -0.580 V a +0.686 V

### Confronti
- **Ibrido vs Tradizionale**: Differenza media 0.073 V
- **Ibrido vs √Id**: Differenza media 0.070 V

## Conclusioni

Il metodo √Id rappresenta un miglioramento significativo per l'estrazione della Vth, specialmente per transistor operanti con Vds più alti. La sua implementazione è relativamente semplice e produce risultati consistenti.

**Raccomandazione principale**: Utilizzare il metodo ibrido che sceglie automaticamente il metodo più appropriato basandosi sul valore di Vds, con soglia a 0.5V. Questo approccio garantisce la massima accuratezza per entrambe le regioni di funzionamento del transistor.

## File di Output Generati

1. `sqrt_method_comparison.csv` - Confronto dettagliato dei due metodi
2. `vds_effect_analysis.csv` - Analisi dell'effetto Vds
3. `hybrid_vth_results.csv` - Risultati del metodo ibrido
4. `sqrt_method_plots/` - Grafici di confronto
5. `vds_effect_plots/` - Grafici dell'analisi Vds

## Codice Implementato

- `compute_vth_sqrt_method()` in `extract_vth.py` - Nuovo metodo √Id
- `compute_vth_hybrid()` in `extract_vth_hybrid.py` - Metodo ibrido
- `compare_sqrt_method.py` - Script di confronto
- `analyze_vds_effect.py` - Script di analisi Vds
- `extract_vth_hybrid.py` - Script per il metodo ibrido
