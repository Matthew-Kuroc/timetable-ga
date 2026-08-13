import { useCallback, useEffect, useState } from "react";
import { AdminPortal } from "./features/admin/AdminPortal";
import { useAuth } from "./features/auth/AuthContext";
import { LoginPage } from "./features/auth/LoginPage";
import { LecturerPortal } from "./features/lecturer/LecturerPortal";
import { TrainingOfficePortal } from "./features/training-office/TrainingOfficePortal";
import type { UserRole } from "./types";

const routesByRole: Record<UserRole, readonly string[]> = {
  ADMIN: ["/admin/accounts", "/admin/audit"],
  TRAINING_OFFICE: ["/training-office/overview", "/training-office/import", "/training-office/ga", "/training-office/results", "/training-office/adjustments", "/training-office/requests"],
  LECTURER: ["/lecturer/timetable", "/lecturer/course-sections", "/lecturer/requests/new", "/lecturer/requests"],
};
const defaultRoutes: Record<UserRole, string> = {
  ADMIN: "/admin/accounts",
  TRAINING_OFFICE: "/training-office/overview",
  LECTURER: "/lecturer/timetable",
};
const knownRoutes = Object.values(routesByRole).flat();

function readHashPath() {
  const value = location.hash.replace(/^#/, "").trim();
  return value.startsWith("/") ? value : value ? `/${value}` : "/";
}

export function App() {
  const auth = useAuth();
  const [path, setPath] = useState(readHashPath);
  const navigate = useCallback((nextPath: string, replace = false) => {
    const target = nextPath.startsWith("/") ? nextPath : `/${nextPath}`;
    if (replace) history.replaceState(null, "", `${location.pathname}${location.search}#${target}`);
    else location.hash = target;
    setPath(target);
  }, []);

  useEffect(() => {
    const onHashChange = () => setPath(readHashPath());
    addEventListener("hashchange", onHashChange);
    return () => removeEventListener("hashchange", onHashChange);
  }, []);

  useEffect(() => {
    if (auth.status === "anonymous" && path !== "/login") navigate("/login", true);
    if (auth.status === "authenticated" && auth.user && (path === "/" || path === "/login")) navigate(defaultRoutes[auth.user.role], true);
    if (auth.status === "authenticated" && auth.user && path !== "/" && path !== "/login" && !knownRoutes.includes(path)) navigate(defaultRoutes[auth.user.role], true);
  }, [auth.status, auth.user, path, navigate]);

  if (auth.status === "checking") return <FullPageState title="Đang kiểm tra phiên đăng nhập" message="Vui lòng chờ trong giây lát..." />;
  if (auth.status === "error") return <FullPageState title="Không thể kết nối hệ thống" message={auth.error || "Không thể kiểm tra phiên đăng nhập."} actionLabel="Thử lại" onAction={() => void auth.retry()} />;
  if (auth.status === "anonymous" || !auth.user) return <LoginPage onAuthenticated={() => navigate("/", true)} />;

  const user = auth.user;
  if (path === "/" || path === "/login") return <FullPageState title="Đang mở cổng làm việc" message="Vui lòng chờ..." />;
  if (!knownRoutes.includes(path)) return <FullPageState title="Đang điều hướng" message="Đường dẫn không hợp lệ, hệ thống đang đưa bạn về trang phù hợp." />;
  if (!routesByRole[user.role].includes(path)) return <ForbiddenPage onBack={() => navigate(defaultRoutes[user.role])} />;

  const common = { user, path, onNavigate: navigate, onLogout: auth.logout };
  if (user.role === "ADMIN") return <AdminPortal {...common} />;
  if (user.role === "LECTURER") return <LecturerPortal {...common} />;
  return <TrainingOfficePortal {...common} />;
}

function FullPageState({ title, message, actionLabel, onAction }: { title: string; message: string; actionLabel?: string; onAction?: () => void }) {
  return <main className="full-page-state"><section className="panel"><div className="state-mark" aria-hidden="true">TKB</div><h1>{title}</h1><p>{message}</p>{actionLabel && onAction && <button type="button" onClick={onAction}>{actionLabel}</button>}</section></main>;
}

function ForbiddenPage({ onBack }: { onBack: () => void }) {
  return <main className="full-page-state"><section className="panel"><div className="state-mark warning" aria-hidden="true">!</div><p className="eyebrow">Không có quyền truy cập</p><h1>Bạn không thể mở trang này</h1><p>Tài khoản hiện tại không có quyền sử dụng chức năng được yêu cầu.</p><button type="button" onClick={onBack}>Về cổng làm việc của tôi</button></section></main>;
}
