export type CourseType = "THEORY" | "PRACTICE" | "INTEGRATED";

export interface Assignment {
  section_code: string;
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
}

export interface Occurrence {
  section_code: string;
  date: string;
  room_code: string;
  slot_code: string;
  academic_week: number;
  status: string;
  original_missing_date?: string;
}

export interface SkippedHolidaySession extends Occurrence {
  holiday_name?: string;
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
export interface AdjustmentSlot { slot_code: string; start_period: number; end_period: number; rooms: { room_code: string; room_name: string; capacity: number }[]; }
