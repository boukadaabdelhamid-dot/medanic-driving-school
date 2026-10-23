import { spawn } from "node:child_process";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { Router, type IRouter } from "express";
import {
  GenerateDocumentBody,
  GetDocumentCatalogResponse,
} from "@workspace/api-zod";
import { pool } from "@workspace/db";
import { requireAuth, requirePermission } from "../lib/auth";

const router: IRouter = Router();
router.use(requireAuth);

type Locale = "ar" | "fr";
type CatalogField = {
  name: string;
  label: string;
  type: "text" | "number" | "date" | "select" | "boolean" | "textarea" | "password" | "permissions";
  required: boolean;
  options?: { value: string; label: string }[];
  multiple?: boolean;
};
type CatalogDocument = {
  id: string;
  label: string;
  scope: "candidate" | "group";
  description: string;
  fields: CatalogField[];
};

const catalog: Record<string, { ar: CatalogDocument; fr: CatalogDocument }> = {
  exam_form: {
    ar: {
      id: "exam_form",
      label: "استمارة الترشح للامتحان",
      description: "استمارة المترشح الرسمية لامتحانات رخصة السياقة.",
      scope: "candidate",
      fields: [],
    },
    fr: {
      id: "exam_form",
      label: "Formulaire d'inscription à l'examen",
      description: "Formulaire officiel du candidat aux examens du permis.",
      scope: "candidate",
      fields: [],
    },
  },
  training_card: {
    ar: {
      id: "training_card",
      label: "بطاقة التكوين",
      description: "بطاقة متابعة تكوين المترشح.",
      scope: "candidate",
      fields: [],
    },
    fr: {
      id: "training_card",
      label: "Carte de formation",
      description: "Carte de suivi de la formation du candidat.",
      scope: "candidate",
      fields: [],
    },
  },
  contract: {
    ar: {
      id: "contract",
      label: "عقد التكوين",
      description: "عقد التكوين الخاص بالمترشح.",
      scope: "candidate",
      fields: [],
    },
    fr: {
      id: "contract",
      label: "Contrat de formation",
      description: "Contrat de formation individuel.",
      scope: "candidate",
      fields: [],
    },
  },
  certificate: {
    ar: {
      id: "certificate",
      label: "شهادة التكوين",
      description: "شهادة إتمام تكوين المترشح.",
      scope: "candidate",
      fields: [],
    },
    fr: {
      id: "certificate",
      label: "Attestation de formation",
      description: "Attestation de fin de formation du candidat.",
      scope: "candidate",
      fields: [],
    },
  },
  payment_receipt: {
    ar: {
      id: "payment_receipt",
      label: "وصل دفع",
      description: "كشف دفعات المترشح والمبلغ المتبقي.",
      scope: "candidate",
      fields: [],
    },
    fr: {
      id: "payment_receipt",
      label: "Reçu et relevé des paiements",
      description: "Paiements du candidat et solde restant.",
      scope: "candidate",
      fields: [],
    },
  },
  dispatch_table: {
    ar: {
      id: "dispatch_table",
      label: "جدول الإرسال",
      description: "قائمة المترشحين الموجهة إلى الجهة الإدارية.",
      scope: "group",
      fields: [
        { name: "dispatchDate", label: "تاريخ الإرسال", type: "date", required: false },
        { name: "recordNumber", label: "رقم المحضر", type: "text", required: false },
        { name: "wilaya", label: "الولاية", type: "text", required: false },
      ],
    },
    fr: {
      id: "dispatch_table",
      label: "Tableau d'envoi",
      description: "Liste des candidats destinée à l'administration.",
      scope: "group",
      fields: [
        { name: "dispatchDate", label: "Date d'envoi", type: "date", required: false },
        { name: "recordNumber", label: "N° du procès-verbal", type: "text", required: false },
        { name: "wilaya", label: "Wilaya", type: "text", required: false },
      ],
    },
  },
  candidates_list: {
    ar: {
      id: "candidates_list",
      label: "قائمة المترشحين",
      description: "قائمة المترشحين المسجلين.",
      scope: "group",
      fields: [],
    },
    fr: {
      id: "candidates_list",
      label: "Liste des candidats",
      description: "Liste des candidats inscrits.",
      scope: "group",
      fields: [],
    },
  },
  instructors_list: {
    ar: {
      id: "instructors_list",
      label: "قائمة الممرنين",
      description: "قائمة طاقم الممرنين.",
      scope: "group",
      fields: [],
    },
    fr: {
      id: "instructors_list",
      label: "Liste des moniteurs",
      description: "Liste de l'équipe de moniteurs.",
      scope: "group",
      fields: [],
    },
  },
  expenses_report: {
    ar: {
      id: "expenses_report",
      label: "تقرير المصاريف",
      description: "تقرير المصاريف خلال فترة زمنية.",
      scope: "group",
      fields: [
        { name: "from", label: "من تاريخ", type: "date", required: false },
        { name: "to", label: "إلى تاريخ", type: "date", required: false },
      ],
    },
    fr: {
      id: "expenses_report",
      label: "Rapport des dépenses",
      description: "Dépenses enregistrées sur une période.",
      scope: "group",
      fields: [
        { name: "from", label: "Du", type: "date", required: false },
        { name: "to", label: "Au", type: "date", required: false },
      ],
    },
  },
  payments_report: {
    ar: {
      id: "payments_report",
      label: "تقرير المدفوعات",
      description: "تقرير دفعات المترشحين خلال فترة زمنية.",
      scope: "group",
      fields: [
        { name: "from", label: "من تاريخ", type: "date", required: false },
        { name: "to", label: "إلى تاريخ", type: "date", required: false },
      ],
    },
    fr: {
      id: "payments_report",
      label: "Rapport des paiements",
      description: "Versements des candidats sur une période.",
      scope: "group",
      fields: [
        { name: "from", label: "Du", type: "date", required: false },
        { name: "to", label: "Au", type: "date", required: false },
      ],
    },
  },
  exam_candidates_list: {
    ar: {
      id: "exam_candidates_list",
      label: "قائمة مترشحي الامتحان",
      description: "قائمة الامتحان الرسمية مع اختيار الصنف والممرّن.",
      scope: "group",
      fields: [
        { name: "examDate", label: "تاريخ الامتحان", type: "date", required: true },
        { name: "examCenter", label: "مركز الامتحان", type: "text", required: false },
        { name: "documentReference", label: "رقم المرجع", type: "text", required: false },
        { name: "trainingCardNumber", label: "رقم بطاقة التكوين", type: "text", required: false },
        { name: "vehicleNumber", label: "نوع ورقم المركبة", type: "text", required: false },
        { name: "instructorName", label: "اسم الممرّن في رأس الوثيقة", type: "text", required: false },
        { name: "wilaya", label: "الولاية", type: "text", required: false },
        {
          name: "stageType",
          label: "مرحلة الامتحان",
          type: "select",
          required: false,
          options: [
            { value: "all", label: "الكل" },
            { value: "code", label: "ق.م" },
            { value: "creneau", label: "المناورات" },
            { value: "circuit", label: "السياقة" },
          ],
        },
        { name: "licenseType", label: "صنف الرخصة", type: "text", required: false },
        { name: "instructorId", label: "الممرّن", type: "number", required: false },
      ],
    },
    fr: {
      id: "exam_candidates_list",
      label: "Liste des candidats à l'examen",
      description: "Liste officielle avec sélection de la catégorie et du moniteur.",
      scope: "group",
      fields: [
        { name: "examDate", label: "Date de l'examen", type: "date", required: true },
        { name: "examCenter", label: "Centre d'examen", type: "text", required: false },
        { name: "documentReference", label: "Référence", type: "text", required: false },
        { name: "trainingCardNumber", label: "N° carte de formation", type: "text", required: false },
        { name: "vehicleNumber", label: "Type et immatriculation", type: "text", required: false },
        { name: "instructorName", label: "Moniteur indiqué dans l'en-tête", type: "text", required: false },
        { name: "wilaya", label: "Wilaya", type: "text", required: false },
        {
          name: "stageType",
          label: "Étape de l'examen",
          type: "select",
          required: false,
          options: [
            { value: "all", label: "Tous" },
            { value: "code", label: "Code" },
            { value: "creneau", label: "Manœuvres" },
            { value: "circuit", label: "Conduite" },
          ],
        },
        { name: "licenseType", label: "Catégorie de permis", type: "text", required: false },
        { name: "instructorId", label: "Moniteur (ID)", type: "number", required: false },
      ],
    },
  },
};

