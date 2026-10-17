// Autor: Edman Rodrigues Miranda
// RA: 2026600198
// E-mail: edmanrm@gmail.com
// Instituição: UNICAMP | Disciplina: Aplicações em Data Science
// Professor: Prof. Dr. Francisco Fambrini
// Atividade: Aula 2 — Sistema de Ordens de Serviço para a TechFix Informática
// Referência: Atividade AULA 2.pdf — Gradio + Supabase + Streamlit

// Teste isolado do PostgreSQL via PGlite. Não acessa Supabase nem dados reais.
// npm install --no-save @electric-sql/pglite
// node tests/sql_integracao.mjs .
import { PGlite } from '@electric-sql/pglite';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import assert from 'node:assert/strict';
const root = resolve(process.argv[2] || '.');
const db = new PGlite();
let count = 0;
const ok = label => { count++; console.log(`OK ${label}`); };
async function rejeita(sql, code, label) {
  await assert.rejects(db.exec(sql), e => (Array.isArray(code) ? code.includes(e.code) : e.code === code));
  ok(label);
}
await db.exec(`
 create role anon nologin;
 create role authenticated nologin;
 create schema auth;
 create table auth.users(id uuid primary key, email text);
 create function auth.uid() returns uuid language sql stable as
 $$ select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;
 grant usage on schema public, auth to anon, authenticated;
 grant execute on function auth.uid() to anon, authenticated;
`);
await db.exec(readFileSync(resolve(root, 'sql/schema.sql'), 'utf8'));
ok('schema completo instalado');
await db.exec(readFileSync(resolve(root, 'sql/dados_demo.sql'), 'utf8'));
await db.exec(readFileSync(resolve(root, 'sql/dados_demo.sql'), 'utf8'));
assert.equal((await db.query('select count(*)::int n from public.ordens_servico')).rows[0].n, 5);
ok('dados ficticios repetiveis: 5 OS');
await db.exec(`insert into auth.users values
 ('11111111-1111-1111-1111-111111111111','equipe@example.com'),
 ('22222222-2222-2222-2222-222222222222','fora@example.com');
 insert into public.equipe(usuario_id) values ('11111111-1111-1111-1111-111111111111');`);
await db.exec('set role anon');
await rejeita('select * from public.clientes', '42501', 'anonimo sem acesso');
await rejeita("select * from public.cadastrar_ordem('A A','Rua 123','a@example.com','11900000001','PC','Falha teste')", '42501', 'anonimo sem RPC');
await db.exec(`reset role; set role authenticated; set request.jwt.claim.sub = '22222222-2222-2222-2222-222222222222'`);
assert.equal((await db.query('select * from public.clientes')).rows.length, 0);
ok('usuario fora da equipe nao le clientes');
await rejeita("insert into public.clientes(nome,endereco,email,celular_whatsapp) values('Teste','Rua Teste','teste@example.com','11900000001')", '42501', 'usuario fora da equipe nao insere');
await db.exec(`set request.jwt.claim.sub = '11111111-1111-1111-1111-111111111111'`);
await rejeita("insert into public.equipe(usuario_id) values('22222222-2222-2222-2222-222222222222')", '42501', 'equipe nao pode autorizar outros usuarios');
let a = (await db.query("select * from public.cadastrar_ordem('Daniel Exemplo','Rua Teste 400',' DANIEL@example.com ','11900000004','Notebook F','Nao carrega a bateria')")).rows[0];
assert.equal(a.cliente_reutilizado, false);
let b = (await db.query("select * from public.cadastrar_ordem('Nome diferente','Outro endereco','daniel@example.com','11900000005','Desktop G','Nao liga ao iniciar')")).rows[0];
assert.equal(b.cliente_reutilizado, true);
assert.notEqual(a.os_id, b.os_id);
assert.equal((await db.query("select nome from public.clientes where email='daniel@example.com'")).rows[0].nome, 'Daniel Exemplo');
ok('RPC reutiliza cliente sem sobrescrever dados');
await rejeita("select * from public.cadastrar_ordem('Novo Cliente','Rua Teste 500','rollback@example.com','11900000006','Notebook','x')", '23514', 'OS invalida rejeitada');
assert.equal((await db.query("select count(*)::int n from public.clientes where email='rollback@example.com'")).rows[0].n, 0);
ok('falha da OS desfaz cliente novo');
await rejeita("update public.ordens_servico set status='Invalido' where id=1", '23514', 'CHECK de status');
await rejeita("update public.clientes set email='bruno@example.com' where email='ana@example.com'", '23505', 'email unico');
await rejeita("update public.clientes set celular_whatsapp='(11)900000001' where email='ana@example.com'", '23514', 'CHECK de celular');
await rejeita("update public.clientes set email='invalido' where email='ana@example.com'", '23514', 'CHECK de email');
await rejeita("delete from public.clientes where email='ana@example.com'", ['23503', '23001'], 'FK RESTRICT protege cliente com OS');
const before=(await db.query(`select * from public.ordens_servico where id=${a.os_id}`)).rows[0];
await db.exec(`update public.ordens_servico set status='Concluído', data_atualizacao='2000-01-01' where id=${a.os_id}`);
const after=(await db.query(`select * from public.ordens_servico where id=${a.os_id}`)).rows[0];
assert.equal(after.status,'Concluído');
assert.equal(String(after.data_abertura),String(before.data_abertura));
assert.notEqual(String(after.data_atualizacao), '2000-01-01T00:00:00.000Z');
ok('trigger atualiza horario e preserva abertura');
await db.exec("delete from public.ordens_servico where cliente_id=(select id from public.clientes where email='daniel@example.com'); delete from public.clientes where email='daniel@example.com'");
assert.equal((await db.query("select * from public.clientes where email='daniel@example.com'")).rows.length,0);
ok('exclusao apos remover OS vinculadas');
await db.close();
console.log(`${count} verificacoes SQL aprovadas.`);
