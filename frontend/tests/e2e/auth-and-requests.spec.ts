import path from "node:path";
import { test, expect } from "@playwright/test";

const lecturer = {
  id: 7,
  username: "lecturer.demo",
  display_name: "Giảng viên Demo",
  role: "LECTURER",
  lecturer_code: "GV001",
};

test("đăng nhập và điều hướng đúng cổng giảng viên", async ({ page }) => {
  await page.route("**/api/auth/me", async (route) => {
    await route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ detail: "Chưa đăng nhập" }) });
  });
  await page.route("**/api/auth/login", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ user: lecturer }) });
  });
  await page.route("**/api/lecturer/timetable**", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ official_code: null, week: 1, lecturer_code: "GV001", lecturer_name: "Giảng viên Demo", occurrences: [], course_sections: [] }) });
  });

  await page.goto("/#/login");
  await expect(page.getByRole("heading", { name: "Chào mừng bạn quay lại" })).toBeVisible();
  await page.getByLabel(/Tên đăng nhập/).fill("lecturer.demo");
  await page.getByLabel(/Mật khẩu/).fill("password");
  await page.getByRole("button", { name: "Đăng nhập" }).click();
  await expect(page).toHaveURL(/#\/lecturer\/timetable$/);
  await expect(page.getByRole("heading", { name: "Lịch giảng dạy của tôi" })).toBeVisible();
});

test("giảng viên chỉ xem được lịch theo mã tài khoản", async ({ page }) => {
  const ownLecturer = { ...lecturer, username: "lecturer.gv001", display_name: "Giảng viên GV001" };
  await page.route("**/api/auth/me", async (route) => await route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ detail: "Chưa đăng nhập" }) }));
  await page.route("**/api/auth/login", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ user: ownLecturer }) }));
  await page.route("**/api/lecturer/timetable**", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ official_code: "OFF-001", week: 1, lecturer_code: "GV001", lecturer_name: ownLecturer.display_name, occurrences: [{ section_code: "SEC-GV001", course_code: "CS101", course_name: "Môn của GV001", lecturer_code: "GV001", date: "2026-09-14", academic_week: 1, room_code: "A301", slot_code: "MON_1_3", day_of_week: 2, start_period: 1, end_period: 3, status: "SCHEDULED" }], course_sections: [{ section_code: "SEC-GV001", course_code: "CS101", course_name: "Môn của GV001", lecturer_code: "GV001", room_code: "A301", slot_code: "MON_1_3", day_of_week: 2, start_period: 1, end_period: 3 }] }) }));
  await page.goto("/#/login");
  await page.getByLabel(/Tên đăng nhập/).fill("lecturer.gv001");
  await page.getByLabel(/Mật khẩu/).fill("password");
  await page.getByRole("button", { name: "Đăng nhập" }).click();
  await expect(page.getByText("SEC-GV001")).toBeVisible();
  await expect(page.getByText("SEC-GV002")).not.toBeVisible();
});

test("hiển thị lịch sử yêu cầu và cho phép hủy yêu cầu đang chờ", async ({ page }) => {
  const request = {
    request_code: "REQ-001",
    official_code: "OFF-001",
    requester_username: lecturer.username,
    requester_display_name: lecturer.display_name,
    section_code: "AI-01",
    request_type: "SUSPEND_ONE_OCCURRENCE",
    occurrence_date: "2026-09-14",
    reason: "Có lịch công tác",
    status: "PENDING",
    created_at: "2026-08-13T08:00:00Z",
    updated_at: "2026-08-13T08:00:00Z",
    current_snapshot: { section_code: "AI-01", date: "2026-09-14", room_code: "A301", slot_code: "LT_01_03", status: "SCHEDULED" },
    events: [],
  };
  await page.route("**/api/auth/me", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ user: lecturer }) });
  });
  await page.route("**/api/lecturer/change-requests", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ requests: [request], total: 1 }) });
    }
  });
  await page.route("**/api/lecturer/change-requests/REQ-001", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(request) });
  });
  await page.route("**/api/lecturer/change-requests/REQ-001/cancel", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ message: "Đã hủy yêu cầu.", request: { ...request, status: "CANCELLED" } }) });
  });

  await page.goto("/#/lecturer/requests");
  await expect(page.getByRole("heading", { name: "Yêu cầu đã gửi" })).toBeVisible();
  await expect(page.getByText("REQ-001")).toBeVisible();
  await page.getByRole("button", { name: "REQ-001" }).click();
  await expect(page.getByRole("button", { name: "Hủy yêu cầu" })).toBeVisible();
  page.once("dialog", (dialog) => void dialog.accept());
  await page.getByRole("button", { name: "Hủy yêu cầu" }).click();
  await expect(page.getByText("Đã hủy yêu cầu.")).toBeVisible();
});

