#!/usr/bin/env python3
"""
Doc Masking Reports Module

Provides dry-run reporting functionality for entity detection and masking operations.
Supports JSON and CSV output formats with detailed entity, page, span, action, and token information.
"""

import json
import csv
import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class EntityReport:
    """Report data for a single detected entity."""
    entity_id: str
    entity_type: str
    start: int
    end: int
    text: str
    masked_text: Optional[str] = None
    action: str = "mask"
    confidence: float = 0.0
    source: str = "unknown"
    page_number: Optional[int] = None
    span_id: Optional[str] = None


@dataclass
class ProcessingReport:
    """Complete processing report with metadata and entity details."""
    document_path: str
    document_type: str  # "text" or "pdf"
    processing_timestamp: str
    total_entities: int
    entities_by_type: Dict[str, int]
    actions_applied: Dict[str, int]
    total_characters: int
    masked_characters: int
    entities: List[EntityReport]
    policy_used: Dict[str, Any]
    processing_time_ms: Optional[float] = None
    errors: List[str] = None


class ReportGenerator:
    """Generates dry-run reports for document masking operations."""
    
    def __init__(self):
        self.entity_counter = 0
    
    def generate_entity_id(self, entity_type: str) -> str:
        """Generate a unique ID for an entity."""
        self.entity_counter += 1
        return f"{entity_type}_{self.entity_counter:04d}"
    
    def create_entity_report(
        self,
        entity: Dict[str, Any],
        masked_text: Optional[str] = None,
        action: str = "mask",
        page_number: Optional[int] = None,
        span_id: Optional[str] = None
    ) -> EntityReport:
        """Create an EntityReport from a detected entity."""
        entity_id = self.generate_entity_id(entity.get("type", "unknown"))
        
        return EntityReport(
            entity_id=entity_id,
            entity_type=entity.get("type", "unknown"),
            start=int(entity.get("start", 0)),
            end=int(entity.get("end", 0)),
            text=entity.get("text", ""),
            masked_text=masked_text,
            action=action,
            confidence=float(entity.get("score", 0.0)),
            source=entity.get("source", "unknown"),
            page_number=page_number,
            span_id=span_id
        )
    
    def generate_dry_run_report(
        self,
        document_path: str,
        document_type: str,
        entities: List[Dict[str, Any]],
        policy: Dict[str, Any],
        masked_text: Optional[str] = None,
        processing_time_ms: Optional[float] = None,
        errors: Optional[List[str]] = None,
        page_entities: Optional[Dict[int, List[Dict[str, Any]]]] = None
    ) -> ProcessingReport:
        """Generate a comprehensive dry-run report."""
        
        # Count entities by type
        entities_by_type = {}
        actions_applied = {}
        
        entity_reports = []
        
        for entity in entities:
            entity_type = entity.get("type", "unknown")
            entities_by_type[entity_type] = entities_by_type.get(entity_type, 0) + 1
            
            # Determine action based on policy
            action = self._determine_action(entity_type, policy)
            actions_applied[action] = actions_applied.get(action, 0) + 1
            
            # Generate masked text if not provided
            masked_text_for_entity = None
            if masked_text:
                start = int(entity.get("start", 0))
                end = int(entity.get("end", 0))
                masked_text_for_entity = masked_text[start:end]
            
            # Check if this entity is from a specific page
            page_number = None
            if page_entities:
                for page_num, page_entity_list in page_entities.items():
                    if entity in page_entity_list:
                        page_number = page_num
                        break
            
            entity_report = self.create_entity_report(
                entity=entity,
                masked_text=masked_text_for_entity,
                action=action,
                page_number=page_number
            )
            entity_reports.append(entity_report)
        
        # Calculate statistics
        total_characters = len(masked_text) if masked_text else 0
        masked_characters = sum(
            len(er.masked_text) if er.masked_text else 0 
            for er in entity_reports
        )
        
        return ProcessingReport(
            document_path=document_path,
            document_type=document_type,
            processing_timestamp=datetime.now().isoformat(),
            total_entities=len(entities),
            entities_by_type=entities_by_type,
            actions_applied=actions_applied,
            total_characters=total_characters,
            masked_characters=masked_characters,
            entities=entity_reports,
            policy_used=policy,
            processing_time_ms=processing_time_ms,
            errors=errors or []
        )
    
    def _determine_action(self, entity_type: str, policy: Dict[str, Any]) -> str:
        """Determine the action that will be applied to an entity based on policy."""
        actions = policy.get("actions", {})
        entity_action = actions.get(entity_type, {})
        return entity_action.get("action", "mask")
    
    def save_json_report(self, report: ProcessingReport, output_path: str) -> None:
        """Save report as JSON file."""
        report_dict = asdict(report)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
    
    def save_csv_report(self, report: ProcessingReport, output_path: str) -> None:
        """Save report as CSV file with entity details."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Entity ID', 'Entity Type', 'Start', 'End', 'Text', 'Masked Text',
                'Action', 'Confidence', 'Source', 'Page Number', 'Span ID'
            ])
            
            # Write entity data
            for entity in report.entities:
                writer.writerow([
                    entity.entity_id,
                    entity.entity_type,
                    entity.start,
                    entity.end,
                    entity.text,
                    entity.masked_text or '',
                    entity.action,
                    entity.confidence,
                    entity.source,
                    entity.page_number or '',
                    entity.span_id or ''
                ])
    
    def save_summary_csv(self, report: ProcessingReport, output_path: str) -> None:
        """Save a summary CSV with document-level statistics."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write summary header
            writer.writerow([
                'Document Path', 'Document Type', 'Processing Timestamp',
                'Total Entities', 'Total Characters', 'Masked Characters',
                'Processing Time (ms)', 'Errors'
            ])
            
            # Write summary data
            writer.writerow([
                report.document_path,
                report.document_type,
                report.processing_timestamp,
                report.total_entities,
                report.total_characters,
                report.masked_characters,
                report.processing_time_ms or '',
                '; '.join(report.errors) if report.errors else ''
            ])
            
            # Write entity type breakdown
            writer.writerow([])  # Empty row
            writer.writerow(['Entity Type', 'Count'])
            for entity_type, count in report.entities_by_type.items():
                writer.writerow([entity_type, count])
            
            # Write action breakdown
            writer.writerow([])  # Empty row
            writer.writerow(['Action', 'Count'])
            for action, count in report.actions_applied.items():
                writer.writerow([action, count])


