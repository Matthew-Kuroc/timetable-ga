import { FormEvent, useEffect, useMemo, useState } from "react";
import { api } from "./api/client";
import type { Assignment, Batch, Occurrence, Preview, Run } from "./types";

type Page = "overview" | "import" | "ga" | "results" | "adjustments";
const requiredFiles = ["lecturers.csv", "rooms.csv", "time_slots.csv", "course_sections.csv", "lecturer_time_preferences.csv", "room_unavailable_slots.csv", "academic_calendar.csv"];
const pages: { key: Page; label: string; note: string }[] = [
  { key: "overview", label: "Tổng quan", note: "Theo dõi dữ liệu đầu vào và các phương án thời khóa biểu." },
  { key: "import", label: "Nhập dữ liệu CSV", note: "Tải đủ bảy tệp CSV để kiểm tra và xác nhận bộ dữ liệu." },
  { key: "ga", label: "Cấu hình và chạy GA", note: "Điều chỉnh tham số để tạo phương án thời khóa biểu." },
  { key: "results", label: "Kết quả thời khóa biểu", note: "Xem, lọc và xuất phương án đã tạo." },
  { key: "adjustments", label: "Chỉnh sửa lịch", note: "Điều chỉnh một buổi học sau khi hệ thống kiểm tra xung đột." },
];
const days: Record<number, string> = { 2: "Thứ Hai", 3: "Thứ Ba", 4: "Thứ Tư", 5: "Thứ Năm", 6: "Thứ Sáu", 7: "Thứ Bảy", 8: "Chủ nhật" };
const courseTypes: Record<string, string> = { THEORY: "Lý thuyết", PRACTICE: "Thực hành", INTEGRATED: "Lý thuyết – thực hành" };
const formatDate = (value?: string) => value ? new Intl.DateTimeFormat("vi-VN").format(new Date(`${value.slice(0, 10)}T00:00:00`)) : "—";
const formatDateTime = (value?: string) => value ? new Intl.DateTimeFormat("vi-VN", { dateStyle: "short", timeStyle: "short", timeZone: "Asia/Ho_Chi_Minh" }).format(new Date(value)) : "—";
const batchLabel = (batch: Batch) => [batch.display_name || batch.batch_code, batch.semester, batch.academic_year].filter(Boolean).join(" · ");
const errorText = (error: unknown) => error instanceof Error ? error.message : "Đã có lỗi không mong muốn.";

