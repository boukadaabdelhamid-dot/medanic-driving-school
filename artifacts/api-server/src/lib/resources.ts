import { hashPassword } from "./auth";
import {
  getResourceDefinition,
  isResourceName,
  toSnakeCase,
  type ResourceField,
  type ResourceName,
} from "./resource-registry";

const safeDate = /^\d{4}-\d{2}-\d{2}$/;
const graduatedCandidateSql = `(
  (c.license_type = 'A1' AND EXISTS (
    SELECT 1 FROM training_stages ts
     WHERE ts.candidate_id = c.id
       AND ts.stage_type = 'code'
       AND ts.status = 'ناجح'
  ))
  OR
  (c.license_type <> 'A1' AND (
    SELECT COUNT(DISTINCT ts.stage_type)
      FROM training_stages ts
     WHERE ts.candidate_id = c.id
       AND ts.status = 'ناجح'
       AND ts.stage_type IN ('code', 'creneau', 'circuit')
  ) >= 3)
)`;

export type ApiRow = Record<string, unknown> & { id: number };
export type SqlExecutor = {
  query: (text: string, values?: unknown[]) => Promise<{ rows: any[]; rowCount: number | null }>;
};

function snakeToCamel(value: string) {
  return value.replace(/_([a-z])/g, (_match, letter: string) =>
    letter.toUpperCase(),
  );
}

function normalizeValue(key: string, value: unknown): unknown {
  if (value === null || value === undefined) return value ?? null;
  if (
    [
      "amount",
      "total_amount",
      "salary",
      "experience_years",
      "score",
      "duration",
      "gross_amount",
      "deductions",
      "net_amount",
      "debit",
      "credit",
    ].includes(key)
  ) {
    const number = Number(value);
    return Number.isFinite(number) ? number : value;
  }
  if (["is_born_abroad", "is_active"].includes(key)) {
    return value === true || value === 1 || value === "1";
  }
  return value;
}

export function normalizeRow(row: Record<string, unknown>): ApiRow {
  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(row)) {
    if (key === "password_hash" || key === "passwordHash") continue;
    result[snakeToCamel(key)] = normalizeValue(key, value);
  }
  return result as ApiRow;
}

function allowedColumns(resource: ResourceName) {
  return new Set(
    getResourceDefinition(resource).fields
      .filter((item) => !item.readOnly)
      .map((item) => item.name),
  );
}

