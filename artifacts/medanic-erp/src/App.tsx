import { useEffect, useMemo, useState, createContext, useContext, type ReactNode } from 'react';
import { QueryClient, QueryClientProvider, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, Route, Router as WouterRouter, Switch, useLocation, useParams } from 'wouter';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import {
  Activity, ArrowDownLeft, ArrowLeft, ArrowRight, ArrowUpRight, BadgeCheck, Banknote,
  BookOpen, BriefcaseBusiness, CalendarDays, ChartNoAxesCombined, Check,
  ChevronLeft, ChevronRight, CircleHelp, Clock3, FileText, Gauge,
  GraduationCap, Languages, LayoutDashboard, LogOut, Menu, Plus, Search,
  ShieldCheck, UserRound, Users, Wallet, X, Pencil, Trash2, Download, RotateCcw,
  Building2, CircleDollarSign, ClipboardList, LoaderCircle, AlertCircle, type LucideIcon,
} from 'lucide-react';
import {
  useGetDashboard, getGetDashboardQueryKey, useGetSchool, getGetSchoolQueryKey,
  useListResourceRecords, getListResourceRecordsQueryKey, useGetResourceRecord,
  getGetResourceRecordQueryKey, useGetDocumentCatalog, useGetReport,
  getCreateResourceRecordMutationOptions,
  getUpdateResourceRecordMutationOptions, getDeleteResourceRecordMutationOptions,
  getUpdateSchoolMutationOptions, getGenerateDocumentMutationOptions,
  getReverseJournalEntryMutationOptions, getPayPayrollItemMutationOptions,
  getUpdateAccountMutationOptions,
  getLoginMutationOptions, getSetupInitialAdminMutationOptions, getLogoutMutationOptions,
  getGetCurrentUserQueryKey, getGetSetupStatusQueryKey,
  useGetCurrentUser, useGetSetupStatus, useHealthCheck,
} from '@workspace/api-client-react';
import type { FieldDefinition, ResourceName as ResourceNameType, ResourceRecord } from '@workspace/api-client-react';
import { Form } from '@/components/ui/form';
import logo from '../../../medanic_logo.png';
import './index.css';

type Lang = 'ar' | 'fr';
const LangContext = createContext<{ lang: Lang; setLang: (lang: Lang) => void }>({ lang: 'ar', setLang: () => undefined });
const useLang = () => useContext(LangContext);
const queryClient = new QueryClient({ defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } } });

const routeInfo: Record<string, { ar: string; fr: string; icon: LucideIcon; resource?: ResourceNameType }> = {
  '/': { ar: 'لوحة القيادة', fr: 'Tableau de bord', icon: LayoutDashboard },
  '/school': { ar: 'ملف المدرسة', fr: 'Fiche de l’école', icon: Building2 },
  '/candidates': { ar: 'المترشحون', fr: 'Candidats', icon: Users, resource: 'candidates' },
  '/instructors': { ar: 'المدربون', fr: 'Moniteurs', icon: UserRound, resource: 'instructors' },
  '/training': { ar: 'التكوين', fr: 'Formation', icon: GraduationCap, resource: 'trainingStages' },
  '/schedule': { ar: 'الجدول والحصص', fr: 'Planning et séances', icon: CalendarDays, resource: 'sessions' },
  '/payments': { ar: 'المدفوعات', fr: 'Paiements', icon: Banknote, resource: 'payments' },
  '/expenses': { ar: 'المصاريف', fr: 'Dépenses', icon: Wallet, resource: 'expenses' },
  '/reports': { ar: 'التقارير', fr: 'Rapports', icon: ChartNoAxesCombined },
  '/documents': { ar: 'الوثائق الرسمية', fr: 'Documents officiels', icon: FileText },
  '/graduates': { ar: 'الناجحون', fr: 'Diplômés', icon: BadgeCheck, resource: 'graduates' },
  '/accounting': { ar: 'المحاسبة والمالية', fr: 'Comptabilité et finances', icon: CircleDollarSign },
  '/hr': { ar: 'الموارد البشرية والأجور', fr: 'Ressources humaines et paie', icon: BriefcaseBusiness },
  '/profile': { ar: 'حسابي', fr: 'Mon compte', icon: UserRound },
  '/team': { ar: 'حسابات المستخدمين', fr: 'Comptes utilisateurs', icon: ShieldCheck, resource: 'users' },
};
const resourceTitles: Record<string, { ar: string; fr: string; subtitleAr: string; subtitleFr: string }> = {
  candidates: { ar: 'ملفات المترشحين', fr: 'Dossiers des candidats', subtitleAr: 'إدارة التسجيلات والملفات الإدارية للمترشحين', subtitleFr: 'Suivi des inscriptions et dossiers administratifs' },
  instructors: { ar: 'طاقم التدريب', fr: 'Équipe pédagogique', subtitleAr: 'بيانات المدربين وعقودهم المهنية', subtitleFr: 'Informations et contrats des moniteurs' },
  trainingStages: { ar: 'مراحل التكوين', fr: 'Étapes de formation', subtitleAr: 'متابعة تقدم المترشحين في مراحل التكوين', subtitleFr: 'Suivi de progression des candidats' },
  sessions: { ar: 'الحصص والجدول', fr: 'Séances et planning', subtitleAr: 'تنظيم حصص التدريب والمواعيد', subtitleFr: 'Organisation des séances et rendez-vous' },
  payments: { ar: 'تحصيل المدفوعات', fr: 'Encaissements', subtitleAr: 'متابعة دفعات المترشحين', subtitleFr: 'Suivi des versements des candidats' },
  expenses: { ar: 'المصاريف التشغيلية', fr: 'Dépenses opérationnelles', subtitleAr: 'تسجيل ومتابعة مصاريف المدرسة', subtitleFr: 'Enregistrement des dépenses de l’auto-école' },
  graduates: { ar: 'سجل الناجحين', fr: 'Registre des diplômés', subtitleAr: 'المترشحون الذين أتموا التكوين', subtitleFr: 'Candidats ayant terminé leur formation' },
  users: { ar: 'المستخدمون والصلاحيات', fr: 'Utilisateurs et accès', subtitleAr: 'الحسابات المخولة باستخدام النظام', subtitleFr: 'Comptes autorisés à utiliser le système' },
  accounts: { ar: 'دليل الحسابات', fr: 'Plan comptable', subtitleAr: 'حسابات النظام المحاسبي', subtitleFr: 'Comptes du système comptable' },
  journalEntries: { ar: 'دفتر اليومية', fr: 'Journal comptable', subtitleAr: 'قيود الحركة المالية المسجلة', subtitleFr: 'Écritures financières enregistrées' },
  employees: { ar: 'ملفات الموظفين', fr: 'Dossiers employés', subtitleAr: 'إدارة بيانات وملفات الموظفين', subtitleFr: 'Gestion des informations des employés' },
  payroll: { ar: 'كشف الأجور', fr: 'Registre de paie', subtitleAr: 'متابعة مستحقات وأداء أجور الموظفين', subtitleFr: 'Suivi des salaires et paiements' },
};

const groups = [
  { title: { ar: 'التسيير', fr: 'Pilotage' }, paths: ['/', '/school'] },
  { title: { ar: 'النشاط التعليمي', fr: 'Activité pédagogique' }, paths: ['/candidates', '/instructors', '/training', '/schedule', '/graduates'] },
  { title: { ar: 'الإدارة والمالية', fr: 'Administration et finances' }, paths: ['/payments', '/expenses', '/accounting', '/hr', '/reports', '/documents'] },
  { title: { ar: 'حسابي', fr: 'Mon compte' }, paths: ['/profile'] },
  { title: { ar: 'إدارة النظام', fr: 'Administration système' }, paths: ['/team'] },
];

function App() {
  const [lang, setLang] = useState<Lang>(() => (localStorage.getItem('medanic-language') as Lang) || 'ar');
  useEffect(() => {
    localStorage.setItem('medanic-language', lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
  }, [lang]);
  return <QueryClientProvider client={queryClient}><LangContext.Provider value={{ lang, setLang }}>
    <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}><Router /></WouterRouter>
  </LangContext.Provider></QueryClientProvider>;
}

function Router() {
  const [path, setLocation] = useLocation();
  const privatePath = path !== '/login' && path !== '/setup';
  const setup = useGetSetupStatus({ query: { retry: false } });
  const currentUser = useGetCurrentUser({ query: { retry: false } });
  useEffect(() => {
    if (!setup.data) return;
    if (setup.data.required && path !== '/setup') setLocation('/setup');
    else if (!setup.data.required && currentUser.data?.mustChangePassword && path !== '/profile') setLocation('/profile');
    else if (!setup.data.required && path === '/setup') setLocation(currentUser.data ? '/' : '/login');
    else if (!setup.data.required && path === '/login' && currentUser.data) setLocation('/');
    else if (!setup.data.required && privatePath && currentUser.isError) setLocation('/login');
  }, [setup.data, currentUser.data, currentUser.isError, path, privatePath, setLocation]);
  if (setup.isLoading || (privatePath && currentUser.isLoading)) {
    return <div className="app-shell grid min-h-[100dvh] place-items-center"><StateMessage loading /></div>;
  }
  if (setup.isError) {
    return <div className="app-shell grid min-h-[100dvh] place-items-center"><StateMessage error retry={() => setup.refetch()} /></div>;
  }
  if (setup.data?.required && path !== '/setup') {
    return <div className="app-shell grid min-h-[100dvh] place-items-center"><StateMessage loading /></div>;
  }
  if (!setup.data?.required && path === '/setup') {
    return <div className="app-shell grid min-h-[100dvh] place-items-center"><StateMessage loading /></div>;
  }
  if (privatePath && !currentUser.data) {
    return <div className="app-shell grid min-h-[100dvh] place-items-center"><StateMessage loading /></div>;
  }
  if (currentUser.data?.mustChangePassword && path !== '/profile') {
    return <div className="app-shell grid min-h-[100dvh] place-items-center"><StateMessage loading /></div>;
  }
  if (path === '/login' && currentUser.data) {
    return <div className="app-shell grid min-h-[100dvh] place-items-center"><StateMessage loading /></div>;
  }
  return <div className="app-shell">{privatePath ? <AppShell><RoutedPages /></AppShell> : <PublicPages />}</div>;
}

