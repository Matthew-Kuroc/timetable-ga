import type {
  AdjustmentScope,
  AdjustmentSlot,
  AdminUser,
  AuditLog,
  AuthUser,
  Batch,
  ChangeRequestListResponse,
  ChangeRequestValidation,
  CreateLecturerChangeRequestInput,
  LecturerChangeRequest,
  LecturerChangeRequestStatus,
  LecturerTimetable,
  LoginResponse,
  OfficialTimetable,
  Preview,
  Run,
  UserRole,
  UserWriteInput,
} from "../types";

export class ApiError extends Error {
  readonly status: number;
  readonly payload: unknown;

  constructor(status: number, message: string, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

let unauthorizedHandler: (() => void) | null = null;

export function setUnauthorizedHandler(handler: (() => void) | null) {
  unauthorizedHandler = handler;
}

function errorMessage(payload: unknown): string {
  const detail = (payload as { detail?: unknown } | null)?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const messages = detail.map((item) => validationErrorMessage(item)).filter(Boolean);
    if (messages.length) return messages.join(" ");
  }
  if (detail && typeof detail === "object" && "message" in detail) {
    const message = (detail as { message?: unknown }).message;
    const validation = (detail as { validation?: unknown }).validation;
    const conflicts = validation && typeof validation === "object"
      ? (validation as { hard_conflicts?: unknown }).hard_conflicts
      : undefined;
    if (typeof message === "string" && Array.isArray(conflicts)) {
      const conflictMessages = conflicts
        .map((item) => item && typeof item === "object" && "message" in item ? String((item as { message: unknown }).message) : "")
        .filter(Boolean);
      return conflictMessages.length ? `${message} ${conflictMessages.join(" ")}` : message;
    }
    if (typeof message === "string") return message;
  }
  return "Máy chủ không thể xử lý yêu cầu. Vui lòng thử lại.";
}

function validationErrorMessage(value: unknown): string {
  if (!value || typeof value !== "object") return "";
  const item = value as { loc?: unknown; msg?: unknown; type?: unknown; ctx?: Record<string, unknown> };
  const location = Array.isArray(item.loc) ? item.loc.filter((part) => part !== "body" && part !== "query" && part !== "path") : [];
  const fieldName = String(location.at(-1) || "dữ liệu");
  const fieldLabels: Record<string, string> = {
    username: "Tên đăng nhập",
    display_name: "Họ và tên",
    password: "Mật khẩu",
    role: "Vai trò",
    lecturer_code: "Mã giảng viên",
    active: "Trạng thái tài khoản",
    week: "Tuần học",
    official_code: "Mã lịch chính thức",
    section_code: "Lớp học phần",
    request_type: "Loại yêu cầu",
    occurrence_date: "Buổi học bị ảnh hưởng",
    reason: "Lý do",
    proposed_date: "Ngày đề xuất",
    proposed_slot_code: "Khung giờ đề xuất",
    proposed_room_code: "Phòng đề xuất",
    limit: "Số bản ghi",
    offset: "Vị trí bắt đầu",
  };
  const label = fieldLabels[fieldName] || fieldName;
  if (item.type === "missing") return `${label} là trường bắt buộc.`;
  if (item.type === "string_too_short" && item.ctx?.min_length !== undefined) return `${label} phải có ít nhất ${item.ctx.min_length} ký tự.`;
  if (item.type === "string_too_long" && item.ctx?.max_length !== undefined) return `${label} không được vượt quá ${item.ctx.max_length} ký tự.`;
  if (item.type === "enum") return `${label} không thuộc danh sách giá trị hợp lệ.`;
  return `${label}: ${typeof item.msg === "string" ? item.msg : "Giá trị không hợp lệ."}`;
}

async function request<T>(path: string, init?: RequestInit, notifyUnauthorized = true): Promise<T> {
  const response = await fetch(path, { ...init, credentials: "same-origin" });
  const payload: unknown = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401 && notifyUnauthorized) unauthorizedHandler?.();
    throw new ApiError(response.status, errorMessage(payload), payload);
  }
  return payload as T;
}

function jsonRequest<T>(path: string, method: "POST" | "PATCH" | "PUT", body: unknown, notifyUnauthorized = true) {
  return request<T>(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }, notifyUnauthorized);
}

function query(params: Record<string, string | number | boolean | undefined>) {
  const values = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") values.set(key, String(value));
  });
  const encoded = values.toString();
  return encoded ? `?${encoded}` : "";
}

