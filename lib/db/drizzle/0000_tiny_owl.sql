CREATE TABLE "candidates" (
	"id" serial PRIMARY KEY NOT NULL,
	"first_name" text NOT NULL,
	"last_name" text NOT NULL,
	"gender" text DEFAULT '' NOT NULL,
	"birth_date" date,
	"birth_place_commune" text DEFAULT '' NOT NULL,
	"birth_place_wilaya" text DEFAULT '' NOT NULL,
	"marital_status" text DEFAULT '' NOT NULL,
	"father_name" text DEFAULT '' NOT NULL,
	"mother_name" text DEFAULT '' NOT NULL,
	"phone" text DEFAULT '' NOT NULL,
	"nationality" text DEFAULT 'جزائرية' NOT NULL,
	"disability" text DEFAULT '' NOT NULL,
	"blood_type" text DEFAULT '' NOT NULL,
	"license_type" text DEFAULT 'B' NOT NULL,
	"previous_licenses" text DEFAULT '' NOT NULL,
	"instructor_id" integer,
	"total_amount" numeric(12, 2) DEFAULT 0 NOT NULL,
	"registration_date" date DEFAULT now() NOT NULL,
	"national_id" text DEFAULT '' NOT NULL,
	"second_nationality" text DEFAULT '' NOT NULL,
	"current_address" text DEFAULT '' NOT NULL,
	"is_born_abroad" boolean DEFAULT false NOT NULL,
	"birth_country" text DEFAULT 'الجزائر' NOT NULL,
	"embassy" text DEFAULT '' NOT NULL,
	"consulate" text DEFAULT '' NOT NULL,
	"file_number" text DEFAULT '' NOT NULL,
	"file_date" date,
	"address_commune" text DEFAULT '' NOT NULL,
	"address_wilaya" text DEFAULT '' NOT NULL,
	"last_name_fr" text DEFAULT '' NOT NULL,
	"first_name_fr" text DEFAULT '' NOT NULL,
	"insurance_number" text DEFAULT '' NOT NULL,
	"email" text DEFAULT '' NOT NULL,
	"guardian_first_name" text DEFAULT '' NOT NULL,
	"guardian_last_name" text DEFAULT '' NOT NULL,
	"guardian_birth_date" date,
	"guardian_address" text DEFAULT '' NOT NULL,
	"guardian_phone" text DEFAULT '' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "instructors" (
	"id" serial PRIMARY KEY NOT NULL,
	"first_name" text NOT NULL,
	"last_name" text NOT NULL,
	"gender" text DEFAULT '' NOT NULL,
	"birth_date" date,
	"birth_place" text DEFAULT '' NOT NULL,
	"phone" text DEFAULT '' NOT NULL,
	"address" text DEFAULT '' NOT NULL,
	"license_number" text DEFAULT '' NOT NULL,
	"license_date" date,
	"categories" text DEFAULT '' NOT NULL,
	"experience_years" integer DEFAULT 0 NOT NULL,
	"contract_duration" text DEFAULT '' NOT NULL,
	"salary" numeric(12, 2) DEFAULT 0 NOT NULL,
	"contract_start_date" date,
	"notice_period" text DEFAULT '0' NOT NULL,
	"contract_signing_date" date
);
--> statement-breakpoint
CREATE TABLE "school_info" (
	"id" integer PRIMARY KEY DEFAULT 1 NOT NULL,
	"name" text DEFAULT '' NOT NULL,
	"commercial_register" text DEFAULT '' NOT NULL,
	"accreditation_number" text DEFAULT '' NOT NULL,
	"nif" text DEFAULT '' NOT NULL,
	"nis" text DEFAULT '' NOT NULL,
	"article_number" text DEFAULT '' NOT NULL,
	"address" text DEFAULT '' NOT NULL,
	"phone" text DEFAULT '' NOT NULL,
	"wilaya" text DEFAULT '' NOT NULL,
	"manager_name" text DEFAULT '' NOT NULL,
	"accreditation_date" date,
	"address_commune" text DEFAULT '' NOT NULL,
	"address_daira" text DEFAULT '' NOT NULL,
	"owner_name" text DEFAULT '' NOT NULL,
	"owner_birth_date" date,
	"owner_birth_place" text DEFAULT '' NOT NULL,
	"owner_email" text DEFAULT '' NOT NULL,
	"representative_name" text DEFAULT '' NOT NULL,
	"representative_birth_date" date,
	"representative_birth_place" text DEFAULT '' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "users" (
	"id" serial PRIMARY KEY NOT NULL,
	"username" text NOT NULL,
	"password_hash" text NOT NULL,
	"role" text DEFAULT 'trainer' NOT NULL,
	"full_name" text DEFAULT '' NOT NULL,
	"permissions" jsonb DEFAULT '{}'::jsonb NOT NULL,
	CONSTRAINT "users_username_unique" UNIQUE("username")
);
--> statement-breakpoint
CREATE TABLE "vehicles" (
	"id" serial PRIMARY KEY NOT NULL,
	"model" text DEFAULT '' NOT NULL,
	"plate_number" text DEFAULT '' NOT NULL,
	"insurance_expiry" date,
	"tech_inspection_expiry" date,
	"notes" text DEFAULT '' NOT NULL,
	"vehicle_type" text DEFAULT 'سيارة' NOT NULL,
	"training_card_number" text DEFAULT '' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "exam_attempts" (
	"id" serial PRIMARY KEY NOT NULL,
	"candidate_id" integer NOT NULL,
	"stage_type" text NOT NULL,
	"exam_date" date DEFAULT now() NOT NULL,
	"score" numeric(8, 2) DEFAULT 0 NOT NULL,
	"result" text DEFAULT 'راسب' NOT NULL,
	"notes" text DEFAULT '' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "exam_results" (
	"id" serial PRIMARY KEY NOT NULL,
	"candidate_id" integer NOT NULL,
	"exam_type" text NOT NULL,
	"exam_date" date DEFAULT now() NOT NULL,
	"result" text NOT NULL,
	"score" numeric(8, 2) DEFAULT 0 NOT NULL,
	"notes" text DEFAULT '' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "expenses" (
	"id" serial PRIMARY KEY NOT NULL,
	"expense_type" text DEFAULT '' NOT NULL,
	"amount" numeric(12, 2) DEFAULT 0 NOT NULL,
	"date" date DEFAULT now() NOT NULL,
	"notes" text DEFAULT '' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "payments" (
	"id" serial PRIMARY KEY NOT NULL,
	"candidate_id" integer NOT NULL,
	"date" date DEFAULT now() NOT NULL,
	"amount" numeric(12, 2) DEFAULT 0 NOT NULL,
	"payment_method" text DEFAULT '' NOT NULL,
	"notes" text DEFAULT '' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "sessions" (
	"id" serial PRIMARY KEY NOT NULL,
	"candidate_id" integer NOT NULL,
	"instructor_id" integer,
	"vehicle_id" integer,
	"session_date" date NOT NULL,
	"session_time" time NOT NULL,
	"duration" numeric(6, 2) DEFAULT 1 NOT NULL,
	"session_type" text DEFAULT '' NOT NULL,
	"notes" text DEFAULT '' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "training_stages" (
	"id" serial PRIMARY KEY NOT NULL,
	"candidate_id" integer NOT NULL,
	"stage_type" text NOT NULL,
	"status" text DEFAULT 'لم يبدأ' NOT NULL,
	"start_date" date,
	"end_date" date,
	"score" numeric(8, 2) DEFAULT 0 NOT NULL,
	"notes" text DEFAULT '' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "erp_accounts" (
	"id" serial PRIMARY KEY NOT NULL,
	"code" text NOT NULL,
	"name" text NOT NULL,
	"category" text NOT NULL,
	"normal_side" text DEFAULT 'debit' NOT NULL,
	"is_active" integer DEFAULT 1 NOT NULL,
	CONSTRAINT "erp_accounts_code_unique" UNIQUE("code")
);
--> statement-breakpoint
CREATE TABLE "erp_employees" (
	"id" serial PRIMARY KEY NOT NULL,
	"first_name" text NOT NULL,
	"last_name" text NOT NULL,
	"job_title" text DEFAULT '' NOT NULL,
	"phone" text DEFAULT '' NOT NULL,
	"email" text DEFAULT '' NOT NULL,
	"contract_type" text DEFAULT '' NOT NULL,
	"start_date" date,
	"base_salary" numeric(12, 2) DEFAULT 0 NOT NULL,
	"status" text DEFAULT 'active' NOT NULL,
	"notes" text DEFAULT '' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "erp_journal_entries" (
	"id" serial PRIMARY KEY NOT NULL,
	"entry_date" date DEFAULT now() NOT NULL,
	"description" text NOT NULL,
	"reference" text DEFAULT '' NOT NULL,
	"source" text DEFAULT 'manual' NOT NULL,
	"created_by" integer,
	"reversal_of_id" integer,
	"created_at" date DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "erp_journal_lines" (
	"id" serial PRIMARY KEY NOT NULL,
	"journal_entry_id" integer NOT NULL,
	"account_id" integer NOT NULL,
	"debit" numeric(12, 2) DEFAULT 0 NOT NULL,
	"credit" numeric(12, 2) DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE "erp_payroll" (
	"id" serial PRIMARY KEY NOT NULL,
	"employee_id" integer NOT NULL,
	"period" text NOT NULL,
	"gross_amount" numeric(12, 2) NOT NULL,
	"deductions" numeric(12, 2) DEFAULT 0 NOT NULL,
	"net_amount" numeric(12, 2) NOT NULL,
	"status" text DEFAULT 'pending' NOT NULL,
	"paid_at" date,
	"notes" text DEFAULT '' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "erp_settings" (
	"key" text PRIMARY KEY NOT NULL,
	"value" jsonb NOT NULL
);
--> statement-breakpoint
ALTER TABLE "candidates" ADD CONSTRAINT "candidates_instructor_id_instructors_id_fk" FOREIGN KEY ("instructor_id") REFERENCES "public"."instructors"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "exam_attempts" ADD CONSTRAINT "exam_attempts_candidate_id_candidates_id_fk" FOREIGN KEY ("candidate_id") REFERENCES "public"."candidates"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "exam_results" ADD CONSTRAINT "exam_results_candidate_id_candidates_id_fk" FOREIGN KEY ("candidate_id") REFERENCES "public"."candidates"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "payments" ADD CONSTRAINT "payments_candidate_id_candidates_id_fk" FOREIGN KEY ("candidate_id") REFERENCES "public"."candidates"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "sessions" ADD CONSTRAINT "sessions_candidate_id_candidates_id_fk" FOREIGN KEY ("candidate_id") REFERENCES "public"."candidates"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "sessions" ADD CONSTRAINT "sessions_instructor_id_instructors_id_fk" FOREIGN KEY ("instructor_id") REFERENCES "public"."instructors"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "sessions" ADD CONSTRAINT "sessions_vehicle_id_vehicles_id_fk" FOREIGN KEY ("vehicle_id") REFERENCES "public"."vehicles"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "training_stages" ADD CONSTRAINT "training_stages_candidate_id_candidates_id_fk" FOREIGN KEY ("candidate_id") REFERENCES "public"."candidates"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "erp_journal_entries" ADD CONSTRAINT "erp_journal_entries_created_by_users_id_fk" FOREIGN KEY ("created_by") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "erp_journal_lines" ADD CONSTRAINT "erp_journal_lines_journal_entry_id_erp_journal_entries_id_fk" FOREIGN KEY ("journal_entry_id") REFERENCES "public"."erp_journal_entries"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "erp_journal_lines" ADD CONSTRAINT "erp_journal_lines_account_id_erp_accounts_id_fk" FOREIGN KEY ("account_id") REFERENCES "public"."erp_accounts"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "erp_payroll" ADD CONSTRAINT "erp_payroll_employee_id_erp_employees_id_fk" FOREIGN KEY ("employee_id") REFERENCES "public"."erp_employees"("id") ON DELETE no action ON UPDATE no action;