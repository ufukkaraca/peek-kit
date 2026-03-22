from typing import List, Optional, Literal, Dict
from mcp.server.fastmcp import FastMCP
from peek_kit.models.actions import ReportResult, PRDResult, ArtifactResult
from peek_kit.models.reports import AuditReport, FeatureMap
from peek_kit.models.prd import PRDDocument
from peek_kit.report.renderer import render_audit_report
from peek_kit.report.prd_renderer import render_reverse_prd
import os
import json
import time

def register_output_tools(mcp: FastMCP):
    @mcp.tool()
    def write_audit_report(app_name: str, report: AuditReport, output_dir: str = './peek-kit-reports', formats: List[str] = ['markdown', 'json']) -> ReportResult:
        """Save full human-readable audit report (markdown + JSON)"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = time.strftime("%Y%m%dT%H%M%S")
        base_filename = os.path.join(output_dir, f"{app_name.lower().replace(' ', '-')}-audit-{timestamp}")
        
        filepaths: Dict[str, str] = {}
        
        if 'json' in formats:
            jp = f"{base_filename}.json"
            with open(jp, 'w', encoding='utf-8') as f:
                f.write(report.model_dump_json(indent=2))
            filepaths['json'] = jp
            
        if 'markdown' in formats:
            mp = f"{base_filename}.md"
            md_content = render_audit_report(app_name, report)
            with open(mp, 'w', encoding='utf-8') as f:
                f.write(md_content)
            filepaths['markdown'] = mp
            
        word_count = len(md_content.split()) if 'markdown' in formats else 0
        return ReportResult(success=True, filepaths=filepaths, word_count=word_count, section_count=13)

    @mcp.tool()
    def write_reverse_prd(app_name: str, prd: PRDDocument, target_audience: Optional[str] = None, output_dir: str = './peek-kit-reports') -> PRDResult:
        """Save a buildable reverse-engineered PRD from Claude's generated spec"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = time.strftime("%Y%m%dT%H%M%S")
        base_filename = os.path.join(output_dir, f"{app_name.lower().replace(' ', '-')}-prd-{timestamp}")
        
        filepath_md = f"{base_filename}.md"
        filepath_json = f"{base_filename}.json"
        
        with open(filepath_json, 'w', encoding='utf-8') as f:
            f.write(prd.model_dump_json(indent=2))
            
        # Render markdown from PRD
        md_content = render_reverse_prd(app_name, prd)
        with open(filepath_md, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        epic_count = len(prd.epics)
        story_count = sum(len(e.stories) for e in prd.epics)
        
        return PRDResult(success=True, filepath_md=filepath_md, filepath_json=filepath_json, feature_count=story_count, epic_count=epic_count)

    @mcp.tool()
    def save_screenshot_artifact(app_name: str, label: str, finding: str, category: str, output_dir: str = './peek-kit-reports') -> ArtifactResult:
        """Save annotated screenshot tagged with finding category"""
        # We need a screenshot here. This function assumes Claude will first take a screenshot, 
        # or we capture the current screen to save as an artifact.
        from peek_kit.bridge.screenshot import take_screenshot
        from peek_kit.bridge.accessibility import extract_tree
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = time.strftime("%Y%m%dT%H%M%S")
        clean_label = label.lower().replace(' ', '-')
        filename = f"{app_name.lower()}-{clean_label}-{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        tree = extract_tree(app_name)
        shot = take_screenshot(app_name, annotated=True, tree=tree)
        if shot and shot.base64_png:
            import base64
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(shot.base64_png))
            return ArtifactResult(success=True, filepath=filepath, label=label)
            
        return ArtifactResult(success=False, filepath="", label=label)
