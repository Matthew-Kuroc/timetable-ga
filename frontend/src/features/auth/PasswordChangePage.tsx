import { FormEvent, useState } from "react";
import { api } from "../../api/client";

export function PasswordChangePage({ username }: { username: string }) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (newPassword !== confirmation) { setError("Mật khẩu xác nhận không khớp."); return; }
    setBusy(true); setError(null);
    try { await api.changePassword({ current_password: currentPassword, new_password: newPassword }); window.location.reload(); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Không thể đổi mật khẩu."); }
    finally { setBusy(false); }
  };
  return <main className="full-page-state"><section className="panel password-change-panel"><p className="eyebrow">Bảo mật tài khoản</p><h1>Đổi mật khẩu trước khi tiếp tục</h1><p>Tài khoản <strong>{username}</strong> đang dùng mật khẩu tạm. Hãy đặt mật khẩu riêng để mở cổng làm việc.</p><form className="form-grid" onSubmit={submit}><label>Mật khẩu hiện tại<input type="password" autoComplete="current-password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} required /></label><label>Mật khẩu mới<input type="password" autoComplete="new-password" minLength={8} value={newPassword} onChange={(event) => setNewPassword(event.target.value)} required /></label><label>Nhập lại mật khẩu mới<input type="password" autoComplete="new-password" minLength={8} value={confirmation} onChange={(event) => setConfirmation(event.target.value)} required /></label>{error && <div className="alert error" role="alert">{error}</div>}<button disabled={busy}>{busy ? "Đang cập nhật..." : "Đổi mật khẩu"}</button></form></section></main>;
}
