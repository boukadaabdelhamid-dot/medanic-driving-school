export const RESOURCE_NAMES = [
  "candidates",
  "instructors",
  "trainingStages",
  "vehicles",
  "sessions",
  "payments",
  "expenses",
  "examResults",
  "examAttempts",
  "graduates",
  "users",
  "accounts",
  "journalEntries",
  "employees",
  "payroll",
] as const;

export type ResourceName = (typeof RESOURCE_NAMES)[number];
export type FieldType =
  | "text"
  | "email"
  | "number"
  | "date"
  | "select"
  | "boolean"
  | "textarea"
  | "password"
  | "permissions";

export type FieldOption = { value: string; label: string };
export type ResourceField = {
  name: string;
  label: string;
  type: FieldType;
  required: boolean;
  options?: FieldOption[];
  multiple?: boolean;
  readOnly?: boolean;
  hidden?: boolean;
};

type FieldSpec = Omit<ResourceField, "label" | "options"> & {
  ar: string;
  fr: string;
  options?: string[];
};

export type ResourceDefinition = {
  table: string;
  permission: string;
  fields: FieldSpec[];
  searchable: string[];
  orderBy: string;
  adminOnly?: boolean;
  readOnly?: boolean;
  derivedGraduates?: boolean;
};

const field = (
  name: string,
  ar: string,
  fr: string,
  type: FieldType = "text",
  required = false,
  options?: string[],
  readOnly = false,
  multiple = false,
): FieldSpec => ({
  name,
  ar,
  fr,
  type,
  required,
  ...(options ? { options } : {}),
  ...(multiple ? { multiple: true } : {}),
  ...(readOnly ? { readOnly: true } : {}),
});

const genderOptions = ["ذكر", "أنثى"];
const permissionLabels: Record<string, { ar: string; fr: string }> = {
  view_dashboard: { ar: "عرض لوحة القيادة", fr: "Voir le tableau de bord" },
  view_candidates: { ar: "عرض المترشحين", fr: "Voir les candidats" },
  edit_candidates: { ar: "إضافة وتعديل وحذف المترشحين", fr: "Gérer les candidats" },
  view_payments: { ar: "عرض المدفوعات", fr: "Voir les paiements" },
  add_payments: { ar: "إضافة المدفوعات", fr: "Ajouter des paiements" },
  view_expenses: { ar: "عرض المصاريف", fr: "Voir les dépenses" },
  view_training: { ar: "عرض مراحل التكوين", fr: "Voir la formation" },
  view_schedule: { ar: "عرض الجدول الزمني", fr: "Voir le planning" },
  print_docs: { ar: "طباعة الوثائق", fr: "Imprimer les documents" },
  view_reports: { ar: "عرض التقارير", fr: "Voir les rapports" },
  manage_school_info: { ar: "إدارة معلومات المدرسة", fr: "Gérer l'école" },
};

const candidateFields = [
  field("firstName", "الاسم", "Prénom", "text", true),
  field("lastName", "اللقب", "Nom", "text", true),
  field("firstNameFr", "الاسم بالفرنسية", "Prénom en français"),
  field("lastNameFr", "اللقب بالفرنسية", "Nom en français"),
  field("gender", "الجنس", "Genre", "select", false, genderOptions),
  field("birthDate", "تاريخ الميلاد", "Date de naissance", "date"),
  field("birthPlaceCommune", "بلدية الميلاد", "Commune de naissance"),
  field("birthPlaceWilaya", "ولاية الميلاد", "Wilaya de naissance"),
  field("maritalStatus", "الحالة العائلية", "Situation familiale"),
  field("fatherName", "اسم الأب", "Nom du père"),
  field("motherName", "اسم الأم", "Nom de la mère"),
  field("phone", "الهاتف", "Téléphone"),
  field("email", "البريد الإلكتروني", "E-mail"),
  field("nationality", "الجنسية", "Nationalité"),
  field("secondNationality", "الجنسية الثانية", "Seconde nationalité"),
  field("disability", "الإعاقة", "Handicap"),
  field("bloodType", "فصيلة الدم", "Groupe sanguin"),
  field("licenseType", "صنف الرخصة", "Catégorie de permis", "select", true, [
    "A1",
    "A",
    "B",
    "C",
    "D",
    "E",
  ]),
  field("previousLicenses", "الرخص السابقة", "Permis précédents"),
  field("instructorId", "الممرّن", "Moniteur", "number"),
  field("totalAmount", "المبلغ الإجمالي", "Montant total", "number"),
  field("registrationDate", "تاريخ التسجيل", "Date d'inscription", "date"),
  field("nationalId", "رقم التعريف الوطني", "N° d'identification nationale"),
  field("insuranceNumber", "رقم التأمين", "N° d'assurance"),
  field("currentAddress", "العنوان الحالي", "Adresse actuelle"),
  field("isBornAbroad", "مولود خارج الوطن", "Né à l'étranger", "boolean"),
  field("birthCountry", "بلد الميلاد", "Pays de naissance"),
  field("embassy", "السفارة", "Ambassade"),
  field("consulate", "القنصلية", "Consulat"),
  field("fileNumber", "رقم الملف", "N° de dossier"),
  field("fileDate", "تاريخ الملف", "Date du dossier", "date"),
  field("addressCommune", "بلدية السكن", "Commune de résidence"),
  field("addressWilaya", "ولاية السكن", "Wilaya de résidence"),
  field("guardianFirstName", "اسم الولي", "Prénom du tuteur"),
  field("guardianLastName", "لقب الولي", "Nom du tuteur"),
  field("guardianBirthDate", "تاريخ ميلاد الولي", "Date de naissance du tuteur", "date"),
  field("guardianAddress", "عنوان الولي", "Adresse du tuteur"),
  field("guardianPhone", "هاتف الولي", "Téléphone du tuteur"),
];

