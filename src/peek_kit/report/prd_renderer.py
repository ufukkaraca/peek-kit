import os
from jinja2 import Environment, FileSystemLoader
from peek_kit.models.prd import PRDDocument

def render_reverse_prd(app_name: str, prd: PRDDocument) -> str:
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('reverse_prd.md.j2')
    return template.render(app_name=app_name, prd=prd)