test("Phòng Đào tạo xem, kiểm tra và áp dụng yêu cầu giảng viên", async ({ page }) => {
  const office = { id: 2, username: "phongdaotao", display_name: "Phòng Đào tạo", role: "TRAINING_OFFICE" };
  const request = {
    request_code: "REQ-002", official_code: "OFF-001", requester_username: "gv001",
    requester_display_name: "Giảng viên Một", section_code: "AI-01",
    request_type: "SUSPEND_ONE_OCCURRENCE", occurrence_date: "2026-09-14",
    reason: "Lịch công tác", status: "PENDING", created_at: "2026-08-13T08:00:00Z",
    updated_at: "2026-08-13T08:00:00Z", current_snapshot: { section_code: "AI-01", date: "2026-09-14", status: "SCHEDULED" }, events: [],
  };
  await page.route("**/api/auth/me", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ user: office }) }));
  await page.route("**/api/batches", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ batches: [] }) }));
  await page.route("**/api/ga/runs", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ runs: [] }) }));
  await page.route("**/api/training-office/change-requests*", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ requests: [request], total: 1 }) });
  });
  await page.route("**/api/training-office/change-requests/REQ-002", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(request) });
  });
  await page.route("**/api/training-office/change-requests/REQ-002/validate", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ request: { ...request, validation_result: { valid: true, hard_conflicts: [], checked_at: "2026-08-13T08:10:00Z" } }, validation: { valid: true, hard_conflicts: [], checked_at: "2026-08-13T08:10:00Z" } }) });
  });
  await page.route("**/api/training-office/change-requests/REQ-002/approve", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ message: "Đã duyệt yêu cầu.", request: { ...request, status: "APPROVED" } }) });
  });
  await page.route("**/api/training-office/change-requests/REQ-002/apply", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ message: "Đã áp dụng yêu cầu.", request: { ...request, status: "APPLIED" }, official: {} }) });
  });

  await page.goto("/#/training-office/requests");
  await expect(page.getByRole("heading", { name: "Yêu cầu từ giảng viên" })).toBeVisible();
  await page.getByRole("button", { name: "REQ-002" }).click();
  await page.getByRole("button", { name: "Kiểm tra xung đột" }).click();
  await expect(page.getByRole("heading", { name: "Không phát hiện xung đột cứng" })).toBeVisible();
  page.once("dialog", (dialog) => void dialog.accept());
  await page.getByRole("button", { name: "Phê duyệt" }).click();
  await expect(page.getByText("Đã duyệt yêu cầu.")).toBeVisible();
  page.once("dialog", (dialog) => void dialog.accept());
  await page.getByRole("button", { name: "Kiểm tra lại và áp dụng" }).click();
  await expect(page.getByText("Đã áp dụng yêu cầu.")).toBeVisible();
});

