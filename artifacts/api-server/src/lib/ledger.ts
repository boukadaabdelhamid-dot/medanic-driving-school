type SqlClient = {
  query: (sql: string, values?: unknown[]) => Promise<{
    rows: Record<string, unknown>[];
    rowCount: number | null;
  }>;
};

export const DEFAULT_ACCOUNTS = [
  ["411", "Candidates / Clients", "asset", "debit"],
  ["512", "Bank", "asset", "debit"],
  ["530", "Cash", "asset", "debit"],
  ["613", "Operating expenses", "expense", "debit"],
  ["641", "Staff salaries", "expense", "debit"],
  ["706", "Training services revenue", "revenue", "credit"],
] as const;

export async function ensureDefaultAccounts(client: SqlClient) {
  for (const [code, name, category, normalSide] of DEFAULT_ACCOUNTS) {
    await client.query(
      `INSERT INTO erp_accounts (code, name, category, normal_side, is_active)
       VALUES ($1, $2, $3, $4, 1)
       ON CONFLICT (code) DO NOTHING`,
      [code, name, category, normalSide],
    );
  }
}

export async function accountIdByCode(client: SqlClient, code: string) {
  const result = await client.query(
    "SELECT id FROM erp_accounts WHERE code = $1 AND is_active = 1",
    [code],
  );
  if (!result.rows[0]) throw new Error(`Required account ${code} is unavailable.`);
  return Number(result.rows[0].id);
}

export async function postDoubleEntry(
  client: SqlClient,
  input: {
    entryDate: string;
    description: string;
    reference: string;
    source: string;
    createdBy: number;
    debitAccountId: number;
    creditAccountId: number;
    amount: number;
    reversalOfId?: number | null;
  },
) {
  if (
    !Number.isFinite(input.amount) ||
    input.amount <= 0 ||
    input.debitAccountId === input.creditAccountId
  ) {
    throw new Error("A balanced entry requires a positive amount and two accounts.");
  }
  const entry = await client.query(
    `INSERT INTO erp_journal_entries
       (entry_date, description, reference, source, created_by, reversal_of_id)
     VALUES ($1, $2, $3, $4, $5, $6)
     RETURNING id, entry_date, description, reference, source, created_by, reversal_of_id`,
    [
      input.entryDate,
      input.description,
      input.reference,
      input.source,
      input.createdBy,
      input.reversalOfId ?? null,
    ],
  );
  const id = Number(entry.rows[0].id);
  await client.query(
    `INSERT INTO erp_journal_lines (journal_entry_id, account_id, debit, credit)
     VALUES ($1, $2, $3, 0), ($1, $4, 0, $3)`,
    [id, input.debitAccountId, input.amount, input.creditAccountId],
  );
  return entry.rows[0];
}

export async function reverseEntryById(
  client: SqlClient,
  entryId: number,
  createdBy: number,
) {
  const originalResult = await client.query(
    "SELECT * FROM erp_journal_entries WHERE id = $1 FOR UPDATE",
    [entryId],
  );
  const original = originalResult.rows[0];
  if (!original) throw new Error("Journal entry not found.");
  const existing = await client.query(
    "SELECT id FROM erp_journal_entries WHERE reversal_of_id = $1 LIMIT 1",
    [entryId],
  );
  if (existing.rows.length) throw new Error("This journal entry has already been reversed.");
  const lines = await client.query(
    `SELECT account_id, debit, credit
       FROM erp_journal_lines WHERE journal_entry_id = $1 ORDER BY id`,
    [entryId],
  );
  if (!lines.rows.length) throw new Error("This journal entry has no ledger lines.");
  const debitTotal = lines.rows.reduce((sum, line) => sum + Number(line.debit), 0);
  const creditTotal = lines.rows.reduce((sum, line) => sum + Number(line.credit), 0);
  if (Math.abs(debitTotal - creditTotal) > 0.01) {
    throw new Error("This journal entry is not balanced.");
  }
  const reversed = await client.query(
    `INSERT INTO erp_journal_entries
       (entry_date, description, reference, source, created_by, reversal_of_id)
     VALUES (CURRENT_DATE, $1, $2, 'reversal', $3, $4)
     RETURNING id, entry_date, description, reference, source, created_by, reversal_of_id`,
    [
      `Reversal of entry #${entryId}: ${original.description}`,
      original.reference ?? "",
      createdBy,
      entryId,
    ],
  );
  const reversalId = Number(reversed.rows[0].id);
  for (const line of lines.rows) {
    await client.query(
      `INSERT INTO erp_journal_lines
         (journal_entry_id, account_id, debit, credit)
       VALUES ($1, $2, $3, $4)`,
      [reversalId, line.account_id, line.credit, line.debit],
    );
  }
  return {
    ...reversed.rows[0],
    originalId: entryId,
    reversalOfId: entryId,
    debitTotal: creditTotal,
    creditTotal: debitTotal,
  };
}

export async function reverseActiveSourceEntry(
  client: SqlClient,
  source: string,
  reference: string,
  createdBy: number,
) {
  const active = await client.query(
    `SELECT entry.id
       FROM erp_journal_entries entry
      WHERE entry.source = $1
        AND entry.reference = $2
        AND entry.reversal_of_id IS NULL
        AND NOT EXISTS (
          SELECT 1 FROM erp_journal_entries reversal
           WHERE reversal.reversal_of_id = entry.id
        )
      ORDER BY entry.id DESC
      LIMIT 1
      FOR UPDATE`,
    [source, reference],
  );
  if (!active.rows[0]) return null;
  return reverseEntryById(client, Number(active.rows[0].id), createdBy);
}
