#!/usr/bin/env python3
"""
Dry-run CLI for Doc Masking

Provides command-line interface for generating dry-run reports without actually masking documents.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from python_backend.processor import process_text_file
from python_backend.pdf_processor import process_pdf_file
from python_backend.reports import generate_dry_run_report, save_reports


def load_policy(policy_path: str) -> dict:
    """Load policy from JSON file."""
    try:
        with open(policy_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load policy from {policy_path}: {e}")
        return {}


def detect_entities_only(input_filepath: str, policy: dict) -> tuple:
    """Detect entities without masking for dry-run purposes."""
    try:
        # Read the input file
        with open(input_filepath, 'r', encoding='utf-8') as input_file:
            content = input_file.read()
        
        from python_backend.detectors.rules import detect_entities_rules
        from python_backend.detectors.ner import detect_entities_ner
        from python_backend.detectors.address import detect_addresses
        from python_backend.detectors.secrets import detect_secrets
        from python_backend.detectors.identifiers import detect_identifiers
        from python_backend.detectors.phi import detect_phi
        from python_backend.detectors.domain import detect_domain_sensitive
        from python_backend.aggregator import merge_overlaps, filter_by_policy
        from python_backend.policy import validate_and_normalize_policy

        policy = validate_and_normalize_policy(policy)
        selected = policy.get("entities", []) or []
        entities = []
        
        # Run all detectors
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
        
        # Process entities
        entities = merge_overlaps(entities)
        entities = filter_by_policy(entities, policy)
        
        return entities, policy, content
        
    except Exception as e:
        print(f"[ERROR] Failed to detect entities: {e}")
        return [], {}, ""


def generate_dry_run_for_text(input_filepath: str, policy: dict, output_path: str) -> dict:
    """Generate dry-run report for text file."""
    entities, policy, content = detect_entities_only(input_filepath, policy)
    
    # Generate report
    report = generate_dry_run_report(
        document_path=input_filepath,
        document_type="text",
        entities=entities,
        policy=policy,
        masked_text=None  # No masking for dry-run
    )
    
    # Save reports
    saved_files = save_reports(report, output_path)
    
    return {
        "status": "success",
        "message": "Dry-run report generated successfully",
        "report_files": saved_files,
        "entities_found": len(entities),
        "entities_by_type": report.entities_by_type
    }


def generate_dry_run_for_pdf(input_filepath: str, policy: dict, output_path: str) -> dict:
    """Generate dry-run report for PDF file."""
    try:
        # For PDF, we'll use a simplified approach
        # In a full implementation, this would extract text and detect entities
        entities = []  # Placeholder - would need PDF text extraction
        
        report = generate_dry_run_report(
            document_path=input_filepath,
            document_type="pdf",
            entities=entities,
            policy=policy,
            masked_text=None
        )
        
        saved_files = save_reports(report, output_path)
        
        return {
            "status": "success",
            "message": "Dry-run report generated successfully",
            "report_files": saved_files,
            "entities_found": len(entities),
            "entities_by_type": report.entities_by_type
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate PDF dry-run report: {e}",
            "error": str(e)
        }


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Generate dry-run reports for document masking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate dry-run report for text file
  python dry_run_cli.py input.txt --policy policy.json --output reports/input_report
  
  # Generate dry-run report with default policy
  python dry_run_cli.py document.pdf --output reports/document_report
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Input file to analyze (TXT or PDF)"
    )
    
    parser.add_argument(
        "--policy", "-p",
        help="Path to policy JSON file (optional)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output path for reports (without extension)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["json", "csv", "both"],
        default="both",
        help="Report format (default: both)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"[ERROR] Input file does not exist: {args.input_file}")
        sys.exit(1)
    
    # Load policy
    policy = {}
    if args.policy:
        if not os.path.exists(args.policy):
            print(f"[ERROR] Policy file does not exist: {args.policy}")
            sys.exit(1)
        policy = load_policy(args.policy)
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        input_name = Path(args.input_file).stem
        output_path = f"reports/{input_name}_dry_run"
    
    # Determine file type
    file_ext = Path(args.input_file).suffix.lower()
    
    # Generate report
    if file_ext == '.pdf':
        result = generate_dry_run_for_pdf(args.input_file, policy, output_path)
    else:
        result = generate_dry_run_for_text(args.input_file, policy, output_path)
    
    # Print results
    if result["status"] == "success":
        print(f"[SUCCESS] {result['message']}")
        print(f"[INFO] Entities found: {result['entities_found']}")
        if result['entities_by_type']:
            print("[INFO] Entities by type:")
            for entity_type, count in result['entities_by_type'].items():
                print(f"  {entity_type}: {count}")
        
        if 'report_files' in result:
            print("[INFO] Report files generated:")
            for format_type, file_path in result['report_files'].items():
                print(f"  {format_type}: {file_path}")
    else:
        print(f"[ERROR] {result['message']}")
        if 'error' in result:
            print(f"[ERROR] Details: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