export function validateResourceInput(
  resource: ResourceName,
  input: unknown,
  isCreate: boolean,
): Record<string, unknown> {
  if (!input || typeof input !== "object" || Array.isArray(input)) {
    throw new Error("The record data must be an object.");
  }
  const record = input as Record<string, unknown>;
  const def = getResourceDefinition(resource);
  const allowed = allowedColumns(resource);
  const unknown = Object.keys(record).filter((key) => !allowed.has(key));
  if (unknown.length) throw new Error("The record contains unsupported fields.");

  const output: Record<string, unknown> = {};
  for (const item of def.fields) {
    if (item.readOnly || !Object.hasOwn(record, item.name)) continue;
    let value = record[item.name];

    if (item.type === "permissions") {
      if (Array.isArray(value)) {
        const known = item.options ?? [];
        const selected = value.map(String).filter((key) => known.includes(key));
        output[item.name] = Object.fromEntries(selected.map((key) => [key, true]));
        continue;
      }
      if (value && typeof value === "object" && !Array.isArray(value)) {
        const known = item.options ?? [];
        output[item.name] = Object.fromEntries(
          Object.entries(value as Record<string, unknown>)
            .filter(([key, enabled]) => known.includes(key) && enabled === true)
            .map(([key]) => [key, true]),
        );
        continue;
      }
      if (value === "" || value === null || value === undefined) {
        output[item.name] = {};
        continue;
      }
      throw new Error("Permissions must be a list of known permissions.");
    }

    if (item.type === "password") {
      if (typeof value !== "string") throw new Error("Invalid password.");
      if (!value && !isCreate) continue;
      if (value.length < 12) throw new Error("Passwords must be at least 12 characters.");
      output[item.name] = hashPassword(value);
      continue;
    }

    if (value === "" || value === undefined) {
      if (item.required) {
        throw new Error(`${item.name} is required.`);
      }
      if (item.type === "number") {
        value = ["instructorId", "vehicleId", "candidateId", "employeeId"].includes(
          item.name,
        )
          ? null
          : 0;
      } else if (item.type === "boolean") {
        value = false;
      } else if (item.type === "date") {
        value = null;
      } else if (item.type === "select") {
        value = "";
      } else {
        value = "";
      }
    }
    if (value === null) {
      output[item.name] = null;
      continue;
    }

    if (item.type === "number") {
      const number = typeof value === "number" ? value : Number(value);
      if (!Number.isFinite(number)) throw new Error(`${item.name} must be a number.`);
      if (number < 0) throw new Error(`${item.name} cannot be negative.`);
      output[item.name] = number;
      continue;
    }
    if (item.type === "boolean") {
      if (typeof value === "boolean") output[item.name] = value;
      else if (value === 1 || value === "1" || value === "true") output[item.name] = true;
      else if (value === 0 || value === "0" || value === "false") output[item.name] = false;
      else throw new Error(`${item.name} must be true or false.`);
      continue;
    }
    if (item.type === "date") {
      const date = String(value);
      if (!safeDate.test(date) || Number.isNaN(Date.parse(`${date}T00:00:00Z`))) {
        throw new Error(`${item.name} must be a valid date.`);
      }
      output[item.name] = date;
      continue;
    }
    if (item.type === "email") {
      if (typeof value !== "string") throw new Error(`${item.name} must be an email.`);
      const email = value.trim().toLowerCase();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        throw new Error(`${item.name} must be a valid email address.`);
      }
      output[item.name] = email;
      continue;
    }
    if (item.type === "select") {
      const optionValues = (item.options ?? []).map((option) => option);
      if (optionValues.length && !optionValues.includes(String(value))) {
        throw new Error(`${item.name} has an unsupported value.`);
      }
    }
    if (typeof value === "string" && value.length > 10000) {
      throw new Error(`${item.name} is too long.`);
    }
    output[item.name] = value;
  }

  // Candidate registration dates are generated by PostgreSQL when the form
  // leaves this optional date blank. Passing null explicitly bypasses the DB default.
  if (resource === "candidates" && isCreate && !output.registrationDate) {
    delete output.registrationDate;
  }

  if (resource === "users" && isCreate && !output.password) {
    throw new Error("A password is required for a new user.");
  }
  if (
    resource === "journalEntries" &&
    (typeof output.amount !== "number" || output.amount <= 0)
  ) {
    throw new Error("Journal entry amounts must be greater than zero.");
  }
  if (resource === "payroll") {
    const hasGross = Object.hasOwn(output, "grossAmount");
    const hasDeductions = Object.hasOwn(output, "deductions");
    if (isCreate || hasGross || hasDeductions) {
      if (!isCreate && hasGross !== hasDeductions) {
        throw new Error("Update gross salary and deductions together.");
      }
      const gross = Number(output.grossAmount);
      const deductions = Number(output.deductions ?? 0);
      if (
        !Number.isFinite(gross) ||
        gross < 0 ||
        !Number.isFinite(deductions) ||
        deductions < 0 ||
        deductions > gross
      ) {
        throw new Error("Deductions must be between zero and gross salary.");
      }
      output.deductions = deductions;
      output.netAmount = Math.round((gross - deductions + Number.EPSILON) * 100) / 100;
    }
    if (isCreate) {
      output.status = "pending";
      output.paidAt = null;
    }
  }
  return output;
}

function inputColumn(resource: ResourceName, field: string) {
  if (resource === "users" && field === "password") return "password_hash";
  return toSnakeCase(field);
}

