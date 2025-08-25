# Makefile for Vth Analysis and Derivative Analysis
# Automates Vth extraction, batch processing, and derivative analysis

.PHONY: help all nmos pmos clean clean-data gui batch batch-daniele derivative derivative-nmos derivative-pmos english quick-all list

# Default target
help:
	@echo "Vth Analysis and Derivative Analysis - Available targets:"
	@echo ""
	@echo "=== BASIC VTH EXTRACTION ==="
	@echo "  gui          - Launch interactive GUI for single file analysis"
	@echo "  batch        - Run batch processing (all chips, summary, plots)"
	@echo "  batch-daniele- Run batch processing with Daniele comparison"
	@echo ""
	@echo "=== DERIVATIVE ANALYSIS ==="
	@echo "  derivative   - Run derivative analysis for all devices (NMOS + PMOS)"
	@echo "  derivative-nmos - Run derivative analysis for NMOS only"
	@echo "  derivative-pmos - Run derivative analysis for PMOS only"
	@echo "  plots        - Generate English version of all derivative plots"
	@echo ""
	@echo "=== LEGACY TARGETS (for backward compatibility) ==="
	@echo "  all          - Same as derivative (all devices)"
	@echo "  nmos         - Same as derivative-nmos"
	@echo "  pmos         - Same as derivative-pmos"

	@echo ""
	@echo "=== UTILITY ==="
	@echo "  quick-all    - Quick derivative analysis (uses existing data)"
	@echo "  list         - List generated files"
	@echo "  clean        - Remove all generated files"
	@echo "  clean-data   - Remove only data files, keep plots"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make gui     # Interactive analysis"
	@echo "  make batch   # Standard batch processing"
	@echo "  make derivative # Derivative analysis"
	@echo "  make clean   # Clean all files"

# ===== BASIC VTH EXTRACTION =====

# Launch interactive GUI
gui:
	@echo "Launching interactive GUI..."
	python3 scripts/extract_vth.py --gui

# Run standard batch processing
batch:
	@echo "Running standard batch processing..."
	python3 scripts/extract_vth.py . --run_all --out vth_all.csv --summary-out vth_summary.csv --plots-outdir .
	@echo "Batch processing completed! Check generated files:"
	@echo "- vth_all.csv: per-file results"
	@echo "- vth_summary.csv: summary by device"
	@echo "- vth_by_chip.csv: pivot by chip"
	@echo "- vth_nmos_vs_temp.png: NMOS plots"
	@echo "- vth_pmos_vs_temp.png: PMOS plots"

# Run batch processing with Daniele comparison
batch-daniele:
	@echo "Running batch processing with Daniele comparison..."
	python3 scripts/extract_vth.py . --run_all --out vth_all.csv --summary-out vth_summary.csv --plots-outdir . --daniele-csv RisultatiDaniele.csv --compare-threshold 0.01
	@echo "Batch processing with comparison completed! Check generated files:"
	@echo "- vth_all.csv: per-file results"
	@echo "- vth_summary.csv: summary by device"
	@echo "- vth_by_chip.csv: pivot by chip"
	@echo "- vth_compare_clean.csv: comparison results"
	@echo "- vth_compare_clean_status.csv: PASS/FAIL status"

# ===== DERIVATIVE ANALYSIS =====

# Extract Vth data for all chips (for derivative analysis)
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

# Run derivative analysis for all devices
derivative: extract-data
	@echo "Running derivative analysis for all devices..."
	@cp all_chips_vth_all_vds.csv all_chips_complete_data.csv
	python3 scripts/vth_derivative_vs_vds_temp.py . --device-type both --output-prefix all_chips_complete --skip-extraction
	@echo "Derivative analysis completed! Check the generated PDF files."

# Run derivative analysis for NMOS only
derivative-nmos: extract-data
	@echo "Running derivative analysis for NMOS only..."
	@cp all_chips_vth_all_vds.csv nmos_derivative_data.csv
	python3 scripts/vth_derivative_vs_vds_temp.py . --device-type nmos --output-prefix nmos_derivative --skip-extraction
	@echo "NMOS derivative analysis completed!"

# Run derivative analysis for PMOS only
derivative-pmos: extract-data
	@echo "Running derivative analysis for PMOS only..."
	@cp all_chips_vth_all_vds.csv pmos_derivative_data.csv
	python3 scripts/vth_derivative_vs_vds_temp.py . --device-type pmos --output-prefix pmos_derivative --skip-extraction
	@echo "PMOS derivative analysis completed!"

# ===== LEGACY TARGETS (for backward compatibility) =====

# Legacy targets that map to derivative analysis
all: derivative
nmos: derivative-nmos
pmos: derivative-pmos

# Generate English version of all plots
plots: extract-data
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
	rm -f vth_all.csv
	rm -f vth_summary.csv
	rm -f vth_by_chip.csv
	rm -f vth_compare_clean.csv
	rm -f vth_compare_clean_status.csv
	rm -f vth_nmos_vs_temp.png
	rm -f vth_pmos_vs_temp.png
	@echo "Clean completed!"

# Clean only data files, keep plots
clean-data:
	@echo "Cleaning data files only..."
	rm -f *_vth_all_vds.csv
	rm -f *_derivative_data.csv
	rm -f *_derivative.csv
	@echo "Data files cleaned!"

# Quick derivative analysis (using existing data if available)
quick-all:
	@if [ -f "all_chips_vth_all_vds.csv" ]; then \
		echo "Using existing data for quick derivative analysis..."; \
		cp all_chips_vth_all_vds.csv all_chips_complete_data.csv; \
		python3 scripts/vth_derivative_vs_vds_temp.py . --device-type both --output-prefix all_chips_complete --skip-extraction; \
	else \
		echo "No existing data found. Running full derivative analysis..."; \
		make derivative; \
	fi

# Show generated files
list:
	@echo "Generated files:"
	@echo ""
	@echo "=== BASIC VTH FILES ==="
	@ls -la vth_*.csv 2>/dev/null || echo "No basic Vth CSV files found"
	@ls -la vth_*.png 2>/dev/null || echo "No basic Vth PNG files found"
	@echo ""
	@echo "=== DERIVATIVE ANALYSIS FILES ==="
	@ls -la *_complete*.pdf 2>/dev/null || echo "No complete PDF files found"
	@ls -la *_derivative*.pdf 2>/dev/null || echo "No derivative PDF files found"
	@ls -la *_english*.pdf 2>/dev/null || echo "No English PDF files found"
	@ls -la *_derivative*.csv 2>/dev/null || echo "No derivative CSV files found"
