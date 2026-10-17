-- Autor: Edman Rodrigues Miranda
-- RA: 2026600198
-- E-mail: edmanrm@gmail.com
-- Instituição: UNICAMP | Disciplina: Aplicações em Data Science
-- Professor: Prof. Dr. Francisco Fambrini
-- Atividade: Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática
-- Referência: Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

-- TechFix Informática | execute no SQL Editor de um projeto Supabase novo.
-- Script transacional: uma falha desfaz a instalação inteira.
-- Não apaga tabelas existentes. Execute uma vez; não é script de migração.
begin;

-- Membros autorizados da equipe. Apenas o proprietário do projeto gerencia esta lista.
create table public.equipe (
  usuario_id uuid primary key references auth.users(id) on delete cascade,
  criado_em timestamptz not null default now()
);
alter table public.equipe enable row level security;
create policy equipe_consulta_propria on public.equipe for select to authenticated
  using (usuario_id = (select auth.uid()));
revoke all on public.equipe from anon, authenticated;
grant select on public.equipe to authenticated;

-- Um cliente pode possuir várias ordens. E-mails são normalizados para minúsculas.
create table public.clientes (
  id bigint generated always as identity primary key,
  nome text not null check (char_length(btrim(nome)) between 2 and 120),
  endereco text not null check (char_length(btrim(endereco)) between 5 and 300),
  email text not null unique,
  celular_whatsapp text not null,
  data_cadastro timestamptz not null default now(),
  constraint clientes_email_formato check (
    email = lower(btrim(email)) and char_length(email) <= 254
    and email ~ '^[A-Za-z0-9.!#$%&''*+/=?^_`{|}~-]+@[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?(\.[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?)+$'
  ),
  constraint clientes_celular_formato check (celular_whatsapp ~ '^[0-9]{10,13}$')
);

-- RESTRICT evita apagar silenciosamente o histórico de atendimento de um cliente.
create table public.ordens_servico (
  id bigint generated always as identity primary key,
  cliente_id bigint not null references public.clientes(id) on delete restrict,
  modelo_computador text not null check (char_length(btrim(modelo_computador)) between 2 and 160),
  problema_relatado text not null check (char_length(btrim(problema_relatado)) between 5 and 4000),
  status text not null default 'Aberto'
    check (status in ('Aberto', 'Em análise', 'Aguardando peça', 'Concluído', 'Entregue')),
  data_abertura timestamptz not null default now(),
  data_atualizacao timestamptz not null default now()
);

-- Índices para relacionamentos, status e ordenação do painel.
create index ordens_cliente_idx on public.ordens_servico(cliente_id);
create index ordens_status_idx on public.ordens_servico(status);
create index ordens_abertura_idx on public.ordens_servico(data_abertura desc);

-- Atualiza automaticamente o horário no servidor, inclusive fora das interfaces.
create function public.atualizar_horario_os() returns trigger
language plpgsql set search_path = '' as $$
begin
  new.data_atualizacao := now();
  return new;
end;
$$;
create trigger ordens_horario before update on public.ordens_servico
  for each row execute function public.atualizar_horario_os();

-- RLS: a chave pública sozinha não concede acesso. Somente usuários da equipe.
alter table public.clientes enable row level security;
alter table public.ordens_servico enable row level security;
create policy clientes_equipe on public.clientes for all to authenticated
 using (exists (select 1 from public.equipe where usuario_id = (select auth.uid())))
 with check (exists (select 1 from public.equipe where usuario_id = (select auth.uid())));
create policy ordens_equipe on public.ordens_servico for all to authenticated
 using (exists (select 1 from public.equipe where usuario_id = (select auth.uid())))
 with check (exists (select 1 from public.equipe where usuario_id = (select auth.uid())));
revoke all on public.clientes, public.ordens_servico from anon, authenticated;
grant select, insert, update, delete on public.clientes, public.ordens_servico to authenticated;
grant usage, select on sequence public.clientes_id_seq, public.ordens_servico_id_seq to authenticated;

-- RPC atômica: reaproveita cliente por e-mail e abre a OS na mesma transação.
-- Não modifica os dados de um cliente existente: alterações são feitas no painel.
-- ON CONFLICT trata cadastros concorrentes sem criar clientes duplicados.
-- SECURITY INVOKER mantém todas as políticas RLS do usuário conectado.
create function public.cadastrar_ordem(
 p_nome text, p_endereco text, p_email text, p_celular text,
 p_modelo text, p_problema text
) returns table (os_id bigint, cliente_reutilizado boolean)
language plpgsql security invoker set search_path = '' as $$
declare
 v_cliente bigint;
 v_reutilizado boolean := false;
 v_os bigint;
begin
 insert into public.clientes (nome, endereco, email, celular_whatsapp)
 values (btrim(p_nome), btrim(p_endereco), lower(btrim(p_email)), btrim(p_celular))
 on conflict (email) do nothing returning id into v_cliente;
 if v_cliente is null then
   select id into strict v_cliente from public.clientes where email = lower(btrim(p_email));
   v_reutilizado := true;
 end if;
 insert into public.ordens_servico (cliente_id, modelo_computador, problema_relatado)
 values (v_cliente, btrim(p_modelo), btrim(p_problema)) returning id into v_os;
 return query select v_os, v_reutilizado;
end;
$$;
revoke all on function public.cadastrar_ordem(text,text,text,text,text,text) from public, anon;
grant execute on function public.cadastrar_ordem(text,text,text,text,text,text) to authenticated;
commit;
