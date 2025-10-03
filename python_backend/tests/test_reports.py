#!/usr/bin/env python3
"""
Unit tests for the reports module.
"""

import unittest
import tempfile
import os
import json
import csv
from datetime import datetime
from unittest.mock import patch

# Add the parent directory to sys.path to import modules
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from python_backend.reports import (
    EntityReport, ProcessingReport, ReportGenerator,
    generate_dry_run_report, save_reports
)


class TestEntityReport(unittest.TestCase):
    """Test EntityReport dataclass."""
    
    def test_entity_report_creation(self):
        """Test creating an EntityReport."""
        entity = EntityReport(
            entity_id="email_0001",
            entity_type="email",
            start=10,
            end=25,
            text="test@example.com",
            masked_text="EMAIL_abc123@mask.local",
            action="pseudonymize",
            confidence=0.95,
            source="rules",
            page_number=1,
            span_id="span_001"
        )
        
        self.assertEqual(entity.entity_id, "email_0001")
        self.assertEqual(entity.entity_type, "email")
        self.assertEqual(entity.start, 10)
        self.assertEqual(entity.end, 25)
        self.assertEqual(entity.text, "test@example.com")
        self.assertEqual(entity.masked_text, "EMAIL_abc123@mask.local")
        self.assertEqual(entity.action, "pseudonymize")
        self.assertEqual(entity.confidence, 0.95)
        self.assertEqual(entity.source, "rules")
        self.assertEqual(entity.page_number, 1)
        self.assertEqual(entity.span_id, "span_001")


class TestProcessingReport(unittest.TestCase):
    """Test ProcessingReport dataclass."""
    
    def test_processing_report_creation(self):
        """Test creating a ProcessingReport."""
        entities = [
            EntityReport(
                entity_id="email_0001",
                entity_type="email",
                start=10,
                end=25,
                text="test@example.com",
                masked_text="EMAIL_abc123@mask.local",
                action="pseudonymize",
                confidence=0.95,
                source="rules"
            )
        ]
        
        report = ProcessingReport(
            document_path="/path/to/test.txt",
            document_type="text",
            processing_timestamp="2025-01-27T10:00:00",
            total_entities=1,
            entities_by_type={"email": 1},
            actions_applied={"pseudonymize": 1},
            total_characters=100,
            masked_characters=20,
            entities=entities,
            policy_used={"entities": ["email"]},
            processing_time_ms=150.5,
            errors=[]
        )
        
        self.assertEqual(report.document_path, "/path/to/test.txt")
        self.assertEqual(report.document_type, "text")
        self.assertEqual(report.total_entities, 1)
        self.assertEqual(report.entities_by_type, {"email": 1})
        self.assertEqual(report.actions_applied, {"pseudonymize": 1})
        self.assertEqual(report.total_characters, 100)
        self.assertEqual(report.masked_characters, 20)
        self.assertEqual(len(report.entities), 1)
        self.assertEqual(report.processing_time_ms, 150.5)


