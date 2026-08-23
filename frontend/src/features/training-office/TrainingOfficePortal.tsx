import { PortalLayout } from "../../layouts/PortalLayout";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { api } from "../../api/client";
import { TrainingRequestReviewPage } from "../lecturer-requests/TrainingRequestReviewPage";
import type { AdjustmentScope, Assignment, AuthUser, Batch, Occurrence, OfficialTimetable, Preview, Run } from "../../types";

type Page = "overview" | "import" | "ga" | "results" | "adjustments" | "requests";
const requiredFiles = ["lecturers.csv", "rooms.csv", "time_slots.csv", "course_sections.csv", "lecturer_time_preferences.csv", "room_unavailable_slots.csv", "academic_calendar.csv"];
const pages: { key: Page; label: string; note: string }[] = [
  {
    key: "overview",
    label: "Tổng quan",
    note: "Theo dõi dữ liệu, lịch xếp và các công việc cần xử lý.",
  },
  {
    key: "import",
    label: "Dữ liệu đầu vào",
    note: "Tải lên, kiểm tra và xác nhận dữ liệu phục vụ xếp thời khóa biểu.",
  },
  {
    key: "ga",
    label: "Cấu hình & chạy GA",
    note: "Thiết lập tham số Genetic Algorithm và thực hiện xếp lịch.",
  },
  {
    key: "results",
    label: "Kết quả thời khóa biểu",
    note: "Xem, lọc và công bố phương án thời khóa biểu.",
  },
  {
    key: "adjustments",
    label: "Điều chỉnh lịch",
    note: "Điều chỉnh lịch chính thức và kiểm tra xung đột trước khi áp dụng.",
  },
  {
    key: "requests",
    label: "Yêu cầu giảng viên",
    note: "Xem xét, phê duyệt hoặc từ chối yêu cầu điều chỉnh lịch.",
  },
];
const days: Record<number, string> = { 2: "Thứ Hai", 3: "Thứ Ba", 4: "Thứ Tư", 5: "Thứ Năm", 6: "Thứ Sáu", 7: "Thứ Bảy", 8: "Chủ nhật" };
const courseTypes: Record<string, string> = { THEORY: "Lý thuyết", PRACTICE: "Thực hành", INTEGRATED: "Lý thuyết – thực hành" };
const formatDate = (value?: string) => value ? new Intl.DateTimeFormat("vi-VN").format(new Date(`${value.slice(0, 10)}T00:00:00`)) : "—";
const formatDateTime = (value?: string) => value ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "short", timeStyle: "short", timeZone: "Asia/Ho_Chi_Minh" }).format(new Date(value)) : "—";
const batchLabel = (batch: Batch) => [batch.display_name || batch.batch_code, batch.semester, batch.academic_year].filter(Boolean).join(" · ");
const errorText = (error: unknown) => error instanceof Error ? error.message : "Đã có lỗi không mong muốn.";

interface TrainingOfficePortalProps {
  user: AuthUser;
  path: string;
  onNavigate: (path: string) => void;
  onLogout: () => void | Promise<void>;
}

const pagePaths: Record<Page, string> = {
  overview: "/training-office/overview",
  import: "/training-office/import",
  ga: "/training-office/ga",
  results: "/training-office/results",
  adjustments: "/training-office/adjustments",
  requests: "/training-office/requests",
};

