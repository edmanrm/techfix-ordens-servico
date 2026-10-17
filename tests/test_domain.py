# Autor: Edman Rodrigues Miranda
# RA: 2026600198
# E-mail: edmanrm@gmail.com
# Instituição: UNICAMP | Disciplina: Aplicações em Data Science
# Professor: Prof. Dr. Francisco Fambrini
# Atividade: Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática
# Referência: Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

import pytest
from domain import AppError, OrdemEntrada, contato, filtrar_ordens


def entrada(**kw):
    values = dict(nome='Ana Exemplo', endereco='Rua de Teste, 100', email='ANA@example.com', celular='11900000001', modelo='Notebook Demo', problema='Não liga ao pressionar o botão.')
    values.update(kw)
    return OrdemEntrada(**values)


def test_normalizacao():
    assert entrada().rpc_params()['p_email'] == 'ana@example.com'


@pytest.mark.parametrize('kw', [dict(nome=''), dict(endereco='x'), dict(email='a@b'), dict(email='a@-bad.com'), dict(celular='(11)900000001'), dict(celular='１２３４５６７８９０'), dict(celular='123'), dict(modelo=''), dict(problema='x')])
def test_rejeita_invalido(kw):
    with pytest.raises(AppError):
        entrada(**kw).rpc_params()


def test_filtros_combinados():
    rows = [dict(id=1, status='Aberto', clientes=dict(nome='Ana Exemplo', email='ana@example.com')), dict(id=2, status='Entregue', clientes=dict(nome='Bruno', email='bruno@example.com'))]
    assert [x['id'] for x in filtrar_ordens(rows, 'ANA', '@EXAMPLE', ['Aberto'])] == [1]
    assert filtrar_ordens(rows, 'Ana', '', ['Entregue']) == []
