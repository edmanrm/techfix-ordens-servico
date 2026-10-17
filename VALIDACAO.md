# Validação da entrega — 16/10/2026

## Verificações concluídas localmente

- **24 testes Python aprovados**, executados com pytest. Cobertura: campos inválidos, normalização, filtros combinados, RPC, paginação com 501 registros, mensagens sem segredos, edição de status, confirmação de exclusão, tabela vazia, métricas, exportação CSV e montagem do Gradio.
- **17 verificações SQL aprovadas** em PostgreSQL embarcado PGlite 0.5.10: instalação integral, dados fictícios repetíveis, permissões anônimas, usuário fora da equipe, proteção da lista da equipe, cliente reaproveitado, rollback de cliente após OS inválida, CHECK, UNIQUE, FK RESTRICT, trigger e exclusão de cliente sem vínculos.
- Os três scripts SQL foram analisados pelo parser PostgreSQL pglast.
- Gradio e Streamlit iniciaram localmente e abriram no Chrome. Capturas das telas de login em evidencias/. A tela inicial do Gradio foi capturada em largura de 390 px e não apresentou transbordamento horizontal.
- Logo inspecionado e integrado às duas telas: PNG RGBA, 1983 × 793 pixels, com canal alfa variando de 0 a 255 (transparência presente).
- Dependências do ambiente de teste registradas em requirements-lock.txt.

Ambiente: Python 3.12, Gradio 6.30.0, Streamlit 1.66.0, supabase-py 2.33.0, pandas 2.3.3, macOS ARM64.

## Limites e pendências de homologação

Nenhum projeto Supabase do aluno foi acessado ou alterado. Os testes SQL reproduzem os papéis e a função auth.uid() em um banco isolado; não validam configuração do serviço Auth, JWT, PostgREST, rede, latência ou políticas já existentes na conta real.

Os testes de interação do painel usam um repositório substituto. As capturas de login não comprovam cadastro real. O formulário autenticado e o painel devem ser testados com o projeto Supabase configurado, seguindo a matriz de ROTEIRO.md.

O link público temporário foi implementado, mas não foi criado durante esta validação local. A captura em 390 px é uma emulação, não uma captura feita no celular. As evidências exigidas pelo enunciado devem ser completadas no ambiente do aluno.

Não houve publicação permanente, criação de conta, implantação em produção ou comprovação de atendimento real. O projeto tem finalidade acadêmica e utiliza dados fictícios.

## Reproduzir os testes

Python, na pasta techfix:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

SQL opcional, com Node.js e npm instalados, na pasta techfix:

```bash
npm install --no-save @electric-sql/pglite@0.5.10
node tests/sql_integracao.mjs .
```

O teste usa banco em memória, cria papéis simulados de Supabase e descarta tudo ao encerrar. Não envie node_modules no pacote. O diagnóstico real `python scripts/verificar_conexao.py` exige as credenciais configuradas e apenas consulta os registros.