export function TrainingOfficePortal({ user, path, onNavigate, onLogout }: TrainingOfficePortalProps) {
  const page = (Object.entries(pagePaths).find(([, route]) => route === path)?.[0] as Page | undefined) || "overview";
  const [apiOnline, setApiOnline] = useState(false);
  const [batches, setBatches] = useState<Batch[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [activeRun, setActiveRun] = useState<Run | null>(null);
  const [activeOfficial, setActiveOfficial] = useState<OfficialTimetable | null>(null);
  const [notice, setNotice] = useState<{ text: string; tone: "success" | "error" } | null>(null);

  const refresh = async () => {
    try { const [nextBatches, nextRuns] = await Promise.all([api.batches(), api.runs()]); setBatches(nextBatches); setRuns(nextRuns); setApiOnline(true); }
    catch { setApiOnline(false); }
  };
  useEffect(() => { void refresh(); }, []);
  const navigate = (target: Page) => onNavigate(pagePaths[target]);
  
  const selectRun = async (runCode: string) => { try { setActiveRun(await api.run(runCode)); navigate("results"); } catch (error) { setNotice({ text: errorText(error), tone: "error" }); } };
  const activePage = pages.find((item) => item.key === page)!;
 const navigation = pages.map((item) => ({
  path: pagePaths[item.key],
  label: item.label,
}));

return (
  <PortalLayout
    user={user}
    navigation={navigation}
    currentPath={path}
    onNavigate={onNavigate}
    onLogout={onLogout}
    eyebrow="Cổng Phòng Đào tạo"
    title={activePage.label}
    description={activePage.note}
  >
    {notice && (
      <div
        className={`alert ${notice.tone}`}
        role="status"
      >
        {notice.text}

        <button
          type="button"
          onClick={() => setNotice(null)}
          aria-label="Đóng thông báo"
        >
          ×
        </button>
      </div>
    )}

    {page === "overview" && (
      <Overview
        runs={runs}
        batches={batches}
        onNavigate={navigate}
        onSelectRun={selectRun}
      />
    )}

    {page === "import" && (
      <ImportPage
        onConfirmed={async (batch) => {
          await refresh();

          setNotice({
            text: `Đã xác nhận bộ dữ liệu ${batch.batch_code}.`,
            tone: "success",
          });

          navigate("ga");
        }}
      />
    )}

    {page === "ga" && (
      <GaPage
        batches={batches}
        onRun={async (run) => {
          setActiveRun(run);
          await refresh();
          navigate("results");
        }}
      />
    )}

    {page === "results" && (
      <ResultsPage
        run={activeRun}
        runs={runs}
        onSelectRun={selectRun}
        onPublish={async (run) => {
          try {
            const official =
              await api.publishRun(run.run_code);

            setActiveOfficial(official);

            setNotice({
              text: `Đã công bố ${official.official_code} thành lịch chính thức.`,
              tone: "success",
            });

            navigate("adjustments");
          } catch (error) {
            setNotice({
              text: errorText(error),
              tone: "error",
            });
          }
        }}
      />
    )}

    {page === "adjustments" && (
      <AdjustmentsPage
        official={activeOfficial}
        onUpdate={setActiveOfficial}
      />
    )}

    {page === "requests" && (
      <TrainingRequestReviewPage
        onOfficialUpdated={setActiveOfficial}
      />
    )}
  </PortalLayout>
);
}

function Overview({ runs, batches, onNavigate, onSelectRun }: { runs: Run[]; batches: Batch[]; onNavigate: (page: Page) => void; onSelectRun: (code: string) => void }) {
  return (
  <div className="training-office-overview">
    <section className="training-office-hero">
      <div>
        <p className="eyebrow">
          Sẵn sàng lập thời khóa biểu
        </p>

        <h2>
          Quản lý dữ liệu, chạy thuật toán
          và điều chỉnh lịch tại một nơi.
        </h2>

        <button
          onClick={() =>
            onNavigate("ga")
          }
        >
          Chạy xếp lịch
        </button>
      </div>

      <div className="training-office-hero-art">
        GA
      </div>
    </section>

    <section className="training-office-metrics">
      <article className="training-office-metric">
        <span>Bộ dữ liệu đã xác nhận</span>
        <strong>{batches.length}</strong>
      </article>

      <article className="training-office-metric">
        <span>Lần chạy đã lưu</span>
        <strong>{runs.length}</strong>
      </article>

      <article className="training-office-metric">
        <span>Lần chạy gần nhất</span>
        <strong>
          {runs[0]?.status === "COMPLETED"
            ? "Hoàn thành"
            : runs[0]?.status || "Chưa có"}
        </strong>
      </article>
    </section>

    <section className="panel">
      <div className="panel-title">
        <div>
          <h2>
            Lịch sử chạy thuật toán
          </h2>

          <p>
            Chọn một phương án để xem
            lại kết quả đã lưu.
          </p>
        </div>
      </div>

      <RunList
        runs={runs}
        onSelect={onSelectRun}
      />
    </section>
  </div>
);
}
function RunList({ runs, onSelect }: { runs: Run[]; onSelect: (code: string) => void }) { return runs.length ? <div className="run-list">{runs.map((run) => <button key={run.run_code} className="run-row" onClick={() => onSelect(run.run_code)}><span><strong>{run.run_code}</strong><small>{formatDate(run.created_at)}</small></span><span className={`status ${run.status.toLowerCase()}`}>{run.status === "COMPLETED" ? "Hoàn thành" : run.status}</span></button>)}</div> : <Empty text="Chưa có lần chạy thuật toán nào." />; }

function ImportPage({ onConfirmed }: { onConfirmed: (batch: Batch) => void }) {
  const [files, setFiles] = useState<File[]>([]); const [preview, setPreview] = useState<Preview | null>(null); const [busy, setBusy] = useState(false); const [displayName, setDisplayName] = useState(""); const [semester, setSemester] = useState(""); const [academicYear, setAcademicYear] = useState(""); const [note, setNote] = useState(""); const names = new Set(files.map((file) => file.name));
  const upload = async (event: FormEvent) => { event.preventDefault(); if (files.length !== 7) { setPreview({ valid: false, errors: [{ reason: "Vui lòng chọn đủ bảy tệp CSV theo danh sách." }] }); return; } setBusy(true); try { setPreview(await api.previewImport(files)); } catch (error) { setPreview({ valid: false, errors: [{ reason: errorText(error) }] }); } finally { setBusy(false); } };
  const confirm = async () => { setBusy(true); try { const result = await api.confirmImport(files, { displayName, semester, academicYear, note }); onConfirmed(result.batch); } catch (error) { setPreview({ valid: false, errors: [{ reason: errorText(error) }] }); } finally { setBusy(false); } };
  return <section className="panel"><h2>Tải bộ dữ liệu CSV</h2><p>Hệ thống chỉ nhận một bộ gồm đủ 7 tệp và kiểm tra trước khi lưu.</p><form onSubmit={upload}><label className="file-drop"><input type="file" accept=".csv,text/csv" multiple onChange={(event) => { setFiles(Array.from(event.target.files || [])); setPreview(null); }} /><strong>Chọn 7 tệp CSV</strong><span>{files.length ? `${files.length} tệp đã chọn` : "Kéo thả hoặc bấm để chọn tệp"}</span></label><div className="file-checklist">{requiredFiles.map((name) => <span className={names.has(name) ? "present" : ""} key={name}>{names.has(name) ? "✓" : "○"} {name}</span>)}</div><button disabled={busy}>{busy ? "Đang kiểm tra..." : "Kiểm tra dữ liệu"}</button></form>
    {preview && <PreviewResult preview={preview} displayName={displayName} semester={semester} academicYear={academicYear} note={note} onDisplayName={setDisplayName} onSemester={setSemester} onAcademicYear={setAcademicYear} onNote={setNote} onConfirm={confirm} busy={busy} />}</section>;
}
function PreviewResult({ preview, displayName, semester, academicYear, note, onDisplayName, onSemester, onAcademicYear, onNote, onConfirm, busy }: { preview: Preview; displayName: string; semester: string; academicYear: string; note: string; onDisplayName: (value: string) => void; onSemester: (value: string) => void; onAcademicYear: (value: string) => void; onNote: (value: string) => void; onConfirm: () => void; busy: boolean }) { return <div className={`preview ${preview.valid ? "valid" : "invalid"}`}><h3>{preview.valid ? "Dữ liệu hợp lệ" : "Phát hiện lỗi dữ liệu"}</h3>{preview.files && <ul>{preview.files.map((file) => <li key={file.file}>{file.file}: {file.row_count} dòng</li>)}</ul>}{preview.errors?.map((error, index) => <p className="error-detail" key={index}>{[error.file, error.row && `dòng ${error.row}`, error.column && `cột ${error.column}`, error.reason].filter(Boolean).join(" — ")}</p>)}{preview.valid && <><p className="metadata-intro">Đặt tên để dễ phân biệt các bộ dữ liệu; bạn có thể bỏ qua và xác nhận ngay.</p><div className="form-grid batch-metadata"><label>Tên bộ dữ liệu <span>(tùy chọn)</span><input value={displayName} onChange={(event) => onDisplayName(event.target.value)} placeholder="Ví dụ: TKB HK1 2026–2027 — Đợt 1" /></label><label>Học kỳ <span>(tùy chọn)</span><input value={semester} onChange={(event) => onSemester(event.target.value)} placeholder="Ví dụ: Học kỳ 1" /></label><label>Năm học <span>(tùy chọn)</span><input value={academicYear} onChange={(event) => onAcademicYear(event.target.value)} placeholder="Ví dụ: 2026–2027" /></label><label>Ghi chú <span>(tùy chọn)</span><textarea value={note} onChange={(event) => onNote(event.target.value)} placeholder="Ví dụ: Dữ liệu sau đăng ký đợt 1" /></label></div><button onClick={onConfirm} disabled={busy}>{busy ? "Đang xác nhận..." : "Xác nhận bộ dữ liệu"}</button></>}</div>; }

function GaPage({ batches, onRun }: { batches: Batch[]; onRun: (run: Run) => void }) {
  const [busy, setBusy] = useState(false); const [error, setError] = useState<string | null>(null);
  const submit = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const data = new FormData(event.currentTarget); setBusy(true); setError(null); try { await onRun(await api.startRun({ batch_code: String(data.get("batch_code")), population_size: Number(data.get("population_size")), generations: Number(data.get("generations")), seed: Number(data.get("seed")), crossover_rate: Number(data.get("crossover_rate")), mutation_rate: Number(data.get("mutation_rate")), elite_count: Number(data.get("elite_count")), tournament_size: Number(data.get("tournament_size")) })); } catch (reason) { setError(errorText(reason)); } finally { setBusy(false); } };
  const selectedBatch = batches[0]; return <section className="panel"><h2>Cấu hình Thuật toán Di truyền</h2><p>Các ràng buộc nghiệp vụ luôn do backend kiểm tra trước khi lưu kết quả.</p>{!batches.length && <div className="alert warning">Hãy xác nhận một bộ dữ liệu CSV trước khi chạy GA.</div>}<form className="form-grid" onSubmit={submit}><label>Bộ dữ liệu<select name="batch_code" required disabled={!batches.length}>{batches.map((batch) => <option value={batch.batch_code} key={batch.batch_code}>{batchLabel(batch)} — xác nhận {formatDateTime(batch.confirmed_at)}</option>)}</select><small className="field-help">{selectedBatch ? `${selectedBatch.section_count || 0} lớp · Phiên bản ${selectedBatch.version_number || 1} · Mã: ${selectedBatch.batch_code}` : ""}</small></label><label>Kích thước quần thể<input name="population_size" type="number" min="1" defaultValue="80" required /></label><label>Số thế hệ<input name="generations" type="number" min="1" defaultValue="200" required /></label><label>Seed<input name="seed" type="number" defaultValue="42" required /></label><label>Tỷ lệ lai ghép<input name="crossover_rate" type="number" min="0" max="1" step="0.05" defaultValue="0.8" required /></label><label>Tỷ lệ đột biến<input name="mutation_rate" type="number" min="0" max="1" step="0.05" defaultValue="0.1" required /></label><label>Số cá thể tinh hoa<input name="elite_count" type="number" min="0" defaultValue="2" required /></label><label>Kích thước tournament<input name="tournament_size" type="number" min="1" defaultValue="3" required /></label><div className="form-action"><button disabled={busy || !batches.length}>{busy ? "Đang chạy..." : "Chạy thuật toán"}</button></div></form>{error && <div className="alert error">{error}</div>}</section>;
}

