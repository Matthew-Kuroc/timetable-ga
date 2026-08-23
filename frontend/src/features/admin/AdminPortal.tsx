import {
  FormEvent,
  useCallback,
  useEffect,
  useState,
} from "react";

import { api } from "../../api/client";

import {
  PortalLayout,
  roleLabel,
} from "../../layouts/PortalLayout";

import type {
  AdminUser,
  AuditLog,
  AuthUser,
  UserRole,
  UserWriteInput,
} from "../../types";

interface AdminPortalProps {
  user: AuthUser;
  path: string;
  onNavigate: (path: string) => void;
  onLogout: () => void | Promise<void>;
}

const navigation = [
  {
    path: "/admin/accounts",
    label: "Quản lý tài khoản",
  },
  {
    path: "/admin/audit",
    label: "Nhật ký tài khoản",
  },
];

const pageSize = 20;

export function AdminPortal({
  user,
  path,
  onNavigate,
  onLogout,
}: AdminPortalProps) {
  const auditPage =
    path === "/admin/audit";

  return (
    <PortalLayout
      user={user}
      navigation={navigation}
      currentPath={path}
      onNavigate={onNavigate}
      onLogout={onLogout}
      eyebrow="Cổng Quản trị viên"
      title={
        auditPage
          ? "Nhật ký tài khoản và xác thực"
          : "Quản lý tài khoản"
      }
      description={
        auditPage
          ? "Theo dõi các thao tác quản trị và hoạt động đăng nhập đã được ghi nhận."
          : "Cấp tài khoản, gán vai trò và kiểm soát trạng thái truy cập hệ thống."
      }
    >
      {auditPage ? (
        <AuditPage />
      ) : (
        <AccountsPage />
      )}
    </PortalLayout>
  );
}