function pythonRoot() {
  if (existsSync(path.join(process.cwd(), "driving_school_single.py"))) {
    return process.cwd();
  }
  return path.resolve(process.cwd(), "../..");
}

function dateParam(value: Date | string | undefined): string | undefined {
  if (value instanceof Date) return value.toISOString().slice(0, 10);
  return value;
}

function runRenderer(scriptPath: string, input: Record<string, unknown>) {
  return new Promise<{ stdout: string; stderr: string }>((resolve, reject) => {
    const child = spawn(
      process.env.PYTHON_BIN || "python3",
      [scriptPath],
      { stdio: ["pipe", "pipe", "pipe"], timeout: 45000 },
    );
    let stdout = "";
    let stderr = "";
    child.stdout.setEncoding("utf8").on("data", (chunk: string) => {
      stdout += chunk;
      if (stdout.length > 20000) child.kill("SIGKILL");
    });
    child.stderr.setEncoding("utf8").on("data", (chunk: string) => {
      stderr += chunk;
      if (stderr.length > 20000) child.kill("SIGKILL");
    });
    child.once("error", reject);
    child.once("close", (code) => {
      if (code !== 0) {
        reject(new Error(stderr || `Document renderer exited with code ${code}.`));
        return;
      }
      resolve({ stdout, stderr });
    });
    child.stdin.end(JSON.stringify(input));
  });
}

