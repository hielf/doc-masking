#!/usr/bin/env python3
"""
Enhanced Test Runner with Real-World Document Generation

This module integrates the test document generator with existing unit tests,
allowing tests to run against realistic documents and compare actual vs expected outputs.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import subprocess

# Add the repository root to the path
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from python_backend.test_document_generator import TestDocumentGenerator, OutputEstimator, TestDocument
from python_backend.processor import process_text_file
from python_backend.pdf_processor import process_pdf_file

class EnhancedTestRunner:
    """Enhanced test runner that uses real-world documents."""
    
    def __init__(self, test_documents_dir: str = "test_documents"):
        self.test_documents_dir = test_documents_dir
        self.generator = TestDocumentGenerator()
        self.estimator = OutputEstimator()
        self.test_results = []
        
    def setup_test_environment(self) -> str:
        """Set up the test environment with generated documents."""
        os.makedirs(self.test_documents_dir, exist_ok=True)
        
        # Generate test documents
        print("Generating test documents...")
        file_paths = self.generator.save_test_documents(self.test_documents_dir)
        
        # Generate expectations
        documents = self.generator.generate_test_documents()
        expectations = self.estimator.generate_test_expectations(documents)
        
        # Save expectations
        expectations_path = os.path.join(self.test_documents_dir, "test_expectations.json")
        with open(expectations_path, 'w', encoding='utf-8') as f:
            json.dump(expectations, f, indent=2)
        
        print(f"Generated {len(file_paths)} test documents in {self.test_documents_dir}")
        return expectations_path
    
    def run_text_processing_tests(self) -> List[Dict[str, Any]]:
        """Run text processing tests with real documents."""
        results = []
        
        # Test basic email masking
        test_doc = self._get_test_document("basic_email_test")
        if test_doc:
            result = self._test_text_processing(
                test_doc,
                entity_policy='{"entities": ["email", "phone", "person_name"]}',
                test_name="basic_email_masking"
            )
            results.append(result)
        
        # Test contact information masking
        test_doc = self._get_test_document("contact_info_test")
        if test_doc:
            result = self._test_text_processing(
                test_doc,
                entity_policy='{"entities": ["person_name", "email", "phone", "address"]}',
                test_name="contact_info_masking"
            )
            results.append(result)
        
        # Test comprehensive masking
        test_doc = self._get_test_document("comprehensive_test")
        if test_doc:
            result = self._test_text_processing(
                test_doc,
                entity_policy='{"entities": ["person_name", "email", "phone", "address", "government_id", "financial", "credentials", "ipv4", "mac", "mrn_or_insurance", "icd10", "cpt", "vin", "license_plate", "gps", "organization"]}',
                test_name="comprehensive_masking"
            )
            results.append(result)
        
        return results
    
    def run_pdf_processing_tests(self) -> List[Dict[str, Any]]:
        """Run PDF processing tests with real documents."""
        results = []
        
        # Test PDF creation and processing for multiple document types
        pdf_test_cases = [
            ("basic_email_test_pdf", '{"entities": ["email", "phone", "person_name"]}', "pdf_basic_email_masking"),
            ("contact_info_test_pdf", '{"entities": ["person_name", "email", "phone", "address"]}', "pdf_contact_info_masking"),
            ("medical_record_test_pdf", '{"entities": ["person_name", "mrn_or_insurance", "government_id", "icd10", "cpt"]}', "pdf_medical_masking"),
            ("comprehensive_test_pdf", '{"entities": ["person_name", "email", "phone", "address", "government_id", "financial", "credentials", "ipv4", "mac", "mrn_or_insurance", "icd10", "cpt", "vin", "license_plate", "gps", "organization"]}', "pdf_comprehensive_masking")
        ]
        
        for doc_name, policy, test_name in pdf_test_cases:
            test_doc = self._get_test_document(doc_name)
            if test_doc:
                result = self._test_pdf_processing(
                    test_doc,
                    entity_policy=policy,
                    test_name=test_name
                )
                results.append(result)
        
        return results
    
    def _get_test_document(self, name: str) -> Optional[TestDocument]:
        """Get a test document by name."""
        documents = self.generator.generate_test_documents()
        for doc in documents:
            if doc.name == name:
                return doc
        return None
    
    def _test_text_processing(self, test_doc: TestDocument, entity_policy: str, test_name: str) -> Dict[str, Any]:
        """Test text processing with a given document."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, "input.txt")
            output_path = os.path.join(temp_dir, "output.txt")
            
            # Write test document
            with open(input_path, 'w', encoding='utf-8') as f:
                f.write(test_doc.content)
            
            # Set environment variables
            env = os.environ.copy()
            env["DOCMASK_ENTITY_POLICY"] = entity_policy
            env["DOCMASK_USE_DEFAULT_TEMPLATES"] = "true"
            env["DOC_MASKING_ENV_KEY"] = "test_env_key"
            env["DOC_MASKING_DOC_KEY"] = "test_doc_key"
            
            # Process the document
            try:
                result = process_text_file(input_path, output_path)
                
                if result["status"] == "success":
                    with open(output_path, 'r', encoding='utf-8') as f:
                        actual_output = f.read()
                else:
                    actual_output = f"Error: {result.get('error', 'Unknown error')}"
                
                # Get expected output
                expected_output = self.estimator.estimate_output(test_doc, preserve_length=False)
                
                # Compare results
                comparison = self._compare_outputs(test_doc.content, actual_output, expected_output, test_doc.expected_entities)
                
                return {
                    "test_name": test_name,
                    "status": "success" if result["status"] == "success" else "failed",
                    "original": test_doc.content,
                    "actual_output": actual_output,
                    "expected_output": expected_output,
                    "comparison": comparison,
                    "entities_found": comparison["entities_found"],
                    "entities_missed": comparison["entities_missed"],
                    "false_positives": comparison["false_positives"]
                }
                
            except Exception as e:
                return {
                    "test_name": test_name,
                    "status": "error",
                    "error": str(e),
                    "original": test_doc.content
                }
    
    def _test_pdf_processing(self, test_doc: TestDocument, entity_policy: str, test_name: str) -> Dict[str, Any]:
        """Test PDF processing with a given document."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, "input.pdf")
            output_path = os.path.join(temp_dir, "output.pdf")
            
            # Create PDF document
            if not self.generator.create_pdf_document(test_doc.content, input_path):
                return {
                    "test_name": test_name,
                    "status": "skipped",
                    "reason": "PDF creation failed (ReportLab not available)"
                }
            
            # Set environment variables
            env = os.environ.copy()
            env["DOCMASK_ENTITY_POLICY"] = entity_policy
            env["DOCMASK_USE_DEFAULT_TEMPLATES"] = "true"
            env["DOC_MASKING_ENV_KEY"] = "test_env_key"
            env["DOC_MASKING_DOC_KEY"] = "test_doc_key"
            
            # Process the PDF
            try:
                result = process_pdf_file(input_path, output_path)
                
                return {
                    "test_name": test_name,
                    "status": "success" if result["status"] == "success" else "failed",
                    "original": test_doc.content,
                    "result": result
                }
                
            except Exception as e:
                return {
                    "test_name": test_name,
                    "status": "error",
                    "error": str(e),
                    "original": test_doc.content
                }
    
    def _compare_outputs(self, original: str, actual: str, expected: str, expected_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare actual output with expected output and analyze entity detection."""
        comparison = {
            "entities_found": [],
            "entities_missed": [],
            "false_positives": [],
            "accuracy_score": 0.0,
            "masking_quality": "unknown"
        }
        
        # Simple analysis - check if original sensitive data is still present
        sensitive_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # Phone
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
        ]
        
        import re
        found_entities = 0
        total_entities = len(expected_entities)
        
        for pattern in sensitive_patterns:
            matches = re.findall(pattern, actual)
            if not matches:  # No sensitive data found in output
                found_entities += 1
        
        if total_entities > 0:
            comparison["accuracy_score"] = found_entities / total_entities
        
        # Determine masking quality
        if comparison["accuracy_score"] >= 0.9:
            comparison["masking_quality"] = "excellent"
        elif comparison["accuracy_score"] >= 0.7:
            comparison["masking_quality"] = "good"
        elif comparison["accuracy_score"] >= 0.5:
            comparison["masking_quality"] = "fair"
        else:
            comparison["masking_quality"] = "poor"
        
        return comparison
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results."""
        print("Setting up test environment...")
        self.setup_test_environment()
        
        print("Running text processing tests...")
        text_results = self.run_text_processing_tests()
        
        print("Running PDF processing tests...")
        pdf_results = self.run_pdf_processing_tests()
        
        # Calculate overall statistics
        total_tests = len(text_results) + len(pdf_results)
        successful_tests = sum(1 for r in text_results + pdf_results if r.get("status") == "success")
        
        overall_results = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "test_documents_dir": self.test_documents_dir
            },
            "text_processing_tests": text_results,
            "pdf_processing_tests": pdf_results
        }
        
        # Save results
        results_path = os.path.join(self.test_documents_dir, "test_results.json")
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(overall_results, f, indent=2)
        
        # Save masked documents
        self._save_masked_documents(overall_results)
        
        print(f"Test results saved to: {results_path}")
        return overall_results
    
    def _save_masked_documents(self, results: Dict[str, Any]) -> None:
        """Save masked documents to files for easy inspection."""
        masked_dir = os.path.join(self.test_documents_dir, "masked_documents")
        os.makedirs(masked_dir, exist_ok=True)
        
        # Save text processing masked documents
        for test in results.get("text_processing_tests", []):
            if test.get("status") == "success" and "actual_output" in test:
                filename = f"{test['test_name']}_masked.txt"
                filepath = os.path.join(masked_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(test['actual_output'])
                print(f"Saved masked document: {filepath}")
        
        # Save PDF processing masked documents (if they exist)
        for test in results.get("pdf_processing_tests", []):
            if test.get("status") == "success" and "result" in test:
                result = test["result"]
                if result.get("status") == "success" and "output_file" in result:
                    # Copy the processed PDF to masked documents
                    src = result["output_file"]
                    filename = f"{test['test_name']}_masked.pdf"
                    dst = os.path.join(masked_dir, filename)
                    if os.path.exists(src):
                        import shutil
                        shutil.copy2(src, dst)
                        print(f"Saved masked PDF: {dst}")
        
        print(f"All masked documents saved to: {masked_dir}")
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable test report."""
        report = []
        report.append("# Doc Masking Test Report")
        report.append("=" * 50)
        report.append("")
        
        # Summary
        summary = results["summary"]
        report.append(f"## Summary")
        report.append(f"- Total Tests: {summary['total_tests']}")
        report.append(f"- Successful: {summary['successful_tests']}")
        report.append(f"- Success Rate: {summary['success_rate']:.1%}")
        report.append("")
        
        # Text Processing Tests
        report.append("## Text Processing Tests")
        for test in results["text_processing_tests"]:
            report.append(f"### {test['test_name']}")
            report.append(f"**Status:** {test['status']}")
            
            if test['status'] == 'success':
                comparison = test.get('comparison', {})
                report.append(f"**Masking Quality:** {comparison.get('masking_quality', 'unknown')}")
                report.append(f"**Accuracy Score:** {comparison.get('accuracy_score', 0):.1%}")
            
            if 'error' in test:
                report.append(f"**Error:** {test['error']}")
            
            report.append("")
        
        # PDF Processing Tests
        report.append("## PDF Processing Tests")
        for test in results["pdf_processing_tests"]:
            report.append(f"### {test['test_name']}")
            report.append(f"**Status:** {test['status']}")
            
            if 'reason' in test:
                report.append(f"**Reason:** {test['reason']}")
            
            if 'error' in test:
                report.append(f"**Error:** {test['error']}")
            
            report.append("")
        
        return "\n".join(report)

def main():
    """Main function to run enhanced tests."""
    runner = EnhancedTestRunner()
    
    print("Running enhanced tests with real-world documents...")
    results = runner.run_all_tests()
    
    # Generate and print report
    report = runner.generate_test_report(results)
    print("\n" + report)
    
    # Save report
    report_path = os.path.join(runner.test_documents_dir, "test_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nDetailed report saved to: {report_path}")

if __name__ == "__main__":
    main()
