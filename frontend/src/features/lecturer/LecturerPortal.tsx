import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { api } from "../../api/client";

import { LecturerRequestCreatePage } from "../lecturer-requests/LecturerRequestCreatePage";
import { LecturerRequestHistoryPage } from "../lecturer-requests/LecturerRequestHistoryPage";

import { PortalLayout } from "../../layouts/PortalLayout";

import type {
  AuthUser,
  LecturerCourseSection,
  LecturerTimetable,
  LecturerTimetableOccurrence,
} from "../../types";

interface Props {
  user: AuthUser;
  path: string;
  onNavigate: (path: string) => void;
  onLogout: () => void | Promise<void>;
}

const navigation = [
  {
    path: "/lecturer/timetable",
    label: "Lịch giảng dạy",
  },
  {
    path: "/lecturer/course-sections",
    label: "Lớp học phần",
  },
  {
    path: "/lecturer/requests/new",
    label: "Yêu cầu đổi lịch",
  },
  {
    path: "/lecturer/requests",
    label: "Yêu cầu đã gửi",
  },
];

const days = [
  {
    code: 2,
    label: "Thứ Hai",
  },
  {
    code: 3,
    label: "Thứ Ba",
  },
  {
    code: 4,
    label: "Thứ Tư",
  },
  {
    code: 5,
    label: "Thứ Năm",
  },
  {
    code: 6,
    label: "Thứ Sáu",
  },
  {
    code: 7,
    label: "Thứ Bảy",
  },
  {
    code: 8,
    label: "Chủ nhật",
  },
];


export function LecturerPortal({
  user,
  path,
  onNavigate,
  onLogout,
}: Props) {
  const [week, setWeek] = useState(1);

  const [data, setData] =
    useState<LecturerTimetable | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [pendingRequests, setPendingRequests] =
    useState(0);

  const sectionsPage =
    path === "/lecturer/course-sections";

  const createRequestPage =
    path === "/lecturer/requests/new";

  const requestHistoryPage =
    path === "/lecturer/requests";

  const needsTimetable =
    path === "/lecturer/timetable" ||
    sectionsPage;


  const loadTimetable =
    useCallback(async () => {
      setLoading(true);
      setError(null);

      try {
        const result =
          await api.lecturerTimetable(
            week
          );

        setData(result);
      } catch (cause) {
        setError(
          cause instanceof Error
            ? cause.message
            : "Không thể tải lịch giảng dạy."
        );
      } finally {
        setLoading(false);
      }
    }, [week]);

  useEffect(() => {
    if (needsTimetable) {
      void loadTimetable();
    }
  }, [
    loadTimetable,
    needsTimetable,
  ]);


  useEffect(() => {
    if (
      path !== "/lecturer/timetable"
    ) {
      return;
    }

    void api
      .lecturerChangeRequests()
      .then((result) => {
        const count =
          result.requests.filter(
            (request) =>
              request.status ===
              "PENDING"
          ).length;

        setPendingRequests(count);
      })
      .catch(() => {
        setPendingRequests(0);
      });
  }, [path]);



  const pageCopy =
    createRequestPage
      ? {
          title:
            "Gửi yêu cầu điều chỉnh lịch",
          description:
            "Đề nghị tạm ngưng hoặc chuyển một buổi dạy thuộc lịch của bạn.",
        }
      : requestHistoryPage
        ? {
            title:
              "Yêu cầu đã gửi",
            description:
              "Theo dõi trạng thái và kết quả xử lý yêu cầu.",
          }
        : sectionsPage
          ? {
              title:
                "Lớp học phần được phân công",
              description:
                "Chỉ hiển thị các lớp thuộc giảng viên đang đăng nhập.",
            }
          : {
              title:
                "Lịch giảng dạy của tôi",
              description:
                "Theo dõi lịch cá nhân theo tuần. Bấm vào buổi học để xem chi tiết.",
            };

  return (
    <PortalLayout
      user={user}
      navigation={navigation}
      currentPath={path}
      onNavigate={onNavigate}
      onLogout={onLogout}
      eyebrow="Cổng Giảng viên"
      title={pageCopy.title}
      description={
        pageCopy.description
      }
    >
      {}
      {needsTimetable &&
        error && (
          <div className="alert error">
            <span>{error}</span>

            <button
              type="button"
              className="secondary"
              onClick={() =>
                void loadTimetable()
              }
            >
              Thử lại
            </button>
          </div>
        )}

      {}
      {createRequestPage ? (
        <LecturerRequestCreatePage
          onNavigateHistory={() =>
            onNavigate(
              "/lecturer/requests"
            )
          }
        />
      ) : requestHistoryPage ? (

        <LecturerRequestHistoryPage
          onCreateRequest={() =>
            onNavigate(
              "/lecturer/requests/new"
            )
          }
        />
      ) : sectionsPage ? (
      

        <AssignedSections
          loading={loading}
          sections={
            data?.course_sections ||
            []
          }
        />
      ) : (
       

        <WeeklyTimetable
          loading={loading}
          data={data}
          week={week}
          pending={
            pendingRequests
          }
          setWeek={setWeek}
          onRequest={() =>
            onNavigate(
              "/lecturer/requests/new"
            )
          }
        />
      )}
    </PortalLayout>
  );
}


