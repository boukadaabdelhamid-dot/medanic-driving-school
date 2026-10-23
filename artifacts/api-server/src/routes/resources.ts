import { Router, type IRouter } from "express";
import { pool, type PoolClient } from "@workspace/db";
import {
  accountIdByCode,
  ensureDefaultAccounts,
  postDoubleEntry,
  reverseActiveSourceEntry,
} from "../lib/ledger";
import { getResourceDefinition, type ResourceName } from "../lib/resource-registry";
import {
  buildWhereClause,
  hydrateFieldOptions,
  isAdminOnly,
  isDerivedGraduates,
  isReadOnly,
  normalizeRow,
  parseResourceName,
  requiredPermission,
  resourceFields,
  resourceOrder,
  sqlColumns,
  tableName,
  validateResourceInput,
} from "../lib/resources";
import {
  requireAuth,
} from "../lib/auth";

const router: IRouter = Router();
router.use(requireAuth);

const JOURNAL_SELECT = `
  SELECT entry.*,
         debit_line.account_id AS debit_account_id,
         credit_line.account_id AS credit_account_id,
         COALESCE(debit_line.debit, credit_line.credit) AS amount,
         EXISTS (
           SELECT 1 FROM erp_journal_entries reversal
            WHERE reversal.reversal_of_id = entry.id
         ) AS is_reversed
    FROM erp_journal_entries entry
    LEFT JOIN LATERAL (
      SELECT account_id, debit
        FROM erp_journal_lines
       WHERE journal_entry_id = entry.id AND debit > 0
       ORDER BY id LIMIT 1
    ) debit_line ON true
    LEFT JOIN LATERAL (
      SELECT account_id, credit
        FROM erp_journal_lines
       WHERE journal_entry_id = entry.id AND credit > 0
       ORDER BY id LIMIT 1
    ) credit_line ON true`;

function canView(req: Parameters<typeof requireAuth>[0], resource: ResourceName) {
  const user = req.user;
  if (!user) return false;
  if (isAdminOnly(resource)) return user.role === "admin";
  return user.role === "admin" || user.permissions[requiredPermission(resource)] === true;
}

function canEdit(req: Parameters<typeof requireAuth>[0], resource: ResourceName) {
  const user = req.user;
  if (!user) return false;
  if (isReadOnly(resource)) return false;
  if (isAdminOnly(resource)) return user.role === "admin";
  if (user.role === "admin") return true;
  if (resource === "candidates") return user.permissions.edit_candidates === true;
  if (resource === "payments") return user.permissions.add_payments === true;
  return false;
}

function addRelations(row: Record<string, unknown>) {
  return normalizeRow(row);
}

function shapeJournalEntry(row: Record<string, unknown>) {
  return normalizeRow(row);
}

function parseFilters(query: Record<string, unknown>) {
  const from = typeof query.from === "string" ? query.from : undefined;
  const to = typeof query.to === "string" ? query.to : undefined;
  const period = typeof query.period === "string" ? query.period : undefined;
  const candidateId =
    typeof query.candidateId === "string" && /^\d+$/.test(query.candidateId)
      ? Number(query.candidateId)
      : undefined;
  if (from && !/^\d{4}-\d{2}-\d{2}$/.test(from)) throw new Error("Invalid start date.");
  if (to && !/^\d{4}-\d{2}-\d{2}$/.test(to)) throw new Error("Invalid end date.");
  if (period && !/^\d{4}-\d{2}$/.test(period)) throw new Error("Invalid period.");
  return {
    search: typeof query.search === "string" ? query.search : undefined,
    from,
    to,
    period,
    candidateId,
  };
}

