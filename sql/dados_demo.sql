-- Autor: Edman Rodrigues Miranda
-- RA: 2026600198
-- E-mail: edmanrm@gmail.com
-- Instituição: UNICAMP | Disciplina: Aplicações em Data Science
-- Professor: Prof. Dr. Francisco Fambrini
-- Atividade: Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática
-- Referência: Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

-- Dados inteiramente fictícios. Execute como proprietário no SQL Editor, após schema.sql.
-- O script pode ser repetido sem duplicar os registros desta demonstração.
begin;
insert into public.clientes (nome,endereco,email,celular_whatsapp) values
 ('Ana Exemplo','Rua de Demonstração, 100','ana@example.com','11900000001'),
 ('Bruno Exemplo','Avenida de Testes, 200','bruno@example.com','11900000002'),
 ('Carla Exemplo','Rua Fictícia, 300','carla@example.com','11900000003')
on conflict (email) do nothing;
insert into public.ordens_servico (cliente_id,modelo_computador,problema_relatado,status)
select c.id, d.modelo, d.problema, d.status
from (values
 ('ana@example.com','Notebook Demo A','Equipamento não liga ao pressionar o botão.','Aberto'),
 ('bruno@example.com','Desktop Demo B','Computador reinicia durante o uso.','Em análise'),
 ('carla@example.com','Notebook Demo C','Tela permanece sem imagem.','Aguardando peça'),
 ('ana@example.com','Desktop Demo D','Sistema apresenta lentidão na inicialização.','Concluído'),
 ('bruno@example.com','Notebook Demo E','Teclado com algumas teclas sem resposta.','Entregue')
) as d(email,modelo,problema,status)
join public.clientes c on c.email=d.email
where not exists (select 1 from public.ordens_servico o where o.cliente_id=c.id and o.modelo_computador=d.modelo);
commit;
