# Doc Masking - Electron + Python Text Processor

A simple desktop application built with Electron and Python for text file processing. This application demonstrates basic communication between Electron (frontend) and Python (backend) for document processing tasks.

## Features

- **File Selection**: Browse and select input and output text files
- **Text Processing**: Convert text files to uppercase (foundation for more complex processing)
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Modern UI**: Clean, responsive interface built with HTML/CSS/JavaScript

## Project Structure

```
doc-masking/
├── main.js                 # Electron main process
├── preload.js             # Secure IPC bridge
├── index.html             # Application UI
├── package.json           # Node.js dependencies
├── python_backend/
│   └── processor.py       # Python text processor
├── sample.txt            # Sample input file for testing
└── README.md             # This file
```

## Prerequisites

- **Node.js** (v14 or higher)
- **Python 3** (v3.6 or higher)
- **npm** (comes with Node.js)

## Installation

1. Clone or download this project
2. Navigate to the project directory:
   ```bash
   cd doc-masking
   ```
3. Install Electron dependencies:
   ```bash
   npm install
   ```

## Usage

1. **Start the application**:
   ```bash
   npm start
   ```

2. **Process a text file**:
   - Click "Browse" next to "Input File Path" to select a text file
   - Click "Browse" next to "Output File Path" to choose where to save the processed file
   - Click "Process File" to convert the text to uppercase
   - Check the status area for processing results

3. **Test with sample file**:
   - Use the included `sample.txt` file to test the application
   - The processed output will be saved to your chosen output location

## How It Works

### Electron Frontend
- **main.js**: Creates the Electron window and handles IPC communication
- **preload.js**: Provides secure bridge between renderer and main process
- **index.html**: User interface with file selection and processing controls

### Python Backend
- **processor.py**: Standalone Python script that processes text files
- Accepts command-line arguments: `input_filepath` and `output_filepath`
- Converts text content to uppercase
- Returns JSON-formatted results to stdout

### Communication Flow
1. User selects files through the Electron UI
2. Electron main process receives file paths via IPC
3. Main process spawns Python script with file paths as arguments
4. Python script processes the file and returns JSON result
5. Electron forwards the result back to the UI
6. UI displays processing status and results

## Development

### Running in Development Mode
```bash
NODE_ENV=development npm start
```
This will open the application with developer tools enabled.

### Testing Python Script Directly
```bash
python3 python_backend/processor.py input.txt output.txt
```

## Extending the Application

This project serves as a foundation for more complex document processing. You can extend it by:

1. **Adding more file formats**: Support for PDF, DOCX, etc.
2. **Advanced text processing**: Regex patterns, text masking, redaction
3. **Batch processing**: Process multiple files at once
4. **Progress tracking**: Real-time progress updates for large files
5. **Configuration**: User settings and preferences

## Troubleshooting

### Common Issues

1. **Python not found**: Ensure Python 3 is installed and accessible via `python3` command
2. **Permission errors**: Check file permissions for input/output directories
3. **Unicode errors**: Ensure text files are UTF-8 encoded

### Error Messages

The application provides detailed error messages in the status area:
- File not found errors
- Permission denied errors
- Unicode decoding errors
- Python process errors

## License

This project is open source and available under the ISC License.