function WeeklyTimetable({
  loading,
  data,
  week,
  pending,
  setWeek,
  onRequest,
}: {
  loading: boolean;
  data: LecturerTimetable | null;
  week: number;
  pending: number;
  setWeek: (week: number) => void;
  onRequest: () => void;
}) {
  const [
    selectedOccurrence,
    setSelectedOccurrence,
  ] =
    useState<LecturerTimetableOccurrence | null>(
      null
    );



  const periodRows =
    useMemo(() => {
      const result =
        new Map<
          string,
          {
            start: number;
            end: number;
          }
        >();

      [
        ...(data?.course_sections ||
          []),
        ...(data?.occurrences || []),
      ].forEach((item) => {
        if (
          item.start_period &&
          item.end_period
        ) {
          result.set(
            `${item.start_period}-${item.end_period}`,
            {
              start:
                item.start_period,
              end:
                item.end_period,
            }
          );
        }
      });

      return [
        ...result.values(),
      ].sort(
        (a, b) =>
          a.start - b.start ||
          a.end - b.end
      );
    }, [data]);


  const occurrenceMap =
    useMemo(() => {
      const map =
        new Map<
          string,
          LecturerTimetableOccurrence[]
        >();

      (
        data?.occurrences || []
      ).forEach((item) => {
        const day =
          item.day_of_week ||
          dayFromDate(item.date);

        const key = `${day}-${item.start_period || 0}-${item.end_period || 0}`;

        map.set(key, [
          ...(map.get(key) || []),
          item,
        ]);
      });

      return map;
    }, [data]);

 

  const dates =
    useMemo(
      () =>
        getWeekDates(
          data?.occurrences || []
        ),
      [data]
    );

 

  const totalPeriods =
    (
      data?.occurrences || []
    ).reduce(
      (total, occurrence) => {
        if (
          occurrence.start_period &&
          occurrence.end_period
        ) {
          return (
            total +
            occurrence.end_period -
            occurrence.start_period +
            1
          );
        }

        return total;
      },
      0
    );

  return (
    <>
      {}

      <div className="lecturer-action">
        <button
          type="button"
          className="secondary"
          onClick={onRequest}
        >
          + Gửi yêu cầu đổi lịch
        </button>
      </div>

      {}

      <section className="lecturer-stats">
        <StatCard
          label="Tuần học"
          value={String(
            week
          ).padStart(2, "0")}
          note={dateRange(dates)}
        />

        <StatCard
          label="Số buổi"
          value={String(
            data?.occurrences
              .length || 0
          )}
          note={`${totalPeriods} tiết giảng dạy`}
        />

        <StatCard
          label="Lớp phụ trách"
          value={String(
            data?.course_sections
              .length || 0
          )}
          note={
            data?.lecturer_code ||
            "Giảng viên hiện tại"
          }
        />

        <StatCard
          label="Yêu cầu chờ duyệt"
          value={String(pending)}
          note="Theo dõi tại Yêu cầu đã gửi"
        />
      </section>

      {}

      <section className="panel calendar-toolbar">
        <div>
          <h2>
            Tuần{" "}
            {String(
              week
            ).padStart(2, "0")}
          </h2>

          <p>
            {data?.official_code
              ? `Lịch chính thức ${data.official_code}`
              : "Chưa có lịch chính thức được công bố."}
          </p>
        </div>

        <div className="calendar-toolbar-actions">
          <button
            type="button"
            className="secondary"
            disabled={week <= 1}
            onClick={() =>
              setWeek(
                Math.max(
                  1,
                  week - 1
                )
              )
            }
          >
            ‹ Tuần trước
          </button>

          <label className="week-picker">
            <span>Tuần</span>

            <input
              type="number"
              min="1"
              max="53"
              value={week}
              onChange={(event) => {
                const value =
                  Number(
                    event.target.value
                  ) || 1;

                setWeek(
                  Math.min(
                    53,
                    Math.max(
                      1,
                      value
                    )
                  )
                );
              }}
            />
          </label>

          <button
            type="button"
            className="secondary"
            disabled={week >= 53}
            onClick={() =>
              setWeek(
                Math.min(
                  53,
                  week + 1
                )
              )
            }
          >
            Tuần sau ›
          </button>
        </div>
      </section>

      {}

      {loading ? (
        <div className="calendar-state">
          <span className="loading-ring" />

          <span>
            Đang tải lịch giảng
            dạy...
          </span>
        </div>
      ) : !data?.occurrences
          .length ? (
       

        <div className="calendar-state">
          <strong>
            Tuần này chưa có lịch
            giảng dạy
          </strong>

          <p>
            Không có buổi học nào
            thuộc giảng viên hiện tại.
          </p>
        </div>
      ) : (
        <>
          {}

          <div className="calendar-grid-wrap">
            <div className="calendar-grid">
              {}
              <div className="calendar-day-head blank" />

              {}
              {days.map((day) => (
                <div
                  key={day.code}
                  className={`calendar-day-head ${
                    isToday(
                      dates.get(
                        day.code
                      )
                    )
                      ? "today"
                      : ""
                  }`}
                >
                  <strong>
                    {day.label}
                  </strong>

                  <span>
                    {shortDate(
                      dates.get(
                        day.code
                      )
                    )}
                  </span>

                  {isToday(
                    dates.get(
                      day.code
                    )
                  ) && (
                    <em>Hôm nay</em>
                  )}
                </div>
              ))}

              {}
              {periodRows.map(
                (row) => (
                  <CalendarRow
                    key={`${row.start}-${row.end}`}
                    row={row}
                    dates={dates}
                    occurrenceMap={
                      occurrenceMap
                    }
                    onSelect={
                      setSelectedOccurrence
                    }
                  />
                )
              )}
            </div>
          </div>

          {}
          <div className="calendar-legend">
            <span>
              <i className="dot theory" />
              Lý thuyết
            </span>

            <span>
              <i className="dot practice" />
              Thực hành
            </span>

            <span>
              <i className="dot adjusted" />
              Đã điều chỉnh
            </span>

            <span>
              <i className="dot makeup" />
              Học bù
            </span>
          </div>
        </>
      )}

      {}

      {selectedOccurrence && (
        <div
          className="modal-backdrop"
          onMouseDown={(event) => {
            if (
              event.currentTarget ===
              event.target
            ) {
              setSelectedOccurrence(
                null
              );
            }
          }}
        >
          <section className="modal session-modal">
            <button
              type="button"
              className="close"
              onClick={() =>
                setSelectedOccurrence(
                  null
                )
              }
            >
              ×
            </button>

            <p className="eyebrow">
              Chi tiết buổi học
            </p>

            <h2>
              {selectedOccurrence.course_name ||
                selectedOccurrence.section_code}
            </h2>

            <p className="session-code">
              {
                selectedOccurrence.section_code
              }

              {selectedOccurrence.course_code
                ? ` · ${selectedOccurrence.course_code}`
                : ""}
            </p>

            <dl className="session-detail">
              <div>
                <dt>Ngày học</dt>

                <dd>
                  {formatDate(
                    selectedOccurrence.date
                  )}
                </dd>
              </div>

              <div>
                <dt>Tiết học</dt>

                <dd>
                  {periodLabel(
                    selectedOccurrence
                  )}
                </dd>
              </div>

              <div>
                <dt>Phòng</dt>

                <dd>
                  {selectedOccurrence.room_code ||
                    "Chưa xếp"}
                </dd>
              </div>

              <div>
                <dt>Trạng thái</dt>

                <dd>
                  {statusLabel(
                    selectedOccurrence.status
                  )}
                </dd>
              </div>

              <div>
                <dt>Tuần học</dt>

                <dd>
                  Tuần{" "}
                  {selectedOccurrence.academic_week ||
                    week}
                </dd>
              </div>

              <div>
                <dt>Loại lớp</dt>

                <dd>
                  {courseTypeLabel(
                    selectedOccurrence.course_type ||
                      ""
                  )}
                </dd>
              </div>
            </dl>

            <div className="permission-note">
              Giảng viên chỉ xem
              lịch cá nhân. Muốn thay
              đổi lịch, hãy gửi yêu
              cầu để Phòng Đào tạo
              xử lý.
            </div>

            <div className="modal-actions">
              <button
                type="button"
                className="secondary"
                onClick={() =>
                  setSelectedOccurrence(
                    null
                  )
                }
              >
                Đóng
              </button>

              <button
                type="button"
                onClick={() => {
                  setSelectedOccurrence(
                    null
                  );

                  onRequest();
                }}
              >
                Gửi yêu cầu đổi lịch
              </button>
            </div>
          </section>
        </div>
      )}
    </>
  );
}

