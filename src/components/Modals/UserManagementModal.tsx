import React, { useState } from 'react';
import { UserAccount, UserRole, AppTheme, Language } from '../../types';
import { 
  X, 
  Users, 
  ShieldCheck, 
  UserPlus, 
  Lock, 
  Check, 
  Mail, 
  Building,
  Trash2,
  Edit3,
  Save,
  Key,
  UserCheck,
  AlertTriangle,
  Search,
  RotateCcw
} from 'lucide-react';
import { playHoloClick } from '../../utils/audioSynth';
import { MOCK_USERS } from '../../data/mockData';

interface UserManagementModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentRole: UserRole;
  onChangeRole: (newRole: UserRole) => void;
  users: UserAccount[];
  setUsers: React.Dispatch<React.SetStateAction<UserAccount[]>>;
  theme?: AppTheme;
  language?: Language;
}

export const UserManagementModal: React.FC<UserManagementModalProps> = ({
  isOpen,
  onClose,
  currentRole,
  onChangeRole,
  users,
  setUsers,
  theme = 'dark',
  language = 'es',
}) => {
  // CRUD state
  const [showAddUser, setShowAddUser] = useState(false);
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  // Form state for creating user
  const [newName, setNewName] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newDepartment, setNewDepartment] = useState('Secretaría del Trabajo & Políticas');
  const [newRole, setNewRole] = useState<UserRole>('POLICY_ANALYST');
  const [newPermissions, setNewPermissions] = useState<UserAccount['permissions']>({
    editPolicies: true,
    retrainAI: false,
    manageDatasets: true,
    manageUsers: false,
    exportReports: true,
  });

  // Form state for editing user
  const [editName, setEditName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editDepartment, setEditDepartment] = useState('');
  const [editRole, setEditRole] = useState<UserRole>('POLICY_ANALYST');

  // Search and filter
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<'ALL' | UserRole>('ALL');

  if (!isOpen) return null;

  const isLight = theme === 'light';
  const isEn = language === 'en';

  const roleStyles: Record<UserRole, { badge: string; label: string; bgDot: string; text: string; desc: string }> = {
    ADMIN: { 
      badge: isLight ? 'bg-rose-100 text-rose-800 border-rose-300' : 'bg-rose-500/20 text-rose-300 border-rose-500/40',
      label: isEn ? 'Global Administrator' : 'Administrador Global',
      bgDot: 'bg-rose-500',
      text: isLight ? 'text-rose-700' : 'text-rose-400',
      desc: isEn ? 'Full root access: AI Retraining, user CRUD, full overrides' : 'Acceso total: Reentrenar IA, CRUD de usuarios, anular restricciones'
    },
    POLICY_ANALYST: { 
      badge: isLight ? 'bg-sky-100 text-sky-800 border-sky-300' : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40',
      label: isEn ? 'Policy Analyst' : 'Analista de Políticas',
      bgDot: 'bg-sky-500',
      text: isLight ? 'text-sky-700' : 'text-cyan-400',
      desc: isEn ? 'Policy adjustments, shockwave triggers, dataset inspection' : 'Ajuste de parámetros, ondas de choque, inspección de datasets'
    },
    RESEARCHER: { 
      badge: isLight ? 'bg-amber-100 text-amber-800 border-amber-300' : 'bg-amber-500/20 text-amber-300 border-amber-500/40',
      label: isEn ? 'Researcher / Inquiry' : 'Investigador / Consulta',
      bgDot: 'bg-amber-500',
      text: isLight ? 'text-amber-700' : 'text-amber-400',
      desc: isEn ? 'Read-only inquiry, telemetry observation, report export' : 'Lectura y consulta, observación de telemetría, exportación'
    },
  };

  const handleRoleChangeForNewUser = (r: UserRole) => {
    setNewRole(r);
    // Suggest standard permissions based on role
    setNewPermissions({
      editPolicies: r !== 'RESEARCHER',
      retrainAI: r === 'ADMIN',
      manageDatasets: r !== 'RESEARCHER',
      manageUsers: r === 'ADMIN',
      exportReports: true,
    });
  };

  // 1. CREATE USER
  const handleCreateUser = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim() || !newEmail.trim()) return;
    playHoloClick(1100);

    const created: UserAccount = {
      id: `usr-${Date.now().toString().slice(-4)}`,
      name: newName.trim(),
      email: newEmail.trim(),
      role: newRole,
      department: newDepartment.trim() || (isEn ? 'Labor Policy Bureau' : 'Departamento de Políticas Laborales'),
      lastActive: isEn ? 'Just created' : 'Recién creado',
      permissions: { ...newPermissions },
    };

    setUsers((prev) => [created, ...prev]);
    setNewName('');
    setNewEmail('');
    setShowAddUser(false);
  };

  // 2. START EDIT USER
  const handleStartEdit = (u: UserAccount) => {
    playHoloClick(800);
    setEditingUserId(u.id);
    setEditName(u.name);
    setEditEmail(u.email);
    setEditDepartment(u.department);
    setEditRole(u.role);
  };

  // 3. SAVE EDIT USER (UPDATE)
  const handleSaveEdit = (userId: string) => {
    playHoloClick(950);
    setUsers((prev) =>
      prev.map((u) => {
        if (u.id === userId) {
          return {
            ...u,
            name: editName.trim() || u.name,
            email: editEmail.trim() || u.email,
            department: editDepartment.trim() || u.department,
            role: editRole,
          };
        }
        return u;
      })
    );
    setEditingUserId(null);
  };

  // 4. DELETE USER (DELETE)
  const handleDeleteUser = (userId: string) => {
    playHoloClick(600);
    const userToDelete = users.find((u) => u.id === userId);
    // Prevent deleting the last ADMIN
    const adminCount = users.filter((u) => u.role === 'ADMIN').length;
    if (userToDelete?.role === 'ADMIN' && adminCount <= 1) {
      alert(isEn ? 'Cannot delete the only remaining Administrator!' : '¡No se puede eliminar al único Administrador restante del sistema!');
      setDeleteConfirmId(null);
      return;
    }

    setUsers((prev) => prev.filter((u) => u.id !== userId));
    setDeleteConfirmId(null);
  };

  // 5. TOGGLE PERMISSION
  const handleTogglePermission = (userId: string, permKey: keyof UserAccount['permissions']) => {
    playHoloClick(900);
    setUsers((prev) =>
      prev.map((u) => {
        if (u.id === userId) {
          return {
            ...u,
            permissions: {
              ...u.permissions,
              [permKey]: !u.permissions[permKey],
            },
          };
        }
        return u;
      })
    );
  };

  // 6. RESTORE DEFAULT USERS
  const handleRestoreDefaults = () => {
    playHoloClick(750);
    setUsers(MOCK_USERS);
  };

  // Filtered users list
  const filteredUsers = users.filter((u) => {
    const matchesSearch = 
      u.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.department.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = roleFilter === 'ALL' || u.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 md:p-6 bg-slate-950/80 backdrop-blur-xl animate-fadeIn"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className={`w-full max-w-5xl h-[88vh] rounded-3xl border shadow-2xl flex flex-col overflow-hidden transition-all duration-200 ${
        isLight
          ? 'bg-white border-slate-300 text-slate-800 shadow-slate-900/20'
          : 'hud-glass-solid border-cyan-500/40 text-slate-100'
      }`}>
        {/* HEADER: Title, RBAC overview, active session role switcher, and close */}
        <div className={`px-5 py-4 border-b flex flex-wrap items-center justify-between gap-3 ${
          isLight ? 'bg-slate-50/90 border-slate-200' : 'bg-slate-950/60 border-cyan-500/20'
        }`}>
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-2xl border ${
              isLight ? 'bg-rose-50 border-rose-300 text-rose-600' : 'bg-rose-500/20 border-rose-400 text-rose-300 glow-rose'
            }`}>
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className={`font-display font-bold text-base sm:text-lg tracking-wide ${
                  isLight ? 'text-slate-900' : 'text-slate-100'
                }`}>
                  {isEn ? 'USER & ROLE MANAGEMENT (CRUD RBAC)' : 'GESTIÓN DE USUARIOS Y ROLES (CRUD / RBAC)'}
                </h2>
                <span className={`text-[10px] font-mono-hud px-2 py-0.5 rounded font-bold border ${
                  isLight ? 'bg-rose-100 text-rose-800 border-rose-300' : 'bg-rose-950 text-rose-300 border-rose-700'
                }`}>
                  CRUD ACTIVO
                </span>
              </div>
              <p className={`text-xs font-mono-hud ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {isEn 
                  ? 'Manage system user accounts, reassign roles, toggle granular security permissions, or switch active session'
                  : 'Crea, edita y elimina usuarios, reasigna roles (ADMIN, ANALISTA, INVESTIGADOR) o asume roles en vivo'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                playHoloClick(900);
                setShowAddUser(!showAddUser);
              }}
              className={`px-3 py-1.5 rounded-xl border text-xs font-mono-hud font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                isLight
                  ? 'bg-rose-600 hover:bg-rose-700 text-white border-rose-600 shadow-sm'
                  : 'bg-rose-500/25 hover:bg-rose-500/40 text-rose-200 border-rose-400/50 glow-rose'
              }`}
            >
              <UserPlus className="w-4 h-4" />
              <span>{isEn ? 'New User' : 'Crear Usuario'}</span>
            </button>

            <button
              onClick={() => {
                playHoloClick(700);
                onClose();
              }}
              className={`p-2 rounded-xl border transition-colors cursor-pointer ${
                isLight
                  ? 'hover:bg-slate-200 text-slate-500 border-slate-300'
                  : 'hover:bg-slate-800 text-slate-400 hover:text-rose-400 border-slate-700'
              }`}
              title={isEn ? 'Close' : 'Cerrar'}
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* ACTIVE SESSION ROLE SELECTOR BAR */}
        <div className={`px-5 py-3 border-b flex flex-wrap items-center justify-between gap-3 text-xs font-mono-hud ${
          isLight ? 'bg-sky-50/60 border-slate-200' : 'bg-slate-900/50 border-cyan-500/20'
        }`}>
          <div className="flex items-center gap-2">
            <Key className={`w-4 h-4 ${isLight ? 'text-sky-600' : 'text-cyan-400'}`} />
            <span className={`font-bold ${isLight ? 'text-slate-800' : 'text-slate-200'}`}>
              {isEn ? 'Your Current Active Session Role:' : 'Tu Rol Activo en Esta Sesión:'}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {(['POLICY_ANALYST', 'ADMIN', 'RESEARCHER'] as UserRole[]).map((r) => {
              const isActive = currentRole === r;
              return (
                <button
                  key={r}
                  onClick={() => {
                    playHoloClick(1000);
                    onChangeRole(r);
                  }}
                  className={`px-3 py-1.5 rounded-xl border text-xs font-mono-hud flex items-center gap-2 transition-all cursor-pointer ${
                    isActive
                      ? isLight
                        ? 'bg-sky-700 text-white font-bold border-sky-700 shadow-md'
                        : 'bg-cyan-500 text-slate-950 font-bold border-cyan-400 shadow-lg glow-cyan'
                      : isLight
                        ? 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300'
                        : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-700'
                  }`}
                >
                  <span className={`w-2 h-2 rounded-full ${roleStyles[r].bgDot}`} />
                  <span>{roleStyles[r].label}</span>
                  {isActive && <Check className="w-3.5 h-3.5 ml-0.5" />}
                </button>
              );
            })}
          </div>
        </div>

        {/* CONTROLS BAR: Search, Filter Tabs, Restore Default */}
        <div className={`px-5 py-2.5 border-b flex flex-wrap items-center justify-between gap-2.5 ${
          isLight ? 'bg-white border-slate-200' : 'bg-slate-950/40 border-slate-800'
        }`}>
          {/* Search box */}
          <div className="relative flex-1 min-w-[200px] max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder={isEn ? 'Search user by name, email, or department...' : 'Buscar usuario por nombre, email o departamento...'}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`w-full pl-9 pr-3 py-1.5 rounded-xl text-xs font-mono-hud border outline-none transition-all ${
                isLight
                  ? 'bg-slate-50 border-slate-300 text-slate-800 focus:border-sky-500 focus:bg-white'
                  : 'bg-slate-900 border-slate-700 text-slate-200 focus:border-cyan-400 focus:bg-slate-950'
              }`}
            />
          </div>

          {/* Role filter buttons */}
          <div className="flex items-center gap-1.5">
            {(['ALL', 'ADMIN', 'POLICY_ANALYST', 'RESEARCHER'] as const).map((rf) => (
              <button
                key={rf}
                onClick={() => {
                  playHoloClick(800);
                  setRoleFilter(rf);
                }}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-mono-hud transition-all cursor-pointer border ${
                  roleFilter === rf
                    ? isLight
                      ? 'bg-slate-800 text-white font-bold border-slate-800'
                      : 'bg-cyan-500/20 text-cyan-300 font-bold border-cyan-500/60'
                    : isLight
                      ? 'bg-slate-100 hover:bg-slate-200 text-slate-600 border-slate-200'
                      : 'bg-slate-900 hover:bg-slate-800 text-slate-400 border-slate-800'
                }`}
              >
                {rf === 'ALL' ? (isEn ? 'All Users' : 'Todos') : roleStyles[rf].label}
              </button>
            ))}

            <button
              onClick={handleRestoreDefaults}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-mono-hud transition-all cursor-pointer border flex items-center gap-1 ${
                isLight
                  ? 'hover:bg-slate-100 text-slate-600 border-slate-200'
                  : 'hover:bg-slate-800 text-slate-400 border-slate-800'
              }`}
              title={isEn ? 'Reset to Mock Users' : 'Restablecer usuarios predeterminados'}
            >
              <RotateCcw className="w-3 h-3" />
              <span>{isEn ? 'Reset' : 'Restablecer'}</span>
            </button>
          </div>
        </div>

        {/* CONTENT BODY */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 font-mono-hud">
          {/* CREATE USER ACCORDION FORM */}
          {showAddUser && (
            <form
              onSubmit={handleCreateUser}
              className={`p-4 sm:p-5 rounded-2xl border space-y-4 animate-fadeIn ${
                isLight
                  ? 'bg-rose-50/50 border-rose-300 shadow-md'
                  : 'bg-slate-900/90 border-rose-500/40 shadow-xl'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <UserPlus className={`w-5 h-5 ${isLight ? 'text-rose-600' : 'text-rose-400'}`} />
                  <h3 className={`font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                    {isEn ? 'Create New User Account (RBAC Provisioning)' : 'Dar de Alta Nuevo Usuario (Provisión RBAC)'}
                  </h3>
                </div>
                <button
                  type="button"
                  onClick={() => setShowAddUser(false)}
                  className="p-1 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-400"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                  <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 block mb-1">
                    {isEn ? 'Full Name' : 'Nombre Completo'}
                  </label>
                  <input
                    type="text"
                    placeholder="Ej. Dra. Carmen Velasco"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    className={`w-full p-2 rounded-xl border text-xs outline-none ${
                      isLight
                        ? 'bg-white border-slate-300 text-slate-800 focus:border-rose-500'
                        : 'bg-slate-950 border-slate-700 text-slate-200 focus:border-rose-400'
                    }`}
                    required
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 block mb-1">
                    {isEn ? 'Email' : 'Correo Institucional'}
                  </label>
                  <input
                    type="email"
                    placeholder="c.velasco@ministerio-trabajo.gob"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    className={`w-full p-2 rounded-xl border text-xs outline-none ${
                      isLight
                        ? 'bg-white border-slate-300 text-slate-800 focus:border-rose-500'
                        : 'bg-slate-950 border-slate-700 text-slate-200 focus:border-rose-400'
                    }`}
                    required
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 block mb-1">
                    {isEn ? 'Department / Unit' : 'Departamento / Unidad'}
                  </label>
                  <input
                    type="text"
                    placeholder="Dirección General de Empleo"
                    value={newDepartment}
                    onChange={(e) => setNewDepartment(e.target.value)}
                    className={`w-full p-2 rounded-xl border text-xs outline-none ${
                      isLight
                        ? 'bg-white border-slate-300 text-slate-800 focus:border-rose-500'
                        : 'bg-slate-950 border-slate-700 text-slate-200 focus:border-rose-400'
                    }`}
                  />
                </div>
              </div>

              {/* Select Role for New User */}
              <div>
                <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 block mb-1.5">
                  {isEn ? 'Assign Role (Changes base capabilities)' : 'Asignar Rol (Determina las capacidades base)'}
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  {(['POLICY_ANALYST', 'ADMIN', 'RESEARCHER'] as UserRole[]).map((r) => (
                    <button
                      type="button"
                      key={r}
                      onClick={() => handleRoleChangeForNewUser(r)}
                      className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer ${
                        newRole === r
                          ? isLight
                            ? 'bg-white border-rose-500 shadow-sm'
                            : 'bg-slate-950 border-rose-400 shadow-md'
                          : isLight
                            ? 'bg-slate-100 hover:bg-slate-200 border-slate-200 text-slate-700'
                            : 'bg-slate-950/40 hover:bg-slate-900 border-slate-800 text-slate-400'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${roleStyles[r].bgDot}`} />
                        <span className="font-bold text-xs">{roleStyles[r].label}</span>
                      </div>
                      <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-1 leading-tight">
                        {roleStyles[r].desc}
                      </p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Initial Permissions Toggles */}
              <div className="pt-2 border-t border-slate-200 dark:border-slate-800">
                <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 block mb-1.5">
                  {isEn ? 'Customize Initial Permissions:' : 'Personalizar Permisos Iniciales:'}
                </span>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
                  {[
                    { key: 'editPolicies' as const, label: isEn ? 'Policy Sliders' : 'Ajuste Políticas' },
                    { key: 'retrainAI' as const, label: isEn ? 'Retrain AI' : 'Reentrenar IA' },
                    { key: 'manageDatasets' as const, label: isEn ? 'Datasets' : 'Gestionar Datos' },
                    { key: 'manageUsers' as const, label: isEn ? 'Manage Users' : 'Gestión Usuarios' },
                    { key: 'exportReports' as const, label: isEn ? 'Reports' : 'Exportar Reportes' },
                  ].map((perm) => (
                    <button
                      type="button"
                      key={perm.key}
                      onClick={() =>
                        setNewPermissions((prev) => ({ ...prev, [perm.key]: !prev[perm.key] }))
                      }
                      className={`p-2 rounded-xl text-left border flex items-center justify-between text-[11px] transition-all cursor-pointer ${
                        newPermissions[perm.key]
                          ? isLight
                            ? 'bg-emerald-50 border-emerald-300 text-emerald-800 font-bold'
                            : 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'
                          : isLight
                            ? 'bg-white border-slate-200 text-slate-400'
                            : 'bg-slate-950 border-slate-800 text-slate-500'
                      }`}
                    >
                      <span>{perm.label}</span>
                      {newPermissions[perm.key] ? (
                        <Check className="w-3.5 h-3.5 text-emerald-500" />
                      ) : (
                        <Lock className="w-3.5 h-3.5 text-slate-400" />
                      )}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddUser(false)}
                  className={`px-3 py-1.5 rounded-xl border text-xs font-semibold cursor-pointer ${
                    isLight
                      ? 'bg-white hover:bg-slate-100 text-slate-600 border-slate-300'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'
                  }`}
                >
                  {isEn ? 'Cancel' : 'Cancelar'}
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs shadow-md cursor-pointer flex items-center gap-1.5"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>{isEn ? 'Create Account' : 'Crear Usuario'}</span>
                </button>
              </div>
            </form>
          )}

          {/* USERS CARDS GRID (READ, UPDATE, DELETE, SWITCH) */}
          {filteredUsers.length === 0 ? (
            <div className={`text-center py-12 rounded-2xl border ${
              isLight ? 'bg-slate-50 border-slate-200' : 'bg-slate-900/40 border-slate-800'
            }`}>
              <Users className="w-8 h-8 mx-auto text-slate-400 mb-2" />
              <p className="text-sm font-bold text-slate-400">
                {isEn ? 'No users found matching the query.' : 'No se encontraron usuarios con ese criterio.'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredUsers.map((u) => {
                const isEditing = editingUserId === u.id;
                const isCurrentActive = currentRole === u.role;

                return (
                  <div
                    key={u.id}
                    className={`p-4 rounded-2xl border transition-all flex flex-col justify-between ${
                      isLight
                        ? 'bg-white border-slate-200 hover:border-slate-300 shadow-sm'
                        : 'bg-slate-900/70 border-slate-800 hover:border-cyan-500/40'
                    }`}
                  >
                    <div>
                      {/* Top bar of Card: User Initials, Name, Edit / Delete Actions */}
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2.5">
                          <div className={`w-9 h-9 rounded-xl flex items-center justify-center font-bold text-xs border ${
                            roleStyles[u.role].badge
                          }`}>
                            {u.name
                              .split(' ')
                              .filter(Boolean)
                              .slice(0, 2)
                              .map((n) => n[0])
                              .join('')
                              .toUpperCase()}
                          </div>
                          <div>
                            {isEditing ? (
                              <input
                                type="text"
                                value={editName}
                                onChange={(e) => setEditName(e.target.value)}
                                className={`p-1 rounded text-xs font-bold border outline-none ${
                                  isLight
                                    ? 'bg-slate-50 border-slate-300 text-slate-800'
                                    : 'bg-slate-950 border-slate-700 text-slate-200'
                                }`}
                              />
                            ) : (
                              <h4 className={`font-bold text-sm leading-tight ${
                                isLight ? 'text-slate-900' : 'text-slate-100'
                              }`}>
                                {u.name}
                              </h4>
                            )}
                            {isEditing ? (
                              <input
                                type="email"
                                value={editEmail}
                                onChange={(e) => setEditEmail(e.target.value)}
                                className={`p-1 rounded text-[10px] border outline-none mt-1 ${
                                  isLight
                                    ? 'bg-slate-50 border-slate-300 text-slate-800'
                                    : 'bg-slate-950 border-slate-700 text-slate-200'
                                }`}
                              />
                            ) : (
                              <span className="text-[10px] text-slate-400 flex items-center gap-1 mt-0.5">
                                <Mail className="w-3 h-3" /> {u.email}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Top Action Icons (Edit & Delete) */}
                        <div className="flex items-center gap-1">
                          {isEditing ? (
                            <button
                              onClick={() => handleSaveEdit(u.id)}
                              className="p-1.5 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 cursor-pointer shadow-sm"
                              title={isEn ? 'Save Changes' : 'Guardar Cambios'}
                            >
                              <Save className="w-3.5 h-3.5" />
                            </button>
                          ) : (
                            <button
                              onClick={() => handleStartEdit(u)}
                              className={`p-1.5 rounded-lg border transition-colors cursor-pointer ${
                                isLight
                                  ? 'hover:bg-slate-100 text-slate-500 border-slate-200'
                                  : 'hover:bg-slate-800 text-slate-400 hover:text-cyan-300 border-slate-800'
                              }`}
                              title={isEn ? 'Edit User (Update)' : 'Editar Usuario (CRUD)'}
                            >
                              <Edit3 className="w-3.5 h-3.5" />
                            </button>
                          )}

                          <button
                            onClick={() => {
                              if (deleteConfirmId === u.id) {
                                handleDeleteUser(u.id);
                              } else {
                                playHoloClick(700);
                                setDeleteConfirmId(u.id);
                              }
                            }}
                            className={`p-1.5 rounded-lg border transition-colors cursor-pointer ${
                              deleteConfirmId === u.id
                                ? 'bg-rose-600 text-white border-rose-600 animate-pulse'
                                : isLight
                                  ? 'hover:bg-rose-50 text-slate-400 hover:text-rose-600 border-slate-200'
                                  : 'hover:bg-rose-950 text-slate-500 hover:text-rose-400 border-slate-800'
                            }`}
                            title={deleteConfirmId === u.id ? (isEn ? 'Confirm Delete' : 'Confirmar Eliminación') : (isEn ? 'Delete User' : 'Eliminar Usuario')}
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>

                      {/* Department & Role Badge */}
                      <div className="mt-2.5 flex items-center justify-between gap-2">
                        {isEditing ? (
                          <input
                            type="text"
                            value={editDepartment}
                            onChange={(e) => setEditDepartment(e.target.value)}
                            placeholder="Departamento"
                            className={`p-1 rounded text-[10px] border outline-none flex-1 ${
                              isLight
                                ? 'bg-slate-50 border-slate-300 text-slate-800'
                                : 'bg-slate-950 border-slate-700 text-slate-200'
                            }`}
                          />
                        ) : (
                          <div className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-1.5 truncate">
                            <Building className="w-3 h-3 text-slate-400" />
                            <span className="truncate">{u.department}</span>
                          </div>
                        )}

                        {isEditing ? (
                          <select
                            value={editRole}
                            onChange={(e) => setEditRole(e.target.value as UserRole)}
                            className={`p-1 rounded text-[10px] font-bold border outline-none ${
                              isLight
                                ? 'bg-slate-50 border-slate-300 text-slate-800'
                                : 'bg-slate-950 border-slate-700 text-slate-200'
                            }`}
                          >
                            <option value="POLICY_ANALYST">{roleStyles.POLICY_ANALYST.label}</option>
                            <option value="ADMIN">{roleStyles.ADMIN.label}</option>
                            <option value="RESEARCHER">{roleStyles.RESEARCHER.label}</option>
                          </select>
                        ) : (
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border whitespace-nowrap ${roleStyles[u.role].badge}`}>
                            {roleStyles[u.role].label}
                          </span>
                        )}
                      </div>

                      {/* Role Switcher Action (Quick Switch session to this user's role) */}
                      <div className="mt-3 pt-2 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
                        <span className="text-[10px] text-slate-400">
                          {isCurrentActive ? (
                            <span className="text-emerald-500 font-bold flex items-center gap-1">
                              <UserCheck className="w-3 h-3" />
                              {isEn ? 'Active in Session' : 'Rol Activo en Sesión'}
                            </span>
                          ) : (
                            <span>{u.lastActive}</span>
                          )}
                        </span>

                        <button
                          onClick={() => {
                            playHoloClick(1000);
                            onChangeRole(u.role);
                          }}
                          className={`px-2 py-0.8 rounded-lg text-[10px] font-mono-hud font-bold border transition-all cursor-pointer flex items-center gap-1 ${
                            isCurrentActive
                              ? isLight
                                ? 'bg-emerald-50 border-emerald-400 text-emerald-700'
                                : 'bg-emerald-950/60 border-emerald-500 text-emerald-300'
                              : isLight
                                ? 'bg-slate-100 hover:bg-sky-50 text-slate-700 hover:text-sky-700 border-slate-300'
                                : 'bg-slate-800 hover:bg-cyan-950 text-slate-300 hover:text-cyan-300 border-slate-700'
                          }`}
                        >
                          <ShieldCheck className="w-3 h-3" />
                          <span>{isCurrentActive ? (isEn ? 'Assumed' : 'Asumido') : (isEn ? 'Assume Role' : 'Asumir Rol')}</span>
                        </button>
                      </div>

                      {/* Permissions Matrix */}
                      <div className="mt-2.5 pt-2 border-t border-slate-200 dark:border-slate-800 space-y-1 text-[10px]">
                        <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold block">
                          {isEn ? 'Module Permissions (Click to toggle):' : 'Permisos de Módulo (Clic para alternar):'}
                        </span>
                        
                        <div className="grid grid-cols-2 gap-1">
                          {[
                            { key: 'editPolicies' as const, label: isEn ? 'Policy Tuning' : 'Parámetros Políticas' },
                            { key: 'retrainAI' as const, label: isEn ? 'Retrain AI' : 'Reentrenar Motor IA' },
                            { key: 'manageDatasets' as const, label: isEn ? 'Datasets' : 'Gestión Datasets' },
                            { key: 'manageUsers' as const, label: isEn ? 'RBAC & Users' : 'Gestión Usuarios' },
                          ].map((perm) => {
                            const isGranted = u.permissions[perm.key];
                            return (
                              <button
                                key={perm.key}
                                onClick={() => handleTogglePermission(u.id, perm.key)}
                                className={`p-1 rounded flex items-center justify-between text-left transition-colors cursor-pointer border ${
                                  isGranted
                                    ? isLight
                                      ? 'bg-sky-50 border-sky-200 text-sky-800'
                                      : 'bg-cyan-950/40 border-cyan-500/30 text-cyan-300'
                                    : isLight
                                      ? 'bg-slate-50 border-slate-200 text-slate-400'
                                      : 'bg-slate-950 border-slate-800 text-slate-500'
                                }`}
                              >
                                <span className="truncate">{perm.label}</span>
                                {isGranted ? <Check className="w-3 h-3 text-emerald-500" /> : <Lock className="w-3 h-3 opacity-50" />}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    </div>

                    {/* Delete Confirmation Warning if clicked */}
                    {deleteConfirmId === u.id && (
                      <div className="mt-2 p-2 rounded-xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-between text-[11px]">
                        <div className="flex items-center gap-1.5 text-rose-400">
                          <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />
                          <span>{isEn ? 'Confirm delete?' : '¿Eliminar cuenta?'}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => setDeleteConfirmId(null)}
                            className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]"
                          >
                            {isEn ? 'No' : 'No'}
                          </button>
                          <button
                            onClick={() => handleDeleteUser(u.id)}
                            className="px-2 py-0.5 rounded bg-rose-600 text-white font-bold text-[10px]"
                          >
                            {isEn ? 'Yes, Delete' : 'Sí, Eliminar'}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* FOOTER: Status summary & help note */}
        <div className={`px-5 py-3 border-t flex flex-wrap items-center justify-between gap-2 text-xs font-mono-hud ${
          isLight ? 'bg-slate-50 border-slate-200 text-slate-600' : 'bg-slate-950/60 border-cyan-500/20 text-slate-400'
        }`}>
          <div className="flex items-center gap-3">
            <span>
              {isEn ? 'Total Accounts:' : 'Cuentas Registradas:'} <strong>{users.length}</strong>
            </span>
            <span>•</span>
            <span className={roleStyles.ADMIN.text}>
              ADMIN: <strong>{users.filter((u) => u.role === 'ADMIN').length}</strong>
            </span>
            <span>•</span>
            <span className={roleStyles.POLICY_ANALYST.text}>
              ANALYST: <strong>{users.filter((u) => u.role === 'POLICY_ANALYST').length}</strong>
            </span>
            <span>•</span>
            <span className={roleStyles.RESEARCHER.text}>
              RESEARCHER: <strong>{users.filter((u) => u.role === 'RESEARCHER').length}</strong>
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                playHoloClick(700);
                onClose();
              }}
              className={`px-4 py-1.5 rounded-xl border text-xs font-bold transition-all cursor-pointer ${
                isLight
                  ? 'bg-slate-800 hover:bg-slate-900 text-white border-slate-800'
                  : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 border-cyan-400 font-bold'
              }`}
            >
              {isEn ? 'Done / Return' : 'Listo / Regresar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
