import { useState, type FormEvent } from "react";
import { useAuth } from "./AuthContext";

export function LoginPage() {
  const { login } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();

    setLoading(true);
    setError(null);

    try {
      await login(username, password);
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Đăng nhập không thành công."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-shell">

        {}
        <div className="login-brand-panel">
          <div className="login-brand-header">
            <img
              className="login-school-logo"
              src="https://giaoduc247.vn/uploads/082021/images/Screenshot%202023-07-01%20at%2017_35_36.png"
              alt="Logo HUIT"
            />

            <div>
              <strong>
                Đại học Công Thương TP.HCM
              </strong>

              <span>
                Hệ thống xếp thời khóa biểu
              </span>
            </div>
          </div>

          <div className="login-brand-content">
            <p className="eyebrow">
              Hệ thống quản lý thời khóa biểu
            </p>

            <h1>
              Xếp lịch giảng dạy
              <br />
              thông minh và trực quan
            </h1>

            <p>
              Hỗ trợ quản lý lịch giảng dạy,
              theo dõi thời khóa biểu và xử lý
              yêu cầu điều chỉnh theo từng
              vai trò người dùng.
            </p>
          </div>

          <div className="login-brand-footer">
            <span>
              Genetic Algorithm Scheduling System
            </span>
          </div>
        </div>

        {}
        <div className="login-form-panel">
          <form
            className="login-card"
            onSubmit={submit}
          >
            <div className="login-card-heading">
              <p className="eyebrow">
                Đăng nhập hệ thống
              </p>

              <h2>
                Chào mừng bạn quay lại
              </h2>

              <p>
                Sử dụng tài khoản đã được
                quản trị viên cấp để truy cập
                đúng chức năng theo vai trò.
              </p>
            </div>

            {error && (
              <div
                className="alert error"
                role="alert"
              >
                {error}
              </div>
            )}

            <label className="login-field">
              <span>
                Tên đăng nhập
              </span>

              <input
                type="text"
                value={username}
                autoComplete="username"
                disabled={loading}
                onChange={(event) =>
                  setUsername(
                    event.target.value
                  )
                }
                placeholder="Nhập tên đăng nhập"
              />
            </label>

            <label className="login-field">
              <span>
                Mật khẩu
              </span>

              <input
                type="password"
                value={password}
                autoComplete="current-password"
                disabled={loading}
                onChange={(event) =>
                  setPassword(
                    event.target.value
                  )
                }
                placeholder="Nhập mật khẩu"
              />
            </label>

            <button
              type="submit"
              className="login-submit"
              disabled={
                loading ||
                !username.trim() ||
                !password
              }
            >
              {loading
                ? "Đang đăng nhập..."
                : "Đăng nhập"}
            </button>

            <p className="login-note">
              Quyền truy cập được xác định
              bởi vai trò của tài khoản:
              Quản trị viên, Phòng Đào tạo
              hoặc Giảng viên.
            </p>
          </form>
        </div>
      </section>
    </main>
  );
}