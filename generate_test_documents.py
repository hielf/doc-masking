#!/usr/bin/env python3
"""
Quick script to generate test documents and run enhanced tests.
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

def main():
    """Generate test documents and run tests."""
    print("Doc Masking - Test Document Generator")
    print("=" * 40)
    
    # Generate test documents
    print("\n1. Generating test documents...")
    generator = TestDocumentGenerator()
    file_paths = generator.save_test_documents("test_documents")
    
    print(f"Generated {len(file_paths)} test documents:")
    for name, path in file_paths.items():
        print(f"  - {name}: {path}")
    
    # Generate output estimates
    print("\n2. Generating output estimates...")
    documents = generator.generate_test_documents()
    estimator = OutputEstimator()
    expectations = estimator.generate_test_expectations(documents)
    
    # Save expectations
    import json
    expectations_path = "test_documents/test_expectations.json"
    with open(expectations_path, 'w', encoding='utf-8') as f:
        json.dump(expectations, f, indent=2)
    
    print(f"Saved expectations to: {expectations_path}")
    
    # Show sample expectations
    print("\n3. Sample expectations:")
    sample_docs = ["basic_email_test", "contact_info_test", "comprehensive_test"]
    
    for doc_name in sample_docs:
        if doc_name in expectations:
            print(f"\n--- {doc_name} ---")
            sample = expectations[doc_name]
            print("Original:")
            print(sample['original'][:200] + "..." if len(sample['original']) > 200 else sample['original'])
            print("\nExpected (template masking):")
            print(sample['masked_template'][:200] + "..." if len(sample['masked_template']) > 200 else sample['masked_template'])
    
    # Run enhanced tests
    print("\n4. Running enhanced tests...")
    runner = EnhancedTestRunner("test_documents")
    results = runner.run_all_tests()
    
    # Generate report
    print("\n5. Generating test report...")
    report = runner.generate_test_report(results)
    print("\n" + report)
    
    print(f"\nAll files saved in: test_documents/")
    print("Test documents, expectations, and results are ready for use!")

if __name__ == "__main__":
    main()
