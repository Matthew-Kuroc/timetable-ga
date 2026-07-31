const requiredFiles = [
  "lecturers.csv",
  "rooms.csv",
  "time_slots.csv",
  "course_sections.csv",
  "lecturer_time_preferences.csv",
  "room_unavailable_slots.csv",
  "academic_calendar.csv",
];

const pageMeta = {
  overview: {
    title: "Tổng quan",
    subtitle: "Theo dõi dữ liệu đầu vào, cấu hình thuật toán và xem kết quả thời khóa biểu.",
  },
  import: {
    title: "Nhập dữ liệu CSV",
    subtitle: "Tải đủ 7 file CSV để kiểm tra dữ liệu trước khi xếp lịch.",
  },
  editor: {
    title: "Chỉnh sửa dữ liệu mẫu",
    subtitle: "Cập nhật nhanh dữ liệu mẫu đang sử dụng để kiểm tra hệ thống.",
  },
  ga: {
    title: "Cấu hình và chạy GA",
    subtitle: "Điều chỉnh tham số và tạo phương án thời khóa biểu.",
  },
  results: {
    title: "Kết quả thời khóa biểu",
    subtitle: "Xem phương án lịch được sinh bởi GA và lọc theo thông tin nghiệp vụ.",
  },
  adjustments: {
    title: "Chỉnh sửa lịch",
    subtitle: "Chọn một buổi học, thay đổi ngày, khung giờ hoặc phòng rồi lưu sau khi kiểm tra xung đột.",
  },
};

const dayLabels = {
  2: "Thứ Hai",
  3: "Thứ Ba",
  4: "Thứ Tư",
  5: "Thứ Năm",
  6: "Thứ Sáu",
  7: "Thứ Bảy",
  8: "Chủ nhật",
};

const dayPrefixes = {
  2: "MON",
  3: "TUE",
  4: "WED",
  5: "THU",
  6: "FRI",
  7: "SAT",
  8: "SUN",
};

const courseTypeLabels = {
  THEORY: "Lý thuyết",
  PRACTICE: "Thực hành",
  INTEGRATED: "Lý thuyết - thực hành",
};

const softLabels = {
  lecturer_preferences: "Nguyện vọng giảng viên",
  room_capacity_waste: "Độ dư sức chứa phòng",
  large_room_small_class: "Phòng lớn cho lớp nhỏ",
  schedule_gaps: "Khoảng trống trong ngày",
  scattered_days: "Số ngày dạy phân tán",
  consecutive_sessions: "Số ca liên tiếp",
  evening_weekend_avoidance: "Hạn chế ca tối và cuối tuần",
};

const editorColumnLabels = {
  lecturer_code: "Mã giảng viên", lecturer_name: "Họ và tên giảng viên",
  preferred_days: "Ngày mong muốn", preferred_slots: "Khung giờ mong muốn",
  undesired_days: "Ngày không mong muốn", undesired_slots: "Khung giờ không mong muốn",
  max_days_per_week: "Số ngày dạy tối đa/tuần", max_consecutive_sessions: "Số ca liên tiếp tối đa",
  room_code: "Mã phòng", room_name: "Tên phòng", capacity: "Sức chứa", room_type: "Loại phòng",
  room_size_category: "Quy mô phòng", available: "Đang khả dụng", slot_code: "Mã khung giờ",
  day_of_week: "Thứ trong tuần", start_period: "Tiết bắt đầu", end_period: "Tiết kết thúc",
  session_type: "Buổi học", supports_course_types: "Dùng cho loại lớp", active: "Đang sử dụng",
  course_code: "Mã môn học", course_name: "Tên môn học", section_code: "Mã lớp học phần",
  required_sessions: "Số buổi cần học", weekly_sessions: "Số buổi/tuần", periods_per_session: "Số tiết/buổi",
  expected_students: "Sĩ số dự kiến", initial_registration_limit: "Sĩ số đăng ký ban đầu",
  approved_max_students: "Sĩ số tối đa đã duyệt", scheduling_student_count: "Sĩ số dùng để xếp lịch",
  course_type: "Loại lớp", required_room_type: "Loại phòng yêu cầu", start_date: "Ngày bắt đầu",
  end_date: "Ngày kết thúc", campus_code: "Mã cơ sở", notes: "Ghi chú", mandatory: "Ràng buộc bắt buộc",
  reason: "Lý do", date: "Ngày", academic_week: "Tuần học kỳ", is_teaching_day: "Là ngày dạy",
  is_holiday: "Là ngày nghỉ", holiday_name: "Tên ngày nghỉ", note: "Ghi chú",
};

let latestAssignments = [];
let latestRun = null;
let currentBatchCode = null;
let resultViewState = {
  view: "list",
  sort: "day_time",
  courseType: "ALL",
};
let editorState = {
  file: null,
  headers: [],
  rows: [],
};
let editorReferences = {
  lecturers: [],
  rooms: [],
  slots: [],
};
let multiPickerState = {
  rowIndex: null,
  header: null,
  selectedValues: new Set(),
  trigger: null,
};

const pageTitle = document.getElementById("pageTitle");
const pageSubtitle = document.getElementById("pageSubtitle");
const apiStatus = document.getElementById("apiStatus");
const apiStatusText = document.getElementById("apiStatusText");
const previewTable = document.getElementById("previewTable");
const validationErrors = document.getElementById("validationErrors");
const csvForm = document.getElementById("csvForm");
const gaForm = document.getElementById("gaForm");
const resultTable = document.getElementById("resultTable");
const resultFilter = document.getElementById("resultFilter");
const resultSort = document.getElementById("resultSort");
const resultCourseType = document.getElementById("resultCourseType");
const resultTableWrap = document.getElementById("resultTableWrap");
const resultAlternateView = document.getElementById("resultAlternateView");
const runMessages = document.getElementById("runMessages");
const confirmImportButton = document.getElementById("confirmImportButton");
const confirmedBatchLabel = document.getElementById("confirmedBatchLabel");
const gaBatchCode = document.getElementById("gaBatchCode");
const adjustmentDialog = document.getElementById("adjustmentDialog");
const adjustmentForm = document.getElementById("adjustmentForm");
let adjustmentTarget = null;
let adjustmentSlots = [];
const occurrenceTable = document.getElementById("occurrenceTable");
const adjustmentViewState = { search: "", week: "ALL", lecturer: "ALL", room: "ALL", page: 1, pageSize: 25 };

initialiseNavigation();
initialiseRequiredFiles();
initialiseEditor();
checkApi();
loadBatches();
loadRunHistory();

document.getElementById("csvFiles").addEventListener("change", () => {
  const selectedNames = Array.from(document.getElementById("csvFiles").files || []).map((file) => file.name);
  renderRequiredFileChecklist(selectedNames);
});

document.getElementById("refreshEditorFilesButton").addEventListener("click", loadEditorFileList);
document.getElementById("addEditorRowButton").addEventListener("click", addEditorRow);
document.getElementById("saveEditorFileButton").addEventListener("click", saveEditorFile);
initialiseMultiPicker();
initialiseAdjustmentDialog();
initialiseAdjustmentFilters();

csvForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("csvFiles");
  const files = Array.from(input.files || []);
  if (!files.length) {
    showValidationErrors([{ reason: "Vui lòng chọn đủ 7 file CSV trước khi kiểm tra." }]);
    return;
  }

  const selectedNames = files.map((file) => file.name);
  const missing = requiredFiles.filter((fileName) => !selectedNames.includes(fileName));
  if (missing.length) {
    showValidationErrors([{ reason: `Thiếu file: ${missing.join(", ")}` }]);
    return;
  }

  const formData = new FormData();
  files.forEach((file) => formData.append("files", file, file.name));
  setPreviewMessage("Đang tải lên và kiểm tra CSV...");

  try {
    const response = await fetch("/api/imports/csv/preview", {
      method: "POST",
      body: formData,
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail?.message || "Không thể kiểm tra CSV.");
    }
    renderPreview(payload);
    confirmImportButton.disabled = !payload.valid;
  } catch (error) {
    showValidationErrors([{ reason: error.message }]);
  }
});

confirmImportButton.addEventListener("click", async () => {
  const files = Array.from(document.getElementById("csvFiles").files || []);
  if (!files.length) return;
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file, file.name));
  confirmImportButton.disabled = true;
  try {
    const response = await fetch("/api/imports/csv/confirm", { method: "POST", body: formData });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail?.message || "Không thể xác nhận bộ dữ liệu.");
    currentBatchCode = payload.batch.batch_code;
    confirmedBatchLabel.textContent = `Đã xác nhận: ${currentBatchCode}`;
    await loadBatches();
    await loadEditorFileList();
  } catch (error) {
    showValidationErrors([{ reason: error.message }]);
  } finally {
    confirmImportButton.disabled = false;
  }
});

gaForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = gaForm.querySelector("button[type='submit']");
  submitButton.disabled = true;
  submitButton.textContent = "Đang chạy...";
  runMessages.textContent = "Hệ thống đang kiểm tra dữ liệu và tạo phương án thời khóa biểu.";

  const formData = new FormData(gaForm);
  const payload = {
    batch_code: String(formData.get("batch_code") || ""),
    population_size: Number(formData.get("population_size")),
    generations: Number(formData.get("generations")),
    seed: Number(formData.get("seed")),
    crossover_rate: Number(formData.get("crossover_rate")),
    mutation_rate: Number(formData.get("mutation_rate")),
    elite_count: Number(formData.get("elite_count")),
    tournament_size: Number(formData.get("tournament_size")),
  };

  try {
    const response = await fetch("/api/ga/runs/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.detail?.diagnostics?.join("; ") || "Không thể chạy GA.");
    }
    if (result.status === "FAILED") {
      showValidationErrors(result.errors || [{ reason: "Dữ liệu đầu vào không hợp lệ." }]);
      runMessages.textContent = "Lần chạy thất bại. Vui lòng kiểm tra trang Nhập dữ liệu CSV.";
      navigateTo("import");
      return;
    }
    renderRunResult(result);
    configureRunExports(result.run_code);
    await loadRunHistory();
    navigateTo("results");
  } catch (error) {
    runMessages.textContent = error.message;
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Chạy thuật toán";
  }
});

resultFilter.addEventListener("input", () => renderAssignments(latestAssignments));
resultSort.addEventListener("change", () => {
  resultViewState.sort = resultSort.value;
  renderAssignments(latestAssignments);
});
resultCourseType.addEventListener("change", () => {
  resultViewState.courseType = resultCourseType.value;
  renderAssignments(latestAssignments);
});
document.querySelectorAll("[data-result-view]").forEach((button) => {
  button.addEventListener("click", () => {
    resultViewState.view = button.dataset.resultView;
    document.querySelectorAll("[data-result-view]").forEach((item) => {
      const isActive = item === button;
      item.classList.toggle("active", isActive);
      item.setAttribute("aria-selected", String(isActive));
    });
    renderAssignments(latestAssignments);
  });
});

occurrenceTable.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-adjust-occurrence]");
  if (!button || !latestRun?.run_code) return;
  const occurrence = (latestRun.occurrences || []).find((item) => item.section_code === button.dataset.adjustOccurrence && item.date === button.dataset.occurrenceDate);
  if (occurrence) await openOccurrenceAdjustmentDialog(occurrence);
});

function initialiseAdjustmentDialog() {
  document.getElementById("closeAdjustmentButton").addEventListener("click", () => adjustmentDialog.close());
  document.getElementById("cancelAdjustmentButton").addEventListener("click", () => adjustmentDialog.close());
  adjustmentForm.addEventListener("submit", submitAdjustment);
  document.getElementById("adjustmentSlot").addEventListener("change", () => renderAvailableRooms());
  document.getElementById("adjustmentDate").addEventListener("change", () => adjustmentTarget && loadOccurrenceOptions(adjustmentTarget));
}

async function openOccurrenceAdjustmentDialog(occurrence) {
  adjustmentTarget = occurrence;
  document.getElementById("adjustmentDate").value = occurrence.date;
  document.getElementById("adjustmentReason").value = "";
  document.getElementById("adjustmentDescription").textContent = `Buổi ${occurrence.section_code} ngày ${formatDate(occurrence.date)}. Lịch hiện tại: tiết ${slotLabel(occurrence.slot_code)}, phòng ${occurrence.room_code}.`;
  await loadOccurrenceOptions(occurrence);
  document.getElementById("adjustmentMessage").innerHTML = "";
  adjustmentDialog.showModal();
}

async function loadOccurrenceOptions(occurrence) {
  const selectedDate = document.getElementById("adjustmentDate").value;
  const response = await fetch(`/api/ga/runs/${encodeURIComponent(latestRun.run_code)}/occurrence-adjustment-options/${encodeURIComponent(occurrence.section_code)}/${encodeURIComponent(occurrence.date)}?target_date=${encodeURIComponent(selectedDate)}`);
  const options = await response.json();
  if (!response.ok) throw new Error(options.detail || "Không tải được lựa chọn điều chỉnh.");
  adjustmentSlots = options.slots || [];
  document.getElementById("adjustmentSlot").innerHTML = adjustmentSlots.map((slot) => `<option value="${escapeHtml(slot.slot_code)}" ${slot.slot_code === occurrence.slot_code ? "selected" : ""}>Tiết ${slot.start_period}-${slot.end_period}</option>`).join("");
  renderAvailableRooms(occurrence.room_code);
}

function renderAvailableRooms(preferredRoomCode = "") {
  const selectedSlot = adjustmentSlots.find((slot) => slot.slot_code === document.getElementById("adjustmentSlot").value);
  const rooms = selectedSlot?.rooms || [];
  const roomSelect = document.getElementById("adjustmentRoom");
  const currentRoom = preferredRoomCode || roomSelect.value;
  roomSelect.innerHTML = rooms.map((room) => `<option value="${escapeHtml(room.room_code)}" ${room.room_code === currentRoom ? "selected" : ""}>${escapeHtml(room.room_code)} - ${escapeHtml(room.room_name)} (${room.capacity} chỗ)</option>`).join("");
}

