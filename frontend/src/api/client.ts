import type { AdjustmentSlot, AdjustmentScope, Batch, OfficialTimetable, Preview, Run } from "../types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = (payload as { detail?: unknown } | null)?.detail;
    const message = typeof detail === "string" ? detail : (detail as { message?: string } | null)?.message;
    throw new Error(message || "Máy chủ không thể xử lý yêu cầu. Vui lòng thử lại.");
  }
  return payload as T;
}

export const api = {
  health: () => request<{ status: string }>("/api/health"),
  batches: async () => (await request<{ batches: Batch[] }>("/api/batches")).batches,
  runs: async () => (await request<{ runs: Run[] }>("/api/ga/runs")).runs,
  run: (runCode: string) => request<Run>(`/api/ga/runs/${encodeURIComponent(runCode)}`),
  officialTimetables: async () => (await request<{ official_timetables: OfficialTimetable[] }>("/api/ga/official-timetables")).official_timetables,
  officialTimetable: (officialCode: string) => request<OfficialTimetable>(`/api/ga/official-timetables/${encodeURIComponent(officialCode)}`),
  publishRun: (runCode: string, note = "") => request<OfficialTimetable>(`/api/ga/runs/${encodeURIComponent(runCode)}/publish`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ note }) }),
  previewImport: (files: File[]) => {
    const form = new FormData(); files.forEach((file) => form.append("files", file, file.name));
    return request<Preview>("/api/imports/csv/preview", { method: "POST", body: form });
  },
  confirmImport: (files: File[], metadata: { displayName: string; semester: string; academicYear: string; note: string }) => {
    const form = new FormData(); files.forEach((file) => form.append("files", file, file.name));
    form.append("display_name", metadata.displayName); form.append("semester", metadata.semester); form.append("academic_year", metadata.academicYear); form.append("note", metadata.note);
    return request<{ batch: Batch }>("/api/imports/csv/confirm", { method: "POST", body: form });
  },
  startRun: (body: Record<string, number | string>) => request<Run>("/api/ga/runs/preview", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  adjustmentOptions: async (runCode: string, sectionCode: string, date: string) => {
    const result = await request<{ slots: AdjustmentSlot[] }>(`/api/ga/runs/${encodeURIComponent(runCode)}/occurrence-adjustment-options/${encodeURIComponent(sectionCode)}/${date}?target_date=${date}`);
    return result.slots;
  },
  adjustOfficial: (officialCode: string, body: { section_code: string; occurrence_date: string; room_code: string; slot_code: string; reason: string; scope: AdjustmentScope; effective_start_date?: string; effective_end_date?: string }) => request<{ message: string; official: OfficialTimetable }>(`/api/ga/official-timetables/${encodeURIComponent(officialCode)}/adjustments`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  createSegment: (officialCode: string, body: Record<string, string>) => request<{ message: string; official: OfficialTimetable }>(`/api/ga/official-timetables/${encodeURIComponent(officialCode)}/segments`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  createMakeup: (officialCode: string, body: Record<string, string>) => request<{ message: string; official: OfficialTimetable }>(`/api/ga/official-timetables/${encodeURIComponent(officialCode)}/makeups`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
};