function AccountsPage() {
  const [users, setUsers] =
    useState<AdminUser[]>([]);

  const [total, setTotal] =
    useState(0);

  const [
    searchDraft,
    setSearchDraft,
  ] = useState("");

  const [search, setSearch] =
    useState("");

  const [role, setRole] =
    useState<"" | UserRole>("");

  const [active, setActive] =
    useState<
      "" | "true" | "false"
    >("");

  const [offset, setOffset] =
    useState(0);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [notice, setNotice] =
    useState<string | null>(null);

  const [showCreate, setShowCreate] =
    useState(false);

  const [editing, setEditing] =
    useState<AdminUser | null>(null);

  const load =
    useCallback(async () => {
      setLoading(true);
      setError(null);

      try {
        const result =
          await api.adminUsers({
            q: search,
            role:
              role || undefined,
            active: active
              ? active === "true"
              : undefined,
            limit: pageSize,
            offset,
          });

        setUsers(result.users);
        setTotal(result.total);
      } catch (cause) {
        setError(
          cause instanceof Error
            ? cause.message
            : "Không thể tải danh sách tài khoản."
        );
      } finally {
        setLoading(false);
      }
    }, [
      search,
      role,
      active,
      offset,
    ]);

  useEffect(() => {
    void load();
  }, [load]);

  const page =
    Math.floor(
      offset / pageSize
    ) + 1;

  const pageCount =
    Math.max(
      1,
      Math.ceil(
        total / pageSize
      )
    );

  return (
    <>
      <section className="admin-stats">
  <article className="admin-stat-card">
    <small>Tổng tài khoản</small>
    <strong>{total}</strong>
    <span>
      {users.filter((x) => x.active).length} đang hoạt động
    </span>
  </article>

  <article className="admin-stat-card">
    <small>Giảng viên</small>
    <strong>
      {
        users.filter(
          (x) => x.role === "LECTURER"
        ).length
      }
    </strong>
    <span>Tài khoản giảng viên</span>
  </article>

  <article className="admin-stat-card">
    <small>Phòng đào tạo</small>
    <strong>
      {
        users.filter(
          (x) =>
            x.role === "TRAINING_OFFICE"
        ).length
      }
    </strong>
    <span>Tài khoản vận hành</span>
  </article>

  <article className="admin-stat-card">
    <small>Quản trị viên</small>
    <strong>
      {
        users.filter(
          (x) => x.role === "ADMIN"
        ).length
      }
    </strong>
    <span>Tài khoản quản trị</span>
  </article>
</section>
      <section className="panel admin-account-panel">

        {}
        <div className="panel-heading admin-account-heading">
          <div>
            <h2>
              Danh sách tài khoản
            </h2>

            <p>
              Quản lý tài khoản,
              vai trò và trạng thái
              truy cập hệ thống.
            </p>
          </div>

          <button
            type="button"
            onClick={() =>
              setShowCreate(
                (value) =>
                  !value
              )
            }
          >
            {showCreate
              ? "Đóng biểu mẫu"
              : "+ Tạo tài khoản"}
          </button>
        </div>

        {}
        {showCreate && (
          <div className="admin-create-box">
            <UserForm
              mode="create"
              onCancel={() =>
                setShowCreate(
                  false
                )
              }
              onSaved={async (
                saved
              ) => {
                setShowCreate(
                  false
                );

                setNotice(
                  `Đã tạo tài khoản ${saved.username}.`
                );

                setOffset(0);

                await load();
              }}
            />
          </div>
        )}

        {}
        <form
          className="account-filters"
          onSubmit={(event) => {
            event.preventDefault();

            setOffset(0);

            setSearch(
              searchDraft.trim()
            );
          }}
        >
          <label>
            Tìm tài khoản

            <input
              value={
                searchDraft
              }
              onChange={(
                event
              ) =>
                setSearchDraft(
                  event.target
                    .value
                )
              }
              placeholder="Tên đăng nhập hoặc họ tên"
            />
          </label>

          <label>
            Vai trò

            <select
              value={role}
              onChange={(
                event
              ) => {
                setRole(
                  event.target
                    .value as
                    | ""
                    | UserRole
                );

                setOffset(0);
              }}
            >
              <option value="">
                Tất cả vai trò
              </option>

              <option value="ADMIN">
                Quản trị viên
              </option>

              <option value="TRAINING_OFFICE">
                Phòng Đào tạo
              </option>

              <option value="LECTURER">
                Giảng viên
              </option>
            </select>
          </label>

          <label>
            Trạng thái

            <select
              value={active}
              onChange={(
                event
              ) => {
                setActive(
                  event.target
                    .value as typeof active
                );

                setOffset(0);
              }}
            >
              <option value="">
                Tất cả trạng thái
              </option>

              <option value="true">
                Đang hoạt động
              </option>

              <option value="false">
                Đã vô hiệu hóa
              </option>
            </select>
          </label>

          <button type="submit">
            Tìm kiếm
          </button>

          <button
            type="button"
            className="secondary"
            onClick={() => {
              setSearchDraft("");
              setSearch("");
              setRole("");
              setActive("");
              setOffset(0);
            }}
          >
            Xóa bộ lọc
          </button>
        </form>

        {}
        {notice && (
          <div
            className="alert success"
            role="status"
          >
            <span>
              {notice}
            </span>

            <button
              type="button"
              onClick={() =>
                setNotice(null)
              }
              aria-label="Đóng thông báo"
            >
              ×
            </button>
          </div>
        )}

        {}
        {error && (
          <div
            className="alert error"
            role="alert"
          >
            <span>
              {error}
            </span>

            <button
              type="button"
              className="secondary"
              onClick={() =>
                void load()
              }
            >
              Thử lại
            </button>
          </div>
        )}

        {}
        {loading ? (
          <div className="calendar-state">
            <span className="loading-ring" />

            <span>
              Đang tải danh sách
              tài khoản...
            </span>
          </div>
        ) : users.length ? (
          <div className="table-wrap admin-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>
                    Tài khoản
                  </th>

                  <th>
                    Vai trò
                  </th>

                  <th>
                    Mã giảng viên
                  </th>

                  <th>
                    Trạng thái
                  </th>

                  <th>
                    Đăng nhập gần nhất
                  </th>

                  <th>
                    Thao tác
                  </th>
                </tr>
              </thead>

              <tbody>
                {users.map(
                  (item) => (
                    <tr
                      key={
                        item.id
                      }
                    >
                      <td>
                        <div className="account-person">
                          <span className="account-person-avatar">
                            {item.display_name
                              .trim()
                              .charAt(
                                0
                              )
                              .toUpperCase() ||
                              "U"}
                          </span>

                          <span>
                            <strong>
                              {
                                item.display_name
                              }
                            </strong>

                            <small>
                              {
                                item.username
                              }
                            </small>
                          </span>
                        </div>
                      </td>

                      <td>
                        <span className="admin-role-badge">
                          {roleLabel(
                            item.role
                          )}
                        </span>
                      </td>

                      <td>
                        {item.lecturer_code ||
                          "—"}
                      </td>

                      <td>
                        <span
                          className={`status ${
                            item.active
                              ? "completed"
                              : "failed"
                          }`}
                        >
                          {item.active
                            ? "Đang hoạt động"
                            : "Đã vô hiệu hóa"}
                        </span>
                      </td>

                      <td>
                        {formatDateTime(
                          item.last_login_at
                        )}
                      </td>

                      <td>
                        <button
                          type="button"
                          className="secondary"
                          onClick={() =>
                            setEditing(
                              item
                            )
                          }
                        >
                          Chỉnh sửa
                        </button>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        ) : (
          !error && (
            <p className="empty">
              Không có tài khoản
              phù hợp với bộ lọc.
            </p>
          )
        )}

        {}
        {total > pageSize && (
          <div className="pagination-controls">
            <button
              type="button"
              className="secondary"
              disabled={
                offset === 0
              }
              onClick={() =>
                setOffset(
                  Math.max(
                    0,
                    offset -
                      pageSize
                  )
                )
              }
            >
              Trang trước
            </button>

            <span>
              Trang {page}/
              {pageCount} ·{" "}
              {total} tài khoản
            </span>

            <button
              type="button"
              className="secondary"
              disabled={
                offset +
                  pageSize >=
                total
              }
              onClick={() =>
                setOffset(
                  offset +
                    pageSize
                )
              }
            >
              Trang sau
            </button>
          </div>
        )}
      </section>

      {}
      {editing && (
        <div
          className="modal-backdrop"
          role="presentation"
          onMouseDown={(
            event
          ) => {
            if (
              event.target ===
              event.currentTarget
            ) {
              setEditing(null);
            }
          }}
        >
          <section
            className="modal account-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="edit-account-title"
          >
            <button
              className="close"
              type="button"
              onClick={() =>
                setEditing(null)
              }
              aria-label="Đóng"
            >
              ×
            </button>

            <p className="eyebrow">
              Quản trị tài khoản
            </p>

            <h2 id="edit-account-title">
              Chỉnh sửa tài khoản
            </h2>

            <p className="admin-modal-description">
              Cập nhật thông tin,
              vai trò hoặc trạng thái
              của tài khoản.
            </p>

            <UserForm
              mode="edit"
              user={editing}
              onCancel={() =>
                setEditing(null)
              }
              onSaved={async (
                saved
              ) => {
                setEditing(null);

                setNotice(
                  `Đã cập nhật tài khoản ${saved.username}.`
                );

                await load();
              }}
            />
          </section>
        </div>
      )}
    </>
  );
}



interface UserFormProps {
  mode: "create" | "edit";
  user?: AdminUser;
  onCancel: () => void;
  onSaved: (
    user: AdminUser
  ) => void | Promise<void>;
}

function UserForm({
  mode,
  user,
  onCancel,
  onSaved,
}: UserFormProps) {
  const [
    username,
    setUsername,
  ] = useState(
    user?.username || ""
  );

  const [
    displayName,
    setDisplayName,
  ] = useState(
    user?.display_name || ""
  );

  const [
    password,
    setPassword,
  ] = useState("");

  const [role, setRole] =
    useState<UserRole>(
      user?.role ||
        "LECTURER"
    );

  const [
    lecturerCode,
    setLecturerCode,
  ] = useState(
    user?.lecturer_code ||
      ""
  );

  const [active, setActive] =
    useState(
      user?.active ?? true
    );

  const [busy, setBusy] =
    useState(false);

  const [error, setError] =
    useState<string | null>(
      null
    );

  const submit = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    if (
      mode === "edit" &&
      user?.active &&
      !active
    ) {
      const confirmed =
        window.confirm(
          `Vô hiệu hóa tài khoản ${user.username}? Người dùng sẽ không thể đăng nhập.`
        );

      if (!confirmed) {
        return;
      }
    }

    if (
      mode === "edit" &&
      user &&
      user.role !== role
    ) {
      const confirmed =
        window.confirm(
          `Đổi vai trò của ${user.username} từ ${roleLabel(
            user.role
          )} sang ${roleLabel(
            role
          )}? Quyền truy cập của tài khoản sẽ thay đổi.`
        );

      if (!confirmed) {
        return;
      }
    }

    setBusy(true);
    setError(null);

    try {
      if (
        mode === "create"
      ) {
        const result =
          await api.createUser(
            {
              username:
                username.trim(),

              display_name:
                displayName.trim(),

              password,

              role,

              lecturer_code:
                role ===
                "LECTURER"
                  ? lecturerCode.trim() ||
                    null
                  : null,
            }
          );

        await onSaved(
          result.user
        );
      } else if (user) {
        const body: UserWriteInput =
          {
            username:
              username.trim(),

            display_name:
              displayName.trim(),

            role,

            active,

            lecturer_code:
              role ===
              "LECTURER"
                ? lecturerCode.trim() ||
                  null
                : null,
          };

        if (password) {
          body.password =
            password;
        }

        const result =
          await api.updateUser(
            user.id,
            body
          );

        await onSaved(
          result.user
        );
      }
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Không thể lưu tài khoản."
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <form
      className="account-form"
      onSubmit={submit}
    >
      <div className="form-grid">
        <label>
          Tên đăng nhập{" "}
          <span aria-hidden="true">
            *
          </span>

          <input
            autoComplete="off"
            value={username}
            onChange={(event) =>
              setUsername(
                event.target
                  .value
              )
            }
            required
          />
        </label>

        <label>
          Họ và tên{" "}
          <span aria-hidden="true">
            *
          </span>

          <input
            value={displayName}
            onChange={(event) =>
              setDisplayName(
                event.target
                  .value
              )
            }
            required
          />
        </label>

        <label>
          {mode === "create"
            ? "Mật khẩu"
            : "Mật khẩu mới (để trống nếu giữ nguyên)"}

          {mode ===
            "create" && (
            <span aria-hidden="true">
              {" "}
              *
            </span>
          )}

          <input
            type="password"
            autoComplete="new-password"
            minLength={8}
            value={password}
            onChange={(event) =>
              setPassword(
                event.target
                  .value
              )
            }
            required={
              mode === "create"
            }
          />
        </label>

        <label>
          Vai trò{" "}
          <span aria-hidden="true">
            *
          </span>

          <select
            value={role}
            onChange={(event) =>
              setRole(
                event.target
                  .value as UserRole
              )
            }
          >
            <option value="ADMIN">
              Quản trị viên
            </option>

            <option value="TRAINING_OFFICE">
              Phòng Đào tạo
            </option>

            <option value="LECTURER">
              Giảng viên
            </option>
          </select>
        </label>

        {role ===
          "LECTURER" && (
          <label>
            Mã giảng viên

            <input
              value={
                lecturerCode
              }
              onChange={(
                event
              ) =>
                setLecturerCode(
                  event.target
                    .value
                )
              }
              placeholder="Ví dụ: GV001"
            />
          </label>
        )}

        {mode ===
          "edit" && (
          <label className="checkbox-label admin-active-checkbox">
            <input
              type="checkbox"
              checked={active}
              onChange={(
                event
              ) =>
                setActive(
                  event.target
                    .checked
                )
              }
            />

            Tài khoản đang
            hoạt động
          </label>
        )}
      </div>

      {error && (
        <div
          className="alert error"
          role="alert"
        >
          {error}
        </div>
      )}

      <div className="modal-actions">
        <button
          type="button"
          className="secondary"
          onClick={onCancel}
        >
          Hủy
        </button>

        <button
          disabled={busy}
        >
          {busy
            ? "Đang lưu..."
            : mode ===
                "create"
              ? "Tạo tài khoản"
              : "Lưu thay đổi"}
        </button>
      </div>
    </form>
  );
}


function AuditPage() {
  const [logs, setLogs] =
    useState<AuditLog[]>([]);

  const [total, setTotal] =
    useState(0);

  const [offset, setOffset] =
    useState(0);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(
      null
    );

  const load =
    useCallback(async () => {
      setLoading(true);
      setError(null);

      try {
        const result =
          await api.auditLogs({
            limit: pageSize,
            offset,
          });

        setLogs(
          result.audit_logs
        );

        setTotal(result.total);
      } catch (cause) {
        setError(
          cause instanceof Error
            ? cause.message
            : "Không thể tải lịch sử tài khoản."
        );
      } finally {
        setLoading(false);
      }
    }, [offset]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <section className="panel admin-audit-panel">
      <div className="panel-heading">
        <div>
          <h2>
            Nhật ký quản trị và
            xác thực
          </h2>

          <p>
            {total} bản ghi được
            lưu để truy vết thay
            đổi.
          </p>
        </div>
      </div>

      {error && (
        <div
          className="alert error"
          role="alert"
        >
          <span>
            {error}
          </span>

          <button
            type="button"
            className="secondary"
            onClick={() =>
              void load()
            }
          >
            Thử lại
          </button>
        </div>
      )}

      {loading ? (
        <div className="calendar-state">
          <span className="loading-ring" />

          <span>
            Đang tải lịch sử...
          </span>
        </div>
      ) : logs.length ? (
        <div className="table-wrap admin-table-wrap">
          <table>
            <thead>
              <tr>
                <th>
                  Thời gian
                </th>

                <th>
                  Hoạt động
                </th>

                <th>
                  Người thực hiện
                </th>

                <th>
                  Tài khoản liên quan
                </th>

                <th>
                  Chi tiết
                </th>
              </tr>
            </thead>

            <tbody>
              {logs.map(
                (log) => (
                  <tr
                    key={log.id}
                  >
                    <td>
                      {formatDateTime(
                        log.created_at
                      )}
                    </td>

                    <td>
                      <span className="admin-audit-action">
                        {auditActionLabel(
                          log.action
                        )}
                      </span>
                    </td>

                    <td>
                      {log.actor_username ||
                        "Hệ thống"}
                    </td>

                    <td>
                      {log.target_username ||
                        (log.target_user_id
                          ? `Tài khoản #${log.target_user_id}`
                          : "—")}
                    </td>

                    <td>
                      {log.old_value ||
                      log.new_value ? (
                        <details>
                          <summary>
                            Xem thay đổi
                          </summary>

                          <div className="audit-detail">
                            {log.old_value && (
                              <p>
                                <strong>
                                  Trước:
                                </strong>{" "}
                                {formatAuditValue(
                                  log.old_value
                                )}
                              </p>
                            )}

                            {log.new_value && (
                              <p>
                                <strong>
                                  Sau:
                                </strong>{" "}
                                {formatAuditValue(
                                  log.new_value
                                )}
                              </p>
                            )}
                          </div>
                        </details>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      ) : (
        !error && (
          <p className="empty">
            Chưa có lịch sử tài
            khoản hoặc xác thực.
          </p>
        )
      )}

      {total >
        pageSize && (
        <div className="pagination-controls">
          <button
            type="button"
            className="secondary"
            disabled={
              offset === 0
            }
            onClick={() =>
              setOffset(
                Math.max(
                  0,
                  offset -
                    pageSize
                )
              )
            }
          >
            Trang trước
          </button>

          <span>
            Trang{" "}
            {Math.floor(
              offset /
                pageSize
            ) + 1}
            /
            {Math.max(
              1,
              Math.ceil(
                total /
                  pageSize
              )
            )}
          </span>

          <button
            type="button"
            className="secondary"
            disabled={
              offset +
                pageSize >=
              total
            }
            onClick={() =>
              setOffset(
                offset +
                  pageSize
              )
            }
          >
            Trang sau
          </button>
        </div>
      )}
    </section>
  );
}



const auditActions: Record<
  string,
  string
> = {
  ADMIN_BOOTSTRAPPED:
    "Khởi tạo tài khoản quản trị",

  ADMIN_RECOVERED:
    "Khôi phục tài khoản quản trị cũ",

  LOGIN_SUCCESS:
    "Đăng nhập thành công",

  LOGIN_FAILED:
    "Đăng nhập không thành công",

  LOGOUT:
    "Đăng xuất",

  USER_CREATED:
    "Tạo tài khoản",

  USER_UPDATED:
    "Cập nhật tài khoản",

  USER_ACTIVATED:
    "Kích hoạt tài khoản",

  USER_DEACTIVATED:
    "Vô hiệu hóa tài khoản",
};

function auditActionLabel(
  action: string
) {
  return (
    auditActions[action] ||
    "Hoạt động tài khoản"
  );
}

function formatAuditValue(
  value: Record<
    string,
    unknown
  >
) {
  const labels: Record<
    string,
    string
  > = {
    username:
      "Tên đăng nhập",

    display_name:
      "Họ tên",

    role:
      "Vai trò",

    active:
      "Trạng thái",

    lecturer_code:
      "Mã giảng viên",
  };

  return Object.entries(
    value
  )
    .map(([key, item]) => {
      const shown =
        key === "role" &&
        typeof item ===
          "string" &&
        [
          "ADMIN",
          "TRAINING_OFFICE",
          "LECTURER",
        ].includes(item)
          ? roleLabel(
              item as UserRole
            )
          : key ===
              "active"
            ? item
              ? "Đang hoạt động"
              : "Đã vô hiệu hóa"
            : String(
                item ?? "—"
              );

      return `${labels[key] || key}: ${shown}`;
    })
    .join(" · ");
}

function formatDateTime(
  value?: string | null
) {
  if (!value) {
    return "—";
  }

  return new Intl.DateTimeFormat(
    "vi-VN",
    {
      dateStyle: "short",
      timeStyle: "short",
      timeZone:
        "Asia/Ho_Chi_Minh",
    }
  ).format(new Date(value));
}