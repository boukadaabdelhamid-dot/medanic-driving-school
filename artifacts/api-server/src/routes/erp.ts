import { Router, type IRouter } from "express";
import { pool } from "@workspace/db";
import { requireAdmin, requireAuth } from "../lib/auth";
import {
  accountIdByCode,
  ensureDefaultAccounts,
  postDoubleEntry,
} from "../lib/ledger";

const router: IRouter = Router();
router.use(requireAuth, requireAdmin);

function parseId(value: string | string[] | undefined) {
  const raw = Array.isArray(value) ? value[0] : value;
  const id = Number(raw);
  return Number.isSafeInteger(id) && id > 0 ? id : null;
}

router.post("/erp/journal/:id/reverse", async (req, res) => {
  const originalId = parseId(req.params.id);
  if (!originalId) {
    res.status(400).json({ error: "Journal entry ID is invalid." });
    return;
  }
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const originalResult = await client.query(
      `SELECT * FROM erp_journal_entries WHERE id = $1 FOR UPDATE`,
      [originalId],
    );
    const original = originalResult.rows[0];
    if (!original) {
      await client.query("ROLLBACK");
      res.status(404).json({ error: "Journal entry not found." });
      return;
    }
    const existingReversal = await client.query(
      "SELECT id FROM erp_journal_entries WHERE reversal_of_id = $1 LIMIT 1",
      [originalId],
    );
    if (existingReversal.rows.length) {
      await client.query("ROLLBACK");
      res.status(409).json({ error: "This journal entry has already been reversed." });
      return;
    }
    const lines = await client.query(
      `SELECT account_id, debit, credit
         FROM erp_journal_lines WHERE journal_entry_id = $1 ORDER BY id`,
      [originalId],
    );
    if (!lines.rows.length) {
      await client.query("ROLLBACK");
      res.status(409).json({ error: "This journal entry has no ledger lines." });
      return;
    }
    const debitTotal = lines.rows.reduce((sum, line) => sum + Number(line.debit), 0);
    const creditTotal = lines.rows.reduce((sum, line) => sum + Number(line.credit), 0);
    if (Math.abs(debitTotal - creditTotal) > 0.01) {
      await client.query("ROLLBACK");
      res.status(409).json({ error: "This journal entry is not balanced." });
      return;
    }
    const reversed = await client.query(
      `INSERT INTO erp_journal_entries
         (entry_date, description, reference, source, created_by, reversal_of_id)
       VALUES (CURRENT_DATE, $1, $2, 'reversal', $3, $4)
       RETURNING id, entry_date, description, reference, source, created_by, reversal_of_id`,
      [
        `Reversal of entry #${originalId}: ${original.description}`,
        original.reference ?? "",
        req.user!.id,
        originalId,
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
    await client.query("COMMIT");
    res.status(201).json({
      ...reversed.rows[0],
      originalId,
      reversalOfId: originalId,
      debitTotal: creditTotal,
      creditTotal: debitTotal,
    });
  } catch (error) {
    await client.query("ROLLBACK").catch(() => undefined);
    req.log.error({ err: error, originalId }, "Journal entry reversal failed");
    res.status(500).json({ error: "Could not reverse this journal entry." });
  } finally {
    client.release();
  }
});

router.post("/erp/payroll/:id/pay", async (req, res) => {
  const payrollId = parseId(req.params.id);
  if (!payrollId) {
    res.status(400).json({ error: "Payroll item ID is invalid." });
    return;
  }
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await ensureDefaultAccounts(client);
    const result = await client.query(
      `SELECT p.*, concat_ws(' ', e.first_name, e.last_name) AS employee_name
         FROM erp_payroll p
         JOIN erp_employees e ON e.id = p.employee_id
        WHERE p.id = $1 FOR UPDATE OF p`,
      [payrollId],
    );
    const payroll = result.rows[0];
    if (!payroll) {
      await client.query("ROLLBACK");
      res.status(404).json({ error: "Payroll item not found." });
      return;
    }
    if (payroll.status !== "pending") {
      await client.query("ROLLBACK");
      res.status(409).json({ error: "This payroll item has already been paid." });
      return;
    }
    const amount = Number(payroll.net_amount);
    if (!Number.isFinite(amount) || amount <= 0) {
      await client.query("ROLLBACK");
      res.status(409).json({ error: "The net payroll amount must be positive." });
      return;
    }
    await ensureDefaultAccounts(client);
    const salaryAccount = await accountIdByCode(client, "641");
    const cashAccount = await accountIdByCode(client, "530");
    const journal = await postDoubleEntry(client, {
      entryDate: new Date().toISOString().slice(0, 10),
      description: `Salary payment: ${payroll.employee_name} (${payroll.period})`,
      reference: `PAYROLL-${payrollId}`,
      source: "payroll",
      createdBy: req.user!.id,
      debitAccountId: salaryAccount,
      creditAccountId: cashAccount,
      amount,
    });
    const updated = await client.query(
      `UPDATE erp_payroll
          SET status = 'paid', paid_at = CURRENT_DATE
        WHERE id = $1
        RETURNING *`,
      [payrollId],
    );
    await client.query("COMMIT");
    res.json({
      ...updated.rows[0],
      employeeName: payroll.employee_name,
      journalEntryId: Number(journal.id),
    });
  } catch (error) {
    await client.query("ROLLBACK").catch(() => undefined);
    req.log.error({ err: error, payrollId }, "Payroll payment failed");
    res.status(500).json({ error: "Could not post this payroll payment." });
  } finally {
    client.release();
  }
});

export default router;
