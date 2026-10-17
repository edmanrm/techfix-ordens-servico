# Autor: Edman Rodrigues Miranda
# RA: 2026600198
# E-mail: edmanrm@gmail.com
# Instituição: UNICAMP | Disciplina: Aplicações em Data Science
# Professor: Prof. Dr. Francisco Fambrini
# Atividade: Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática
# Referência: Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

"""Painel TechFix: streamlit run app_streamlit.py."""
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from backend import Repositorio, ROOT
from domain import AppError, STATUS, OrdemEntrada, filtrar_ordens, linhas_tabela

st.set_page_config(page_title='TechFix | Gestão de serviços', page_icon='🔧', layout='wide')
COLUNAS = ['OS', 'Cliente', 'E-mail', 'WhatsApp', 'Equipamento', 'Problema', 'Status', 'Abertura', 'Atualização']


def dataframe(ordens):
    df = pd.DataFrame(linhas_tabela(ordens), columns=COLUNAS)
    for col in ['Abertura', 'Atualização']:
        if not df.empty:
            df[col] = pd.to_datetime(df[col], utc=True).dt.tz_convert('America/Sao_Paulo').dt.strftime('%d/%m/%Y %H:%M:%S')
    return df


def csv_seguro(df):
    # Evita que células textuais sejam interpretadas como fórmulas no Excel.
    def safe(v):
        return "'" + v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else v
    return df.map(safe).to_csv(index=False, sep=';').encode('utf-8-sig')


def formulario_cadastro(repo):
    st.subheader('Nova ordem de serviço')
    st.caption('E-mail existente reaproveita o cliente sem alterar o cadastro. Todos os campos são obrigatórios.')
    with st.form('nova_os', clear_on_submit=False):
        a, b = st.columns(2)
        nome = a.text_input('Nome do cliente', max_chars=120, placeholder='Ana Exemplo')
        email = b.text_input('E-mail do cliente', max_chars=254, placeholder='ana@example.com')
        endereco = st.text_input('Endereço', max_chars=300, placeholder='Rua de Demonstração, 100')
        celular = st.text_input('Celular/WhatsApp', max_chars=13, placeholder='11900000001')
        modelo = st.text_input('Modelo do computador', max_chars=160, placeholder='Notebook Demo A')
        problema = st.text_area('Problema apresentado', max_chars=4000, placeholder='Descreva o defeito e quando ele ocorre.')
        if st.form_submit_button('Cadastrar OS', type='primary'):
            try:
                result = repo.cadastrar(OrdemEntrada(nome, endereco, email, celular, modelo, problema))
                st.session_state['flash'] = f"OS #{result['os_id']} cadastrada com sucesso."
                st.rerun()
            except AppError as exc:
                st.error(str(exc))


def edicao_exclusao(repo, ordens, clientes):
    st.subheader('Ordens de serviço')
    por_id = {o['id']: o for o in ordens}
    if por_id:
        os_id = st.selectbox('Ordem para editar ou excluir', list(por_id),
                             format_func=lambda i: f"OS #{i} · {por_id[i]['modelo_computador']}")
        ordem = por_id[os_id]
        with st.form(f'status_{os_id}'):
            novo_status = st.selectbox('Status da OS', STATUS, index=STATUS.index(ordem['status']))
            if st.form_submit_button('Salvar status'):
                try:
                    repo.atualizar_status(os_id, novo_status)
                    st.session_state['flash'] = f'Status da OS #{os_id} atualizado.'
                    st.rerun()
                except AppError as exc:
                    st.error(str(exc))
        with st.expander('Excluir ordem de serviço'):
            with st.form(f'excluir_os_{os_id}'):
                confirmar = st.checkbox(f'Confirmo a exclusão definitiva da OS #{os_id}')
                if st.form_submit_button('Excluir OS'):
                    if not confirmar:
                        st.warning('Marque a confirmação antes de excluir.')
                    else:
                        try:
                            repo.excluir('ordens_servico', os_id)
                            st.session_state['flash'] = f'OS #{os_id} excluída.'
                            st.rerun()
                        except AppError as exc:
                            st.error(str(exc))
    else:
        st.info('Nenhuma ordem cadastrada.')
    st.divider()
    st.subheader('Clientes')
    clientes_id = {c['id']: c for c in clientes}
    if not clientes_id:
        st.info('Nenhum cliente cadastrado.')
        return
    cid = st.selectbox('Cliente para editar ou excluir', list(clientes_id),
                      format_func=lambda i: f"#{i} · {clientes_id[i]['nome']} · {clientes_id[i]['email']}")
    cliente = clientes_id[cid]
    st.caption('Alterações neste cliente serão refletidas em todas as suas ordens de serviço.')
    with st.form(f'cliente_{cid}'):
        endereco = st.text_input('Endereço atualizado', value=cliente['endereco'], max_chars=300)
        email = st.text_input('E-mail atualizado', value=cliente['email'], max_chars=254)
        celular = st.text_input('Celular atualizado', value=cliente['celular_whatsapp'], max_chars=13)
        if st.form_submit_button('Salvar cliente'):
            try:
                repo.atualizar_cliente(cid, endereco, email, celular)
                st.session_state['flash'] = f'Cliente #{cid} atualizado.'
                st.rerun()
            except AppError as exc:
                st.error(str(exc))
    with st.expander('Excluir cliente'):
        st.write('O banco bloqueia a exclusão enquanto houver ordens vinculadas ao cliente.')
        with st.form(f'excluir_cliente_{cid}'):
            confirmar = st.checkbox(f'Confirmo a exclusão definitiva do cliente #{cid}')
            if st.form_submit_button('Excluir cliente'):
                if not confirmar:
                    st.warning('Marque a confirmação antes de excluir.')
                else:
                    try:
                        repo.excluir('clientes', cid)
                        st.session_state['flash'] = f'Cliente #{cid} excluído.'
                        st.rerun()
                    except AppError as exc:
                        st.error(str(exc))


