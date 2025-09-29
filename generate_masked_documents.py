#!/usr/bin/env python3
"""
Generate Masked Documents Script

This script generates masked versions of all test documents and saves them
to a dedicated directory for easy inspection and comparison.
"""

import os
import sys
from pathlib import Path

# Add the repository root to the path
repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from python_backend.test_document_generator import TestDocumentGenerator, OutputEstimator
from python_backend.test_runner_with_documents import EnhancedTestRunner

def generate_masked_documents():
    """Generate masked versions of all test documents."""
    print("[SECURE] Doc Masking - Generating Masked Documents")
    print("=" * 50)
    
    # Create test runner
    runner = EnhancedTestRunner("test_documents")
    
    # Generate test documents and run tests
    print("\n1. Generating test documents...")
    runner.setup_test_environment()
    
    print("\n2. Running masking tests...")
    results = runner.run_all_tests()
    
    # Generate additional masked documents for inspection
    print("\n3. Creating additional masked documents for inspection...")
    create_inspection_documents()
    
    print("\n[SUCCESS] Masked documents generation complete!")
    print(f"\n[INFO] Check out the masked documents in: test_documents/masked_documents/")
    
    return results

def create_inspection_documents():
    """Create additional masked documents for easy inspection."""
    generator = TestDocumentGenerator()
    estimator = OutputEstimator()
    
    # Create inspection directory
    inspection_dir = "test_documents/masked_documents/inspection"
    os.makedirs(inspection_dir, exist_ok=True)
    
    # Get all test documents
    documents = generator.generate_test_documents()
    
    # Create comparison documents
    for doc in documents:
        if doc.document_type == "txt":
            # Original document
            original_path = os.path.join(inspection_dir, f"{doc.name}_original.txt")
            with open(original_path, 'w', encoding='utf-8') as f:
                f.write(doc.content)
            
            # Expected masked output (template-based)
            expected_masked = estimator.estimate_output(doc, preserve_length=False)
            expected_path = os.path.join(inspection_dir, f"{doc.name}_expected_masked.txt")
            with open(expected_path, 'w', encoding='utf-8') as f:
                f.write(expected_masked)
            
            # Length-preserving masked output
            length_preserving = estimator.estimate_output(doc, preserve_length=True)
            length_path = os.path.join(inspection_dir, f"{doc.name}_length_preserving.txt")
            with open(length_path, 'w', encoding='utf-8') as f:
                f.write(length_preserving)
            
            print(f"  [FILE] {doc.name}: original, expected, length-preserving")
    
    # Create a summary document
    create_summary_document(inspection_dir, documents)

def create_summary_document(inspection_dir: str, documents: list):
    """Create a summary document with all test cases."""
    summary_path = os.path.join(inspection_dir, "SUMMARY.md")
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# Masked Documents Summary\n\n")
        f.write("This directory contains masked versions of all test documents for inspection.\n\n")
        
        f.write("## Document Types\n\n")
        f.write("For each test document, you'll find:\n")
        f.write("- `{name}_original.txt` - Original document with sensitive data\n")
        f.write("- `{name}_expected_masked.txt` - Expected masked output (template-based)\n")
        f.write("- `{name}_length_preserving.txt` - Length-preserving masked output\n\n")
        
        f.write("## Test Documents\n\n")
        for doc in documents:
            if doc.document_type == "txt":
                f.write(f"### {doc.name}\n")
                f.write(f"**Description:** {doc.description}\n")
                f.write(f"**Entity Types:** {', '.join(set(e['type'] for e in doc.expected_entities))}\n")
                f.write(f"**Expected Entities:** {len(doc.expected_entities)}\n\n")
        
        f.write("## How to Use\n\n")
        f.write("1. Compare `original` vs `expected_masked` to see what should be masked\n")
        f.write("2. Compare `original` vs `length_preserving` to see length-preserving masking\n")
        f.write("3. Use these documents to validate your masking implementation\n")
        f.write("4. Check the actual masked outputs in the parent directory\n\n")
        
        f.write("## File Locations\n\n")
        f.write("- **Test Results:** `../test_results.json`\n")
        f.write("- **Expected Outputs:** `../test_expectations.json`\n")
        f.write("- **Actual Masked:** `../` (files ending with `_masked.txt`)\n")
    
    print(f"  [SUMMARY] Summary document: {summary_path}")

def main():
    """Main function."""
    try:
        results = generate_masked_documents()
        
        # Show summary
        print("\n" + "=" * 50)
        print("[SUMMARY] SUMMARY")
        print("=" * 50)
        
        summary = results["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        
        print(f"\n[INFO] Masked documents saved to:")
        print(f"  - test_documents/masked_documents/ (actual test results)")
        print(f"  - test_documents/masked_documents/inspection/ (comparison documents)")
        
        print(f"\n[INFO] To inspect masked documents:")
        print(f"  - View: test_documents/masked_documents/")
        print(f"  - Compare: test_documents/masked_documents/inspection/")
        print(f"  - Results: test_documents/test_results.json")
        
    except Exception as e:
        print(f"[ERROR] Error generating masked documents: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
