#!/usr/bin/env python3
"""
Test Document Generator for Doc Masking

This module generates realistic test documents (.txt and .pdf) for unit tests
and provides output estimation capabilities to predict what the masking process will produce.
"""

import os
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

@dataclass
class TestDocument:
    """Represents a test document with content and expected entities."""
    name: str
    content: str
    expected_entities: List[Dict[str, Any]]
    document_type: str  # 'txt' or 'pdf'
    description: str

class TestDocumentGenerator:
    """Generates realistic test documents for various entity types."""
    
    def __init__(self):
        self.sample_data = self._load_sample_data()
        
    def _load_sample_data(self) -> Dict[str, List[str]]:
        """Load sample data for generating realistic documents."""
        return {
            "person_names": [
                "Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Emma Brown",
                "Frank Miller", "Grace Lee", "Henry Taylor", "Iris Garcia", "Jack Anderson",
                "Dr. Sarah Williams", "Prof. Michael Chen", "Ms. Jennifer Martinez"
            ],
            "emails": [
                "alice.johnson@company.com", "bob.smith@example.org", "carol.davis@techcorp.net",
                "david.wilson@startup.io", "emma.brown@consulting.com", "frank.miller@lawfirm.com",
                "grace.lee@hospital.org", "henry.taylor@university.edu", "iris.garcia@bank.com"
            ],
            "phones": [
                "(555) 123-4567", "555-987-6543", "+1-415-555-0123", "1-800-555-0199",
                "(212) 555-0100", "555.123.4567", "+44 20 7946 0958", "03-1234-5678"
            ],
            "addresses": [
                "123 Main Street, Anytown, CA 90210",
                "456 Oak Avenue, Springfield, IL 62701", 
                "789 Pine Road, Austin, TX 73301",
                "321 Elm Street, Boston, MA 02101",
                "654 Maple Drive, Seattle, WA 98101"
            ],
            "ssns": [
                "123-45-6789", "987-65-4321", "555-12-3456", "111-22-3333"
            ],
            "credit_cards": [
                "4532-1234-5678-9012", "5555-4444-3333-2222", "4111-1111-1111-1111",
                "6011-1111-1111-1111", "3782-822463-10005"
            ],
            "ip_addresses": [
                "192.168.1.100", "10.0.0.1", "172.16.0.1", "203.0.113.1",
                "2001:db8::1", "fe80::1ff:fe23:4567:890a"
            ],
            "mac_addresses": [
                "aa:bb:cc:dd:ee:ff", "00:11:22:33:44:55", "ff:ee:dd:cc:bb:aa"
            ],
            "urls": [
                "https://www.example.com", "http://api.service.org", "https://secure.bank.com/login",
                "ftp://files.company.net", "https://docs.google.com/document/123"
            ],
            "jwt_tokens": [
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tIiwiYXVkIjoiaHR0cHM6Ly9leGFtcGxlLm9yZyIsInN1YiI6IjEyMzQ1Njc4OTAifQ.signature"
            ],
            "api_keys": [
                "sk-1234567890abcdef1234567890abcdef12345678",
                "ghp_1234567890abcdef1234567890abcdef12345678",
                "AKIAIOSFODNN7EXAMPLE",
                "AIzaSyBOti4mM-6x9WDnZIjIey21JXK5h2U7Y0Y"
            ],
            "medical_codes": [
                "E11.9", "Z00", "99213", "93000", "ICD-10: F32.9", "CPT: 99201"
            ],
            "mrn_numbers": [
                "MRN123456", "ABC12345", "XYZ789012", "PATIENT-001"
            ],
            "vin_numbers": [
                "1HGBH41JXMN109186", "1FTFW1ET5DFC12345", "WBAFR9C50BC123456"
            ],
            "license_plates": [
                "ABC-1234", "XYZ-9876", "1ABC-234", "DEF-5678"
            ],
            "gps_coordinates": [
                "37.7749, -122.4194", "40.7128, -74.0060", "51.5074, -0.1278"
            ],
            "organizations": [
                "Acme Corporation", "Tech Solutions Inc", "Global Industries LLC",
                "Metropolitan Hospital", "State University", "First National Bank"
            ]
        }
    
    def generate_test_documents(self) -> List[TestDocument]:
        """Generate a comprehensive set of test documents."""
        documents = []
        
        # Basic entity detection tests
        documents.extend(self._generate_basic_entity_tests())
        
        # PHI (Protected Health Information) tests
        documents.extend(self._generate_phi_tests())
        
        # Identifier and metadata tests
        documents.extend(self._generate_identifier_tests())
        
        # Secret and credential tests
        documents.extend(self._generate_secret_tests())
        
        # Address and NER tests
        documents.extend(self._generate_address_ner_tests())
        
        # Domain-specific tests
        documents.extend(self._generate_domain_tests())
        
        # Complex multi-entity documents
        documents.extend(self._generate_complex_documents())
        
        # Generate PDF versions of all documents
        pdf_documents = []
        for doc in documents:
            pdf_doc = TestDocument(
                name=f"{doc.name}_pdf",
                content=doc.content,
                expected_entities=doc.expected_entities,
                document_type="pdf",
                description=f"PDF version of {doc.description}"
            )
            pdf_documents.append(pdf_doc)
        
        documents.extend(pdf_documents)
        return documents
    
    def _generate_basic_entity_tests(self) -> List[TestDocument]:
        """Generate basic entity detection test documents."""
        documents = []
        
        # Email test
        email_content = f"""
        Dear {random.choice(self.sample_data['person_names'])},
        
        Thank you for your inquiry. Please contact us at {random.choice(self.sample_data['emails'])} 
        or call {random.choice(self.sample_data['phones'])} for more information.
        
        Best regards,
        Customer Service
        """
        
        documents.append(TestDocument(
            name="basic_email_test",
            content=email_content.strip(),
            expected_entities=[
                {"type": "person_name", "start": 5, "end": 20},
                {"type": "email", "start": 100, "end": 125},
                {"type": "phone", "start": 150, "end": 165}
            ],
            document_type="txt",
            description="Basic email, phone, and name detection"
        ))
        
        # Phone and address test
        contact_content = f"""
        Contact Information:
        Name: {random.choice(self.sample_data['person_names'])}
        Phone: {random.choice(self.sample_data['phones'])}
        Address: {random.choice(self.sample_data['addresses'])}
        Email: {random.choice(self.sample_data['emails'])}
        """
        
        documents.append(TestDocument(
            name="contact_info_test",
            content=contact_content.strip(),
            expected_entities=[
                {"type": "person_name", "start": 20, "end": 35},
                {"type": "phone", "start": 45, "end": 60},
                {"type": "address", "start": 70, "end": 100},
                {"type": "email", "start": 110, "end": 135}
            ],
            document_type="txt",
            description="Contact information with multiple entity types"
        ))
        
        return documents
    
    def _generate_phi_tests(self) -> List[TestDocument]:
        """Generate PHI (Protected Health Information) test documents."""
        documents = []
        
        # Medical record test
        medical_content = f"""
        PATIENT RECORD
        ==============
        
        Patient: {random.choice(self.sample_data['person_names'])}
        MRN: {random.choice(self.sample_data['mrn_numbers'])}
        DOB: 01/15/1985
        SSN: {random.choice(self.sample_data['ssns'])}
        
        DIAGNOSIS:
        - Type 2 Diabetes (E11.9)
        - Annual Physical (Z00)
        
        PROCEDURES:
        - Office Visit (CPT: 99213)
        - EKG (CPT: 93000)
        
        Provider: Dr. {random.choice(self.sample_data['person_names'])}
        Date: {datetime.now().strftime('%m/%d/%Y')}
        """
        
        documents.append(TestDocument(
            name="medical_record_test",
            content=medical_content.strip(),
            expected_entities=[
                {"type": "person_name", "start": 25, "end": 40},
                {"type": "mrn_or_insurance", "start": 50, "end": 65},
                {"type": "government_id", "start": 85, "end": 95},
                {"type": "icd10", "start": 120, "end": 125},
                {"type": "cpt", "start": 150, "end": 155},
                {"type": "person_name", "start": 180, "end": 195}
            ],
            document_type="txt",
            description="Medical record with PHI including diagnoses and procedures"
        ))
        
        return documents
    
    def _generate_identifier_tests(self) -> List[TestDocument]:
        """Generate identifier and metadata test documents."""
        documents = []
        
        # System log test
        log_content = f"""
        SYSTEM LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        ================================================
        
        User: {random.choice(self.sample_data['person_names'])}
        IP: {random.choice(self.sample_data['ip_addresses'])}
        MAC: {random.choice(self.sample_data['mac_addresses'])}
        Host: {random.choice(self.sample_data['urls']).split('//')[1].split('/')[0]}
        Session: sessionid={random.choice(self.sample_data['api_keys'])[:20]}
        IMEI: {random.choice(['490154203237518', '123456789012345'])}
        MEID: A10000009296F1
        
        GPS Location: {random.choice(self.sample_data['gps_coordinates'])}
        Flight: 2025-10-01 departure 08:00
        """
        
        documents.append(TestDocument(
            name="system_log_test",
            content=log_content.strip(),
            expected_entities=[
                {"type": "person_name", "start": 50, "end": 65},
                {"type": "ipv4", "start": 75, "end": 90},
                {"type": "mac", "start": 100, "end": 115},
                {"type": "hostname", "start": 125, "end": 140},
                {"type": "cookie", "start": 150, "end": 170},
                {"type": "imei", "start": 180, "end": 195},
                {"type": "meid", "start": 205, "end": 220},
                {"type": "gps", "start": 240, "end": 255},
                {"type": "itinerary", "start": 265, "end": 285}
            ],
            document_type="txt",
            description="System log with various identifiers and metadata"
        ))
        
        return documents
    
    def _generate_secret_tests(self) -> List[TestDocument]:
        """Generate secret and credential test documents."""
        documents = []
        
        # API configuration test
        config_content = f"""
        # API Configuration
        OPENAI_API_KEY={random.choice(self.sample_data['api_keys'])}
        GITHUB_TOKEN={random.choice(self.sample_data['api_keys'])}
        AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
        AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
        
        # Database
        DATABASE_URL=postgresql://user:password@localhost:5432/db
        JWT_SECRET=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
        
        # Crypto
        WIF_PRIVATE_KEY=5KJvsngHeMpm884wtkJQQLc2Wb1wUf7zLgSai4y3XfotjLDQJTH
        ETH_PRIVATE_KEY=0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
        MNEMONIC=abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
        """
        
        documents.append(TestDocument(
            name="api_config_test",
            content=config_content.strip(),
            expected_entities=[
                {"type": "credentials", "start": 30, "end": 80},
                {"type": "credentials", "start": 100, "end": 150},
                {"type": "credentials", "start": 170, "end": 200},
                {"type": "credentials", "start": 220, "end": 270},
                {"type": "credentials", "start": 290, "end": 340},
                {"type": "credentials", "start": 360, "end": 450},
                {"type": "credentials", "start": 470, "end": 520},
                {"type": "credentials", "start": 540, "end": 590},
                {"type": "credentials", "start": 610, "end": 660}
            ],
            document_type="txt",
            description="API configuration file with various secrets and credentials"
        ))
        
        return documents
    
    def _generate_address_ner_tests(self) -> List[TestDocument]:
        """Generate address and NER test documents."""
        documents = []
        
        # Business letter test
        letter_content = f"""
        {random.choice(self.sample_data['organizations'])}
        {random.choice(self.sample_data['addresses'])}
        
        {datetime.now().strftime('%B %d, %Y')}
        
        Dear {random.choice(self.sample_data['person_names'])},
        
        We are pleased to inform you that your application has been approved.
        Please visit our office at {random.choice(self.sample_data['addresses'])} 
        to complete the process.
        
        If you have any questions, please contact {random.choice(self.sample_data['person_names'])} 
        at {random.choice(self.sample_data['phones'])} or {random.choice(self.sample_data['emails'])}.
        
        Sincerely,
        {random.choice(self.sample_data['person_names'])}
        {random.choice(self.sample_data['organizations'])}
        """
        
        documents.append(TestDocument(
            name="business_letter_test",
            content=letter_content.strip(),
            expected_entities=[
                {"type": "organization", "start": 0, "end": 20},
                {"type": "address", "start": 25, "end": 55},
                {"type": "person_name", "start": 80, "end": 95},
                {"type": "address", "start": 200, "end": 230},
                {"type": "person_name", "start": 250, "end": 265},
                {"type": "phone", "start": 285, "end": 300},
                {"type": "email", "start": 310, "end": 335},
                {"type": "person_name", "start": 350, "end": 365},
                {"type": "organization", "start": 370, "end": 390}
            ],
            document_type="txt",
            description="Business letter with addresses, names, and contact information"
        ))
        
        return documents
    
    def _generate_domain_tests(self) -> List[TestDocument]:
        """Generate domain-specific test documents."""
        documents = []
        
        # Vehicle registration test
        vehicle_content = f"""
        VEHICLE REGISTRATION
        ====================
        
        Owner: {random.choice(self.sample_data['person_names'])}
        Address: {random.choice(self.sample_data['addresses'])}
        Phone: {random.choice(self.sample_data['phones'])}
        Email: {random.choice(self.sample_data['emails'])}
        
        Vehicle Information:
        VIN: {random.choice(self.sample_data['vin_numbers'])}
        License Plate: {random.choice(self.sample_data['license_plates'])}
        Year: 2020
        Make: Toyota
        Model: Camry
        
        Registration Date: {datetime.now().strftime('%m/%d/%Y')}
        Expiration: {datetime(datetime.now().year + 1, 1, 1).strftime('%m/%d/%Y')}
        """
        
        documents.append(TestDocument(
            name="vehicle_registration_test",
            content=vehicle_content.strip(),
            expected_entities=[
                {"type": "person_name", "start": 30, "end": 45},
                {"type": "address", "start": 55, "end": 85},
                {"type": "phone", "start": 95, "end": 110},
                {"type": "email", "start": 120, "end": 145},
                {"type": "vin", "start": 180, "end": 200},
                {"type": "license_plate", "start": 220, "end": 230}
            ],
            document_type="txt",
            description="Vehicle registration with VIN, license plate, and owner information"
        ))
        
        return documents
    
    def _generate_complex_documents(self) -> List[TestDocument]:
        """Generate complex multi-entity documents."""
        documents = []
        
        # Comprehensive test document
        complex_content = f"""
        CONFIDENTIAL DOCUMENT
        =====================
        
        Client: {random.choice(self.sample_data['person_names'])}
        Case ID: CASE-{random.randint(1000, 9999)}
        Date: {datetime.now().strftime('%m/%d/%Y')}
        
        Personal Information:
        - Full Name: {random.choice(self.sample_data['person_names'])}
        - SSN: {random.choice(self.sample_data['ssns'])}
        - DOB: 03/15/1980
        - Address: {random.choice(self.sample_data['addresses'])}
        - Phone: {random.choice(self.sample_data['phones'])}
        - Email: {random.choice(self.sample_data['emails'])}
        
        Financial Information:
        - Credit Card: {random.choice(self.sample_data['credit_cards'])}
        - Bank Account: 1234567890
        - Routing Number: 021000021
        
        Technical Details:
        - IP Address: {random.choice(self.sample_data['ip_addresses'])}
        - MAC Address: {random.choice(self.sample_data['mac_addresses'])}
        - API Key: {random.choice(self.sample_data['api_keys'])}
        - JWT Token: {random.choice(self.sample_data['jwt_tokens'])}
        
        Medical Information:
        - MRN: {random.choice(self.sample_data['mrn_numbers'])}
        - Diagnosis: E11.9 (Type 2 Diabetes)
        - Procedure: 99213 (Office Visit)
        
        Legal Information:
        - VIN: {random.choice(self.sample_data['vin_numbers'])}
        - License Plate: {random.choice(self.sample_data['license_plates'])}
        - Attorney: {random.choice(self.sample_data['person_names'])}
        - Law Firm: {random.choice(self.sample_data['organizations'])}
        
        Location Data:
        - GPS: {random.choice(self.sample_data['gps_coordinates'])}
        - Travel: Flight 2025-10-01 departure 08:00
        
        This document contains sensitive information that must be protected.
        """
        
        documents.append(TestDocument(
            name="comprehensive_test",
            content=complex_content.strip(),
            expected_entities=[
                {"type": "person_name", "start": 30, "end": 45},
                {"type": "person_name", "start": 80, "end": 95},
                {"type": "government_id", "start": 110, "end": 120},
                {"type": "address", "start": 140, "end": 170},
                {"type": "phone", "start": 180, "end": 195},
                {"type": "email", "start": 205, "end": 230},
                {"type": "financial", "start": 250, "end": 270},
                {"type": "ipv4", "start": 300, "end": 315},
                {"type": "mac", "start": 330, "end": 345},
                {"type": "credentials", "start": 360, "end": 400},
                {"type": "credentials", "start": 420, "end": 500},
                {"type": "mrn_or_insurance", "start": 520, "end": 535},
                {"type": "icd10", "start": 560, "end": 565},
                {"type": "cpt", "start": 580, "end": 585},
                {"type": "vin", "start": 610, "end": 630},
                {"type": "license_plate", "start": 650, "end": 660},
                {"type": "person_name", "start": 680, "end": 695},
                {"type": "organization", "start": 710, "end": 730},
                {"type": "gps", "start": 750, "end": 765},
                {"type": "itinerary", "start": 775, "end": 795}
            ],
            document_type="txt",
            description="Comprehensive document with all major entity types"
        ))
        
        return documents
    
    def create_pdf_document(self, content: str, output_path: str) -> bool:
        """Create a PDF document from text content."""
        if not REPORTLAB_AVAILABLE:
            print("ReportLab not available. Cannot create PDF documents.")
            return False
        
        try:
            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter
            
            # Split content into lines and draw them
            lines = content.split('\n')
            y_position = height - 50
            
            for line in lines:
                if y_position < 50:  # Start new page if needed
                    c.showPage()
                    y_position = height - 50
                
                c.drawString(50, y_position, line[:80])  # Limit line length
                y_position -= 15
            
            c.save()
            return True
        except Exception as e:
            print(f"Error creating PDF: {e}")
            return False
    
    def save_test_documents(self, output_dir: str = "test_documents") -> Dict[str, str]:
        """Save all test documents to files and return file paths."""
        os.makedirs(output_dir, exist_ok=True)
        file_paths = {}
        
        documents = self.generate_test_documents()
        
        for doc in documents:
            if doc.document_type == "txt":
                file_path = os.path.join(output_dir, f"{doc.name}.txt")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(doc.content)
                file_paths[doc.name] = file_path
                
            elif doc.document_type == "pdf":
                file_path = os.path.join(output_dir, f"{doc.name}.pdf")
                if self.create_pdf_document(doc.content, file_path):
                    file_paths[doc.name] = file_path
        
        # Save metadata
        metadata_path = os.path.join(output_dir, "test_documents_metadata.json")
        metadata = []
        for doc in documents:
            metadata.append({
                "name": doc.name,
                "description": doc.description,
                "document_type": doc.document_type,
                "expected_entities": doc.expected_entities,
                "file_path": file_paths.get(doc.name, "")
            })
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return file_paths

