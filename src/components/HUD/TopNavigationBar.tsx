import React from 'react';
import { 
  CountryCode, 
  UserRole, 
  ScenarioPreset,
  MainView,
  Language,
  AppTheme
} from '../../types';
import { COUNTRY_PROFILES } from '../../data/mockData';
import { t } from '../../utils/i18n';
import { 
  Globe2, 
  Cpu, 
  Volume2, 
  VolumeX, 
  Award,
  ChevronDown,
  BarChart2,
  Box,
  Brain,
  FolderArchive,
  Sun,
  Moon,
  Languages,
  Sparkles,
  Users,
  ShieldCheck
} from 'lucide-react';
import { playHoloClick, isSoundEnabled, setSoundEnabled } from '../../utils/audioSynth';

interface TopNavigationBarProps {
  currentView: MainView;
  onChangeView: (view: MainView) => void;
  country: CountryCode;
  onSelectCountry: (c: CountryCode) => void;
  role: UserRole;
  onChangeRole: (r: UserRole) => void;
  scenario: ScenarioPreset;
  onSelectScenario: (s: ScenarioPreset) => void;
  onOpenILO: () => void;
  onOpenUsers: () => void;
  language: Language;
  onChangeLanguage: (lang: Language) => void;
  theme: AppTheme;
  onChangeTheme: (theme: AppTheme) => void;
  onOpenChatbot?: () => void;
  isDatasetLoaded?: boolean;
}

