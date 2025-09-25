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

def _load_entity_policy_from_env():
    """Load entity policy JSON from DOCMASK_ENTITY_POLICY env var."""
    raw = os.environ.get("DOCMASK_ENTITY_POLICY", "{}")
    try:
        policy = json.loads(raw)
        if not isinstance(policy, dict):
            return {}
        # normalize
        policy.setdefault("mask_all", False)
        entities = policy.get("entities", [])
        if not isinstance(entities, list):
            entities = []
        policy["entities"] = [str(e) for e in entities]
        return policy
    except Exception:
        return {}


def process_text_file(input_filepath, output_filepath, policy=None):
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
        
        from python_backend.detectors.rules import detect_entities_rules  # type: ignore
        from python_backend.detectors.ner import detect_entities_ner  # type: ignore
        from python_backend.detectors.address import detect_addresses  # type: ignore
        from python_backend.detectors.secrets import detect_secrets  # type: ignore
        from python_backend.detectors.identifiers import detect_identifiers  # type: ignore
        from python_backend.detectors.phi import detect_phi  # type: ignore
        from python_backend.detectors.domain import detect_domain_sensitive  # type: ignore
        from python_backend.aggregator import merge_overlaps, filter_by_policy  # type: ignore
        from python_backend.redaction import mask_text_spans  # type: ignore

        policy = policy or _load_entity_policy_from_env()
        if policy.get("mask_all"):
            import re as _re
            processed_content = _re.sub(r"[A-Za-z0-9]", "x", content)
        else:
            selected = policy.get("entities", []) or []
            entities = []
            # Run detectors
            entities.extend(detect_entities_rules(content, selected))
            try:
                entities.extend(detect_entities_ner(content, selected))
            except Exception:
                pass
            try:
                entities.extend(detect_addresses(content, selected))
            except Exception:
                pass
            try:
                entities.extend(detect_secrets(content, selected))
            except Exception:
                pass
            try:
                entities.extend(detect_identifiers(content, selected))
            except Exception:
                pass
            try:
                entities.extend(detect_phi(content, selected))
            except Exception:
                pass
            try:
                entities.extend(detect_domain_sensitive(content, selected))
            except Exception:
                pass
            entities = merge_overlaps(entities)
            entities = filter_by_policy(entities, policy)
            processed_content = mask_text_spans(content, entities)
        
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
    policy = _load_entity_policy_from_env()
    if ext == ".pdf":
        result = process_pdf_file(input_filepath, output_filepath, policy)
    else:
        result = process_text_file(input_filepath, output_filepath, policy)
    
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
