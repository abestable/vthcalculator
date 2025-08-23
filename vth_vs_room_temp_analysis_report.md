# Analisi Vth vs Temperatura Ambiente (295K)

*Report generato automaticamente - Analisi Vth vs temperatura ambiente completata con successo*

## 📊 **Panoramica dell'Analisi**

Questa analisi confronta la variazione della tensione di soglia (Vth) rispetto alla temperatura ambiente (295K) per entrambi i metodi di estrazione:
- **Metodo Traditional** (estrapolazione lineare)
- **Metodo Sqrt** (metodo della radice quadrata)

### **Configurazione dei Vds:**
- **NMOS**: Vds=0.1V (traditional) vs Vds=1.2V (sqrt)
- **PMOS**: Vds=1.1V (traditional) vs Vds=0.0V (sqrt)

## 🔬 **Risultati Principali**

### **Comportamento Fisico Corretto:**
- **NMOS**: ΔVth medio = **+0.075 V** (Vth diminuisce con la temperatura ✅)
- **PMOS**: ΔVth medio = **-0.112 V** (Vth aumenta con la temperatura ✅)

### **Confronto tra Metodi:**

#### **NMOS:**
- **Traditional**: ΔVth = 0.074870 V
- **Sqrt**: ΔVth = 0.075592 V
- **Differenza**: **0.96%** (eccellente correlazione)

#### **PMOS:**
- **Traditional**: ΔVth = -0.112403 V
- **Sqrt**: ΔVth = -0.112017 V
- **Differenza**: **0.34%** (correlazione quasi perfetta)

## 📈 **Analisi per Device**

### **NMOS - Sensibilità Termica per Device:**
- **Device 1**: ΔVth medio = 0.061 V (meno sensibile)
- **Device 2**: ΔVth medio = 0.068 V
- **Device 3**: ΔVth medio = 0.081 V
- **Device 4**: ΔVth medio = 0.091 V (più sensibile)

### **PMOS - Sensibilità Termica per Device:**
- **Device 1**: ΔVth medio = -0.096 V (meno sensibile)
- **Device 2**: ΔVth medio = -0.118 V
- **Device 3**: ΔVth medio = -0.113 V
- **Device 4**: ΔVth medio = -0.122 V (più sensibile)

## 🎯 **Interpretazione dei Grafici**

### **1. Vth vs Temperatura (vth_vs_room_temp.pdf)**
- Mostra l'andamento assoluto di Vth con la temperatura
- NMOS: Vth diminuisce linearmente con la temperatura
- PMOS: Vth aumenta linearmente con la temperatura
- Entrambi i metodi mostrano lo stesso comportamento fisico

### **2. ΔVth vs ΔTemperatura (vth_diff_vs_temp_diff.pdf)**
- Mostra la variazione di Vth rispetto alla temperatura ambiente (295K)
- ΔT = T - 295K (differenza dalla temperatura ambiente)
- ΔVth = Vth(T) - Vth(295K) (differenza dalla Vth a temperatura ambiente)
- Pendenza = sensibilità termica del device

### **3. Scatter ΔVth (vth_diff_vs_room_temp_scatter.pdf)**
- Confronta i due metodi per la variazione di Vth
- Punti sulla bisettrice = metodi equivalenti
- Colori diversi = device diversi
- Error bars = incertezza statistica

## 📊 **Statistiche Dettagliate**

### **NMOS - Range di Variazione:**
- **Traditional**: ΔVth = [0.031, 0.118] V
- **Sqrt**: ΔVth = [0.036, 0.123] V
- **Deviazione standard**: ~0.023 V per entrambi i metodi

### **PMOS - Range di Variazione:**
- **Traditional**: ΔVth = [-0.180, -0.051] V
- **Sqrt**: ΔVth = [-0.183, -0.031] V
- **Deviazione standard**: ~0.043 V per entrambi i metodi

## 🔍 **Esempi Specifici**

### **NMOS Device 1 a 85K:**
- **ΔVth**: 0.084 ± 0.004 V
- **Vth(85K)**: 0.474 V
- **Vth(295K)**: 0.391 V
- **Variazione**: +21.3% rispetto alla temperatura ambiente

### **PMOS Device 1 a 85K:**
- **ΔVth**: -0.141 ± 0.006 V
- **Vth(85K)**: -0.519 V
- **Vth(295K)**: -0.378 V
- **Variazione**: -37.2% rispetto alla temperatura ambiente

## 🎯 **Conclusioni**

### **1. Validazione Fisica:**
- ✅ Entrambi i device mostrano il comportamento termico corretto
- ✅ NMOS: Vth diminuisce con la temperatura (effetto termico normale)
- ✅ PMOS: Vth aumenta con la temperatura (effetto termico normale)

### **2. Equivalenza dei Metodi:**
- ✅ **Eccellente correlazione** tra metodi traditional e sqrt
- ✅ Differenze < 1% per entrambi i tipi di device
- ✅ Entrambi i metodi catturano lo stesso fenomeno fisico

### **3. Variabilità tra Device:**
- 📊 **NMOS**: Sensibilità termica varia del 56% tra device (0.061-0.091 V)
- 📊 **PMOS**: Sensibilità termica varia del 27% tra device (-0.096 a -0.122 V)
- 🔍 Possibili differenze nella qualità del processo o caratteristiche specifiche

### **4. Applicazioni Pratiche:**
- **Modellazione termica**: I dati possono essere usati per modelli di comportamento termico
- **Controllo qualità**: Identificazione di device con comportamento anomalo
- **Ottimizzazione**: Selezione di device con sensibilità termica specifica
- **Validazione**: Conferma che entrambi i metodi di estrazione sono equivalenti

## 📁 **File Generati**

- `vth_vs_room_temp_plots/vth_vs_room_temp.pdf` - Vth assoluto vs temperatura
- `vth_vs_room_temp_plots/vth_diff_vs_temp_diff.pdf` - ΔVth vs ΔT
- `vth_vs_room_temp_plots/vth_diff_vs_room_temp_scatter.pdf` - Confronto metodi per ΔVth
- `vth_vs_room_temp_plots/vth_diff_aggregated_data.csv` - Dati aggregati
- `vth_vs_room_temp_data.csv` - Dati grezzi Vth
- `vth_diff_vs_room_temp_data.csv` - Differenze Vth

## 🚀 **Prossimi Passi Suggeriti**

1. **Analisi di correlazione** tra sensibilità termica e altre caratteristiche del device
2. **Modellazione matematica** del comportamento termico
3. **Identificazione di outlier** per controllo qualità
4. **Confronto con dati di letteratura** per validazione
5. **Ottimizzazione dei metodi** basata sui risultati ottenuti

---

*Analisi completata con successo - Tutti i device mostrano comportamento termico corretto e i metodi sono equivalenti.*

