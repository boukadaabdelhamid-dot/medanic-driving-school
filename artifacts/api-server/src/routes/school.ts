import { Router, type IRouter } from "express";
import { GetSchoolResponse, UpdateSchoolBody, UpdateSchoolResponse } from "@workspace/api-zod";
import { pool } from "@workspace/db";
import { requireAuth, requirePermission } from "../lib/auth";
import { normalizeRow } from "../lib/resources";

const router: IRouter = Router();
router.use(requireAuth);

const schoolDateFields = [
  "accreditationDate",
  "ownerBirthDate",
  "representativeBirthDate",
];

const schoolStringFields = [
  "name",
  "commercialRegister",
  "accreditationNumber",
  "nif",
  "nis",
  "articleNumber",
  "address",
  "phone",
  "wilaya",
  "managerName",
  "accreditationDate",
  "addressCommune",
  "addressDaira",
  "ownerName",
  "ownerBirthDate",
  "ownerBirthPlace",
  "ownerEmail",
  "representativeName",
  "representativeBirthDate",
  "representativeBirthPlace",
];

function schoolResponse(row: Record<string, unknown>) {
  const data = normalizeRow(row);
  for (const key of schoolStringFields) {
    const value = data[key];
    if (value === null || value === undefined) {
      data[key] = "";
    } else if (schoolDateFields.includes(key) && value instanceof Date) {
      const year = value.getFullYear();
      const month = String(value.getMonth() + 1).padStart(2, "0");
      const day = String(value.getDate()).padStart(2, "0");
      data[key] = `${year}-${month}-${day}`;
    } else if (typeof value !== "string") {
      data[key] = String(value);
    }
  }
  return data;
}

router.get("/school", requirePermission("manage_school_info"), async (req, res) => {
  try {
    await pool.query("INSERT INTO school_info (id) VALUES (1) ON CONFLICT (id) DO NOTHING");
    const result = await pool.query("SELECT * FROM school_info WHERE id = 1");
    res.json(GetSchoolResponse.parse(schoolResponse(result.rows[0] ?? { id: 1 })));
  } catch (error) {
    req.log.error({ err: error }, "Could not load school profile");
    res.status(500).json({ error: "Could not load the school profile." });
  }
});

router.patch(
  "/school",
  requirePermission("manage_school_info"),
  async (req, res) => {
    const parsed = UpdateSchoolBody.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: "Review the school profile fields." });
      return;
    }
    const data: Record<string, unknown> = { ...parsed.data };
    for (const name of schoolDateFields) {
      if (data[name] === "") data[name] = null;
    }
    const entries = Object.entries(data);
    if (!entries.length) {
      res.status(400).json({ error: "Enter at least one field to update." });
      return;
    }
    const columns = entries.map(([key]) =>
      key.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`),
    );
    const values = entries.map(([, value]) => value);
    try {
      const insertColumns = ["id", ...columns];
      const placeholders = ["1", ...values.map((_, index) => `$${index + 1}`)];
      const updates = columns.map((column, index) => `${column} = $${index + 1}`);
      const result = await pool.query(
        `INSERT INTO school_info (${insertColumns.join(", ")})
         VALUES (${placeholders.join(", ")})
         ON CONFLICT (id) DO UPDATE SET ${updates.join(", ")}
         RETURNING *`,
        values,
      );
      res.json(UpdateSchoolResponse.parse(schoolResponse(result.rows[0])));
    } catch (error) {
      req.log.error({ err: error }, "Could not update school profile");
      res.status(500).json({ error: "Could not save the school profile." });
    }
  },
);

export default router;