async function submitAdjustment(event) {
  event.preventDefault();
  if (!adjustmentTarget || !latestRun?.run_code) return;
  const button = document.getElementById("applyAdjustmentButton");
  button.disabled = true;
  try {
    const response = await fetch(`/api/ga/runs/${encodeURIComponent(latestRun.run_code)}/occurrences`, {
      method: "PUT", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ section_code: adjustmentTarget.section_code, occurrence_date: adjustmentTarget.date, new_date: document.getElementById("adjustmentDate").value, room_code: document.getElementById("adjustmentRoom").value, slot_code: document.getElementById("adjustmentSlot").value, reason: document.getElementById("adjustmentReason").value }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Không thể điều chỉnh lịch.");
    latestRun = payload.run;
    latestAssignments = payload.run.assignments;
    renderAssignments(latestAssignments);
    renderOccurrences();
    adjustmentDialog.close();
  } catch (error) {
    document.getElementById("adjustmentMessage").innerHTML = `<div class="message">${escapeHtml(error.message)}</div>`;
  } finally { button.disabled = false; }
}

function renderOccurrences() {
  if (!latestRun?.occurrences?.length) {
    occurrenceTable.innerHTML = '<tr><td colspan="7">Chưa có kết quả để chỉnh sửa.</td></tr>';
    document.getElementById("adjustmentListSummary").textContent = "Chưa có kết quả để chỉnh sửa.";
    document.getElementById("adjustmentPagination").hidden = true;
    renderAdjustmentHistory();
    return;
  }
  populateAdjustmentFilters();
  const assignments = new Map((latestRun.assignments || []).map((item) => [item.section_code, item]));
  const normalizedSearch = adjustmentViewState.search.trim().toLocaleLowerCase("vi");
  const filtered = latestRun.occurrences.filter((occurrence) => {
    const assignment = assignments.get(occurrence.section_code) || {};
    const haystack = [occurrence.section_code, occurrence.room_code, assignment.course_name, assignment.lecturer_name, assignment.lecturer_code].join(" ").toLocaleLowerCase("vi");
    return (!normalizedSearch || haystack.includes(normalizedSearch))
      && (adjustmentViewState.week === "ALL" || String(occurrence.academic_week) === adjustmentViewState.week)
      && (adjustmentViewState.lecturer === "ALL" || assignment.lecturer_code === adjustmentViewState.lecturer)
      && (adjustmentViewState.room === "ALL" || occurrence.room_code === adjustmentViewState.room);
  }).sort((first, second) => String(first.date).localeCompare(String(second.date)) || String(first.section_code).localeCompare(String(second.section_code)));
  const pageCount = Math.max(1, Math.ceil(filtered.length / adjustmentViewState.pageSize));
  adjustmentViewState.page = Math.min(adjustmentViewState.page, pageCount);
  const start = (adjustmentViewState.page - 1) * adjustmentViewState.pageSize;
  const currentPage = filtered.slice(start, start + adjustmentViewState.pageSize);
  occurrenceTable.innerHTML = currentPage.map((occurrence) => {
    const assignment = assignments.get(occurrence.section_code) || {};
    const slot = slotLabel(occurrence.slot_code);
    return `<tr><td>${formatDate(occurrence.date)}</td><td><strong>${escapeHtml(occurrence.section_code)}</strong></td><td>${escapeHtml(assignment.course_name || "")}</td><td>${escapeHtml(assignment.lecturer_name || assignment.lecturer_code || "")}</td><td>${escapeHtml(slot)}</td><td>${escapeHtml(occurrence.room_code)}</td><td><button class="secondary-button" type="button" data-adjust-occurrence="${escapeHtml(occurrence.section_code)}" data-occurrence-date="${escapeHtml(occurrence.date)}">Sửa buổi này</button></td></tr>`;
  }).join("") || '<tr><td colspan="7">Không có buổi học phù hợp với bộ lọc.</td></tr>';
  document.getElementById("adjustmentListSummary").textContent = `Hiển thị ${filtered.length ? start + 1 : 0}-${Math.min(start + adjustmentViewState.pageSize, filtered.length)} trên ${filtered.length}/${latestRun.occurrences.length} buổi học.`;
  document.getElementById("adjustmentPagination").hidden = filtered.length <= adjustmentViewState.pageSize;
  document.getElementById("adjustmentPageInfo").textContent = `Trang ${adjustmentViewState.page}/${pageCount}`;
  document.getElementById("adjustmentPreviousPage").disabled = adjustmentViewState.page === 1;
  document.getElementById("adjustmentNextPage").disabled = adjustmentViewState.page === pageCount;
  renderAdjustmentHistory();
}

function initialiseAdjustmentFilters() {
  const resetPage = () => { adjustmentViewState.page = 1; renderOccurrences(); };
  document.getElementById("adjustmentSearch").addEventListener("input", (event) => { adjustmentViewState.search = event.target.value; resetPage(); });
  document.getElementById("adjustmentWeek").addEventListener("change", (event) => { adjustmentViewState.week = event.target.value; resetPage(); });
  document.getElementById("adjustmentLecturer").addEventListener("change", (event) => { adjustmentViewState.lecturer = event.target.value; resetPage(); });
  document.getElementById("adjustmentRoomFilter").addEventListener("change", (event) => { adjustmentViewState.room = event.target.value; resetPage(); });
  document.getElementById("adjustmentPageSize").addEventListener("change", (event) => { adjustmentViewState.pageSize = Number(event.target.value); resetPage(); });
  document.getElementById("clearAdjustmentFiltersButton").addEventListener("click", () => {
    Object.assign(adjustmentViewState, { search: "", week: "ALL", lecturer: "ALL", room: "ALL", page: 1 });
    ["adjustmentSearch", "adjustmentWeek", "adjustmentLecturer", "adjustmentRoomFilter"].forEach((id) => { document.getElementById(id).value = id === "adjustmentSearch" ? "" : "ALL"; });
    renderOccurrences();
  });
  document.getElementById("adjustmentPreviousPage").addEventListener("click", () => { adjustmentViewState.page -= 1; renderOccurrences(); });
  document.getElementById("adjustmentNextPage").addEventListener("click", () => { adjustmentViewState.page += 1; renderOccurrences(); });
}

function populateAdjustmentFilters() {
  const assignments = new Map((latestRun.assignments || []).map((item) => [item.section_code, item]));
  const updateOptions = (id, values, selected, label) => {
    const select = document.getElementById(id);
    const current = select.value || selected;
    select.innerHTML = `<option value="ALL">${label}</option>${values.map(([value, text]) => `<option value="${escapeHtml(value)}">${escapeHtml(text)}</option>`).join("")}`;
    select.value = [...select.options].some((option) => option.value === current) ? current : "ALL";
  };
  updateOptions("adjustmentWeek", [...new Set(latestRun.occurrences.map((item) => item.academic_week))].sort((a, b) => a - b).map((week) => [String(week), `Tuần ${week}`]), adjustmentViewState.week, "Tất cả các tuần");
  updateOptions("adjustmentLecturer", [...assignments.values()].map((item) => [item.lecturer_code, `${item.lecturer_name || item.lecturer_code} (${item.lecturer_code})`]).filter(([value], index, items) => items.findIndex(([other]) => other === value) === index).sort((a, b) => a[1].localeCompare(b[1], "vi")), adjustmentViewState.lecturer, "Tất cả giảng viên");
  updateOptions("adjustmentRoomFilter", [...new Set(latestRun.occurrences.map((item) => item.room_code))].sort().map((room) => [room, room]), adjustmentViewState.room, "Tất cả phòng");
}

function renderAdjustmentHistory() {
  const container = document.getElementById("adjustmentHistory");
  const history = latestRun?.change_history || [];
  if (!history.length) { container.innerHTML = '<p class="empty-day">Chưa có thay đổi nào.</p>'; return; }
  container.innerHTML = [...history].reverse().map((item) => `<article class="adjustment-history-item"><div><strong>${escapeHtml(item.section_code)}</strong><br><small>${formatRunTime(item.changed_at)}</small></div><div><strong>${formatDate(item.previous?.date)} · ${escapeHtml(item.previous?.room_code || "")}</strong> → <strong>${formatDate(item.current?.date)} · ${escapeHtml(item.current?.room_code || "")}</strong><br><small>${escapeHtml(item.reason || "Không có lý do")}</small></div><small>${escapeHtml(item.scope || "")}</small></article>`).join("");
}

function slotLabel(slotCode) {
  const occurrence = adjustmentSlots.find((slot) => slot.slot_code === slotCode);
  if (occurrence) return `${occurrence.start_period}-${occurrence.end_period}`;
  const assignment = (latestRun?.assignments || []).find((item) => item.slot_code === slotCode);
  return assignment ? `${assignment.start_period}-${assignment.end_period}` : slotCode;
}

function formatDate(value) {
  const [year, month, day] = String(value).split("-");
  return year && month && day ? `${day}/${month}/${year}` : value;
}

function initialiseNavigation() {
  document.querySelectorAll("[data-navigate]").forEach((button) => {
    button.addEventListener("click", () => navigateTo(button.dataset.navigate));
  });
  window.addEventListener("hashchange", () => navigateTo(getRouteFromHash()));
  navigateTo(getRouteFromHash());
}

function getRouteFromHash() {
  return (window.location.hash || "#overview").replace("#", "");
}

function navigateTo(route) {
  const selectedRoute = pageMeta[route] ? route : "overview";
  document.querySelectorAll(".page").forEach((page) => {
    page.classList.toggle("active", page.id === `page-${selectedRoute}`);
  });
  document.querySelectorAll("[data-route]").forEach((link) => {
    link.classList.toggle("active", link.dataset.route === selectedRoute);
  });
  pageTitle.textContent = pageMeta[selectedRoute].title;
  pageSubtitle.textContent = pageMeta[selectedRoute].subtitle;
  if (window.location.hash !== `#${selectedRoute}`) {
    window.location.hash = selectedRoute;
  }
}

function initialiseRequiredFiles() {
  renderRequiredFileChecklist([]);
}

function renderRequiredFileChecklist(selectedNames) {
  document.getElementById("requiredFiles").innerHTML = requiredFiles
    .map((fileName) => {
      const selected = selectedNames.includes(fileName);
      return `<span class="${selected ? "selected" : ""}">${selected ? "Đã chọn" : "Cần có"}: ${escapeHtml(fileName)}</span>`;
    })
    .join("");
}

function initialiseEditor() {
  loadEditorFileList();
}

async function checkApi() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) {
      throw new Error();
    }
    apiStatus.className = "connection-dot ok";
    apiStatusText.textContent = "Hệ thống sẵn sàng";
  } catch {
    apiStatus.className = "connection-dot error";
    apiStatusText.textContent = "Chưa thể kết nối hệ thống";
  }
}