async function loadRows(resource: ResourceName, filters: ReturnType<typeof parseFilters>) {
  const def = getResourceDefinition(resource);
  const { where, values } = buildWhereClause(resource, filters);
  const countQuery = isDerivedGraduates(resource)
    ? `SELECT COUNT(*)::text AS count FROM candidates c LEFT JOIN instructors i ON i.id = c.instructor_id ${where}`
    : `SELECT COUNT(*)::text AS count FROM ${tableName(resource)} ${where}`;
  const count = await pool.query(countQuery, values);
  const queryValues = [...values, 500];
  const limitPlaceholder = `$${queryValues.length}`;
  const select = isDerivedGraduates(resource)
    ? `SELECT c.*, concat_ws(' ', i.first_name, i.last_name) AS instructor_name
         FROM candidates c LEFT JOIN instructors i ON i.id = c.instructor_id ${where}
        ORDER BY ${def.orderBy.split(",").map((part) => `c.${part.trim()}`).join(", ")}
        LIMIT ${limitPlaceholder}`
    : resource === "journalEntries"
      ? `${JOURNAL_SELECT} ${where} ORDER BY ${resourceOrder(resource)} LIMIT ${limitPlaceholder}`
      : `SELECT * FROM ${tableName(resource)} ${where} ORDER BY ${resourceOrder(resource)} LIMIT ${limitPlaceholder}`;
  const result = await pool.query(select, queryValues);
  return {
    items: result.rows.map((row) =>
      resource === "journalEntries" ? shapeJournalEntry(row) : addRelations(row),
    ),
    total: Number(count.rows[0]?.count ?? 0),
  };
}

async function loadRecord(resource: ResourceName, id: number) {
  if (isDerivedGraduates(resource)) {
    const result = await pool.query(
      `SELECT c.*, concat_ws(' ', i.first_name, i.last_name) AS instructor_name
         FROM candidates c LEFT JOIN instructors i ON i.id = c.instructor_id
        WHERE c.id = $1 AND ${graduatedSqlForId}`,
      [id],
    );
    return result.rows[0] ? normalizeRow(result.rows[0]) : null;
  }
  const result =
    resource === "journalEntries"
      ? await pool.query(`${JOURNAL_SELECT} WHERE entry.id = $1`, [id])
      : await pool.query(`SELECT * FROM ${tableName(resource)} WHERE id = $1`, [id]);
  return result.rows[0]
    ? resource === "journalEntries"
      ? shapeJournalEntry(result.rows[0])
      : normalizeRow(result.rows[0])
    : null;
}

const graduatedSqlForId = `(
  (c.license_type = 'A1' AND EXISTS (
    SELECT 1 FROM training_stages ts
     WHERE ts.candidate_id = c.id AND ts.stage_type = 'code' AND ts.status = 'ناجح'
  ))
  OR (c.license_type <> 'A1' AND (
    SELECT COUNT(DISTINCT ts.stage_type) FROM training_stages ts
     WHERE ts.candidate_id = c.id AND ts.status = 'ناجح'
       AND ts.stage_type IN ('code', 'creneau', 'circuit')
  ) >= 3)
)`;

async function createJournalEntry(
  input: Record<string, unknown>,
  userId: number,
) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await ensureDefaultAccounts(client);
    const accountIds = [Number(input.debitAccountId), Number(input.creditAccountId)];
    if (
      !accountIds.every((id) => Number.isSafeInteger(id) && id > 0) ||
      accountIds[0] === accountIds[1]
    ) {
      throw new Error("Choose two different active accounts.");
    }
    const accounts = await client.query(
      `SELECT id FROM erp_accounts
        WHERE id = ANY($1::integer[]) AND is_active = 1 FOR SHARE`,
      [accountIds],
    );
    if (accounts.rowCount !== 2) throw new Error("One or more accounts are unavailable.");
    const entry = await client.query(
      `INSERT INTO erp_journal_entries (entry_date, description, reference, source, created_by)
       VALUES ($1, $2, $3, 'manual', $4)
       RETURNING id, entry_date, description, reference, source, created_by, reversal_of_id`,
      [
        input.entryDate,
        input.description,
        input.reference ?? "",
        userId,
      ],
    );
    const id = Number(entry.rows[0].id);
    await client.query(
      `INSERT INTO erp_journal_lines (journal_entry_id, account_id, debit, credit)
       VALUES ($1, $2, $3, 0), ($1, $4, 0, $3)`,
      [id, accountIds[0], input.amount, accountIds[1]],
    );
    await client.query("COMMIT");
    return {
      ...normalizeRow(entry.rows[0]),
      debitAccountId: accountIds[0],
      creditAccountId: accountIds[1],
      amount: Number(input.amount),
    };
  } catch (error) {
    await client.query("ROLLBACK").catch(() => undefined);
    throw error;
  } finally {
    client.release();
  }
}

type LedgerResource = "payments" | "expenses" | "candidates";

function ledgerSource(resource: LedgerResource) {
  return resource === "payments"
    ? "payment"
    : resource === "expenses"
      ? "expense"
      : "registration";
}

