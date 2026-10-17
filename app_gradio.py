# Autor: Edman Rodrigues Miranda
# RA: 2026600198
# E-mail: edmanrm@gmail.com
# Instituição: UNICAMP | Disciplina: Aplicações em Data Science
# Professor: Prof. Dr. Francisco Fambrini
# Atividade: Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática
# Referência: Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

"""Atendimento TechFix: python app_gradio.py (link temporário habilitado por padrão)."""
import argparse
from pathlib import Path
import gradio as gr
from backend import Repositorio, novo_cliente, ROOT
from domain import AppError, OrdemEntrada


def entrar(email, senha):
    try:
        repo = Repositorio.entrar(email, senha)
        session = repo.client.auth.get_session()
        tokens = {'access_token': session.access_token, 'refresh_token': session.refresh_token}
        return tokens, gr.update(visible=False), gr.update(visible=True), 'Acesso autorizado.', ''
    except AppError as exc:
        return None, gr.update(visible=True), gr.update(visible=False), str(exc), ''


def cadastrar(tokens, nome, endereco, email, celular, modelo, problema):
    try:
        entrada = OrdemEntrada(nome, endereco, email, celular, modelo, problema)
        entrada.rpc_params()  # Validar antes de qualquer chamada de rede.
        if not tokens:
            raise AppError('Entre com seu usuário da equipe para cadastrar uma OS.')
        client = novo_cliente()
        session = client.auth.set_session(tokens['access_token'], tokens['refresh_token']).session
        updated = {'access_token': session.access_token, 'refresh_token': session.refresh_token}
        result = Repositorio(client).cadastrar(entrada)
        detalhe = ' Cliente existente reaproveitado, sem alterar seus dados.' if result['cliente_reutilizado'] else ''
        return f"OS #{result['os_id']} cadastrada com sucesso. Status: Aberto.{detalhe}", updated
    except AppError as exc:
        return str(exc), tokens
    except Exception:
        return 'Falha de conexão ou sessão expirada. Entre novamente; consulte o painel antes de repetir o cadastro.', tokens


def sair(tokens):
    message = 'Sessão encerrada.'
    try:
        if tokens:
            client = novo_cliente()
            client.auth.set_session(tokens['access_token'], tokens['refresh_token'])
            Repositorio(client).sair()
    except Exception:
        message = 'Sessão local encerrada. Não foi possível confirmar a saída no servidor.'
    return None, gr.update(visible=True), gr.update(visible=False), message, *([''] * 7)


def criar_app():
    with gr.Blocks(title='TechFix | Atendimento') as app:
        tokens = gr.State(None, time_to_live=3600)
        logo = ROOT / 'assets' / 'techfix-logo.png'
        if logo.exists():
            gr.Image(str(logo), image_mode='RGBA', show_label=False, interactive=False, height=115,
                     buttons=[], container=False)
        gr.Markdown('# Atendimento\nCadastre o cliente e o equipamento para abrir uma ordem de serviço.\n\n**Projeto acadêmico: utilize somente dados fictícios.**')
        with gr.Column() as login:
            gr.Markdown('### Acesso da equipe')
            login_email = gr.Textbox(label='E-mail da equipe', placeholder='Seu usuário autorizado no Supabase')
            senha = gr.Textbox(label='Senha', type='password', placeholder='Senha do seu usuário')
            entrar_btn = gr.Button('Entrar', variant='primary')
        aviso_login = gr.Textbox(label='Acesso', interactive=False)
        with gr.Column(visible=False) as form:
            gr.Markdown('### 1. Dados do cliente\nSe o e-mail já estiver cadastrado, o cliente será reaproveitado. Edite dados existentes pelo painel administrativo.')
            with gr.Row():
                nome = gr.Textbox(label='Nome do cliente', placeholder='Ana Exemplo', max_length=120)
                email = gr.Textbox(label='E-mail', placeholder='ana@example.com', max_length=254)
            endereco = gr.Textbox(label='Endereço', placeholder='Rua de Demonstração, 100', max_length=300)
            celular = gr.Textbox(label='Celular/WhatsApp', placeholder='11900000001 — somente números, com DDD', max_length=13)
            gr.Markdown('### 2. Equipamento e problema')
            modelo = gr.Textbox(label='Modelo do computador', placeholder='Notebook Demo A', max_length=160)
            problema = gr.Textbox(label='Problema apresentado', placeholder='Descreva o defeito e quando ele ocorre.', lines=4, max_length=4000)
            with gr.Row():
                cadastrar_btn = gr.Button('Cadastrar', variant='primary')
                limpar_btn = gr.Button('Limpar')
                sair_btn = gr.Button('Sair')
            resultado = gr.Textbox(label='Resultado do atendimento', interactive=False)
        campos = [nome, endereco, email, celular, modelo, problema]
        entrar_btn.click(entrar, [login_email, senha], [tokens, login, form, aviso_login, senha], api_name=False)
        cadastrar_btn.click(cadastrar, [tokens] + campos, [resultado, tokens], api_name=False, concurrency_limit=1)
        limpar_btn.click(lambda: tuple([''] * 7), outputs=campos + [resultado], api_name=False)
        sair_btn.click(sair, [tokens], [tokens, login, form, aviso_login] + campos + [resultado], api_name=False)
    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Atendimento TechFix')
    parser.add_argument('--local', action='store_true', help='Desativar o link público temporário')
    parser.add_argument('--port', type=int, default=7860)
    args = parser.parse_args()
    criar_app().launch(share=not args.local, server_name='127.0.0.1', server_port=args.port,
                       allowed_paths=[str(ROOT / 'assets')],
                       blocked_paths=[str(ROOT / '.env'), str(ROOT / '.streamlit' / 'secrets.toml')],
                       theme=gr.themes.Soft(primary_hue='teal', neutral_hue='slate'))