function renderPreview(payload) {
  previewTable.innerHTML = payload.files.map((file) => `
    <tr>
      <td><strong>${escapeHtml(file.file)}</strong></td>
      <td>${file.row_count}</td>
      <td>${file.headers.map(escapeHtml).join(", ")}</td>
      <td>${payload.valid ? "Hợp lệ" : "Có lỗi"}</td>
    </tr>
  `).join("");
  showValidationErrors(payload.errors || []);
}

function setPreviewMessage(message) {
  previewTable.innerHTML = `<tr><td colspan="4">${escapeHtml(message)}</td></tr>`;
  validationErrors.innerHTML = "";
}

function showValidationErrors(errors) {
  if (!errors.length) {
    validationErrors.innerHTML = `<div class="message ok">Dữ liệu hợp lệ và có thể dùng để chạy xếp lịch.</div>`;
    return;
  }
  validationErrors.innerHTML = errors.map((error) => `
    <div class="message">
      ${error.file ? `<strong>${escapeHtml(error.file)}</strong> ` : ""}
      ${error.row ? `dòng ${error.row} ` : ""}
      ${error.column ? `cột ${escapeHtml(error.column)} ` : ""}
      ${escapeHtml(error.reason || "Dữ liệu không hợp lệ.")}
    </div>
  `).join("");
}

function renderRunResult(result) {
  latestRun = result;
  latestAssignments = result.assignments || [];
  Object.assign(adjustmentViewState, { search: "", week: "ALL", lecturer: "ALL", room: "ALL", page: 1 });
  const evaluation = result.evaluation;
  document.getElementById("overviewRunState").innerHTML = `
    <strong>Đã chạy xong với ${latestAssignments.length} lớp học phần.</strong>
    <p>Ràng buộc cứng: ${evaluation.hard_violation_count}. Điểm mềm: ${Number(evaluation.soft_cost).toFixed(2)}.</p>
  `;
  document.getElementById("runSummary").textContent =
    `Đã hoàn thành sau ${result.generation_count} thế hệ tìm kiếm.`;
  document.getElementById("hardCount").textContent = evaluation.hard_violation_count;
  document.getElementById("softCost").textContent = Number(evaluation.soft_cost).toFixed(2);
  document.getElementById("generationCount").textContent = result.generation_count;
  document.getElementById("runtime").textContent = `${Number(result.execution_time_seconds).toFixed(2)}s`;
  document.getElementById("softBreakdown").innerHTML = Object.entries(evaluation.soft_breakdown || {})
    .map(([key, value]) => `<span>${escapeHtml(softLabels[key] || key)}: ${Number(value).toFixed(2)}</span>`)
    .join("");
  runMessages.textContent = "Chạy thuật toán thành công. Kết quả đã được hiển thị ở trang Kết quả thời khóa biểu.";
  renderAssignments(latestAssignments);
  renderOccurrences();
  configureAdjustmentExports(result.run_code);
}

function configureRunExports(runCode) {
  const exportButton = document.getElementById("exportCsvButton");
  const exportXlsxButton = document.getElementById("exportXlsxButton");
  if (!runCode) {
    exportButton.hidden = true;
    exportXlsxButton.hidden = true;
    return;
  }
  exportButton.href = `/api/ga/runs/${encodeURIComponent(runCode)}/export.csv`;
  exportButton.hidden = false;
  exportXlsxButton.href = `/api/ga/runs/${encodeURIComponent(runCode)}/export.xlsx`;
  exportXlsxButton.hidden = false;
}

function configureAdjustmentExports(runCode) {
  const csvButton = document.getElementById("adjustmentExportCsvButton");
  const xlsxButton = document.getElementById("adjustmentExportXlsxButton");
  if (!runCode) { csvButton.hidden = true; xlsxButton.hidden = true; return; }
  csvButton.href = `/api/ga/runs/${encodeURIComponent(runCode)}/export.csv`;
  xlsxButton.href = `/api/ga/runs/${encodeURIComponent(runCode)}/export.xlsx`;
  csvButton.hidden = false;
  xlsxButton.hidden = false;
}

async function loadRunHistory() {
  const container = document.getElementById("runHistory");
  try {
    const response = await fetch("/api/ga/runs?limit=10");
    const payload = await response.json();
    if (!response.ok) throw new Error();
    const runs = payload.runs || [];
    if (!runs.length) {
      container.innerHTML = '<p class="empty-day">Chưa có lịch sử chạy.</p>';
      return;
    }
    container.innerHTML = runs.map((run) => `
      <article class="run-history-item">
        <div>
          <strong>${escapeHtml(run.run_code)}</strong>
          <span>${escapeHtml(run.batch_code || "Chưa xác định bộ dữ liệu")} · ${Number(run.assignment_count || 0)} lớp</span>
          <small>${formatRunTime(run.created_at)} · ${Number(run.generation_count || 0)} thế hệ · điểm mềm ${Number(run.soft_cost || 0).toFixed(2)}</small>
        </div>
        <button class="secondary-button" type="button" data-load-run="${escapeHtml(run.run_code)}">Xem</button>
      </article>
    `).join("");
  } catch {
    container.innerHTML = '<p class="empty-day">Không tải được lịch sử chạy.</p>';
  }
}

