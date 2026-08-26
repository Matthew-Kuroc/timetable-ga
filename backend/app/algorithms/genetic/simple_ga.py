from __future__ import annotations

import random
import time
from dataclasses import dataclass
from collections.abc import Callable

from backend.app.algorithms.genetic.soft_constraints import (
    SoftConstraintWeights,
    score_soft_constraints,
)
from backend.app.domain.models import (
    FeasibleAssignmentDomain,
    HardConstraintViolation,
    ScheduleAssignment,
    TimetableInputData,
)
from backend.app.scheduling.feasible_assignments import (
    FeasibleDomainBuildStopped,
    build_feasible_assignment_domains,
    find_sections_without_feasible_assignments,
)
from backend.app.scheduling.hard_constraints import check_hard_constraints


@dataclass(frozen=True)
class GeneticAlgorithmConfig:
    population_size: int = 50
    generations: int = 100
    seed: int | None = None
    crossover_rate: float = 0.8
    mutation_rate: float = 0.1
    elite_count: int = 2
    tournament_size: int = 3
    target_soft_cost: float | None = None
    soft_weights: SoftConstraintWeights = SoftConstraintWeights()
    time_limit_seconds: float | None = None
    progress_callback: Callable[[int, int, "TimetableCandidate"], None] | None = None
    cancellation_callback: Callable[[], bool] | None = None


@dataclass(frozen=True)
class CandidateEvaluation:
    hard_violation_count: int
    hard_violations: tuple[HardConstraintViolation, ...]
    soft_cost: float
    soft_breakdown: dict[str, float]
    total_cost: float


@dataclass(frozen=True)
class TimetableCandidate:
    assignments: tuple[ScheduleAssignment, ...]
    evaluation: CandidateEvaluation


@dataclass(frozen=True)
class GeneticAlgorithmResult:
    status: str
    best_candidate: TimetableCandidate | None
    generation_count: int
    seed: int | None
    stop_reason: str
    execution_time_seconds: float
    diagnostics: tuple[str, ...]
    fitness_history: tuple[CandidateEvaluation, ...] = ()


