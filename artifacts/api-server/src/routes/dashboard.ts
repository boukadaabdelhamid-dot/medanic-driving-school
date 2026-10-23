import { Router, type IRouter } from "express";
import { GetDashboardResponse } from "@workspace/api-zod";
import { pool } from "@workspace/db";
import { requireAuth, requirePermission } from "../lib/auth";

const router: IRouter = Router();
router.use(requireAuth);

router.get(
  "/dashboard",
  requirePermission("view_dashboard"),
  async (req, res) => {
    try {
      const [
        candidates,
        instructors,
        sessions,
        payments,
        expenses,
        activity,
      ] = await Promise.all([
        pool.query("SELECT COUNT(*)::int AS count FROM candidates"),
        pool.query("SELECT COUNT(*)::int AS count FROM instructors"),
        pool.query(
          `SELECT COUNT(*)::int AS count FROM sessions
            WHERE session_date = (CURRENT_TIMESTAMP AT TIME ZONE 'Africa/Algiers')::date`,
        ),
        pool.query(
          `SELECT COALESCE(SUM(amount), 0)::float8 AS total
             FROM payments
            WHERE date >= date_trunc('month', CURRENT_TIMESTAMP AT TIME ZONE 'Africa/Algiers')::date`,
        ),
        pool.query(
          `SELECT COALESCE(SUM(amount), 0)::float8 AS total
             FROM expenses
            WHERE date >= date_trunc('month', CURRENT_TIMESTAMP AT TIME ZONE 'Africa/Algiers')::date`,
        ),
        pool.query(
          `SELECT ROW_NUMBER() OVER (ORDER BY activity_date DESC, source_order)::int AS id,
                  activity_date AS "createdAt", activity_type AS "recordType",
                  description, amount
             FROM (
               SELECT registration_date::timestamp AS activity_date,
                      1 AS source_order, 'registration' AS activity_type,
                      concat_ws(' ', first_name, last_name) AS description,
                      NULL::numeric AS amount
                 FROM candidates
               UNION ALL
               SELECT date::timestamp, 2, 'payment',
                      concat('Payment recorded for candidate #', candidate_id),
                      amount
                 FROM payments
               UNION ALL
               SELECT date::timestamp, 3, 'expense', expense_type, amount
                 FROM expenses
               UNION ALL
               SELECT session_date::timestamp, 4, 'session',
                      concat('Training session for candidate #', candidate_id),
                      NULL::numeric
                 FROM sessions
             ) recent
            ORDER BY activity_date DESC, source_order
            LIMIT 8`,
        ),
      ]);
      const summary = {
        candidateCount: Number(candidates.rows[0]?.count ?? 0),
        instructorCount: Number(instructors.rows[0]?.count ?? 0),
        todaySessions: Number(sessions.rows[0]?.count ?? 0),
        paidThisMonth: Number(payments.rows[0]?.total ?? 0),
        expensesThisMonth: Number(expenses.rows[0]?.total ?? 0),
        recentActivity: activity.rows.map((row) => ({
          ...row,
          amount: row.amount === null ? null : Number(row.amount),
        })),
      };
      res.json(GetDashboardResponse.parse(summary));
    } catch (error) {
      req.log.error({ err: error }, "Could not load dashboard summary");
      res.status(500).json({ error: "Could not load the dashboard." });
    }
  },
);

export default router;
