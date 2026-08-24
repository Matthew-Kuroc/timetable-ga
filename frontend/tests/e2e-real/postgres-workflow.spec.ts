import path from "node:path";
import { readFile } from "node:fs/promises";
import { expect, request as playwrightRequest, test, type APIRequestContext, type Page } from "@playwright/test";

const repoRoot = path.resolve(import.meta.dirname, "../../..");
const sampleRoot = path.join(repoRoot, "data", "samples", "small");
const csvFiles = [
  "lecturers.csv",
  "rooms.csv",
  "time_slots.csv",
  "course_sections.csv",
  "lecturer_time_preferences.csv",
  "room_unavailable_slots.csv",
  "academic_calendar.csv",
].map((name) => path.join(sampleRoot, name));

const adminUsername = process.env.E2E_ADMIN_USERNAME || "admin.e2e";
const officeUsername = process.env.E2E_OFFICE_USERNAME || "office.e2e";
const lecturerUsername = "lecturer.e2e";
const accountPassword = process.env.E2E_ACCOUNT_PASSWORD;
const apiBaseUrl = process.env.E2E_API_BASE_URL || "http://127.0.0.1:18080";

type Assignment = {
  section_code: string;
  lecturer_code: string;
  meeting_number?: number;
  room_code: string;
  slot_code: string;
  day_of_week: number;
};

type Occurrence = {
  section_code: string;
  meeting_number?: number;
  date: string;
  room_code: string;
  slot_code: string;
  academic_week: number;
  status: string;
};

type RunPayload = {
  run_code: string;
  batch_code: string;
  assignments: Assignment[];
  occurrences: Occurrence[];
  skipped_holiday_sessions: Array<{ section_code: string; meeting_number?: number; date: string }>;
  evaluation: { hard_violation_count: number };
};

type OfficialPayload = RunPayload & {
  official_code: string;
  source_run_code: string;
  makeup_sessions: Occurrence[];
};

async function loginInBrowser(page: Page, username: string) {
  if (!accountPassword) throw new Error("Thiếu E2E_ACCOUNT_PASSWORD.");
  await page.goto("/#/login");
  await page.getByLabel(/Tên đăng nhập/i).fill(username);
  await page.getByLabel(/Mật khẩu/i).fill(accountPassword);
  await page.getByRole("button", { name: "Đăng nhập" }).click();
}

async function authenticatedApi(username: string): Promise<APIRequestContext> {
  if (!accountPassword) throw new Error("Thiếu E2E_ACCOUNT_PASSWORD.");
  const api = await playwrightRequest.newContext({ baseURL: apiBaseUrl });
  const response = await api.post("/api/auth/login", {
    data: { username, password: accountPassword },
  });
  expect(response.ok(), await response.text()).toBeTruthy();
  return api;
}

function weekDate(weekStart: string, dayOfWeek: number) {
  const result = new Date(`${weekStart}T00:00:00Z`);
  result.setUTCDate(result.getUTCDate() + dayOfWeek - 2);
  return result.toISOString().slice(0, 10);
}

