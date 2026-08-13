import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api } from "../../api/client";
import type {
  LecturerChangeRequest,
  LecturerChangeRequestStatus,
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

interface LecturerRequestHistoryPageProps {
  onCreateRequest: () => void;
}

type StatusFilter = "ALL" | LecturerChangeRequestStatus;

export function LecturerRequestHistoryPage({ onCreateRequest }: LecturerRequestHistoryPageProps) {
  const [requests, setRequests] = useState<LecturerChangeRequest[]>([]);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState<StatusFilter>("ALL");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<LecturerChangeRequest | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [detailRequestCode, setDetailRequestCode] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const listLoadId = useRef(0);
  const detailLoadId = useRef(0);

  const load = useCallback(async () => {
    const loadId = ++listLoadId.current;
    setLoading(true);
    setError(null);
    try {
      const result = await api.lecturerChangeRequests();
      if (loadId === listLoadId.current) {
        setRequests(result.requests);
        setTotal(result.total);
      }
    } catch (cause) {
      if (loadId === listLoadId.current) {
        setError(requestErrorText(cause, "Không thể tải danh sách yêu cầu đã gửi."));
      }
    } finally {
      if (loadId === listLoadId.current) setLoading(false);
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  const filtered = useMemo(() => requests.filter((request) => filter === "ALL" || request.status === filter), [filter, requests]);

  const openDetail = async (requestCode: string) => {
    const loadId = ++detailLoadId.current;
    setDetailRequestCode(requestCode);
    setSelected(null);
    setDetailLoading(true);
    setDetailError(null);
    setActionMessage(null);
    try {
      const result = await api.lecturerChangeRequest(requestCode);
      if (loadId === detailLoadId.current) setSelected(result);
    } catch (cause) {
      if (loadId === detailLoadId.current) {
        setDetailError(requestErrorText(cause, "Không thể tải chi tiết yêu cầu."));
      }
    } finally {
      if (loadId === detailLoadId.current) setDetailLoading(false);
    }
  };

  const cancel = async () => {
    if (!selected || selected.status !== "PENDING" || cancelling) return;
    if (!window.confirm(`Bạn xác nhận hủy yêu cầu ${selected.request_code}? Yêu cầu đã hủy không thể được phê duyệt.`)) return;
    setCancelling(true);
    setDetailError(null);
    setActionMessage(null);
    try {
      const result = await api.cancelLecturerChangeRequest(selected.request_code);
      setSelected(result.request);
      setRequests((current) => current.map((item) => item.request_code === result.request.request_code ? result.request : item));
      setActionMessage(result.message || "Đã hủy yêu cầu.");
    } catch (cause) {
      setDetailError(requestErrorText(cause, "Không thể hủy yêu cầu. Vui lòng tải lại trạng thái và thử lại."));
    } finally {
      setCancelling(false);
    }
  };

  return <>
    <section className="panel request-history-toolbar">
      <div><h2>Yêu cầu điều chỉnh đã gửi</h2><p>Theo dõi trạng thái và toàn bộ lịch sử xử lý. Chỉ yêu cầu đang chờ duyệt mới có thể hủy.</p></div>
      <button type="button" onClick={onCreateRequest}>Gửi yêu cầu mới</button>
    </section>

    <section className="panel">
      <div className="request-list-toolbar">
        <p role="status">{loading ? "Đang tải danh sách..." : `${filtered.length} yêu cầu phù hợp · ${total} yêu cầu đã gửi`}</p>
        <label>Lọc trạng thái<select value={filter} onChange={(event) => setFilter(event.target.value as StatusFilter)}><option value="ALL">Tất cả trạng thái</option>{(Object.keys(requestStatusLabels) as LecturerChangeRequestStatus[]).map((status) => <option value={status} key={status}>{requestStatusLabels[status]}</option>)}</select></label>
      </div>
      {error && <div className="alert error" role="alert"><span>{error}</span><button type="button" className="secondary" onClick={() => void load()}>Thử lại</button></div>}
      {loading ? <p className="empty" role="status">Đang tải yêu cầu đã gửi...</p> : !requests.length ? <div className="empty"><p>Bạn chưa gửi yêu cầu điều chỉnh lịch nào.</p><button type="button" onClick={onCreateRequest}>Gửi yêu cầu đầu tiên</button></div> : !filtered.length ? <p className="empty">Không có yêu cầu nào ở trạng thái đã chọn.</p> : <div className="lecturer-request-list">{filtered.map((request) => <button type="button" className={selected?.request_code === request.request_code ? "request-list-card selected" : "request-list-card"} key={request.request_code} onClick={() => void openDetail(request.request_code)} aria-pressed={selected?.request_code === request.request_code}>
        <span className="request-list-main"><strong>{request.request_code}</strong><small>{requestTypeLabels[request.request_type]} · {request.section_code} · {formatRequestDate(request.occurrence_date)}</small></span>
        <span><span className={requestStatusClass(request.status)}>{requestStatusLabels[request.status]}</span><small>{formatRequestDateTime(request.updated_at || request.created_at)}</small></span>
      </button>)}</div>}
    </section>

    {(detailLoading || detailError || selected) && <section className="panel request-detail-panel" aria-busy={detailLoading}>
      {detailLoading && <p className="empty" role="status">Đang tải chi tiết yêu cầu...</p>}
      {detailError && <div className="alert error" role="alert"><span>{detailError}</span>{detailRequestCode && <button type="button" className="secondary" onClick={() => void openDetail(detailRequestCode)}>Thử lại</button>}</div>}
      {actionMessage && <div className="alert success" role="status">{actionMessage}</div>}
      {!detailLoading && selected && <><RequestDetails request={selected} />{selected.status === "PENDING" && <div className="request-detail-actions"><button type="button" className="danger-button" disabled={cancelling} onClick={() => void cancel()}>{cancelling ? "Đang hủy..." : "Hủy yêu cầu"}</button></div>}</>}
    </section>}
  </>;
}
