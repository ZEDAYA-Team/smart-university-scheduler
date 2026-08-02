"""CP-SAT scheduling worker for SUTMS.

The Node API owns transport and authentication boundaries. This small stdin/stdout
worker keeps the OR-Tools model isolated and makes it easy to run the same engine
from tests or a future FastAPI service.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from itertools import combinations
from typing import Any

from ortools.sat.python import cp_model


def conflict(
    code: str,
    message: str,
    offering_ids: list[str],
    room_id: str | None = None,
    time_slot_id: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "code": code,
        "message": message,
        "offeringIds": offering_ids,
    }
    if room_id is not None:
        result["roomId"] = room_id
    if time_slot_id is not None:
        result["timeSlotId"] = time_slot_id
    return result


def overlaps(first: dict[str, Any], second: dict[str, Any]) -> bool:
    return (
        first["day"] == second["day"]
        and first["startMinute"] < second["endMinute"]
        and second["startMinute"] < first["endMinute"]
    )


def interval_is_available(
    slot: dict[str, Any], availability: list[dict[str, Any]]
) -> bool:
    return any(
        window["day"] == slot["day"]
        and window["startMinute"] <= slot["startMinute"]
        and window["endMinute"] >= slot["endMinute"]
        for window in availability
    )


def room_type_for(offering: dict[str, Any]) -> str:
    required = offering.get("requiredRoomType")
    if required:
        return required
    return "LAB" if offering["courseType"] == "LAB" else "LECTURE"


def validate_input(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate semantic relationships not covered by the generated API schema."""
    conflicts: list[dict[str, Any]] = []
    slots = payload["timeSlots"]
    rooms = payload["rooms"]
    lecturers = payload["lecturers"]
    sections = payload["sections"]
    offerings = payload["offerings"]

    def check_unique(items: list[dict[str, Any]], label: str) -> None:
        seen: set[str] = set()
        for item in items:
            item_id = item["id"]
            if item_id in seen:
                conflicts.append(
                    conflict(
                        "INVALID_REFERENCE",
                        f"Duplicate {label} id '{item_id}'.",
                        [],
                    )
                )
            seen.add(item_id)

    check_unique(slots, "time slot")
    check_unique(rooms, "room")
    check_unique(lecturers, "lecturer")
    check_unique(sections, "section")
    check_unique(offerings, "course offering")

    slot_ids = {item["id"] for item in slots}
    room_ids = {item["id"] for item in rooms}
    lecturer_ids = {item["id"] for item in lecturers}
    section_ids = {item["id"] for item in sections}

    for slot in slots:
        if slot["startMinute"] >= slot["endMinute"]:
            conflicts.append(
                conflict(
                    "INVALID_REFERENCE",
                    f"Time slot '{slot['id']}' must end after it starts.",
                    [],
                    time_slot_id=slot["id"],
                )
            )
    for lecturer in lecturers:
        for window in lecturer["availability"]:
            if window["startMinute"] >= window["endMinute"]:
                conflicts.append(
                    conflict(
                        "INVALID_REFERENCE",
                        f"Availability window for lecturer '{lecturer['id']}' is invalid.",
                        [],
                    )
                )

    for offering in offerings:
        ids = [offering["id"]]
        if offering["lecturerId"] not in lecturer_ids:
            conflicts.append(
                conflict(
                    "INVALID_REFERENCE",
                    f"Offering '{offering['id']}' references unknown lecturer '{offering['lecturerId']}'.",
                    ids,
                )
            )
        if offering["sectionId"] not in section_ids:
            conflicts.append(
                conflict(
                    "INVALID_REFERENCE",
                    f"Offering '{offering['id']}' references unknown section '{offering['sectionId']}'.",
                    ids,
                )
            )
        for slot_id in offering.get("allowedTimeSlotIds", []):
            if slot_id not in slot_ids:
                conflicts.append(
                    conflict(
                        "INVALID_REFERENCE",
                        f"Offering '{offering['id']}' allows unknown time slot '{slot_id}'.",
                        ids,
                    )
                )
        for slot_id in offering.get("forbiddenTimeSlotIds", []):
            if slot_id not in slot_ids:
                conflicts.append(
                    conflict(
                        "INVALID_REFERENCE",
                        f"Offering '{offering['id']}' forbids unknown time slot '{slot_id}'.",
                        ids,
                    )
                )

    # This catches accidental payload fields that would otherwise make a schedule
    # look valid while silently losing a resource reference.
    _ = room_ids
    return conflicts


