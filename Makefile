SHELL := /bin/bash  # Default shell

# Define variables
VENV_DIR = .venv
REQUIREMENTS = requirements.txt
SERVER_DIR = .

# Phony targets
.PHONY: all install run-server run-client clean format

# Default target
all: install

# Install dependencies
install:
	@echo "Activating virtual environment and installing dependencies..."
	@if [ -d "$(VENV_DIR)" ]; then \
		. $(VENV_DIR)/bin/activate && pip install -r $(REQUIREMENTS); \
	else \
		python -m venv $(VENV_DIR) && \
		. $(VENV_DIR)/bin/activate && pip install -r $(REQUIREMENTS); \
	fi

# Run the server
run-server:
	@echo "Starting the server..."
	@if [ -d "$(VENV_DIR)" ]; then \
		. $(VENV_DIR)/bin/activate && uvicorn main:app --port 8000; \
	else \
		echo "Virtual environment not found!"; \
	fi

# Clean target (optional)
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_DIR)

# Format code
format:
	@echo "Formatting code..."
	@if [ -d "$(VENV_DIR)" ]; then \
		. $(VENV_DIR)/bin/activate && \
		pip install ruff pyclean && \
		ruff format *.py && \
		pyclean -v .; \
	else \
		echo "Virtual environment not found!"; \
	fi
