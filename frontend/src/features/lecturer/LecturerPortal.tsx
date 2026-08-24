import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api } from "../../api/client";
import { LecturerRequestCreatePage } from "../lecturer-requests/LecturerRequestCreatePage";
import { LecturerRequestHistoryPage } from "../lecturer-requests/LecturerRequestHistoryPage";
import { PortalLayout } from "../../layouts/PortalLayout";
import type { AuthUser, LecturerCourseSection, LecturerTimetable, LecturerTimetableOccurrence } from "../../types";

interface LecturerPortalProps {
  user: AuthUser;
  path: string;
  onNavigate: (path: string) => void;
  onLogout: () => void | Promise<void>;
}

const navigation = [
  { path: "/lecturer/timetable", label: "Lịch giảng dạy của tôi" },
  { path: "/lecturer/course-sections", label: "Lớp học phần được phân công" },
  { path: "/lecturer/requests/new", label: "Gửi yêu cầu điều chỉnh" },
  { path: "/lecturer/requests", label: "Yêu cầu đã gửi" },
];
const days = [
  { code: 2, label: "Thứ Hai", short: "T2" }, { code: 3, label: "Thứ Ba", short: "T3" }, { code: 4, label: "Thứ Tư", short: "T4" },
  { code: 5, label: "Thứ Năm", short: "T5" }, { code: 6, label: "Thứ Sáu", short: "T6" }, { code: 7, label: "Thứ Bảy", short: "T7" }, { code: 8, label: "Chủ nhật", short: "CN" },
];

const SESSION_SLOTS = [
  { key: "morning", label: "Sáng", test: (p: number) => p >= 1 && p <= 6 },
  { key: "afternoon", label: "Chiều", test: (p: number) => p >= 7 && p <= 12 },
  { key: "evening", label: "Tối", test: (p: number) => p >= 13 },
];

export function LecturerPortal({ user, path, onNavigate, onLogout }: LecturerPortalProps) {
  const sectionsPage = path === "/lecturer/course-sections";
  const requestCreatePage = path === "/lecturer/requests/new";
  const requestHistoryPage = path === "/lecturer/requests";

  const pageCopy = requestCreatePage
    ? { title: "Gửi yêu cầu điều chỉnh", description: "Đề nghị tạm ngưng hoặc chuyển một buổi dạy thuộc lịch của bạn." }
    : requestHistoryPage
      ? { title: "Yêu cầu đã gửi", description: "Theo dõi trạng thái, kết quả xử lý và lịch sử các yêu cầu của bạn." }
      : sectionsPage
        ? { title: "Lớp học phần được phân công", description: "Xem thông tin các lớp học phần đang được phân công giảng dạy." }
        : { title: "Lịch giảng dạy của tôi", description: "Theo dõi lịch cá nhân theo từng tuần, bao gồm cả lịch cuối tuần và buổi học bù." };

  return <PortalLayout
    user={user}
    navigation={navigation}
    currentPath={path}
    onNavigate={onNavigate}
    onLogout={onLogout}
    eyebrow="Cổng Giảng viên"
    title={pageCopy.title}
    description={pageCopy.description}
  >
    {requestCreatePage
      ? <LecturerRequestCreatePage onNavigateHistory={() => onNavigate("/lecturer/requests")} />
      : requestHistoryPage
        ? <LecturerRequestHistoryPage onCreateRequest={() => onNavigate("/lecturer/requests/new")} />
        : sectionsPage
          ? <AssignedSectionsContainer />
          : <WeeklyTimetable />}
  </PortalLayout>;
}

function weekDateRange(data: LecturerTimetable | null, week: number): string {
  const weekStart = timetableWeekStart(data, week);
  if (weekStart) {
    const first = new Date(`${weekStart}T00:00:00`);
    const last = new Date(first);
    last.setDate(first.getDate() + 6);
    const fmt = (d: Date) => new Intl.DateTimeFormat("vi-VN", { day: "2-digit", month: "2-digit" }).format(d);
    return `${fmt(first)} – ${fmt(last)}`;
  }
  return "";
}

