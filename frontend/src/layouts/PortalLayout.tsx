import { useState } from "react";
import type { AuthUser, UserRole } from "../types";

export interface NavigationItem {
  path: string;
  label: string;
}

const roleLabels: Record<UserRole, string> = {
  ADMIN: "Quản trị viên",
  TRAINING_OFFICE: "Phòng Đào tạo",
  LECTURER: "Giảng viên",
};

interface PortalLayoutProps {
  user: AuthUser;
  navigation: NavigationItem[];
  currentPath: string;
  onNavigate: (path: string) => void;
  onLogout: () => void | Promise<void>;
  eyebrow: string;
  title: string;
  description: string;
  children: React.ReactNode;
  connection?: { online: boolean; label: string };
}

export function PortalLayout({ user, navigation, currentPath, onNavigate, onLogout, eyebrow, title, description, children, connection }: PortalLayoutProps) {
  const [loggingOut, setLoggingOut] = useState(false);
  const [logoutError, setLogoutError] = useState<string | null>(null);

  const logout = async () => {
    setLoggingOut(true);
    setLogoutError(null);
    try { await onLogout(); }
    catch (cause) { setLogoutError(cause instanceof Error ? cause.message : "Không thể đăng xuất. Vui lòng thử lại."); }
    finally { setLoggingOut(false); }
  };

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span>TKB</span><div><strong>Timetable GA</strong><small>{roleLabels[user.role]}</small></div></div>
      <nav aria-label="Điều hướng chính">{navigation.map((item) => <button className={currentPath === item.path ? "active" : ""} key={item.path} onClick={() => onNavigate(item.path)}>{item.label}</button>)}</nav>
      <div className="sidebar-user"><strong>{user.display_name}</strong><span>{user.username}</span><button type="button" className="sidebar-logout" disabled={loggingOut} onClick={() => void logout()}>{loggingOut ? "Đang đăng xuất..." : "Đăng xuất"}</button></div>
      {connection && <p className={`connection ${connection.online ? "online" : ""}`}>{connection.label}</p>}
    </aside>
    <main>
      <header className="portal-header"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p>{description}</p></div><div className="user-chip"><span>{roleLabels[user.role]}</span><strong>{user.display_name}</strong></div></header>
      {logoutError && <div className="alert error" role="alert">{logoutError}</div>}
      {children}
    </main>
  </div>;
}

export function roleLabel(role: UserRole) {
  return roleLabels[role];
}