def generate_dry_run_report(
    document_path: str,
    document_type: str,
    entities: List[Dict[str, Any]],
    policy: Dict[str, Any],
    masked_text: Optional[str] = None,
    processing_time_ms: Optional[float] = None,
    errors: Optional[List[str]] = None,
    page_entities: Optional[Dict[int, List[Dict[str, Any]]]] = None
) -> ProcessingReport:
    """Convenience function to generate a dry-run report."""
    generator = ReportGenerator()
    return generator.generate_dry_run_report(
        document_path=document_path,
        document_type=document_type,
        entities=entities,
        policy=policy,
        masked_text=masked_text,
        processing_time_ms=processing_time_ms,
        errors=errors,
        page_entities=page_entities
    )


def save_reports(
    report: ProcessingReport,
    base_output_path: str,
    include_json: bool = True,
    include_csv: bool = True,
    include_summary_csv: bool = True
) -> Dict[str, str]:
    """Save reports in multiple formats and return file paths."""
    generator = ReportGenerator()
    saved_files = {}
    
    if include_json:
        json_path = f"{base_output_path}.json"
        generator.save_json_report(report, json_path)
        saved_files['json'] = json_path
    
    if include_csv:
        csv_path = f"{base_output_path}_entities.csv"
        generator.save_csv_report(report, csv_path)
        saved_files['csv'] = csv_path
    
    if include_summary_csv:
        summary_path = f"{base_output_path}_summary.csv"
        generator.save_summary_csv(report, summary_path)
        saved_files['summary_csv'] = summary_path
    
    return saved_files