function CalendarRow({
  row,
  dates,
  occurrenceMap,
  onSelect,
}: {
  row: {
    start: number;
    end: number;
  };

  dates: Map<number, string>;

  occurrenceMap: Map<
    string,
    LecturerTimetableOccurrence[]
  >;

  onSelect: (
    occurrence: LecturerTimetableOccurrence
  ) => void;
}) {
  return (
    <>
      {}
      <div className="calendar-period">
        <strong>
          Tiết {row.start}–
          {row.end}
        </strong>

        <span>
          {row.end -
            row.start +
            1}{" "}
          tiết
        </span>
      </div>

      {}
      {days.map((day) => {
        const key = `${day.code}-${row.start}-${row.end}`;

        const occurrences =
          occurrenceMap.get(key) ||
          [];

        return (
          <div
            key={key}
            className={`calendar-cell ${
              isToday(
                dates.get(day.code)
              )
                ? "today-col"
                : ""
            }`}
          >
            {occurrences.map(
              (occurrence) => (
                <button
                  type="button"
                  key={`${occurrence.section_code}-${occurrence.date}-${occurrence.slot_code}`}
                  className={`calendar-event ${eventClass(
                    occurrence
                  )}`}
                  onClick={() =>
                    onSelect(
                      occurrence
                    )
                  }
                >
                  <strong>
                    {occurrence.course_name ||
                      occurrence.section_code}
                  </strong>

                  <small>
                    {
                      occurrence.section_code
                    }

                    {occurrence.course_code
                      ? ` · ${occurrence.course_code}`
                      : ""}
                  </small>

                  <span>
                    📍{" "}
                    {occurrence.room_code ||
                      "Chưa xếp"}
                  </span>
                </button>
              )
            )}
          </div>
        );
      })}
    </>
  );
}



