import type {
  ChangeRequestSnapshot,
  LecturerChangeRequest,
  LecturerChangeRequestStatus,
} from "../../types";
import {
  formatRequestDate,
  formatRequestDateTime,
  requestEventLabels,
  requestStatusClass,
  requestStatusLabels,
  requestTypeLabels,
} from "./requestLabels";

interface RequestDetailsProps {
  request: LecturerChangeRequest;
  compact?: boolean;
}

export function RequestDetails({ request, compact = false }: RequestDetailsProps) {
  const proposal = request.proposal_snapshot || {
    date: request.proposed_date,
    slot_code: request.proposed_slot_code,
    room_code: request.proposed_room_code,
  };

  return <div className={compact ? "request-details compact" : "request-details"}>
    <div className="request-detail-heading">
      <div>
        <p className="eyebrow">Mã yêu cầu</p>
        <h2>{request.request_code}</h2>
      </div>
      <span className={requestStatusClass(request.status)}>{requestStatusLabels[request.status]}</span>
    </div>

    <dl className="request-facts">
      <Fact label="Loại yêu cầu" value={requestTypeLabels[request.request_type]} />
      <Fact label="Lớp học phần" value={request.section_code} />
      <Fact label="Buổi bị ảnh hưởng" value={formatRequestDate(request.occurrence_date)} />
      <Fact label="Người gửi" value={request.requester_display_name || request.requester_username} />
      <Fact label="Gửi lúc" value={formatRequestDateTime(request.created_at)} />
      <Fact label="Lịch chính thức" value={request.official_code} />
    </dl>

    <section className="request-reason" aria-labelledby={`${request.request_code}-reason`}>
      <h3 id={`${request.request_code}-reason`}>Lý do của giảng viên</h3>
      <p>{request.reason}</p>
    </section>

    <div className="snapshot-grid">
      <ScheduleSnapshot title="Lịch hiện tại" snapshot={request.current_snapshot} fallbackDate={request.occurrence_date} />
      {request.request_type === "MOVE_ONE_OCCURRENCE" && <ScheduleSnapshot title="Phương án đề xuất" snapshot={proposal} fallbackDate={request.proposed_date} />}
      {request.request_type === "SUSPEND_ONE_OCCURRENCE" && <section className="schedule-snapshot"><h3>Phương án đề xuất</h3><p>Tạm ngưng buổi học đã chọn. Lịch chính thức chỉ thay đổi sau khi yêu cầu được áp dụng.</p></section>}
    </div>

    {(request.reviewer_display_name || request.reviewer_username || request.review_note) && <section className={`review-note ${request.status === "REJECTED" ? "rejected" : ""}`}>
      <h3>Kết quả xử lý</h3>
      <p><strong>Người xử lý:</strong> {request.reviewer_display_name || request.reviewer_username || "—"}</p>
      <p><strong>Ghi chú:</strong> {request.review_note || "Không có ghi chú."}</p>
      {request.reviewed_at && <p><strong>Thời gian:</strong> {formatRequestDateTime(request.reviewed_at)}</p>}
    </section>}

    {request.validation_result && <ValidationResult request={request} />}
    {!compact && <RequestTimeline request={request} />}
  </div>;
}

function Fact({ label, value }: { label: string; value: string }) {
  return <div><dt>{label}</dt><dd>{value}</dd></div>;
}

function ScheduleSnapshot({ title, snapshot, fallbackDate }: { title: string; snapshot?: ChangeRequestSnapshot | null; fallbackDate?: string | null }) {
  const date = snapshot?.date || snapshot?.occurrence_date || fallbackDate;
  const start = typeof snapshot?.start_period === "number" ? snapshot.start_period : undefined;
  const end = typeof snapshot?.end_period === "number" ? snapshot.end_period : undefined;
  const period = start !== undefined && end !== undefined ? `Tiết ${start}–${end}` : snapshot?.slot_code;

  return <section className="schedule-snapshot">
    <h3>{title}</h3>
    <dl>
      <Fact label="Ngày" value={formatRequestDate(date)} />
      <Fact label="Khung giờ" value={typeof period === "string" && period ? period : "—"} />
      <Fact label="Phòng" value={typeof snapshot?.room_code === "string" && snapshot.room_code ? snapshot.room_code : "—"} />
    </dl>
  </section>;
}

function ValidationResult({ request }: { request: LecturerChangeRequest }) {
  const validation = request.validation_result;
  if (!validation) return null;
  return <section className={`validation-result ${validation.valid ? "valid" : "invalid"}`} aria-live="polite">
    <div>
      <h3>{validation.valid ? "Không phát hiện xung đột cứng" : "Có xung đột cứng"}</h3>
      <p>Kiểm tra lúc {formatRequestDateTime(validation.checked_at)}. Kết quả do hệ thống phía máy chủ xác định.</p>
    </div>
    {!validation.valid && <ul>{validation.hard_conflicts.map((conflict) => <li key={`${conflict.code}-${conflict.message}`}><strong>{conflict.code}</strong><span>{conflict.message}</span></li>)}</ul>}
  </section>;
}

export function RequestTimeline({ request }: { request: LecturerChangeRequest }) {
  const events = request.events || [];
  return <section className="request-timeline" aria-labelledby={`${request.request_code}-timeline`}>
    <h3 id={`${request.request_code}-timeline`}>Lịch sử xử lý</h3>
    {!events.length ? <p className="empty compact-empty">Chưa có sự kiện xử lý nào được ghi nhận.</p> : <ol>{events.map((event) => {
      const kind = event.event_type || event.action || event.to_status || event.status || "UPDATED";
      const actor = event.actor_display_name || event.actor_username || "Hệ thống";
      return <li key={event.id ?? `${event.created_at}-${kind}-${event.from_status || ""}-${event.to_status || ""}`}>
        <span className="timeline-mark" aria-hidden="true" />
        <div><strong>{requestEventLabels[kind] || statusTransitionLabel(event.from_status, event.to_status) || "Đã cập nhật yêu cầu"}</strong><p>{actor} · {formatRequestDateTime(event.created_at)}</p>{event.note && <p className="timeline-note">{event.note}</p>}</div>
      </li>;
    })}</ol>}
  </section>;
}

function statusTransitionLabel(fromStatus?: LecturerChangeRequestStatus | null, toStatus?: LecturerChangeRequestStatus | null) {
  if (!toStatus) return "";
  if (!fromStatus) return requestStatusLabels[toStatus];
  return `${requestStatusLabels[fromStatus]} → ${requestStatusLabels[toStatus]}`;
}