def run_simple_genetic_algorithm(
    input_data: TimetableInputData,
    config: GeneticAlgorithmConfig,
) -> GeneticAlgorithmResult:
    started_at = time.perf_counter()
    config_errors = _validate_config(input_data, config)
    if config_errors:
        return GeneticAlgorithmResult(
            status="FAILED",
            best_candidate=None,
            generation_count=0,
            seed=config.seed,
            stop_reason="INVALID_CONFIGURATION",
            execution_time_seconds=time.perf_counter() - started_at,
            diagnostics=tuple(config_errors),
        )

    deadline = started_at + config.time_limit_seconds if config.time_limit_seconds is not None else None
    try:
        domains = build_feasible_assignment_domains(
            input_data,
            should_stop=lambda: (config.cancellation_callback is not None and config.cancellation_callback()) or (deadline is not None and time.perf_counter() >= deadline),
        )
    except FeasibleDomainBuildStopped:
        return GeneticAlgorithmResult(
            status="STOPPED",
            best_candidate=None,
            generation_count=0,
            seed=config.seed,
            stop_reason="CANCELLED" if config.cancellation_callback is not None and config.cancellation_callback() else "TIME_LIMIT",
            execution_time_seconds=time.perf_counter() - started_at,
            diagnostics=("Run đã dừng trong khi xây dựng miền khả thi.",),
        )
    sections_without_domain = find_sections_without_feasible_assignments(domains)
    if sections_without_domain:
        return GeneticAlgorithmResult(
            status="FAILED",
            best_candidate=None,
            generation_count=0,
            seed=config.seed,
            stop_reason="NO_FEASIBLE_ASSIGNMENT_DOMAIN",
            execution_time_seconds=time.perf_counter() - started_at,
            diagnostics=tuple(
                f"Lớp {section_code} không có tổ hợp phòng và khung giờ hợp lệ."
                for section_code in sections_without_domain
            ),
        )

    ordered_domains = tuple(sorted(domains, key=lambda domain: domain.section_code))
    assignment_domains = _build_assignment_domain_index(ordered_domains)
    rng = random.Random(config.seed)
    population = [
        _evaluate_candidate(
            input_data,
            _greedy_assignments(input_data, ordered_domains, config.soft_weights, rng, random_window=5),
            config.soft_weights,
        )
        for _ in range(max(1, config.population_size // 2))
    ]
    while len(population) < config.population_size:
        population.append(
            _evaluate_candidate(input_data, _random_assignments(ordered_domains, rng), config.soft_weights)
        )
    best_candidate = min(population, key=_candidate_sort_key)
    generation_count = 0
    history: list[CandidateEvaluation] = []

    for generation in range(1, config.generations + 1):
        generation_count = generation
        population = sorted(population, key=_candidate_sort_key)
        if _is_better(population[0], best_candidate):
            best_candidate = population[0]
        history.append(best_candidate.evaluation)
        if config.progress_callback is not None:
            config.progress_callback(generation, config.generations, best_candidate)

        if _target_reached(best_candidate, config):
            return GeneticAlgorithmResult(
                status="COMPLETED",
                best_candidate=best_candidate,
                generation_count=generation_count,
                seed=config.seed,
                stop_reason="TARGET_SOFT_COST_REACHED",
                execution_time_seconds=time.perf_counter() - started_at,
                diagnostics=(),
                fitness_history=tuple(history),
            )

        if config.cancellation_callback is not None and config.cancellation_callback():
            return GeneticAlgorithmResult(
                status="STOPPED",
                best_candidate=best_candidate,
                generation_count=generation_count,
                seed=config.seed,
                stop_reason="CANCELLED",
                execution_time_seconds=time.perf_counter() - started_at,
                diagnostics=("Run đã được yêu cầu dừng; kết quả tốt nhất đã được giữ lại.",),
                fitness_history=tuple(history),
            )
        if config.time_limit_seconds is not None and time.perf_counter() - started_at >= config.time_limit_seconds:
            return GeneticAlgorithmResult(
                status="STOPPED",
                best_candidate=best_candidate,
                generation_count=generation_count,
                seed=config.seed,
                stop_reason="TIME_LIMIT",
                execution_time_seconds=time.perf_counter() - started_at,
                diagnostics=("Đã đạt giới hạn thời gian; kết quả tốt nhất đã được giữ lại.",),
                fitness_history=tuple(history),
            )

        population = _next_generation(input_data, population, assignment_domains, config, rng)

    return GeneticAlgorithmResult(
        status="COMPLETED",
        best_candidate=best_candidate,
        generation_count=generation_count,
        seed=config.seed,
        stop_reason="MAX_GENERATIONS",
        execution_time_seconds=time.perf_counter() - started_at,
        diagnostics=(),
        fitness_history=tuple(history),
    )


def _evaluate_candidate(
    input_data: TimetableInputData,
    assignments: tuple[ScheduleAssignment, ...],
    weights: SoftConstraintWeights,
) -> TimetableCandidate:
    hard_violations = check_hard_constraints(input_data, assignments)
    soft_breakdown = score_soft_constraints(input_data, assignments, weights)
    soft_cost = sum(soft_breakdown.values())
    evaluation = CandidateEvaluation(
        hard_violation_count=len(hard_violations),
        hard_violations=hard_violations,
        soft_cost=soft_cost,
        soft_breakdown=soft_breakdown,
        total_cost=float(len(hard_violations)) + soft_cost,
    )
    return TimetableCandidate(assignments=assignments, evaluation=evaluation)


def _is_better(candidate: TimetableCandidate, current_best: TimetableCandidate) -> bool:
    return _candidate_sort_key(candidate) < _candidate_sort_key(current_best)


def _candidate_sort_key(candidate: TimetableCandidate) -> tuple[int, float, tuple[tuple[str, int, str, str], ...]]:
    stable_assignments = tuple(
        sorted(
            (assignment.section_code, assignment.meeting_number, assignment.slot_code, assignment.room_code)
            for assignment in candidate.assignments
        )
    )
    return (
        candidate.evaluation.hard_violation_count,
        candidate.evaluation.soft_cost,
        stable_assignments,
    )


def _target_reached(candidate: TimetableCandidate, config: GeneticAlgorithmConfig) -> bool:
    return (
        config.target_soft_cost is not None
        and candidate.evaluation.hard_violation_count == 0
        and candidate.evaluation.soft_cost <= config.target_soft_cost
    )


def _build_assignment_domain_index(
    ordered_domains: tuple[FeasibleAssignmentDomain, ...],
) -> dict[tuple[str, int], tuple[ScheduleAssignment, ...]]:
    return {
        (domain.section_code, domain.meeting_number): tuple(
            sorted(
                domain.assignments,
                key=lambda assignment: (assignment.section_code, assignment.meeting_number, assignment.slot_code, assignment.room_code),
            )
        )
        for domain in ordered_domains
    }


def _random_assignments(
    ordered_domains: tuple[FeasibleAssignmentDomain, ...],
    rng: random.Random,
) -> tuple[ScheduleAssignment, ...]:
    return tuple(
        rng.choice(
            tuple(
                sorted(
                    domain.assignments,
                    key=lambda assignment: (assignment.section_code, assignment.meeting_number, assignment.slot_code, assignment.room_code),
                )
            )
        )
        for domain in ordered_domains
    )


def _greedy_assignments(
    input_data: TimetableInputData,
    ordered_domains: tuple[FeasibleAssignmentDomain, ...],
    weights: SoftConstraintWeights,
    rng: random.Random,
    random_window: int,
) -> tuple[ScheduleAssignment, ...]:
    assignments: list[ScheduleAssignment] = []
    lecturer_day_ranges: dict[tuple[str, int], list[tuple[int, int]]] = {}
    room_day_ranges: dict[tuple[str, int], list[tuple[int, int]]] = {}
    domains_by_difficulty = sorted(ordered_domains, key=lambda domain: (len(domain.assignments), domain.section_code))

    for domain in domains_by_difficulty:
        ranked_assignments = sorted(
            domain.assignments,
            key=lambda assignment: (
                sum(score_soft_constraints(input_data, (assignment,), weights).values()),
                assignment.slot_code,
                assignment.room_code,
            ),
        )
        non_conflicting = [
            assignment
            for assignment in ranked_assignments
            if not _has_global_conflict(input_data, assignment, lecturer_day_ranges, room_day_ranges)
        ]
        if non_conflicting:
            window = non_conflicting[: max(1, min(random_window, len(non_conflicting)))]
            selected = rng.choice(window)
        else:
            selected = rng.choice(tuple(ranked_assignments))
        assignments.append(selected)
        _record_assignment(input_data, selected, lecturer_day_ranges, room_day_ranges)

    return tuple(sorted(assignments, key=lambda assignment: assignment.section_code))


def _has_global_conflict(
    input_data: TimetableInputData,
    assignment: ScheduleAssignment,
    lecturer_day_ranges: dict[tuple[str, int], list[tuple[int, int]]],
    room_day_ranges: dict[tuple[str, int], list[tuple[int, int]]],
) -> bool:
    section = input_data.course_sections[assignment.section_code]
    slot = input_data.time_slots[assignment.slot_code]
    current_range = (slot.start_period, slot.end_period)
    lecturer_key = (section.lecturer_code, slot.day_of_week)
    room_key = (assignment.room_code, slot.day_of_week)
    return (
        _range_conflicts(current_range, lecturer_day_ranges.get(lecturer_key, []))
        or _range_conflicts(current_range, room_day_ranges.get(room_key, []))
    )


def _record_assignment(
    input_data: TimetableInputData,
    assignment: ScheduleAssignment,
    lecturer_day_ranges: dict[tuple[str, int], list[tuple[int, int]]],
    room_day_ranges: dict[tuple[str, int], list[tuple[int, int]]],
) -> None:
    section = input_data.course_sections[assignment.section_code]
    slot = input_data.time_slots[assignment.slot_code]
    current_range = (slot.start_period, slot.end_period)
    lecturer_day_ranges.setdefault((section.lecturer_code, slot.day_of_week), []).append(current_range)
    room_day_ranges.setdefault((assignment.room_code, slot.day_of_week), []).append(current_range)


def _range_conflicts(current_range: tuple[int, int], existing_ranges: list[tuple[int, int]]) -> bool:
    start, end = current_range
    return any(start <= existing_end and existing_start <= end for existing_start, existing_end in existing_ranges)


def _next_generation(
    input_data: TimetableInputData,
    population: list[TimetableCandidate],
    assignment_domains: dict[tuple[str, int], tuple[ScheduleAssignment, ...]],
    config: GeneticAlgorithmConfig,
    rng: random.Random,
) -> list[TimetableCandidate]:
    sorted_population = sorted(population, key=_candidate_sort_key)
    elite_count = min(config.elite_count, len(sorted_population))
    next_population = sorted_population[:elite_count]

    while len(next_population) < config.population_size:
        first_parent = _tournament_select(sorted_population, config.tournament_size, rng)
        second_parent = _tournament_select(sorted_population, config.tournament_size, rng)
        assignments = _crossover(first_parent.assignments, second_parent.assignments, config.crossover_rate, rng)
        assignments = _mutate(assignments, assignment_domains, config.mutation_rate, rng)
        next_population.append(_evaluate_candidate(input_data, assignments, config.soft_weights))
    return next_population


def _tournament_select(
    population: list[TimetableCandidate],
    tournament_size: int,
    rng: random.Random,
) -> TimetableCandidate:
    contenders = [rng.choice(population) for _ in range(tournament_size)]
    return min(contenders, key=_candidate_sort_key)


def _crossover(
    first_parent: tuple[ScheduleAssignment, ...],
    second_parent: tuple[ScheduleAssignment, ...],
    crossover_rate: float,
    rng: random.Random,
) -> tuple[ScheduleAssignment, ...]:
    first_by_section = {(assignment.section_code, assignment.meeting_number): assignment for assignment in first_parent}
    second_by_section = {(assignment.section_code, assignment.meeting_number): assignment for assignment in second_parent}
    section_order = sorted(first_by_section)
    if rng.random() >= crossover_rate:
        return tuple(first_by_section[section_code] for section_code in section_order)
    return tuple(
        (first_by_section if rng.random() < 0.5 else second_by_section)[section_code]
        for section_code in section_order
    )


def _mutate(
    assignments: tuple[ScheduleAssignment, ...],
    assignment_domains: dict[tuple[str, int], tuple[ScheduleAssignment, ...]],
    mutation_rate: float,
    rng: random.Random,
) -> tuple[ScheduleAssignment, ...]:
    mutated: list[ScheduleAssignment] = []
    for assignment in assignments:
        if rng.random() < mutation_rate:
            mutated.append(rng.choice(assignment_domains[(assignment.section_code, assignment.meeting_number)]))
        else:
            mutated.append(assignment)
    return tuple(mutated)


def _validate_config(
    input_data: TimetableInputData,
    config: GeneticAlgorithmConfig,
) -> list[str]:
    errors: list[str] = []
    if not input_data.course_sections:
        errors.append("Không có lớp học phần để xếp lịch.")
    if config.population_size < 1:
        errors.append("population_size phải lớn hơn hoặc bằng 1.")
    if config.generations < 1:
        errors.append("generations phải lớn hơn hoặc bằng 1.")
    if not 0 <= config.crossover_rate <= 1:
        errors.append("crossover_rate phải nằm trong khoảng 0 đến 1.")
    if not 0 <= config.mutation_rate <= 1:
        errors.append("mutation_rate phải nằm trong khoảng 0 đến 1.")
    if config.elite_count < 0:
        errors.append("elite_count phải lớn hơn hoặc bằng 0.")
    if config.tournament_size < 1:
        errors.append("tournament_size phải lớn hơn hoặc bằng 1.")
    if config.target_soft_cost is not None and config.target_soft_cost < 0:
        errors.append("target_soft_cost phải lớn hơn hoặc bằng 0.")
    if config.time_limit_seconds is not None and config.time_limit_seconds <= 0:
        errors.append("time_limit_seconds phải lớn hơn 0.")
    errors.extend(config.soft_weights.validate())
    return errors
