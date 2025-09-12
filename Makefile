# Makefile per VthCalculator - Versione Riorganizzata
# Automatizza Vth extraction, batch processing, e derivative analysis

.PHONY: help all nmos pmos clean clean-data gui batch batch-daniele derivative derivative-nmos derivative-pmos english quick-all list install test venv-activate

# Configurazioni
VENV_DIR = venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
SRC_DIR = src
DATA_DIR = data
OUTPUT_DIR = output
CONFIG_DIR = config

# Default target
help:
	@echo "VthCalculator - Analisi Vth e Derivative Analysis"
	@echo "Struttura riorganizzata - Available targets:"
	@echo ""
	@echo "=== SETUP ==="
	@echo "  install     - Installa le dipendenze in virtual environment"
	@echo "  venv-activate - Mostra come attivare il virtual environment"
	@echo "  test        - Esegue i test unitari"
	@echo ""
	@echo "=== BASIC VTH EXTRACTION ==="
	@echo "  gui          - Launch interactive GUI per analisi singolo file"
	@echo "  batch        - Run batch processing con entrambi i metodi (traditional + sqrt)"
	@echo "  batch-daniele- Run batch processing con confronto Daniele (entrambi i metodi)"
	@echo ""
	@echo "=== DERIVATIVE ANALYSIS ==="
	@echo "  derivative   - Run derivative analysis per tutti i dispositivi"
	@echo "  derivative-nmos - Run derivative analysis per NMOS only"
	@echo "  derivative-pmos - Run derivative analysis per PMOS only"
	@echo "  plots        - Generate English version di tutti i plot"
	@echo ""
	@echo "=== UTILITY ==="
	@echo "  quick-all    - Quick derivative analysis (usa dati esistenti)"
	@echo "  list         - Lista tutti i file generati"
	@echo "  clean        - Rimuove tutti i file generati"
	@echo "  clean-data   - Rimuove solo i file dati, mantiene i plot"
	@echo "  help         - Mostra questo messaggio di aiuto"
	@echo ""
	@echo "Esempi:"
	@echo "  make install # Installa dipendenze"
	@echo "  make gui     # Analisi interattiva"
	@echo "  make batch   # Batch processing (entrambi i metodi)"
	@echo "  make derivative # Derivative analysis"
	@echo "  make clean   # Pulisce tutti i file"

# ===== SETUP =====

install:
	@echo "Creating virtual environment if it doesn't exist..."
	@python3 -m venv $(VENV_DIR) || echo "Virtual environment already exists"
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✓ Dependencies installed in virtual environment"

venv-activate:
	@echo "To activate the virtual environment, run:"
	@echo "  source $(VENV_DIR)/bin/activate"
	@echo ""
	@echo "To deactivate, run:"
	@echo "  deactivate"
	@echo ""
	@echo "Or use the Makefile targets directly (they use the venv automatically)"

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/ -v
	@echo "✓ Tests completed"

# ===== BASIC VTH EXTRACTION =====

# Launch interactive GUI
gui:
	@echo "Launching interactive GUI..."
	$(PYTHON) $(SRC_DIR)/analysis/extract_vth.py --gui

# Run batch processing with both traditional and sqrt methods
batch:
	@echo "Running batch processing with both traditional and sqrt methods..."
	$(PYTHON) $(SRC_DIR)/analysis/extract_vth.py $(DATA_DIR)/raw --run_all \
		--methods traditional sqrt \
		--out $(OUTPUT_DIR)/vth_extraction/csv/vth_all.csv \
		--summary-out $(OUTPUT_DIR)/vth_extraction/csv/vth_summary.csv \
		--plots-outdir $(OUTPUT_DIR)/vth_extraction/plots
	@echo "✓ Batch processing completed!"
	@echo "Check generated files in $(OUTPUT_DIR)/vth_extraction/"

# Run batch processing with Daniele comparison (both methods)
batch-daniele:
	@echo "Running batch processing with Daniele comparison (both methods)..."
	$(PYTHON) $(SRC_DIR)/analysis/extract_vth.py $(DATA_DIR)/raw --run_all \
		--methods traditional sqrt \
		--out $(OUTPUT_DIR)/vth_extraction/csv/vth_all.csv \
		--summary-out $(OUTPUT_DIR)/vth_extraction/csv/vth_summary.csv \
		--plots-outdir $(OUTPUT_DIR)/vth_extraction/plots \
		--daniele-csv $(DATA_DIR)/reference/RisultatiDaniele.csv \
		--compare-threshold 0.01
	@echo "✓ Batch processing with comparison completed!"
	@echo "Check generated files in $(OUTPUT_DIR)/vth_extraction/"

# ===== DERIVATIVE ANALYSIS =====

# Extract Vth data for all chips (for derivative analysis)
extract-data:
	@echo "Extracting Vth data for all chips..."
	$(PYTHON) $(SRC_DIR)/analysis/extract_vth.py $(DATA_DIR)/raw/chip3 --all-vd \
		--out $(OUTPUT_DIR)/derivative_analysis/csv/chip3_vth_all_vds.csv
	$(PYTHON) $(SRC_DIR)/analysis/extract_vth.py $(DATA_DIR)/raw/chip4 --all-vd \
		--out $(OUTPUT_DIR)/derivative_analysis/csv/chip4_vth_all_vds.csv
	$(PYTHON) $(SRC_DIR)/analysis/extract_vth.py $(DATA_DIR)/raw/chip5 --all-vd \
		--out $(OUTPUT_DIR)/derivative_analysis/csv/chip5_vth_all_vds.csv
	@echo "Combining data from all chips..."
	@head -1 $(OUTPUT_DIR)/derivative_analysis/csv/chip3_vth_all_vds.csv > $(OUTPUT_DIR)/derivative_analysis/csv/all_chips_vth_all_vds.csv
	@tail -n +2 $(OUTPUT_DIR)/derivative_analysis/csv/chip3_vth_all_vds.csv >> $(OUTPUT_DIR)/derivative_analysis/csv/all_chips_vth_all_vds.csv
	@tail -n +2 $(OUTPUT_DIR)/derivative_analysis/csv/chip4_vth_all_vds.csv >> $(OUTPUT_DIR)/derivative_analysis/csv/all_chips_vth_all_vds.csv
	@tail -n +2 $(OUTPUT_DIR)/derivative_analysis/csv/chip5_vth_all_vds.csv >> $(OUTPUT_DIR)/derivative_analysis/csv/all_chips_vth_all_vds.csv
	@echo "✓ Data extraction completed!"

