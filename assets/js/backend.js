// A chave publishable identifica o projeto. O acesso aos registros é protegido por RLS.
export const db = window.supabase.createClient(
  'https://hjbrhrolzeadbtywfyzp.supabase.co',
  'sb_publishable_wqz9uB1qa9FGvajtLLSIlw_JKgzCMV3'
);

export function result(response) {
  if (response.error) throw new Error(response.error.message);
  return response.data;
}

export async function myRows(table, order) {
  const rows = [];
  for (let start = 0; ; start += 500) {
    let query = db.from(table).select('*');
    for (const column of order) query = query.order(column);
    const batch = result(await query.range(start, start + 499));
    rows.push(...batch);
    if (batch.length < 500) return rows;
  }
}
