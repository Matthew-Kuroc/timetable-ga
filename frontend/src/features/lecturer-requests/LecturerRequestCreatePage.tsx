import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api } from "../../api/client";
import type {
  AdjustmentSlot,
  LecturerChangeRequest,
  LecturerChangeRequestType,
  LecturerTimetable,
  LecturerTimetableOccurrence,
} from "../../types";
import {
  formatRequestDate,
  requestErrorText,
  requestStatusClass,
  requestStatusLabels,
  requestTypeLabels,
} from "./requestLabels";

interface LecturerRequestCreatePageProps {
  onNavigateHistory: () => void;
}

export function LecturerRequestCreatePage({ onNavigateHistory }: LecturerRequestCreatePageProps) {
  const [week, setWeek] = useState(1);
  const [timetable, setTimetable] = useState<LecturerTimetable | null>(null);
  const [timetableLoading, setTimetableLoading] = useState(true);
  const [timetableError, setTimetableError] = useState<string | null>(null);
  const [occurrenceKey, setOccurrenceKey] = useState("");
  const [requestType, setRequestType] = useState<LecturerChangeRequestType>("SUSPEND_ONE_OCCURRENCE");
  const [reason, setReason] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [options, setOptions] = useState<AdjustmentSlot[]>([]);
  const [optionsLoading, setOptionsLoading] = useState(false);
  const [optionsError, setOptionsError] = useState<string | null>(null);
  const [slotCode, setSlotCode] = useState("");
  const [roomCode, setRoomCode] = useState("");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [createdRequest, setCreatedRequest] = useState<LecturerChangeRequest | null>(null);
  const timetableLoadId = useRef(0);
  const optionsLoadId = useRef(0);

  const loadTimetable = useCallback(async () => {
    const loadId = ++timetableLoadId.current;
    setTimetableLoading(true);
    setTimetableError(null);
    setTimetable(null);
    try {
      const result = await api.lecturerTimetable(week);
      if (loadId === timetableLoadId.current) setTimetable(result);
    } catch (cause) {
      if (loadId === timetableLoadId.current) {
        setTimetableError(requestErrorText(cause, "Không thể tải các buổi dạy trong tuần này."));
      }
    } finally {
      if (loadId === timetableLoadId.current) setTimetableLoading(false);
    }
  }, [week]);

  useEffect(() => { void loadTimetable(); }, [loadTimetable]);

  const occurrences = useMemo(() => [...(timetable?.occurrences || [])].sort((first, second) =>
    first.date.localeCompare(second.date)
    || Number(first.start_period || 0) - Number(second.start_period || 0)
    || first.section_code.localeCompare(second.section_code, "vi")), [timetable]);
  const sections = useMemo(() => new Map((timetable?.course_sections || []).map((section) => [section.section_code, section])), [timetable]);
  const occurrence = occurrences.find((item) => occurrenceValue(item) === occurrenceKey) || null;
  const selectedSlot = options.find((option) => option.slot_code === slotCode);
  const availableRooms = selectedSlot?.rooms || [];

  const loadOptions = useCallback(async () => {
    const loadId = ++optionsLoadId.current;
    if (requestType !== "MOVE_ONE_OCCURRENCE" || !occurrence || !targetDate || !timetable?.official_code) {
      setOptions([]);
      setOptionsLoading(false);
      setSlotCode("");
      setRoomCode("");
      return;
    }
    setOptionsLoading(true);
    setOptionsError(null);
    setOptions([]);
    setSlotCode("");
    setRoomCode("");
    try {
      const result = await api.lecturerChangeRequestOptions({
        officialCode: timetable.official_code,
        sectionCode: occurrence.section_code,
        occurrenceDate: occurrence.date,
        targetDate,
      });
      if (loadId === optionsLoadId.current) setOptions(result);
    } catch (cause) {
      if (loadId === optionsLoadId.current) {
        setOptionsError(requestErrorText(cause, "Không thể tải các khung giờ và phòng có thể đề xuất."));
      }
    } finally {
      if (loadId === optionsLoadId.current) setOptionsLoading(false);
    }
  }, [occurrence, requestType, targetDate, timetable?.official_code]);

  useEffect(() => { void loadOptions(); }, [loadOptions]);

  const changeWeek = (value: number) => {
    timetableLoadId.current += 1;
    setWeek(Math.min(53, Math.max(1, value || 1)));
    setTimetable(null);
    setOccurrenceKey("");
    clearProposal();
  };

  const clearProposal = () => {
    optionsLoadId.current += 1;
    setTargetDate("");
    setOptions([]);
    setOptionsLoading(false);
    setOptionsError(null);
    setSlotCode("");
    setRoomCode("");
  };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitError(null);
    if (!timetable?.official_code) {
      setSubmitError("Chưa có lịch chính thức để gửi yêu cầu điều chỉnh.");
      return;
    }
    if (!occurrence) {
      setSubmitError("Vui lòng chọn một buổi dạy thuộc lịch của bạn.");
      return;
    }
    if (!reason.trim()) {
      setSubmitError("Vui lòng nhập lý do điều chỉnh.");
      return;
    }
    if (requestType === "MOVE_ONE_OCCURRENCE" && (!targetDate || !slotCode || !roomCode)) {
      setSubmitError("Vui lòng chọn đầy đủ ngày, khung giờ và phòng đề xuất.");
      return;
    }

    const summary = requestType === "MOVE_ONE_OCCURRENCE"
      ? `${requestTypeLabels[requestType]} ${occurrence.section_code} từ ${formatRequestDate(occurrence.date)} sang ${formatRequestDate(targetDate)}, ${periodLabel(selectedSlot)}, phòng ${roomCode}.`
      : `${requestTypeLabels[requestType]} ${occurrence.section_code} ngày ${formatRequestDate(occurrence.date)}.`;
    if (!window.confirm(`${summary}\n\nBạn xác nhận gửi yêu cầu này? Lịch chính thức sẽ chưa thay đổi.`)) return;

    setSubmitting(true);
    try {
      const result = await api.createLecturerChangeRequest({
        official_code: timetable.official_code,
        section_code: occurrence.section_code,
        request_type: requestType,
        occurrence_date: occurrence.date,
        reason: reason.trim(),
        ...(requestType === "MOVE_ONE_OCCURRENCE" ? {
          proposed_date: targetDate,
          proposed_slot_code: slotCode,
          proposed_room_code: roomCode,
        } : {}),
      });
      setCreatedRequest(result.request);
    } catch (cause) {
      setSubmitError(requestErrorText(cause, "Không thể gửi yêu cầu điều chỉnh. Các thông tin đã nhập vẫn được giữ lại."));
    } finally {
      setSubmitting(false);
    }
  };

  const startAnother = () => {
    setCreatedRequest(null);
    setOccurrenceKey("");
    setReason("");
    setRequestType("SUSPEND_ONE_OCCURRENCE");
    setSubmitError(null);
    clearProposal();
  };

  if (createdRequest) return <section className="panel request-success" aria-live="polite">
    <div className="request-success-mark" aria-hidden="true">✓</div>
    <p className="eyebrow">Đã gửi yêu cầu</p>
    <h2>{createdRequest.request_code}</h2>
    <span className={requestStatusClass(createdRequest.status)}>{requestStatusLabels[createdRequest.status]}</span>
    <p>Yêu cầu đã được ghi nhận. Thời khóa biểu chính thức chưa thay đổi và chỉ được cập nhật sau khi Phòng Đào tạo phê duyệt, kiểm tra hợp lệ và áp dụng.</p>
    <div className="request-success-actions"><button type="button" onClick={onNavigateHistory}>Xem yêu cầu đã gửi</button><button type="button" className="secondary" onClick={startAnother}>Gửi yêu cầu khác</button></div>
  </section>;

  return <>
    <section className="panel request-form-intro">
      <h2>Gửi yêu cầu điều chỉnh một buổi dạy</h2>
      <p>Chọn tuần rồi chọn đúng buổi dạy của bạn. Yêu cầu này không tự thay đổi lịch chính thức.</p>
    </section>

    <section className="panel">
      <div className="request-week-picker">
        <div><h2>1. Chọn buổi bị ảnh hưởng</h2><p>Hệ thống chỉ hiển thị các buổi thuộc lịch giảng dạy của tài khoản hiện tại.</p></div>
        <label>Tuần học<input type="number" min="1" max="53" value={week} onChange={(event) => changeWeek(Number(event.target.value))} /></label>
      </div>
      {timetableError && <div className="alert error" role="alert"><span>{timetableError}</span><button type="button" className="secondary" onClick={() => void loadTimetable()}>Thử lại</button></div>}
      {timetableLoading ? <p className="empty" role="status">Đang tải các buổi dạy...</p> : !timetable?.official_code ? <p className="empty">Chưa có lịch chính thức được công bố để gửi yêu cầu.</p> : !occurrences.length ? <p className="empty">Bạn chưa có buổi dạy nào trong tuần {week}.</p> : <label>Buổi dạy <span className="required-mark">*</span><select value={occurrenceKey} onChange={(event) => { setOccurrenceKey(event.target.value); clearProposal(); }} required><option value="">Chọn một buổi dạy</option>{occurrences.map((item) => {
        const section = sections.get(item.section_code);
        return <option key={occurrenceValue(item)} value={occurrenceValue(item)}>{formatRequestDate(item.date)} · {section?.course_name || item.course_name || item.section_code} ({item.section_code}) · {periodLabel(item)} · phòng {item.room_code || "chưa xếp"}</option>;
      })}</select></label>}

      <form className="lecturer-request-form" onSubmit={submit}>
        <fieldset disabled={timetableLoading || submitting || !occurrence}>
          <legend>2. Nội dung yêu cầu</legend>
          <div className="request-type-options">
            {(Object.keys(requestTypeLabels) as LecturerChangeRequestType[]).map((type) => <label className={requestType === type ? "selected" : ""} key={type}><input type="radio" name="request-type" value={type} checked={requestType === type} onChange={() => { setRequestType(type); clearProposal(); }} /><span><strong>{requestTypeLabels[type]}</strong><small>{type === "SUSPEND_ONE_OCCURRENCE" ? "Đề nghị không tổ chức buổi đã chọn." : "Đề xuất một ngày, khung giờ và phòng khác cho buổi đã chọn."}</small></span></label>)}
          </div>

          <label>Lý do <span className="required-mark">*</span><textarea value={reason} onChange={(event) => setReason(event.target.value)} required rows={4} placeholder="Trình bày lý do để Phòng Đào tạo xem xét" /></label>

          {requestType === "MOVE_ONE_OCCURRENCE" && <section className="proposal-fields" aria-labelledby="proposal-title">
            <h3 id="proposal-title">3. Phương án đề xuất</h3>
            <label>Ngày đề xuất <span className="required-mark">*</span><input type="date" value={targetDate} onChange={(event) => setTargetDate(event.target.value)} required /></label>
            {optionsLoading && <p className="empty" role="status">Đang tải khung giờ và phòng có thể đề xuất...</p>}
            {optionsError && <div className="alert error" role="alert"><span>{optionsError}</span><button type="button" className="secondary" onClick={() => void loadOptions()}>Thử lại</button></div>}
            {!optionsLoading && targetDate && !optionsError && !options.length && <p className="empty">Không có khung giờ và phòng phù hợp cho ngày đã chọn.</p>}
            {!!options.length && <div className="form-grid"><label>Khung giờ <span className="required-mark">*</span><select value={slotCode} onChange={(event) => { setSlotCode(event.target.value); setRoomCode(""); }} required><option value="">Chọn khung giờ</option>{options.map((slot) => <option key={slot.slot_code} value={slot.slot_code}>{periodLabel(slot)} ({slot.rooms.length} phòng)</option>)}</select></label><label>Phòng học <span className="required-mark">*</span><select value={roomCode} onChange={(event) => setRoomCode(event.target.value)} disabled={!selectedSlot} required><option value="">Chọn phòng</option>{availableRooms.map((room) => <option key={room.room_code} value={room.room_code}>{room.room_code} · {room.room_name} · {room.capacity} chỗ</option>)}</select></label></div>}
          </section>}
        </fieldset>
        {submitError && <div className="alert error" role="alert">{submitError}</div>}
        <div className="request-form-actions"><button type="submit" disabled={submitting || timetableLoading || !occurrence || (requestType === "MOVE_ONE_OCCURRENCE" && (!targetDate || !slotCode || !roomCode))}>{submitting ? "Đang gửi..." : "Xác nhận và gửi yêu cầu"}</button></div>
      </form>
    </section>
  </>;
}

function occurrenceValue(item: LecturerTimetableOccurrence) {
  return [item.section_code, item.date, item.slot_code, item.room_code].join("|");
}

function periodLabel(item?: { start_period?: number; end_period?: number; slot_code?: string }) {
  if (!item) return "Chưa chọn khung giờ";
  return item.start_period !== undefined && item.end_period !== undefined
    ? `Tiết ${item.start_period}–${item.end_period}`
    : item.slot_code || "Chưa xác định khung giờ";
}
