import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../../api/client";
import type {
  LecturerChangeRequest,
  LecturerChangeRequestStatus,
  OfficialTimetable,
} from "../../types";
import { RequestDetails } from "./RequestDetails";
import {
  formatRequestDate,
  formatRequestDateTime,
  requestErrorText,
  requestStatusClass,
  requestStatusLabels,
  requestTypeLabels,
} from "./requestLabels";

type StatusFilter = "ALL" | LecturerChangeRequestStatus;
type RequestAction = "validate" | "approve" | "reject" | "apply";

const pageSize = 20;

export function TrainingRequestReviewPage({ onOfficialUpdated }: { onOfficialUpdated?: (official: OfficialTimetable) => void }) {
  const [status, setStatus] = useState<StatusFilter>("PENDING");
  const [offset, setOffset] = useState(0);
  const [requests, setRequests] = useState<LecturerChangeRequest[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [listError, setListError] = useState<string | null>(null);
  const [selected, setSelected] = useState<LecturerChangeRequest | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [detailRequestCode, setDetailRequestCode] = useState<string | null>(null);
  const [busyAction, setBusyAction] = useState<RequestAction | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState("");
  const [rejectReasonError, setRejectReasonError] = useState<string | null>(null);
  const listLoadId = useRef(0);
  const detailLoadId = useRef(0);

  const loadList = useCallback(async () => {
    const loadId = ++listLoadId.current;
    setLoading(true);
    setListError(null);
    try {
      const result = await api.trainingChangeRequests({
        status: status === "ALL" ? undefined : status,
        limit: pageSize,
        offset,
      });
      if (loadId !== listLoadId.current) return;
      const lastOffset = result.total > 0 ? Math.floor((result.total - 1) / pageSize) * pageSize : 0;
      if (offset > lastOffset) {
        setOffset(lastOffset);
        return;
      }
      setRequests(result.requests);
      setTotal(result.total);
    } catch (cause) {
      if (loadId === listLoadId.current) {
        setListError(requestErrorText(cause, "Không thể tải danh sách yêu cầu từ giảng viên."));
      }
    } finally {
      if (loadId === listLoadId.current) setLoading(false);
    }
  }, [offset, status]);

  useEffect(() => { void loadList(); }, [loadList]);

  const openDetail = async (requestCode: string) => {
    const loadId = ++detailLoadId.current;
    setDetailRequestCode(requestCode);
    setSelected(null);
    setDetailLoading(true);
    setDetailError(null);
    setActionError(null);
    setActionMessage(null);
    setRejectReason("");
    setRejectReasonError(null);
    try {
      const result = await api.trainingChangeRequest(requestCode);
      if (loadId === detailLoadId.current) setSelected(result);
    } catch (cause) {
      if (loadId === detailLoadId.current) {
        setDetailError(requestErrorText(cause, "Không thể tải chi tiết yêu cầu."));
      }
    } finally {
      if (loadId === detailLoadId.current) setDetailLoading(false);
    }
  };

  const updateSelected = (request: LecturerChangeRequest) => {
    setSelected(request);
    setRequests((current) => current.map((item) => item.request_code === request.request_code ? request : item));
  };

  const validate = async () => {
    if (!selected || busyAction) return;
    setBusyAction("validate");
    setActionError(null);
    setActionMessage(null);
    try {
      const result = await api.validateTrainingChangeRequest(selected.request_code);
      updateSelected({ ...result.request, validation_result: result.validation });
      setActionMessage(result.validation.valid
        ? "Đã kiểm tra: không phát hiện xung đột cứng. Bạn có thể phê duyệt yêu cầu."
        : `Không thể phê duyệt vì có ${result.validation.hard_conflicts.length} xung đột cứng.`);
    } catch (cause) {
      setActionError(requestErrorText(cause, "Không thể kiểm tra xung đột cho yêu cầu."));
    } finally {
      setBusyAction(null);
    }
  };

  const approve = async () => {
    if (!selected || selected.status !== "PENDING" || !selected.validation_result?.valid || busyAction) return;
    if (!window.confirm(`Phê duyệt yêu cầu ${selected.request_code}? Lịch chính thức vẫn chưa đổi cho đến bước áp dụng.`)) return;
    setBusyAction("approve");
    setActionError(null);
    setActionMessage(null);
    try {
      const result = await api.approveTrainingChangeRequest(selected.request_code);
      updateSelected(result.request);
      setActionMessage(result.message || "Đã phê duyệt yêu cầu.");
      await loadList();
    } catch (cause) {
      setActionError(requestErrorText(cause, "Không thể phê duyệt yêu cầu. Vui lòng kiểm tra lại trạng thái."));
    } finally {
      setBusyAction(null);
    }
  };

  const reject = async () => {
    if (!selected || selected.status !== "PENDING" || busyAction) return;
    const trimmedReason = rejectReason.trim();
    if (!trimmedReason) {
      setRejectReasonError("Vui lòng nhập lý do từ chối để giảng viên có thể theo dõi kết quả.");
      return;
    }
    setRejectReasonError(null);
    if (!window.confirm(`Từ chối yêu cầu ${selected.request_code} với lý do đã nhập?`)) return;
    setBusyAction("reject");
    setActionError(null);
    setActionMessage(null);
    try {
      const result = await api.rejectTrainingChangeRequest(selected.request_code, trimmedReason);
      updateSelected(result.request);
      setRejectReason("");
      setActionMessage(result.message || "Đã từ chối yêu cầu.");
      await loadList();
    } catch (cause) {
      setActionError(requestErrorText(cause, "Không thể từ chối yêu cầu. Vui lòng kiểm tra lại trạng thái."));
    } finally {
      setBusyAction(null);
    }
  };

  const apply = async () => {
    if (!selected || selected.status !== "APPROVED" || busyAction) return;
    if (!window.confirm(`Kiểm tra lại xung đột và áp dụng yêu cầu ${selected.request_code} vào lịch chính thức?`)) return;
    setBusyAction("apply");
    setActionError(null);
    setActionMessage(null);
    try {
      // The apply endpoint performs the authoritative revalidation and writes
      // the official timetable plus audit trail in one transaction.
      const result = await api.applyTrainingChangeRequest(selected.request_code);
      updateSelected(result.request);
      if (result.official) onOfficialUpdated?.(result.official);
      setActionMessage(result.message || "Đã áp dụng yêu cầu vào lịch chính thức.");
      await loadList();
    } catch (cause) {
      setActionError(requestErrorText(cause, "Không thể áp dụng yêu cầu. Lịch chính thức chưa được thay đổi."));
    } finally {
      setBusyAction(null);
    }
  };

  const currentPage = Math.floor(offset / pageSize) + 1;
  const pageCount = Math.max(1, Math.ceil(total / pageSize));

  return <>
    <section className="panel request-review-intro">
      <div><h2>Yêu cầu điều chỉnh từ giảng viên</h2><p>Kiểm tra xung đột bằng backend trước khi phê duyệt. Yêu cầu đã phê duyệt chỉ thay đổi lịch chính thức sau bước áp dụng.</p></div>
      <label>Trạng thái<select value={status} onChange={(event) => { setStatus(event.target.value as StatusFilter); setOffset(0); setSelected(null); }}><option value="ALL">Tất cả trạng thái</option>{(Object.keys(requestStatusLabels) as LecturerChangeRequestStatus[]).map((value) => <option value={value} key={value}>{requestStatusLabels[value]}</option>)}</select></label>
    </section>

    <div className="request-review-layout">
      <section className="panel request-review-list" aria-busy={loading}>
        <div className="panel-heading"><div><h2>Danh sách yêu cầu</h2><p>{loading ? "Đang tải..." : `${total} yêu cầu`}</p></div><button type="button" className="secondary" disabled={loading} onClick={() => void loadList()}>Tải lại</button></div>
        {listError && <div className="alert error" role="alert"><span>{listError}</span><button type="button" className="secondary" onClick={() => void loadList()}>Thử lại</button></div>}
        {loading ? <p className="empty" role="status">Đang tải yêu cầu...</p> : !requests.length ? <p className="empty">Không có yêu cầu điều chỉnh nào phù hợp với bộ lọc.</p> : <div className="training-request-list">{requests.map((request) => <button type="button" key={request.request_code} className={selected?.request_code === request.request_code ? "training-request-card selected" : "training-request-card"} aria-pressed={selected?.request_code === request.request_code} onClick={() => void openDetail(request.request_code)}>
          <span className="training-request-card-heading"><strong>{request.request_code}</strong><span className={requestStatusClass(request.status)}>{requestStatusLabels[request.status]}</span></span>
          <span>{request.requester_display_name || request.requester_username}</span>
          <small>{requestTypeLabels[request.request_type]} · {request.section_code}</small>
          <small>Buổi {formatRequestDate(request.occurrence_date)} · gửi {formatRequestDateTime(request.created_at)}</small>
        </button>)}</div>}
        {total > pageSize && <div className="pagination-controls"><button type="button" className="secondary" disabled={loading || offset === 0} onClick={() => { setOffset(Math.max(0, offset - pageSize)); setSelected(null); }}>Trang trước</button><span>Trang {currentPage}/{pageCount}</span><button type="button" className="secondary" disabled={loading || offset + pageSize >= total} onClick={() => { setOffset(offset + pageSize); setSelected(null); }}>Trang sau</button></div>}
      </section>

      <section className="panel training-request-detail" aria-busy={detailLoading}>
        {!selected && !detailLoading && !detailError && <p className="empty">Chọn một yêu cầu để xem chi tiết và xử lý.</p>}
        {detailLoading && <p className="empty" role="status">Đang tải chi tiết yêu cầu...</p>}
        {detailError && <div className="alert error" role="alert"><span>{detailError}</span>{detailRequestCode && <button type="button" className="secondary" onClick={() => void openDetail(detailRequestCode)}>Thử lại</button>}</div>}
        {actionError && <div className="alert error" role="alert">{actionError}</div>}
        {actionMessage && <div className="alert success" role="status">{actionMessage}</div>}
        {!detailLoading && selected && <>
          <RequestDetails request={selected} />
          {selected.status === "PENDING" && <section className="request-review-actions" aria-labelledby="review-actions-title">
            <h3 id="review-actions-title">Xử lý yêu cầu</h3>
            <p>Phải có kết quả kiểm tra hợp lệ từ backend trước khi phê duyệt.</p>
            <div className="review-primary-actions"><button type="button" className="secondary" disabled={busyAction !== null} onClick={() => void validate()}>{busyAction === "validate" ? "Đang kiểm tra..." : "Kiểm tra xung đột"}</button><button type="button" disabled={busyAction !== null || !selected.validation_result?.valid} onClick={() => void approve()}>{busyAction === "approve" ? "Đang phê duyệt..." : "Phê duyệt"}</button></div>
            {!selected.validation_result?.valid && <small className="field-help">Nút phê duyệt chỉ mở khi lần kiểm tra gần nhất không có xung đột cứng.</small>}
            <div className="reject-request-box"><label>Lý do từ chối <span className="required-mark">*</span><textarea value={rejectReason} onChange={(event) => { setRejectReason(event.target.value); setRejectReasonError(null); }} rows={3} placeholder="Nêu rõ lý do để giảng viên theo dõi" /></label>{rejectReasonError && <p className="field-error" role="alert">{rejectReasonError}</p>}<button type="button" className="danger-button" disabled={busyAction !== null} onClick={() => void reject()}>{busyAction === "reject" ? "Đang từ chối..." : "Từ chối yêu cầu"}</button></div>
          </section>}
          {selected.status === "APPROVED" && <section className="request-review-actions apply-request-box"><h3>Áp dụng vào lịch chính thức</h3><p>Hệ thống sẽ kiểm tra lại toàn bộ ràng buộc cứng ở backend ngay trước khi áp dụng.</p><button type="button" disabled={busyAction !== null} onClick={() => void apply()}>{busyAction === "apply" ? "Đang kiểm tra và áp dụng..." : "Kiểm tra lại và áp dụng"}</button></section>}
        </>}
      </section>
    </div>
  </>;
}
