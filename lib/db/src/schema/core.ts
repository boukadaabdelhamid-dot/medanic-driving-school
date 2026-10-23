import { createInsertSchema } from "drizzle-zod";
import {
  boolean,
  date,
  integer,
  jsonb,
  numeric,
  pgTable,
  serial,
  text,
} from "drizzle-orm/pg-core";
import { z } from "zod/v4";

export const usersTable = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  passwordHash: text("password_hash").notNull(),
  role: text("role").notNull().default("trainer"),
  fullName: text("full_name").notNull().default(""),
  permissions: jsonb("permissions")
    .$type<Record<string, boolean>>()
    .notNull()
    .default({}),
});

export const insertUserSchema = createInsertSchema(usersTable).omit({
  id: true,
});
export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof usersTable.$inferSelect;

export const schoolInfoTable = pgTable("school_info", {
  id: integer("id").primaryKey().default(1),
  name: text("name").notNull().default(""),
  commercialRegister: text("commercial_register").notNull().default(""),
  accreditationNumber: text("accreditation_number").notNull().default(""),
  nif: text("nif").notNull().default(""),
  nis: text("nis").notNull().default(""),
  articleNumber: text("article_number").notNull().default(""),
  address: text("address").notNull().default(""),
  phone: text("phone").notNull().default(""),
  wilaya: text("wilaya").notNull().default(""),
  managerName: text("manager_name").notNull().default(""),
  accreditationDate: date("accreditation_date", { mode: "string" }),
  addressCommune: text("address_commune").notNull().default(""),
  addressDaira: text("address_daira").notNull().default(""),
  ownerName: text("owner_name").notNull().default(""),
  ownerBirthDate: date("owner_birth_date", { mode: "string" }),
  ownerBirthPlace: text("owner_birth_place").notNull().default(""),
  ownerEmail: text("owner_email").notNull().default(""),
  representativeName: text("representative_name").notNull().default(""),
  representativeBirthDate: date("representative_birth_date", {
    mode: "string",
  }),
  representativeBirthPlace: text("representative_birth_place")
    .notNull()
    .default(""),
});

export const insertSchoolInfoSchema = createInsertSchema(schoolInfoTable).omit({
  id: true,
});
export type InsertSchoolInfo = z.infer<typeof insertSchoolInfoSchema>;
export type SchoolInfo = typeof schoolInfoTable.$inferSelect;

export const instructorsTable = pgTable("instructors", {
  id: serial("id").primaryKey(),
  firstName: text("first_name").notNull(),
  lastName: text("last_name").notNull(),
  gender: text("gender").notNull().default(""),
  birthDate: date("birth_date", { mode: "string" }),
  birthPlace: text("birth_place").notNull().default(""),
  phone: text("phone").notNull().default(""),
  address: text("address").notNull().default(""),
  licenseNumber: text("license_number").notNull().default(""),
  licenseDate: date("license_date", { mode: "string" }),
  categories: text("categories").notNull().default(""),
  experienceYears: integer("experience_years").notNull().default(0),
  contractDuration: text("contract_duration").notNull().default(""),
  salary: numeric("salary", { precision: 12, scale: 2, mode: "number" })
    .notNull()
    .default(0),
  contractStartDate: date("contract_start_date", { mode: "string" }),
  noticePeriod: text("notice_period").notNull().default("0"),
  contractSigningDate: date("contract_signing_date", { mode: "string" }),
});

export const insertInstructorSchema = createInsertSchema(instructorsTable).omit({
  id: true,
});
export type InsertInstructor = z.infer<typeof insertInstructorSchema>;
export type Instructor = typeof instructorsTable.$inferSelect;

export const candidatesTable = pgTable("candidates", {
  id: serial("id").primaryKey(),
  firstName: text("first_name").notNull(),
  lastName: text("last_name").notNull(),
  gender: text("gender").notNull().default(""),
  birthDate: date("birth_date", { mode: "string" }),
  birthPlaceCommune: text("birth_place_commune").notNull().default(""),
  birthPlaceWilaya: text("birth_place_wilaya").notNull().default(""),
  maritalStatus: text("marital_status").notNull().default(""),
  fatherName: text("father_name").notNull().default(""),
  motherName: text("mother_name").notNull().default(""),
  phone: text("phone").notNull().default(""),
  nationality: text("nationality").notNull().default("جزائرية"),
  disability: text("disability").notNull().default(""),
  bloodType: text("blood_type").notNull().default(""),
  licenseType: text("license_type").notNull().default("B"),
  previousLicenses: text("previous_licenses").notNull().default(""),
  instructorId: integer("instructor_id").references(() => instructorsTable.id),
  totalAmount: numeric("total_amount", {
    precision: 12,
    scale: 2,
    mode: "number",
  })
    .notNull()
    .default(0),
  registrationDate: date("registration_date", { mode: "string" })
    .notNull()
    .defaultNow(),
  nationalId: text("national_id").notNull().default(""),
  secondNationality: text("second_nationality").notNull().default(""),
  currentAddress: text("current_address").notNull().default(""),
  isBornAbroad: boolean("is_born_abroad").notNull().default(false),
  birthCountry: text("birth_country").notNull().default("الجزائر"),
  embassy: text("embassy").notNull().default(""),
  consulate: text("consulate").notNull().default(""),
  fileNumber: text("file_number").notNull().default(""),
  fileDate: date("file_date", { mode: "string" }),
  addressCommune: text("address_commune").notNull().default(""),
  addressWilaya: text("address_wilaya").notNull().default(""),
  lastNameFr: text("last_name_fr").notNull().default(""),
  firstNameFr: text("first_name_fr").notNull().default(""),
  insuranceNumber: text("insurance_number").notNull().default(""),
  email: text("email").notNull().default(""),
  guardianFirstName: text("guardian_first_name").notNull().default(""),
  guardianLastName: text("guardian_last_name").notNull().default(""),
  guardianBirthDate: date("guardian_birth_date", { mode: "string" }),
  guardianAddress: text("guardian_address").notNull().default(""),
  guardianPhone: text("guardian_phone").notNull().default(""),
});

export const insertCandidateSchema = createInsertSchema(candidatesTable).omit({
  id: true,
});
export type InsertCandidate = z.infer<typeof insertCandidateSchema>;
export type Candidate = typeof candidatesTable.$inferSelect;

export const vehiclesTable = pgTable("vehicles", {
  id: serial("id").primaryKey(),
  model: text("model").notNull().default(""),
  plateNumber: text("plate_number").notNull().default(""),
  insuranceExpiry: date("insurance_expiry", { mode: "string" }),
  techInspectionExpiry: date("tech_inspection_expiry", { mode: "string" }),
  notes: text("notes").notNull().default(""),
  vehicleType: text("vehicle_type").notNull().default("سيارة"),
  trainingCardNumber: text("training_card_number").notNull().default(""),
});

export const insertVehicleSchema = createInsertSchema(vehiclesTable).omit({
  id: true,
});
export type InsertVehicle = z.infer<typeof insertVehicleSchema>;
export type Vehicle = typeof vehiclesTable.$inferSelect;