function ledgerReference(resource: LedgerResource, id: number) {
  const prefix =
    resource === "payments"
      ? "PAYMENT"
      : resource === "expenses"
        ? "EXPENSE"
        : "CANDIDATE";
  return `${prefix}-${id}`;
}

function ledgerDate(value: unknown) {
  if (value instanceof Date) return value.toISOString().slice(0, 10);
  if (typeof value === "string" && /^\d{4}-\d{2}-\d{2}/.test(value)) {
    return value.slice(0, 10);
  }
  return new Date().toISOString().slice(0, 10);
}

async function postResourceLedger(
  client: Parameters<typeof postDoubleEntry>[0],
  resource: LedgerResource,
  row: Record<string, unknown>,
  userId: number,
) {
  const amount = Number(
    resource === "candidates" ? row.total_amount : row.amount,
  );
  if (!Number.isFinite(amount) || amount <= 0) return;
  await ensureDefaultAccounts(client);
  const source = ledgerSource(resource);
  const reference = ledgerReference(resource, Number(row.id));
  let debitCode = "530";
  let creditCode = "706";
  let description = `Candidate registration #${row.id}`;
  if (resource === "payments") {
    const method = String(row.payment_method ?? "").toLowerCase();
    debitCode = /bank|transfer|check|cheque|تحويل|صك/.test(method) ? "512" : "530";
    creditCode = "411";
    description = `Candidate payment #${row.id}`;
  } else if (resource === "expenses") {
    debitCode = "613";
    creditCode = "530";
    description = `Operating expense #${row.id}: ${String(row.expense_type ?? "")}`;
  } else {
    debitCode = "411";
    creditCode = "706";
  }
  const debitAccountId = await accountIdByCode(client, debitCode);
  const creditAccountId = await accountIdByCode(client, creditCode);
  await postDoubleEntry(client, {
    entryDate: ledgerDate(
      resource === "candidates" ? row.registration_date : row.date,
    ),
    description,
    reference,
    source,
    createdBy: userId,
    debitAccountId,
    creditAccountId,
    amount,
  });
}

async function refreshResourceLedger(
  client: Parameters<typeof postDoubleEntry>[0],
  resource: LedgerResource,
  id: number,
  row: Record<string, unknown>,
  userId: number,
) {
  await reverseActiveSourceEntry(
    client,
    ledgerSource(resource),
    ledgerReference(resource, id),
    userId,
  );
  await postResourceLedger(client, resource, row, userId);
}

function isLedgerResource(resource: ResourceName): resource is LedgerResource {
  return resource === "payments" || resource === "expenses" || resource === "candidates";
}

router.get("/:resource", async (req, res) => {
  const resource = parseResourceName(req.params.resource);
  if (!resource) {
    res.status(404).json({ error: "Unknown resource." });
    return;
  }
  if (!canView(req, resource)) {
    res.status(403).json({ error: "You do not have permission to view this section." });
    return;
  }
  try {
    if (resource === "accounts" || resource === "journalEntries") {
      await ensureDefaultAccounts(pool);
    }
    const filters = parseFilters(req.query as Record<string, unknown>);
    const [page, fields] = await Promise.all([
      loadRows(resource, filters),
      hydrateFieldOptions(
        pool,
        resource,
        typeof req.query.language === "string" ? req.query.language : "ar",
      ),
    ]);
    res.json({ ...page, fields, total: page.total });
  } catch (error) {
    if (error instanceof Error && /Invalid /.test(error.message)) {
      res.status(400).json({ error: error.message });
      return;
    }
    req.log.error({ err: error, resource }, "Could not list resource records");
    res.status(500).json({ error: "Could not load these records." });
  }
});

