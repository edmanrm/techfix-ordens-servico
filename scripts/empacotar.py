# Autor: Edman Rodrigues Miranda
# RA: 2026600198
# E-mail: edmanrm@gmail.com
# Instituição: UNICAMP | Disciplina: Aplicações em Data Science
# Professor: Prof. Dr. Francisco Fambrini
# Atividade: Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática
# Referência: Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

"""Cria ZIP de entrega sem arquivos locais de credenciais nem caches."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.venv', 'venv', '.git', '__pycache__', '.pytest_cache', '.gradio', 'node_modules'}

def incluir(p):
    relative = p.relative_to(ROOT)
    if any(part in SKIP_DIRS for part in relative.parts):
        return False
    if p.name.startswith('.env') and p.name != '.env.example':
        return False
    if p.name in {'secrets.toml', '.DS_Store'} or p.suffix in {'.pyc', '.zip', '.log'}:
        return False
    return True

if __name__ == '__main__':
    destino = ROOT.parent / 'techfix_entrega.zip'
    with ZipFile(destino, 'w', ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file() and incluir(p):
                z.write(p, Path('techfix') / p.relative_to(ROOT))
    print(f'Pacote criado: {destino}')