function formatRunTime(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Không rõ thời gian" : date.toLocaleString("vi-VN");
}

document.getElementById("runHistory").addEventListener("click", async (event) => {
  const button = event.target.closest("[data-load-run]");
  if (!button) return;
  button.disabled = true;
  try {
    const response = await fetch(`/api/ga/runs/${encodeURIComponent(button.dataset.loadRun)}`);
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || "Không tải được kết quả đã chạy.");
    renderRunResult(result);
    configureRunExports(result.run_code);
    navigateTo("results");
  } catch (error) {
    window.alert(error.message);
  } finally {
    button.disabled = false;
  }
});

function renderAssignments(assignments) {
  const keyword = resultFilter.value.trim().toLowerCase();
  const searched = keyword
    ? assignments.filter((assignment) => [
        assignment.section_code,
        assignment.course_name,
        assignment.lecturer_code,
        assignment.lecturer_name,
        assignment.room_code,
      ].some((value) => String(value).toLowerCase().includes(keyword)))
    : assignments;
  const filtered = resultViewState.courseType === "ALL"
    ? searched
    : searched.filter((assignment) => assignment.course_type === resultViewState.courseType);
  const sorted = [...filtered].sort(compareAssignments);

  if (!sorted.length) {
    resultTableWrap.hidden = false;
    resultAlternateView.hidden = true;
    resultTable.innerHTML = `<tr><td colspan="9">Không có kết quả phù hợp.</td></tr>`;
    return;
  }

  if (resultViewState.view === "list") {
    resultTableWrap.hidden = false;
    resultAlternateView.hidden = true;
    resultTable.innerHTML = sorted.map(renderAssignmentRow).join("");
    return;
  }

  resultTableWrap.hidden = true;
  resultAlternateView.hidden = false;
  resultAlternateView.innerHTML = resultViewState.view === "week"
    ? renderWeeklyBoard(sorted)
    : renderGroupedAssignments(sorted, resultViewState.view);
}

function compareAssignments(first, second) {
  const compareText = (left, right) => String(left || "").localeCompare(String(right || ""), "vi");
  const compareDayTime = () => Number(first.day_of_week) - Number(second.day_of_week)
    || Number(first.start_period) - Number(second.start_period)
    || compareText(first.section_code, second.section_code);
  const comparisons = {
    day_time: compareDayTime,
    lecturer: () => compareText(first.lecturer_name || first.lecturer_code, second.lecturer_name || second.lecturer_code) || compareDayTime(),
    section: () => compareText(first.section_code, second.section_code),
    room: () => compareText(first.room_code, second.room_code) || compareDayTime(),
    course_type: () => compareText(courseTypeLabels[first.course_type], courseTypeLabels[second.course_type]) || compareDayTime(),
  };
  return (comparisons[resultViewState.sort] || compareDayTime)();
}

function renderAssignmentRow(assignment) {
  return `
    <tr>
      <td><strong>${escapeHtml(assignment.section_code)}</strong></td>
      <td>${escapeHtml(assignment.course_name)}</td>
      <td>${escapeHtml(assignment.lecturer_name || assignment.lecturer_code)}<br><small>${escapeHtml(assignment.lecturer_code)}</small></td>
      <td>${dayLabels[assignment.day_of_week] || assignment.day_of_week}</td>
      <td>Tiết ${assignment.start_period}-${assignment.end_period}</td>
      <td>${escapeHtml(assignment.room_code)}</td>
      <td>${courseTypeLabels[assignment.course_type] || escapeHtml(assignment.course_type)}</td>
      <td>${assignment.scheduling_student_count}</td>
    </tr>
  `;
}

function renderGroupedAssignments(assignments, groupBy) {
  const groupKey = groupBy === "lecturer"
    ? (assignment) => assignment.lecturer_name || assignment.lecturer_code
    : groupBy === "room"
      ? (assignment) => assignment.room_code
      : (assignment) => `${assignment.course_name} (${assignment.section_code.split("_")[0]})`;
  const groups = new Map();
  assignments.forEach((assignment) => {
    const key = groupKey(assignment);
    groups.set(key, [...(groups.get(key) || []), assignment]);
  });
  return `<div class="result-groups">
    ${[...groups.entries()].sort(([first], [second]) => String(first).localeCompare(String(second), "vi")).map(([label, items]) => `
      <section class="result-group">
        <header><h3>${escapeHtml(label)}</h3><span>${items.length} lớp học phần</span></header>
        <div class="table-wrap result-group-table">
          <table>
            <thead><tr><th>Lớp học phần</th><th>Thứ</th><th>Tiết</th><th>Phòng</th><th>Loại lớp</th></tr></thead>
            <tbody>${items.sort(compareAssignments).map((assignment) => `
              <tr><td><strong>${escapeHtml(assignment.section_code)}</strong><br><small>${escapeHtml(assignment.course_name)}</small></td><td>${dayLabels[assignment.day_of_week] || assignment.day_of_week}</td><td>Tiết ${assignment.start_period}-${assignment.end_period}</td><td>${escapeHtml(assignment.room_code)}</td><td>${courseTypeLabels[assignment.course_type] || escapeHtml(assignment.course_type)}</td></tr>
            `).join("")}</tbody>
          </table>
        </div>
      </section>
    `).join("")}
  </div>`;
}

function renderWeeklyBoard(assignments) {
  const byDay = new Map(Object.keys(dayLabels).map((day) => [day, []]));
  assignments.forEach((assignment) => byDay.get(String(assignment.day_of_week))?.push(assignment));
  return `<div class="weekly-board">
    ${Object.entries(dayLabels).map(([day, label]) => `
      <section class="weekly-day">
        <h3>${escapeHtml(label)}</h3>
        <div class="weekly-day-items">
          ${(byDay.get(day) || []).sort((first, second) => Number(first.start_period) - Number(second.start_period)).map((assignment) => `
            <article class="schedule-item ${escapeHtml(String(assignment.course_type || "").toLowerCase())}">
              <strong>Tiết ${assignment.start_period}-${assignment.end_period}</strong>
              <span>${escapeHtml(assignment.section_code)}</span>
              <span>${escapeHtml(assignment.course_name)}</span>
              <small>${escapeHtml(assignment.lecturer_name || assignment.lecturer_code)} · ${escapeHtml(assignment.room_code)}</small>
            </article>
          `).join("") || '<p class="empty-day">Chưa có lớp.</p>'}
        </div>
      </section>
    `).join("")}
  </div>`;
}

async function loadEditorFileList() {
  const list = document.getElementById("editorFileList");
  list.innerHTML = "Đang tải danh sách file...";
  try {
    if (!currentBatchCode) {
      list.innerHTML = '<div class="message">Hãy xác nhận một bộ CSV ở trang Nhập dữ liệu trước.</div>';
      return;
    }
    const response = await fetch(`/api/batches/${encodeURIComponent(currentBatchCode)}/files`);
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Không thể tải danh sách dữ liệu.");
    }
    list.innerHTML = payload.files.map((file) => `
      <button type="button" data-editor-file="${escapeHtml(file.file)}">
        ${escapeHtml(file.file)} (${file.row_count})
      </button>
    `).join("");
    list.querySelectorAll("[data-editor-file]").forEach((button) => {
      button.addEventListener("click", () => loadEditorFile(button.dataset.editorFile));
    });
    await loadEditorReferences();
  } catch (error) {
    list.innerHTML = `<div class="message">${escapeHtml(error.message)}</div>`;
  }
}

