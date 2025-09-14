# Doc Masking

A simple desktop app that converts text files to uppercase. Built with Electron for the UI and Python for processing.

## Quick Start

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the app:
   ```bash
   npm start
   ```

3. Select input and output files, then click "Process File"

## What it does

- Electron handles the UI and file dialogs
- Python script processes the text (converts to uppercase)
- They communicate via command line arguments and JSON

## Files

- `main.js` - Electron main process
- `index.html` - UI
- `python_backend/processor.py` - Text processor
- `sample.txt` - Test file

## Requirements

- Node.js
- Python 3

## Development

Run with dev tools:
```bash
NODE_ENV=development npm start
```

Test Python script directly:
```bash
python3 python_backend/processor.py input.txt output.txt
```