export function buildWhereClause(
  resource: ResourceName,
  input: {
    search?: string;
    candidateId?: number;
    from?: string;
    to?: string;
    period?: string;
  },
  startIndex = 1,
) {
  const def = getResourceDefinition(resource);
  const clauses: string[] = [];
  const values: unknown[] = [];
  const add = (expression: string, value: unknown) => {
    values.push(value);
    clauses.push(expression.replace("?", `$${startIndex + values.length - 1}`));
  };

  if (input.search?.trim()) {
    const columns = def.searchable.map(toSnakeCase);
    if (columns.length) {
      const placeholder = `$${startIndex + values.length}`;
      values.push(`%${input.search.trim()}%`);
      clauses.push(
        `(${columns.map((column) => `${column}::text ILIKE ${placeholder}`).join(" OR ")})`,
      );
    }
  }

  if (
    input.candidateId &&
    ["trainingStages", "sessions", "payments", "examResults", "examAttempts"].includes(
      resource,
    )
  ) {
    add("candidate_id = ?", input.candidateId);
  }

  const dateColumn: Partial<Record<ResourceName, string>> = {
    candidates: "registration_date",
    instructors: "contract_start_date",
    trainingStages: "start_date",
    sessions: "session_date",
    payments: "date",
    expenses: "date",
    examResults: "exam_date",
    examAttempts: "exam_date",
    journalEntries: "entry_date",
    payroll: "period",
  };
  const column = dateColumn[resource];
  if (column && input.from) add(`${column} >= ?`, input.from);
  if (column && input.to) add(`${column} <= ?`, input.to);
  if (resource === "payroll" && input.period) {
    add("period = ?", input.period);
  }

  if (resource === "graduates") {
    const graduateFilters = clauses.map((clause) =>
      clause.replace(/\b(first_name|last_name|phone|national_id)::text/g, "c.$1::text"),
    );
    return {
      where: graduateFilters.length
        ? `WHERE ${graduatedCandidateSql} AND ${graduateFilters.join(" AND ")}`
        : `WHERE ${graduatedCandidateSql}`,
      values,
    };
  }

  return { where: clauses.length ? `WHERE ${clauses.join(" AND ")}` : "", values };
}

export function parseResourceName(value: string): ResourceName | null {
  return isResourceName(value) ? value : null;
}

export function tableName(resource: ResourceName) {
  return getResourceDefinition(resource).table;
}

export function resourceOrder(resource: ResourceName) {
  return getResourceDefinition(resource).orderBy;
}

export function resourceFields(resource: ResourceName, language: string) {
  const locale = language === "fr" ? "fr" : "ar";
  const specs = getResourceDefinition(resource).fields;
  return specs.map((spec) => {
    const { ar, fr, options, ...rest } = spec as typeof spec & {
      ar?: string;
      fr?: string;
    };
    const localized = getResourceDefinition(resource).fields.find(
      (item) => item.name === spec.name,
    )!;
    const optionList = (options ?? []).map((value) => ({
      value,
      label: optionLabel(value, locale),
    }));
    return {
      ...rest,
      name: spec.name,
      label: locale === "fr" ? localized.fr : localized.ar,
      ...(optionList.length ? { options: optionList } : {}),
    };
  }) as ResourceField[];
}

