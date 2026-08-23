import { useCallback, useEffect, useState } from "react";
import { AdminPortal } from "./features/admin/AdminPortal";
import { useAuth } from "./features/auth/AuthContext";
import { LoginPage } from "./features/auth/LoginPage";
import { LecturerPortal } from "./features/lecturer/LecturerPortal";
import { TrainingOfficePortal } from "./features/training-office/TrainingOfficePortal";
import type { UserRole } from "./types";

const routesByRole: Record<UserRole, readonly string[]> = {
  ADMIN: ["/admin/accounts", "/admin/audit"],

  TRAINING_OFFICE: [
    "/training-office/overview",
    "/training-office/import",
    "/training-office/ga",
    "/training-office/results",
    "/training-office/adjustments",
    "/training-office/requests",
  ],

  LECTURER: [
    "/lecturer/timetable",
    "/lecturer/course-sections",
    "/lecturer/requests/new",
    "/lecturer/requests",
  ],
};

const defaultRoutes: Record<UserRole, string> = {
  ADMIN: "/admin/accounts",
  TRAINING_OFFICE: "/training-office/overview",
  LECTURER: "/lecturer/timetable",
};

const knownRoutes = Object.values(routesByRole).flat();

function readHashPath(): string {
  const value = window.location.hash.replace(/^#/, "").trim();

  if (value.startsWith("/")) {
    return value;
  }

  if (value) {
    return `/${value}`;
  }

  return "/";
}

function getDefaultRoute(role: UserRole): string {
  return defaultRoutes[role] ?? "/login";
}

export function App() {
  const auth = useAuth();

  const [path, setPath] = useState<string>(() => readHashPath());

  const navigate = useCallback(
    (nextPath: string | undefined | null, replace = false) => {      if (!nextPath) {
        nextPath = "/login";
      }

      const target = nextPath.startsWith("/")
        ? nextPath
        : `/${nextPath}`;

      if (replace) {
        window.history.replaceState(
          null,
          "",
          `${window.location.pathname}${window.location.search}#${target}`,
        );
      } else {
        window.location.hash = target;
      }

      setPath(target);
    },
    [],
  );

  useEffect(() => {
    const onHashChange = () => {
      setPath(readHashPath());
    };

    window.addEventListener("hashchange", onHashChange);

    return () => {
      window.removeEventListener("hashchange", onHashChange);
    };
  }, []);

  useEffect(() => {
    if (auth.status === "anonymous" && path !== "/login") {
      navigate("/login", true);
      return;
    }

    if (
      auth.status === "authenticated" &&
      auth.user
    ) {
      const role = auth.user.role;

      if (
        role !== "ADMIN" &&
        role !== "TRAINING_OFFICE" &&
        role !== "LECTURER"
      ) {
        console.error("Role không hợp lệ từ backend:", role);

        navigate("/login", true);
        return;
      }

      if (path === "/" || path === "/login") {
        navigate(getDefaultRoute(role), true);
        return;
      }

      if (!knownRoutes.includes(path)) {
        navigate(getDefaultRoute(role), true);
        return;
      }
    }
  }, [auth.status, auth.user, path, navigate]);

  if (auth.status === "checking") {
    return (
      <FullPageState
        title="Đang kiểm tra phiên đăng nhập"
        message="Vui lòng chờ trong giây lát..."
      />
    );
  }

  if (auth.status === "error") {
    return (
      <FullPageState
        title="Không thể kết nối hệ thống"
        message={
          auth.error ||
          "Không thể kiểm tra phiên đăng nhập."
        }
        actionLabel="Thử lại"
        onAction={() => void auth.retry()}
      />
    );
  }
 if (auth.status === "anonymous" || !auth.user) {
  return <LoginPage />;
}

  const user = auth.user;

  
  if (
    user.role !== "ADMIN" &&
    user.role !== "TRAINING_OFFICE" &&
    user.role !== "LECTURER"
  ) {
    return (
      <FullPageState
        title="Role không hợp lệ"
        message={`Backend trả về role không được hỗ trợ: ${String(
          user.role,
        )}`}
        actionLabel="Đăng nhập lại"
        onAction={() => navigate("/login", true)}
      />
    );
  }

  if (path === "/" || path === "/login") {
    return (
      <FullPageState
        title="Đang mở cổng làm việc"
        message="Vui lòng chờ..."
      />
    );
  }

  if (!knownRoutes.includes(path)) {
    return (
      <FullPageState
        title="Đang điều hướng"
        message="Đường dẫn không hợp lệ, hệ thống đang đưa bạn về trang phù hợp."
      />
    );
  }

  
  if (!routesByRole[user.role].includes(path)) {
    return (
      <ForbiddenPage
        onBack={() =>
          navigate(getDefaultRoute(user.role))
        }
      />
    );
  }

  const common = {
    user,
    path,
    onNavigate: navigate,
    onLogout: auth.logout,
  };

  if (user.role === "ADMIN") {
    return <AdminPortal {...common} />;
  }

  if (user.role === "LECTURER") {
    return <LecturerPortal {...common} />;
  }

  return <TrainingOfficePortal {...common} />;
}

function FullPageState({
  title,
  message,
  actionLabel,
  onAction,
}: {
  title: string;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <main className="full-page-state">
      <section className="panel">
        <div className="state-mark" aria-hidden="true">
          TKB
        </div>

        <h1>{title}</h1>

        <p>{message}</p>

        {actionLabel && onAction && (
          <button
            type="button"
            onClick={onAction}
          >
            {actionLabel}
          </button>
        )}
      </section>
    </main>
  );
}

function ForbiddenPage({
  onBack,
}: {
  onBack: () => void;
}) {
  return (
    <main className="full-page-state">
      <section className="panel">
        <div
          className="state-mark warning"
          aria-hidden="true"
        >
          !
        </div>

        <p className="eyebrow">
          Không có quyền truy cập
        </p>

        <h1>Bạn không thể mở trang này</h1>

        <p>
          Tài khoản hiện tại không có quyền sử dụng
          chức năng được yêu cầu.
        </p>

        <button
          type="button"
          onClick={onBack}
        >
          Về cổng làm việc của tôi
        </button>
      </section>
    </main>
  );
}