test("Phòng Đào tạo hiển thị lọc, xuất và công cụ ngày nghỉ", async ({ page }) => {
  const office = { id: 2, username: "phongdaotao", display_name: "Phòng Đào tạo", role: "TRAINING_OFFICE" };
  const assignment = { section_code: "AI-01", course_code: "AI101", course_name: "Trí tuệ nhân tạo", lecturer_code: "GV001", lecturer_name: "Giảng viên Một", room_code: "A301", slot_code: "LT_01_03", start_period: 1, end_period: 3, course_type: "THEORY", scheduling_student_count: 40 };
  const occurrence = { ...assignment, date: "2026-09-14", academic_week: 1, status: "SCHEDULED" };
  const run = { run_code: "RUN-001", status: "COMPLETED", created_at: "2026-08-13T08:00:00Z", assignments: [assignment], occurrences: [occurrence] };
  const official = { official_code: "OFF-001", source_run_code: "RUN-001", assignments: [assignment], occurrences: [occurrence], skipped_holiday_sessions: [{ ...occurrence, date: "2026-09-21", holiday_name: "Ngày lễ" }], makeup_sessions: [] };
  await page.route("**/api/auth/me", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ user: office }) }));
  await page.route("**/api/batches", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ batches: [] }) }));
  await page.route("**/api/ga/runs", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ runs: [run] }) }));
  await page.route("**/api/ga/runs/RUN-001", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(run) }));
  await page.route("**/api/ga/runs/RUN-001/publish", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(official) }));
  await page.route("**/api/ga/official-timetables/OFF-001/segments", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ message: "Đã tạo phân đoạn.", official: { ...official, segments: [{ section_code: "AI-01" }] } }) }));
  await page.route("**/api/ga/official-timetables/OFF-001/makeups", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ message: "Đã thêm buổi học bù.", official: { ...official, makeup_sessions: [{ ...occurrence, status: "MAKEUP" }] } }) }));

  await page.goto("/#/training-office/results");
  await page.getByRole("button", { name: "RUN-001" }).click();
  await expect(page.getByText("Hiển thị 1 trên 1 lớp học phần.")).toBeVisible();
  await page.getByLabel("Tìm kiếm").fill("GV001");
  await expect(page.getByText("Hiển thị 1 trên 1 lớp học phần.")).toBeVisible();
  await expect(page.getByRole("link", { name: "Xuất CSV" })).toHaveAttribute("href", /export\.csv$/);
  await page.getByRole("button", { name: "Công bố lịch chính thức" }).click();
  await expect(page.getByText("Có 1 buổi cần bù do ngày nghỉ.")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Tạo phân đoạn lịch" })).toBeVisible();
  await page.getByRole("heading", { name: "Thêm buổi học bù" }).scrollIntoViewIfNeeded();
  await expect(page.getByLabel("Buổi thiếu do ngày nghỉ")).toBeVisible();
});

test("Phòng Đào tạo upload, preview và xác nhận đủ 7 CSV", async ({ page }) => {
  const office = { id: 2, username: "phongdaotao.import", display_name: "Phòng Đào tạo", role: "TRAINING_OFFICE" };
  const batch = { batch_code: "BATCH-IMPORT-001", display_name: "Bộ dữ liệu kiểm thử", version_number: 1, section_count: 5, confirmed_at: "2026-08-21T08:00:00Z" };
  const files = ["lecturers.csv", "rooms.csv", "time_slots.csv", "course_sections.csv", "lecturer_time_preferences.csv", "room_unavailable_slots.csv", "academic_calendar.csv"];
  await page.route("**/api/auth/me", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ user: office }) }));
  await page.route("**/api/batches", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ batches: [batch] }) }));
  await page.route("**/api/ga/runs", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ runs: [] }) }));
  await page.route("**/api/imports/csv/preview", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ valid: true, files: files.map((file) => ({ file, row_count: 5 })), errors: [] }) }));
  await page.route("**/api/imports/csv/confirm", async (route) => await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ batch, message: "Đã xác nhận bộ dữ liệu." }) }));

  await page.goto("/#/training-office/import");
  await page.locator('input[type="file"]').setInputFiles(files.map((file) => path.resolve(process.cwd(), "..", "data", "samples", "small", file)));
  await page.getByRole("button", { name: "Kiểm tra dữ liệu" }).click();
  await expect(page.getByRole("heading", { name: "Dữ liệu hợp lệ" })).toBeVisible();
  await page.getByRole("button", { name: "Xác nhận bộ dữ liệu" }).click();
  await expect(page).toHaveURL(/#\/training-office\/ga$/);
  await expect(page.getByRole("heading", { name: "Cấu hình Thuật toán Di truyền" })).toBeVisible();
  await expect(page.getByText("Trọng số ràng buộc mềm")).toBeVisible();
  await expect(page.getByLabel("Ưu tiên giảng viên")).toHaveValue("10");
});
