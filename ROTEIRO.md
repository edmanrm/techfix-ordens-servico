# Roteiro de desenvolvimento, execução e apresentação

**Autor:** Edman Rodrigues Miranda  
**RA:** 2026600198  
**E-mail:** edmanrm@gmail.com  
**Instituição:** UNICAMP  
**Disciplina:** Aplicações em Data Science  
**Professor:** Prof. Dr. Francisco Fambrini  
**Atividade:** Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática  
**Referência:** Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

## Preparação e construção por etapas

### Etapa 1 — Entender o processo

A TechFix recebe um equipamento, cadastra ou identifica o cliente e abre uma OS. O gerente acompanha o reparo até a entrega. Um cliente pode trazer vários equipamentos; por isso existe um relacionamento 1:N entre `clientes` e `ordens_servico`. O enunciado não exige controle financeiro, peças em estoque nem cadastro separado de equipamentos.

Confira os arquivos `domain.py` (regras), `backend.py` (acesso ao banco) e as duas interfaces. As telas compartilham as regras e o banco, mas não precisam estar no mesmo processo.

### Etapa 2 — Instalar o banco

Siga a seção 2 do README: crie projeto, execute schema, crie usuário e autorize na equipe. No Table Editor, veja as tabelas `clientes`, `ordens_servico` e `equipe`.

Explique os pontos do SQL:

- Identity cria o ID sem o usuário precisar digitá-lo.
- E-mail único identifica cliente já cadastrado; o programa normaliza para minúsculas.
- FK relaciona cada OS a um cliente e RESTRICT protege o histórico contra exclusões em cascata.
- CHECK valida status, tamanho dos textos, e-mail e celular no próprio banco.
- Trigger preenche data_atualizacao; data_abertura preserva o horário original.
- RLS exige usuário autenticado e autorizado na equipe.
- RPC mantém cliente e OS na mesma transação, incluindo proteção contra e-mails concorrentes.

Execute dados_demo.sql se quiser começar com exemplos. São três clientes e cinco OS fictícias. O Table Editor usa privilégios do proprietário; conseguir ver dados ali não prova que as políticas de acesso estão corretas para um usuário do aplicativo.

### Etapa 3 — Conectar e testar Gradio

Configure .env, rode o diagnóstico e execute o Gradio. Entre com o usuário da equipe. Cadastre:

| Campo | Exemplo fictício |
|---|---|
| Nome | Daniel Exemplo |
| Endereço | Rua de Demonstração, 400 |
| E-mail | daniel@example.com |
| Celular | 11900000004 |
| Equipamento | Notebook Demo F |
| Problema | Equipamento não carrega a bateria. |

Anote o número real da OS retornada; não presuma uma sequência específica. Confirme que o status é Aberto. Teste Limpar. Abra o link temporário no celular e repita com outro modelo para o mesmo e-mail: deve haver um cliente e duas OS, sem sobrescrever o cliente existente.

### Etapa 4 — Testar Streamlit

Execute o painel em outro terminal e entre. Consulte a OS cadastrada pelo Gradio. Use os filtros laterais por nome, e-mail e status. Cadastre outra OS pela aba Cadastrar. Em Editar/Excluir, altere o status e edite endereço, e-mail e celular. Atualize os dados e confirme o resultado. Em Indicadores, veja as contagens e o gráfico. Exporte o CSV da consulta filtrada.

### Etapa 5 — Testar exclusões

Use apenas registros fictícios descartáveis. Clique Excluir OS sem confirmar: deve haver aviso, sem exclusão. Confirme a OS selecionada e exclua. Para um cliente que ainda possui OS, confirme a exclusão: o banco deve impedir. Exclua primeiro as OS desse cliente e só então o cliente. Esse comportamento é intencional e demonstra integridade referencial.

## Matriz de testes manuais no Supabase real

Marque apenas após executar e registrar o resultado. Estes itens ainda não estão homologados no seu projeto.