class OutputEstimator:
    """Estimates what the masking process will produce for given documents."""
    
    def __init__(self):
        self.templates = {
            "person_name": "NAME_{hash8}",
            "email": "EMAIL_{hash8}@mask.local", 
            "phone": "PHONE_{hash6}_{orig_last:4}",
            "address": "ADDRESS_{hash8}",
            "ssn": "SSN_{hash6}_{orig_last:4}",
            "credit_card": "CARD_{hash6}_{orig_last:4}",
            "ipv4": "IP_{hash6}",
            "mac": "MAC_{hash6}",
            "credentials": "",  # Full redaction
            "government_id": "ID_{hash6}_{orig_last:4}",
            "vin": "VIN_{hash8}",
            "license_plate": "PLATE_{hash6}",
            "gps": "LOC_{hash6}",
            "mrn_or_insurance": "MRN_{hash6}",
            "icd10": "ICD_{hash6}",
            "cpt": "CPT_{hash6}",
            "organization": "ORG_{hash8}",
            "hostname": "HOST_{hash6}",
            "cookie": "COOKIE_{hash6}",
            "imei": "IMEI_{hash6}",
            "meid": "MEID_{hash6}",
            "itinerary": "TRAVEL_{hash6}"
        }
    
    def estimate_output(self, document: TestDocument, preserve_length: bool = False) -> str:
        """Estimate what the masked output will look like."""
        content = document.content
        entities = document.expected_entities
        
        # Sort entities by start position in reverse order to avoid offset issues
        entities = sorted(entities, key=lambda x: x['start'], reverse=True)
        
        for entity in entities:
            entity_type = entity['type']
            start = entity['start']
            end = entity['end']
            original_text = content[start:end]
            
            if preserve_length:
                # Replace with 'x' characters to preserve length
                masked_text = 'x' * (end - start)
            else:
                # Use template-based masking
                template = self.templates.get(entity_type, "MASKED_{hash6}")
                masked_text = self._apply_template(template, original_text, entity_type)
            
            content = content[:start] + masked_text + content[end:]
        
        return content
    
    def _apply_template(self, template: str, original_text: str, entity_type: str) -> str:
        """Apply a template to generate masked text."""
        import hashlib
        
        # Generate a simple hash for demonstration
        hash_input = f"{entity_type}_{original_text}".encode('utf-8')
        hash_hex = hashlib.md5(hash_input).hexdigest()
        
        # Replace template tokens
        result = template
        result = result.replace("{hash6}", hash_hex[:6])
        result = result.replace("{hash8}", hash_hex[:8])
        result = result.replace("{hash40}", hash_hex)
        
        # Handle orig_last token
        if "{orig_last:" in result:
            import re
            match = re.search(r"\{orig_last:(\d+)\}", result)
            if match:
                last_chars = int(match.group(1))
                result = result.replace(match.group(0), original_text[-last_chars:])
        
        return result
    
    def generate_test_expectations(self, documents: List[TestDocument]) -> Dict[str, Dict[str, str]]:
        """Generate expected outputs for all test documents."""
        expectations = {}
        
        for doc in documents:
            expectations[doc.name] = {
                "original": doc.content,
                "masked_preserve_length": self.estimate_output(doc, preserve_length=True),
                "masked_template": self.estimate_output(doc, preserve_length=False),
                "expected_entities": doc.expected_entities
            }
        
        return expectations

def main():
    """Main function to generate test documents and estimates."""
    generator = TestDocumentGenerator()
    estimator = OutputEstimator()
    
    print("Generating test documents...")
    file_paths = generator.save_test_documents()
    
    print(f"Generated {len(file_paths)} test documents:")
    for name, path in file_paths.items():
        print(f"  {name}: {path}")
    
    print("\nGenerating output estimates...")
    documents = generator.generate_test_documents()
    expectations = estimator.generate_test_expectations(documents)
    
    # Save expectations
    expectations_path = "test_documents/test_expectations.json"
    with open(expectations_path, 'w', encoding='utf-8') as f:
        json.dump(expectations, f, indent=2)
    
    print(f"Saved expectations to: {expectations_path}")
    
    # Print sample expectations
    print("\nSample expectations for 'basic_email_test':")
    sample = expectations['basic_email_test']
    print("Original:")
    print(sample['original'])
    print("\nMasked (preserve length):")
    print(sample['masked_preserve_length'])
    print("\nMasked (template):")
    print(sample['masked_template'])

if __name__ == "__main__":
    main()
