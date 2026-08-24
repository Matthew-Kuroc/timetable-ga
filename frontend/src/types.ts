export type UserRole = "ADMIN" | "TRAINING_OFFICE" | "LECTURER";

export interface AuthUser {
  id: number;
  username: string;
  display_name: string;
  role: UserRole;
  active: boolean;
  system_account?: boolean;
  lecturer_code?: string | null;
}

export interface LoginResponse {
  user: AuthUser;
  expires_at: string;
}

export interface AdminUser extends AuthUser {
  created_at?: string;
  updated_at?: string;
  last_login_at?: string | null;
}

export interface LecturerOption {
  lecturer_code: string;
  lecturer_name: string;
  account_username?: string | null;
  account_active?: boolean | null;
}

export interface UserWriteInput {
  username?: string;
  display_name?: string;
  password?: string;
  role?: UserRole;
  active?: boolean;
  lecturer_code?: string | null;
}

export interface AuditLog {
  id: number;
  action: string;
  actor_username?: string | null;
  target_user_id?: number | null;
  target_username?: string | null;
  old_value?: Record<string, unknown> | null;
  new_value?: Record<string, unknown> | null;
  created_at: string;
}

export type CourseType = "THEORY" | "PRACTICE" | "INTEGRATED";

export interface Assignment {
  section_code: string;
  meeting_number?: number;
  course_code: string;
  course_name: string;
  lecturer_code: string;
  lecturer_name: string;
  room_code: string;
  slot_code: string;
  day_of_week: number;
  start_period: number;
  end_period: number;
  course_type: CourseType;
  scheduling_student_count: number;
  required_sessions?: number;
  periods_per_session?: number;
  second_session_periods?: number | null;
}

export interface Occurrence {
  section_code: string;
  meeting_number?: number;
  date: string;
  room_code: string;
  slot_code: string;
  academic_week: number;
  status: string;
  original_missing_date?: string;
}

export interface SkippedHolidaySession extends Occurrence {
  holiday_name?: string;
  course_code?: string;
  course_name?: string;
  lecturer_code?: string;
  lecturer_name?: string;
  course_type?: CourseType;
}

export interface Run {
  run_code: string;
  status: string;
  created_at?: string;
  completed_at?: string;
  batch_code?: string;
  evaluation?: { hard_violation_count?: number; soft_cost?: number; soft_breakdown?: Record<string, number> };
  assignments: Assignment[];
  occurrences: Occurrence[];
  change_history?: ChangeHistory[];
  skipped_holiday_sessions?: SkippedHolidaySession[];
}

/** A published timetable is a separate, editable copy of an immutable GA run. */
export interface OfficialTimetable extends Run {
  official_code: string;
  source_run_code: string;
  published_at?: string;
  version_number?: number;
  segments?: ScheduleSegment[];
  makeup_sessions?: Occurrence[];
}

export interface ScheduleSegment {
  section_code: string;
  effective_start_date: string;
  effective_end_date: string;
  room_code: string;
  slot_code: string;
  reason?: string;
}

export type AdjustmentScope = "ONE_OCCURRENCE" | "DATE_RANGE" | "FROM_DATE_TO_END";

export interface ChangeHistory {
  section_code: string;
  occurrence_date?: string;
  changed_at: string;
  scope: string;
  reason?: string;
}

export interface Batch {
  batch_code: string;
  display_name: string;
  semester?: string;
  academic_year?: string;
  version_number?: number;
  created_at?: string;
  confirmed_at?: string;
  section_count?: number;
  status?: string;
  note?: string;
}
export interface CsvError { file?: string; row?: number; column?: string; value?: string; reason: string; }
export interface Preview { valid: boolean; files?: { file: string; row_count: number; headers?: string[] }[]; errors?: CsvError[]; }
export interface AdjustmentSlot { slot_code: string; day_of_week?: number; start_period: number; end_period: number; rooms: { room_code: string; room_name: string; capacity: number }[]; }

export interface LecturerCourseSection {
  section_code: string;
  course_code?: string;
  course_name?: string;
  course_type?: CourseType;
  required_sessions?: number;
  periods_per_session?: number;
  scheduling_student_count?: number;
  room_code?: string;
  slot_code?: string;
  day_of_week?: number;
  start_period?: number;
  end_period?: number;
  start_date?: string | null;
  end_date?: string | null;
}

export interface LecturerTimetableOccurrence extends Occurrence {
  course_code?: string;
  course_name?: string;
  lecturer_code?: string;
  lecturer_name?: string;
  day_of_week?: number;
  start_period?: number;
  end_period?: number;
  course_type?: CourseType;
}

export interface LecturerTimetable {
  official_code: string | null;
  academic_week: number;
  week_start_date?: string | null;
  week_end_date?: string | null;
  lecturer_code: string;
  lecturer_name: string;
  occurrences: LecturerTimetableOccurrence[];
  teaching_dates?: string[];
  course_sections: LecturerCourseSection[];
}

export type LecturerChangeRequestType =
  | "SUSPEND_ONE_OCCURRENCE"
  | "MOVE_ONE_OCCURRENCE";

export type LecturerChangeRequestStatus =
  | "PENDING"
  | "APPROVED"
  | "REJECTED"
  | "CANCELLED"
  | "APPLIED";

export interface ChangeRequestHardConflict {
  code: string;
  message: string;
}

export interface ChangeRequestValidation {
  valid: boolean;
  hard_conflicts: ChangeRequestHardConflict[];
  checked_at: string;
  official_code?: string;
  request_code?: string;
}

export interface ChangeRequestSnapshot {
  section_code?: string;
  occurrence_date?: string | null;
  date?: string | null;
  room_code?: string | null;
  slot_code?: string | null;
  status?: string;
  academic_week?: number;
  start_period?: number;
  end_period?: number;
  [key: string]: unknown;
}

export interface ChangeRequestEvent {
  id?: number;
  event_type?: string;
  action?: string;
  from_status?: LecturerChangeRequestStatus | null;
  to_status?: LecturerChangeRequestStatus | null;
  status?: LecturerChangeRequestStatus;
  actor_username?: string | null;
  actor_display_name?: string | null;
  note?: string | null;
  created_at: string;
}

export interface LecturerChangeRequest {
  request_code: string;
  official_code: string;
  requester_username: string;
  requester_display_name: string;
  section_code: string;
  request_type: LecturerChangeRequestType;
  occurrence_date: string;
  reason: string;
  proposed_date?: string | null;
  proposed_slot_code?: string | null;
  proposed_room_code?: string | null;
  current_snapshot?: ChangeRequestSnapshot | null;
  proposal_snapshot?: ChangeRequestSnapshot | null;
  status: LecturerChangeRequestStatus;
  reviewer_username?: string | null;
  reviewer_display_name?: string | null;
  review_note?: string | null;
  validation_result?: ChangeRequestValidation | null;
  created_at: string;
  updated_at: string;
  reviewed_at?: string | null;
  applied_at?: string | null;
  cancelled_at?: string | null;
  events: ChangeRequestEvent[];
}

export interface CreateLecturerChangeRequestInput {
  official_code: string;
  section_code: string;
  request_type: LecturerChangeRequestType;
  occurrence_date: string;
  reason: string;
  proposed_date?: string;
  proposed_slot_code?: string;
  proposed_room_code?: string;
}

export interface ChangeRequestListResponse {
  requests: LecturerChangeRequest[];
  total: number;
}
