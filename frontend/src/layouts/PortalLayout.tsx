import { useState, type ReactNode } from "react";
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
  children: ReactNode;
  connection?: {
    online: boolean;
    label: string;
  };
}

export function PortalLayout({
  user,
  navigation,
  currentPath,
  onNavigate,
  onLogout,
  eyebrow,
  title,
  description,
  children,
  connection,
}: PortalLayoutProps) {
  const [loggingOut, setLoggingOut] = useState(false);
  const [logoutError, setLogoutError] = useState<string | null>(null);

  const logout = async () => {
    setLoggingOut(true);
    setLogoutError(null);

    try {
      await onLogout();
    } catch (cause) {
      setLogoutError(
        cause instanceof Error
          ? cause.message
          : "Không thể đăng xuất."
      );
    } finally {
      setLoggingOut(false);
    }
  };

  return (
    <div className="app-shell top-layout">
      <header className="school-header">

        {}
        <div className="school-header-main">

          {}
          <button
            type="button"
            className="school-brand"
            onClick={() =>
              onNavigate(navigation[0]?.path || "/")
            }
          >
            <span className="school-logo-box">
              <img
                src="https://giaoduc247.vn/uploads/082021/images/Screenshot%202023-07-01%20at%2017_35_36.png"
                alt="Logo HUIT"
              />
            </span>

            <span className="school-brand-text">
              <strong>
                Đại học Công Thương TP.HCM
              </strong>

              <small>
                Hệ thống xếp thời khóa biểu ·{" "}
                {roleLabels[user.role]}
              </small>
            </span>
          </button>

          {}
          <div className="header-user">

            {connection && (
              <span
                className={`top-connection ${
                  connection.online
                    ? "online"
                    : ""
                }`}
              >
                {connection.label}
              </span>
            )}

            <span className="header-avatar">
              {user.display_name
                .trim()
                .charAt(0)
                .toUpperCase() || "U"}
            </span>

            <span className="header-user-copy">
              <strong>
                {user.display_name}
              </strong>

              <small>
                {user.username} ·{" "}
                {roleLabels[user.role]}
              </small>
            </span>

            <button
              type="button"
              className="header-logout"
              disabled={loggingOut}
              onClick={() => void logout()}
            >
              {loggingOut
                ? "Đang đăng xuất..."
                : "Đăng xuất"}
            </button>
          </div>
        </div>

        {}
        <nav
          className="top-navigation"
          aria-label="Điều hướng chính"
        >
          {navigation.map((item) => (
            <button
              type="button"
              key={item.path}
              className={
                currentPath === item.path
                  ? "active"
                  : ""
              }
              onClick={() =>
                onNavigate(item.path)
              }
            >
              {item.label}
            </button>
          ))}
        </nav>
      </header>

      {}
      <main className="portal-content">

        <header className="portal-header clean-header">
          <div>
            <p className="eyebrow">
              {eyebrow}
            </p>

            <h1>{title}</h1>

            <p>{description}</p>
          </div>
        </header>

        {logoutError && (
          <div
            className="alert error"
            role="alert"
          >
            {logoutError}
          </div>
        )}

        {children}
      </main>
    </div>
  );
}

export function roleLabel(role: UserRole) {
  return roleLabels[role];
}