-- Executar no SQL Editor para registrar a ordem das novas respostas.
begin;
create sequence if not exists public.trilha_respostas_answer_order_seq;
alter table public.trilha_respostas add column if not exists answer_order bigint;
alter sequence public.trilha_respostas_answer_order_seq owned by public.trilha_respostas.answer_order;
alter table public.trilha_respostas alter column answer_order
  set default nextval('public.trilha_respostas_answer_order_seq'::regclass);
revoke insert on public.trilha_respostas from authenticated;
grant select on public.trilha_respostas to authenticated;
grant insert (user_id, attempt, topic, question, selected) on public.trilha_respostas to authenticated;
grant usage on sequence public.trilha_respostas_answer_order_seq to authenticated;
commit;
