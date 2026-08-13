import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { ApiError, api, setUnauthorizedHandler } from "../../api/client";
import type { AuthUser } from "../../types";

type AuthStatus = "checking" | "authenticated" | "anonymous" | "error";

interface AuthContextValue {
  status: AuthStatus;
  user: AuthUser | null;
  error: string | null;
  notice: string | null;
  login: (username: string, password: string) => Promise<AuthUser>;
  logout: () => Promise<void>;
  retry: () => Promise<void>;
  dismissNotice: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const fallbackError = "Không thể kiểm tra phiên đăng nhập. Vui lòng thử lại.";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("checking");
  const [user, setUser] = useState<AuthUser | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const clearSession = useCallback((message?: string) => {
    setUser(null);
    setStatus("anonymous");
    setError(null);
    if (message) setNotice(message);
  }, []);

  const retry = useCallback(async () => {
    setStatus("checking");
    setError(null);
    try {
      const currentUser = await api.me();
      setUser(currentUser);
      setStatus("authenticated");
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 401) {
        clearSession();
        return;
      }
      setUser(null);
      setStatus("error");
      setError(cause instanceof Error ? cause.message : fallbackError);
    }
  }, [clearSession]);

  useEffect(() => { void retry(); }, [retry]);
  useEffect(() => {
    setUnauthorizedHandler(() => clearSession("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại."));
    return () => setUnauthorizedHandler(null);
  }, [clearSession]);

  const login = useCallback(async (username: string, password: string) => {
    const result = await api.login(username, password);
    setUser(result.user);
    setStatus("authenticated");
    setError(null);
    setNotice(null);
    return result.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.logout();
      clearSession("Bạn đã đăng xuất an toàn.");
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 401) {
        clearSession("Phiên đăng nhập đã kết thúc. Vui lòng đăng nhập lại.");
        return;
      }
      const message = cause instanceof Error ? cause.message : "Không thể đăng xuất. Vui lòng thử lại.";
      setError(message);
      throw cause instanceof Error ? cause : new Error(message);
    }
  }, [clearSession]);

  const value = useMemo<AuthContextValue>(() => ({
    status,
    user,
    error,
    notice,
    login,
    logout,
    retry,
    dismissNotice: () => setNotice(null),
  }), [status, user, error, notice, login, logout, retry]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth phải được sử dụng bên trong AuthProvider.");
  return context;
}