router.post("/:resource", async (req, res) => {
  const resource = parseResourceName(req.params.resource);
  if (!resource) {
    res.status(404).json({ error: "Unknown resource." });
    return;
  }
  if (!canEdit(req, resource)) {
    res.status(403).json({ error: "You do not have permission to change this section." });
    return;
  }
  const ledgerResource = isLedgerResource(resource) ? resource : null;
  let transactionClient: PoolClient | null = null;
  try {
    const input = validateResourceInput(resource, req.body, true);
    if (resource === "journalEntries") {
      const entry = await createJournalEntry(input, req.user!.id);
      res.status(201).json(entry);
      return;
    }
    const columns = sqlColumns(resource, input);
    if (!columns.length) {
      res.status(400).json({ error: "Enter at least one field." });
      return;
    }
    const names = columns.map((item) => item.column);
    const placeholders = columns.map((_, index) => `$${index + 1}`);
    const values = columns.map((item) =>
      item.column === "permissions" && item.value
        ? JSON.stringify(item.value)
        : item.value,
    );
    transactionClient = ledgerResource ? await pool.connect() : null;
    if (transactionClient) await transactionClient.query("BEGIN");
    const result = await (transactionClient ?? pool).query(
      `INSERT INTO ${tableName(resource)} (${names.join(", ")})
       VALUES (${placeholders.join(", ")})
       RETURNING *`,
      values,
    );
    if (transactionClient && ledgerResource) {
      await postResourceLedger(transactionClient, ledgerResource, result.rows[0], req.user!.id);
      await transactionClient.query("COMMIT");
    }
    res.status(201).json(normalizeRow(result.rows[0]));
  } catch (error) {
    await transactionClient?.query("ROLLBACK").catch(() => undefined);
    const code = (error as { code?: string }).code;
    if (error instanceof Error && !code) {
      res.status(400).json({ error: error.message });
      return;
    }
    if (code === "23505") {
      res.status(409).json({ error: "A record with that unique value already exists." });
      return;
    }
    if (code === "23503" || code === "23514") {
      res.status(409).json({ error: "This record refers to unavailable related data." });
      return;
    }
    req.log.error({ err: error, resource }, "Could not create resource record");
    res.status(500).json({ error: "Could not create this record." });
  } finally {
    transactionClient?.release();
  }
});

router.get("/:resource/:id", async (req, res) => {
  const resource = parseResourceName(req.params.resource);
  const id = Number(req.params.id);
  if (!resource || !Number.isSafeInteger(id) || id < 1) {
    res.status(404).json({ error: "Record not found." });
    return;
  }
  if (!canView(req, resource)) {
    res.status(403).json({ error: "You do not have permission to view this section." });
    return;
  }
  try {
    const record = await loadRecord(resource, id);
    if (!record) {
      res.status(404).json({ error: "Record not found." });
      return;
    }
    res.json(record);
  } catch (error) {
    req.log.error({ err: error, resource, id }, "Could not read resource record");
    res.status(500).json({ error: "Could not load this record." });
  }
});

router.patch("/:resource/:id", async (req, res) => {
  const resource = parseResourceName(req.params.resource);
  const id = Number(req.params.id);
  if (!resource || !Number.isSafeInteger(id) || id < 1) {
    res.status(404).json({ error: "Record not found." });
    return;
  }
  if (!canEdit(req, resource)) {
    res.status(403).json({ error: "You do not have permission to change this section." });
    return;
  }
  if (resource === "journalEntries") {
    res.status(409).json({ error: "Journal entries are immutable; post a reversal instead." });
    return;
  }
  if (resource === "payroll") {
    const current = await pool.query(
      "SELECT status FROM erp_payroll WHERE id = $1",
      [id],
    );
    if (!current.rows[0]) {
      res.status(404).json({ error: "Record not found." });
      return;
    }
    if (current.rows[0].status === "paid") {
      res.status(409).json({ error: "Paid payroll records are immutable." });
      return;
    }
  }
  const ledgerResource = isLedgerResource(resource) ? resource : null;
  let transactionClient: PoolClient | null = null;
  try {
    const input = validateResourceInput(resource, req.body, false);
    if (!Object.keys(input).length) {
      res.status(400).json({ error: "Enter at least one field to update." });
      return;
    }
    const columns = sqlColumns(resource, input);
    if (!columns.length) {
      res.status(400).json({ error: "Enter at least one field to update." });
      return;
    }
    const values = columns.map((item) =>
      item.column === "permissions" && item.value
        ? JSON.stringify(item.value)
        : item.value,
    );
    values.push(id);
    const assignments = columns.map(
      (item, index) => `${item.column} = $${index + 1}`,
    );
    transactionClient = ledgerResource || resource === "payroll" ? await pool.connect() : null;
    if (transactionClient) {
      await transactionClient.query("BEGIN");
      const current = await transactionClient.query(
        `SELECT * FROM ${tableName(resource)} WHERE id = $1 FOR UPDATE`,
        [id],
      );
      if (!current.rows[0]) {
        await transactionClient.query("ROLLBACK");
        res.status(404).json({ error: "Record not found." });
        return;
      }
      if (resource === "payroll" && current.rows[0].status === "paid") {
        await transactionClient.query("ROLLBACK");
        res.status(409).json({ error: "Paid payroll records are immutable." });
        return;
      }
    }
    const result = await (transactionClient ?? pool).query(
      `UPDATE ${tableName(resource)}
          SET ${assignments.join(", ")}
        WHERE id = $${values.length}
        RETURNING *`,
      values,
    );
    if (!result.rows[0]) {
      await transactionClient?.query("ROLLBACK");
      res.status(404).json({ error: "Record not found." });
      return;
    }
    if (transactionClient) {
      if (ledgerResource) {
        await refreshResourceLedger(
          transactionClient,
          ledgerResource,
          id,
          result.rows[0],
          req.user!.id,
        );
      }
      await transactionClient.query("COMMIT");
    }
    res.json(normalizeRow(result.rows[0]));
  } catch (error) {
    await transactionClient?.query("ROLLBACK").catch(() => undefined);
    const code = (error as { code?: string }).code;
    if (error instanceof Error && !code) {
      res.status(400).json({ error: error.message });
      return;
    }
    if (code === "23505") {
      res.status(409).json({ error: "A record with that unique value already exists." });
      return;
    }
    if (code === "23503" || code === "23514") {
      res.status(409).json({ error: "This record refers to unavailable related data." });
      return;
    }
    req.log.error({ err: error, resource, id }, "Could not update resource record");
    res.status(500).json({ error: "Could not update this record." });
  } finally {
    transactionClient?.release();
  }
});

