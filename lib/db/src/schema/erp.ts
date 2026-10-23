import { createInsertSchema } from "drizzle-zod";
import {
  date,
  integer,
  jsonb,
  numeric,
  pgTable,
  serial,
  text,
} from "drizzle-orm/pg-core";
import { z } from "zod/v4";
import { usersTable } from "./core";

export const erpAccountsTable = pgTable("erp_accounts", {
  id: serial("id").primaryKey(),
  code: text("code").notNull().unique(),
  name: text("name").notNull(),
  category: text("category").notNull(),
  normalSide: text("normal_side").notNull().default("debit"),
  isActive: integer("is_active").notNull().default(1),
});

export const insertErpAccountSchema = createInsertSchema(erpAccountsTable).omit({
  id: true,
});
export type InsertErpAccount = z.infer<typeof insertErpAccountSchema>;
export type ErpAccount = typeof erpAccountsTable.$inferSelect;

export const erpEmployeesTable = pgTable("erp_employees", {
  id: serial("id").primaryKey(),
  firstName: text("first_name").notNull(),
  lastName: text("last_name").notNull(),
  jobTitle: text("job_title").notNull().default(""),
  phone: text("phone").notNull().default(""),
  email: text("email").notNull().default(""),
  contractType: text("contract_type").notNull().default(""),
  startDate: date("start_date", { mode: "string" }),
  baseSalary: numeric("base_salary", {
    precision: 12,
    scale: 2,
    mode: "number",
  })
    .notNull()
    .default(0),
  status: text("status").notNull().default("active"),
  notes: text("notes").notNull().default(""),
});

export const insertErpEmployeeSchema = createInsertSchema(
  erpEmployeesTable,
).omit({ id: true });
export type InsertErpEmployee = z.infer<typeof insertErpEmployeeSchema>;
export type ErpEmployee = typeof erpEmployeesTable.$inferSelect;

export const erpJournalEntriesTable = pgTable("erp_journal_entries", {
  id: serial("id").primaryKey(),
  entryDate: date("entry_date", { mode: "string" }).notNull().defaultNow(),
  description: text("description").notNull(),
  reference: text("reference").notNull().default(""),
  source: text("source").notNull().default("manual"),
  createdBy: integer("created_by").references(() => usersTable.id),
  reversalOfId: integer("reversal_of_id"),
  createdAt: date("created_at", { mode: "string" }).notNull().defaultNow(),
});

export const erpJournalLinesTable = pgTable("erp_journal_lines", {
  id: serial("id").primaryKey(),
  journalEntryId: integer("journal_entry_id")
    .notNull()
    .references(() => erpJournalEntriesTable.id),
  accountId: integer("account_id")
    .notNull()
    .references(() => erpAccountsTable.id),
  debit: numeric("debit", { precision: 12, scale: 2, mode: "number" })
    .notNull()
    .default(0),
  credit: numeric("credit", { precision: 12, scale: 2, mode: "number" })
    .notNull()
    .default(0),
});

export const insertErpJournalEntrySchema = createInsertSchema(
  erpJournalEntriesTable,
).omit({ id: true, createdAt: true });
export type InsertErpJournalEntry = z.infer<typeof insertErpJournalEntrySchema>;
export type ErpJournalEntry = typeof erpJournalEntriesTable.$inferSelect;

export const erpPayrollTable = pgTable("erp_payroll", {
  id: serial("id").primaryKey(),
  employeeId: integer("employee_id")
    .notNull()
    .references(() => erpEmployeesTable.id),
  period: text("period").notNull(),
  grossAmount: numeric("gross_amount", {
    precision: 12,
    scale: 2,
    mode: "number",
  }).notNull(),
  deductions: numeric("deductions", {
    precision: 12,
    scale: 2,
    mode: "number",
  })
    .notNull()
    .default(0),
  netAmount: numeric("net_amount", {
    precision: 12,
    scale: 2,
    mode: "number",
  }).notNull(),
  status: text("status").notNull().default("pending"),
  paidAt: date("paid_at", { mode: "string" }),
  notes: text("notes").notNull().default(""),
});

export const insertErpPayrollSchema = createInsertSchema(erpPayrollTable).omit({
  id: true,
});
export type InsertErpPayroll = z.infer<typeof insertErpPayrollSchema>;
export type ErpPayroll = typeof erpPayrollTable.$inferSelect;

export const erpSettingsTable = pgTable("erp_settings", {
  key: text("key").primaryKey(),
  value: jsonb("value").$type<unknown>().notNull(),
});
