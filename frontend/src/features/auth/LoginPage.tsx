import { FormEvent, useState } from "react";
import { useAuth } from "./AuthContext";

export function LoginPage({ onAuthenticated }: { onAuthenticated: () => void }) {
  const { login, notice, dismissNotice } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(username.trim(), password);
      setPassword("");
      onAuthenticated();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Không thể đăng nhập. Vui lòng thử lại.");
    } finally {
      setBusy(false);
    }
  };

  return <main className="login-page">
    <section className="login-card" aria-labelledby="login-title">
      <div className="login-brand"><span>TKB</span><div><strong>Timetable GA</strong><small>Ứng dụng xếp lịch giảng dạy</small></div></div>
      <p className="eyebrow">Đăng nhập hệ thống</p>
      <h1 id="login-title">Chào mừng bạn quay lại</h1>
      <p>Sử dụng tài khoản đã được Quản trị viên cấp. Hệ thống không hỗ trợ đăng ký công khai.</p>
      {notice && <div className="alert success" role="status"><span>{notice}</span><button type="button" onClick={dismissNotice} aria-label="Đóng thông báo">×</button></div>}
      {error && <div className="alert error" role="alert">{error}</div>}
      <form className="login-form" onSubmit={submit}>
        <label>Tên đăng nhập <span aria-hidden="true">*</span><input autoComplete="username" autoFocus value={username} onChange={(event) => setUsername(event.target.value)} required /></label>
        <label>Mật khẩu <span aria-hidden="true">*</span><input type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
        <button disabled={busy || !username.trim() || !password}>{busy ? "Đang đăng nhập..." : "Đăng nhập"}</button>
      </form>
      <small className="login-help">Nếu tài khoản bị khóa hoặc chưa được cấp, vui lòng liên hệ Quản trị viên.</small>
    </section>
  </main>;
}