async function loadEditorReferences() {
  try {
    const [lecturers, rooms, slots] = await Promise.all([
      fetchBatchCsv("lecturers.csv"),
      fetchBatchCsv("rooms.csv"),
      fetchBatchCsv("time_slots.csv"),
    ]);
    editorReferences = {
      lecturers: lecturers.rows,
      rooms: rooms.rows,
      slots: slots.rows,
    };
  } catch {
    editorReferences = { lecturers: [], rooms: [], slots: [] };
  }
}

async function fetchBatchCsv(fileName) {
  const response = await fetch(`/api/batches/${encodeURIComponent(currentBatchCode)}/files/${encodeURIComponent(fileName)}`);
  if (!response.ok) {
    throw new Error(`Không thể đọc ${fileName}.`);
  }
  return response.json();
}

async function loadEditorFile(fileName) {
  setEditorMessage("Đang mở file...", "ok");
  try {
    const response = await fetch(`/api/batches/${encodeURIComponent(currentBatchCode)}/files/${encodeURIComponent(fileName)}`);
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Không thể mở file CSV.");
    }
    editorState = {
      file: payload.file,
      headers: payload.headers,
      rows: payload.rows,
    };
    document.querySelectorAll("[data-editor-file]").forEach((button) => {
      button.classList.toggle("active", button.dataset.editorFile === fileName);
    });
    renderEditorTable();
    setEditorMessage(`Đã mở ${payload.file}. Có ${payload.row_count} dòng dữ liệu.`, "ok");
  } catch (error) {
    setEditorMessage(error.message);
  }
}

function renderEditorTable() {
  document.getElementById("editorTitle").textContent = editorState.file || "Chưa chọn file";
  document.getElementById("editorSubtitle").textContent = editorState.file
    ? "Sửa trực tiếp trong ô dữ liệu rồi bấm Lưu file."
    : "Chọn một file phía trên để xem và sửa dữ liệu.";

  const table = document.getElementById("editorTable");
  if (!editorState.file) {
    table.innerHTML = `<thead><tr><th>Dữ liệu</th></tr></thead><tbody><tr><td>Chưa chọn file.</td></tr></tbody>`;
    return;
  }

  table.innerHTML = `
    <thead>
      <tr>
        <th>#</th>
        ${editorState.headers.map((header) => `<th title="${escapeHtml(header)}">${escapeHtml(editorColumnLabel(header))}</th>`).join("")}
        <th>Thao tác</th>
      </tr>
    </thead>
    <tbody>
      ${editorState.rows.map((row, rowIndex) => `
        <tr>
          <td>${rowIndex + 1}</td>
          ${editorState.headers.map((header) => `
            <td>${renderEditorField(header, row[header] || "", rowIndex)}</td>
          `).join("")}
          <td class="editor-action-cell"><button class="delete-row-button" type="button" data-delete-row="${rowIndex}">Xóa</button></td>
        </tr>
      `).join("")}
    </tbody>
  `;

  table.querySelectorAll("input[data-row][data-column]").forEach((input) => {
    input.addEventListener("input", () => {
      const rowIndex = Number(input.dataset.row);
      const column = input.dataset.column;
      editorState.rows[rowIndex][column] = input.value;
      applyDerivedEditorValues(rowIndex);
    });
  });
  table.querySelectorAll("select[data-row][data-column]").forEach((select) => {
    select.addEventListener("change", () => {
      const rowIndex = Number(select.dataset.row);
      const column = select.dataset.column;
      editorState.rows[rowIndex][column] = select.value;
      applyDerivedEditorValues(rowIndex);
    });
  });
  table.querySelectorAll("button[data-multi-picker]").forEach((button) => {
    button.addEventListener("click", () => {
      openMultiPicker(Number(button.dataset.row), button.dataset.column, button);
    });
  });
  table.querySelectorAll("button[data-delete-row]").forEach((button) => {
    button.addEventListener("click", () => deleteEditorRow(Number(button.dataset.deleteRow)));
  });
}

function renderEditorField(header, value, rowIndex) {
  if (editorState.file === "time_slots.csv" && header === "slot_code") {
    return `
      <input
        data-row="${rowIndex}"
        data-column="${escapeHtml(header)}"
        value="${escapeHtml(value)}"
        readonly
        title="Mã này được tự tạo từ thứ và khoảng tiết."
      />
    `;
  }
  if (editorState.file === "academic_calendar.csv" && header === "day_of_week") {
    return `<input data-row="${rowIndex}" data-column="${escapeHtml(header)}" value="${escapeHtml(dayLabels[value] || value)}" readonly title="Thứ được tự cập nhật theo ngày đã chọn." />`;
  }
  const multiOptions = getEditorMultiOptions(header);
  if (multiOptions) {
    return `
      <button
        class="multi-picker-trigger"
        type="button"
        data-multi-picker
        data-row="${rowIndex}"
        data-column="${escapeHtml(header)}"
        aria-haspopup="dialog"
      >
        <span>${escapeHtml(summarizeMultiValue(header, value))}</span>
        <span class="multi-picker-trigger-action">Chọn</span>
      </button>
    `;
  }
  const options = getEditorOptions(header);
  if (!options) {
    return `<input ${getEditorInputAttributes(header)} data-row="${rowIndex}" data-column="${escapeHtml(header)}" aria-label="${escapeHtml(editorColumnLabel(header))}" value="${escapeHtml(value)}" />`;
  }
  const hasValue = value !== "" && !options.some((option) => option.value === value);
  const normalizedOptions = hasValue
    ? [{ value, label: `${value} (giá trị hiện tại)` }, ...options]
    : options;
  return `
    <select data-row="${rowIndex}" data-column="${escapeHtml(header)}">
      ${normalizedOptions.map((option) => `
        <option value="${escapeHtml(option.value)}" ${option.value === value ? "selected" : ""}>
          ${escapeHtml(option.label)}
        </option>
      `).join("")}
    </select>
  `;
}

