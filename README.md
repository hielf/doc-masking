# Doc Masking

[![CI](https://github.com/hielf/doc-masking/actions/workflows/ci.yml/badge.svg)](https://github.com/hielf/doc-masking/actions/workflows/ci.yml)

Protect Sensitive Data in the AI Era

Using AI can be powerful—but uploading documents can put your personal or business information at risk. Sensitive data can be leaked or misused if not properly protected.

Docusafely is a fully local, fast, and all-in-one tool that keeps your documents safe. With features like masking, pseudonymization, and anonymization, it ensures your content is protected before it ever reaches AI—completely free to use.

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

- **Entity Detection**: Identifies sensitive information including emails, phones, addresses, SSNs, credit cards, medical codes, API keys, and more
- **Document Processing**: Handles both text (.txt) and PDF documents with advanced masking capabilities
- **Pseudonymization**: Replaces sensitive data with realistic pseudonyms using configurable templates
- **Policy Management**: Per-entity actions (remove, pseudonymize, format-preserve) with customizable templates
- **Dry-Run Reports**: Generate detailed JSON/CSV reports showing detected entities, actions, and masking results
- **UI Preview**: Preview masking results before processing with entity counts and type breakdowns
- **Test Document Generation**: Creates realistic test documents for comprehensive testing and validation
- **Cross-Platform**: Electron UI with Python backend for maximum compatibility

## Files

- `main.js` - Electron main process
- `index.html` - UI
- `python_backend/processor.py` - Text processor
- `python_backend/pdf_processor.py` - PDF processor
- `python_backend/test_document_generator.py` - Test document generation system
- `python_backend/test_runner_with_documents.py` - Enhanced test runner
- `python_backend/reports.py` - Dry-run reporting functionality
- `python_backend/dry_run_cli.py` - Command-line interface for dry-run reports
- `generate_test_documents.py` - Generate test documents script
- `generate_masked_documents.py` - Generate masked documents for inspection
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

## Dry-Run Reports and Preview

The application includes comprehensive reporting functionality for analyzing documents before processing and generating detailed reports.

### UI Preview
- Click "Preview Masking" to see what entities will be detected without actually masking the document
- View entity counts by type and see which actions will be applied
- Generate dry-run reports automatically when processing documents

### Command-Line Dry-Run
```bash
# Generate dry-run report for a text file
python python_backend/dry_run_cli.py input.txt --output reports/input_report

# Generate dry-run report with custom policy
python python_backend/dry_run_cli.py document.pdf --policy policy.json --output reports/document_report

# Generate reports in specific formats
python python_backend/dry_run_cli.py input.txt --format json --output reports/input_report
```

### Report Formats
- **JSON**: Complete structured data with all entity details
- **CSV**: Entity-level data for spreadsheet analysis
- **Summary CSV**: Document-level statistics and entity type breakdowns

## Test Document Generation

The application includes a comprehensive test document generation system that creates realistic test data for validation and testing purposes.

### Generate Test Documents
```bash
# Generate all test documents (TXT and PDF)
python generate_test_documents.py

# Generate masked documents for inspection
python generate_masked_documents.py

# Run example tests with generated documents
python example_test_with_documents.py
```

### Test Document Types
- **Basic Email Test** - Simple business email with contact information
- **Contact Information Test** - Contact form with multiple entity types
- **Medical Record Test** - Healthcare data with PHI (diagnoses, procedures, MRNs)
- **System Log Test** - Technical identifiers (IPs, MACs, cookies, GPS)
- **API Configuration Test** - Secrets and credentials (API keys, JWT tokens)
- **Business Letter Test** - Formal business letter with addresses
- **Vehicle Registration Test** - Government document with VINs and license plates
- **Comprehensive Test** - Complex document with all major entity types

### Masked Document Inspection
Generated test documents are saved to `test_documents/` with:
- **Original documents** - Source documents with sensitive data
- **Masked documents** - Processed documents with sensitive data masked
- **Expected outputs** - Predicted masked outputs for comparison
- **Test results** - Detailed analysis and accuracy scores

### Entity Types Supported
- Personal Information: names, emails, phones, addresses
- Government IDs: SSNs, MRNs, insurance IDs
- Financial: credit cards, bank accounts
- Technical: IP addresses, MAC addresses, API keys
- Medical: ICD codes, CPT codes, medical record numbers
- Legal: VINs, license plates, case numbers
- Location: GPS coordinates, travel itineraries
- Credentials: passwords, tokens, private keys
