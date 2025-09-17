#!/usr/bin/env python3
"""
Doc Masking Text Processor
Simple text processor that converts text files to uppercase.
"""

import sys
import json
import os

# Support running as a script (python python_backend/processor.py) and as a module
try:
    # When run with -m or when repo root is in sys.path
    from python_backend.pdf_processor import process_pdf_file  # type: ignore
except Exception:
    try:
        # When run from inside the package context
        from .pdf_processor import process_pdf_file  # type: ignore
    except Exception:
        # As a last resort, add repo root to sys.path and import again
        _current_dir = os.path.dirname(os.path.abspath(__file__))
        _repo_root = os.path.abspath(os.path.join(_current_dir, os.pardir))
        if _repo_root not in sys.path:
            sys.path.insert(0, _repo_root)
        from python_backend.pdf_processor import process_pdf_file  # type: ignore

def process_text_file(input_filepath, output_filepath):
    """
    Process a text file by converting its content to uppercase.
    
    Args:
        input_filepath (str): Path to the input text file
        output_filepath (str): Path to save the processed output file
    
    Returns:
        dict: Processing result with status and message
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_filepath):
            return {
                "status": "error",
                "message": f"Input file does not exist: {input_filepath}",
                "error": "FileNotFoundError"
            }
        
        # Read the input file
        with open(input_filepath, 'r', encoding='utf-8') as input_file:
            content = input_file.read()
        
        # Process the content (convert to uppercase)
        processed_content = content.upper()
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Write the processed content to output file
        with open(output_filepath, 'w', encoding='utf-8') as output_file:
            output_file.write(processed_content)
        
        return {
            "status": "success",
            "message": "File processed successfully!",
            "output": output_filepath,
            "input_file": input_filepath,
            "characters_processed": len(processed_content)
        }
        
    except PermissionError as e:
        return {
            "status": "error",
            "message": f"Permission denied: {str(e)}",
            "error": "PermissionError"
        }
    except UnicodeDecodeError as e:
        return {
            "status": "error",
            "message": f"Unable to decode file as UTF-8: {str(e)}",
            "error": "UnicodeDecodeError"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "error": type(e).__name__
        }


    

def main():
    """Main function to handle command line arguments and process the file."""
    if len(sys.argv) != 3:
        error_result = {
            "status": "error",
            "message": "Usage: python processor.py <input_filepath> <output_filepath>",
            "error": "InvalidArguments"
        }
        sys.stdout.write(json.dumps(error_result) + '\n')
        sys.stdout.flush()
        sys.exit(1)
    
    input_filepath = sys.argv[1]
    output_filepath = sys.argv[2]
    
    # Choose processor based on input file extension
    _, ext = os.path.splitext(input_filepath)
    ext = ext.lower()
    if ext == ".pdf":
        result = process_pdf_file(input_filepath, output_filepath)
    else:
        result = process_text_file(input_filepath, output_filepath)
    
    # Output the result as JSON
    sys.stdout.write(json.dumps(result) + '\n')
    sys.stdout.flush()
    
    # Exit with appropriate code
    if result["status"] == "success":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