export const api = {
  login: (username: string, password: string) => jsonRequest<LoginResponse>("/api/auth/login", "POST", { username, password }, false),
  me: async () => (await request<{ user: AuthUser }>("/api/auth/me", undefined, false)).user,
  logout: () => request<{ message: string }>("/api/auth/logout", { method: "POST" }, false),

  adminUsers: (params: { q?: string; role?: UserRole; active?: boolean; limit?: number; offset?: number }) =>
    request<{ users: AdminUser[]; total: number }>(`/api/admin/users${query(params)}`),
  createUser: (body: { username: string; display_name: string; password: string; role: UserRole; lecturer_code?: string | null }) =>
    jsonRequest<{ user: AdminUser }>("/api/admin/users", "POST", body),
  updateUser: (userId: number, body: UserWriteInput) =>
    jsonRequest<{ user: AdminUser }>(`/api/admin/users/${userId}`, "PATCH", body),
  auditLogs: (params: { limit?: number; offset?: number }) =>
    request<{ audit_logs: AuditLog[]; total: number }>(`/api/admin/audit-logs${query(params)}`),

  lecturerTimetable: (week: number) => request<LecturerTimetable>(`/api/lecturer/timetable${query({ week })}`),
  lecturerChangeRequests: () => request<ChangeRequestListResponse>("/api/lecturer/change-requests"),
  lecturerChangeRequest: (requestCode: string) =>
    request<LecturerChangeRequest>(`/api/lecturer/change-requests/${encodeURIComponent(requestCode)}`),
  createLecturerChangeRequest: (body: CreateLecturerChangeRequestInput) =>
    jsonRequest<{ message: string; request: LecturerChangeRequest }>("/api/lecturer/change-requests", "POST", body),
  cancelLecturerChangeRequest: (requestCode: string) =>
    request<{ message: string; request: LecturerChangeRequest }>(`/api/lecturer/change-requests/${encodeURIComponent(requestCode)}/cancel`, { method: "POST" }),
  lecturerChangeRequestOptions: async (params: { officialCode: string; sectionCode: string; occurrenceDate: string; targetDate: string }) => {
    const result = await request<{ slots: AdjustmentSlot[] }>(`/api/lecturer/change-requests/options${query({
      official_code: params.officialCode,
      section_code: params.sectionCode,
      occurrence_date: params.occurrenceDate,
      target_date: params.targetDate,
    })}`);
    return result.slots;
  },

  trainingChangeRequests: (params: { status?: LecturerChangeRequestStatus; limit?: number; offset?: number }) =>
    request<ChangeRequestListResponse>(`/api/training-office/change-requests${query(params)}`),
  trainingChangeRequest: (requestCode: string) =>
    request<LecturerChangeRequest>(`/api/training-office/change-requests/${encodeURIComponent(requestCode)}`),
  validateTrainingChangeRequest: (requestCode: string) =>
    request<{ request: LecturerChangeRequest; validation: ChangeRequestValidation }>(`/api/training-office/change-requests/${encodeURIComponent(requestCode)}/validate`, { method: "POST" }),
  approveTrainingChangeRequest: (requestCode: string) =>
    jsonRequest<{ message: string; request: LecturerChangeRequest }>(`/api/training-office/change-requests/${encodeURIComponent(requestCode)}/approve`, "POST", {}),
  rejectTrainingChangeRequest: (requestCode: string, reason: string) =>
    jsonRequest<{ message: string; request: LecturerChangeRequest }>(`/api/training-office/change-requests/${encodeURIComponent(requestCode)}/reject`, "POST", { reason }),
  applyTrainingChangeRequest: (requestCode: string) =>
    request<{ message: string; request: LecturerChangeRequest; official?: OfficialTimetable }>(`/api/training-office/change-requests/${encodeURIComponent(requestCode)}/apply`, { method: "POST" }),

  health: () => request<{ status: string }>("/api/health"),
  batches: async () => (await request<{ batches: Batch[] }>("/api/batches")).batches,
  runs: async () => (await request<{ runs: Run[] }>("/api/ga/runs")).runs,
  run: (runCode: string) => request<Run>(`/api/ga/runs/${encodeURIComponent(runCode)}`),
  officialTimetables: async () => (await request<{ official_timetables: OfficialTimetable[] }>("/api/ga/official-timetables")).official_timetables,
  officialTimetable: (officialCode: string) => request<OfficialTimetable>(`/api/ga/official-timetables/${encodeURIComponent(officialCode)}`),
  publishRun: (runCode: string, note = "") => jsonRequest<OfficialTimetable>(`/api/ga/runs/${encodeURIComponent(runCode)}/publish`, "POST", { note }),
  previewImport: (files: File[]) => {
    const form = new FormData();
    files.forEach((file) => form.append("files", file, file.name));
    return request<Preview>("/api/imports/csv/preview", { method: "POST", body: form });
  },
  confirmImport: (files: File[], metadata: { displayName: string; semester: string; academicYear: string; note: string }) => {
    const form = new FormData();
    files.forEach((file) => form.append("files", file, file.name));
    form.append("display_name", metadata.displayName);
    form.append("semester", metadata.semester);
    form.append("academic_year", metadata.academicYear);
    form.append("note", metadata.note);
    return request<{ batch: Batch }>("/api/imports/csv/confirm", { method: "POST", body: form });
  },
  startRun: (body: Record<string, number | string>) => jsonRequest<Run>("/api/ga/runs/preview", "POST", body),
  adjustmentOptions: async (runCode: string, sectionCode: string, date: string) => {
    const result = await request<{ slots: AdjustmentSlot[] }>(`/api/ga/runs/${encodeURIComponent(runCode)}/occurrence-adjustment-options/${encodeURIComponent(sectionCode)}/${date}?target_date=${date}`);
    return result.slots;
  },
  adjustOfficial: (officialCode: string, body: { section_code: string; occurrence_date: string; room_code: string; slot_code: string; reason: string; scope: AdjustmentScope; effective_start_date?: string; effective_end_date?: string }) =>
    jsonRequest<{ message: string; official: OfficialTimetable }>(`/api/ga/official-timetables/${encodeURIComponent(officialCode)}/adjustments`, "PUT", body),
  createSegment: (officialCode: string, body: Record<string, string>) =>
    jsonRequest<{ message: string; official: OfficialTimetable }>(`/api/ga/official-timetables/${encodeURIComponent(officialCode)}/segments`, "POST", body),
  createMakeup: (officialCode: string, body: Record<string, string>) =>
    jsonRequest<{ message: string; official: OfficialTimetable }>(`/api/ga/official-timetables/${encodeURIComponent(officialCode)}/makeups`, "POST", body),
};