router.delete("/:resource/:id", async (req, res) => {
  const resource = parseResourceName(req.params.resource);
  const id = Number(req.params.id);
  if (!resource || !Number.isSafeInteger(id) || id < 1) {
    res.status(404).json({ error: "Record not found." });
    return;
  }
  if (!canEdit(req, resource)) {
    res.status(403).json({ error: "You do not have permission to change this section." });
    return;
  }
  if (resource === "journalEntries") {
    res.status(409).json({ error: "Journal entries are immutable; post a reversal instead." });
    return;
  }
  if (resource === "users" && id === req.user?.id) {
    res.status(409).json({ error: "You cannot delete the account currently in use." });
    return;
  }
  const ledgerResource = isLedgerResource(resource) ? resource : null;
  let transactionClient: PoolClient | null = null;
  try {
    transactionClient = ledgerResource || resource === "payroll" ? await pool.connect() : null;
    if (transactionClient) {
      await transactionClient.query("BEGIN");
      const current = await transactionClient.query(
        `SELECT * FROM ${tableName(resource)} WHERE id = $1 FOR UPDATE`,
        [id],
      );
      if (!current.rows[0]) {
        await transactionClient.query("ROLLBACK");
        res.status(404).json({ error: "Record not found." });
        return;
      }
      if (resource === "payroll" && current.rows[0].status === "paid") {
        await transactionClient.query("ROLLBACK");
        res.status(409).json({ error: "Paid payroll records are immutable." });
        return;
      }
      if (ledgerResource) {
        await reverseActiveSourceEntry(
          transactionClient,
          ledgerSource(ledgerResource),
          ledgerReference(ledgerResource, id),
          req.user!.id,
        );
      }
    }
    const result = await (transactionClient ?? pool).query(
      `DELETE FROM ${tableName(resource)} WHERE id = $1`,
      [id],
    );
    if (!result.rowCount) {
      await transactionClient?.query("ROLLBACK");
      res.status(404).json({ error: "Record not found." });
      return;
    }
    if (transactionClient) await transactionClient.query("COMMIT");
    res.status(204).end();
  } catch (error) {
    await transactionClient?.query("ROLLBACK").catch(() => undefined);
    if ((error as { code?: string }).code === "23503") {
      res.status(409).json({
        error: "This record is linked to other records and cannot be deleted.",
      });
      return;
    }
    req.log.error({ err: error, resource, id }, "Could not delete resource record");
    res.status(500).json({ error: "Could not delete this record." });
  } finally {
    transactionClient?.release();
  }
});

export default router;