const instructorFields = [
  field("firstName", "الاسم", "Prénom", "text", true),
  field("lastName", "اللقب", "Nom", "text", true),
  field("gender", "الجنس", "Genre", "select", false, genderOptions),
  field("birthDate", "تاريخ الميلاد", "Date de naissance", "date"),
  field("birthPlace", "مكان الميلاد", "Lieu de naissance"),
  field("phone", "الهاتف", "Téléphone"),
  field("address", "العنوان", "Adresse"),
  field("licenseNumber", "رقم الرخصة", "N° de permis"),
  field("licenseDate", "تاريخ الرخصة", "Date du permis", "date"),
  field("categories", "الأصناف", "Catégories"),
  field("experienceYears", "سنوات الخبرة", "Années d'expérience", "number"),
  field("contractDuration", "مدة العقد", "Durée du contrat"),
  field("salary", "الأجر", "Salaire", "number"),
  field("contractStartDate", "بداية العقد", "Début du contrat", "date"),
  field("noticePeriod", "مدة الإشعار", "Préavis"),
  field("contractSigningDate", "تاريخ توقيع العقد", "Date de signature", "date"),
];

export const resourceDefinitions: Record<ResourceName, ResourceDefinition> = {
  candidates: {
    table: "candidates",
    permission: "view_candidates",
    fields: candidateFields,
    searchable: ["firstName", "lastName", "phone", "nationalId", "fileNumber"],
    orderBy: "last_name ASC, first_name ASC",
  },
  instructors: {
    table: "instructors",
    permission: "view_instructors",
    fields: instructorFields,
    searchable: ["firstName", "lastName", "phone", "licenseNumber"],
    orderBy: "last_name ASC, first_name ASC",
  },
  trainingStages: {
    table: "training_stages",
    permission: "view_training",
    fields: [
      field("candidateId", "المترشح", "Candidat", "number", true),
      field("stageType", "مرحلة التكوين", "Étape de formation", "select", true, [
        "code",
        "creneau",
        "circuit",
      ]),
      field("status", "الحالة", "Statut", "select", false, [
        "لم يبدأ",
        "قيد التكوين",
        "ناجح",
        "راسب",
      ]),
      field("startDate", "تاريخ البداية", "Date de début", "date"),
      field("endDate", "تاريخ النهاية", "Date de fin", "date"),
      field("score", "العلامة", "Note", "number"),
      field("notes", "ملاحظات", "Notes", "textarea"),
    ],
    searchable: ["stageType", "status", "notes"],
    orderBy: "id DESC",
  },
  vehicles: {
    table: "vehicles",
    permission: "view_schedule",
    fields: [
      field("model", "الطراز", "Modèle", "text", true),
      field("plateNumber", "رقم التسجيل", "Immatriculation"),
      field("insuranceExpiry", "انتهاء التأمين", "Expiration assurance", "date"),
      field("techInspectionExpiry", "انتهاء الفحص التقني", "Expiration contrôle technique", "date"),
      field("notes", "ملاحظات", "Notes", "textarea"),
      field("vehicleType", "نوع المركبة", "Type de véhicule", "select", false, [
        "سيارة",
        "دراجة نارية",
      ]),
      field("trainingCardNumber", "رقم بطاقة التكوين", "N° carte de formation"),
    ],
    searchable: ["model", "plateNumber", "trainingCardNumber"],
    orderBy: "model ASC",
  },
  sessions: {
    table: "sessions",
    permission: "view_schedule",
    fields: [
      field("candidateId", "المترشح", "Candidat", "number", true),
      field("instructorId", "الممرّن", "Moniteur", "number", true),
      field("vehicleId", "المركبة", "Véhicule", "number"),
      field("sessionDate", "التاريخ", "Date", "date", true),
      field("sessionTime", "الوقت", "Heure", "text", true),
      field("duration", "المدة بالساعات", "Durée en heures", "number", true),
      field("sessionType", "نوع الحصة", "Type de séance"),
      field("notes", "ملاحظات", "Notes", "textarea"),
    ],
    searchable: ["sessionType", "notes"],
    orderBy: "session_date DESC, session_time DESC",
  },
  payments: {
    table: "payments",
    permission: "view_payments",
    fields: [
      field("candidateId", "المترشح", "Candidat", "number", true),
      field("date", "التاريخ", "Date", "date", true),
      field("amount", "المبلغ", "Montant", "number", true),
      field("paymentMethod", "طريقة الدفع", "Mode de paiement", "select", false, [
        "نقدي",
        "تحويل",
        "بطاقة",
        "شيك",
      ]),
      field("notes", "ملاحظات", "Notes", "textarea"),
    ],
    searchable: ["paymentMethod", "notes"],
    orderBy: "date DESC, id DESC",
  },
  expenses: {
    table: "expenses",
    permission: "view_expenses",
    fields: [
      field("expenseType", "نوع المصروف", "Type de dépense", "text", true),
      field("amount", "المبلغ", "Montant", "number", true),
      field("date", "التاريخ", "Date", "date", true),
      field("notes", "ملاحظات", "Notes", "textarea"),
    ],
    searchable: ["expenseType", "notes"],
    orderBy: "date DESC, id DESC",
  },
  examResults: {
    table: "exam_results",
    permission: "view_training",
    fields: [
      field("candidateId", "المترشح", "Candidat", "number", true),
      field("examType", "نوع الامتحان", "Type d'examen", "text", true),
      field("examDate", "تاريخ الامتحان", "Date d'examen", "date"),
      field("result", "النتيجة", "Résultat", "text", true),
      field("score", "العلامة", "Note", "number"),
      field("notes", "ملاحظات", "Notes", "textarea"),
    ],
    searchable: ["examType", "result", "notes"],
    orderBy: "exam_date DESC, id DESC",
  },
  examAttempts: {
    table: "exam_attempts",
    permission: "view_training",
    fields: [
      field("candidateId", "المترشح", "Candidat", "number", true),
      field("stageType", "المرحلة", "Étape", "text", true),
      field("examDate", "تاريخ الامتحان", "Date d'examen", "date"),
      field("score", "العلامة", "Note", "number"),
      field("result", "النتيجة", "Résultat", "text", true),
      field("notes", "ملاحظات", "Notes", "textarea"),
    ],
    searchable: ["stageType", "result", "notes"],
    orderBy: "exam_date DESC, id DESC",
  },
  graduates: {
    table: "candidates",
    permission: "view_graduates",
    fields: [
      ...candidateFields.map((item) => ({ ...item, readOnly: true })),
      field("instructorName", "الممرّن", "Moniteur", "text", false, undefined, true),
    ],
    searchable: ["firstName", "lastName", "phone", "nationalId"],
    orderBy: "last_name ASC, first_name ASC",
    readOnly: true,
    derivedGraduates: true,
  },
  users: {
    table: "users",
    permission: "manage_users",
    fields: [
      field("username", "البريد الإلكتروني", "Adresse e-mail", "email", true),
      field("password", "كلمة المرور", "Mot de passe", "password", false),
      field("fullName", "الاسم الكامل", "Nom complet"),
      field("role", "الدور", "Rôle", "select", true, ["admin", "trainer"]),
      field(
        "permissions",
        "الصلاحيات",
        "Autorisations",
        "permissions",
        false,
        Object.keys(permissionLabels),
        false,
        true,
      ),
    ],
    searchable: ["username", "fullName", "role"],
    orderBy: "role DESC, username ASC",
    adminOnly: true,
  },
  accounts: {
    table: "erp_accounts",
    permission: "view_erp",
    fields: [
      field("code", "رمز الحساب", "Code du compte", "text", true),
      field("name", "اسم الحساب", "Nom du compte", "text", true),
      field("category", "الفئة", "Catégorie", "select", true, [
        "asset",
        "liability",
        "equity",
        "revenue",
        "expense",
      ]),
      field("normalSide", "الطرف الطبيعي", "Solde normal", "select", true, [
        "debit",
        "credit",
      ]),
      field("isActive", "نشط", "Actif", "boolean"),
    ],
    searchable: ["code", "name", "category"],
    orderBy: "code ASC",
    adminOnly: true,
  },
  journalEntries: {
    table: "erp_journal_entries",
    permission: "view_erp",
    fields: [
      field("entryDate", "تاريخ القيد", "Date de l'écriture", "date", true),
      field("description", "البيان", "Libellé", "text", true),
      field("reference", "المرجع", "Référence"),
      field("debitAccountId", "حساب المدين", "Compte débité", "number", true),
      field("creditAccountId", "حساب الدائن", "Compte crédité", "number", true),
      field("amount", "المبلغ", "Montant", "number", true),
      field("source", "المصدر", "Source", "text", false, undefined, true),
      field("reversalOfId", "القيد المعكوس", "Écriture contrepassée", "number", false, undefined, true),
    ],
    searchable: ["description", "reference", "source"],
    orderBy: "entry_date DESC, id DESC",
    adminOnly: true,
  },
  employees: {
    table: "erp_employees",
    permission: "view_erp",
    fields: [
      field("firstName", "الاسم", "Prénom", "text", true),
      field("lastName", "اللقب", "Nom", "text", true),
      field("jobTitle", "المنصب", "Poste"),
      field("phone", "الهاتف", "Téléphone"),
      field("email", "البريد الإلكتروني", "E-mail"),
      field("contractType", "نوع العقد", "Type de contrat"),
      field("startDate", "تاريخ البداية", "Date de début", "date"),
      field("baseSalary", "الأجر الأساسي", "Salaire de base", "number", true),
      field("status", "الحالة", "Statut", "select", false, [
        "active",
        "inactive",
      ]),
      field("notes", "ملاحظات", "Notes", "textarea"),
    ],
    searchable: ["firstName", "lastName", "jobTitle", "phone", "email"],
    orderBy: "last_name ASC, first_name ASC",
    adminOnly: true,
  },
  payroll: {
    table: "erp_payroll",
    permission: "view_erp",
    fields: [
      field("employeeId", "الموظف", "Employé", "number", true),
      field("period", "الفترة (YYYY-MM)", "Période (AAAA-MM)", "text", true),
      field("grossAmount", "الأجر الإجمالي", "Salaire brut", "number", true),
      field("deductions", "الاقتطاعات", "Retenues", "number"),
      field("netAmount", "الصافي", "Net à payer", "number", true, undefined, true),
      field("status", "الحالة", "Statut", "select", false, [
        "pending",
        "paid",
      ], true),
      field("paidAt", "تاريخ الدفع", "Date de paiement", "date", false, undefined, true),
      field("notes", "ملاحظات", "Notes", "textarea"),
    ],
    searchable: ["period", "status", "notes"],
    orderBy: "period DESC, id DESC",
    adminOnly: true,
  },
};

export function isResourceName(value: string): value is ResourceName {
  return (RESOURCE_NAMES as readonly string[]).includes(value);
}

export function getResourceDefinition(resource: ResourceName) {
  return resourceDefinitions[resource];
}

export function getLocalizedFields(
  resource: ResourceName,
  language: string,
): ResourceField[] {
  const locale = language === "fr" ? "fr" : "ar";
  return resourceDefinitions[resource].fields.map((item) => {
    const { ar, fr, options: rawOptions, ...fieldData } = item;
    const options = rawOptions?.map((value) => ({
      value,
      label:
        permissionLabels[value]?.[locale] ??
        translatedOptionLabels[value]?.[locale] ??
        value,
    }));
    return { ...fieldData, ...(options ? { options } : {}), label: locale === "fr" ? fr : ar };
  });
}

const translatedOptionLabels: Record<string, { ar: string; fr: string }> = {
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
};

export function toSnakeCase(value: string) {
  return value.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
}
