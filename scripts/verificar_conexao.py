# Autor: Edman Rodrigues Miranda
# RA: 2026600198
# E-mail: edmanrm@gmail.com
# Instituição: UNICAMP | Disciplina: Aplicações em Data Science
# Professor: Prof. Dr. Francisco Fambrini
# Atividade: Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática
# Referência: Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

"""Diagnóstico real, somente leitura; não imprime chaves ou tokens."""
import sys
from pathlib import Path
from getpass import getpass
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend import Repositorio
from domain import AppError

if __name__ == '__main__':
    repo = None
    try:
        repo = Repositorio.entrar(input('E-mail da equipe: '), getpass('Senha: '))
        print(f'Conexão e acesso confirmados: {len(repo.clientes())} clientes e {len(repo.ordens())} ordens visíveis.')
    except AppError as exc:
        print(f'Diagnóstico não concluído: {exc}')
        sys.exit(1)
    finally:
        if repo:
            try:
                repo.sair()
            except AppError as exc:
                print(exc)
