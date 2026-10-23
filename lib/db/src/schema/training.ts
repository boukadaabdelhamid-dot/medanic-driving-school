import { createInsertSchema } from "drizzle-zod";
import {
  date,
  integer,
  numeric,
  pgTable,
  serial,
  text,
  time,
} from "drizzle-orm/pg-core";
import { z } from "zod/v4";
import { candidatesTable, instructorsTable, vehiclesTable } from "./core";

export const trainingStagesTable = pgTable("training_stages", {
  id: serial("id").primaryKey(),
  candidateId: integer("candidate_id")
    .notNull()
    .references(() => candidatesTable.id),
  stageType: text("stage_type").notNull(),
  status: text("status").notNull().default("لم يبدأ"),
  startDate: date("start_date", { mode: "string" }),
  endDate: date("end_date", { mode: "string" }),
  score: numeric("score", { precision: 8, scale: 2, mode: "number" })
    .notNull()
    .default(0),
  notes: text("notes").notNull().default(""),
});

export const insertTrainingStageSchema = createInsertSchema(
  trainingStagesTable,
).omit({ id: true });
export type InsertTrainingStage = z.infer<typeof insertTrainingStageSchema>;
export type TrainingStage = typeof trainingStagesTable.$inferSelect;

export const sessionsTable = pgTable("sessions", {
  id: serial("id").primaryKey(),
  candidateId: integer("candidate_id")
    .notNull()
    .references(() => candidatesTable.id),
  instructorId: integer("instructor_id").references(() => instructorsTable.id),
  vehicleId: integer("vehicle_id").references(() => vehiclesTable.id),
  sessionDate: date("session_date", { mode: "string" }).notNull(),
  sessionTime: time("session_time").notNull(),
  duration: numeric("duration", { precision: 6, scale: 2, mode: "number" })
    .notNull()
    .default(1),
  sessionType: text("session_type").notNull().default(""),
  notes: text("notes").notNull().default(""),
});

export const insertSessionSchema = createInsertSchema(sessionsTable).omit({
  id: true,
});
export type InsertSession = z.infer<typeof insertSessionSchema>;
export type Session = typeof sessionsTable.$inferSelect;

export const paymentsTable = pgTable("payments", {
  id: serial("id").primaryKey(),
  candidateId: integer("candidate_id")
    .notNull()
    .references(() => candidatesTable.id),
  date: date("date", { mode: "string" }).notNull().defaultNow(),
  amount: numeric("amount", { precision: 12, scale: 2, mode: "number" })
    .notNull()
    .default(0),
  paymentMethod: text("payment_method").notNull().default(""),
  notes: text("notes").notNull().default(""),
});

export const insertPaymentSchema = createInsertSchema(paymentsTable).omit({
  id: true,
});
export type InsertPayment = z.infer<typeof insertPaymentSchema>;
export type Payment = typeof paymentsTable.$inferSelect;

export const expensesTable = pgTable("expenses", {
  id: serial("id").primaryKey(),
  expenseType: text("expense_type").notNull().default(""),
  amount: numeric("amount", { precision: 12, scale: 2, mode: "number" })
    .notNull()
    .default(0),
  date: date("date", { mode: "string" }).notNull().defaultNow(),
  notes: text("notes").notNull().default(""),
});

export const insertExpenseSchema = createInsertSchema(expensesTable).omit({
  id: true,
});
export type InsertExpense = z.infer<typeof insertExpenseSchema>;
export type Expense = typeof expensesTable.$inferSelect;

export const examResultsTable = pgTable("exam_results", {
  id: serial("id").primaryKey(),
  candidateId: integer("candidate_id")
    .notNull()
    .references(() => candidatesTable.id),
  examType: text("exam_type").notNull(),
  examDate: date("exam_date", { mode: "string" }).notNull().defaultNow(),
  result: text("result").notNull(),
  score: numeric("score", { precision: 8, scale: 2, mode: "number" })
    .notNull()
    .default(0),
  notes: text("notes").notNull().default(""),
});

export const insertExamResultSchema = createInsertSchema(examResultsTable).omit({
  id: true,
});
export type InsertExamResult = z.infer<typeof insertExamResultSchema>;
export type ExamResult = typeof examResultsTable.$inferSelect;

export const examAttemptsTable = pgTable("exam_attempts", {
  id: serial("id").primaryKey(),
  candidateId: integer("candidate_id")
    .notNull()
    .references(() => candidatesTable.id),
  stageType: text("stage_type").notNull(),
  examDate: date("exam_date", { mode: "string" }).notNull().defaultNow(),
  score: numeric("score", { precision: 8, scale: 2, mode: "number" })
    .notNull()
    .default(0),
  result: text("result").notNull().default("راسب"),
  notes: text("notes").notNull().default(""),
});

export const insertExamAttemptSchema = createInsertSchema(examAttemptsTable).omit(
  { id: true },
);
export type InsertExamAttempt = z.infer<typeof insertExamAttemptSchema>;
export type ExamAttempt = typeof examAttemptsTable.$inferSelect;