function StatCard({
  label,
  value,
  note,
}: {
  label: string;
  value: string;
  note: string;
}) {
  return (
    <article className="lecturer-stat-card">
      <small>{label}</small>

      <strong>{value}</strong>

      <span>{note}</span>
    </article>
  );
}



function AssignedSections({
  loading,
  sections,
}: {
  loading: boolean;
  sections: LecturerCourseSection[];
}) {
  if (loading) {
    return (
      <div className="calendar-state">
        <span className="loading-ring" />

        <span>Đang tải lớp học phần...</span>
      </div>
    );
  }

  if (!sections.length) {
    return (
      <div className="calendar-state">
        Chưa có lớp học phần nào được phân công.
      </div>
    );
  }

  const theorySections = sections.filter(
    (section) =>
      section.course_type === "THEORY"
  );

  const practiceSections = sections.filter(
    (section) =>
      section.course_type === "PRACTICE" ||
      section.course_type === "INTEGRATED"
  );

  return (
    <div className="assigned-section-groups">
      {}
      <section className="assigned-group">
        <div className="assigned-group-heading">
          <div>
            <p className="eyebrow">
              Nhóm lớp
            </p>

            <h2>Lý thuyết</h2>
          </div>

          <span className="assigned-count">
            {theorySections.length} lớp
          </span>
        </div>

        <div className="section-card-grid compact">
          {theorySections.length ? (
            theorySections.map((section) => (
              <SectionCard
                key={section.section_code}
                section={section}
              />
            ))
          ) : (
            <div className="assigned-empty">
              Không có lớp lý thuyết.
            </div>
          )}
        </div>
      </section>

      {}
      <section className="assigned-group">
        <div className="assigned-group-heading">
          <div>
            <p className="eyebrow">
              Nhóm lớp
            </p>

            <h2>Thực hành</h2>
          </div>

          <span className="assigned-count">
            {practiceSections.length} lớp
          </span>
        </div>

        <div className="section-card-grid compact">
          {practiceSections.length ? (
            practiceSections.map((section) => (
              <SectionCard
                key={section.section_code}
                section={section}
              />
            ))
          ) : (
            <div className="assigned-empty">
              Không có lớp thực hành.
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
function SectionCard({
  section,
}: {
  section: LecturerCourseSection;
}) {
  return (
    <article className="course-section-row">
      <div className="course-row-code">
        <span>{section.course_code}</span>
        <strong>
          {section.course_name ||
            section.section_code}
        </strong>
        <small>{section.section_code}</small>
      </div>

      <div className="course-row-item">
        <span>Loại lớp</span>
        <strong>
          {section.course_type
            ? courseTypeLabel(section.course_type)
            : "—"}
        </strong>
      </div>

      <div className="course-row-item">
        <span>Lịch học</span>
        <strong>
          {section.day_of_week
            ? `${dayLabel(
                section.day_of_week
              )}, ${periodLabel(section)}`
            : "Chưa có lịch"}
        </strong>
      </div>

      <div className="course-row-item">
        <span>Phòng</span>
        <strong>
          {section.room_code || "Chưa xếp"}
        </strong>
      </div>

      <div className="course-row-item">
        <span>Sĩ số</span>
        <strong>
          {section.scheduling_student_count ??
            "—"}{" "}
          SV
        </strong>
      </div>
    </article>
  );
}

function getWeekDates(
  occurrences: LecturerTimetableOccurrence[]
) {
  const result =
    new Map<number, string>();

  const anchor =
    occurrences.find(
      (item) => item.date
    );

  if (!anchor) {
    return result;
  }

  const anchorDay =
    anchor.day_of_week ||
    dayFromDate(anchor.date);

  const anchorDate =
    new Date(
      `${anchor.date.slice(
        0,
        10
      )}T00:00:00`
    );

  days.forEach((day) => {
    const date =
      new Date(anchorDate);

    date.setDate(
      anchorDate.getDate() +
        day.code -
        anchorDay
    );

    result.set(
      day.code,
      isoDate(date)
    );
  });

  return result;
}

/* YYYY-MM-DD */
function isoDate(date: Date) {
  return `${date.getFullYear()}-${String(
    date.getMonth() + 1
  ).padStart(2, "0")}-${String(
    date.getDate()
  ).padStart(2, "0")}`;
}

function isToday(
  value?: string
) {
  return (
    !!value &&
    value === isoDate(new Date())
  );
}

function shortDate(
  value?: string
) {
  if (!value) {
    return "—";
  }

  const [
    year,
    month,
    day,
  ] = value.split("-");

  return `${day}/${month}/${year}`;
}

function dateRange(
  map: Map<number, string>
) {
  const monday =
    map.get(2);

  const sunday =
    map.get(8);

  if (
    monday &&
    sunday
  ) {
    return `${shortDate(
      monday
    )} – ${shortDate(
      sunday
    )}`;
  }

  return "Theo lịch học kỳ";
}

function dayFromDate(
  value: string
) {
  const day =
    new Date(
      `${value.slice(
        0,
        10
      )}T00:00:00`
    ).getDay();

 

  return day === 0
    ? 8
    : day + 1;
}

function dayLabel(
  code: number
) {
  return (
    days.find(
      (day) =>
        day.code === code
    )?.label ||
    `Ngày ${code}`
  );
}

function periodLabel(
  item: {
    start_period?: number;
    end_period?: number;
    slot_code?: string;
  }
) {
  if (
    item.start_period &&
    item.end_period
  ) {
    return `Tiết ${item.start_period}–${item.end_period}`;
  }

  return (
    item.slot_code ||
    "Chưa xếp"
  );
}

function statusLabel(
  status: string
) {
  const labels: Record<
    string,
    string
  > = {
    SCHEDULED:
      "Bình thường",

    NORMAL:
      "Bình thường",

    MAKEUP:
      "Học bù",

    MOVED:
      "Đã chuyển",

    ADJUSTED:
      "Đã điều chỉnh",

    SEGMENT:
      "Theo phân đoạn",

    EXCEPTION:
      "Ngoại lệ một buổi",

    SUSPENDED:
      "Tạm ngưng",
  };

  return (
    labels[status] ||
    "Buổi học"
  );
}

function courseTypeLabel(
  type: string
) {
  const labels: Record<
    string,
    string
  > = {
    THEORY:
      "Lý thuyết",

    PRACTICE:
      "Thực hành",

    INTEGRATED:
      "Lý thuyết – thực hành",
  };

  return (
    labels[type] ||
    "Lớp học phần"
  );
}

function eventClass(
  occurrence: LecturerTimetableOccurrence
) {
  if (
    occurrence.status ===
    "MAKEUP"
  ) {
    return "makeup";
  }

  if (
    [
      "MOVED",
      "ADJUSTED",
      "SEGMENT",
      "EXCEPTION",
    ].includes(
      occurrence.status
    )
  ) {
    return "adjusted";
  }

  if (
    occurrence.course_type ===
    "PRACTICE"
  ) {
    return "practice";
  }

  return "theory";
}

function formatDate(
  value: string
) {
  return new Intl.DateTimeFormat(
    "vi-VN"
  ).format(
    new Date(
      `${value.slice(
        0,
        10
      )}T00:00:00`
    )
  );
}
