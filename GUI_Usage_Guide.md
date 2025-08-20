# Guida all'Uso della GUI per l'Estrazione Vth

## Avvio della GUI

Per avviare la GUI interattiva, esegui:

```bash
python3 scripts/extract_vth.py --gui
```

oppure

```bash
make gui
```

## Interfaccia della GUI

La GUI è composta da diversi elementi:

### 1. Barra Superiore
- **File**: Campo di testo che mostra il percorso del file selezionato
- **Browse...**: Pulsante per selezionare un file di misurazione (.txt)
- **Device**: Campo che mostra automaticamente il tipo di dispositivo (NMOS/PMOS)
- **Vd block**: Menu a tendina per selezionare il valore di Vd da analizzare
- **Method**: **NUOVO** - Menu a tendina per scegliere il metodo di estrazione Vth

### 2. Grafici
- **Grafico superiore**: Curva IV (o √IV per il metodo Sqrt) con tangente e Vth
- **Grafico inferiore**: Transconduttanza (gm) con punto di massimo

### 3. Barra di Stato
Mostra informazioni in tempo reale:
- Tipo di dispositivo
- Valore Vd selezionato
- **Metodo utilizzato**
- Valore Vth calcolato
- Indice del punto di massimo gm

## Metodi di Estrazione Vth

### 1. Traditional
- **Descrizione**: Metodo tradizionale che utilizza la derivata della corrente Id
- **Formula**: gm = dId/dVg
- **Grafico**: Mostra Id vs Vg
- **Raccomandato per**: Vds bassi (< 0.5V) - regione lineare

### 2. Sqrt
- **Descrizione**: Nuovo metodo che utilizza la radice quadrata della corrente
- **Formula**: gm = d(√Id)/dVg
- **Grafico**: Mostra √Id vs Vg
- **Raccomandato per**: Vds alti (> 0.5V) - regione di saturazione
- **Vantaggi**: 
  - Linearità migliorata per transistor in saturazione
  - Estrapolazione più stabile
  - Teoricamente più corretto per Vds > Vdsat

### 3. Hybrid
- **Descrizione**: Metodo intelligente che sceglie automaticamente il metodo più appropriato
- **Logica**:
  - Se Vds < 0.5V → usa metodo Traditional
  - Se Vds ≥ 0.5V → usa metodo Sqrt
- **Vantaggi**: Massima accuratezza per entrambe le regioni di funzionamento

## Come Utilizzare la GUI

### 1. Selezione del File
1. Clicca su **Browse...**
2. Naviga fino alla cartella contenente i file di misurazione
3. Seleziona un file .txt (es. `chip3/115K/Nmos/2.txt`)
4. Il tipo di dispositivo viene rilevato automaticamente

### 2. Selezione del Vd
1. Il menu **Vd block** si popola automaticamente con i valori disponibili
2. Per NMOS: viene selezionato automaticamente il Vd più vicino a 0.1V
3. Per PMOS: viene selezionato automaticamente il Vd più vicino a 1.1V
4. Puoi cambiare manualmente il valore selezionato

### 3. Selezione del Metodo
1. Dal menu **Method**, scegli uno dei tre metodi:
   - **Traditional**: Per analisi tradizionale
   - **Sqrt**: Per analisi con radice quadrata
   - **Hybrid**: Per selezione automatica (raccomandato)

### 4. Analisi dei Risultati
- I grafici si aggiornano automaticamente quando cambi file, Vd o metodo
- **Grafico superiore**:
  - Linea blu: corrente (Id o √Id)
  - Linea nera: tangente al punto di massimo gm
  - Linea tratteggiata: Vth calcolata
- **Grafico inferiore**:
  - Linea rossa: transconduttanza (gm)
  - Punto rosso: massimo di gm
- **Barra di stato**: Mostra tutti i parametri rilevanti

## Interpretazione dei Risultati

### Confronto tra Metodi
- **Traditional vs Sqrt**: Le differenze sono normali e dipendono dal Vds
- **NMOS**: Il metodo Sqrt tende a dare Vth più basse
- **PMOS**: Il metodo Sqrt tende a dare Vth più alte
- **Hybrid**: Combina i vantaggi di entrambi i metodi

### Quando Usare Ogni Metodo
- **Traditional**: Per Vds bassi o quando si vuole confrontare con risultati precedenti
- **Sqrt**: Per Vds alti o quando si vuole massimizzare l'accuratezza in saturazione
- **Hybrid**: **Raccomandato** per uso generale - sceglie automaticamente il metodo migliore

## Suggerimenti per l'Analisi

1. **Inizia con Hybrid**: È il metodo più robusto e adatto alla maggior parte dei casi
2. **Confronta i metodi**: Cambia tra Traditional e Sqrt per vedere le differenze
3. **Osserva i grafici**: 
   - La linearità della tangente
   - La chiarezza del massimo di gm
   - La stabilità del calcolo Vth
4. **Considera il Vds**: 
   - Vds < 0.5V → Traditional è più appropriato
   - Vds > 0.5V → Sqrt è più appropriato

## Risoluzione Problemi

### GUI non si avvia
```bash
# Verifica le dipendenze
pip install "numpy<2" pandas matplotlib
# Su Ubuntu/Debian
sudo apt-get install python3-tk
```

### Errori di calcolo
- Verifica che il file contenga dati validi
- Controlla che il Vd selezionato sia presente nel file
- Prova a cambiare metodo se uno non funziona

### Grafici non si aggiornano
- Clicca su un altro elemento della GUI
- Riavvia la GUI se necessario

## Esempi di Utilizzo

### Analisi NMOS (Vds = 0.1V)
1. Seleziona file NMOS
2. Vd selezionato automaticamente: ~0.1V
3. Metodo Hybrid → usa Traditional (Vds < 0.5V)
4. Risultato: Vth tipicamente ~0.6-0.7V

### Analisi PMOS (Vds = 1.1V)
1. Seleziona file PMOS
2. Vd selezionato automaticamente: ~1.1V
3. Metodo Hybrid → usa Sqrt (Vds > 0.5V)
4. Risultato: Vth tipicamente ~-0.4-0.6V

### Confronto Metodi
1. Seleziona un file
2. Cambia metodo da Traditional a Sqrt
3. Osserva le differenze nei grafici e nei valori Vth
4. Nota come cambiano le etichette degli assi