function timetableWeekStart(data: LecturerTimetable | null, week: number): string | null {
  const explicit = data?.academic_week === week ? data?.week_start_date?.slice(0, 10) : undefined;
  const fallback = (data?.occurrences || [])
    .filter((item) => item.academic_week === week)
    .map((item) => item.date.slice(0, 10))
    .sort()[0];
  const source = explicit || fallback;
  if (!source) return null;
  const date = new Date(`${source}T00:00:00`);
  date.setDate(date.getDate() - ((date.getDay() + 6) % 7));
  return localDateKey(date);
}

// Self-contained: owns week + data state so parent never re-renders on week change
function WeeklyTimetable() {
  const [week, setWeek] = useState(1);
  const [displayWeekStart, setDisplayWeekStart] = useState(() => mondayOf(localDateKey(new Date())));
  const [selectedDate, setSelectedDate] = useState(() => localDateKey(new Date()));
  const [data, setData] = useState<LecturerTimetable | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (w: number) => {
    setLoading(true); setError(null);
    try { setData(await api.lecturerTimetable(w, selectedDate)); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Không thể tải lịch giảng dạy."); }
    finally { setLoading(false); }
  }, [selectedDate]);

  useEffect(() => { void load(week); }, [load, week]);

  useEffect(() => {
    const fromApi = timetableWeekStart(data, week);
    if (fromApi && (data?.occurrences?.length || data?.week_start_date)) setDisplayWeekStart(fromApi);
  }, [data, week]);

  const onWeekChange = useCallback((nextWeek: number, explicitStart?: string) => {
    const target = Math.min(53, Math.max(1, nextWeek));
    setDisplayWeekStart((current) => explicitStart || addDays(current, (target - week) * 7));
    setWeek(target);
  }, [week]);

  const moveByWeek = useCallback((offset: number) => {
    const nextStart = addDays(displayWeekStart, offset * 7);
    setSelectedDate(nextStart);
    onWeekChange(Math.min(53, Math.max(1, week + offset)), nextStart);
  }, [displayWeekStart, onWeekChange, week]);

  // Accumulate ALL occurrence dates + their academic_week seen across all week loads
  // so the calendar picker always knows the correct week to load when any date is clicked.
  const [allDates, setAllDates] = useState<Set<string>>(new Set());
  const [dateWeekMap, setDateWeekMap] = useState<Map<string, number>>(new Map());
  useEffect(() => {
    if (data?.teaching_dates?.length || data?.occurrences?.length) {
      setAllDates((prev) => {
        const next = new Set(prev);
        (data.teaching_dates || data.occurrences.map((o) => o.date)).forEach((value) => next.add(value.slice(0, 10)));
        return next.size === prev.size ? prev : next;
      });
      setDateWeekMap((prev) => {
        let changed = false;
        const next = new Map(prev);
        data.occurrences.forEach((o) => {
          const key = o.date.slice(0, 10);
          if (o.academic_week && !next.has(key)) { next.set(key, o.academic_week); changed = true; }
        });
        return changed ? next : prev;
      });
    }
  }, [data]);

  useEffect(() => {
    if (!selectedDate && data?.occurrences?.[0]?.date) setSelectedDate(data.occurrences[0].date.slice(0, 10));
  }, [data, selectedDate]);

  if (error) return <div className="alert error" role="alert"><span>{error}</span><button type="button" className="secondary" onClick={() => void load(week)}>Thử lại</button></div>;

  // byDaySlot: Map<dayCode, Map<slotKey, items[]>>
  const byDaySlot = useMemo(() => {
    const groups = new Map<number, Map<string, LecturerTimetableOccurrence[]>>();
    days.forEach((day) => {
      const slotMap = new Map<string, LecturerTimetableOccurrence[]>();
      SESSION_SLOTS.forEach((s) => slotMap.set(s.key, []));
      groups.set(day.code, slotMap);
    });
    (data?.occurrences || []).forEach((item) => {
      const dayCode = item.day_of_week || dayCodeFromDate(item.date);
      const period = Number(item.start_period || 0);
      const slot = SESSION_SLOTS.find((s) => s.test(period)) || SESSION_SLOTS[0];
      groups.get(dayCode)?.get(slot.key)?.push(item);
    });
    groups.forEach((slotMap) => slotMap.forEach((items) => items.sort((a, b) => Number(a.start_period || 0) - Number(b.start_period || 0))));
    return groups;
  }, [data]);

  // Count per day
  const countByDay = useMemo(() => {
    const counts = new Map<number, number>();
    days.forEach((d) => counts.set(d.code, 0));
    (data?.occurrences || []).forEach((item) => {
      const dc = item.day_of_week || dayCodeFromDate(item.date);
      counts.set(dc, (counts.get(dc) || 0) + 1);
    });
    return counts;
  }, [data]);

  return <>
    {/* === Week navigation bar === */}
    <section className="wt-nav-bar panel">
      <div className="wt-nav-left">

        <div>
          <div className="wt-week-range">{data?.week_start_date && data.week_end_date ? `${formatDate(data.week_start_date)} – ${formatDate(data.week_end_date)}` : "Đang tải ngày tuần..."}</div>
        </div>
      </div>
      <div className="wt-nav-actions">
        <button type="button" className="wt-nav-btn" onClick={() => moveByWeek(-1)} aria-label="Tuần trước">
          ‹ Trước
        </button>
        <button type="button" className="wt-today-btn secondary" onClick={() => {
          const today = localDateKey(new Date());
          const match = data?.occurrences.find((o) => o.date.slice(0, 10) === today);
          setSelectedDate(today);
          setDisplayWeekStart(mondayOf(today));
          onWeekChange(match?.academic_week || dateWeekMap.get(today) || week, mondayOf(today));
        }}>
          Hôm nay
        </button>
        <button type="button" className="wt-nav-btn" onClick={() => moveByWeek(1)} aria-label="Tuần sau">
          Tiếp ›
        </button>
      </div>
    </section>

    <EnhancedCalendarPicker data={data} allDates={allDates} dateWeekMap={dateWeekMap} selectedDate={selectedDate} onDateSelected={setSelectedDate} onWeekChange={onWeekChange} />
    <section className="week-date-picker legacy-date-picker" aria-label="Chọn ngày trong lịch">
      <label>Chọn ngày<input aria-label="Chọn ngày" type="date" value={selectedDate} onChange={(event) => { const value = event.target.value; setSelectedDate(value); const match = data?.occurrences.find((item) => item.date.slice(0, 10) === value); onWeekChange(match?.academic_week || dateWeekMap.get(value) || isoWeek(value), mondayOf(value)); }} /></label>
      <span className="field-help">Chọn ngày để chuyển nhanh đến tuần tương ứng.</span>
    </section>

    {loading && !data ? (
      <p className="empty" role="status">Đang tải lịch giảng dạy...</p>
    ) : (
      <>
      <section className="wt-grid" aria-label={`Lịch giảng dạy tuần ${week}`}>
        {/* Header row: Ca học | Mon … Sun */}
        <div className="wt-header-cell wt-slot-label-header">Ca học</div>
        {days.map((day) => {
          const cnt = countByDay.get(day.code) || 0;
          const weekStartValue = data?.week_start_date || "";
          const weekStart = weekStartValue ? new Date(`${weekStartValue}T00:00:00`) : null;
          const dayDate = weekStart ? (() => { const target = new Date(weekStart); target.setDate(weekStart.getDate() + day.code - 2); return localDateKey(target); })() : null;
          return (
            <div className="wt-header-cell wt-day-header" key={day.code}>
              <span className="wt-day-name">{day.label}</span>
              {dayDate && <span className="wt-day-date">{formatDate(dayDate)}</span>}
              {cnt > 0 && <span className="wt-day-count">{cnt} buổi</span>}
            </div>
          );
        })}

        {/* Session rows */}
        {SESSION_SLOTS.map((slot) => (
          <>
            {/* Row label */}
            <div className={`wt-slot-label wt-slot-${slot.key}`} key={`label-${slot.key}`}>{slot.label}</div>
            {/* Day cells */}
            {days.map((day) => {
              const items = byDaySlot.get(day.code)?.get(slot.key) || [];
              return (
                <div className={`wt-cell ${slot.key === "evening" ? "wt-cell-evening" : ""}`} key={`${day.code}-${slot.key}`}>
                  {items.length ? items.map((item) => (
                    <SessionCard item={item} key={`${item.section_code}-${item.date}-${item.slot_code}`} />
                  )) : (
                    <span className="wt-empty-cell">—</span>
                  )}
                </div>
              );
            })}
          </>
        ))}
      </section>
      {!data?.occurrences.length && <p className="empty wt-empty-week">Giảng viên chưa có lịch dạy trong tuần này.</p>}
      </>
    )}
  </>;
}

