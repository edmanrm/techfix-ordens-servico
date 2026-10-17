# Autor: Edman Rodrigues Miranda
# RA: 2026600198
# E-mail: edmanrm@gmail.com
# Instituição: UNICAMP | Disciplina: Aplicações em Data Science
# Professor: Prof. Dr. Francisco Fambrini
# Atividade: Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática
# Referência: Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

from pathlib import Path
from unittest.mock import Mock
from types import SimpleNamespace
from streamlit.testing.v1 import AppTest
from app_gradio import criar_app, cadastrar

ROOT = Path(__file__).resolve().parents[1]


def dados():
    c = dict(id=1, nome='Ana Exemplo', endereco='Rua de Teste, 100', email='ana@example.com', celular_whatsapp='11900000001')
    o = dict(id=1, cliente_id=1, clientes=c, modelo_computador='Notebook Demo', problema_relatado='Não liga.', status='Aberto', data_abertura='2026-10-16T12:00:00Z', data_atualizacao='2026-10-16T12:00:00Z')
    return c, o


def painel():
    c, o = dados()
    repo = Mock()
    repo.ordens.return_value = [o]
    repo.clientes.return_value = [c]
    repo.cadastrar.return_value = dict(os_id=2, cliente_reutilizado=True)
    at = AppTest.from_file(str(ROOT / 'app_streamlit.py'), default_timeout=20)
    at.session_state['repo'] = repo
    return at.run(), repo


def test_gradio_blocks_e_sem_cadastro_anonimo():
    app = criar_app()
    assert app.config['mode'] == 'blocks'
    message, _ = cadastrar(None, 'Ana', 'Rua Teste', 'ana@example.com', '11900000001', 'Notebook', 'Não liga.')
    assert 'Entre' in message


def test_streamlit_login_sem_configuracao():
    at = AppTest.from_file(str(ROOT / 'app_streamlit.py')).run()
    assert not at.exception
    at.button[0].click().run()
    assert not at.exception
    assert at.error


def test_streamlit_todas_abas():
    at, _ = painel()
    assert not at.exception
    assert len(at.tabs) == 4
    assert at.dataframe[0].value.iloc[0]['OS'] == 1
    assert [m.value for m in at.metric] == ['1', '0', '0', '0', '0', '1']


def test_streamlit_busca_vazia():
    at, _ = painel()
    at.sidebar.text_input[0].set_value('inexistente').run()
    assert not at.exception
    assert at.dataframe[0].value.empty
    assert at.metric[-1].value == '0'


def test_exclusao_exige_confirmacao():
    at, repo = painel()
    next(b for b in at.button if b.label == 'Excluir OS').click().run()
    assert not at.exception
    repo.excluir.assert_not_called()
    assert any('confirmação' in w.value for w in at.warning)
    at.checkbox[0].check()
    next(b for b in at.button if b.label == 'Excluir OS').click().run()
    repo.excluir.assert_called_once_with('ordens_servico', 1)


def test_editar_status():
    at, repo = painel()
    next(s for s in at.selectbox if s.label == 'Status da OS').set_value('Concluído')
    next(b for b in at.button if b.label == 'Salvar status').click().run()
    repo.atualizar_status.assert_called_once_with(1, 'Concluído')


def test_csv_protege_formula():
    # O módulo não executa main quando importado.
    from app_streamlit import csv_seguro
    import pandas as pd
    value = csv_seguro(pd.DataFrame([{'Cliente': '=1+1'}])).decode('utf-8-sig')
    assert "'=1+1" in value
