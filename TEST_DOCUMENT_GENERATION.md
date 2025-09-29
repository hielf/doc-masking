# Test Document Generation for Doc Masking

This document explains how to generate real-world test documents for your unit tests and estimate their output results.

## Overview

The test document generation system provides:

1. **Realistic Test Documents**: Generate `.txt` and `.pdf` files with realistic content containing various types of sensitive data
2. **Output Estimation**: Predict what the masking process will produce for each document
3. **Integration with Tests**: Use generated documents in your existing unit tests
4. **Comprehensive Testing**: Test all entity types and masking scenarios

## Files Created

- `python_backend/test_document_generator.py` - Core document generator
- `python_backend/test_runner_with_documents.py` - Enhanced test runner
- `generate_test_documents.py` - Main script to generate all documents
- `example_test_with_documents.py` - Example usage
- `test_documents/` - Directory containing generated test documents

## Quick Start

### 1. Generate Test Documents

```bash
python generate_test_documents.py
```

This will create:
- 8 different test documents in `test_documents/`
- Expected output estimates in `test_documents/test_expectations.json`
- Test results in `test_documents/test_results.json`
- A detailed report in `test_documents/test_report.md`

### 2. Run Example Tests

```bash
python example_test_with_documents.py
```

This demonstrates how to use the generated documents in your tests.

## Generated Test Documents

The system generates **16 test documents** - 8 in TXT format and 8 in PDF format:

### Text Documents (.txt)

#### 1. Basic Email Test (`basic_email_test.txt`)
- **Content**: Simple business email with name, email, and phone
- **Entities**: person_name, email, phone
- **Use Case**: Basic entity detection testing

#### 2. Contact Information Test (`contact_info_test.txt`)
- **Content**: Contact form with multiple entity types
- **Entities**: person_name, phone, address, email
- **Use Case**: Multi-entity detection testing

#### 3. Medical Record Test (`medical_record_test.txt`)
- **Content**: Medical record with PHI data
- **Entities**: person_name, mrn_or_insurance, government_id, icd10, cpt
- **Use Case**: Healthcare data masking testing

#### 4. System Log Test (`system_log_test.txt`)
- **Content**: System log with technical identifiers
- **Entities**: person_name, ipv4, mac, hostname, cookie, imei, meid, gps, itinerary
- **Use Case**: Technical metadata masking testing

#### 5. API Configuration Test (`api_config_test.txt`)
- **Content**: Configuration file with secrets and credentials
- **Entities**: credentials (API keys, JWT tokens, private keys)
- **Use Case**: Secret detection and masking testing

#### 6. Business Letter Test (`business_letter_test.txt`)
- **Content**: Formal business letter with addresses and names
- **Entities**: organization, address, person_name, phone, email
- **Use Case**: Business document masking testing

#### 7. Vehicle Registration Test (`vehicle_registration_test.txt`)
- **Content**: Vehicle registration form
- **Entities**: person_name, address, phone, email, vin, license_plate
- **Use Case**: Government document masking testing

#### 8. Comprehensive Test (`comprehensive_test.txt`)
- **Content**: Complex document with all major entity types
- **Entities**: All supported entity types
- **Use Case**: End-to-end masking testing

### PDF Documents (.pdf)

Each text document has a corresponding PDF version:

- `basic_email_test_pdf.pdf` - PDF version of basic email test
- `contact_info_test_pdf.pdf` - PDF version of contact info test
- `medical_record_test_pdf.pdf` - PDF version of medical record test
- `system_log_test_pdf.pdf` - PDF version of system log test
- `api_config_test_pdf.pdf` - PDF version of API config test
- `business_letter_test_pdf.pdf` - PDF version of business letter test
- `vehicle_registration_test_pdf.pdf` - PDF version of vehicle registration test
- `comprehensive_test_pdf.pdf` - PDF version of comprehensive test

**PDF Features:**
- Generated using ReportLab library
- Proper PDF formatting with fonts and layout
- Same content as TXT versions but in PDF format
- Tested for both generation and processing
- Support for PDF-specific masking operations

## Using Generated Documents in Tests

### Basic Usage