async function queryRows(query: string, values: unknown[] = []) {
  const result = await pool.query(query, values);
  if (result.rows.length > 5000) {
    throw new Error("Document data exceeds the safe generation limit.");
  }
  return result.rows;
}

async function collectData(
  type: string,
  candidateId: number | undefined,
  candidateIds: number[],
  from: string | undefined,
  to: string | undefined,
) {
  const schoolRows = await queryRows("SELECT * FROM school_info WHERE id = 1");
  let candidates: Record<string, unknown>[] = [];
  if (candidateId) {
    candidates = await queryRows("SELECT * FROM candidates WHERE id = $1", [candidateId]);
  } else if (candidateIds.length) {
    candidates = await queryRows(
      "SELECT * FROM candidates WHERE id = ANY($1::integer[]) ORDER BY last_name, first_name",
      [candidateIds],
    );
  } else if (
    ["dispatch_table", "candidates_list", "exam_candidates_list"].includes(type)
  ) {
    candidates = await queryRows(
      "SELECT * FROM candidates ORDER BY last_name, first_name LIMIT 5000",
    );
  }
  const ids = candidates.map((row) => Number(row.id));
  const wantsInstructors = [
    "instructors_list",
    "exam_candidates_list",
    "candidates_list",
  ].includes(type);
  const instructors = wantsInstructors
    ? await queryRows("SELECT * FROM instructors ORDER BY last_name, first_name LIMIT 5000")
    : ids.length
      ? await queryRows(
          "SELECT * FROM instructors WHERE id = ANY($1::integer[])",
          [[...new Set(candidates.map((row) => Number(row.instructor_id)).filter(Boolean))]],
        )
      : [];
  const wantsVehicles = type === "exam_candidates_list";
  const vehicles = wantsVehicles
    ? await queryRows("SELECT * FROM vehicles ORDER BY model LIMIT 5000")
    : [];

  const stages =
    ids.length && ["training_card", "certificate", "exam_candidates_list"].includes(type)
      ? await queryRows(
          "SELECT * FROM training_stages WHERE candidate_id = ANY($1::integer[]) ORDER BY id",
          [ids],
        )
      : [];
  const sessions =
    ids.length && type === "training_card"
      ? await queryRows(
          "SELECT * FROM sessions WHERE candidate_id = ANY($1::integer[]) ORDER BY session_date, session_time",
          [ids],
        )
      : [];
  const payments =
    type === "payment_receipt"
      ? await queryRows(
          "SELECT * FROM payments WHERE candidate_id = $1 ORDER BY date, id",
          [candidateId],
        )
      : type === "payments_report"
        ? await queryRows(
            `SELECT * FROM payments
             WHERE ($1::date IS NULL OR date >= $1)
               AND ($2::date IS NULL OR date <= $2)
             ORDER BY date, id LIMIT 5000`,
            [from || null, to || null],
          )
        : [];
  if (type === "payments_report") {
    const paymentCandidateRows = await queryRows(
      `SELECT DISTINCT c.*
         FROM candidates c
         JOIN payments p ON p.candidate_id = c.id
        WHERE ($1::date IS NULL OR p.date >= $1)
          AND ($2::date IS NULL OR p.date <= $2)
        ORDER BY c.last_name, c.first_name`,
      [from || null, to || null],
    );
    candidates = paymentCandidateRows;
  }
  const expenses =
    type === "expenses_report"
      ? await queryRows(
          `SELECT * FROM expenses
           WHERE ($1::date IS NULL OR date >= $1)
             AND ($2::date IS NULL OR date <= $2)
           ORDER BY date, id LIMIT 5000`,
          [from || null, to || null],
        )
      : [];
  const examResults =
    ids.length
      ? await queryRows(
          "SELECT * FROM exam_results WHERE candidate_id = ANY($1::integer[]) ORDER BY exam_date, id",
          [ids],
        )
      : [];
  const examAttempts =
    ids.length
      ? await queryRows(
          "SELECT * FROM exam_attempts WHERE candidate_id = ANY($1::integer[]) ORDER BY exam_date, id",
          [ids],
        )
      : [];

  return {
    school: schoolRows[0] ?? {},
    candidates,
    instructors,
    vehicles,
    training_stages: stages,
    sessions,
    payments,
    expenses,
    exam_results: examResults,
    exam_attempts: examAttempts,
  };
}