function optionLabel(value: string, locale: "ar" | "fr") {
  const labels: Record<string, { ar: string; fr: string }> = {
    ذكر: { ar: "ذكر", fr: "Homme" },
    "أنثى": { ar: "أنثى", fr: "Femme" },
    "لم يبدأ": { ar: "لم يبدأ", fr: "Non commencé" },
    "قيد التكوين": { ar: "قيد التكوين", fr: "En formation" },
    ناجح: { ar: "ناجح", fr: "Réussi" },
    راسب: { ar: "راسب", fr: "Échoué" },
    سيارة: { ar: "سيارة", fr: "Voiture" },
    "دراجة نارية": { ar: "دراجة نارية", fr: "Moto" },
    نقدي: { ar: "نقدي", fr: "Espèces" },
    تحويل: { ar: "تحويل", fr: "Virement" },
    بطاقة: { ar: "بطاقة", fr: "Carte" },
    شيك: { ar: "شيك", fr: "Chèque" },
    asset: { ar: "أصول", fr: "Actif" },
    liability: { ar: "خصوم", fr: "Passif" },
    equity: { ar: "حقوق الملكية", fr: "Capitaux propres" },
    revenue: { ar: "إيرادات", fr: "Produits" },
    expense: { ar: "مصروفات", fr: "Charges" },
    debit: { ar: "مدين", fr: "Débit" },
    credit: { ar: "دائن", fr: "Crédit" },
    active: { ar: "نشط", fr: "Actif" },
    inactive: { ar: "غير نشط", fr: "Inactif" },
    pending: { ar: "معلق", fr: "En attente" },
    paid: { ar: "مدفوع", fr: "Payé" },
    admin: { ar: "مدير", fr: "Administrateur" },
    trainer: { ar: "ممرّن", fr: "Moniteur" },
    view_dashboard: { ar: "عرض لوحة القيادة", fr: "Voir le tableau de bord" },
    view_candidates: { ar: "عرض المترشحين", fr: "Voir les candidats" },
    edit_candidates: { ar: "إدارة المترشحين", fr: "Gérer les candidats" },
    view_payments: { ar: "عرض المدفوعات", fr: "Voir les paiements" },
    add_payments: { ar: "إضافة المدفوعات", fr: "Ajouter des paiements" },
    view_expenses: { ar: "عرض المصاريف", fr: "Voir les dépenses" },
    view_training: { ar: "عرض التكوين", fr: "Voir la formation" },
    view_schedule: { ar: "عرض الجدول", fr: "Voir le planning" },
    print_docs: { ar: "طباعة الوثائق", fr: "Imprimer les documents" },
    view_reports: { ar: "عرض التقارير", fr: "Voir les rapports" },
    manage_school_info: { ar: "إدارة معلومات المدرسة", fr: "Gérer l'école" },
  };
  return labels[value]?.[locale] ?? value;
}

export async function hydrateFieldOptions(
  executor: SqlExecutor,
  resource: ResourceName,
  language: string,
  fields = resourceFields(resource, language),
) {
  const locale = language === "fr" ? "fr" : "ar";
  const referenceFields: Record<string, { sql: string }> = {
    candidateId: {
      sql: `SELECT id, concat_ws(' ', first_name, last_name) AS name FROM candidates ORDER BY last_name, first_name LIMIT 1000`,
    },
    instructorId: {
      sql: `SELECT id, concat_ws(' ', first_name, last_name) AS name FROM instructors ORDER BY last_name, first_name LIMIT 1000`,
    },
    vehicleId: {
      sql: `SELECT id, concat_ws(' ', model, plate_number) AS name FROM vehicles ORDER BY model LIMIT 1000`,
    },
    employeeId: {
      sql: `SELECT id, concat_ws(' ', first_name, last_name) AS name FROM erp_employees ORDER BY last_name, first_name LIMIT 1000`,
    },
    debitAccountId: {
      sql: `SELECT id, concat_ws(' — ', code, name) AS name FROM erp_accounts WHERE is_active = 1 ORDER BY code LIMIT 1000`,
    },
    creditAccountId: {
      sql: `SELECT id, concat_ws(' — ', code, name) AS name FROM erp_accounts WHERE is_active = 1 ORDER BY code LIMIT 1000`,
    },
  };
  const result: ResourceField[] = [];
  for (const item of fields) {
    const reference = referenceFields[item.name];
    if (!reference) {
      result.push(item);
      continue;
    }
    const options = await executor.query(reference.sql);
    result.push({
      ...item,
      type: "select",
      options: options.rows.map((row) => ({
        value: String(row.id),
        label: locale === "fr" ? String(row.name) : String(row.name),
      })),
    });
  }
  return result;
}

export function sqlColumns(resource: ResourceName, input: Record<string, unknown>) {
  return Object.entries(input)
    .filter(([key, value]) => value !== undefined && key !== "id")
    .map(([key, value]) => ({
      column: inputColumn(resource, key),
      value,
    }));
}

export function isReadOnly(resource: ResourceName) {
  return getResourceDefinition(resource).readOnly === true;
}

export function isAdminOnly(resource: ResourceName) {
  return getResourceDefinition(resource).adminOnly === true;
}

export function requiredPermission(resource: ResourceName) {
  return getResourceDefinition(resource).permission;
}

export function isDerivedGraduates(resource: ResourceName) {
  return getResourceDefinition(resource).derivedGraduates === true;
}