# Run derivative analysis for all devices
derivative: extract-data
	@echo "Running derivative analysis for all devices..."
	@cp $(OUTPUT_DIR)/derivative_analysis/csv/all_chips_vth_all_vds.csv $(OUTPUT_DIR)/derivative_analysis/csv/all_chips_complete_data.csv
	$(PYTHON) $(SRC_DIR)/analysis/vth_derivative_vs_vds_temp.py . \
		--device-type both \
		--output-prefix all_chips_complete \
		--skip-extraction
	@echo "✓ Derivative analysis completed!"
	@echo "Check generated files in $(OUTPUT_DIR)/derivative_analysis/"

# Run derivative analysis for NMOS only
derivative-nmos: extract-data
	@echo "Running derivative analysis for NMOS only..."
	@cp $(OUTPUT_DIR)/derivative_analysis/csv/all_chips_vth_all_vds.csv $(OUTPUT_DIR)/derivative_analysis/csv/nmos_derivative_data.csv
	$(PYTHON) $(SRC_DIR)/analysis/vth_derivative_vs_vds_temp.py . \
		--device-type nmos \
		--output-prefix nmos_derivative \
		--skip-extraction \
	@echo "✓ NMOS derivative analysis completed!"

# Run derivative analysis for PMOS only
derivative-pmos: extract-data
	@echo "Running derivative analysis for PMOS only..."
	@cp $(OUTPUT_DIR)/derivative_analysis/csv/all_chips_vth_all_vds.csv $(OUTPUT_DIR)/derivative_analysis/csv/pmos_derivative_data.csv
	$(PYTHON) $(SRC_DIR)/analysis/vth_derivative_vs_vds_temp.py . \
		--device-type pmos \
		--output-prefix pmos_derivative \
		--skip-extraction \
	@echo "✓ PMOS derivative analysis completed!"

# Generate English version of all derivative plots
plots:
	@echo "Generating English version of all derivative plots..."
	$(PYTHON) $(SRC_DIR)/analysis/vth_derivative_vs_vds_temp.py . \
		--device-type both \
		--output-prefix all_chips_english
	@echo "✓ English plots generated!"

# ===== LEGACY TARGETS (for backward compatibility) =====

all: derivative
nmos: derivative-nmos
pmos: derivative-pmos

# ===== UTILITY =====

# Quick derivative analysis (uses existing data)
quick-all:
	@echo "Running quick derivative analysis..."
	$(PYTHON) $(SRC_DIR)/analysis/vth_derivative_vs_vds_temp.py . \
		--device-type both \
		--output-prefix all_chips_complete \
		--skip-extraction \
	@echo "✓ Quick analysis completed!"

# List all generated files
list:
	@echo "Generated files in $(OUTPUT_DIR):"
	@find $(OUTPUT_DIR) -type f -name "*.csv" -o -name "*.pdf" -o -name "*.png" -o -name "*.md" | sort

# Clean all generated files
clean:
	@echo "Cleaning all generated files..."
	@rm -rf $(OUTPUT_DIR)/*/csv/*.csv
	@rm -rf $(OUTPUT_DIR)/*/plots/*.pdf
	@rm -rf $(OUTPUT_DIR)/*/plots/*.png
	@rm -rf $(OUTPUT_DIR)/*/reports/*.md
	@echo "✓ All generated files cleaned"

# Clean only data files, keep plots
clean-data:
	@echo "Cleaning data files only..."
	@rm -rf $(OUTPUT_DIR)/*/csv/*.csv
	@rm -rf $(OUTPUT_DIR)/*/reports/*.md
	@echo "✓ Data files cleaned, plots preserved"

# ===== DEVELOPMENT =====

# Format code
format:
	@echo "Formatting code..."
	black $(SRC_DIR)/
	@echo "✓ Code formatted"

# Lint code
lint:
	@echo "Linting code..."
	flake8 $(SRC_DIR)/
	@echo "✓ Code linted"

# Run all development checks
dev-check: format lint test
	@echo "✓ All development checks passed"

# ===== DOCUMENTATION =====

# Generate documentation
docs:
	@echo "Generating documentation..."
	@mkdir -p $(OUTPUT_DIR)/docs
	$(PYTHON) -m pydoc -w $(SRC_DIR)/core/
	$(PYTHON) -m pydoc -w $(SRC_DIR)/analysis/
	@mv *.html $(OUTPUT_DIR)/docs/
	@echo "✓ Documentation generated in $(OUTPUT_DIR)/docs/"

# ===== DEPLOYMENT =====

# Create distribution package
dist:
	@echo "Creating distribution package..."
	$(PYTHON) setup.py sdist bdist_wheel
	@echo "✓ Distribution package created"

# Install in development mode
dev-install:
	@echo "Installing in development mode..."
	$(PIP) install -e .
	@echo "✓ Development installation completed"