router.get(
  "/documents/catalog",
  requirePermission("print_docs"),
  (req, res) => {
    const locale: Locale = req.query.language === "fr" ? "fr" : "ar";
    const docs = Object.values(catalog).map((item) => item[locale]);
    res.json(GetDocumentCatalogResponse.parse(docs));
  },
);

router.post(
  "/documents/generate",
  requirePermission("print_docs"),
  async (req, res) => {
    const parsed = GenerateDocumentBody.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: "Review the document request fields." });
      return;
    }
    const input = parsed.data;
    const selected = catalog[input.type];
    if (!selected) {
      res.status(404).json({ error: "This official document is not available." });
      return;
    }
    const definition = selected[input.language];
    if (definition.scope === "candidate" && !input.candidateId) {
      res.status(400).json({ error: "Select a candidate for this document." });
      return;
    }
    if (
      input.type === "exam_candidates_list" &&
      (!input.options ||
        typeof input.options.examDate !== "string" ||
        !input.options.examDate)
    ) {
      res.status(400).json({ error: "Enter the exam date." });
      return;
    }
    const candidateIds = (input.candidateIds ?? []).map(Number);
    if (
      candidateIds.length > 1000 ||
      candidateIds.some((id) => !Number.isSafeInteger(id) || id < 1)
    ) {
      res.status(400).json({ error: "The candidate selection is invalid." });
      return;
    }
    if (input.candidateId !== undefined && input.candidateId < 1) {
      res.status(400).json({ error: "The candidate selection is invalid." });
      return;
    }
    try {
      const root = pythonRoot();
      const scriptPath = path.join(root, "scripts", "render_medanic_document.py");
      if (!existsSync(scriptPath)) {
        throw new Error("The official document renderer is missing.");
      }
      const tempDir = await mkdtemp(path.join(os.tmpdir(), "medanic-document-"));
      const outputPath = path.join(tempDir, `${input.type}.pdf`);
      try {
        const datasets = await collectData(
          input.type,
          input.candidateId,
          candidateIds,
          dateParam(input.from),
          dateParam(input.to),
        );
        if (definition.scope === "candidate" && !datasets.candidates.length) {
          res.status(404).json({ error: "Candidate not found." });
          return;
        }
        if (
          definition.scope === "group" &&
          ["dispatch_table", "candidates_list", "exam_candidates_list"].includes(input.type) &&
          !datasets.candidates.length
        ) {
          res.status(404).json({ error: "There are no candidates for this document." });
          return;
        }
        await runRenderer(scriptPath, {
          type: input.type,
          language: input.language,
          candidateId: input.candidateId,
          candidateIds,
          from: input.from,
          to: input.to,
          options: input.options ?? {},
          datasets,
          tempDir,
          outputPath,
        });
        const pdf = await readFile(outputPath);
        const fileName = `medanic-${input.type}.pdf`;
        res.setHeader("Content-Type", "application/pdf");
        res.setHeader(
          "Content-Disposition",
          `attachment; filename="${fileName}"`,
        );
        res.setHeader("Content-Length", pdf.length);
        res.send(pdf);
      } finally {
        await rm(tempDir, { recursive: true, force: true });
      }
    } catch (error) {
      req.log.error({ err: error, documentType: input.type }, "Official PDF generation failed");
      res.status(500).json({
        error: "The official PDF could not be generated. Check the document data and try again.",
      });
    }
  },
);

export default router;
