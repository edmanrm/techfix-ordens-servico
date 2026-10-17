# Autor: Edman Rodrigues Miranda
# RA: 2026600198
# E-mail: edmanrm@gmail.com
# Instituição: UNICAMP | Disciplina: Aplicações em Data Science
# Professor: Prof. Dr. Francisco Fambrini
# Atividade: Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática
# Referência: Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from backend import Repositorio, erro_banco
from domain import AppError
from test_domain import entrada


def test_cadastro_usa_rpc_atomica():
    client = Mock()
    client.rpc.return_value.execute.return_value.data = [{'os_id': 12, 'cliente_reutilizado': True}]
    result = Repositorio(client).cadastrar(entrada())
    assert result['os_id'] == 12
    assert client.rpc.call_args.args[0] == 'cadastrar_ordem'
    assert client.rpc.call_args.args[1]['p_email'] == 'ana@example.com'
    client.table.assert_not_called()


def test_validacao_sem_rede():
    client = Mock()
    with pytest.raises(AppError):
        Repositorio(client).cadastrar(entrada(email='invalido'))
    client.rpc.assert_not_called()


def test_paginacao_nao_trunca():
    client = Mock()
    query = client.table.return_value.select.return_value.order.return_value
    query.range.return_value.execute.side_effect = [SimpleNamespace(data=[{'id': i} for i in range(500)]), SimpleNamespace(data=[{'id': 500}])]
    rows = Repositorio(client).clientes()
    assert len(rows) == 501
    assert query.range.call_args_list[1].args == (500, 999)


def test_erro_sem_dados_sensiveis():
    client = Mock()
    client.rpc.return_value.execute.side_effect = RuntimeError('senha_super_secreta')
    with pytest.raises(AppError) as error:
        Repositorio(client).cadastrar(entrada())
    assert 'senha_super_secreta' not in str(error.value)


def test_fk_e_email_mensagens():
    assert 'ordens' in str(erro_banco(SimpleNamespace(code='23503')))
    assert 'ordens' in str(erro_banco(SimpleNamespace(code='23001')))
    assert 'e-mail' in str(erro_banco(SimpleNamespace(code='23505')))


def test_update_registro_inexistente():
    client = Mock()
    client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = []
    with pytest.raises(AppError, match='não encontrado'):
        Repositorio(client).atualizar_status(1, 'Aberto')