function RoutedPages() {
  return <Switch>
    <Route path="/" component={DashboardPage} />
    <Route path="/school" component={SchoolPage} />
    <Route path="/candidates/:id" component={CandidateDetailPage} />
    <Route path="/candidates" component={CandidatesPage} />
    <Route path="/instructors" component={InstructorsPage} />
    <Route path="/training" component={TrainingPage} />
    <Route path="/schedule" component={SchedulePage} />
    <Route path="/payments" component={PaymentsPage} />
    <Route path="/expenses" component={ExpensesPage} />
    <Route path="/reports" component={ReportsPage} />
    <Route path="/documents" component={DocumentsPage} />
    <Route path="/graduates" component={GraduatesPage} />
    <Route path="/accounting" component={AccountingPage} />
    <Route path="/hr" component={HrPage} />
    <Route path="/profile" component={ProfilePage} />
    <Route path="/team" component={TeamPage} />
    <Route component={NotFound} />
  </Switch>;
}

function PublicPages() {
  return <Switch><Route path="/login" component={LoginPage} /><Route path="/setup" component={SetupPage} /><Route component={NotFound} /></Switch>;
}

function AppShell({ children }: { children: ReactNode }) {
  const [path] = useLocation();
  const { lang, setLang } = useLang();
  const [mobileOpen, setMobileOpen] = useState(false);
  const current = routeInfo[path] || routeInfo['/'];
  const user = useCurrentUser();
  const health = useHealthCheck({ query: { refetchInterval: 60000 } });
  return <div className="flex min-h-[100dvh]">
    {mobileOpen && <button aria-label={lang === 'ar' ? 'إغلاق القائمة' : 'Fermer le menu'} onClick={() => setMobileOpen(false)} className="fixed inset-0 z-30 bg-[#12263a]/45 md:hidden" data-testid="button-close-menu" />}
    <aside className={`sidebar fixed inset-y-0 z-40 flex w-[266px] flex-col transition-transform duration-200 md:sticky md:top-0 md:h-[100dvh] md:translate-x-0 ${mobileOpen ? 'translate-x-0 start-0' : 'rtl:translate-x-full ltr:-translate-x-full md:translate-x-0'}`}>
      <div className="flex h-[82px] shrink-0 items-center gap-3 border-b border-white/10 px-5">
        <img src={logo} alt="شعار مدرسة ميدانيك" className="h-[48px] w-[48px] rounded-full bg-[#f7f4ec] object-cover" data-testid="img-medanic-logo" />
        <div className="leading-tight"><div className="text-[15px] font-bold tracking-wide">MEDANIC</div><div className="mt-1 text-[11px] text-[#bac5cf]">إدارة مدرسة السياقة</div></div>
        <button className="ms-auto rounded-lg p-2 text-white/70 md:hidden" onClick={() => setMobileOpen(false)} aria-label="إغلاق" data-testid="button-close-sidebar"><X size={17} /></button>
      </div>
      <div className="sidebar-scroll flex-1 overflow-y-auto px-3 py-5">
        {groups.map((group) => <div key={group.title.ar} className="mb-5">
          <p className="mb-2 px-3 text-[10px] font-semibold tracking-[.11em] text-[#9dabb9]">{group.title[lang]}</p>
          <nav className="space-y-1" aria-label={group.title[lang]}>
            {group.paths.map((href) => {
              const item = routeInfo[href]; const active = path === href || (href === '/candidates' && path.startsWith('/candidates/')); const Icon = item.icon;
              return <Link href={href} key={href} onClick={() => setMobileOpen(false)} data-testid={`link-nav-${href.replaceAll('/', '') || 'dashboard'}`} className={`nav-link flex min-h-10 items-center gap-3 rounded-lg px-3 text-[13px] ${active ? 'bg-[#f0d7ad] font-semibold text-[#193047]' : 'text-[#d5dce2] hover:bg-white/8 hover:text-white'}`}>
                <Icon size={17} strokeWidth={1.8} /><span className="flex-1">{item[lang]}</span>{active && <span className="h-1.5 w-1.5 rounded-full bg-[#b6792c]" />}
              </Link>;
            })}
          </nav>
        </div>)}
      </div>
      <div className="border-t border-white/10 p-3">
        <div className="mb-2 flex items-center gap-3 rounded-lg bg-white/[.06] px-3 py-3">
          <div className="grid h-9 w-9 place-items-center rounded-full bg-[#e5c58f] text-sm font-bold text-[#1b334a]">{user.name?.slice(0, 1) || 'م'}</div>
          <div className="min-w-0 flex-1"><div className="truncate text-xs font-semibold">{user.name || (lang === 'ar' ? 'مستخدم النظام' : 'Utilisateur')}</div><div className="mt-1 text-[10px] text-[#aeb9c3]">{user.loading ? (lang === 'ar' ? 'جارٍ التحقق…' : 'Vérification…') : user.name ? (lang === 'ar' ? 'حساب مخول' : 'Compte autorisé') : (lang === 'ar' ? 'جلسة غير متصلة' : 'Session hors ligne')}</div></div>
          <LogoutButton />
        </div>
        <div className="flex items-center justify-between px-3 text-[10px] text-[#9dabb9]"><span>MEDANIC ERP</span><span className="flex items-center gap-1.5"><i className={`h-1.5 w-1.5 rounded-full ${health.isSuccess ? 'bg-[#79b48a]' : health.isError ? 'bg-[#c37a70]' : 'bg-[#cfb16f]'}`} />{health.isSuccess ? (lang === 'ar' ? 'متصل' : 'En ligne') : health.isError ? (lang === 'ar' ? 'غير متاح' : 'Indisponible') : (lang === 'ar' ? 'جارٍ التحقق' : 'Vérification')}</span></div>
      </div>
    </aside>
    <div className="min-w-0 flex-1">
      <header className="sticky top-0 z-20 flex h-[68px] items-center justify-between border-b border-[#e5dfd3] bg-[#f8f6ef]/95 px-4 backdrop-blur md:px-8">
        <div className="flex items-center gap-3">
          <button onClick={() => setMobileOpen(true)} className="rounded-lg p-2 text-[#20374d] hover:bg-[#ece6d9] md:hidden" aria-label="فتح القائمة" data-testid="button-open-menu"><Menu size={20} /></button>
          <div><p className="text-[11px] text-[#898b86]">{lang === 'ar' ? 'مدرسة تعليم السياقة' : 'École de conduite'} <span className="mx-1 text-[#c1b8a8]">/</span> <span className="font-medium text-[#455363]">{current[lang]}</span></p><h1 className="mt-0.5 text-[15px] font-bold text-[#1d344a] md:text-base">{current[lang]}</h1></div>
        </div>
        <div className="flex items-center gap-2 md:gap-4">
          <div className="hidden items-center gap-2 rounded-lg border border-[#e4ded2] bg-[#fffdf8] px-3 py-2 text-xs text-[#6d7479] sm:flex"><CalendarDays size={14} className="text-[#b27c36]" /><span>{new Intl.DateTimeFormat(lang === 'ar' ? 'ar-DZ' : 'fr-DZ', { dateStyle: 'medium' }).format(new Date())}</span></div>
          <button onClick={() => setLang(lang === 'ar' ? 'fr' : 'ar')} className="flex items-center gap-2 rounded-lg border border-[#e4ded2] bg-[#fffdf8] px-3 py-2 text-xs font-semibold text-[#31475a] hover:border-[#c9ad7c]" data-testid="button-language"><Languages size={15} /><span>{lang === 'ar' ? 'FR' : 'عربي'}</span></button>
        </div>
      </header>
      <main className="page-enter mx-auto max-w-[1500px] p-4 md:p-7 lg:p-9">{children}</main>
    </div>
  </div>;
}

function useCurrentUser() {
  const { data, isLoading } = useQuerySafeUser();
  return { name: data?.fullName, loading: isLoading };
}
function useQuerySafeUser() {
  // Current-user state is supplied by the authentication API; a missing session is an honest signed-out state.
  return useGetCurrentUser({ query: { retry: false } });
}
function LogoutButton() {
  const { lang } = useLang(); const client = useQueryClient(); const mutation = useMutation(getLogoutMutationOptions()); const [, setLocation] = useLocation();
  return <button title={lang === 'ar' ? 'تسجيل الخروج' : 'Déconnexion'} onClick={() => mutation.mutate(undefined, { onSuccess: () => { client.removeQueries(); setLocation('/login'); } })} disabled={mutation.isPending} className="rounded-md p-2 text-[#aeb9c3] hover:bg-white/10 hover:text-white disabled:opacity-50" data-testid="button-logout"><LogOut size={16} /></button>;
}

function PageIntro({ title, subtitle, actions }: { title: string; subtitle: string; actions?: ReactNode }) {
  return <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"><div><div className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[.13em] text-[#a6783c]"><span className="h-px w-5 bg-[#c58d43]" /> MEDANIC • ERP</div><h2 className="text-[25px] font-bold tracking-[-.03em] text-[#1c3349] md:text-[29px]">{title}</h2><p className="mt-1.5 text-sm text-[#777c7d]">{subtitle}</p></div>{actions && <div className="flex items-center gap-2">{actions}</div>}</div>;
}
function Button({ children, onClick, variant = 'primary', disabled, testId, type = 'button' }: { children: ReactNode; onClick?: () => void; variant?: 'primary' | 'outline' | 'danger' | 'ghost'; disabled?: boolean; testId: string; type?: 'button' | 'submit' }) {
  const style = variant === 'primary' ? 'bg-[#203a52] text-white hover:bg-[#2b4a66]' : variant === 'danger' ? 'bg-[#a83d37] text-white hover:bg-[#91332e]' : variant === 'outline' ? 'border border-[#d9d2c6] bg-[#fffdf8] text-[#33485a] hover:border-[#bd9a63]' : 'text-[#4c5964] hover:bg-[#efeae0]';
  return <button type={type} onClick={onClick} disabled={disabled} data-testid={testId} className={`inline-flex min-h-10 items-center justify-center gap-2 rounded-lg px-3.5 text-[12px] font-semibold transition disabled:cursor-not-allowed disabled:opacity-55 ${style}`}>{children}</button>;
}
function StateMessage({ loading, error, empty, retry }: { loading?: boolean; error?: boolean; empty?: boolean; retry?: () => void }) {
  const { lang } = useLang();
  if (loading) return <div className="space-y-3 p-5" aria-label={lang === 'ar' ? 'جارٍ التحميل' : 'Chargement'}>{[0, 1, 2].map((i) => <div key={i} className="h-12 animate-pulse rounded-lg bg-[#eee9df]" />)}</div>;
  if (error) return <div className="flex min-h-[220px] flex-col items-center justify-center gap-3 p-8 text-center"><div className="grid h-11 w-11 place-items-center rounded-full bg-[#f8e8e5] text-[#a83d37]"><AlertCircle size={20} /></div><p className="text-sm font-semibold text-[#364b5e]">{lang === 'ar' ? 'تعذر تحميل البيانات' : 'Impossible de charger les données'}</p><p className="text-xs text-[#838783]">{lang === 'ar' ? 'تحقق من الاتصال ثم أعد المحاولة.' : 'Vérifiez la connexion puis réessayez.'}</p>{retry && <Button variant="outline" onClick={retry} testId="button-retry"><RotateCcw size={14} />{lang === 'ar' ? 'إعادة المحاولة' : 'Réessayer'}</Button>}</div>;
  if (empty) return <div className="flex min-h-[220px] flex-col items-center justify-center gap-3 p-8 text-center"><div className="grid h-12 w-12 place-items-center rounded-2xl bg-[#f0eadf] text-[#9b7948]"><ClipboardList size={21} /></div><p className="text-sm font-semibold text-[#364b5e]">{lang === 'ar' ? 'لا توجد سجلات لعرضها' : 'Aucun enregistrement à afficher'}</p><p className="max-w-xs text-xs leading-5 text-[#878982]">{lang === 'ar' ? 'ستظهر البيانات هنا عند إضافتها إلى النظام.' : 'Les données apparaîtront ici dès leur ajout au système.'}</p></div>;
  return null;
}