function EnhancedCalendarPicker({ data, allDates, dateWeekMap, selectedDate: externalSelectedDate, onDateSelected, onWeekChange }: { data: LecturerTimetable | null; allDates: Set<string>; dateWeekMap: Map<string, number>; selectedDate?: string; onDateSelected: (value: string) => void; onWeekChange: (week: number, explicitStart?: string) => void }) {
  const initial = data?.week_start_date?.slice(0, 10) || data?.occurrences?.[0]?.date?.slice(0, 10) || localDateKey(new Date());
  const [selected, setSelected] = useState(initial);
  const [month, setMonth] = useState(() => new Date(`${initial}T00:00:00`));
  const [open, setOpen] = useState(false);
  const pickerRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!open) return;
    const closeWhenOutside = (event: PointerEvent) => {
      const target = event.target as Node | null;
      if (target && pickerRef.current && !pickerRef.current.contains(target)) setOpen(false);
    };
    document.addEventListener("pointerdown", closeWhenOutside);
    return () => document.removeEventListener("pointerdown", closeWhenOutside);
  }, [open]);

  useEffect(() => {
    if (!externalSelectedDate) return;
    setSelected(externalSelectedDate);
    setMonth(new Date(`${externalSelectedDate}T00:00:00`));
  }, [externalSelectedDate]);

  // When the loaded week changes (data prop updates), jump the picker to Monday of that week.
  // Use local date parts to avoid the UTC+7 timezone shift from toISOString().
  useEffect(() => {
    const firstDate = data?.week_start_date?.slice(0, 10) || data?.occurrences?.[0]?.date?.slice(0, 10);
    if (!firstDate) return;
    const d = new Date(`${firstDate}T00:00:00`);
    const dayOfWeek = d.getDay(); // 0=Sun
    d.setDate(d.getDate() + (dayOfWeek === 0 ? -6 : 1 - dayOfWeek));
    const y = d.getFullYear();
    const mo = String(d.getMonth() + 1).padStart(2, "0");
    const dy = String(d.getDate()).padStart(2, "0");
    const monday = `${y}-${mo}-${dy}`;
    setSelected(monday);
    setMonth(new Date(`${monday}T00:00:00`));
  }, [data]);

  const choose = (value: string) => {
    setSelected(value);
    setOpen(false);
    onDateSelected(value);
    // Keep the academic week when selecting one of its dates, even when it has no lecturer sessions.
    const match = data?.occurrences.find((item) => item.date.slice(0, 10) === value);
    const inCurrentWeek = Boolean(data?.week_start_date && data?.week_end_date && value >= data.week_start_date.slice(0, 10) && value <= data.week_end_date.slice(0, 10));
    const academicWeek = (inCurrentWeek ? data?.academic_week : undefined) ?? match?.academic_week ?? dateWeekMap.get(value) ?? isoWeek(value);
    onWeekChange(academicWeek, mondayOf(value));
  };
  const years = Array.from({ length: 11 }, (_, index) => new Date().getFullYear() - 5 + index);
  const MONTHS = ["Tháng 1","Tháng 2","Tháng 3","Tháng 4","Tháng 5","Tháng 6","Tháng 7","Tháng 8","Tháng 9","Tháng 10","Tháng 11","Tháng 12"];
  return (
    <section className="compact-calendar-picker" ref={pickerRef}>
      <button type="button" className="compact-calendar-trigger" onClick={() => setOpen((v) => !v)} aria-expanded={open}>
        <span className="calendar-icon">▦</span>
        <span><small>Đang xem tuần</small><strong>{formatDate(selected)}</strong></span>
        <span className="calendar-chevron">⌄</span>
      </button>
      {open && (
        <div className="compact-calendar-popover">
          <div className="compact-calendar-head">
            <button type="button" onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() - 1, 1))}>‹</button>
            <div className="ccp-month-year-selects">
              <select
                aria-label="Chọn tháng"
                value={month.getMonth()}
                onChange={(e) => setMonth(new Date(month.getFullYear(), Number(e.target.value), 1))}
              >
                {MONTHS.map((label, index) => <option value={index} key={label}>{label}</option>)}
              </select>
              <select
                aria-label="Chọn năm"
                value={month.getFullYear()}
                onChange={(e) => setMonth(new Date(Number(e.target.value), month.getMonth(), 1))}
              >
                {years.map((year) => <option value={year} key={year}>{year}</option>)}
              </select>
            </div>
            <button type="button" onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() + 1, 1))}>›</button>
          </div>
          <div className="compact-calendar-weekdays">
            {["T2", "T3", "T4", "T5", "T6", "T7", "CN"].map((day) => <span key={day}>{day}</span>)}
          </div>
          <div className="compact-calendar-grid">
            {monthCells(month).map((cell) => (
              <button
                type="button"
                className={`${cell.month === month.getMonth() ? "" : "muted-day"} ${cell.value === selected ? "picked-day" : ""} ${allDates.has(cell.value) ? "busy-day" : ""}`}
                key={cell.value}
                onClick={() => choose(cell.value)}
              >{cell.day}</button>
            ))}
          </div>
          <small className="calendar-help"><span className="calendar-help-dot" aria-hidden="true">●</span> Có lịch dạy trong ngày</small>
        </div>
      )}
    </section>
  );
}