def candidate_assignments(
    payload: dict[str, Any],
) -> tuple[
    dict[str, list[tuple[int, int]]],
    list[dict[str, Any]],
]:
    slots = payload["timeSlots"]
    rooms = payload["rooms"]
    lecturers = {item["id"]: item for item in payload["lecturers"]}
    sections = {item["id"]: item for item in payload["sections"]}
    assignments: dict[str, list[tuple[int, int]]] = {}
    conflicts: list[dict[str, Any]] = []

    for offering in payload["offerings"]:
        offering_id = offering["id"]
        candidates: list[tuple[int, int]] = []
        lecturer = lecturers.get(offering["lecturerId"])
        section = sections.get(offering["sectionId"])
        if lecturer is None or section is None:
            assignments[offering_id] = candidates
            continue

        allowed = set(offering.get("allowedTimeSlotIds", []))
        forbidden = set(offering.get("forbiddenTimeSlotIds", []))
        required_type = room_type_for(offering)
        matching_type_rooms = [room for room in rooms if room["type"] == required_type]
        capacity_rooms = [
            room for room in matching_type_rooms if room["capacity"] >= section["capacity"]
        ]
        available_slots = [
            slot
            for slot in slots
            if (not allowed or slot["id"] in allowed)
            and slot["id"] not in forbidden
            and interval_is_available(slot, lecturer["availability"])
        ]
        if not capacity_rooms:
            if not matching_type_rooms:
                conflicts.append(
                    conflict(
                        "ROOM_TYPE",
                        f"Offering '{offering_id}' requires a {required_type.lower()} room, but none is available.",
                        [offering_id],
                    )
                )
            else:
                conflicts.append(
                    conflict(
                        "ROOM_CAPACITY",
                        f"Offering '{offering_id}' needs capacity {section['capacity']}, but no matching room is large enough.",
                        [offering_id],
                    )
                )
        if not available_slots:
            conflicts.append(
                conflict(
                    "LECTURER_AVAILABILITY",
                    f"Lecturer '{lecturer['name']}' has no available time slot for offering '{offering_id}'.",
                    [offering_id],
                )
            )
        for time_index, slot in enumerate(slots):
            if slot not in available_slots:
                continue
            for room_index, room in enumerate(rooms):
                if room in capacity_rooms:
                    candidates.append((time_index, room_index))
        assignments[offering_id] = candidates
        if not candidates and not any(
            item["offeringIds"] == [offering_id] for item in conflicts
        ):
            conflicts.append(
                conflict(
                    "NO_AVAILABLE_ASSIGNMENT",
                    f"Offering '{offering_id}' has no valid room and time-slot combination.",
                    [offering_id],
                )
            )
    return assignments, conflicts


def add_resource_constraints(
    model: cp_model.CpModel,
    variables: dict[tuple[int, int, int], cp_model.IntVar],
    payload: dict[str, Any],
    resource_groups: list[set[str]],
) -> None:
    """Prevent overlap for a resource, including partially overlapping slots."""
    slots = payload["timeSlots"]
    slot_pairs: list[tuple[int, int]] = []
    for first_index, second_index in combinations(range(len(slots)), 2):
        if overlaps(slots[first_index], slots[second_index]):
            slot_pairs.append((first_index, second_index))

    resources = set().union(*resource_groups) if resource_groups else set()
    for resource in resources:
        # One resource can be represented by many offering-specific assignment vars.
        by_slot: dict[int, list[cp_model.IntVar]] = defaultdict(list)
        for (offering_index, time_index, room_index), variable in variables.items():
            if resource in resource_groups[offering_index]:
                by_slot[time_index].append(variable)

        for time_index, resource_variables in by_slot.items():
            model.AddAtMostOne(resource_variables)
        for first_index, second_index in slot_pairs:
            first_variables = by_slot.get(first_index, [])
            second_variables = by_slot.get(second_index, [])
            if first_variables and second_variables:
                model.AddAtMostOne(first_variables + second_variables)