export const TopNavigationBar: React.FC<TopNavigationBarProps> = ({
  currentView,
  onChangeView,
  country,
  onSelectCountry,
  role,
  onChangeRole,
  onOpenILO,
  onOpenUsers,
  language,
  onChangeLanguage,
  theme,
  onChangeTheme,
  onOpenChatbot,
  isDatasetLoaded = false,
}) => {
  const [soundOn, setSoundOn] = React.useState(isSoundEnabled());
  const [showRoleDropdown, setShowRoleDropdown] = React.useState(false);
  const [showCountryDropdown, setShowCountryDropdown] = React.useState(false);

  const isLight = theme === 'light';

  const toggleSound = () => {
    const nextState = !soundOn;
    setSoundOn(nextState);
    setSoundEnabled(nextState);
    if (nextState) playHoloClick(1000);
  };

  const toggleLanguage = () => {
    playHoloClick(800);
    onChangeLanguage(language === 'es' ? 'en' : 'es');
  };

  const toggleTheme = () => {
    playHoloClick(750);
    onChangeTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const roleColors: Record<UserRole, { badge: string; text: string; bg: string }> = {
    ADMIN: {
      badge: isLight ? 'border-red-300 bg-red-50 text-red-700' : 'border-red-500/40 bg-red-500/10 text-red-400',
      text: t('roleAdmin', language),
      bg: 'bg-red-500',
    },
    POLICY_ANALYST: {
      badge: isLight ? 'border-sky-300 bg-sky-50 text-sky-800' : 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300',
      text: t('rolePolicyAnalyst', language),
      bg: 'bg-cyan-500',
    },
    RESEARCHER: {
      badge: isLight ? 'border-amber-300 bg-amber-50 text-amber-800' : 'border-amber-500/40 bg-amber-500/10 text-amber-300',
      text: t('roleResearcher', language),
      bg: 'bg-amber-500',
    },
  };

  const navItems: { id: MainView; label: string; icon: React.FC<{ className?: string }> }[] = [
    { id: 'dashboard', label: t('navDashboard', language), icon: BarChart2 },
    { id: 'digital_twin_3d', label: t('navDigitalTwin', language), icon: Box },
    { id: 'ai_engine', label: t('navAIEngine', language), icon: Brain },
    { id: 'datasets_reports', label: t('navDatasets', language), icon: FolderArchive },
  ];

  return (
    <header 
      onPointerDown={(e) => e.stopPropagation()}
      onWheel={(e) => e.stopPropagation()}
      className={`absolute top-0 left-0 right-0 h-16 z-30 px-3 sm:px-4 flex items-center justify-between gap-2 sm:gap-3 pointer-events-auto shadow-xl backdrop-blur-xl select-none transition-colors duration-200 ${
        isLight
          ? 'bg-white/90 border-b border-slate-300 text-slate-800 shadow-slate-900/5'
          : 'hud-glass-solid border-b border-cyan-500/25 text-slate-100'
      }`}
    >
      {/* Brand & System Logo */}
      <div className="flex items-center gap-2.5 sm:gap-3">
        <div className="relative">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center border ${
            isLight
              ? 'bg-sky-50 border-sky-400 shadow-sm'
              : 'bg-cyan-500/20 border-cyan-400 glow-cyan'
          }`}>
            <Cpu className={`w-4 h-4 ${isLight ? 'text-sky-600' : 'text-cyan-300 animate-pulse'}`} />
          </div>
          <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-400 border border-slate-900 animate-ping" />
          <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-400 border border-slate-900" />
        </div>

        <div>
          <div className="flex items-center gap-1.5 sm:gap-2">
            <h1 className={`font-display font-bold text-sm tracking-wide flex items-center gap-1.5 ${
              isLight ? 'text-slate-900' : 'text-slate-100'
            }`}>
              <span>POLICYSYNTH</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono border ${
                isLight
                  ? 'bg-sky-100 text-sky-800 border-sky-300'
                  : 'bg-cyan-950 text-cyan-400 border-cyan-700'
              }`}>
                PRO
              </span>
            </h1>
          </div>
          <div className={`text-[10px] font-mono-hud hidden sm:block ${
            isLight ? 'text-slate-500' : 'text-slate-400'
          }`}>
            {t('brandSubtitle', language)}
          </div>
        </div>
      </div>

      {/* PRIMARY 4-VIEW ROUTE SELECTOR NAVIGATION */}
      <nav className={`flex items-center gap-1 p-1 rounded-2xl border shadow-inner ${
        isLight
          ? 'bg-slate-200/70 border-slate-300'
          : 'bg-slate-950/80 border-cyan-500/30'
      }`}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => {
                playHoloClick(1000);
                onChangeView(item.id);
              }}
              className={`px-2.5 sm:px-3 py-1.5 rounded-xl text-xs font-mono-hud font-medium flex items-center gap-1.5 sm:gap-2 transition-all cursor-pointer ${
                isActive
                  ? isLight
                    ? 'bg-sky-600 text-white font-bold shadow-md shadow-sky-600/20'
                    : 'bg-cyan-500 text-slate-950 font-bold shadow-lg shadow-cyan-500/25 glow-cyan'
                  : isLight
                    ? 'text-slate-600 hover:text-slate-900 hover:bg-slate-300/60'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${
                isActive 
                  ? (isLight ? 'text-white' : 'text-slate-950')
                  : (isLight ? 'text-sky-700' : 'text-cyan-400')
              }`} />
              <span className="hidden md:inline">{item.label}</span>
              {item.id === 'ai_engine' && (
                <span
                  className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                    isDatasetLoaded ? 'bg-emerald-400 ring-2 ring-emerald-400/20' : 'bg-amber-400'
                  }`}
                  title={isDatasetLoaded ? 'Dataset cargado' : 'Requiere dataset'}
                />
              )}
            </button>
          );
        })}
      </nav>

      {/* Right Controls: Country Selector, Role Switcher, Language Toggle, Theme Toggle & SFX */}
      <div className="flex items-center gap-1.5 sm:gap-2">
        {/* Country Selector Dropdown */}
        <div className="relative">
          <button
            onClick={() => {
              playHoloClick(780);
              setShowCountryDropdown(!showCountryDropdown);
            }}
            className={`px-2.5 sm:px-3 py-1.5 rounded-xl border flex items-center gap-1.5 sm:gap-2 transition-all font-mono-hud text-xs cursor-pointer ${
              isLight
                ? 'bg-white hover:bg-slate-100 border-slate-300 text-slate-800'
                : 'hud-glass hover:border-cyan-400 border-cyan-500/30 text-slate-200'
            }`}
          >
            <Globe2 className={`w-3.5 h-3.5 ${isLight ? 'text-sky-600' : 'text-cyan-400'}`} />
            <span className="text-sm">{COUNTRY_PROFILES[country].flag}</span>
            <span className="font-medium hidden lg:inline">{COUNTRY_PROFILES[country].name}</span>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {showCountryDropdown && (
            <div className={`absolute top-full mt-1.5 right-0 w-60 p-2 rounded-xl shadow-2xl z-50 flex flex-col gap-1 border animate-in fade-in slide-in-from-top-1 ${
              isLight
                ? 'bg-white border-slate-300 shadow-slate-900/15'
                : 'hud-glass-solid border-cyan-500/40'
            }`}>
              <div className={`px-2 py-1 text-[10px] font-mono-hud font-semibold uppercase tracking-wider ${
                isLight ? 'text-sky-700' : 'text-cyan-400'
              }`}>
                {t('selectCountry', language)}
              </div>
              {(Object.keys(COUNTRY_PROFILES) as CountryCode[]).map((c) => (
                <button
                  key={c}
                  onClick={() => {
                    playHoloClick(900);
                    onSelectCountry(c);
                    setShowCountryDropdown(false);
                  }}
                  className={`flex items-center justify-between p-2 rounded-lg text-xs font-mono-hud transition-all cursor-pointer ${
                    country === c
                      ? isLight
                        ? 'bg-sky-100 text-sky-800 font-bold border border-sky-300'
                        : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50'
                      : isLight
                        ? 'hover:bg-slate-100 text-slate-700'
                        : 'hover:bg-slate-800/80 text-slate-300'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-base">{COUNTRY_PROFILES[c].flag}</span>
                    <span className="font-medium">{COUNTRY_PROFILES[c].name}</span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">Inf: {COUNTRY_PROFILES[c].baseInformalityRate}%</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* User Role Switcher Dropdown (Visible on all viewports) */}
        <div className="relative flex items-center">
          <button
            onClick={() => {
              playHoloClick(750);
              setShowRoleDropdown(!showRoleDropdown);
            }}
            className={`px-2 sm:px-2.5 py-1.5 rounded-xl border text-xs font-mono-hud flex items-center gap-1.5 sm:gap-2 cursor-pointer transition-all ${roleColors[role].badge}`}
            title={t('roleChangePrompt', language)}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${roleColors[role].bg}`} />
            <span className="font-semibold text-xs">{roleColors[role].text}</span>
            <ChevronDown className="w-3 h-3 opacity-60" />
          </button>

          {showRoleDropdown && (
            <div className={`absolute top-full mt-1.5 right-0 w-64 p-2 rounded-xl shadow-2xl z-50 flex flex-col gap-1 border animate-in fade-in slide-in-from-top-1 ${
              isLight
                ? 'bg-white border-slate-300 shadow-slate-900/15'
                : 'hud-glass-solid border-cyan-500/40'
            }`}>
              <div className="px-2 py-1 text-[10px] font-mono-hud text-slate-400 font-semibold uppercase tracking-wider flex items-center justify-between">
                <span>{t('roleChangePrompt', language)}</span>
                <span className="text-[9px] px-1 rounded bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400">RBAC</span>
              </div>
              {(['POLICY_ANALYST', 'ADMIN', 'RESEARCHER'] as UserRole[]).map((r) => (
                <button
                  key={r}
                  onClick={() => {
                    playHoloClick(850);
                    onChangeRole(r);
                    setShowRoleDropdown(false);
                  }}
                  className={`flex items-center justify-between p-2 rounded-lg text-xs font-mono-hud transition-all cursor-pointer ${
                    role === r 
                      ? isLight ? 'bg-sky-100 text-sky-800 font-bold border border-sky-300' : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50'
                      : isLight ? 'hover:bg-slate-100 text-slate-700' : 'hover:bg-slate-800/80 text-slate-300'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${roleColors[r].bg}`} />
                    <span>{roleColors[r].text}</span>
                  </div>
                  {role === r && (
                    <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold ${
                      isLight ? 'bg-sky-700 text-white' : 'bg-cyan-400 text-slate-950'
                    }`}>
                      {language === 'en' ? 'Active' : 'Activo'}
                    </span>
                  )}
                </button>
              ))}

              <div className="my-1 border-t border-slate-200 dark:border-slate-800" />

              {/* Direct Link to Full User & Role Management CRUD */}
              <button
                onClick={() => {
                  playHoloClick(900);
                  setShowRoleDropdown(false);
                  onOpenUsers();
                }}
                className={`flex items-center justify-between p-2 rounded-lg text-xs font-mono-hud transition-all cursor-pointer ${
                  isLight
                    ? 'bg-rose-50 text-rose-800 hover:bg-rose-100 border border-rose-200'
                    : 'bg-rose-950/40 text-rose-300 hover:bg-rose-900/50 border border-rose-500/30'
                }`}
              >
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-rose-500" />
                  <span className="font-bold">{t('roleManagement', language)}</span>
                </div>
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-400 border border-rose-500/40 font-bold">
                  CRUD
                </span>
              </button>
            </div>
          )}
        </div>

        {/* Dedicated Roles & Users CRUD Button in Topbar */}
        <button
          onClick={() => {
            playHoloClick(900);
            onOpenUsers();
          }}
          className={`px-2 sm:px-2.5 py-1.5 rounded-xl border flex items-center gap-1.5 font-mono-hud text-xs font-semibold transition-all cursor-pointer ${
            isLight
              ? 'bg-rose-50 hover:bg-rose-100 border-rose-300 text-rose-800 shadow-sm'
              : 'hud-glass text-rose-300 border-rose-500/40 hover:border-rose-300 hover:bg-rose-950/40'
          }`}
          title={t('roleManagement', language)}
        >
          <Users className="w-3.5 h-3.5 text-rose-500" />
          <span className="hidden sm:inline">{t('rolesCrud', language)}</span>
        </button>

        {/* 2. LANGUAGE SWITCH TOGGLE (ES / EN) */}
        <button
          onClick={toggleLanguage}
          className={`px-2.5 py-1.5 rounded-xl border flex items-center gap-1.5 font-mono-hud text-xs font-semibold transition-all cursor-pointer ${
            isLight
              ? 'bg-white hover:bg-slate-100 border-slate-300 text-slate-700'
              : 'hud-glass hover:border-cyan-400 border-cyan-500/30 text-slate-200'
          }`}
          title={language === 'es' ? 'Switch to English' : 'Cambiar a Español'}
        >
          <Languages className={`w-3.5 h-3.5 ${isLight ? 'text-sky-600' : 'text-cyan-400'}`} />
          <div className="flex items-center gap-1 text-[11px]">
            <span className={language === 'es' ? (isLight ? 'text-sky-700 font-bold' : 'text-cyan-300 font-bold') : 'text-slate-400'}>ES</span>
            <span className="text-slate-400">/</span>
            <span className={language === 'en' ? (isLight ? 'text-sky-700 font-bold' : 'text-cyan-300 font-bold') : 'text-slate-400'}>EN</span>
          </div>
        </button>

        {/* AI Assistant Quick Trigger */}
        {onOpenChatbot && (
          <button
            onClick={() => {
              playHoloClick(1000);
              onOpenChatbot();
            }}
            className={`px-2.5 py-1.5 rounded-xl border flex items-center gap-1.5 font-mono-hud text-xs font-semibold transition-all cursor-pointer ${
              isLight
                ? 'bg-sky-50 hover:bg-sky-100 border-sky-300 text-sky-800'
                : 'hud-glass text-cyan-300 border-cyan-500/40 hover:border-cyan-300 glow-cyan'
            }`}
            title={language === 'en' ? 'Open AI Copilot' : 'Abrir Copiloto IA'}
          >
            <Sparkles className={`w-3.5 h-3.5 ${isLight ? 'text-sky-600' : 'text-cyan-400'}`} />
            <span className="hidden lg:inline">{language === 'en' ? 'AI Advisor' : 'Asistente IA'}</span>
          </button>
        )}

        {/* 3. THEME TOGGLE (Sun / Moon) */}
        <button
          id="theme-toggle-btn"
          onClick={toggleTheme}
          className="p-2 rounded-xl border transition-all cursor-pointer bg-white hover:bg-slate-100 border-slate-300 text-amber-600 hover:text-amber-500 shadow-sm dark:bg-slate-900/90 dark:border-cyan-500/30 dark:text-cyan-300 dark:hover:border-cyan-400 dark:hover:text-cyan-200 dark:glow-cyan"
          title={isLight ? t('darkMode', language) : t('lightMode', language)}
          aria-label="Cambiar tema claro u oscuro"
        >
          {isLight ? <Sun className="w-4 h-4 text-amber-500" /> : <Moon className="w-4 h-4 text-cyan-300" />}
        </button>

        {/* ILO Decent Work Quick Trigger */}
        <button
          onClick={() => {
            playHoloClick(900);
            onOpenILO();
          }}
          className={`p-2 rounded-xl border transition-colors cursor-pointer hidden 2xl:flex items-center gap-1.5 text-xs font-mono-hud ${
            isLight
              ? 'bg-white hover:bg-emerald-50 border-slate-300 text-emerald-700'
              : 'hud-glass text-slate-300 hover:text-emerald-300 border-cyan-500/30 hover:border-emerald-400/50'
          }`}
          title={t('iloMatrix', language)}
        >
          <Award className="w-3.5 h-3.5 text-emerald-500" />
          <span>{t('iloMatrix', language)}</span>
        </button>

        {/* Audio Sound Toggle */}
        <button
          onClick={toggleSound}
          className={`p-2 rounded-xl border transition-all cursor-pointer ${
            isLight
              ? soundOn
                ? 'bg-white text-sky-700 border-sky-300 hover:bg-sky-50 shadow-sm'
                : 'bg-white text-slate-400 border-slate-300 hover:text-slate-600'
              : soundOn
                ? 'hud-glass text-cyan-300 border-cyan-500/40 hover:border-cyan-300 glow-cyan'
                : 'hud-glass text-slate-500 border-slate-700 hover:text-slate-300'
          }`}
          title={soundOn ? 'Sonido Holográfico Activado' : 'Silenciado'}
        >
          {soundOn ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
        </button>
      </div>
    </header>
  );
};

