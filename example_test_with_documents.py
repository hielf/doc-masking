#!/usr/bin/env python3
"""
Example of how to use generated test documents with existing unit tests.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the repository root to the path
repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from python_backend.test_document_generator import TestDocumentGenerator, OutputEstimator
from python_backend.processor import process_text_file

def example_basic_test():
    """Example of using generated documents in a basic test."""
    print("Example: Basic Test with Generated Document")
    print("=" * 50)
    
    # Generate a test document
    generator = TestDocumentGenerator()
    documents = generator.generate_test_documents()
    
    # Find the basic email test document
    test_doc = None
    for doc in documents:
        if doc.name == "basic_email_test":
            test_doc = doc
            break
    
    if not test_doc:
        print("Test document not found!")
        return
    
    print("Original document:")
    print(test_doc.content)
    print("\n" + "-" * 50)
    
    # Process the document
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.txt")
        output_path = os.path.join(temp_dir, "output.txt")
        
        # Write test document
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(test_doc.content)
        
        # Set environment variables for processing
        os.environ["DOCMASK_ENTITY_POLICY"] = '{"entities": ["email", "phone", "person_name"]}'
        os.environ["DOCMASK_USE_DEFAULT_TEMPLATES"] = "true"
        os.environ["DOC_MASKING_ENV_KEY"] = "test_env_key"
        os.environ["DOC_MASKING_DOC_KEY"] = "test_doc_key"
        
        # Process the document
        result = process_text_file(input_path, output_path)
        
        if result["status"] == "success":
            with open(output_path, 'r', encoding='utf-8') as f:
                actual_output = f.read()
            
            print("Processed document:")
            print(actual_output)
            
            # Compare with expected output
            estimator = OutputEstimator()
            expected_output = estimator.estimate_output(test_doc, preserve_length=False)
            
            print("\n" + "-" * 50)
            print("Expected output (estimated):")
            print(expected_output)
            
            # Simple comparison
            print("\n" + "-" * 50)
            print("Comparison:")
            print(f"Original length: {len(test_doc.content)}")
            print(f"Processed length: {len(actual_output)}")
            print(f"Expected length: {len(expected_output)}")
            
            # Check if sensitive data was masked
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            
            original_emails = re.findall(email_pattern, test_doc.content)
            processed_emails = re.findall(email_pattern, actual_output)
            
            original_phones = re.findall(phone_pattern, test_doc.content)
            processed_phones = re.findall(phone_pattern, actual_output)
            
            print(f"Original emails found: {len(original_emails)}")
            print(f"Processed emails found: {len(processed_emails)}")
            print(f"Original phones found: {len(original_phones)}")
            print(f"Processed phones found: {len(processed_phones)}")
            
            if len(processed_emails) == 0 and len(processed_phones) == 0:
                print("✅ SUCCESS: All sensitive data appears to be masked!")
            else:
                print("❌ WARNING: Some sensitive data may not be properly masked")
        
        else:
            print(f"Processing failed: {result.get('error', 'Unknown error')}")

def example_comprehensive_test():
    """Example of using a comprehensive test document."""
    print("\n\nExample: Comprehensive Test with Generated Document")
    print("=" * 60)
    
    # Generate a test document
    generator = TestDocumentGenerator()
    documents = generator.generate_test_documents()
    
    # Find the comprehensive test document
    test_doc = None
    for doc in documents:
        if doc.name == "comprehensive_test":
            test_doc = doc
            break
    
    if not test_doc:
        print("Comprehensive test document not found!")
        return
    
    print("Original document (first 500 chars):")
    print(test_doc.content[:500] + "...")
    print("\n" + "-" * 50)
    
    # Show expected entities
    print("Expected entities to be masked:")
    for i, entity in enumerate(test_doc.expected_entities[:10]):  # Show first 10
        entity_text = test_doc.content[entity['start']:entity['end']]
        print(f"  {i+1}. {entity['type']}: '{entity_text}'")
    
    if len(test_doc.expected_entities) > 10:
        print(f"  ... and {len(test_doc.expected_entities) - 10} more entities")
    
    # Process the document
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.txt")
        output_path = os.path.join(temp_dir, "output.txt")
        
        # Write test document
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(test_doc.content)
        
        # Set environment variables for comprehensive processing
        os.environ["DOCMASK_ENTITY_POLICY"] = '{"entities": ["person_name", "email", "phone", "address", "government_id", "financial", "credentials", "ipv4", "mac", "mrn_or_insurance", "icd10", "cpt", "vin", "license_plate", "gps", "organization"]}'
        os.environ["DOCMASK_USE_DEFAULT_TEMPLATES"] = "true"
        os.environ["DOC_MASKING_ENV_KEY"] = "test_env_key"
        os.environ["DOC_MASKING_DOC_KEY"] = "test_doc_key"
        
        # Process the document
        result = process_text_file(input_path, output_path)
        
        if result["status"] == "success":
            with open(output_path, 'r', encoding='utf-8') as f:
                actual_output = f.read()
            
            print("\nProcessed document (first 500 chars):")
            print(actual_output[:500] + "...")
            
            # Analyze masking effectiveness
            print("\n" + "-" * 50)
            print("Masking Analysis:")
            
            import re
            patterns = {
                "Email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                "Phone": r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
                "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
                "Credit Card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                "IP Address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
            }
            
            for pattern_name, pattern in patterns.items():
                original_count = len(re.findall(pattern, test_doc.content))
                processed_count = len(re.findall(pattern, actual_output))
                print(f"  {pattern_name}: {original_count} → {processed_count} (masked: {original_count - processed_count})")
        
        else:
            print(f"Processing failed: {result.get('error', 'Unknown error')}")

def main():
    """Run example tests."""
    print("Doc Masking - Example Tests with Generated Documents")
    print("=" * 60)
    
    # Run basic example
    example_basic_test()
    
    # Run comprehensive example
    example_comprehensive_test()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("\nTo generate all test documents and run full tests:")
    print("  python generate_test_documents.py")

if __name__ == "__main__":
    main()
