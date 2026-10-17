# Autor: Edman Rodrigues Miranda
# RA: 2026600198
# E-mail: edmanrm@gmail.com
# Instituição: UNICAMP | Disciplina: Aplicações em Data Science
# Professor: Prof. Dr. Francisco Fambrini
# Atividade: Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática
# Referência: Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

"""Supabase: conexão por sessão, RLS e operações com mensagens controladas."""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from supabase.lib.client_options import SyncClientOptions
from domain import AppError, STATUS, contato

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')


def configuracao(overrides=None):
    overrides = overrides or {}
    url = os.getenv('SUPABASE_URL') or overrides.get('SUPABASE_URL', '')
    key = os.getenv('SUPABASE_KEY') or overrides.get('SUPABASE_KEY', '')
    if not url or not key:
        raise AppError('Configure SUPABASE_URL e SUPABASE_KEY no .env ou nos secrets do Streamlit.')
    if not url.startswith('https://'):
        raise AppError('SUPABASE_URL deve usar HTTPS e corresponder ao projeto Supabase.')
    return url, key


def novo_cliente(overrides=None):
    url, key = configuracao(overrides)
    return create_client(url, key, options=SyncClientOptions(persist_session=False))


def erro_banco(exc):
    code = str(getattr(exc, 'code', ''))
    if code == '23505':
        return AppError('Este e-mail já pertence a outro cliente. Confira o cadastro.')
    if code in ('23503', '23001'):
        return AppError('O cliente possui ordens vinculadas. Exclua as ordens antes de excluir o cliente.')
    if code == '23514':
        return AppError('Os dados não atendem às regras do banco. Revise os campos.')
    if code in ('42501', 'PGRST301', 'PGRST302', 'PGRST303'):
        return AppError('Acesso não autorizado ou sessão expirada. Entre novamente e confira a lista da equipe.')
    return AppError('Não foi possível concluir a operação. Confira a conexão e a configuração do banco antes de tentar novamente.')


class Repositorio:
    def __init__(self, client):
        self.client = client

    @classmethod
    def entrar(cls, email, senha, overrides=None):
        if not email or not senha:
            raise AppError('Informe o e-mail e a senha da equipe.')
        try:
            client = novo_cliente(overrides)
            result = client.auth.sign_in_with_password({'email': email.strip(), 'password': senha})
            if not result.user:
                raise AppError('Não foi possível iniciar a sessão.')
            equipe = client.table('equipe').select('usuario_id').eq('usuario_id', str(result.user.id)).execute().data
            if not equipe:
                client.auth.sign_out()
                raise AppError('Usuário sem autorização. Peça a inclusão na equipe do projeto.')
            return cls(client)
        except AppError:
            raise
        except Exception:
            raise AppError('Falha no acesso. Confira e-mail, senha, conexão e confirmação do usuário no Supabase.') from None

    def sair(self):
        try:
            self.client.auth.sign_out()
        except Exception:
            raise AppError('A sessão local foi encerrada, mas não foi possível confirmar a saída no servidor.') from None

    def _executar(self, query):
        try:
            return query.execute().data or []
        except Exception as exc:
            raise erro_banco(exc) from None

    def cadastrar(self, entrada):
        params = entrada.rpc_params()
        data = self._executar(self.client.rpc('cadastrar_ordem', params))
        if not data:
            raise AppError('O banco não confirmou o cadastro. Consulte o painel antes de repetir a operação.')
        return data[0]

    def _todos(self, table, select, order):
        # Paginação explícita: não truncar a listagem no limite padrão do Supabase.
        rows, offset, size = [], 0, 500
        while True:
            page = self._executar(self.client.table(table).select(select).order(order).range(offset, offset + size - 1))
            rows.extend(page)
            if len(page) < size:
                return rows
            offset += size

    def ordens(self):
        return self._todos('ordens_servico', '*,clientes(id,nome,endereco,email,celular_whatsapp)', 'id')

    def clientes(self):
        return self._todos('clientes', '*', 'id')

    def atualizar_status(self, os_id, status):
        if status not in STATUS:
            raise AppError('Selecione um status válido.')
        self._alterar('ordens_servico', os_id, {'status': status})

    def atualizar_cliente(self, cliente_id, endereco, email, celular):
        self._alterar('clientes', cliente_id, contato(endereco, email, celular))

    def _alterar(self, table, record_id, values):
        rows = self._executar(self.client.table(table).update(values).eq('id', int(record_id)))
        if not rows:
            raise AppError('Registro não encontrado ou sem permissão. Atualize a consulta.')

    def excluir(self, table, record_id):
        if table not in ('clientes', 'ordens_servico'):
            raise AppError('Tipo de registro inválido.')
        rows = self._executar(self.client.table(table).delete().eq('id', int(record_id)))
        if not rows:
            raise AppError('Registro não encontrado ou sem permissão. Atualize a consulta.')