```python
from python_backend.test_document_generator import TestDocumentGenerator, OutputEstimator
from python_backend.processor import process_text_file

# Generate test documents
generator = TestDocumentGenerator()
documents = generator.generate_test_documents()

# Find specific test document
test_doc = None
for doc in documents:
    if doc.name == "basic_email_test":
        test_doc = doc
        break

# Process the document
with tempfile.TemporaryDirectory() as temp_dir:
    input_path = os.path.join(temp_dir, "input.txt")
    output_path = os.path.join(temp_dir, "output.txt")
    
    with open(input_path, 'w', encoding='utf-8') as f:
        f.write(test_doc.content)
    
    # Set environment variables
    os.environ["DOCMASK_ENTITY_POLICY"] = '{"entities": ["email", "phone", "person_name"]}'
    os.environ["DOCMASK_USE_DEFAULT_TEMPLATES"] = "true"
    os.environ["DOC_MASKING_ENV_KEY"] = "test_env_key"
    os.environ["DOC_MASKING_DOC_KEY"] = "test_doc_key"
    
    # Process
    result = process_text_file(input_path, output_path)
    
    # Get actual output
    with open(output_path, 'r', encoding='utf-8') as f:
        actual_output = f.read()
    
    # Compare with expected output
    estimator = OutputEstimator()
    expected_output = estimator.estimate_output(test_doc, preserve_length=False)
    
    print("Original:", test_doc.content)
    print("Actual:", actual_output)
    print("Expected:", expected_output)
```

### Advanced Usage with Test Runner

```python
from python_backend.test_runner_with_documents import EnhancedTestRunner

# Create test runner
runner = EnhancedTestRunner("test_documents")

# Run all tests
results = runner.run_all_tests()

# Generate report
report = runner.generate_test_report(results)
print(report)
```

## Output Estimation

The system provides two types of output estimation:

### 1. Template-based Masking
- Uses predefined templates for each entity type
- Example: `EMAIL_{hash8}@mask.local` for emails
- More realistic but may not match exact implementation

### 2. Length-preserving Masking
- Replaces sensitive data with 'x' characters
- Preserves original document length
- Useful for testing length preservation

## Entity Types Supported

The generator creates documents with these entity types:

- **Personal Information**: person_name, email, phone, address
- **Government IDs**: ssn, government_id, mrn_or_insurance
- **Financial**: credit_card, financial
- **Technical**: ipv4, ipv6, mac, hostname, cookie, imei, meid
- **Medical**: icd10, cpt, mrn_or_insurance
- **Legal**: vin, license_plate, organization
- **Location**: gps, itinerary
- **Credentials**: api_key, jwt_token, private_key, mnemonic

## Customizing Test Documents

### Adding New Entity Types

1. Add sample data to `_load_sample_data()` method
2. Create new test document generator method
3. Add to `generate_test_documents()` method

### Modifying Templates

Edit the `templates` dictionary in `OutputEstimator` class:

```python
self.templates = {
    "person_name": "NAME_{hash8}",
    "email": "EMAIL_{hash8}@mask.local",
    # Add your custom templates here
}
```

### Creating Custom Documents

```python
from python_backend.test_document_generator import TestDocument

custom_doc = TestDocument(
    name="my_custom_test",
    content="Your custom content here...",
    expected_entities=[
        {"type": "email", "start": 10, "end": 25},
        {"type": "phone", "start": 30, "end": 45}
    ],
    document_type="txt",
    description="My custom test document"
)
```

## Integration with Existing Tests

### Unit Test Integration

```python
def test_with_generated_document():
    generator = TestDocumentGenerator()
    documents = generator.generate_test_documents()
    
    # Use specific document for your test
    test_doc = next(doc for doc in documents if doc.name == "basic_email_test")
    
    # Your existing test logic here
    # ...
```

### CI/CD Integration

Add to your test pipeline:

```bash
# Generate test documents
python generate_test_documents.py

# Run your existing tests
python -m pytest python_backend/tests/

# Run enhanced tests
python python_backend/test_runner_with_documents.py
```

## PDF Support

PDF generation requires ReportLab:

```bash
pip install reportlab
```

Without ReportLab, PDF tests will be skipped but text tests will still work.

## Best Practices

1. **Use Realistic Data**: The generator uses realistic sample data to create more meaningful tests
2. **Test Edge Cases**: Create documents with unusual formatting or edge cases
3. **Validate Outputs**: Always compare actual vs expected outputs
4. **Update Regularly**: Regenerate documents periodically to test with fresh data
5. **Document Changes**: Keep track of what each test document is designed to test

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the repository root is in your Python path
2. **Missing Dependencies**: Install required packages (reportlab for PDF support)
3. **Permission Errors**: Ensure write permissions for the test_documents directory
4. **Template Mismatches**: Adjust templates in OutputEstimator to match your implementation

### Debug Mode

Enable debug output by setting environment variables:

```bash
export DOCMASK_DEBUG=1
python generate_test_documents.py
```

## Conclusion

The test document generation system provides a comprehensive way to test your doc masking implementation with realistic data. It helps ensure your masking works correctly across all supported entity types and provides a foundation for robust testing.

For questions or issues, refer to the generated test documents and examples in the `test_documents/` directory.
