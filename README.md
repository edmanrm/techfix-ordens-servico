# TechFix Informática — Ordens de serviço

**Autor:** Edman Rodrigues Miranda  
**RA:** 2026600198  
**E-mail:** edmanrm@gmail.com  
**Instituição:** UNICAMP  
**Disciplina:** Aplicações em Data Science  
**Professor:** Prof. Dr. Francisco Fambrini  
**Atividade:** Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática  
**Referência:** Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

Projeto acadêmico da atividade **Atividade AULA 2.pdf**, anexada pelo aluno: atendimento em Gradio, gestão em Streamlit e armazenamento central no Supabase/PostgreSQL. Este enunciado trata de assistência técnica; não é o exercício anterior de vendas/MongoDB/Tkinter.

## O que foi entregue

- `app_gradio.py`: formulário em Blocks, responsivo, com login, cadastro e limpeza.
- `app_streamlit.py`: consulta, filtros, cadastro, edição, exclusão confirmada, métricas, gráfico e exportação CSV.
- `backend.py` e `domain.py`: integração compartilhada, validações e mensagens de erro.
- `sql/schema.sql`: tabelas, integridade, índices, trigger, RLS e função transacional de cadastro.
- `sql/autorizar_equipe.sql`: autorização de usuários criados no Supabase Auth.
- `sql/dados_demo.sql`: três clientes e cinco OS fictícias, uma por status.
- `ROTEIRO.md`: preparação, testes, apresentação e evidências.
- `assets/techfix-logo.png`: logo original com fundo transparente, aplicado às duas telas.
- `tests/`: testes automatizados; `scripts/verificar_conexao.py`: diagnóstico real, somente leitura.

## 1. Preparar o Python

Use Python 3.11 ou 3.12. Abra o terminal **dentro da pasta techfix**.

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Se o PowerShell bloquear a ativação, execute diretamente `.venv\Scripts\python.exe` e `.venv\Scripts\streamlit.exe`; não é necessário alterar políticas do computador.

As faixas em requirements.txt limitam versões principais. `requirements-lock.txt` registra as versões efetivamente testadas em Python 3.12/macOS; para reproduzi-las, use `python -m pip install -r requirements-lock.txt`. Algumas dependências podem precisar de wheels específicos em outros sistemas.

## 2. Preparar o Supabase

1. Crie um projeto próprio dedicado ao exercício.
2. No SQL Editor, execute **uma vez** `sql/schema.sql`. O script cria objetos novos; não deve ser reaplicado sobre uma instalação existente.
3. Em Authentication > Users, crie o usuário da equipe, com e-mail confirmado e senha própria. Desative novos cadastros públicos em Authentication se não forem necessários.
4. Edite somente o e-mail em `sql/autorizar_equipe.sql` e execute. Confira que a consulta final retorna esse usuário.
5. Opcionalmente execute `sql/dados_demo.sql` para carregar os exemplos fictícios. O script de demonstração é repetível e não remove dados.
6. Em Project Settings, copie a URL do projeto e a chave pública `anon` ou `publishable`. **Não use a service_role nem uma chave secret.**
7. Preencha localmente `.env`:

```dotenv
SUPABASE_URL=https://SEU_PROJETO.supabase.co
SUPABASE_KEY=SUA_CHAVE_PUBLICA
```

A senha do usuário é digitada na tela de login. Não precisa ser colocada no código nem no .env. A senha do banco PostgreSQL é diferente da senha desse usuário.

