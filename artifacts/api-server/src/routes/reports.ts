import { Router, type IRouter } from "express";
import { GetReportResponse } from "@workspace/api-zod";
import { pool } from "@workspace/db";
import { requireAuth, requirePermission } from "../lib/auth";

const router: IRouter = Router();
router.use(requireAuth);

function dateFilters(from: unknown, to: unknown, column: string) {
  const clauses: string[] = [];
  const values: string[] = [];
  if (typeof from === "string" && from) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(from)) throw new Error("Invalid start date.");
    values.push(from);
    clauses.push(`${column} >= $${values.length}`);
  }
  if (typeof to === "string" && to) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(to)) throw new Error("Invalid end date.");
    values.push(to);
    clauses.push(`${column} <= $${values.length}`);
  }
  return { where: clauses.length ? `WHERE ${clauses.join(" AND ")}` : "", values };
}

router.get(
  "/reports/:report",
  requirePermission("view_reports"),
  async (req, res) => {
    const reportValue = req.params.report;
    const report = Array.isArray(reportValue) ? reportValue[0] ?? "" : reportValue;
    const allowed = new Set([
      "payments",
      "expenses",
      "candidates",
      "instructors",
      "exams",
      "payroll",
      "journal",
    ]);
    if (!allowed.has(report)) {
      res.status(404).json({ error: "Unknown report." });
      return;
    }
    if (
      (report === "payroll" || report === "journal") &&
      req.user?.role !== "admin"
    ) {
      res.status(403).json({ error: "Administrator access is required for this report." });
      return;
    }

    try {
      let items: Record<string, unknown>[] = [];
      let totals: Record<string, number> = {};

      if (report === "payments") {
        const filter = dateFilters(req.query.from, req.query.to, "p.date");
        const [rows, sum] = await Promise.all([
          pool.query(
            `SELECT p.*, concat_ws(' ', c.first_name, c.last_name) AS candidate_name
               FROM payments p JOIN candidates c ON c.id = p.candidate_id
               ${filter.where}
              ORDER BY p.date DESC, p.id DESC LIMIT 500`,
            filter.values,
          ),
          pool.query(
            `SELECT COALESCE(SUM(amount), 0)::float8 AS total,
                    COUNT(*)::int AS count
               FROM payments p ${filter.where}`,
            filter.values,
          ),
        ]);
        items = rows.rows;
        totals = {
          amount: Number(sum.rows[0]?.total ?? 0),
          count: Number(sum.rows[0]?.count ?? 0),
        };
      } else if (report === "expenses") {
        const filter = dateFilters(req.query.from, req.query.to, "date");
        const [rows, sum] = await Promise.all([
          pool.query(
            `SELECT * FROM expenses ${filter.where}
              ORDER BY date DESC, id DESC LIMIT 500`,
            filter.values,
          ),
          pool.query(
            `SELECT COALESCE(SUM(amount), 0)::float8 AS total, COUNT(*)::int AS count
               FROM expenses ${filter.where}`,
            filter.values,
          ),
        ]);
        items = rows.rows;
        totals = {
          amount: Number(sum.rows[0]?.total ?? 0),
          count: Number(sum.rows[0]?.count ?? 0),
        };
      } else if (report === "candidates") {
        const filter = dateFilters(req.query.from, req.query.to, "registration_date");
        const [rows, sum] = await Promise.all([
          pool.query(
            `SELECT id, first_name, last_name, license_type, registration_date
               FROM candidates ${filter.where}
              ORDER BY registration_date DESC, id DESC LIMIT 500`,
            filter.values,
          ),
          pool.query(
            `SELECT COUNT(*)::int AS count FROM candidates ${filter.where}`,
            filter.values,
          ),
        ]);
        items = rows.rows;
        totals = { count: Number(sum.rows[0]?.count ?? 0) };
      } else if (report === "instructors") {
        const [rows, sum] = await Promise.all([
          pool.query(
            `SELECT i.id, i.first_name, i.last_name, i.phone, i.salary,
                    COUNT(c.id)::int AS candidate_count
               FROM instructors i
               LEFT JOIN candidates c ON c.instructor_id = i.id
              GROUP BY i.id ORDER BY i.last_name, i.first_name LIMIT 500`,
          ),
          pool.query("SELECT COUNT(*)::int AS count FROM instructors"),
        ]);
        items = rows.rows;
        totals = { count: Number(sum.rows[0]?.count ?? 0) };
      } else if (report === "exams") {
        const filter = dateFilters(req.query.from, req.query.to, "exam_date");
        const result = await pool.query(
          `SELECT MIN(id)::int AS id, exam_type,
                  COUNT(*)::int AS total,
                  COUNT(*) FILTER (WHERE result = 'ناجح')::int AS passed,
                  COUNT(*) FILTER (WHERE result <> 'ناجح')::int AS failed
             FROM exam_results ${filter.where}
            GROUP BY exam_type ORDER BY exam_type`,
          filter.values,
        );
        items = result.rows;
        totals = {
          total: result.rows.reduce((sum, row) => sum + Number(row.total), 0),
          passed: result.rows.reduce((sum, row) => sum + Number(row.passed), 0),
          failed: result.rows.reduce((sum, row) => sum + Number(row.failed), 0),
        };
      } else if (report === "payroll") {
        const filter = dateFilters(req.query.from, req.query.to, "p.paid_at");
        const [rows, sum] = await Promise.all([
          pool.query(
            `SELECT p.*, concat_ws(' ', e.first_name, e.last_name) AS employee_name
               FROM erp_payroll p JOIN erp_employees e ON e.id = p.employee_id
               ${filter.where}
              ORDER BY p.period DESC, p.id DESC LIMIT 500`,
            filter.values,
          ),
          pool.query(
            `SELECT COALESCE(SUM(net_amount), 0)::float8 AS total,
                    COUNT(*)::int AS count
               FROM erp_payroll p ${filter.where}`,
            filter.values,
          ),
        ]);
        items = rows.rows;
        totals = {
          netAmount: Number(sum.rows[0]?.total ?? 0),
          count: Number(sum.rows[0]?.count ?? 0),
        };
      } else {
        const filter = dateFilters(req.query.from, req.query.to, "entry.entry_date");
        const result = await pool.query(
          `SELECT entry.id, entry.entry_date, entry.description, entry.reference,
                  COALESCE(SUM(line.debit), 0)::float8 AS debit,
                  COALESCE(SUM(line.credit), 0)::float8 AS credit
             FROM erp_journal_entries entry
             LEFT JOIN erp_journal_lines line ON line.journal_entry_id = entry.id
             ${filter.where}
            GROUP BY entry.id
            ORDER BY entry.entry_date DESC, entry.id DESC LIMIT 500`,
          filter.values,
        );
        items = result.rows;
        totals = {
          debit: result.rows.reduce((sum, row) => sum + Number(row.debit), 0),
          credit: result.rows.reduce((sum, row) => sum + Number(row.credit), 0),
          count: result.rows.length,
        };
      }

      const response = {
        items: items.map((row) => {
          const normalized: Record<string, unknown> = {};
          for (const [key, value] of Object.entries(row)) {
            normalized[key.replace(/_([a-z])/g, (_match, letter: string) =>
              letter.toUpperCase(),
            )] = value;
          }
          return normalized;
        }),
        totals,
      };
      res.json(GetReportResponse.parse(response));
    } catch (error) {
      if (error instanceof Error && error.message.startsWith("Invalid ")) {
        res.status(400).json({ error: error.message });
        return;
      }
      req.log.error({ err: error, report }, "Could not build report");
      res.status(500).json({ error: "Could not build this report." });
    }
  },
);

export default router;
