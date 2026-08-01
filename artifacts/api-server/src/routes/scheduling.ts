import { Router, type IRouter } from "express";
import {
  DetectScheduleConflictsBody,
  DetectScheduleConflictsResponse,
  GenerateScheduleBody,
  GenerateScheduleResponse,
  SchedulingHealthResponse,
} from "@workspace/api-zod";
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

export default router;