def main():
    logo = ROOT / 'assets' / 'techfix-logo.png'
    if logo.exists():
        st.image(str(logo), width=290)
    st.title('Gestão de serviços')
    st.caption('TechFix Informática · Projeto acadêmico com dados fictícios')
    if 'repo' not in st.session_state:
        st.subheader('Acesso da equipe')
        with st.form('login'):
            email = st.text_input('E-mail da equipe', placeholder='Usuário autorizado no Supabase')
            senha = st.text_input('Senha', type='password')
            if st.form_submit_button('Entrar', type='primary'):
                try:
                    try:
                        secrets = dict(st.secrets)
                    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
                        secrets = {}
                    st.session_state['repo'] = Repositorio.entrar(email, senha, secrets)
                    st.rerun()
                except AppError as exc:
                    st.error(str(exc))
        st.info('Configure o projeto conforme o README e autorize o usuário em sql/autorizar_equipe.sql.')
        return
    repo = st.session_state['repo']
    with st.sidebar:
        st.header('Consulta')
        nome = st.text_input('Buscar por nome')
        email = st.text_input('Buscar por e-mail')
        status = st.multiselect('Filtrar por status', STATUS)
        st.button('Atualizar dados')
        if st.button('Sair'):
            try:
                repo.sair()
            except AppError as exc:
                st.session_state['flash'] = str(exc)
            finally:
                st.session_state.pop('repo', None)
            st.rerun()
    if 'flash' in st.session_state:
        st.success(st.session_state.pop('flash'))
    try:
        ordens, clientes = repo.ordens(), repo.clientes()
    except AppError as exc:
        st.error(str(exc))
        return
    filtradas = filtrar_ordens(ordens, nome, email, status)
    consultar, cadastrar, editar, indicadores = st.tabs(['Consultar', 'Cadastrar', 'Editar/Excluir', 'Indicadores'])
    with consultar:
        st.subheader('Ordens de serviço')
        st.caption(f'{len(filtradas)} de {len(ordens)} ordens · Horários em America/Sao_Paulo')
        df = dataframe(filtradas)
        st.dataframe(df, hide_index=True, width='stretch')
        st.download_button('Exportar consulta em CSV', csv_seguro(df), 'techfix_ordens.csv', 'text/csv')
        if not filtradas:
            st.info('Nenhuma ordem corresponde aos filtros selecionados.')
    with cadastrar:
        formulario_cadastro(repo)
    with editar:
        st.caption('Esta aba mostra todos os registros, independentemente dos filtros da consulta.')
        edicao_exclusao(repo, ordens, clientes)
    with indicadores:
        st.subheader('Ordens por status')
        st.caption('Indicadores respeitam os filtros da barra lateral.')
        counts = {s: sum(o['status'] == s for o in filtradas) for s in STATUS}
        cols = st.columns(len(STATUS))
        for col, (s, total) in zip(cols, counts.items()):
            col.metric(s, total)
        st.bar_chart(pd.DataFrame({'Status': list(counts), 'Quantidade': list(counts.values())}).set_index('Status'), color='#007F86')
        st.metric('Total no filtro', len(filtradas))
        st.caption('Consulta realizada em ' + datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S'))


if __name__ == '__main__':
    main()
