# Autor: Edman Rodrigues Miranda
# RA: 2026600198
# E-mail: edmanrm@gmail.com
# Instituição: UNICAMP | Disciplina: Aplicações em Data Science
# Professor: Prof. Dr. Francisco Fambrini
# Atividade: Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática
# Referência: Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

"""Regras compartilhadas pelas duas interfaces, sem acesso à rede."""
import re
from dataclasses import dataclass

STATUS = ('Aberto', 'Em análise', 'Aguardando peça', 'Concluído', 'Entregue')
EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+$")

class AppError(Exception):
    """Erro que pode ser exibido sem expor dados internos ou credenciais."""


def texto(valor, rotulo, minimo, maximo):
    valor = str(valor or '').strip()
    if not minimo <= len(valor) <= maximo:
        raise AppError(f'{rotulo}: informe entre {minimo} e {maximo} caracteres.')
    return valor


def contato(endereco, email, celular):
    endereco = texto(endereco, 'Endereço', 5, 300)
    email = str(email or '').strip().lower()
    if len(email) > 254 or not EMAIL_RE.fullmatch(email):
        raise AppError('Informe um e-mail válido, como cliente@example.com.')
    celular = str(celular or '').strip()
    if not re.fullmatch(r'[0-9]{10,13}', celular):
        raise AppError('Celular/WhatsApp: use somente números, de 10 a 13 dígitos, com DDD.')
    return {'endereco': endereco, 'email': email, 'celular_whatsapp': celular}


@dataclass(frozen=True)
class OrdemEntrada:
    nome: str
    endereco: str
    email: str
    celular: str
    modelo: str
    problema: str

    def rpc_params(self):
        c = contato(self.endereco, self.email, self.celular)
        return {'p_nome': texto(self.nome, 'Nome do cliente', 2, 120),
                'p_endereco': c['endereco'], 'p_email': c['email'],
                'p_celular': c['celular_whatsapp'],
                'p_modelo': texto(self.modelo, 'Modelo do computador', 2, 160),
                'p_problema': texto(self.problema, 'Problema apresentado', 5, 4000)}


def filtrar_ordens(ordens, nome='', email='', status=()):
    nome, email = nome.strip().casefold(), email.strip().casefold()
    return [o for o in ordens
            if nome in (o.get('clientes') or {}).get('nome', '').casefold()
            and email in (o.get('clientes') or {}).get('email', '').casefold()
            and (not status or o['status'] in status)]


def linhas_tabela(ordens):
    return [{'OS': o['id'], 'Cliente': (o.get('clientes') or {}).get('nome', ''),
             'E-mail': (o.get('clientes') or {}).get('email', ''),
             'WhatsApp': (o.get('clientes') or {}).get('celular_whatsapp', ''),
             'Equipamento': o['modelo_computador'], 'Problema': o['problema_relatado'],
             'Status': o['status'], 'Abertura': o['data_abertura'],
             'Atualização': o['data_atualizacao']} for o in ordens]