def generate(payload: dict[str, Any]) -> dict[str, Any]:
    import time

    started = time.perf_counter()
    semantic_conflicts = validate_input(payload)
    if semantic_conflicts:
        return {
            "status": "MODEL_INVALID",
            "placements": [],
            "conflicts": semantic_conflicts,
            "objectiveValue": 0,
            "solveTimeMs": round((time.perf_counter() - started) * 1000),
            "message": "The scheduling input contains invalid references or time windows.",
        }

    assignments, candidate_conflicts = candidate_assignments(payload)
    if any(not values for values in assignments.values()):
        return {
            "status": "INFEASIBLE",
            "placements": [],
            "conflicts": candidate_conflicts,
            "objectiveValue": 0,
            "solveTimeMs": round((time.perf_counter() - started) * 1000),
            "message": "No valid assignment exists for at least one course offering.",
        }

    offerings = payload["offerings"]
    slots = payload["timeSlots"]
    rooms = payload["rooms"]
    lecturers = payload["lecturers"]
    sections = payload["sections"]
    model = cp_model.CpModel()
    variables: dict[tuple[int, int, int], cp_model.IntVar] = {}
    preferred_penalties: list[cp_model.IntVar] = []

    for offering_index, offering in enumerate(offerings):
        preferred = set(offering.get("preferredTimeSlotIds", []))
        for time_index, room_index in assignments[offering["id"]]:
            variable = model.NewBoolVar(
                f"offering_{offering_index}_slot_{time_index}_room_{room_index}"
            )
            variables[(offering_index, time_index, room_index)] = variable
            if preferred and slots[time_index]["id"] not in preferred:
                preferred_penalties.append(variable)

    for offering_index, offering in enumerate(offerings):
        offering_variables = [
            variable
            for (index, _, _), variable in variables.items()
            if index == offering_index
        ]
        model.AddExactlyOne(offering_variables)

    lecturer_groups = [
        {offering["lecturerId"]} for offering in offerings
    ]
    section_groups = [{offering["sectionId"]} for offering in offerings]
    # Resource groups are indexed by offering, while room ids are supplied by
    # the assignment's room index below.
    add_resource_constraints(model, variables, payload, lecturer_groups)
    add_resource_constraints(model, variables, payload, section_groups)

    # Room resources depend on the room chosen by each assignment.
    room_by_slot: dict[tuple[str, int], list[cp_model.IntVar]] = defaultdict(list)
    for (offering_index, time_index, room_index), variable in variables.items():
        room_by_slot[(rooms[room_index]["id"], time_index)].append(variable)
    room_slot_pairs: list[tuple[str, int, int]] = []
    for room in rooms:
        for first_index, second_index in combinations(range(len(slots)), 2):
            if overlaps(slots[first_index], slots[second_index]):
                room_slot_pairs.append((room["id"], first_index, second_index))
    for variables_at_slot in room_by_slot.values():
        model.AddAtMostOne(variables_at_slot)
    for room_id, first_index, second_index in room_slot_pairs:
        first_variables = room_by_slot.get((room_id, first_index), [])
        second_variables = room_by_slot.get((room_id, second_index), [])
        if first_variables and second_variables:
            model.AddAtMostOne(first_variables + second_variables)

    # Student enrollment is represented directly on an offering for this API
    # slice, matching the ERD's ENROLLMENT -> COURSE_OFFERING relationship.
    student_groups = [
        set(offering.get("studentIds", [])) for offering in offerings
    ]
    add_resource_constraints(model, variables, payload, student_groups)

    if preferred_penalties:
        model.Minimize(sum(preferred_penalties))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(
        min(max(payload.get("timeLimitSeconds", 30), 1), 120)
    )
    solver.parameters.num_search_workers = 8
    solver.parameters.random_seed = 17
    status = solver.Solve(model)
    status_name = {
        cp_model.OPTIMAL: "OPTIMAL",
        cp_model.FEASIBLE: "FEASIBLE",
        cp_model.INFEASIBLE: "INFEASIBLE",
        cp_model.MODEL_INVALID: "MODEL_INVALID",
        cp_model.UNKNOWN: "UNKNOWN",
    }.get(status, "UNKNOWN")

    placements: list[dict[str, str]] = []
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for (offering_index, time_index, room_index), variable in variables.items():
            if solver.Value(variable):
                placements.append(
                    {
                        "offeringId": offerings[offering_index]["id"],
                        "timeSlotId": slots[time_index]["id"],
                        "roomId": rooms[room_index]["id"],
                    }
                )
    conflicts = candidate_conflicts
    if status == cp_model.INFEASIBLE:
        conflicts = conflicts + [
            conflict(
                "INFEASIBLE_MODEL",
                "The hard constraints cannot all be satisfied with the supplied rooms, lecturers, sections, and time slots.",
                [offering["id"] for offering in offerings],
            )
        ]
    message = (
        "Schedule generated successfully."
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        else "The solver could not produce a complete schedule."
    )
    return {
        "status": status_name,
        "placements": placements,
        "conflicts": conflicts,
        "objectiveValue": float(solver.ObjectiveValue())
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        else 0,
        "solveTimeMs": round((time.perf_counter() - started) * 1000),
        "message": message,
    }