type ResultSort = "day_time" | "lecturer" | "section" | "room" | "course_type";

function ResultsPage({ run, runs, onSelectRun, onPublish }: { run: Run | null; runs: Run[]; onSelectRun: (code: string) => void; onPublish: (run: Run) => void }) {
  const [search, setSearch] = useState("");
  const [type, setType] = useState("ALL");
  const [sort, setSort] = useState<ResultSort>("day_time");

  useEffect(() => {
    setSearch("");
    setType("ALL");
    setSort("day_time");
  }, [run?.run_code]);

  const filtered = useMemo(() => {
    const normalizedSearch = search.trim().toLocaleLowerCase("vi");
    return (run?.assignments || []).filter((item) => {
      const haystack = [item.section_code, item.course_code, item.course_name, item.lecturer_code, item.lecturer_name, item.room_code]
        .join(" ")
        .toLocaleLowerCase("vi");
      return (!normalizedSearch || haystack.includes(normalizedSearch))
        && (type === "ALL" || item.course_type === type);
    });
  }, [run, search, type]);

  const sorted = useMemo(() => [...filtered].sort((first, second) => compareAssignments(first, second, sort)), [filtered, sort]);

  if (!run) return <section className="panel"><h2>Chọn phương án</h2><RunList runs={runs} onSelect={onSelectRun} /></section>;

  return <>
    <section className="panel run-summary">
      <div><p className="eyebrow">Mã lần chạy</p><h2>{run.run_code}</h2><p>{run.assignments.length} lớp học phần · {run.occurrences.length} buổi học theo ngày</p></div>
      <div className="export-links"><button type="button" onClick={() => onPublish(run)}>Công bố lịch chính thức</button><a href={`/api/ga/runs/${encodeURIComponent(run.run_code)}/export.csv`}>Xuất CSV</a><a href={`/api/ga/runs/${encodeURIComponent(run.run_code)}/export.xlsx`}>Xuất Excel</a></div>
    </section>
    <section className="panel">
      <div className="toolbar result-toolbar">
        <input aria-label="Tìm kiếm" placeholder="Tìm lớp, môn, giảng viên hoặc phòng" value={search} onChange={(event) => setSearch(event.target.value)} />
        <label>Sắp xếp lớp theo<select aria-label="Sắp xếp lớp học" value={sort} onChange={(event) => setSort(event.target.value as ResultSort)}>
          <option value="day_time">Thứ và tiết học</option><option value="lecturer">Tên giảng viên</option><option value="section">Mã lớp học phần</option><option value="room">Mã phòng</option><option value="course_type">Loại lớp</option>
        </select></label>
        <label>Loại lớp<select aria-label="Lọc loại lớp" value={type} onChange={(event) => setType(event.target.value)}><option value="ALL">Tất cả loại lớp</option>{Object.entries(courseTypes).map(([key, label]) => <option value={key} key={key}>{label}</option>)}</select></label>
      </div>
      <p className="filter-summary" role="status">Hiển thị {sorted.length} trên {run.assignments.length} lớp học phần.</p>
      <AssignmentTable rows={sorted} />
    </section>
  </>;
}