Para o Streamlit, uma alternativa é copiar `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e preencher as mesmas duas variáveis. Variáveis de ambiente/.env têm prioridade sobre os secrets. O Gradio usa ambiente/.env.

### Como o acesso funciona

A chave pública identifica o projeto. O login Supabase Auth identifica o usuário. As políticas RLS permitem operações apenas para usuários incluídos na tabela `equipe`. Usuários anônimos e usuários autenticados fora da equipe não leem nem alteram os cadastros. A tabela `equipe` só pode ser administrada pelo proprietário no SQL Editor; o aplicativo pode apenas consultar a própria autorização. Todos os membros autorizados têm o mesmo acesso acadêmico de gestão, inclusive exclusão. Não há distinção de papéis gerente/atendente nesta versão.

## 3. Verificar a conexão real

```bash
python scripts/verificar_conexao.py
```

Informe usuário e senha quando solicitado. O diagnóstico autentica e consulta contagens por leitura; não cadastra nem exclui dados. Se falhar, confira URL, chave, execução do schema, confirmação do usuário e autorização na equipe.

## 4. Executar as aplicações

Terminal 1, na pasta techfix, com o ambiente ativo:

```bash
python app_gradio.py
```

Abra http://127.0.0.1:7860. O padrão usa `share=True` e tenta gerar um link público temporário, exibido no terminal. Abra **esse link HTTPS** no celular e entre com o usuário da equipe. Mantenha o processo ligado. O link depende de internet e do serviço de compartilhamento do Gradio; não é hospedagem permanente.

Para testar só no computador, sem criar o link:

```bash
python app_gradio.py --local
```

Terminal 2, com o mesmo ambiente ativo:

```bash
streamlit run app_streamlit.py
```

Abra http://localhost:8501 e entre. As sessões das duas interfaces são independentes. Se uma sessão expirar, entre novamente. Não é necessário configurar MongoDB nem Tkinter para este novo enunciado.

## 5. Comportamentos importantes

- E-mail é normalizado para minúsculas. E-mail existente reaproveita o cliente sem atualizar nome/endereço/telefone automaticamente.
- Cliente e OS são gravados na mesma transação pela RPC `cadastrar_ordem`. Se a OS falhar, um cliente novo também é desfeito.
- Cliques repetidos após um cadastro bem-sucedido criam ordens distintas. Depois de sucesso, use **Limpar**. Se houver erro de rede, consulte o painel antes de tentar de novo: a resposta pode ter se perdido depois da gravação.
- A OS começa em `Aberto`. O banco aceita somente os cinco status do enunciado.
- O horário de atualização é definido por trigger no PostgreSQL. O painel mostra os horários de São Paulo.
- Exclusões exigem confirmação específica do registro. Clientes com OS vinculadas são protegidos por `ON DELETE RESTRICT`.
- Filtros de nome, e-mail e status se combinam. Indicadores e CSV seguem os mesmos filtros. A aba de edição apresenta todos os registros e informa esse escopo.
- CSV inclui BOM UTF-8, separador `;` e proteção contra interpretação de texto como fórmula em planilhas.
- O aplicativo lê todas as páginas da API (500 registros por página) antes de filtrar. Adequado à atividade; grandes volumes exigem filtros e agregações no servidor.

## 6. Testes e entrega

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Os testes Python usam substitutos de banco e verificam regras, paginação e interações do painel. Eles não confirmam a instalação em uma conta Supabase. Consulte `VALIDACAO.md` para a evidência local e o que falta executar no ambiente real.

A pasta `evidencias/` contém o roteiro dos prints e apenas capturas locais identificadas como tais. As evidências reais do celular, cadastro e Table Editor devem ser feitas depois de configurar seu Supabase; não foram fabricadas.

Para gerar um ZIP sem credenciais, caches ou ambiente virtual:

```bash
python scripts/empacotar.py
```

O ZIP é criado ao lado da pasta techfix. Revise as capturas antes de enviar e oculte senhas, tokens e dados pessoais. Não entregue .env, secrets.toml nem .venv. Caso o professor precise testar o sistema, compartilhe o acesso de um usuário fictício autorizado por um canal separado.

## Referências técnicas

- Enunciado fornecido pelo aluno: Atividade AULA 2.pdf, 4 páginas.
- [Supabase Python: login com senha](https://supabase.com/docs/reference/python/auth-signinwithpassword)
- [Supabase: Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Supabase Python: funções PostgreSQL](https://supabase.com/docs/reference/python/rpc)
- [Gradio: Blocks](https://www.gradio.app/docs/gradio/blocks)
- [Gradio: compartilhamento](https://www.gradio.app/guides/sharing-your-app)
- [Streamlit: documentação](https://docs.streamlit.io/)
- [PostgreSQL: restrições](https://www.postgresql.org/docs/current/ddl-constraints.html)