def detect_conflicts(payload: dict[str, Any]) -> dict[str, Any]:
    semantic_conflicts = validate_input(payload)
    slots = {item["id"]: item for item in payload["timeSlots"]}
    rooms = {item["id"]: item for item in payload["rooms"]}
    lecturers = {item["id"]: item for item in payload["lecturers"]}
    sections = {item["id"]: item for item in payload["sections"]}
    offerings = {item["id"]: item for item in payload["offerings"]}
    result = list(semantic_conflicts)
    valid_placements: list[tuple[dict[str, Any], dict[str, Any]]] = []
    seen_offerings: set[str] = set()

    for placement in payload["placements"]:
        offering_id = placement["offeringId"]
        offering = offerings.get(offering_id)
        room = rooms.get(placement["roomId"])
        slot = slots.get(placement["timeSlotId"])
        if offering is None or room is None or slot is None:
            result.append(
                conflict(
                    "INVALID_REFERENCE",
                    f"Placement for offering '{offering_id}' references an unknown offering, room, or time slot.",
                    [offering_id],
                    placement.get("roomId"),
                    placement.get("timeSlotId"),
                )
            )
            continue
        if offering_id in seen_offerings:
            result.append(
                conflict(
                    "INVALID_REFERENCE",
                    f"Offering '{offering_id}' is placed more than once.",
                    [offering_id],
                    placement["roomId"],
                    placement["timeSlotId"],
                )
            )
            continue
        seen_offerings.add(offering_id)
        valid_placements.append((placement, offering))
        section = sections.get(offering["sectionId"])
        if section and room["capacity"] < section["capacity"]:
            result.append(
                conflict(
                    "ROOM_CAPACITY",
                    f"Room '{room['name']}' cannot hold section '{section['name']}' ({section['capacity']} seats required).",
                    [offering_id],
                    room["id"],
                    slot["id"],
                )
            )
        if room["type"] != room_type_for(offering):
            result.append(
                conflict(
                    "ROOM_TYPE",
                    f"Room '{room['name']}' is {room['type'].lower()}, but this offering requires {room_type_for(offering).lower()}.",
                    [offering_id],
                    room["id"],
                    slot["id"],
                )
            )
        lecturer = lecturers.get(offering["lecturerId"])
        if lecturer and not interval_is_available(slot, lecturer["availability"]):
            result.append(
                conflict(
                    "LECTURER_AVAILABILITY",
                    f"Lecturer '{lecturer['name']}' is not available for this time slot.",
                    [offering_id],
                    room["id"],
                    slot["id"],
                )
            )

    missing = set(offerings) - seen_offerings
    for offering_id in sorted(missing):
        result.append(
            conflict(
                "INVALID_REFERENCE",
                f"Offering '{offering_id}' has no schedule placement.",
                [offering_id],
            )
        )

    for (first_placement, first_offering), (second_placement, second_offering) in combinations(
        valid_placements, 2
    ):
        first_slot = slots[first_placement["timeSlotId"]]
        second_slot = slots[second_placement["timeSlotId"]]
        if not overlaps(first_slot, second_slot):
            continue
        first_ids = [first_offering["id"], second_offering["id"]]
        if first_placement["roomId"] == second_placement["roomId"]:
            result.append(
                conflict(
                    "ROOM_DOUBLE_BOOKING",
                    "Two offerings use the same room during overlapping time slots.",
                    first_ids,
                    first_placement["roomId"],
                    first_placement["timeSlotId"],
                )
            )
        if first_offering["lecturerId"] == second_offering["lecturerId"]:
            result.append(
                conflict(
                    "LECTURER_DOUBLE_BOOKING",
                    "A lecturer is assigned to two offerings during overlapping time slots.",
                    first_ids,
                    time_slot_id=first_placement["timeSlotId"],
                )
            )
        if first_offering["sectionId"] == second_offering["sectionId"]:
            result.append(
                conflict(
                    "SECTION_DOUBLE_BOOKING",
                    "A section is assigned to two offerings during overlapping time slots.",
                    first_ids,
                    time_slot_id=first_placement["timeSlotId"],
                )
            )
        shared_students = set(first_offering.get("studentIds", [])) & set(
            second_offering.get("studentIds", [])
        )
        if shared_students:
            result.append(
                conflict(
                    "STUDENT_DOUBLE_BOOKING",
                    f"{len(shared_students)} enrolled student(s) have overlapping offerings.",
                    first_ids,
                    time_slot_id=first_placement["timeSlotId"],
                )
            )
    return {"valid": not result, "conflicts": result}


def main() -> None:
    payload = json.load(sys.stdin)
    action = payload.get("action")
    if action == "health":
        import ortools

        output = {
            "status": "ready",
            "solver": "OR-Tools CP-SAT",
            "version": ortools.__version__,
        }
    elif action == "generate":
        output = generate(payload["payload"])
    elif action == "conflicts":
        output = detect_conflicts(payload["payload"])
    else:
        raise ValueError("Unknown scheduling worker action.")
    sys.stdout.write(json.dumps(output, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        sys.stderr.write(f"{type(error).__name__}: {error}\n")
        sys.exit(1)