function getEditorOptions(header) {
  const staticOptions = {
    day_of_week: [
      { value: "2", label: "Thứ Hai" },
      { value: "3", label: "Thứ Ba" },
      { value: "4", label: "Thứ Tư" },
      { value: "5", label: "Thứ Năm" },
      { value: "6", label: "Thứ Sáu" },
      { value: "7", label: "Thứ Bảy" },
      { value: "8", label: "Chủ nhật" },
    ],
    session_type: [
      { value: "SANG", label: "Sáng" },
      { value: "CHIEU", label: "Chiều" },
      { value: "TOI", label: "Tối" },
    ],
    supports_course_types: [
      { value: "THEORY", label: "Lý thuyết" },
      { value: "PRACTICE|INTEGRATED", label: "Thực hành / tích hợp" },
    ],
    course_type: [
      { value: "THEORY", label: "Lý thuyết" },
      { value: "PRACTICE", label: "Thực hành" },
      { value: "INTEGRATED", label: "Lý thuyết - thực hành" },
    ],
    required_room_type: [
      { value: "THEORY_ROOM", label: "Phòng lý thuyết" },
      { value: "COMPUTER_LAB", label: "Phòng máy" },
      { value: "SPECIALIZED_LAB", label: "Phòng chuyên ngành" },
    ],
    room_type: [
      { value: "THEORY_ROOM", label: "Phòng lý thuyết" },
      { value: "COMPUTER_LAB", label: "Phòng máy" },
      { value: "SPECIALIZED_LAB", label: "Phòng chuyên ngành" },
    ],
    room_size_category: [
      { value: "STANDARD", label: "Phòng tiêu chuẩn" },
      { value: "LARGE_HALL", label: "Giảng đường lớn" },
    ],
    available: booleanOptions(),
    active: booleanOptions(),
    mandatory: booleanOptions(),
    is_teaching_day: booleanOptions(),
    is_holiday: booleanOptions(),
  };
  if (staticOptions[header]) {
    return staticOptions[header];
  }
  if (header === "lecturer_code" && editorState.file !== "lecturers.csv") {
    return editorReferences.lecturers.map((lecturer) => ({
      value: lecturer.lecturer_code,
      label: `${lecturer.lecturer_code} - ${lecturer.lecturer_name}`,
    }));
  }
  if (header === "room_code" && editorState.file !== "rooms.csv") {
    return editorReferences.rooms.map((room) => ({
      value: room.room_code,
      label: `${room.room_code} - ${room.room_name}`,
    }));
  }
  if (header === "slot_code" && editorState.file !== "time_slots.csv") {
    return editorReferences.slots.map((slot) => ({
      value: slot.slot_code,
      label: `${slot.slot_code} - ${dayLabels[slot.day_of_week] || slot.day_of_week}, tiết ${slot.start_period}-${slot.end_period}`,
    }));
  }
  return null;
}

function getEditorInputAttributes(header) {
  if (header === "date" || header === "start_date" || header === "end_date") {
    return 'type="date"';
  }
  const positiveNumberFields = new Set([
    "capacity", "start_period", "end_period", "required_sessions", "weekly_sessions",
    "periods_per_session", "expected_students", "initial_registration_limit",
    "approved_max_students", "scheduling_student_count", "academic_week",
    "max_days_per_week", "max_consecutive_sessions",
  ]);
  return positiveNumberFields.has(header) ? 'type="number" min="1" step="1"' : 'type="text"';
}

function editorColumnLabel(header) {
  return editorColumnLabels[header] || header;
}

function deleteEditorRow(rowIndex) {
  const row = editorState.rows[rowIndex];
  if (!row) return;
  const identity = row.section_code || row.lecturer_code || row.room_code || row.slot_code || row.date || `dòng ${rowIndex + 1}`;
  const confirmed = window.confirm(`Xóa ${identity}? Thay đổi chỉ được ghi vào file sau khi bạn bấm Lưu file.`);
  if (!confirmed) return;
  editorState.rows.splice(rowIndex, 1);
  renderEditorTable();
  setEditorMessage("Đã xóa dòng khỏi bảng. Bấm Lưu file để xác nhận thay đổi, hoặc tải lại file để bỏ thay đổi này.", "ok");
}

function getEditorMultiOptions(header) {
  if (header === "preferred_days" || header === "undesired_days") {
    return Object.entries(dayLabels).map(([value, label]) => ({ value, label }));
  }
  if (header === "preferred_slots" || header === "undesired_slots") {
    return editorReferences.slots.map((slot) => ({
      value: slot.slot_code,
      label: `${slot.slot_code} - ${dayLabels[slot.day_of_week] || slot.day_of_week}, tiết ${slot.start_period}-${slot.end_period}`,
    }));
  }
  return null;
}

function initialiseMultiPicker() {
  const dialog = document.getElementById("multiPickerDialog");
  document.getElementById("closeMultiPickerButton").addEventListener("click", closeMultiPicker);
  document.getElementById("clearMultiPickerButton").addEventListener("click", () => {
    multiPickerState.selectedValues.clear();
    renderMultiPickerContent();
  });
  document.getElementById("applyMultiPickerButton").addEventListener("click", applyMultiPicker);
  dialog.addEventListener("close", () => {
    multiPickerState.trigger?.focus();
  });
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) closeMultiPicker();
  });
}

function openMultiPicker(rowIndex, header, trigger) {
  const value = editorState.rows[rowIndex][header] || "";
  multiPickerState = {
    rowIndex,
    header,
    selectedValues: new Set(value.split("|").filter(Boolean)),
    trigger,
  };
  const isDayPicker = header === "preferred_days" || header === "undesired_days";
  document.getElementById("multiPickerTitle").textContent = isDayPicker
    ? (header === "preferred_days" ? "Ngày giảng dạy mong muốn" : "Ngày không mong muốn")
    : (header === "preferred_slots" ? "Khung giờ giảng dạy mong muốn" : "Khung giờ không mong muốn");
  document.getElementById("multiPickerDescription").textContent = isDayPicker
    ? "Bấm vào từng ngày để chọn hoặc bỏ chọn."
    : "Tích các khung giờ phù hợp. Mỗi khung giờ đã có thứ và khoảng tiết cố định.";
  renderMultiPickerContent();
  document.getElementById("multiPickerDialog").showModal();
}

function renderMultiPickerContent() {
  const content = document.getElementById("multiPickerContent");
  const { header, selectedValues } = multiPickerState;
  if (header === "preferred_days" || header === "undesired_days") {
    content.innerHTML = `
      <div class="day-picker-grid" role="group" aria-label="Chọn ngày trong tuần">
        ${Object.entries(dayLabels).map(([value, label]) => `
          <button class="day-picker-option ${selectedValues.has(value) ? "selected" : ""}" type="button" data-picker-value="${value}" aria-pressed="${selectedValues.has(value)}">${escapeHtml(label)}</button>
        `).join("")}
      </div>
    `;
  } else {
    const slotsByDay = editorReferences.slots.reduce((groups, slot) => {
      const day = slot.day_of_week;
      groups[day] = groups[day] || [];
      groups[day].push(slot);
      return groups;
    }, {});
    content.innerHTML = `
      <div class="slot-picker-grid">
        ${Object.entries(dayLabels).map(([day, label]) => {
          const slots = slotsByDay[day] || [];
          if (!slots.length) return "";
          return `
            <fieldset class="slot-picker-day">
              <legend>${escapeHtml(label)}</legend>
              ${slots.map((slot) => `
                <label class="slot-picker-option">
                  <input type="checkbox" data-picker-value="${escapeHtml(slot.slot_code)}" ${selectedValues.has(slot.slot_code) ? "checked" : ""} />
                  <span>${escapeHtml(formatSlotLabel(slot))}</span>
                </label>
              `).join("")}
            </fieldset>
          `;
        }).join("")}
      </div>
    `;
  }
  content.querySelectorAll("[data-picker-value]").forEach((control) => {
    control.addEventListener("change", () => toggleMultiPickerValue(control.dataset.pickerValue, control.checked));
    control.addEventListener("click", () => {
      if (control.tagName === "BUTTON") {
        toggleMultiPickerValue(control.dataset.pickerValue, !multiPickerState.selectedValues.has(control.dataset.pickerValue));
      }
    });
  });
  updateMultiPickerSelectionCount();
}

function toggleMultiPickerValue(value, isSelected) {
  if (isSelected) {
    multiPickerState.selectedValues.add(value);
  } else {
    multiPickerState.selectedValues.delete(value);
  }
  renderMultiPickerContent();
}