test("luồng thật từ CSV đến PostgreSQL, publish, học bù, request và export", async ({ page }) => {
  test.skip(!accountPassword, "Runner phải tạo E2E_ACCOUNT_PASSWORD.");

  await loginInBrowser(page, officeUsername);
  await expect(page).toHaveURL(/#\/training-office\/overview$/);
  await expect(page.getByText("Đã kết nối hệ thống")).toBeVisible();

  await page.goto("/#/training-office/import");
  await page.locator('input[type="file"]').setInputFiles(csvFiles);
  await page.getByRole("button", { name: "Kiểm tra dữ liệu" }).click();
  await expect(page.getByRole("heading", { name: "Dữ liệu hợp lệ" })).toBeVisible();
  await page.getByLabel(/Tên bộ dữ liệu/i).fill("E2E PostgreSQL thật");
  await page.getByLabel(/Học kỳ/i).fill("HK1");
  await page.getByLabel(/Năm học/i).fill("2026-2027");
  const confirmResponsePromise = page.waitForResponse((response) =>
    response.url().includes("/api/imports/csv/confirm") && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Xác nhận bộ dữ liệu" }).click();
  const confirmResponse = await confirmResponsePromise;
  expect(confirmResponse.ok(), await confirmResponse.text()).toBeTruthy();
  await expect(page).toHaveURL(/#\/training-office\/ga$/);

  await page.getByLabel("Kích thước quần thể").fill("12");
  await page.getByLabel("Số thế hệ").fill("4");
  const runResponsePromise = page.waitForResponse((response) =>
    response.url().includes("/api/ga/runs/preview") && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Chạy thuật toán" }).click();
  const runResponse = await runResponsePromise;
  expect(runResponse.ok(), await runResponse.text()).toBeTruthy();
  const run = await runResponse.json() as RunPayload;
  expect(run.evaluation.hard_violation_count).toBe(0);
  expect(run.assignments.length).toBeGreaterThan(0);
  await expect(page).toHaveURL(/#\/training-office\/results$/);
  await expect(page.getByRole("heading", { name: run.run_code })).toBeVisible();

  const publishResponsePromise = page.waitForResponse((response) =>
    response.url().includes(`/api/ga/runs/${run.run_code}/publish`) && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Công bố lịch chính thức" }).click();
  const publishResponse = await publishResponsePromise;
  expect(publishResponse.ok(), await publishResponse.text()).toBeTruthy();
  let official = await publishResponse.json() as OfficialPayload;
  expect(official.source_run_code).toBe(run.run_code);
  await expect(page).toHaveURL(/#\/training-office\/adjustments$/);
  await expect(page.getByText(official.official_code).last()).toBeVisible();

  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("link", { name: "Xuất CSV" }).first().click(),
  ]);
  expect(download.suggestedFilename()).toContain(official.official_code);
  expect(download.suggestedFilename()).toMatch(/\.csv$/);
  const downloadedPath = await download.path();
  expect(downloadedPath).not.toBeNull();
  const exported = await readFile(downloadedPath!);
  expect([...exported.subarray(0, 3)]).toEqual([0xef, 0xbb, 0xbf]);
  expect(exported.toString("utf8")).toMatch(/\d{2}-\d{2}-\d{4}/);

  const officeApi = await authenticatedApi(officeUsername);
  const firstOccurrence = official.occurrences[0];
  const firstAssignment = official.assignments.find((item) =>
    item.section_code === firstOccurrence.section_code
      && (item.meeting_number || 1) === (firstOccurrence.meeting_number || 1),
  )!;

  const segmentResponse = await officeApi.post(
    `/api/ga/official-timetables/${official.official_code}/segments`,
    {
      data: {
        section_code: firstOccurrence.section_code,
        meeting_number: firstOccurrence.meeting_number || 1,
        effective_start_date: firstOccurrence.date,
        effective_end_date: firstOccurrence.date,
        room_code: firstOccurrence.room_code,
        slot_code: firstOccurrence.slot_code,
        reason: "E2E xác minh phân đoạn room-only sau publish.",
      },
    },
  );
  expect(segmentResponse.ok(), await segmentResponse.text()).toBeTruthy();
  official = (await segmentResponse.json()).official as OfficialPayload;

  const skipped = run.skipped_holiday_sessions[0];
  expect(skipped).toBeTruthy();
  const skippedAssignment = official.assignments.find((item) =>
    item.section_code === skipped.section_code
      && (item.meeting_number || 1) === (skipped.meeting_number || 1),
  )!;
  const makeupDate = weekDate("2026-12-28", skippedAssignment.day_of_week);
  const makeupResponse = await officeApi.post(
    `/api/ga/official-timetables/${official.official_code}/makeups`,
    {
      data: {
        section_code: skipped.section_code,
        meeting_number: skipped.meeting_number || 1,
        makeup_date: makeupDate,
        room_code: skippedAssignment.room_code,
        slot_code: skippedAssignment.slot_code,
        original_missing_date: skipped.date,
        reason: "E2E học bù trong tuần 18.",
      },
    },
  );
  expect(makeupResponse.ok(), await makeupResponse.text()).toBeTruthy();
  official = (await makeupResponse.json()).official as OfficialPayload;
  expect(official.makeup_sessions.some((item) => item.date === makeupDate)).toBeTruthy();

  const week19Response = await officeApi.post(
    `/api/ga/official-timetables/${official.official_code}/makeups`,
    {
      data: {
        section_code: skipped.section_code,
        meeting_number: skipped.meeting_number || 1,
        makeup_date: weekDate("2027-01-04", skippedAssignment.day_of_week),
        room_code: skippedAssignment.room_code,
        slot_code: skippedAssignment.slot_code,
        reason: "E2E phải từ chối tuần 19.",
      },
    },
  );
  expect(week19Response.status()).toBe(422);

  const adminApi = await authenticatedApi(adminUsername);
  const createLecturer = await adminApi.post("/api/admin/users", {
    data: {
      username: lecturerUsername,
      display_name: "Giảng viên E2E",
      password: accountPassword,
      role: "LECTURER",
      lecturer_code: firstAssignment.lecturer_code,
    },
  });
  expect(createLecturer.ok(), await createLecturer.text()).toBeTruthy();

  await page.getByRole("button", { name: "Đăng xuất" }).click();
  await loginInBrowser(page, lecturerUsername);
  await expect(page).toHaveURL(/#\/lecturer\/timetable$/);
  await expect(page.getByRole("heading", { name: "Lịch giảng dạy của tôi" })).toBeVisible();

  const lecturerApi = await authenticatedApi(lecturerUsername);
  const ownedOccurrence = official.occurrences.find((item) =>
    official.assignments.some((assignment) =>
      assignment.section_code === item.section_code
        && assignment.lecturer_code === firstAssignment.lecturer_code,
    ) && item.status !== "MAKEUP",
  )!;
  const requestResponse = await lecturerApi.post("/api/lecturer/change-requests", {
    data: {
      official_code: official.official_code,
      section_code: ownedOccurrence.section_code,
      occurrence_date: ownedOccurrence.date,
      request_type: "SUSPEND_ONE_OCCURRENCE",
      reason: "E2E kiểm tra quy trình yêu cầu giảng viên.",
    },
  });
  expect(requestResponse.ok(), await requestResponse.text()).toBeTruthy();
  const requestPayload = (await requestResponse.json()).request as { request_code: string };

  const validateResponse = await officeApi.post(
    `/api/training-office/change-requests/${requestPayload.request_code}/validate`,
  );
  expect(validateResponse.ok(), await validateResponse.text()).toBeTruthy();
  expect((await validateResponse.json()).validation.valid).toBeTruthy();
  const approveResponse = await officeApi.post(
    `/api/training-office/change-requests/${requestPayload.request_code}/approve`,
    { data: {} },
  );
  expect(approveResponse.ok(), await approveResponse.text()).toBeTruthy();
  const applyResponse = await officeApi.post(
    `/api/training-office/change-requests/${requestPayload.request_code}/apply`,
  );
  expect(applyResponse.ok(), await applyResponse.text()).toBeTruthy();
  expect((await applyResponse.json()).request.status).toBe("APPLIED");

  await page.goto("/#/lecturer/requests");
  const requestCard = page.getByRole("button", { name: new RegExp(requestPayload.request_code) });
  await expect(requestCard).toBeVisible();
  await expect(requestCard).toContainText("Đã áp dụng");

  await Promise.all([adminApi.dispose(), officeApi.dispose(), lecturerApi.dispose()]);
});