class TestReportGenerator(unittest.TestCase):
    """Test ReportGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ReportGenerator()
    
    def test_generate_entity_id(self):
        """Test entity ID generation."""
        id1 = self.generator.generate_entity_id("email")
        id2 = self.generator.generate_entity_id("phone")
        id3 = self.generator.generate_entity_id("email")
        
        self.assertEqual(id1, "email_0001")
        self.assertEqual(id2, "phone_0002")
        self.assertEqual(id3, "email_0003")
    
    def test_create_entity_report(self):
        """Test creating an entity report."""
        entity = {
            "type": "email",
            "start": 10,
            "end": 25,
            "text": "test@example.com",
            "score": 0.95,
            "source": "rules"
        }
        
        report = self.generator.create_entity_report(
            entity=entity,
            masked_text="EMAIL_abc123@mask.local",
            action="pseudonymize",
            page_number=1,
            span_id="span_001"
        )
        
        self.assertEqual(report.entity_type, "email")
        self.assertEqual(report.start, 10)
        self.assertEqual(report.end, 25)
        self.assertEqual(report.text, "test@example.com")
        self.assertEqual(report.masked_text, "EMAIL_abc123@mask.local")
        self.assertEqual(report.action, "pseudonymize")
        self.assertEqual(report.confidence, 0.95)
        self.assertEqual(report.source, "rules")
        self.assertEqual(report.page_number, 1)
        self.assertEqual(report.span_id, "span_001")
    
    def test_determine_action(self):
        """Test action determination based on policy."""
        policy = {
            "actions": {
                "email": {"action": "pseudonymize"},
                "phone": {"action": "remove"},
                "address": {"action": "placeholder"}
            }
        }
        
        self.assertEqual(self.generator._determine_action("email", policy), "pseudonymize")
        self.assertEqual(self.generator._determine_action("phone", policy), "remove")
        self.assertEqual(self.generator._determine_action("address", policy), "placeholder")
        self.assertEqual(self.generator._determine_action("unknown", policy), "mask")
    
    def test_generate_dry_run_report(self):
        """Test generating a dry-run report."""
        entities = [
            {
                "type": "email",
                "start": 10,
                "end": 25,
                "text": "test@example.com",
                "score": 0.95,
                "source": "rules"
            },
            {
                "type": "phone",
                "start": 30,
                "end": 42,
                "text": "555-123-4567",
                "score": 0.90,
                "source": "rules"
            }
        ]
        
        policy = {
            "entities": ["email", "phone"],
            "actions": {
                "email": {"action": "pseudonymize"},
                "phone": {"action": "remove"}
            }
        }
        
        report = self.generator.generate_dry_run_report(
            document_path="/path/to/test.txt",
            document_type="text",
            entities=entities,
            policy=policy,
            masked_text="test@example.com 555-123-4567",
            processing_time_ms=150.5
        )
        
        self.assertEqual(report.document_path, "/path/to/test.txt")
        self.assertEqual(report.document_type, "text")
        self.assertEqual(report.total_entities, 2)
        self.assertEqual(report.entities_by_type, {"email": 1, "phone": 1})
        self.assertEqual(report.actions_applied, {"pseudonymize": 1, "remove": 1})
        self.assertEqual(len(report.entities), 2)
        self.assertEqual(report.processing_time_ms, 150.5)
    
    def test_save_json_report(self):
        """Test saving JSON report."""
        entities = [
            EntityReport(
                entity_id="email_0001",
                entity_type="email",
                start=10,
                end=25,
                text="test@example.com",
                masked_text="EMAIL_abc123@mask.local",
                action="pseudonymize",
                confidence=0.95,
                source="rules"
            )
        ]
        
        report = ProcessingReport(
            document_path="/path/to/test.txt",
            document_type="text",
            processing_timestamp="2025-01-27T10:00:00",
            total_entities=1,
            entities_by_type={"email": 1},
            actions_applied={"pseudonymize": 1},
            total_characters=100,
            masked_characters=20,
            entities=entities,
            policy_used={"entities": ["email"]},
            processing_time_ms=150.5,
            errors=[]
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_report.json")
            self.generator.save_json_report(report, output_path)
            
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.assertEqual(data["document_path"], "/path/to/test.txt")
            self.assertEqual(data["total_entities"], 1)
            self.assertEqual(len(data["entities"]), 1)
    
    def test_save_csv_report(self):
        """Test saving CSV report."""
        entities = [
            EntityReport(
                entity_id="email_0001",
                entity_type="email",
                start=10,
                end=25,
                text="test@example.com",
                masked_text="EMAIL_abc123@mask.local",
                action="pseudonymize",
                confidence=0.95,
                source="rules"
            )
        ]
        
        report = ProcessingReport(
            document_path="/path/to/test.txt",
            document_type="text",
            processing_timestamp="2025-01-27T10:00:00",
            total_entities=1,
            entities_by_type={"email": 1},
            actions_applied={"pseudonymize": 1},
            total_characters=100,
            masked_characters=20,
            entities=entities,
            policy_used={"entities": ["email"]},
            processing_time_ms=150.5,
            errors=[]
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_report.csv")
            self.generator.save_csv_report(report, output_path)
            
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Check header
            self.assertEqual(rows[0], [
                'Entity ID', 'Entity Type', 'Start', 'End', 'Text', 'Masked Text',
                'Action', 'Confidence', 'Source', 'Page Number', 'Span ID'
            ])
            
            # Check data row
            self.assertEqual(rows[1], [
                'email_0001', 'email', '10', '25', 'test@example.com',
                'EMAIL_abc123@mask.local', 'pseudonymize', '0.95', 'rules', '', ''
            ])
    
    def test_save_summary_csv(self):
        """Test saving summary CSV report."""
        report = ProcessingReport(
            document_path="/path/to/test.txt",
            document_type="text",
            processing_timestamp="2025-01-27T10:00:00",
            total_entities=2,
            entities_by_type={"email": 1, "phone": 1},
            actions_applied={"pseudonymize": 1, "remove": 1},
            total_characters=100,
            masked_characters=20,
            entities=[],
            policy_used={"entities": ["email", "phone"]},
            processing_time_ms=150.5,
            errors=[]
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_summary.csv")
            self.generator.save_summary_csv(report, output_path)
            
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Check summary header
            self.assertEqual(rows[0], [
                'Document Path', 'Document Type', 'Processing Timestamp',
                'Total Entities', 'Total Characters', 'Masked Characters',
                'Processing Time (ms)', 'Errors'
            ])
            
            # Check summary data
            self.assertEqual(rows[1], [
                '/path/to/test.txt', 'text', '2025-01-27T10:00:00',
                '2', '100', '20', '150.5', ''
            ])


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    def test_generate_dry_run_report_function(self):
        """Test the generate_dry_run_report convenience function."""
        entities = [
            {
                "type": "email",
                "start": 10,
                "end": 25,
                "text": "test@example.com",
                "score": 0.95,
                "source": "rules"
            }
        ]
        
        policy = {"entities": ["email"]}
        
        report = generate_dry_run_report(
            document_path="/path/to/test.txt",
            document_type="text",
            entities=entities,
            policy=policy,
            masked_text="test@example.com",
            processing_time_ms=100.0
        )
        
        self.assertIsInstance(report, ProcessingReport)
        self.assertEqual(report.document_path, "/path/to/test.txt")
        self.assertEqual(report.total_entities, 1)
    
    def test_save_reports_function(self):
        """Test the save_reports convenience function."""
        report = ProcessingReport(
            document_path="/path/to/test.txt",
            document_type="text",
            processing_timestamp="2025-01-27T10:00:00",
            total_entities=1,
            entities_by_type={"email": 1},
            actions_applied={"pseudonymize": 1},
            total_characters=100,
            masked_characters=20,
            entities=[],
            policy_used={"entities": ["email"]},
            processing_time_ms=150.5,
            errors=[]
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = os.path.join(temp_dir, "test_report")
            saved_files = save_reports(report, base_path)
            
            # Check that files were created
            self.assertIn('json', saved_files)
            self.assertIn('csv', saved_files)
            self.assertIn('summary_csv', saved_files)
            
            # Check that files exist
            for file_path in saved_files.values():
                self.assertTrue(os.path.exists(file_path))


if __name__ == '__main__':
    unittest.main()
