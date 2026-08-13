import { useCallback, useEffect, useMemo, useState } from "react";
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
  { code: 2, label: "Thứ Hai" }, { code: 3, label: "Thứ Ba" }, { code: 4, label: "Thứ Tư" },
  { code: 5, label: "Thứ Năm" }, { code: 6, label: "Thứ Sáu" }, { code: 7, label: "Thứ Bảy" }, { code: 8, label: "Chủ nhật" },
];

export function LecturerPortal({ user, path, onNavigate, onLogout }: LecturerPortalProps) {
  const [week, setWeek] = useState(1);
  const [data, setData] = useState<LecturerTimetable | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const sectionsPage = path === "/lecturer/course-sections";
  const requestCreatePage = path === "/lecturer/requests/new";
  const requestHistoryPage = path === "/lecturer/requests";
  const timetableDataPage = path === "/lecturer/timetable" || sectionsPage;

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try { setData(await api.lecturerTimetable(week)); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Không thể tải lịch giảng dạy."); }
    finally { setLoading(false); }
  }, [week]);
  useEffect(() => { if (timetableDataPage) void load(); }, [load, timetableDataPage]);

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
    {timetableDataPage && error && <div className="alert error" role="alert"><span>{error}</span><button type="button" className="secondary" onClick={() => void load()}>Thử lại</button></div>}
    {requestCreatePage
      ? <LecturerRequestCreatePage onNavigateHistory={() => onNavigate("/lecturer/requests")} />
      : requestHistoryPage
        ? <LecturerRequestHistoryPage onCreateRequest={() => onNavigate("/lecturer/requests/new")} />
        : sectionsPage
          ? <AssignedSections loading={loading} sections={data?.course_sections || []} />
          : <WeeklyTimetable loading={loading} data={data} week={week} onWeekChange={setWeek} />}
  </PortalLayout>;
}

function WeeklyTimetable({ loading, data, week, onWeekChange }: { loading: boolean; data: LecturerTimetable | null; week: number; onWeekChange: (week: number) => void }) {
  const byDay = useMemo(() => {
    const groups = new Map<number, LecturerTimetableOccurrence[]>();
    days.forEach((day) => groups.set(day.code, []));
    (data?.occurrences || []).forEach((item) => groups.get(item.day_of_week || dayCodeFromDate(item.date))?.push(item));
    groups.forEach((items) => items.sort((first, second) => Number(first.start_period || 0) - Number(second.start_period || 0) || first.date.localeCompare(second.date)));
    return groups;
  }, [data]);

  return <>
    <section className="panel week-toolbar">
      <div><h2>Tuần học {week}</h2><p>{data?.official_code ? `Lịch chính thức ${data.official_code}` : "Chưa có lịch chính thức được công bố."}</p></div>
      <div className="week-actions"><button type="button" className="secondary" disabled={week <= 1} onClick={() => onWeekChange(Math.max(1, week - 1))}>Tuần trước</button><label>Chọn tuần<input aria-label="Tuần học" type="number" min="1" max="53" value={week} onChange={(event) => onWeekChange(Math.min(53, Math.max(1, Number(event.target.value) || 1)))} /></label><button type="button" className="secondary" disabled={week >= 53} onClick={() => onWeekChange(Math.min(53, week + 1))}>Tuần sau</button></div>
    </section>
    {loading ? <p className="empty" role="status">Đang tải lịch giảng dạy...</p> : !data?.occurrences.length ? <p className="empty">Giảng viên chưa có lịch trong tuần này.</p> : <section className="weekly-calendar" aria-label={`Lịch giảng dạy tuần ${week}`}>{days.map((day) => <article className={`calendar-day ${day.code >= 7 ? "weekend" : ""}`} key={day.code}><header><h2>{day.label}</h2><span>{byDay.get(day.code)?.length || 0} buổi</span></header><div className="calendar-sessions">{byDay.get(day.code)?.length ? byDay.get(day.code)?.map((item) => <SessionCard item={item} key={`${item.section_code}-${item.date}-${item.slot_code}`} />) : <p>Không có lịch</p>}</div></article>)}</section>}
  </>;
}

function SessionCard({ item }: { item: LecturerTimetableOccurrence }) {
  return <article className="session-card">
    <div className="session-card-heading"><strong>{item.course_name || item.section_code}</strong><span className="pill">{statusLabel(item.status)}</span></div>
    <span>{item.section_code}{item.course_code ? ` · ${item.course_code}` : ""}</span>
    <dl><div><dt>Ngày</dt><dd>{formatDate(item.date)}</dd></div><div><dt>Tiết</dt><dd>{periodLabel(item)}</dd></div><div><dt>Phòng</dt><dd>{item.room_code || "Chưa xếp"}</dd></div></dl>
  </article>;
}

function AssignedSections({ loading, sections }: { loading: boolean; sections: LecturerCourseSection[] }) {
  if (loading) return <p className="empty" role="status">Đang tải lớp học phần...</p>;
  if (!sections.length) return <p className="empty">Chưa có lớp học phần nào được phân công.</p>;
  return <section className="section-card-grid">{sections.map((section) => <article className="panel course-section-card" key={section.section_code}><div className="panel-heading"><div><p className="eyebrow">{section.course_code || "Lớp học phần"}</p><h2>{section.course_name || section.section_code}</h2><p>{section.section_code}</p></div>{section.course_type && <span className="pill">{courseTypeLabel(section.course_type)}</span>}</div><dl className="section-facts"><div><dt>Lịch cố định</dt><dd>{section.day_of_week ? `${dayLabel(section.day_of_week)}, ${periodLabel(section)}` : "Chưa có lịch"}</dd></div><div><dt>Phòng</dt><dd>{section.room_code || "Chưa xếp"}</dd></div><div><dt>Số buổi yêu cầu</dt><dd>{section.required_sessions ?? "—"}</dd></div><div><dt>Sĩ số xếp lịch</dt><dd>{section.scheduling_student_count ?? "—"}</dd></div></dl></article>)}</section>;
}

function dayCodeFromDate(value: string) {
  const day = new Date(`${value.slice(0, 10)}T00:00:00`).getDay();
  return day === 0 ? 8 : day + 1;
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
