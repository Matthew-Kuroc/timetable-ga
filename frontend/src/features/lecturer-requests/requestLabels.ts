import type {
  LecturerChangeRequestStatus,
  LecturerChangeRequestType,
} from "../../types";

export const requestStatusLabels: Record<LecturerChangeRequestStatus, string> = {
  PENDING: "Chờ duyệt",
  APPROVED: "Đã phê duyệt",
  REJECTED: "Bị từ chối",
  CANCELLED: "Đã hủy",
  APPLIED: "Đã áp dụng",
};

export const requestTypeLabels: Record<LecturerChangeRequestType, string> = {
  SUSPEND_ONE_OCCURRENCE: "Tạm ngưng một buổi",
  MOVE_ONE_OCCURRENCE: "Chuyển một buổi",
};

export const requestEventLabels: Record<string, string> = {
  CREATED: "Đã gửi yêu cầu",
  SUBMITTED: "Đã gửi yêu cầu",
  VALIDATED: "Đã kiểm tra xung đột",
  APPROVED: "Đã phê duyệt",
  REJECTED: "Đã từ chối",
  CANCELLED: "Đã hủy",
  APPLIED: "Đã áp dụng vào lịch chính thức",
};

export function requestStatusClass(status: LecturerChangeRequestStatus) {
  return `request-status request-status-${status.toLocaleLowerCase()}`;
}

export function formatRequestDate(value?: string | null) {
  if (!value) return "—";
  const normalized = value.slice(0, 10);
  const parsed = new Date(`${normalized}T00:00:00`);
  return Number.isNaN(parsed.getTime())
    ? value
    : new Intl.DateTimeFormat("vi-VN").format(parsed);
}

export function formatRequestDateTime(value?: string | null) {
  if (!value) return "—";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime())
    ? value
    : new Intl.DateTimeFormat("vi-VN", {
        dateStyle: "short",
        timeStyle: "short",
        timeZone: "Asia/Ho_Chi_Minh",
      }).format(parsed);
}

export function requestErrorText(error: unknown, fallback: string) {
  return error instanceof Error && error.message ? error.message : fallback;
}