function compareAssignments(first: Assignment, second: Assignment, sort: ResultSort) {
  const compareText = (left: string | undefined, right: string | undefined) => String(left || "").localeCompare(String(right || ""), "vi");
  const compareDayTime = () => Number(first.day_of_week) - Number(second.day_of_week)
    || Number(first.start_period) - Number(second.start_period)
    || compareText(first.section_code, second.section_code);
  if (sort === "lecturer") return compareText(first.lecturer_name || first.lecturer_code, second.lecturer_name || second.lecturer_code) || compareDayTime();
  if (sort === "section") return compareText(first.section_code, second.section_code) || compareDayTime();
  if (sort === "room") return compareText(first.room_code, second.room_code) || compareDayTime();
  if (sort === "course_type") return compareText(courseTypes[first.course_type], courseTypes[second.course_type]) || compareDayTime();
  return compareDayTime();
}

function AssignmentTable({ rows }: { rows: Assignment[] }) {
  if (!rows.length) return <Empty text="Không có lớp học phần phù hợp với bộ lọc." />;
  return <div className="table-wrap"><table><thead><tr><th>Lớp học phần</th><th>Giảng viên</th><th>Ngày / tiết</th><th>Phòng</th><th>Loại lớp</th></tr></thead><tbody>{rows.map((item) => <tr key={item.section_code}><td><strong>{item.section_code}</strong><small>{item.course_name}</small></td><td>{item.lecturer_name || item.lecturer_code}</td><td>{days[item.day_of_week] || item.day_of_week}<small>Tiết {item.start_period}–{item.end_period}</small></td><td>{item.room_code}</td><td><span className="pill">{courseTypes[item.course_type] || "Không xác định"}</span></td></tr>)}</tbody></table></div>;
}