function monthCells(value: Date) {
  const first = new Date(value.getFullYear(), value.getMonth(), 1);
  const offset = (first.getDay() + 6) % 7;
  return Array.from({ length: 42 }, (_, index) => {
    const date = new Date(value.getFullYear(), value.getMonth(), index - offset + 1);
    // Use local date parts (NOT toISOString which converts to UTC and shifts the date
    // by -1 day in UTC+7, causing dots to appear on wrong cells).
    return { value: localDateKey(date), day: date.getDate(), month: date.getMonth() };
  });
}

/** Format a calendar key from local date parts; never use UTC ISO conversion here. */
function localDateKey(value: Date): string {
  const y = value.getFullYear();
  const m = String(value.getMonth() + 1).padStart(2, "0");
  const d = String(value.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function mondayOf(value: string): string {
  const date = new Date(`${value.slice(0, 10)}T00:00:00`);
  date.setDate(date.getDate() - ((date.getDay() + 6) % 7));
  return localDateKey(date);
}

function addDays(value: string, days: number): string {
  const date = new Date(`${value.slice(0, 10)}T00:00:00`);
  date.setDate(date.getDate() + days);
  return localDateKey(date);
}

function monthLabel(value: Date) {
  return new Intl.DateTimeFormat("vi-VN", { month: "long", year: "numeric" }).format(value);
}

const SESSION_STATUS_COLOR: Record<string, string> = {
  MAKEUP: "sc-makeup",
  MOVED: "sc-moved",
  ADJUSTED: "sc-adjusted",
  SUSPENDED: "sc-suspended",
  EXCEPTION: "sc-exception",
};

function SessionCard({ item }: { item: LecturerTimetableOccurrence }) {
  const isSpecial = !['SCHEDULED', 'NORMAL'].includes(item.status);
  const colorClass = SESSION_STATUS_COLOR[item.status] || "sc-normal";
  return (
    <article className={`session-card ${colorClass}`}>
      <div className="sc-top">
        <strong className="sc-name">{item.course_name || item.section_code}</strong>
        {isSpecial && <span className={`pill ${item.status === "SUSPENDED" ? "pill-danger" : "pill-info"}`}>{statusLabel(item.status)}</span>}
      </div>
      <span className="sc-code">{item.section_code}{item.course_code ? ` · ${item.course_code}` : ""}</span>
      <div className="sc-meta">
        <span className="sc-meta-item"><span className="sc-meta-label">Tiết</span> {periodLabel(item)}</span>
        <span className="sc-meta-item"><span className="sc-meta-label">Phòng</span> {item.room_code || "Chưa xếp"}</span>
      </div>
    </article>
  );
}

// Fetches its own data so it doesn't depend on parent's week state
function AssignedSectionsContainer() {
  const [loading, setLoading] = useState(true);
  const [sections, setSections] = useState<LecturerCourseSection[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    setLoading(true); setError(null);
    api.lecturerTimetable(1)
      .then((d) => setSections(d.course_sections || []))
      .catch((e) => setError(e instanceof Error ? e.message : "Không thể tải dữ liệu."))
      .finally(() => setLoading(false));
  }, []);
  if (loading) return <p className="empty" role="status">Đang tải lớp học phần...</p>;
  if (error) return <div className="alert error" role="alert"><span>{error}</span></div>;
  if (!sections.length) return <p className="empty">Chưa có lớp học phần nào được phân công.</p>;
  return <AssignedSections sections={sections} />;
}

const COURSE_TYPE_ACCENT: Record<string, string> = {
  THEORY: "#176b87",
  PRACTICE: "#1a8a5a",
  INTEGRATED: "#7e3cb4",
};

function AssignedSections({ sections }: { sections: LecturerCourseSection[] }) {
  return (
    <section className="cs-grid">
      {sections.map((section) => {
        const accent = COURSE_TYPE_ACCENT[section.course_type || ""] || "#176b87";
        return (
          <article className="cs-card" key={section.section_code} style={{ "--cs-accent": accent } as React.CSSProperties}>
            <div className="cs-card-top">
              <div className="cs-card-title-block">
                <p className="cs-eyebrow">{section.course_code || "Lớp học phần"}</p>
                <h2 className="cs-title">{section.course_name || section.section_code}</h2>
                <span className="cs-section-code">{section.section_code}</span>
              </div>
              {section.course_type && (
                <span className={`cs-type-badge cs-type-${(section.course_type || "").toLowerCase()}`}>
                  {courseTypeLabel(section.course_type)}
                </span>
              )}
            </div>
            <div className="cs-divider" />
            <dl className="cs-info-grid">
              <div className="cs-info-item">
                <dt>Lịch cố định</dt>
                <dd>{section.day_of_week ? `${dayLabel(section.day_of_week)}, ${periodLabel(section)}` : "Chưa có lịch"}</dd>
              </div>
              <div className="cs-info-item">
                <dt>Mã lớp học phần</dt>
                <dd>{section.section_code}</dd>
              </div>
              <div className="cs-info-item cs-date-item">
                <dt>Thời gian giảng dạy</dt>
                <dd>{section.start_date && section.end_date ? `${formatDate(section.start_date)} – ${formatDate(section.end_date)}` : "Chưa có dữ liệu"}</dd>
              </div>
              <div className="cs-info-item">
                <dt>Số buổi yêu cầu</dt>
                <dd>{section.required_sessions ?? "—"}</dd>
              </div>
              <div className="cs-info-item">
                <dt>Sĩ số xếp lịch</dt>
                <dd>{section.scheduling_student_count ?? "—"}</dd>
              </div>
            </dl>
          </article>
        );
      })}
    </section>
  );
}

function dayCodeFromDate(value: string) {
  const day = new Date(`${value.slice(0, 10)}T00:00:00`).getDay();
  return day === 0 ? 8 : day + 1;
}

function isoWeek(value: string) {
  const date = new Date(`${value}T00:00:00`);
  if (Number.isNaN(date.getTime())) return 1;
  date.setDate(date.getDate() + 4 - (date.getDay() || 7));
  const yearStart = new Date(date.getFullYear(), 0, 1);
  return Math.ceil((((date.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
}

function dayLabel(code: number) {
  return days.find((day) => day.code === code)?.label || `Ngày ${code}`;
}

function periodLabel(item: { start_period?: number; end_period?: number; slot_code?: string }) {
  return item.start_period && item.end_period ? `Tiết ${item.start_period}–${item.end_period}` : item.slot_code || "Chưa xếp";
}

function statusLabel(status: string) {
  const labels: Record<string, string> = { SCHEDULED: "Bình thường", NORMAL: "Bình thường", MAKEUP: "Học bù", MOVED: "Đã chuyển", ADJUSTED: "Đã điều chỉnh", SEGMENT: "Theo phân đoạn", EXCEPTION: "Ngoại lệ một buổi", SUSPENDED: "Tạm ngưng" };
  return labels[status] || "Buổi học";
}

function courseTypeLabel(type: string) {
  return ({ THEORY: "Lý thuyết", PRACTICE: "Thực hành", INTEGRATED: "Lý thuyết – thực hành" } as Record<string, string>)[type] || "Lớp học phần";
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("vi-VN").format(new Date(`${value.slice(0, 10)}T00:00:00`));
}
