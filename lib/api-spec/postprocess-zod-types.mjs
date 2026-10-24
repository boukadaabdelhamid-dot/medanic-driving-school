import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const apiZodIndex = fileURLToPath(
  new URL("../api-zod/src/index.ts", import.meta.url),
);
const typesIndex = fileURLToPath(
  new URL("../api-zod/src/generated/types/index.ts", import.meta.url),
);
let contents = await readFile(typesIndex, "utf8");

for (const duplicate of ["getReportParams", "listResourceRecordsParams"]) {
  const exportLine = new RegExp(
    `^export \\* from ['"]\\./${duplicate}['"];\\r?\\n?`,
    "m",
  );
  contents = contents.replace(exportLine, "");
}

await writeFile(typesIndex, contents);
await writeFile(
  apiZodIndex,
  `export * from "./generated/api";
export type {
  AccountUpdateInput,
  ApiError,
  AuthCredentials,
  AuthUser,
  AuthUserPermissions,
  AuthUserRole,
  BadRequestResponse,
  CandidateIdParameter,
  ConflictResponse,
  DashboardSummary,
  DocumentRequest,
  DocumentRequestLanguage,
  DocumentRequestOptions,
  DocumentType,
  DocumentTypeScope,
  FieldDefinition,
  FieldDefinitionType,
  FieldOption,
  FromDateParameter,
  GetDashboardParams,
  GetDocumentCatalogParams,
  HealthStatus,
  InitialAdminInput,
  LanguageParameter,
  NotFoundResponse,
  PeriodParameter,
  ReportData,
  ReportDataTotals,
  ResourceInput,
  ResourceName,
  ResourcePage,
  ResourceRecord,
  SchoolInfo,
  SchoolInfoUpdate,
  SearchParameter,
  SetupStatus,
  ToDateParameter,
  UnauthorizedResponse,
} from "./generated/types";
`,
);