export function App() {
  const [page, setPage] = useState<Page>(() => (location.hash.slice(1) as Page) || "overview");
  const [apiOnline, setApiOnline] = useState(false);
  const [batches, setBatches] = useState<Batch[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [activeRun, setActiveRun] = useState<Run | null>(null);
  const [notice, setNotice] = useState<{ text: string; tone: "success" | "error" } | null>(null);

  const refresh = async () => {
    try { const [nextBatches, nextRuns] = await Promise.all([api.batches(), api.runs()]); setBatches(nextBatches); setRuns(nextRuns); setApiOnline(true); }
    catch { setApiOnline(false); }
  };
  useEffect(() => { void refresh(); }, []);
  useEffect(() => { const onHash = () => setPage((location.hash.slice(1) as Page) || "overview"); addEventListener("hashchange", onHash); return () => removeEventListener("hashchange", onHash); }, []);
  const navigate = (target: Page) => { location.hash = target; setPage(target); };
  const selectRun = async (runCode: string) => { try { setActiveRun(await api.run(runCode)); navigate("results"); } catch (error) { setNotice({ text: errorText(error), tone: "error" }); } };
  const activePage = pages.find((item) => item.key === page)!;

  return <div className="app-shell">
    <aside className="sidebar"><div className="brand"><span>TKB</span><div><strong>Timetable GA</strong><small>Phòng Đào tạo</small></div></div>
      <nav aria-label="Điều hướng chính">{pages.map((item) => <button className={page === item.key ? "active" : ""} key={item.key} onClick={() => navigate(item.key)}>{item.label}</button>)}</nav>
      <p className={`connection ${apiOnline ? "online" : ""}`}>{apiOnline ? "Đã kết nối hệ thống" : "Chưa kết nối máy chủ"}</p>
    </aside>
    <main><header><div><p className="eyebrow">Ứng dụng xếp lịch giảng dạy</p><h1>{activePage.label}</h1><p>{activePage.note}</p></div></header>
      {notice && <div className={`alert ${notice.tone}`} role="status">{notice.text}<button onClick={() => setNotice(null)} aria-label="Đóng thông báo">×</button></div>}
      {page === "overview" && <Overview runs={runs} batches={batches} onNavigate={navigate} onSelectRun={selectRun} />}
      {page === "import" && <ImportPage onConfirmed={async (batch) => { await refresh(); setNotice({ text: `Đã xác nhận bộ dữ liệu ${batch.batch_code}.`, tone: "success" }); navigate("ga"); }} />}
      {page === "ga" && <GaPage batches={batches} onRun={async (run) => { setActiveRun(run); await refresh(); navigate("results"); }} />}
      {page === "results" && <ResultsPage run={activeRun} runs={runs} onSelectRun={selectRun} />}
      {page === "adjustments" && <AdjustmentsPage run={activeRun} onUpdate={setActiveRun} />}
    </main>
  </div>;
}

function Overview({ runs, batches, onNavigate, onSelectRun }: { runs: Run[]; batches: Batch[]; onNavigate: (page: Page) => void; onSelectRun: (code: string) => void }) {
  return <><section className="hero"><div><p className="eyebrow">Sẵn sàng lập thời khóa biểu</p><h2>Quản lý dữ liệu, chạy thuật toán và điều chỉnh lịch tại một nơi.</h2><button onClick={() => onNavigate("ga")}>Chạy xếp lịch</button></div><div className="hero-art">GA</div></section>
    <section className="metrics"><Metric label="Bộ dữ liệu đã xác nhận" value={batches.length} /><Metric label="Lần chạy đã lưu" value={runs.length} /><Metric label="Lần chạy gần nhất" value={runs[0]?.status === "COMPLETED" ? "Hoàn thành" : runs[0]?.status || "Chưa có"} /></section>
    <section className="panel"><div className="panel-title"><div><h2>Lịch sử chạy thuật toán</h2><p>Chọn một phương án để xem lại kết quả đã lưu.</p></div></div><RunList runs={runs} onSelect={onSelectRun} /></section></>;
}
function Metric({ label, value }: { label: string; value: string | number }) { return <article className="metric"><span>{label}</span><strong>{value}</strong></article>; }
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

function ResultsPage({ run, runs, onSelectRun }: { run: Run | null; runs: Run[]; onSelectRun: (code: string) => void }) {
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
      <div className="export-links"><a href={`/api/ga/runs/${encodeURIComponent(run.run_code)}/export.csv`}>Xuất CSV</a><a href={`/api/ga/runs/${encodeURIComponent(run.run_code)}/export.xlsx`}>Xuất Excel</a></div>
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

function AdjustmentsPage({ run, onUpdate }: { run: Run | null; onUpdate: (run: Run) => void }) {
  const [search, setSearch] = useState("");
  const [week, setWeek] = useState("ALL");
  const [lecturer, setLecturer] = useState("ALL");
  const [room, setRoom] = useState("ALL");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [editing, setEditing] = useState<Occurrence | null>(null);
  const [options, setOptions] = useState<Awaited<ReturnType<typeof api.adjustmentOptions>>>([]);
  const [message, setMessage] = useState<string | null>(null);
  const runCode = run?.run_code;

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
  const open = async (item: Occurrence) => { if (!run) return; setMessage(null); try { setOptions(await api.adjustmentOptions(run.run_code, item.section_code, item.date)); setEditing(item); } catch (error) { setMessage(errorText(error)); } };

  if (!run) return <section className="panel"><Empty text="Hãy chọn một kết quả thời khóa biểu trước khi điều chỉnh." /></section>;
  return <section className="panel">
    <div className="panel-heading"><div><h2>Điều chỉnh một buổi học</h2><p>Tìm buổi học cần xử lý, sau đó thay đổi ngày, khung giờ hoặc phòng. Thay đổi chỉ áp dụng cho buổi được chọn.</p></div><div className="export-links"><a href={`/api/ga/runs/${encodeURIComponent(run.run_code)}/export.csv`}>Xuất CSV</a><a href={`/api/ga/runs/${encodeURIComponent(run.run_code)}/export.xlsx`}>Xuất Excel</a></div></div>
    <div className="adjustment-filter-bar" aria-label="Tìm và lọc buổi học">
      <label className="adjustment-search">Tìm buổi học<input aria-label="Tìm buổi học" placeholder="Mã lớp, tên môn, giảng viên hoặc phòng" value={search} onChange={(event) => { setSearch(event.target.value); setPage(1); }} /></label>
      <label>Tuần học<select aria-label="Lọc theo tuần học" value={week} onChange={(event) => { setWeek(event.target.value); setPage(1); }}><option value="ALL">Tất cả các tuần</option>{weeks.map((value) => <option value={String(value)} key={value}>Tuần {value}</option>)}</select></label>
      <label>Giảng viên<select aria-label="Lọc theo giảng viên" value={lecturer} onChange={(event) => { setLecturer(event.target.value); setPage(1); }}><option value="ALL">Tất cả giảng viên</option>{lecturers.map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label>
      <label>Phòng<select aria-label="Lọc theo phòng" value={room} onChange={(event) => { setRoom(event.target.value); setPage(1); }}><option value="ALL">Tất cả phòng</option>{rooms.map((value) => <option value={value} key={value}>{value}</option>)}</select></label>
      <button className="secondary" type="button" onClick={clearFilters}>Xóa bộ lọc</button>
    </div>
    {message && <div className="alert success">{message}</div>}
    <div className="adjustment-list-summary"><span>Hiển thị {firstRow}-{lastRow} trên {filteredRows.length}/{run.occurrences.length} buổi học.</span><label>Hiển thị<select aria-label="Số buổi hiển thị mỗi trang" value={pageSize} onChange={(event) => { setPageSize(Number(event.target.value)); setPage(1); }}><option value={25}>25 buổi</option><option value={50}>50 buổi</option><option value={100}>100 buổi</option></select></label></div>
    <div className="table-wrap result-table"><table><thead><tr><th>Ngày</th><th>Lớp học phần</th><th>Môn học</th><th>Giảng viên</th><th>Tiết</th><th>Phòng</th><th>Thao tác</th></tr></thead><tbody>{currentRows.map((item) => { const assignment = assignments.get(item.section_code); const period = assignment && item.slot_code === assignment.slot_code ? `${assignment.start_period}–${assignment.end_period}` : item.slot_code; return <tr key={`${item.section_code}-${item.date}`}><td>{formatDate(item.date)}<small>Tuần {item.academic_week}</small></td><td><strong>{item.section_code}</strong></td><td>{assignment?.course_name || "—"}</td><td>{assignment?.lecturer_name || assignment?.lecturer_code || "—"}</td><td>{period}</td><td>{item.room_code}</td><td><button className="secondary" type="button" onClick={() => void open(item)}>Sửa buổi này</button></td></tr>; })}</tbody></table></div>
    {!currentRows.length && <Empty text="Không có buổi học phù hợp với bộ lọc." />}
    {pageCount > 1 && <div className="pagination-controls" aria-label="Phân trang buổi học"><button className="secondary" type="button" disabled={currentPageNumber === 1} onClick={() => setPage((value) => Math.max(1, value - 1))}>Trang trước</button><span>Trang {currentPageNumber}/{pageCount}</span><button className="secondary" type="button" disabled={currentPageNumber === pageCount} onClick={() => setPage((value) => Math.min(pageCount, value + 1))}>Trang sau</button></div>}
    {editing && <AdjustmentDialog run={run} occurrence={editing} options={options} onClose={() => setEditing(null)} onSaved={(next, note) => { onUpdate(next); setEditing(null); setMessage(note); }} />}
  </section>;
}

function AdjustmentDialog({ run, occurrence, options, onClose, onSaved }: { run: Run; occurrence: Occurrence; options: Awaited<ReturnType<typeof api.adjustmentOptions>>; onClose: () => void; onSaved: (run: Run, note: string) => void }) {
  const [slotCode, setSlotCode] = useState(occurrence.slot_code); const [roomCode, setRoomCode] = useState(occurrence.room_code); const [date, setDate] = useState(occurrence.date); const [reason, setReason] = useState(""); const [busy, setBusy] = useState(false); const [error, setError] = useState<string | null>(null);
  const selected = options.find((slot) => slot.slot_code === slotCode) || options[0]; const rooms = selected?.rooms || [];
  useEffect(() => { if (selected && !rooms.some((room) => room.room_code === roomCode)) setRoomCode(rooms[0]?.room_code || ""); }, [selected, rooms, roomCode]);
  const submit = async (event: FormEvent) => { event.preventDefault(); if (!reason.trim()) { setError("Vui lòng nhập lý do điều chỉnh."); return; } setBusy(true); try { const result = await api.adjustOccurrence(run.run_code, { section_code: occurrence.section_code, occurrence_date: occurrence.date, new_date: date, slot_code: selected?.slot_code || "", room_code: roomCode, reason }); onSaved(result.run, result.message); } catch (cause) { setError(errorText(cause)); } finally { setBusy(false); } };
  return <div className="modal-backdrop" role="presentation"><section className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><button className="close" onClick={onClose} aria-label="Đóng">×</button><p className="eyebrow">Điều chỉnh một buổi học</p><h2 id="modal-title">{occurrence.section_code} · {formatDate(occurrence.date)}</h2><form onSubmit={submit}><label>Ngày học mới<input type="date" value={date} onChange={(event) => setDate(event.target.value)} required /></label><label>Khung giờ<select value={selected?.slot_code || ""} onChange={(event) => setSlotCode(event.target.value)}>{options.map((slot) => <option key={slot.slot_code} value={slot.slot_code}>Tiết {slot.start_period}–{slot.end_period}</option>)}</select></label><label>Phòng học<select value={roomCode} onChange={(event) => setRoomCode(event.target.value)}>{rooms.map((room) => <option key={room.room_code} value={room.room_code}>{room.room_code} — {room.room_name} ({room.capacity} chỗ)</option>)}</select></label><label>Lý do điều chỉnh<textarea value={reason} onChange={(event) => setReason(event.target.value)} required /></label>{error && <div className="alert error">{error}</div>}<div className="modal-actions"><button type="button" className="secondary" onClick={onClose}>Hủy</button><button disabled={busy || !selected || !roomCode}>{busy ? "Đang lưu..." : "Lưu điều chỉnh"}</button></div></form></section></div>;
}
function Empty({ text }: { text: string }) { return <p className="empty">{text}</p>; }