function updateMultiPickerSelectionCount() {
  const count = multiPickerState.selectedValues.size;
  document.getElementById("multiPickerSelectionCount").textContent = count
    ? `Đã chọn ${count} giá trị`
    : "Chưa chọn giá trị nào";
}

function applyMultiPicker() {
  const { rowIndex, header, selectedValues } = multiPickerState;
  if (rowIndex === null || !header) return;
  const optionOrder = getEditorMultiOptions(header).map((option) => option.value);
  editorState.rows[rowIndex][header] = optionOrder.filter((value) => selectedValues.has(value)).join("|");
  const button = document.querySelector(`[data-row="${rowIndex}"][data-column="${header}"]`);
  if (button) button.querySelector("span").textContent = summarizeMultiValue(header, editorState.rows[rowIndex][header]);
  document.getElementById("multiPickerDialog").close();
}

function closeMultiPicker() {
  const dialog = document.getElementById("multiPickerDialog");
  if (dialog.open) dialog.close();
}

function summarizeMultiValue(header, value) {
  const selectedValues = value.split("|").filter(Boolean);
  if (!selectedValues.length) return "Chưa chọn";
  if (header === "preferred_days" || header === "undesired_days") {
    return selectedValues.map((day) => dayLabels[day] || day).join(", ");
  }
  const labels = selectedValues.map((slotCode) => {
    const slot = editorReferences.slots.find((item) => item.slot_code === slotCode);
    return slot ? formatSlotLabel(slot) : slotCode;
  });
  return labels.length <= 2 ? labels.join("; ") : `Đã chọn ${labels.length} khung giờ`;
}

function formatSlotLabel(slot) {
  const sessionLabels = { SANG: "Sáng", CHIEU: "Chiều", TOI: "Tối" };
  return `${sessionLabels[slot.session_type] || "Ca học"}, tiết ${slot.start_period}-${slot.end_period}`;
}

function applyDerivedEditorValues(rowIndex) {
  if (editorState.file === "time_slots.csv") {
    updateTimeSlotDerivedValues(rowIndex);
  }
  if (editorState.file === "academic_calendar.csv") {
    updateAcademicCalendarDerivedValues(rowIndex);
  }
  if (editorState.file === "course_sections.csv") {
    updateCourseSectionDerivedValues(rowIndex);
  }
}

function updateAcademicCalendarDerivedValues(rowIndex) {
  const row = editorState.rows[rowIndex];
  if (!/^\d{4}-\d{2}-\d{2}$/.test(row.date || "")) return;
  const selectedDate = new Date(`${row.date}T00:00:00`);
  if (Number.isNaN(selectedDate.getTime())) return;
  row.day_of_week = String(selectedDate.getDay() === 0 ? 8 : selectedDate.getDay() + 1);
  const field = document.querySelector(`[data-row="${rowIndex}"][data-column="day_of_week"]`);
  if (field) field.value = dayLabels[row.day_of_week];
}

function updateTimeSlotDerivedValues(rowIndex) {
  const row = editorState.rows[rowIndex];
  const day = row.day_of_week;
  const start = row.start_period;
  const end = row.end_period;
  if (!day || !start || !end || !dayPrefixes[day]) {
    return;
  }
  row.slot_code = `${dayPrefixes[day]}_${start}_${end}`;
  row.session_type = Number(end) <= 6 ? "SANG" : Number(end) <= 12 ? "CHIEU" : "TOI";
  row.supports_course_types = Number(end) - Number(start) + 1 === 3
    ? "THEORY"
    : "PRACTICE|INTEGRATED";
  syncEditorField(rowIndex, "slot_code", row.slot_code);
  syncEditorField(rowIndex, "session_type", row.session_type);
  syncEditorField(rowIndex, "supports_course_types", row.supports_course_types);
}

function updateCourseSectionDerivedValues(rowIndex) {
  const row = editorState.rows[rowIndex];
  const approved = parsePositiveInteger(row.approved_max_students);
  const initial = parsePositiveInteger(row.initial_registration_limit);
  const expected = parsePositiveInteger(row.expected_students);
  const schedulingCount = approved || initial || expected;
  if (schedulingCount) {
    row.scheduling_student_count = String(schedulingCount);
    syncEditorField(rowIndex, "scheduling_student_count", row.scheduling_student_count);
  }
  if (row.course_type === "THEORY") {
    row.periods_per_session = "3";
    syncEditorField(rowIndex, "periods_per_session", row.periods_per_session);
  }
}

function parsePositiveInteger(value) {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}

function syncEditorField(rowIndex, column, value) {
  const field = document.querySelector(`[data-row="${rowIndex}"][data-column="${column}"]`);
  if (field) {
    field.value = value;
  }
}

function booleanOptions() {
  return [
    { value: "true", label: "Có" },
    { value: "false", label: "Không" },
  ];
}

function addEditorRow() {
  if (!editorState.file) {
    setEditorMessage("Vui lòng chọn file trước khi thêm dòng.");
    return;
  }
  const row = {};
  editorState.headers.forEach((header) => {
    row[header] = "";
  });
  editorState.rows.push(row);
  renderEditorTable();
  setEditorMessage("Đã thêm một dòng trống. Hãy nhập dữ liệu rồi bấm Lưu file.", "ok");
}

async function saveEditorFile() {
  if (!editorState.file) {
    setEditorMessage("Vui lòng chọn file trước khi lưu.");
    return;
  }
  setEditorMessage("Đang lưu file...", "ok");
  try {
    const response = await fetch(`/api/batches/${encodeURIComponent(currentBatchCode)}/files/${encodeURIComponent(editorState.file)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rows: editorState.rows }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(formatDatasetSaveError(payload.detail));
    }
    if (payload.batch?.batch_code) {
      currentBatchCode = payload.batch.batch_code;
      confirmedBatchLabel.textContent = `Đang chỉnh sửa: ${currentBatchCode}`;
      await loadBatches();
    }
    setEditorMessage(`${payload.message} Hiện có ${payload.row_count} dòng dữ liệu.`, "ok");
    loadEditorFileList();
  } catch (error) {
    setEditorMessage(error.message);
  }
}

function formatDatasetSaveError(detail) {
  if (typeof detail === "string") return detail;
  if (!detail || typeof detail !== "object") return "Không thể lưu file CSV.";
  const messages = (detail.errors || []).slice(0, 3).map((error) => {
    const position = [error.file, error.row ? `dòng ${error.row}` : "", error.column || ""].filter(Boolean).join(", ");
    return `${position}: ${error.reason}`;
  });
  return [detail.message || "Không thể lưu file CSV.", ...messages].join(" ");
}

async function loadBatches() {
  try {
    const response = await fetch("/api/batches");
    const payload = await response.json();
    const batches = payload.batches || [];
    if (!currentBatchCode && batches.length) currentBatchCode = batches[0].batch_code;
    gaBatchCode.innerHTML = batches.length
      ? batches.map((batch) => `<option value="${escapeHtml(batch.batch_code)}">${escapeHtml(batch.batch_code)} (${batch.section_count} lớp)</option>`).join("")
      : '<option value="">Chưa có bộ dữ liệu đã xác nhận</option>';
    if (currentBatchCode) gaBatchCode.value = currentBatchCode;
  } catch {
    gaBatchCode.innerHTML = '<option value="">Không tải được danh sách bộ dữ liệu</option>';
  }
}

function setEditorMessage(message, tone = "error") {
  document.getElementById("editorMessages").innerHTML = `<div class="message ${tone === "ok" ? "ok" : ""}">${escapeHtml(message)}</div>`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
