-- Autor: Edman Rodrigues Miranda
-- RA: 2026600198
-- E-mail: edmanrm@gmail.com
-- Instituição: UNICAMP | Disciplina: Aplicações em Data Science
-- Professor: Prof. Dr. Francisco Fambrini
-- Atividade: Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática
-- Referência: Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

-- 1. No Supabase: Authentication > Users > Add user, crie um usuário de teste
--    com e-mail confirmado e senha definida por você.
-- 2. Substitua o e-mail abaixo pelo e-mail exato criado, e execute este script.
--    Nenhuma senha deve ser incluída aqui. Somente membros desta lista acessam dados.
insert into public.equipe (usuario_id)
select id from auth.users where email = 'SUBSTITUA_PELO_EMAIL_DA_EQUIPE'
on conflict do nothing;

-- Confira se o usuário foi autorizado. Se retornar zero linhas, revise o e-mail.
select u.email, e.criado_em from public.equipe e
join auth.users u on u.id = e.usuario_id;