| Caso | Ação | Resultado esperado | Executado |
|---|---|---|---|
| T01 | Login com usuário autorizado | Acesso às interfaces | ☐ |
| T02 | Login com usuário fora da equipe | Acesso recusado | ☐ |
| T03 | Abrir sem login | Não exibir nem gravar cadastros | ☐ |
| T04 | Cadastro completo novo | Um cliente e uma OS Aberto | ☐ |
| T05 | Mesmo e-mail, outro equipamento | Mesmo cliente, nova OS | ☐ |
| T06 | E-mail maiúsculo com espaços nas bordas | Normalizar e reaproveitar cliente | ☐ |
| T07 | Campo vazio, e-mail inválido ou telefone com letras | Rejeitar antes da gravação | ☐ |
| T08 | Nome + e-mail + status nos filtros | Interseção dos filtros | ☐ |
| T09 | Editar status e contato | Persistir no banco e refletir nas telas | ☐ |
| T10 | Alterar e-mail para o de outro cliente | Rejeitar duplicidade | ☐ |
| T11 | Exclusão sem confirmação | Preservar registro | ☐ |
| T12 | Excluir cliente com OS | Bloquear por FK | ☐ |
| T13 | Excluir OS e depois cliente sem OS | Remover somente registros confirmados | ☐ |
| T14 | Filtrar e exportar CSV | Mesmas linhas da consulta, acentos corretos | ☐ |
| T15 | Sem resultados | Tabela vazia e indicadores zerados | ☐ |
| T16 | Link temporário no celular | Login e formulário utilizáveis | ☐ |
| T17 | Projeto/chave incorretos ou rede indisponível | Mensagem amigável, sem segredos | ☐ |
| T18 | Atualizar status | data_atualizacao muda; data_abertura preservada | ☐ |

## Apresentação sugerida — aproximadamente 8 minutos

1. **Contexto (45 s):** “A TechFix precisava substituir o atendimento em papel. Criamos uma tela de balcão e um painel de gestão usando o mesmo banco em nuvem.”
2. **Modelo de dados (1 min):** mostre as duas tabelas principais, PK, FK, e-mail único, os cinco status e a regra de exclusão.
3. **Atendimento (2 min):** faça login, registre um atendimento fictício, mostre o número da OS e reutilize o e-mail com outro equipamento.
4. **Gestão (2 min):** localize a OS, filtre, edite status e contato; mostre a confirmação de exclusão e a proteção do cliente com OS.
5. **Indicadores (45 s):** exiba contagem por status, gráfico e exportação CSV.
6. **Segurança e validação (1 min):** mostre .env.example vazio, explique login/RLS e apresente resultados realmente executados. Não abra o .env nem mostre senhas na apresentação.
7. **Encerramento (30 s):** mostre as evidências, o roteiro e a estrutura entregue.

## Evidências obrigatórias

Use a lista em `evidencias/LEIA-ME.md`. Fotografe/capture telas reais e legíveis. O print mobile deve vir do celular: uma emulação de navegador pode ajudar a verificar o layout, mas não substitui a evidência pedida no enunciado.

## Relação entre requisito e implementação

| Requisito | Onde conferir |
|---|---|
| Duas tabelas, PK/FK, NOT NULL, UNIQUE e CHECK | sql/schema.sql |
| Índices, horário automático e políticas | sql/schema.sql |
| Blocks, Row/Column, labels, placeholders e Limpar | app_gradio.py |
| Cadastro de cliente novo/existente e OS inicial Aberto | backend.py + cadastrar_ordem no SQL |
| share=True | launch com share=not args.local; padrão público |
| Consulta com dados do cliente e filtros laterais | app_streamlit.py, aba Consultar |
| Inserção, edição e exclusão com confirmação | app_streamlit.py, Cadastrar e Editar/Excluir |
| Métricas, gráfico e CSV | app_streamlit.py, Indicadores e Consultar |
| Credenciais externas e .gitignore | backend.py, .env.example e .gitignore |
| Erros amigáveis e dados fictícios | backend.py, domain.py, sql/dados_demo.sql |
| Capturas reais da entrega | evidencias/; completar após configurar Supabase |
