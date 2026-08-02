import { Router, type IRouter } from "express";
import {
  CreateTimetableRunBody,
  CreateTimetableRunResponse,
  DetectScheduleConflictsBody,
  DetectScheduleConflictsResponse,
  GenerateScheduleBody,
  GenerateScheduleResponse,
  GetTimetableRunParams,
  GetTimetableRunResponse,
  ListTimetableRunsResponse,
  SchedulingHealthResponse,
} from "@workspace/api-zod";
import { desc, eq } from "drizzle-orm";
import { db, timetableRunsTable } from "@workspace/db";
import { runSchedulingWorker } from "../scheduling/worker";

const router: IRouter = Router();

router.get("/scheduling/health", async (req, res) => {
  try {
    const data = SchedulingHealthResponse.parse(
      await runSchedulingWorker({ action: "health" }),
    );
    res.json(data);
  } catch (error) {
    req.log.error({ err: error }, "Scheduling worker health check failed");
    res.json({
      status: "unavailable",
      solver: "OR-Tools CP-SAT",
      version: "unavailable",
    });
  }
});

router.post("/scheduling/generate", async (req, res) => {
  const parsed = GenerateScheduleBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({
      message: "Invalid scheduling input.",
      issues: parsed.error.issues,
    });
    return;
  }

  try {
    const result = await runSchedulingWorker({
      action: "generate",
      payload: parsed.data,
    });
    const data = GenerateScheduleResponse.parse(result);
    res.json(data);
  } catch (error) {
    req.log.error({ err: error }, "Schedule generation failed");
    res.status(500).json({
      message: "The scheduling engine failed while generating the timetable.",
    });
  }
});

router.post("/scheduling/conflicts", async (req, res) => {
  const parsed = DetectScheduleConflictsBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({
      message: "Invalid conflict detection input.",
      issues: parsed.error.issues,
    });
    return;
  }

  try {
    const result = await runSchedulingWorker({
      action: "conflicts",
      payload: parsed.data,
    });
    const data = DetectScheduleConflictsResponse.parse(result);
    res.json(data);
  } catch (error) {
    req.log.error({ err: error }, "Schedule conflict detection failed");
    res.status(500).json({
      message: "The scheduling engine failed while checking conflicts.",
    });
  }
});

function toSummary(row: typeof timetableRunsTable.$inferSelect) {
  return {
    id: row.id,
    name: row.name,
    status: row.status,
    solverStatus: row.solverStatus,
    offeringCount: row.offeringCount,
    placementCount: row.placementCount,
    conflictCount: row.conflictCount,
    createdAt: row.createdAt.toISOString(),
  };
}

function toDetail(row: typeof timetableRunsTable.$inferSelect) {
  return {
    ...toSummary(row),
    schedule: row.schedule,
    placements: row.placements,
    conflicts: row.conflicts,
    objectiveValue: row.objectiveValue,
    solveTimeMs: row.solveTimeMs,
    message: row.message,
  };
}

router.get("/scheduling/runs", async (req, res) => {
  try {
    const rows = await db
      .select()
      .from(timetableRunsTable)
      .orderBy(desc(timetableRunsTable.createdAt));
    res.json(ListTimetableRunsResponse.parse(rows.map(toSummary)));
  } catch (error) {
    req.log.error({ err: error }, "Failed to list timetable runs");
    res.status(500).json({ message: "Unable to load saved timetable drafts." });
  }
});

router.post("/scheduling/runs", async (req, res) => {
  const parsed = CreateTimetableRunBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({
      message: "Invalid timetable run input.",
      issues: parsed.error.issues,
    });
    return;
  }

  try {
    const solverResult = GenerateScheduleResponse.parse(
      await runSchedulingWorker({
        action: "generate",
        payload: parsed.data.schedule,
      }),
    );
    const [row] = await db
      .insert(timetableRunsTable)
      .values({
        name: parsed.data.name,
        status: "draft",
        solverStatus: solverResult.status,
        schedule: parsed.data.schedule,
        placements: solverResult.placements,
        conflicts: solverResult.conflicts,
        objectiveValue: solverResult.objectiveValue,
        solveTimeMs: solverResult.solveTimeMs,
        message: solverResult.message,
        offeringCount: parsed.data.schedule.offerings.length,
        placementCount: solverResult.placements.length,
        conflictCount: solverResult.conflicts.length,
      })
      .returning();

    res.status(201).json(CreateTimetableRunResponse.parse(toDetail(row)));
  } catch (error) {
    req.log.error({ err: error }, "Failed to generate and save timetable run");
    res.status(500).json({
      message: "Unable to generate and save the timetable draft.",
    });
  }
});

router.get("/scheduling/runs/:runId", async (req, res) => {
  const parsed = GetTimetableRunParams.safeParse(req.params);
  if (!parsed.success) {
    res.status(400).json({
      message: "Invalid timetable run id.",
      issues: parsed.error.issues,
    });
    return;
  }

  try {
    const [row] = await db
      .select()
      .from(timetableRunsTable)
      .where(eq(timetableRunsTable.id, parsed.data.runId))
      .limit(1);
    if (!row) {
      res.status(404).json({ message: "Timetable draft not found." });
      return;
    }
    res.json(GetTimetableRunResponse.parse(toDetail(row)));
  } catch (error) {
    req.log.error({ err: error }, "Failed to load timetable run");
    res.status(500).json({ message: "Unable to load the timetable draft." });
  }
});

export default router;