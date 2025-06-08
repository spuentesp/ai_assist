# utils.py
import os
from jinja2 import Template

def load_template(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()

def render_template(template_str: str, variables: dict) -> str:
    template = Template(template_str)
    return template.render(**variables)
