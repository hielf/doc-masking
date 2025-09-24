# Doc Masking

[![CI](https://github.com/hielf/doc-masking/actions/workflows/ci.yml/badge.svg)](https://github.com/hielf/doc-masking/actions/workflows/ci.yml)

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
- `example/sample.txt` - Test file

## Requirements

- Node.js
- Python 3.13 (used for development and as a fallback when the compiled backend is not present)
  - Tip: with pyenv
    ```bash
    pyenv install 3.13.7
    pyenv local 3.13.7
    ```

## Development

Run with dev tools:
```bash
NODE_ENV=development npm start
```

Test Python script directly:
```bash
python3 python_backend/processor.py input.txt output.txt
```

## Processor execution

- The app first tries to run the compiled backend at `python_backend/dist/processor` (or `processor.exe` on Windows).
- If it is missing or not executable, it falls back to: `python3 python_backend/processor.py <in> <out>` (on Windows it tries `python` too).

## Testing

### JavaScript (Electron main process)
```bash
npm run test:js
```

### Python (backend)
Install dev requirements once:
```bash
python3 -m pip install -r python_backend/requirements-dev.txt
```
Run tests:
```bash
npm run test:py
# or
python3 -m pytest -q
```

### All tests
```bash
npm test
```
