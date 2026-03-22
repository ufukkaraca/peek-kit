import os
from jinja2 import Environment, FileSystemLoader
from peek_kit.models.reports import AuditReport

def render_audit_report(app_name: str, report: AuditReport) -> str:
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('audit_report.md.j2')
    return template.render(app_name=app_name, report=report)