function DashboardPage() {
  const { lang } = useLang(); const dashboard = useGetDashboard({ language: lang });
  const summary = dashboard.data;
  const cards = summary ? [
    { label: { ar: 'المترشحون', fr: 'Candidats' }, value: summary.candidateCount, icon: Users, tint: 'sand' },
    { label: { ar: 'المدربون', fr: 'Moniteurs' }, value: summary.instructorCount, icon: UserRound, tint: 'blue' },
    { label: { ar: 'حصص اليوم', fr: 'Séances du jour' }, value: summary.todaySessions, icon: CalendarDays, tint: 'green' },
    { label: { ar: 'تحصيل الشهر', fr: 'Recettes du mois' }, value: money(summary.paidThisMonth, lang), icon: ArrowDownLeft, tint: 'gold' },
    { label: { ar: 'مصاريف الشهر', fr: 'Dépenses du mois' }, value: money(summary.expensesThisMonth, lang), icon: ArrowUpRight, tint: 'rose' },
  ] : [];
  return <div>
    <PageIntro title={lang === 'ar' ? 'صباح النشاط، إليك ملخص المدرسة' : 'Bonjour, voici le point de l’école'} subtitle={lang === 'ar' ? 'نظرة يومية على التسجيلات، الحصص والحركة المالية.' : 'Un aperçu quotidien des inscriptions, séances et mouvements financiers.'} actions={<Link href="/candidates" className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-[#203a52] px-3.5 text-[12px] font-semibold text-white no-underline transition hover:bg-[#2b4a66]" data-testid="button-new-candidate"><Plus size={15} />{lang === 'ar' ? 'تسجيل مترشح' : 'Inscrire un candidat'}</Link>} />
    {dashboard.isLoading ? <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-5">{[0,1,2,3,4].map(i => <div key={i} className="h-[124px] animate-pulse rounded-xl bg-[#e9e4d9]" />)}</div> : dashboard.isError ? <div className="surface mb-6"><StateMessage error retry={() => dashboard.refetch()} /></div> : <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-5">{cards.map((card) => <MetricCard key={card.label.ar} {...card} lang={lang} />)}</div>}
    <div className="grid gap-5 xl:grid-cols-[1.4fr_.8fr]">
      <section className="surface overflow-hidden">
        <div className="flex items-center justify-between border-b border-[#eee8dd] px-5 py-4"><div><h3 className="text-sm font-bold text-[#20374d]">{lang === 'ar' ? 'آخر النشاطات' : 'Activité récente'}</h3><p className="mt-1 text-[11px] text-[#858984]">{lang === 'ar' ? 'الحركة المسجلة في المدرسة' : 'Mouvements enregistrés dans l’école'}</p></div><Activity size={18} className="text-[#bb873e]" /></div>
        {dashboard.isLoading ? <StateMessage loading /> : dashboard.isError ? <StateMessage error retry={() => dashboard.refetch()} /> : !summary?.recentActivity?.length ? <StateMessage empty /> : <div className="divide-y divide-[#eee8dd]">{summary.recentActivity.map((row, i) => <div key={row.id} className="flex items-center gap-3 px-5 py-3.5" data-testid={`activity-row-${row.id}`}><div className="grid h-9 w-9 place-items-center rounded-full bg-[#f1ece1] text-[#9d753d]"><Clock3 size={16} /></div><div className="min-w-0 flex-1"><div className="truncate text-xs font-semibold text-[#33495c]">{recordTitle(row)}</div><div className="mt-1 text-[10px] text-[#858984]">{recordDate(row) || (lang === 'ar' ? 'نشاط مسجل' : 'Activité enregistrée')}</div></div><span className="font-mono text-[10px] text-[#9d9a90]">#{row.id}</span></div>)}</div>}
      </section>
      <section className="surface relative overflow-hidden p-5 md:p-6">
        <div className="absolute -end-8 -top-8 h-36 w-36 rounded-full border-[26px] border-[#f2eadc]" /><div className="relative"><div className="mb-5 flex items-center gap-2"><div className="grid h-9 w-9 place-items-center rounded-xl bg-[#203a52] text-[#eed4ab]"><Gauge size={17} /></div><div><h3 className="text-sm font-bold text-[#20374d]">{lang === 'ar' ? 'مساحات العمل' : 'Accès rapides'}</h3><p className="mt-1 text-[10px] text-[#858984]">{lang === 'ar' ? 'انتقل مباشرة إلى مهامك اليومية' : 'Accédez rapidement à vos tâches'}</p></div></div>
          <div className="space-y-2">{['/schedule', '/payments', '/documents', '/reports'].map((route) => { const item = routeInfo[route]; const Icon = item.icon; return <Link href={route} key={route} className="group flex items-center gap-3 rounded-lg border border-[#eee8dd] bg-[#fffdf9] px-3.5 py-3 text-xs font-semibold text-[#34495b] transition hover:border-[#d9c7a8] hover:bg-[#f9f4e9]"><Icon size={16} className="text-[#a8793c]" /><span className="flex-1">{item[lang]}</span>{lang === 'ar' ? <ChevronLeft size={15} className="text-[#aaa399] transition group-hover:-translate-x-0.5" /> : <ChevronRight size={15} className="text-[#aaa399] transition group-hover:translate-x-0.5" />}</Link>; })}</div>
        </div>
      </section>
    </div>
  </div>;
}
function MetricCard({ label, value, icon: Icon, tint }: { label: { ar: string; fr: string }; value: unknown; icon: LucideIcon; tint: string; lang: Lang }) {
  const colors: Record<string, string> = { sand: 'bg-[#f4ecdc] text-[#9a7239]', blue: 'bg-[#e6edf2] text-[#395b75]', green: 'bg-[#e6eee7] text-[#4d765e]', gold: 'bg-[#f7edd9] text-[#9a7239]', rose: 'bg-[#f5e9e5] text-[#a35b4f]' };
  const { lang } = useLang();
  return <article className="surface min-h-[124px] p-4 transition hover:-translate-y-0.5 hover:shadow-md" data-testid={`metric-${label.ar}`}><div className="mb-4 flex items-start justify-between"><span className="text-[11px] font-medium text-[#7a807f]">{label[lang]}</span><span className={`grid h-8 w-8 place-items-center rounded-lg ${colors[tint]}`}><Icon size={16} /></span></div><div className="truncate text-[21px] font-bold tracking-[-.04em] text-[#20374d]" dir="auto">{String(value ?? '—')}</div></article>;
}

function ResourcePage({ resource }: { resource: ResourceNameType }) {
  const { lang } = useLang(); const client = useQueryClient(); const config = resourceTitles[resource];
  const [search, setSearch] = useState(''); const [editing, setEditing] = useState<ResourceRecord | null>(null); const [open, setOpen] = useState(false);
  const params = useMemo(() => ({ language: lang, ...(search.trim() ? { search: search.trim() } : {}) }), [lang, search]);
  const query = useListResourceRecords(resource, params);
  const fields = query.data?.fields || [];
  const create = useMutation(getCreateResourceRecordMutationOptions());
  const update = useMutation(getUpdateResourceRecordMutationOptions());
  const remove = useMutation(getDeleteResourceRecordMutationOptions());
  const reversal = useMutation(getReverseJournalEntryMutationOptions());
  const refresh = () => client.invalidateQueries({ queryKey: getListResourceRecordsQueryKey(resource) });
  const saving = create.isPending || update.isPending;
  const canCreate = resource !== 'graduates';
  const submit = (payload: Record<string, unknown>) => {
    const onSuccess = () => { setOpen(false); setEditing(null); refresh(); };
    if (editing) update.mutate({ resource, id: editing.id, data: payload }, { onSuccess });
    else create.mutate({ resource, data: payload }, { onSuccess });
  };
  const del = (record: ResourceRecord) => {
    if (window.confirm(lang === 'ar' ? 'هل تريد حذف هذا السجل؟' : 'Supprimer cet enregistrement ?')) remove.mutate({ resource, id: record.id }, { onSuccess: refresh });
  };
  const showForm = (record?: ResourceRecord) => { setEditing(record || null); setOpen(true); };
  const title = lang === 'ar' ? config.ar : config.fr;
  const displayFields = fields.filter(f => !f.hidden && f.name !== 'id').slice(0, 4);
  return <div>
    <PageIntro title={title} subtitle={lang === 'ar' ? config.subtitleAr : config.subtitleFr} actions={canCreate ? <Button onClick={() => showForm()} testId={`button-add-${resource}`}><Plus size={15} />{lang === 'ar' ? 'إضافة سجل' : 'Ajouter'}</Button> : null} />
    <section className="surface overflow-hidden">
      <div className="flex flex-col gap-3 border-b border-[#eee8dd] p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="text-xs text-[#777e80]"><strong className="text-[#20374d]">{query.data?.total ?? '—'}</strong> {lang === 'ar' ? 'سجل' : 'enregistrements'}</div>
        <label className="relative block w-full sm:max-w-[280px]"><Search size={15} className="absolute start-3 top-1/2 -translate-y-1/2 text-[#99978f]" /><input className="field-control ps-9 text-xs" value={search} onChange={e => setSearch(e.target.value)} placeholder={lang === 'ar' ? 'بحث في السجلات…' : 'Rechercher…'} aria-label={lang === 'ar' ? 'بحث' : 'Recherche'} data-testid={`input-search-${resource}`} /></label>
      </div>
      {query.isLoading ? <StateMessage loading /> : query.isError ? <StateMessage error retry={() => query.refetch()} /> : !query.data?.items.length ? <StateMessage empty /> : <div className="overflow-x-auto">
        <table className="w-full min-w-[680px] text-start"><thead><tr className="bg-[#f6f3ec] text-[10px] font-semibold text-[#7e817c]">{['#', ...displayFields.map(f => f.label), ...(resource === 'journalEntries' || resource === 'payroll' ? [lang === 'ar' ? 'الإجراء' : 'Action'] : []), lang === 'ar' ? 'إجراءات' : 'Actions'].map((head, i) => <th key={`${head}-${i}`} className="px-4 py-3 text-start">{head}</th>)}</tr></thead><tbody className="divide-y divide-[#f0ebe2]">
           {query.data.items.map((row) => { const rowLocked = resource === 'graduates' || resource === 'journalEntries' || (resource === 'payroll' && row.status === 'paid'); return <tr key={row.id} className="table-row" data-testid={`row-${resource}-${row.id}`}><td className="px-4 py-3 font-mono text-[10px] text-[#92958f]">{row.id}</td>{displayFields.map(field => <td key={field.name} className="max-w-[230px] px-4 py-3 text-xs text-[#34495a]" dir="auto"><span className="block truncate">{formatField(row[field.name], field)}</span></td>)}
             {resource === 'journalEntries' && <td className="px-4 py-3"><Button variant="outline" disabled={Boolean(row.isReversed) || reversal.isPending} onClick={() => { if (window.confirm(lang === 'ar' ? 'عكس هذا القيد المحاسبي؟' : 'Contrepasser cette écriture ?')) reversal.mutate({ id: row.id }, { onSuccess: refresh }); }} testId={`button-reverse-${row.id}`}><RotateCcw size={13} />{lang === 'ar' ? 'عكس القيد' : 'Contrepasser'}</Button></td>}
            {resource === 'payroll' && <td className="px-4 py-3"><PayrollAction id={row.id} paid={Boolean(row.paidAt || row.status === 'paid')} onDone={refresh} /></td>}
             <td className="px-4 py-3">{rowLocked ? <span className="text-[10px] text-[#9b9b92]">—</span> : <div className="flex gap-1"><button onClick={() => showForm(row)} className="rounded-md p-2 text-[#637384] hover:bg-[#eae6de] hover:text-[#203a52]" aria-label={lang === 'ar' ? 'تعديل' : 'Modifier'} data-testid={`button-edit-${resource}-${row.id}`}><Pencil size={14} /></button><button onClick={() => del(row)} className="rounded-md p-2 text-[#a16b62] hover:bg-[#f7e8e5]" aria-label={lang === 'ar' ? 'حذف' : 'Supprimer'} data-testid={`button-delete-${resource}-${row.id}`}><Trash2 size={14} /></button></div>}</td></tr>})}
        </tbody></table>
      </div>}
    </section>
    {(create.isError || update.isError || remove.isError || reversal.isError) && <p role="alert" className="mt-3 text-xs text-[#a83d37]" data-testid="status-resource-error">{lang === 'ar' ? 'لم يتم حفظ التغيير. يرجى مراجعة البيانات والمحاولة مجدداً.' : 'La modification n’a pas été enregistrée. Vérifiez les données puis réessayez.'}</p>}
    {open && <RecordModal resource={resource} fields={fields} initial={editing} saving={saving} error={create.isError || update.isError} onClose={() => setOpen(false)} onSubmit={submit} />}
  </div>;
}
function PayrollAction({ id, paid, onDone }: { id: number; paid: boolean; onDone: () => void }) {
  const { lang } = useLang(); const client = useQueryClient(); const mutation = useMutation(getPayPayrollItemMutationOptions());
  const act = () => mutation.mutate({ id }, { onSuccess: () => { onDone(); client.invalidateQueries({ queryKey: getListResourceRecordsQueryKey('payroll') }); } });
  return <Button variant={paid ? 'ghost' : 'outline'} disabled={paid || mutation.isPending} onClick={act} testId={`button-payroll-${id}`}><Check size={13} />{paid ? (lang === 'ar' ? 'تم الدفع' : 'Payé') : mutation.isPending ? '…' : (lang === 'ar' ? 'دفع الأجر' : 'Payer')}</Button>;
}
function RecordModal({ resource, fields, initial, saving, error, onClose, onSubmit }: { resource: ResourceNameType; fields: FieldDefinition[]; initial: ResourceRecord | null; saving: boolean; error: boolean; onClose: () => void; onSubmit: (data: Record<string, unknown>) => void }) {
  const { lang } = useLang();
  const editable = fields.filter(f => !f.hidden && !f.readOnly && f.name !== 'id');
  const defaults = Object.fromEntries(editable.map(field => [field.name, formFieldDefault(field, initial?.[field.name])]));
  const form = useForm<Record<string, unknown>>({ defaultValues: defaults });
  useEffect(() => { form.reset(defaults); }, [initial?.id]);
  return <div className="fixed inset-0 z-50 flex items-end justify-center bg-[#152a3d]/45 p-0 backdrop-blur-[2px] sm:items-center sm:p-5" role="presentation" onMouseDown={e => { if (e.target === e.currentTarget) onClose(); }}>
    <section role="dialog" aria-modal="true" aria-labelledby="record-form-title" className="max-h-[92dvh] w-full max-w-[760px] overflow-hidden rounded-t-2xl bg-[#fffdf8] shadow-2xl sm:rounded-2xl">
      <div className="flex items-center justify-between border-b border-[#eae4d9] px-5 py-4"><div><h3 id="record-form-title" className="text-base font-bold text-[#20374d]">{initial ? (lang === 'ar' ? 'تعديل سجل' : 'Modifier') : (lang === 'ar' ? 'إضافة سجل جديد' : 'Nouvel enregistrement')}</h3><p className="mt-1 text-[11px] text-[#888a84]">{lang === 'ar' ? 'تُعرض الحقول حسب تعريف النظام' : 'Champs définis par le système'}</p></div><button onClick={onClose} className="rounded-lg p-2 text-[#7b817f] hover:bg-[#f0ece3]" aria-label={lang === 'ar' ? 'إغلاق' : 'Fermer'} data-testid="button-close-form"><X size={17} /></button></div>
      <Form {...form}><form onSubmit={form.handleSubmit(onSubmit)} className="max-h-[calc(92dvh-72px)] overflow-y-auto">
        <div className="grid gap-x-4 gap-y-4 p-5 sm:grid-cols-2">
          {editable.map(field => <FieldControl key={field.name} field={field} form={form} lang={lang} />)}
          {!editable.length && <p className="col-span-2 py-8 text-center text-sm text-[#777e80]">{lang === 'ar' ? 'لا توجد حقول قابلة للتحرير في تعريف هذا المورد.' : 'Aucun champ modifiable défini pour cette ressource.'}</p>}
        </div>
        {error && <p className="mx-5 rounded-lg bg-[#f8e8e5] px-3 py-2 text-xs text-[#a83d37]" role="alert">{lang === 'ar' ? 'تعذر حفظ السجل. تحقق من الحقول المطلوبة.' : 'Enregistrement impossible. Vérifiez les champs requis.'}</p>}
        <div className="sticky bottom-0 flex justify-end gap-2 border-t border-[#eae4d9] bg-[#fffdf8] px-5 py-4"><Button variant="outline" onClick={onClose} testId="button-cancel-form">{lang === 'ar' ? 'إلغاء' : 'Annuler'}</Button><Button type="submit" disabled={saving} testId="button-submit-form">{saving && <LoaderCircle size={14} className="animate-spin" />}{saving ? (lang === 'ar' ? 'جارٍ الحفظ' : 'Enregistrement…') : (lang === 'ar' ? 'حفظ السجل' : 'Enregistrer')}</Button></div>
      </form></Form>
    </section>
  </div>;
}
function FieldControl({ field, form, lang }: { field: FieldDefinition; form: ReturnType<typeof useForm<Record<string, unknown>>>; lang: Lang }) {
  const value = form.register(field.name, { required: field.required ? (lang === 'ar' ? 'هذا الحقل مطلوب' : 'Ce champ est requis') : false });
  const error = form.formState.errors[field.name];
  const label = field.label || field.name;
  const type = field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : field.type === 'password' ? 'password' : field.type === 'email' ? 'email' : 'text';
  if (field.type === 'permissions') {
    const selected = (form.watch(field.name) as string[] | undefined) || [];
    return <fieldset className="sm:col-span-2 rounded-lg border border-[#ded8cc] p-3" data-testid={`field-${field.name}`}><legend className="px-1 text-xs font-medium text-[#455565]">{label}</legend><div className="grid gap-2 sm:grid-cols-2">{(field.options || []).map(option => <label key={option.value} className="flex items-center gap-2 rounded-md bg-[#f8f5ee] px-3 py-2 text-[11px] text-[#536170]"><input type="checkbox" checked={selected.includes(option.value)} onChange={event => { const next = event.target.checked ? [...selected, option.value] : selected.filter(item => item !== option.value); form.setValue(field.name, next, { shouldDirty: true, shouldValidate: true }); }} className="h-4 w-4 accent-[#203a52]" /><span>{option.label}</span></label>)}</div>{error && <span className="mt-1 block text-[10px] text-[#a83d37]">{String(error.message || '')}</span>}</fieldset>;
  }
  return <label className={`${field.type === 'textarea' ? 'sm:col-span-2' : ''} block text-xs font-medium text-[#455565]`} data-testid={`field-${field.name}`}><span className="mb-1.5 block">{label}{field.required && <span className="ms-1 text-[#a83d37]">*</span>}</span>
    {field.type === 'textarea' ? <textarea {...value} className="field-control min-h-[88px] py-2.5" placeholder={label} /> : field.type === 'select' ? <select {...value} multiple={field.multiple} className="field-control" defaultValue={field.multiple ? (form.getValues(field.name) as string[] ?? []) : String(form.getValues(field.name) ?? '')}>{!field.multiple && <option value="">{lang === 'ar' ? 'اختر…' : 'Sélectionner…'}</option>}{(field.options || []).map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select> : field.type === 'boolean' ? <span className="flex h-[42px] items-center gap-2 rounded-lg border border-[#ded8cc] bg-[#fffefa] px-3"><input {...value} type="checkbox" defaultChecked={Boolean(form.getValues(field.name))} className="h-4 w-4 accent-[#203a52]" /><span className="text-xs text-[#6c7477]">{lang === 'ar' ? 'نعم' : 'Oui'}</span></span> : <input {...value} type={type} step={field.type === 'number' ? 'any' : undefined} className="field-control" placeholder={label} />}
    {error && <span className="mt-1 block text-[10px] text-[#a83d37]">{String(error.message || '')}</span>}
  </label>;
}

function formFieldDefault(field: FieldDefinition, current: unknown) {
  if (field.type === 'permissions') {
    if (Array.isArray(current)) return current;
    if (current && typeof current === 'object') {
      return Object.entries(current as Record<string, unknown>)
        .filter(([, enabled]) => Boolean(enabled))
        .map(([permission]) => permission);
    }
    return [];
  }
  if (field.name === 'registrationDate' && !current) {
    const today = new Date();
    today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
    return today.toISOString().slice(0, 10);
  }
  return current ?? (field.type === 'boolean' ? false : field.multiple ? [] : '');
}

function SchoolPage() {
  const { lang } = useLang(); const client = useQueryClient(); const query = useGetSchool();
  const mutation = useMutation(getUpdateSchoolMutationOptions());
  const labels: Record<string, { ar: string; fr: string }> = {
    name: { ar: 'اسم المدرسة', fr: 'Nom de l’école' }, commercialRegister: { ar: 'السجل التجاري', fr: 'Registre de commerce' }, accreditationNumber: { ar: 'رقم الاعتماد', fr: 'Numéro d’agrément' }, nif: { ar: 'الرقم الجبائي NIF', fr: 'NIF' }, nis: { ar: 'رقم الإحصاء NIS', fr: 'NIS' }, articleNumber: { ar: 'رقم المادة', fr: 'Numéro d’article' }, address: { ar: 'العنوان', fr: 'Adresse' }, phone: { ar: 'الهاتف', fr: 'Téléphone' }, wilaya: { ar: 'الولاية', fr: 'Wilaya' }, managerName: { ar: 'اسم المدير', fr: 'Nom du directeur' }, accreditationDate: { ar: 'تاريخ الاعتماد', fr: 'Date d’agrément' }, addressCommune: { ar: 'البلدية', fr: 'Commune' }, addressDaira: { ar: 'الدائرة', fr: 'Daïra' }, ownerName: { ar: 'اسم المالك', fr: 'Nom du propriétaire' }, ownerBirthDate: { ar: 'تاريخ ميلاد المالك', fr: 'Date de naissance du propriétaire' }, ownerBirthPlace: { ar: 'مكان الميلاد', fr: 'Lieu de naissance' }, ownerEmail: { ar: 'البريد الإلكتروني', fr: 'E-mail' }, representativeName: { ar: 'اسم الممثل', fr: 'Nom du représentant' }, representativeBirthDate: { ar: 'تاريخ ميلاد الممثل', fr: 'Date de naissance du représentant' }, representativeBirthPlace: { ar: 'مكان الميلاد', fr: 'Lieu de naissance' },
  };
  const schema = z.object(Object.fromEntries(Object.keys(labels).map(k => [k, z.string().optional()])) as Record<string, z.ZodTypeAny>);
  const form = useForm<Record<string, string>>({ resolver: zodResolver(schema), defaultValues: {} });
  useEffect(() => { if (query.data) form.reset(Object.fromEntries(Object.keys(labels).map(k => [k, String(query.data?.[k as keyof typeof query.data] ?? '')]))); }, [query.data]);
  const submit = form.handleSubmit(data => mutation.mutate({ data }, { onSuccess: () => client.invalidateQueries({ queryKey: getGetSchoolQueryKey() }) }));
  return <div><PageIntro title={lang === 'ar' ? 'ملف المدرسة والاعتماد' : 'École et agrément'} subtitle={lang === 'ar' ? 'البيانات القانونية والإدارية المعتمدة للمؤسسة.' : 'Informations légales et administratives de l’établissement.'} />
    <div className="surface overflow-hidden">
      <div className="flex items-center gap-3 border-b border-[#eee8dd] px-5 py-4"><div className="grid h-9 w-9 place-items-center rounded-lg bg-[#e9edf0] text-[#36556f]"><Building2 size={17} /></div><div><h3 className="text-sm font-bold text-[#20374d]">{lang === 'ar' ? 'معلومات المؤسسة' : 'Informations de l’établissement'}</h3><p className="mt-1 text-[10px] text-[#858984]">{lang === 'ar' ? 'تُستخدم هذه البيانات في الوثائق الرسمية' : 'Ces données sont utilisées dans les documents officiels'}</p></div></div>
      {query.isLoading ? <StateMessage loading /> : query.isError ? <StateMessage error retry={() => query.refetch()} /> : <form onSubmit={submit}><div className="grid gap-4 p-5 md:grid-cols-2 xl:grid-cols-3">{Object.entries(labels).map(([key, label]) => <label key={key} className={key === 'address' ? 'md:col-span-2' : ''}><span className="mb-1.5 block text-xs font-medium text-[#455565]">{label[lang]}</span><input type={key.toLowerCase().includes('date') ? 'date' : key === 'ownerEmail' ? 'email' : 'text'} {...form.register(key)} className="field-control" data-testid={`input-school-${key}`} /></label>)}</div>
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-[#eee8dd] px-5 py-4"><span className="text-[10px] text-[#868984]">{lang === 'ar' ? 'يُرجى الحفاظ على مطابقة بيانات الاعتماد مع الوثائق الأصلية.' : 'Les informations d’agrément doivent correspondre aux documents officiels.'}</span><Button type="submit" disabled={mutation.isPending} testId="button-save-school">{mutation.isPending && <LoaderCircle size={14} className="animate-spin" />}{mutation.isPending ? (lang === 'ar' ? 'جارٍ الحفظ' : 'Enregistrement…') : (lang === 'ar' ? 'حفظ الملف' : 'Enregistrer')}</Button></div>
        {mutation.isError && <p className="px-5 pb-4 text-xs text-[#a83d37]" role="alert">{lang === 'ar' ? 'تعذر حفظ معلومات المدرسة.' : 'Impossible d’enregistrer les informations.'}</p>}</form>}
    </div>
  </div>;
}

function CandidateDetailPage() {
  const { id } = useParams<{ id: string }>(); const { lang } = useLang(); const num = Number(id);
  const query = useGetResourceRecord('candidates', num, { query: { enabled: Number.isFinite(num), queryKey: getGetResourceRecordQueryKey('candidates', num) } });
  const definitions = useListResourceRecords('candidates', { language: lang });
  const labels = new Map((definitions.data?.fields || []).map(field => [field.name, field.label]));
  return <div><PageIntro title={lang === 'ar' ? 'ملف المترشح' : 'Dossier candidat'} subtitle={lang === 'ar' ? 'عرض المعلومات المسجلة في النظام' : 'Informations enregistrées dans le système'} actions={<Link href="/candidates" className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg border border-[#d9d2c6] bg-[#fffdf8] px-3.5 text-[12px] font-semibold text-[#33485a] no-underline transition hover:border-[#bd9a63]" data-testid="button-back-candidates"><ArrowRight size={14} />{lang === 'ar' ? 'قائمة المترشحين' : 'Liste des candidats'}</Link>} />
    <section className="surface overflow-hidden">{query.isLoading ? <StateMessage loading /> : query.isError || !query.data ? <StateMessage error retry={() => query.refetch()} /> : <div className="grid gap-px bg-[#eee8dd] sm:grid-cols-2 lg:grid-cols-3">{Object.entries(query.data).filter(([key]) => key !== 'id').map(([key, value]) => <div key={key} className="bg-[#fffdf8] px-5 py-4"><p className="text-[10px] font-medium text-[#888b85]">{labels.get(key) || friendlyLabel(key, lang)}</p><p className="mt-1.5 break-words text-sm font-semibold text-[#30475a]" dir="auto">{String(value ?? '—')}</p></div>)}</div>}</section>
  </div>;
}

function CandidatesPage() { return <ResourcePage resource="candidates" />; }
function InstructorsPage() { return <ResourcePage resource="instructors" />; }
function TrainingPage() { return <ResourcePage resource="trainingStages" />; }
function SchedulePage() { return <ResourcePage resource="sessions" />; }
function PaymentsPage() { return <ResourcePage resource="payments" />; }
function ExpensesPage() { return <ResourcePage resource="expenses" />; }
function GraduatesPage() { return <ResourcePage resource="graduates" />; }
function TeamPage() { return <ResourcePage resource="users" />; }

function ReportsPage() {
  const { lang } = useLang(); const [category, setCategory] = useState<'operational' | 'financial'>('operational');
  const [report, setReport] = useState<'payments' | 'expenses' | 'candidates' | 'instructors' | 'exams' | 'payroll' | 'journal'>('candidates');
  const query = useGetReport(report, { language: lang });
  const totals = query.data?.totals || {};
  const reportOptions = category === 'operational'
    ? [['candidates', lang === 'ar' ? 'المترشحون' : 'Candidats'], ['instructors', lang === 'ar' ? 'المدربون' : 'Moniteurs'], ['exams', lang === 'ar' ? 'الامتحانات' : 'Examens']] as const
    : [['payments', lang === 'ar' ? 'المدفوعات' : 'Paiements'], ['expenses', lang === 'ar' ? 'المصاريف' : 'Dépenses'], ['journal', lang === 'ar' ? 'دفتر اليومية' : 'Journal'], ['payroll', lang === 'ar' ? 'الأجور' : 'Paie']] as const;
  return <div><PageIntro title={lang === 'ar' ? 'التقارير التشغيلية والمالية' : 'Rapports opérationnels et financiers'} subtitle={lang === 'ar' ? 'بيانات وتقارير مستخرجة من سجلات المدرسة.' : 'Données et rapports issus des registres de l’école.'} />
    <div className="mb-3 flex flex-wrap items-center gap-3"><div className="inline-flex rounded-lg border border-[#e3ddd2] bg-[#f8f5ee] p-1">{(['operational', 'financial'] as const).map(k => <button key={k} onClick={() => { setCategory(k); setReport(k === 'operational' ? 'candidates' : 'payments'); }} className={`rounded-md px-4 py-2 text-xs font-semibold transition ${category === k ? 'bg-[#203a52] text-white shadow-sm' : 'text-[#69727a] hover:text-[#243b50]'}`} data-testid={`button-report-${k}`}>{k === 'operational' ? (lang === 'ar' ? 'التقرير التشغيلي' : 'Rapport opérationnel') : (lang === 'ar' ? 'التقرير المالي' : 'Rapport financier')}</button>)}</div>
      <select value={report} onChange={e => setReport(e.target.value as typeof report)} className="field-control w-auto min-w-[190px] text-xs" aria-label={lang === 'ar' ? 'نوع التقرير' : 'Type de rapport'} data-testid="select-report-type">{reportOptions.map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select>
    </div>
    <div className="surface overflow-hidden">{query.isLoading ? <StateMessage loading /> : query.isError ? <StateMessage error retry={() => query.refetch()} /> : <><div className="grid gap-3 border-b border-[#eee8dd] p-4 sm:grid-cols-2 lg:grid-cols-4">{Object.entries(totals).map(([key, val]) => <div key={key} className="rounded-lg bg-[#f6f3ec] p-4"><p className="text-[10px] text-[#7c817e]">{friendlyLabel(key, lang)}</p><p className="mt-2 font-mono text-lg font-semibold text-[#20374d]">{money(val, lang)}</p></div>)}{!Object.keys(totals).length && <p className="text-xs text-[#868984]">{lang === 'ar' ? 'لا توجد إجماليات للفترة المحددة.' : 'Aucun total pour la période sélectionnée.'}</p>}</div>{query.data?.items.length ? <div className="overflow-x-auto"><table className="w-full min-w-[500px]"><thead><tr className="bg-[#f6f3ec] text-[10px] text-[#7e817c]">{Object.keys(query.data.items[0]).map(key => <th key={key} className="px-4 py-3 text-start">{friendlyLabel(key, lang)}</th>)}</tr></thead><tbody className="divide-y divide-[#eee8dd]">{query.data.items.map((row, i) => <tr key={row.id ?? i} className="table-row">{Object.entries(row).map(([key, val]) => <td key={key} className="px-4 py-3 text-xs text-[#405365]" dir="auto">{String(val ?? '—')}</td>)}</tr>)}</tbody></table></div> : <StateMessage empty />}</>}</div>
  </div>;
}

function DocumentsPage() {
  const { lang } = useLang();
  const [selected, setSelected] = useState('');
  const [candidateId, setCandidateId] = useState('');
  const [candidateIds, setCandidateIds] = useState<number[]>([]);
  const [docOptions, setDocOptions] = useState<Record<string, string>>({});
  const catalog = useGetDocumentCatalog({ language: lang });
  const generate = useMutation(getGenerateDocumentMutationOptions());
  const candidates = useListResourceRecords('candidates', { language: lang });
  const selectedDoc = catalog.data?.find(doc => doc.id === selected);
  const selectDocument = (doc: NonNullable<typeof catalog.data>[number]) => {
    setSelected(doc.id);
    setCandidateIds([]);
    setCandidateId('');
    setDocOptions(Object.fromEntries((doc.fields ?? []).map(field => [
      field.name,
      field.type === 'date' && ['examDate', 'dispatchDate'].includes(field.name)
        ? new Date().toISOString().slice(0, 10)
        : '',
    ])));
  };
  const toggleCandidate = (id: number, checked: boolean) => {
    setCandidateIds(current => checked
      ? current.includes(id) ? current : [...current, id]
      : current.filter(candidate => candidate !== id));
  };
  const onGenerate = () => {
    const item = selectedDoc;
    if (!item) return;
    const options: Record<string, unknown> = {};
    for (const field of item.fields ?? []) {
      const value = docOptions[field.name] ?? '';
      if (!value) continue;
      options[field.name] = field.type === 'number' ? Number(value) : value;
    }
    const from = docOptions.from;
    const to = docOptions.to;
    delete options.from;
    delete options.to;
    generate.mutate({
      data: {
        type: item.id,
        language: lang,
        ...(item.scope === 'candidate' && candidateId ? { candidateId: Number(candidateId) } : {}),
        ...(candidateIds.length ? { candidateIds } : {}),
        ...(from ? { from } : {}),
        ...(to ? { to } : {}),
        ...(Object.keys(options).length ? { options } : {}),
      },
    }, { onSuccess: blob => {
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${item.id}.pdf`;
      link.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    } });
  };
  const missingRequiredOption = Boolean(selectedDoc?.fields?.some(field => field.required && !docOptions[field.name]));
  return <div><PageIntro title={lang === 'ar' ? 'الوثائق الرسمية' : 'Documents officiels'} subtitle={lang === 'ar' ? 'اختر وثيقة من فهرس النظام لإنشاء ملف PDF الرسمي.' : 'Choisissez un document du catalogue pour générer le PDF officiel.'} />
    <div className="grid gap-5 xl:grid-cols-[1fr_340px]"><section className="surface overflow-hidden"><div className="flex items-center justify-between border-b border-[#eee8dd] px-5 py-4"><div><h3 className="text-sm font-bold text-[#20374d]">{lang === 'ar' ? 'فهرس الوثائق' : 'Catalogue des documents'}</h3><p className="mt-1 text-[10px] text-[#858984]">{lang === 'ar' ? 'الأسماء والنماذج من الخادم فقط' : 'Noms et modèles fournis par le serveur'}</p></div><FileText size={18} className="text-[#b7803a]" /></div>
      {catalog.isLoading ? <StateMessage loading /> : catalog.isError ? <StateMessage error retry={() => catalog.refetch()} /> : !catalog.data?.length ? <StateMessage empty /> : <div className="grid gap-3 p-4 md:grid-cols-2">{catalog.data.map(doc => <button key={doc.id} onClick={() => selectDocument(doc)} className={`rounded-xl border p-4 text-start transition ${selected === doc.id ? 'border-[#b8894c] bg-[#f8f1e4] ring-1 ring-[#c9a26a]/30' : 'border-[#eae4d9] bg-[#fffefa] hover:border-[#d6c5a6]'}`} data-testid={`document-option-${doc.id}`}><div className="mb-3 flex items-start justify-between"><span className={`grid h-9 w-9 place-items-center rounded-lg ${selected === doc.id ? 'bg-[#ead8b9] text-[#805b2c]' : 'bg-[#f1eee7] text-[#6c7580]'}`}><FileText size={17} /></span><span className="rounded-full bg-[#f1eee7] px-2 py-1 text-[9px] font-semibold text-[#737a7b]">{doc.scope === 'candidate' ? (lang === 'ar' ? 'مترشح' : 'Candidat') : (lang === 'ar' ? 'جماعي' : 'Groupe')}</span></div><p className="text-sm font-bold text-[#2c4256]">{doc.label}</p>{doc.description && <p className="mt-1.5 text-[11px] leading-5 text-[#7e827d]">{doc.description}</p>}</button>)}</div>}
    </section>
    <aside className="surface h-fit p-5"><h3 className="text-sm font-bold text-[#20374d]">{lang === 'ar' ? 'إنشاء PDF' : 'Générer un PDF'}</h3><p className="mt-1 text-[11px] leading-5 text-[#858984]">{lang === 'ar' ? 'تُحافظ الوثيقة المنشأة على قواعد التنسيق الرسمية.' : 'Le PDF généré conserve les règles de mise en page officielles.'}</p>
      {selectedDoc?.scope === 'candidate' && <label className="mt-5 block text-xs font-medium text-[#455565]"><span className="mb-1.5 block">{lang === 'ar' ? 'المترشح' : 'Candidat'}</span><select className="field-control" value={candidateId} onChange={e => setCandidateId(e.target.value)} data-testid="select-document-candidate"><option value="">{lang === 'ar' ? 'اختر مترشحاً' : 'Choisir un candidat'}</option>{(candidates.data?.items || []).map(candidate => <option value={candidate.id} key={candidate.id}>{recordTitle(candidate)}</option>)}</select></label>}
      {selectedDoc?.fields?.map(field => <label key={field.name} className="mt-4 block text-xs font-medium text-[#455565]"><span className="mb-1.5 block">{field.label}{field.required && <b className="ms-1 text-[#a83d37]">*</b>}</span>{field.type === 'select' ? <select className="field-control" value={docOptions[field.name] || ''} onChange={e => setDocOptions(current => ({ ...current, [field.name]: e.target.value }))}><option value="">{lang === 'ar' ? 'اختر…' : 'Sélectionner…'}</option>{(field.options || []).map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select> : field.type === 'textarea' ? <textarea className="field-control min-h-20" value={docOptions[field.name] || ''} onChange={e => setDocOptions(current => ({ ...current, [field.name]: e.target.value }))} /> : <input type={field.type === 'date' ? 'date' : field.type === 'number' ? 'number' : 'text'} className="field-control" value={docOptions[field.name] || ''} onChange={e => setDocOptions(current => ({ ...current, [field.name]: e.target.value }))} />}</label>)}
      {selectedDoc && ['dispatch_table', 'exam_candidates_list'].includes(selectedDoc.id) && <div className="mt-5 rounded-lg border border-[#eae4d9] p-3"><p className="mb-2 text-[11px] font-semibold text-[#455565]">{lang === 'ar' ? 'المترشحون (اترك القائمة فارغة لاختيار الجميع)' : 'Candidats (laissez vide pour tout sélectionner)'}</p>{candidates.isLoading ? <StateMessage loading /> : <div className="max-h-48 space-y-1 overflow-y-auto">{(candidates.data?.items || []).map(candidate => <label key={candidate.id} className="flex items-center gap-2 rounded-md px-2 py-1.5 text-[11px] text-[#596675] hover:bg-[#f6f3ec]"><input type="checkbox" checked={candidateIds.includes(candidate.id)} onChange={e => toggleCandidate(candidate.id, e.target.checked)} className="h-4 w-4 accent-[#203a52]" /><span className="truncate">{recordTitle(candidate)}</span></label>)}</div>}</div>}
      <Button onClick={onGenerate} disabled={!selected || generate.isPending || (selectedDoc?.scope === 'candidate' && !candidateId) || missingRequiredOption} testId="button-generate-document" ><Download size={14} />{generate.isPending ? (lang === 'ar' ? 'جارٍ الإنشاء…' : 'Génération…') : (lang === 'ar' ? 'إنشاء وتحميل PDF' : 'Générer et télécharger')}</Button>
      {generate.isError && <p className="mt-3 text-xs text-[#a83d37]" role="alert">{lang === 'ar' ? 'تعذر إنشاء الوثيقة. تحقق من الاختيار وحاول مجدداً.' : 'Impossible de générer le document. Vérifiez votre sélection.'}</p>}
      {!selected && <p className="mt-4 border-t border-[#eee8dd] pt-4 text-[10px] leading-5 text-[#8b8b83]">{lang === 'ar' ? 'يجب اختيار وثيقة من الفهرس أولاً.' : 'Sélectionnez d’abord un document du catalogue.'}</p>}
    </aside></div>
  </div>;
}

function AccountingPage() {
  const { lang } = useLang();
  return <div><PageIntro title={lang === 'ar' ? 'المحاسبة والمالية' : 'Comptabilité et finances'} subtitle={lang === 'ar' ? 'دليل الحسابات ودفتر اليومية مع سجل الرواتب.' : 'Plan comptable, journal et registre de paie.'} />
    <div className="mb-5 grid gap-4 md:grid-cols-3">{[['accounts', BookOpen], ['journalEntries', ClipboardList], ['payroll', Banknote]].map(([resource, icon]) => { const Icon = icon as LucideIcon; const info = resourceTitles[resource as string]; const query = resource as string; return <Link key={query} href={query === 'payroll' ? '/hr' : '/accounting'} className="surface flex items-center gap-3 p-4 text-inherit no-underline hover:border-[#d7c39f]">{/* Tabs are rendered below for the active ledger. */}<span className="grid h-10 w-10 place-items-center rounded-xl bg-[#e9edf0] text-[#385b75]"><Icon size={18} /></span><span><b className="block text-xs text-[#20374d]">{info[lang]}</b><small className="mt-1 block text-[10px] text-[#818680]">{query === 'accounts' ? (lang === 'ar' ? 'عرض الحسابات' : 'Voir les comptes') : query === 'journalEntries' ? (lang === 'ar' ? 'عرض القيود' : 'Voir les écritures') : (lang === 'ar' ? 'إدارة الأجور' : 'Gérer la paie')}</small></span>{lang === 'ar' ? <ChevronLeft size={15} className="ms-auto text-[#aaa399]" /> : <ChevronRight size={15} className="ms-auto text-[#aaa399]" />}</Link>; })}</div>
    <ResourcePage resource="accounts" /><div className="mt-8"><ResourcePage resource="journalEntries" /></div>
  </div>;
}
function HrPage() {
  const { lang } = useLang();
  return <div><PageIntro title={lang === 'ar' ? 'الموارد البشرية والأجور' : 'Ressources humaines et paie'} subtitle={lang === 'ar' ? 'ملفات الموظفين ومتابعة كشف الرواتب.' : 'Dossiers des employés et suivi de la paie.'} />
    <div className="grid gap-7"><section><h3 className="mb-3 flex items-center gap-2 text-sm font-bold text-[#30475a]"><BriefcaseBusiness size={16} className="text-[#aa793c]" />{lang === 'ar' ? 'الموظفون' : 'Employés'}</h3><ResourcePage resource="employees" /></section><section><h3 className="mb-3 flex items-center gap-2 text-sm font-bold text-[#30475a]"><Banknote size={16} className="text-[#aa793c]" />{lang === 'ar' ? 'كشف الأجور' : 'Paie'}</h3><ResourcePage resource="payroll" /></section></div>
  </div>;
}

function LoginPage() {
  const { lang } = useLang(); const [, setLocation] = useLocation(); const client = useQueryClient();
  const form = useForm<{ email: string; password: string }>({ resolver: zodResolver(z.object({ email: z.string().email(), password: z.string().min(1) })), defaultValues: { email: 'admin@midanic.com', password: '' } });
  const mutation = useMutation(getLoginMutationOptions());
  const submit = form.handleSubmit(data => mutation.mutate({ data }, { onSuccess: user => { client.setQueryData(getGetCurrentUserQueryKey(), user); client.invalidateQueries({ queryKey: getGetDashboardQueryKey() }); setLocation('/'); } }));
  return <AuthFrame><div className="mb-7 text-center"><img src={logo} className="mx-auto mb-4 h-[82px] w-[82px] rounded-full border border-[#e6e0d5] bg-[#f8f6ef] object-cover" alt="شعار ميدانيك" /><p className="text-[10px] font-semibold tracking-[.15em] text-[#a5793d]">MEDANIC ERP</p><h1 className="mt-2 text-[24px] font-bold text-[#1e344a]">{lang === 'ar' ? 'تسجيل الدخول' : 'Connexion'}</h1><p className="mt-2 text-xs text-[#818680]">{lang === 'ar' ? 'فضاء تسيير مدرسة تعليم السياقة' : 'Espace de gestion de l’auto-école'}</p></div>
    <Form {...form}><form onSubmit={submit} className="space-y-4"><label className="block text-xs font-medium text-[#455565]">{lang === 'ar' ? 'البريد الإلكتروني' : 'Adresse e-mail'}<input {...form.register('email')} type="email" autoComplete="email" className="field-control mt-1.5" data-testid="input-login-email" /></label><label className="block text-xs font-medium text-[#455565]">{lang === 'ar' ? 'كلمة المرور' : 'Mot de passe'}<input {...form.register('password')} type="password" autoComplete="current-password" className="field-control mt-1.5" data-testid="input-login-password" /></label>{mutation.isError && <p role="alert" className="rounded-lg bg-[#f8e8e5] px-3 py-2 text-xs text-[#a83d37]">{lang === 'ar' ? 'البريد الإلكتروني أو كلمة المرور غير صحيحة، أو تعذر الاتصال.' : 'Adresse e-mail ou mot de passe incorrect, ou connexion impossible.'}</p>}<Button type="submit" disabled={mutation.isPending} testId="button-login" >{mutation.isPending && <LoaderCircle size={14} className="animate-spin" />}{lang === 'ar' ? 'الدخول إلى النظام' : 'Se connecter'}<ArrowLeft size={14} /></Button></form></Form>
    <div className="mt-5 flex justify-between border-t border-[#eee8dd] pt-4 text-xs"><Link href="/setup" className="text-[#7f633e] hover:underline">{lang === 'ar' ? 'إنشاء المدير الأول' : 'Créer le premier administrateur'}</Link><button onClick={() => form.reset()} className="text-[#777e80] hover:text-[#243b50]" data-testid="button-clear-login">{lang === 'ar' ? 'مسح الحقول' : 'Effacer'}</button></div>
  </AuthFrame>;
}
function SetupPage() {
  const { lang } = useLang(); const [, setLocation] = useLocation(); const client = useQueryClient(); const setup = useGetSetupStatus();
  const form = useForm<{ fullName: string }>({ resolver: zodResolver(z.object({ fullName: z.string().min(1) })), defaultValues: { fullName: '' } });
  const mutation = useMutation(getSetupInitialAdminMutationOptions());
  useEffect(() => {
    if (!mutation.isSuccess) return;
    client.setQueryData(getGetSetupStatusQueryKey(), { required: false });
    client.invalidateQueries({ queryKey: getGetCurrentUserQueryKey() });
  }, [mutation.isSuccess, client]);
  const submit = form.handleSubmit(data => mutation.mutate({ data }, { onSuccess: user => { client.setQueryData(getGetCurrentUserQueryKey(), user); client.invalidateQueries(); setLocation('/'); } }));
  const setupError = mutation.error instanceof Error ? mutation.error.message : '';
  const setupErrorText = setupError.includes('INITIAL_ADMIN_PASSWORD')
    ? (lang === 'ar' ? 'أضف السر INITIAL_ADMIN_PASSWORD إلى متغيرات بيئة الخادم (12 حرفاً على الأقل) ثم أعد تشغيل الخدمة.' : 'Ajoutez le secret INITIAL_ADMIN_PASSWORD aux variables du serveur (12 caractères minimum), puis redémarrez le service.')
    : setupError.includes('SESSION_SECRET')
      ? (lang === 'ar' ? 'أضف السر SESSION_SECRET إلى متغيرات بيئة الخادم (32 حرفاً على الأقل) ثم أعد تشغيل الخدمة.' : 'Ajoutez le secret SESSION_SECRET aux variables du serveur (32 caractères minimum), puis redémarrez le service.')
      : (lang === 'ar' ? 'تعذر إنشاء الحساب. تحقق من الإعدادات وحاول مجدداً.' : 'Création impossible. Vérifiez la configuration et réessayez.');
  const inputs: { name: 'fullName'; ar: string; fr: string }[] = [
    { name: 'fullName', ar: 'الاسم الكامل', fr: 'Nom complet' },
  ];
  return <AuthFrame><div className="mb-6 text-center"><img src={logo} className="mx-auto mb-4 h-[72px] w-[72px] rounded-full border border-[#e6e0d5] object-cover" alt="شعار ميدانيك" /><h1 className="text-[22px] font-bold text-[#1e344a]">{lang === 'ar' ? 'إعداد الحساب الأول' : 'Configuration initiale'}</h1><p className="mt-2 text-xs text-[#818680]">{lang === 'ar' ? 'أنشئ حساب المدير الأول. اختر كلمة مرور قوية واحتفظ بها.' : 'Créez le premier compte administrateur et choisissez un mot de passe robuste.'}</p></div>
    {setup.data?.required === false ? <div className="rounded-lg bg-[#f5f0e5] p-4 text-center text-xs text-[#6e716d]">{lang === 'ar' ? 'تم إعداد النظام مسبقاً. سجّل الدخول بحسابك.' : 'Le système est déjà configuré. Connectez-vous avec votre compte.'}<Link href="/login" className="mt-3 block font-semibold text-[#7f633e] hover:underline">{lang === 'ar' ? 'الانتقال إلى تسجيل الدخول' : 'Aller à la connexion'}</Link></div> : setup.isError ? <div className="mb-4 rounded-lg bg-[#f8e8e5] p-3 text-xs text-[#a83d37]">{lang === 'ar' ? 'تعذر التحقق من حالة الإعداد.' : 'Impossible de vérifier l’état de configuration.'}</div> : null}
     {setup.data?.required !== false && <Form {...form}><form onSubmit={submit} className="space-y-3"><label className="block text-xs font-medium text-[#455565]">{lang === 'ar' ? 'البريد الإلكتروني' : 'Adresse e-mail'}<input value="admin@midanic.com" readOnly className="field-control mt-1.5 bg-[#f5f2eb] text-[#68747b]" data-testid="input-setup-email" /></label>{inputs.map(item => <label key={item.name} className="block text-xs font-medium text-[#455565]">{item[lang]}<input {...form.register(item.name)} autoComplete="name" className="field-control mt-1.5" data-testid={`input-setup-${item.name}`} /></label>)}<p className="rounded-lg bg-[#f5f0e5] px-3 py-2 text-xs text-[#6e716d]">{lang === 'ar' ? 'كلمة المرور المؤقتة محفوظة في السر INITIAL_ADMIN_PASSWORD في إعدادات الخادم، وسيُطلب تغييرها بعد أول دخول.' : 'Le mot de passe temporaire est stocké dans le secret serveur INITIAL_ADMIN_PASSWORD et devra être changé après la première connexion.'}</p>{mutation.isError && <p role="alert" className="rounded-lg bg-[#f8e8e5] px-3 py-2 text-xs text-[#a83d37]">{setupErrorText}</p>}<Button type="submit" disabled={mutation.isPending || setup.isLoading} testId="button-setup-admin">{mutation.isPending && <LoaderCircle size={14} className="animate-spin" />}{lang === 'ar' ? 'إنشاء حساب المدير' : 'Créer le compte administrateur'}</Button></form></Form>}
    <Link href="/login" className="mt-5 block text-center text-xs text-[#7f633e] hover:underline">{lang === 'ar' ? 'العودة إلى تسجيل الدخول' : 'Retour à la connexion'}</Link>
  </AuthFrame>;
}
function ProfilePage() {
  const { lang } = useLang();
  const client = useQueryClient();
  const currentUser = useGetCurrentUser({ query: { retry: false } });
  const mutation = useMutation(getUpdateAccountMutationOptions());
  const [saved, setSaved] = useState(false);
  const form = useForm<{ email: string; currentPassword: string; newPassword: string; confirmPassword: string }>({
    resolver: zodResolver(z.object({
      email: z.string().email(),
      currentPassword: z.string().min(1),
      newPassword: z.string(),
      confirmPassword: z.string(),
    }).superRefine((values, context) => {
      if (values.newPassword && values.newPassword.length < 12) {
        context.addIssue({ code: z.ZodIssueCode.custom, path: ['newPassword'], message: 'Password must be at least 12 characters.' });
      }
      if (currentUser.data?.mustChangePassword && !values.newPassword) {
        context.addIssue({ code: z.ZodIssueCode.custom, path: ['newPassword'], message: 'A new password is required.' });
      }
      if (values.newPassword !== values.confirmPassword) {
        context.addIssue({ code: z.ZodIssueCode.custom, path: ['confirmPassword'], message: 'Passwords do not match.' });
      }
    })),
    defaultValues: { email: '', currentPassword: '', newPassword: '', confirmPassword: '' },
  });

  useEffect(() => {
    if (currentUser.data) {
      form.reset({ email: currentUser.data.email, currentPassword: '', newPassword: '', confirmPassword: '' });
    }
  }, [currentUser.data?.email, form]);

  const submit = form.handleSubmit(({ email, currentPassword, newPassword }) => {
    setSaved(false);
    mutation.mutate({
      data: { email, currentPassword, ...(newPassword ? { newPassword } : {}) },
    }, {
      onSuccess: user => {
        client.setQueryData(getGetCurrentUserQueryKey(), user);
        form.reset({ email: user.email, currentPassword: '', newPassword: '', confirmPassword: '' });
        setSaved(true);
      },
    });
  });

  return <div><PageIntro title={lang === 'ar' ? 'الحساب والأمان' : 'Compte et sécurité'} subtitle={lang === 'ar' ? 'تغيير البريد الإلكتروني أو كلمة المرور بعد التحقق من كلمة المرور الحالية.' : 'Modifiez votre adresse e-mail ou votre mot de passe après vérification du mot de passe actuel.'} />
    {currentUser.data?.mustChangePassword && <div role="status" className="mb-4 rounded-lg border border-[#e7d2a9] bg-[#f8f0df] p-4 text-sm text-[#6e5732]">{lang === 'ar' ? 'هذه كلمة مرور مؤقتة. غيّرها الآن للمتابعة إلى بقية النظام.' : 'Ce mot de passe est temporaire. Changez-le maintenant pour accéder au reste du système.'}</div>}
    {currentUser.isLoading ? <StateMessage loading /> : <section className="surface max-w-2xl p-5 md:p-7">
      <Form {...form}><form onSubmit={submit} className="space-y-4">
        <label className="block text-xs font-medium text-[#455565]">{lang === 'ar' ? 'البريد الإلكتروني' : 'Adresse e-mail'}<input {...form.register('email')} type="email" autoComplete="email" className="field-control mt-1.5" data-testid="input-profile-email" /></label>
        <label className="block text-xs font-medium text-[#455565]">{lang === 'ar' ? 'كلمة المرور الحالية للتأكيد' : 'Mot de passe actuel pour confirmer'}<input {...form.register('currentPassword')} type="password" autoComplete="current-password" className="field-control mt-1.5" data-testid="input-profile-current-password" /></label>
        <div className="grid gap-4 md:grid-cols-2">
          <label className="block text-xs font-medium text-[#455565]">{currentUser.data?.mustChangePassword ? (lang === 'ar' ? 'كلمة المرور الجديدة (مطلوبة، 12 حرفاً على الأقل)' : 'Nouveau mot de passe (obligatoire, 12 caractères minimum)') : (lang === 'ar' ? 'كلمة المرور الجديدة (اختياري، 12 حرفاً على الأقل)' : 'Nouveau mot de passe (facultatif, 12 caractères minimum)')}<input {...form.register('newPassword')} type="password" autoComplete="new-password" className="field-control mt-1.5" data-testid="input-profile-new-password" /></label>
          <label className="block text-xs font-medium text-[#455565]">{lang === 'ar' ? 'تأكيد كلمة المرور الجديدة' : 'Confirmer le nouveau mot de passe'}<input {...form.register('confirmPassword')} type="password" autoComplete="new-password" className="field-control mt-1.5" data-testid="input-profile-confirm-password" /></label>
        </div>
        {form.formState.errors.newPassword && <p role="alert" className="text-xs text-[#a83d37]">{lang === 'ar' ? 'كلمة المرور الجديدة يجب أن تتكون من 12 حرفاً على الأقل.' : 'Le nouveau mot de passe doit contenir au moins 12 caractères.'}</p>}
        {form.formState.errors.confirmPassword && <p role="alert" className="text-xs text-[#a83d37]">{lang === 'ar' ? 'تأكيد كلمة المرور غير مطابق.' : 'La confirmation du mot de passe ne correspond pas.'}</p>}
        {mutation.isError && <p role="alert" className="rounded-lg bg-[#f8e8e5] px-3 py-2 text-xs text-[#a83d37]">{lang === 'ar' ? 'تعذر تحديث الحساب. تحقق من كلمة المرور الحالية والبريد الإلكتروني.' : 'Impossible de mettre à jour le compte. Vérifiez le mot de passe actuel et l’adresse e-mail.'}</p>}
        {saved && <p role="status" className="rounded-lg bg-[#e8f2e8] px-3 py-2 text-xs text-[#386344]">{lang === 'ar' ? 'تم تحديث بيانات الحساب.' : 'Les informations du compte ont été mises à jour.'}</p>}
        <Button type="submit" disabled={mutation.isPending} testId="button-profile-save">{mutation.isPending && <LoaderCircle size={14} className="animate-spin" />}{currentUser.data?.mustChangePassword ? (lang === 'ar' ? 'تغيير كلمة المرور والمتابعة' : 'Changer le mot de passe et continuer') : (lang === 'ar' ? 'حفظ التغييرات' : 'Enregistrer les modifications')}</Button>
      </form></Form>
    </section>}
  </div>;
}
function AuthFrame({ children }: { children: ReactNode }) {
  const { lang, setLang } = useLang();
  return <div className="flex min-h-[100dvh] items-center justify-center bg-[#f2efe7] p-4"><div className="surface w-full max-w-[440px] p-6 sm:p-9"><div className="mb-4 flex justify-end"><button onClick={() => setLang(lang === 'ar' ? 'fr' : 'ar')} className="flex items-center gap-2 rounded-md px-2 py-1 text-xs font-semibold text-[#5d6b75] hover:bg-[#f1ece2]" data-testid="button-auth-language"><Languages size={14} />{lang === 'ar' ? 'Français' : 'العربية'}</button></div>{children}</div></div>;
}
function NotFound() {
  const { lang } = useLang();
  return <div className="flex min-h-[60vh] flex-col items-center justify-center text-center"><div className="grid h-16 w-16 place-items-center rounded-2xl bg-[#e8edf0] text-[#385b75]"><CircleHelp size={27} /></div><p className="mt-5 font-mono text-xs text-[#a8783c]">404</p><h2 className="mt-2 text-xl font-bold text-[#20374d]">{lang === 'ar' ? 'الصفحة غير موجودة' : 'Page introuvable'}</h2><Link href="/" className="mt-5 text-sm font-semibold text-[#7f633e] hover:underline">{lang === 'ar' ? 'العودة إلى لوحة القيادة' : 'Retour au tableau de bord'}</Link></div>;
}

function recordTitle(row: ResourceRecord) {
  const name = [row.firstName, row.lastName].filter(Boolean).join(' ');
  return String(name || row.name || row.label || row.description || `#${row.id}`);
}
function recordDate(row: ResourceRecord) {
  const date = row.date || row.sessionDate || row.registrationDate || row.createdAt;
  if (!date) return '';
  const parsed = new Date(String(date));
  return Number.isNaN(parsed.getTime()) ? String(date) : new Intl.DateTimeFormat('fr-DZ', { dateStyle: 'medium' }).format(parsed);
}
function formatField(value: unknown, field: FieldDefinition) {
  if (value === null || value === undefined || value === '') return '—';
  if (field.type === 'boolean') return value ? 'نعم / Oui' : '—';
  if (field.type === 'date') { const date = new Date(String(value)); return Number.isNaN(date.getTime()) ? String(value) : new Intl.DateTimeFormat('fr-DZ').format(date); }
  return String(value);
}
function money(value: unknown, lang: Lang) {
  if (value === null || value === undefined || value === '') return '—';
  const amount = Number(value);
  return Number.isFinite(amount) ? new Intl.NumberFormat(lang === 'ar' ? 'ar-DZ' : 'fr-DZ', { style: 'currency', currency: 'DZD', maximumFractionDigits: 0 }).format(amount) : String(value);
}
function friendlyLabel(key: string, lang: Lang) {
  const labels: Record<string, { ar: string; fr: string }> = {
    id: { ar: 'رقم السجل', fr: 'Référence' }, amount: { ar: 'المبلغ', fr: 'Montant' }, total: { ar: 'الإجمالي', fr: 'Total' },
    count: { ar: 'العدد', fr: 'Nombre' }, date: { ar: 'التاريخ', fr: 'Date' }, status: { ar: 'الحالة', fr: 'Statut' },
    result: { ar: 'النتيجة', fr: 'Résultat' }, candidateId: { ar: 'رقم المترشح', fr: 'Référence candidat' },
    candidateName: { ar: 'اسم المترشح', fr: 'Nom du candidat' }, firstName: { ar: 'الاسم', fr: 'Prénom' },
    lastName: { ar: 'اللقب', fr: 'Nom' }, type: { ar: 'النوع', fr: 'Type' },
    expenseType: { ar: 'نوع المصروف', fr: 'Type de dépense' }, paymentMethod: { ar: 'طريقة الدفع', fr: 'Mode de paiement' },
    debit: { ar: 'مدين', fr: 'Débit' }, credit: { ar: 'دائن', fr: 'Crédit' },
    accountName: { ar: 'الحساب', fr: 'Compte' }, salary: { ar: 'الأجر', fr: 'Salaire' },
    payments: { ar: 'المدفوعات', fr: 'Paiements' }, expenses: { ar: 'المصاريف', fr: 'Dépenses' },
    candidates: { ar: 'المترشحون', fr: 'Candidats' }, instructors: { ar: 'المدربون', fr: 'Moniteurs' },
    exams: { ar: 'الامتحانات', fr: 'Examens' }, payroll: { ar: 'الأجور', fr: 'Paie' }, journal: { ar: 'دفتر اليومية', fr: 'Journal' },
  };
  return labels[key]?.[lang] || (lang === 'ar' ? 'معلومة' : 'Information');
}

export default App;