function AdjustmentsPage({ official, onUpdate }: { official: OfficialTimetable | null; onUpdate: (official: OfficialTimetable) => void }) {
  const [search, setSearch] = useState("");
  const [week, setWeek] = useState("ALL");
  const [lecturer, setLecturer] = useState("ALL");
  const [room, setRoom] = useState("ALL");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [editing, setEditing] = useState<Occurrence | null>(null);
  const [options, setOptions] = useState<Awaited<ReturnType<typeof api.adjustmentOptions>>>([]);
  const [message, setMessage] = useState<string | null>(null);
  const run = official;
  const runCode = official?.official_code;

  useEffect(() => {
    setSearch("");
    setWeek("ALL");
    setLecturer("ALL");
    setRoom("ALL");
    setPage(1);
  }, [runCode]);

  const assignments = useMemo(() => new Map((run?.assignments || []).map((item) => [item.section_code, item])), [run]);
  const weeks = useMemo(() => [...new Set((run?.occurrences || []).map((item) => item.academic_week))].sort((first, second) => first - second), [run]);
  const lecturers = useMemo(() => {
    const values = new Map<string, string>();
    assignments.forEach((item) => { if (item.lecturer_code) values.set(item.lecturer_code, `${item.lecturer_name || item.lecturer_code} (${item.lecturer_code})`); });
    return [...values.entries()].sort(([, first], [, second]) => first.localeCompare(second, "vi"));
  }, [assignments]);
  const rooms = useMemo(() => [...new Set((run?.occurrences || []).map((item) => item.room_code))].sort((first, second) => first.localeCompare(second, "vi")), [run]);

  const filteredRows = useMemo(() => {
    const normalizedSearch = search.trim().toLocaleLowerCase("vi");
    return (run?.occurrences || []).filter((item) => {
      const assignment = assignments.get(item.section_code);
      const haystack = [item.section_code, item.room_code, assignment?.course_code, assignment?.course_name, assignment?.lecturer_name, assignment?.lecturer_code]
        .join(" ")
        .toLocaleLowerCase("vi");
      return (!normalizedSearch || haystack.includes(normalizedSearch))
        && (week === "ALL" || String(item.academic_week) === week)
        && (lecturer === "ALL" || assignment?.lecturer_code === lecturer)
        && (room === "ALL" || item.room_code === room);
    }).sort((first, second) => String(first.date).localeCompare(String(second.date))
      || String(first.section_code).localeCompare(String(second.section_code), "vi")
      || String(first.slot_code).localeCompare(String(second.slot_code), "vi"));
  }, [run, assignments, search, week, lecturer, room]);

  const pageCount = Math.max(1, Math.ceil(filteredRows.length / pageSize));
  const currentPageNumber = Math.min(page, pageCount);
  const currentRows = filteredRows.slice((currentPageNumber - 1) * pageSize, currentPageNumber * pageSize);
  const firstRow = filteredRows.length ? (currentPageNumber - 1) * pageSize + 1 : 0;
  const lastRow = filteredRows.length ? Math.min(currentPageNumber * pageSize, filteredRows.length) : 0;

  useEffect(() => { if (page > pageCount) setPage(pageCount); }, [page, pageCount]);

  const clearFilters = () => { setSearch(""); setWeek("ALL"); setLecturer("ALL"); setRoom("ALL"); setPage(1); };
  const open = async (item: Occurrence) => { if (!official) return; setMessage(null); try { setOptions(await api.adjustmentOptions(official.source_run_code, item.section_code, item.date)); setEditing(item); } catch (error) { setMessage(errorText(error)); } };

  if (!official) return <section className="panel"><Empty text="Hãy công bố một phương án GA thành lịch chính thức trước khi điều chỉnh." /></section>;
  return <section className="panel">
    <div className="panel-heading"><div><h2>Điều chỉnh lịch chính thức</h2><p>{official.official_code} · Phương án gốc {official.source_run_code} được giữ nguyên. Chọn phạm vi trước khi lưu thay đổi.</p></div><div className="export-links"><a href={`/api/ga/official-timetables/${encodeURIComponent(official.official_code)}/export.csv`}>Xuất CSV</a><a href={`/api/ga/official-timetables/${encodeURIComponent(official.official_code)}/export.xlsx`}>Xuất Excel</a></div></div>
    <OfficialScheduleTools official={official} onUpdate={onUpdate} onMessage={setMessage} />
    <div className="adjustment-filter-bar" aria-label="Tìm và lọc buổi học">
      <label className="adjustment-search">Tìm buổi học<input aria-label="Tìm buổi học" placeholder="Mã lớp, tên môn, giảng viên hoặc phòng" value={search} onChange={(event) => { setSearch(event.target.value); setPage(1); }} /></label>
      <label>Tuần học<select aria-label="Lọc theo tuần học" value={week} onChange={(event) => { setWeek(event.target.value); setPage(1); }}><option value="ALL">Tất cả các tuần</option>{weeks.map((value) => <option value={String(value)} key={value}>Tuần {value}</option>)}</select></label>
      <label>Giảng viên<select aria-label="Lọc theo giảng viên" value={lecturer} onChange={(event) => { setLecturer(event.target.value); setPage(1); }}><option value="ALL">Tất cả giảng viên</option>{lecturers.map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label>
      <label>Phòng<select aria-label="Lọc theo phòng" value={room} onChange={(event) => { setRoom(event.target.value); setPage(1); }}><option value="ALL">Tất cả phòng</option>{rooms.map((value) => <option value={value} key={value}>{value}</option>)}</select></label>
      <button className="secondary" type="button" onClick={clearFilters}>Xóa bộ lọc</button>
    </div>
    {message && <div className="alert success">{message}</div>}
    <div className="adjustment-list-summary"><span>Hiển thị {firstRow}-{lastRow} trên {filteredRows.length}/{official.occurrences.length} buổi học.</span><label>Hiển thị<select aria-label="Số buổi hiển thị mỗi trang" value={pageSize} onChange={(event) => { setPageSize(Number(event.target.value)); setPage(1); }}><option value={25}>25 buổi</option><option value={50}>50 buổi</option><option value={100}>100 buổi</option></select></label></div>
    <div className="table-wrap result-table"><table><thead><tr><th>Ngày</th><th>Lớp học phần</th><th>Môn học</th><th>Giảng viên</th><th>Tiết</th><th>Phòng</th><th>Thao tác</th></tr></thead><tbody>{currentRows.map((item) => { const assignment = assignments.get(item.section_code); const period = assignment && item.slot_code === assignment.slot_code ? `${assignment.start_period}–${assignment.end_period}` : item.slot_code; return <tr key={`${item.section_code}-${item.date}`}><td>{formatDate(item.date)}<small>Tuần {item.academic_week}</small></td><td><strong>{item.section_code}</strong></td><td>{assignment?.course_name || "—"}</td><td>{assignment?.lecturer_name || assignment?.lecturer_code || "—"}</td><td>{period}</td><td>{item.room_code}</td><td><button className="secondary" type="button" onClick={() => void open(item)}>Sửa buổi này</button></td></tr>; })}</tbody></table></div>
    {!currentRows.length && <Empty text="Không có buổi học phù hợp với bộ lọc." />}
    {pageCount > 1 && <div className="pagination-controls" aria-label="Phân trang buổi học"><button className="secondary" type="button" disabled={currentPageNumber === 1} onClick={() => setPage((value) => Math.max(1, value - 1))}>Trang trước</button><span>Trang {currentPageNumber}/{pageCount}</span><button className="secondary" type="button" disabled={currentPageNumber === pageCount} onClick={() => setPage((value) => Math.min(pageCount, value + 1))}>Trang sau</button></div>}
    {editing && <AdjustmentDialog official={official} occurrence={editing} options={options} onClose={() => setEditing(null)} onSaved={(next, note) => { onUpdate(next); setEditing(null); setMessage(note); }} />}
  </section>;
}

function AdjustmentDialog({ official, occurrence, options, onClose, onSaved }: { official: OfficialTimetable; occurrence: Occurrence; options: Awaited<ReturnType<typeof api.adjustmentOptions>>; onClose: () => void; onSaved: (official: OfficialTimetable, note: string) => void }) {
  const [slotCode, setSlotCode] = useState(occurrence.slot_code); const [roomCode, setRoomCode] = useState(occurrence.room_code); const [scope, setScope] = useState<AdjustmentScope>("ONE_OCCURRENCE"); const [endDate, setEndDate] = useState(occurrence.date); const [reason, setReason] = useState(""); const [busy, setBusy] = useState(false); const [error, setError] = useState<string | null>(null);
  const selected = options.find((slot) => slot.slot_code === slotCode) || options[0]; const rooms = selected?.rooms || [];
  useEffect(() => { if (selected && !rooms.some((room) => room.room_code === roomCode)) setRoomCode(rooms[0]?.room_code || ""); }, [selected, rooms, roomCode]);
  const submit = async (event: FormEvent) => { event.preventDefault(); if (!reason.trim()) { setError("Vui lòng nhập lý do điều chỉnh."); return; } setBusy(true); try { const body = { section_code: occurrence.section_code, occurrence_date: occurrence.date, slot_code: selected?.slot_code || "", room_code: roomCode, reason, scope, ...(scope === "DATE_RANGE" ? { effective_start_date: occurrence.date, effective_end_date: endDate } : scope === "FROM_DATE_TO_END" ? { effective_start_date: occurrence.date } : {}) }; const result = await api.adjustOfficial(official.official_code, body); onSaved(result.official, result.message); } catch (cause) { setError(errorText(cause)); } finally { setBusy(false); } };
  return <div className="modal-backdrop" role="presentation"><section className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><button className="close" onClick={onClose} aria-label="Đóng">×</button><p className="eyebrow">Điều chỉnh lịch chính thức</p><h2 id="modal-title">{occurrence.section_code} · {formatDate(occurrence.date)}</h2><form onSubmit={submit}><label>Phạm vi áp dụng<select value={scope} onChange={(event) => setScope(event.target.value as AdjustmentScope)}><option value="ONE_OCCURRENCE">Chỉ buổi học này</option><option value="DATE_RANGE">Từ buổi này đến ngày đã chọn</option><option value="FROM_DATE_TO_END">Từ buổi này đến hết học phần</option></select></label>{scope === "DATE_RANGE" && <label>Ngày kết thúc<input type="date" min={occurrence.date} value={endDate} onChange={(event) => setEndDate(event.target.value)} required /></label>}<label>Khung giờ<select value={selected?.slot_code || ""} onChange={(event) => setSlotCode(event.target.value)}>{options.map((slot) => <option key={slot.slot_code} value={slot.slot_code}>Tiết {slot.start_period}–{slot.end_period}</option>)}</select></label><label>Phòng học<select value={roomCode} onChange={(event) => setRoomCode(event.target.value)}>{rooms.map((room) => <option key={room.room_code} value={room.room_code}>{room.room_code} — {room.room_name} ({room.capacity} chỗ)</option>)}</select></label><label>Lý do điều chỉnh<textarea value={reason} onChange={(event) => setReason(event.target.value)} required /></label>{error && <div className="alert error">{error}</div>}<div className="modal-actions"><button type="button" className="secondary" onClick={onClose}>Hủy</button><button disabled={busy || !selected || !roomCode}>{busy ? "Đang lưu..." : "Lưu điều chỉnh"}</button></div></form></section></div>;
}

function OfficialScheduleTools({ official, onUpdate, onMessage }: { official: OfficialTimetable; onUpdate: (official: OfficialTimetable) => void; onMessage: (message: string) => void }) {
  const [error, setError] = useState<string | null>(null);
  const [missingKey, setMissingKey] = useState("");
  const [missingSearch, setMissingSearch] = useState("");
  const [missingLecturer, setMissingLecturer] = useState("ALL");
  const [missingPage, setMissingPage] = useState(1);
  const completedMissingDates = new Set((official.makeup_sessions || []).map((item) => `${item.section_code}|${item.original_missing_date || ""}`));
  const missingSessions = (official.skipped_holiday_sessions || []).filter((item) => !completedMissingDates.has(`${item.section_code}|${item.date}`));
  const lecturerOptions = [...new Map(missingSessions.map((item) => [item.lecturer_code || "", item.lecturer_name || item.lecturer_code || "Chưa rõ"])).entries()].filter(([code]) => code);
  const filteredMissing = missingSessions.filter((item) => {
    const query = missingSearch.trim().toLocaleLowerCase("vi");
    const haystack = [item.section_code, item.course_code, item.course_name, item.lecturer_code, item.lecturer_name, item.holiday_name].join(" ").toLocaleLowerCase("vi");
    return (!query || haystack.includes(query)) && (missingLecturer === "ALL" || item.lecturer_code === missingLecturer);
  });
  const missingPageSize = 10;
  const missingPageCount = Math.max(1, Math.ceil(filteredMissing.length / missingPageSize));
  const visibleMissing = filteredMissing.slice((missingPage - 1) * missingPageSize, missingPage * missingPageSize);
  const selectedMissing = missingSessions.find((item) => `${item.section_code}|${item.date}` === missingKey);
  const submit = async (event: FormEvent<HTMLFormElement>, kind: "segment" | "makeup") => {
    event.preventDefault();
    const values = Object.fromEntries(new FormData(event.currentTarget).entries()) as Record<string, string>;
    if (kind === "makeup" && values.missing_session) {
      const [sectionCode, originalDate] = values.missing_session.split("|");
      values.section_code = sectionCode; values.original_missing_date = originalDate; delete values.missing_session;
    }
    setError(null);
    try { const result = kind === "segment" ? await api.createSegment(official.official_code, values) : await api.createMakeup(official.official_code, values); onUpdate(result.official); onMessage(result.message); event.currentTarget.reset(); setMissingKey(""); } catch (cause) { setError(errorText(cause)); }
  };
  return <section className="schedule-tools"><div className="tool-intro"><h3>Quản lý ngoại lệ lịch</h3><p><strong>Phân đoạn lịch</strong> dùng khi một lớp đổi phòng hoặc khung giờ lặp lại trong một khoảng ngày; không tạo thêm buổi học. <strong>Buổi học bù</strong> là một buổi riêng để bù cho ngày nghỉ.</p></div>{missingSessions.length ? <div className="missing-sessions"><strong>Có {missingSessions.length} buổi cần bù do ngày nghỉ.</strong><span> Chọn chi tiết buổi thiếu trong biểu mẫu “Thêm buổi học bù”.</span></div> : <div className="missing-sessions complete"><strong>Không có buổi thiếu do ngày nghỉ trong lịch này.</strong></div>}<MissingSessionBrowser sessions={filteredMissing} visibleSessions={visibleMissing} selectedKey={missingKey} onSelect={setMissingKey} search={missingSearch} onSearch={(value) => { setMissingSearch(value); setMissingPage(1); }} lecturer={missingLecturer} onLecturer={(value) => { setMissingLecturer(value); setMissingPage(1); }} lecturerOptions={lecturerOptions} page={missingPage} pageCount={missingPageCount} onPage={setMissingPage} /><div className="tool-forms"><form className="tool-card" onSubmit={(event) => void submit(event, "segment")}><h3>Tạo phân đoạn lịch</h3><p>Ví dụ: chuyển phòng từ ngày 16/10 đến hết học kỳ.</p><label>Mã lớp học phần<input name="section_code" required /></label><div className="compact-grid"><label>Từ ngày<input name="effective_start_date" type="date" required /></label><label>Đến ngày<input name="effective_end_date" type="date" required /></label></div><div className="compact-grid"><label>Mã khung giờ<input name="slot_code" required /></label><label>Mã phòng<input name="room_code" required /></label></div><label>Lý do<textarea name="reason" required /></label><button>Tạo phân đoạn</button></form><form className="tool-card" onSubmit={(event) => void submit(event, "makeup")}><h3>Thêm buổi học bù</h3><p>Chọn một buổi thiếu để liên kết và theo dõi số buổi cần dạy.</p><label>Buổi thiếu do ngày nghỉ<select name="missing_session" value={missingKey} onChange={(event) => setMissingKey(event.target.value)} required><option value="">Chọn buổi cần bù</option>{missingSessions.map((item) => <option value={`${item.section_code}|${item.date}`} key={`${item.section_code}-${item.date}`}>{item.section_code} · {formatDate(item.date)}{item.holiday_name ? ` — ${item.holiday_name}` : ""}</option>)}</select></label><div className="compact-grid"><label>Ngày học bù<input name="makeup_date" type="date" required /></label><label>Mã khung giờ<input name="slot_code" required /></label></div><label>Mã phòng<input name="room_code" required /></label><label>Lý do<textarea name="reason" required /></label><button disabled={!missingSessions.length}>Thêm buổi bù</button></form></div>{error && <div className="alert error">{error}</div>}</section>;
}
function MissingSessionBrowser({ sessions, visibleSessions, selectedKey, onSelect, search, onSearch, lecturer, onLecturer, lecturerOptions, page, pageCount, onPage }: { sessions: NonNullable<OfficialTimetable["skipped_holiday_sessions"]>; visibleSessions: NonNullable<OfficialTimetable["skipped_holiday_sessions"]>; selectedKey: string; onSelect: (key: string) => void; search: string; onSearch: (value: string) => void; lecturer: string; onLecturer: (value: string) => void; lecturerOptions: [string, string][]; page: number; pageCount: number; onPage: (page: number) => void }) {
  return <div className="missing-session-browser" aria-label="Danh sách buổi thiếu"><div className="missing-session-filters"><label>Tìm buổi thiếu<input aria-label="Tìm buổi thiếu" value={search} onChange={(event) => onSearch(event.target.value)} placeholder="Mã lớp, môn hoặc giảng viên" /></label><label>Giảng viên<select aria-label="Lọc buổi thiếu theo giảng viên" value={lecturer} onChange={(event) => onLecturer(event.target.value)}><option value="ALL">Tất cả giảng viên</option>{lecturerOptions.map(([code, name]) => <option value={code} key={code}>{name} ({code})</option>)}</select></label></div><p className="filter-summary" role="status">Hiển thị {sessions.length ? ((page - 1) * 10 + 1) : 0}–{Math.min(page * 10, sessions.length)} trên {sessions.length} buổi thiếu.</p>{visibleSessions.length ? <div className="missing-session-table-wrap"><table className="missing-session-table"><thead><tr><th>Lớp / môn học</th><th>Giảng viên</th><th>Ngày thiếu</th><th>Lý do</th><th /></tr></thead><tbody>{visibleSessions.map((item) => { const key = `${item.section_code}|${item.date}`; return <tr className={key === selectedKey ? "selected" : ""} key={key}><td><strong>{item.section_code}</strong><small>{item.course_code ? `${item.course_code} · ` : ""}{item.course_name || "Chưa có tên môn"}</small></td><td>{item.lecturer_name || "Chưa rõ"}<small>{item.lecturer_code || ""}</small></td><td>{formatDate(item.date)}<small>Tuần {item.academic_week}</small></td><td>{item.holiday_name || "Ngày không dạy"}</td><td><button type="button" className="secondary" onClick={() => onSelect(key)}>{key === selectedKey ? "Đã chọn" : "Chọn buổi này"}</button></td></tr>; })}</tbody></table></div> : <p className="empty">Không có buổi thiếu phù hợp với bộ lọc.</p>}{pageCount > 1 && <div className="pagination-controls"><button type="button" className="secondary" disabled={page === 1} onClick={() => onPage(Math.max(1, page - 1))}>Trang trước</button><span>Trang {page}/{pageCount}</span><button type="button" className="secondary" disabled={page === pageCount} onClick={() => onPage(Math.min(pageCount, page + 1))}>Trang sau</button></div>}</div>;
}

function Empty({ text }: { text: string }) { return <p className="empty">{text}</p>; }


