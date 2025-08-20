# Makefile for Vth Derivative Analysis
# Automates the analysis of Vth derivative vs temperature and Vds

.PHONY: help all nmos pmos clean clean-data

# Default target
help:
	@echo "Vth Derivative Analysis - Available targets:"
	@echo ""
	@echo "  all          - Run analysis for all devices (NMOS + PMOS)"
	@echo "  nmos         - Run analysis for NMOS only"
	@echo "  pmos         - Run analysis for PMOS only"
	@echo "  clean        - Remove all generated PDF and CSV files"
	@echo "  clean-data   - Remove only data CSV files, keep plots"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make all     # Generate all plots and data"
	@echo "  make nmos    # Generate NMOS analysis only"
	@echo "  make clean   # Clean all generated files"

# Extract Vth data for all chips
extract-data:
	@echo "Extracting Vth data for all chips..."
	python3 scripts/extract_vth.py chip3 --all-vd --out chip3_vth_all_vds.csv
	python3 scripts/extract_vth.py chip4 --all-vd --out chip4_vth_all_vds.csv
	python3 scripts/extract_vth.py chip5 --all-vd --out chip5_vth_all_vds.csv
	@echo "Combining data from all chips..."
	@head -1 chip3_vth_all_vds.csv > all_chips_vth_all_vds.csv
	@tail -n +2 chip3_vth_all_vds.csv >> all_chips_vth_all_vds.csv
	@tail -n +2 chip4_vth_all_vds.csv >> all_chips_vth_all_vds.csv
	@tail -n +2 chip5_vth_all_vds.csv >> all_chips_vth_all_vds.csv
	@echo "Data extraction completed!"

# Run analysis for all devices
all: extract-data
	@echo "Running analysis for all devices..."
	@cp all_chips_vth_all_vds.csv all_chips_complete_data.csv
	python3 scripts/vth_derivative_vs_vds_temp.py . --device-type both --output-prefix all_chips_complete --skip-extraction
	@echo "Analysis completed! Check the generated PDF files."

# Run analysis for NMOS only
nmos: extract-data
	@echo "Running analysis for NMOS only..."
	@cp all_chips_vth_all_vds.csv nmos_derivative_data.csv
	python3 scripts/vth_derivative_vs_vds_temp.py . --device-type nmos --output-prefix nmos_derivative --skip-extraction
	@echo "NMOS analysis completed!"

# Run analysis for PMOS only
pmos: extract-data
	@echo "Running analysis for PMOS only..."
	@cp all_chips_vth_all_vds.csv pmos_derivative_data.csv
	python3 scripts/vth_derivative_vs_vds_temp.py . --device-type pmos --output-prefix pmos_derivative --skip-extraction
	@echo "PMOS analysis completed!"

# Generate English version of all plots
english: extract-data
	@echo "Generating English version of all plots..."
	@cp all_chips_vth_all_vds.csv all_chips_english_data.csv
	python3 scripts/vth_derivative_vs_vds_temp.py . --device-type both --output-prefix all_chips_english --skip-extraction
	@cp all_chips_vth_all_vds.csv nmos_english_data.csv
	python3 scripts/vth_derivative_vs_vds_temp.py . --device-type nmos --output-prefix nmos_english --skip-extraction
	@cp all_chips_vth_all_vds.csv pmos_english_data.csv
	python3 scripts/vth_derivative_vs_vds_temp.py . --device-type pmos --output-prefix pmos_english --skip-extraction
	@echo "English plots generated!"

# Clean all generated files
clean:
	@echo "Cleaning all generated files..."
	rm -f *_vth_all_vds.csv
	rm -f *_derivative_data.csv
	rm -f *_derivative.csv
	rm -f *_3d.pdf
	rm -f *_heatmap.pdf
	rm -f *_contour.pdf
	rm -f *_english_*.pdf
	rm -f *_english_*.csv
	@echo "Clean completed!"

# Clean only data files, keep plots
clean-data:
	@echo "Cleaning data files only..."
	rm -f *_vth_all_vds.csv
	rm -f *_derivative_data.csv
	rm -f *_derivative.csv
	@echo "Data files cleaned!"

# Quick analysis (using existing data if available)
quick-all:
	@if [ -f "all_chips_vth_all_vds.csv" ]; then \
		echo "Using existing data for quick analysis..."; \
		cp all_chips_vth_all_vds.csv all_chips_complete_data.csv; \
		python3 scripts/vth_derivative_vs_vds_temp.py . --device-type both --output-prefix all_chips_complete --skip-extraction; \
	else \
		echo "No existing data found. Running full analysis..."; \
		make all; \
	fi

# Show generated files
list:
	@echo "Generated files:"
	@ls -la *_complete*.pdf 2>/dev/null || echo "No complete PDF files found"
	@ls -la *_derivative*.pdf 2>/dev/null || echo "No derivative PDF files found"
	@ls -la *_english*.pdf 2>/dev/null || echo "No English PDF files found"
	@ls -la *_derivative*.csv 2>/dev/null || echo "No CSV files found"
