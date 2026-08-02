import { createInsertSchema } from "drizzle-zod";
import {
  integer,
  jsonb,
  pgTable,
  serial,
  text,
  timestamp,
  real,
} from "drizzle-orm/pg-core";
import { z } from "zod/v4";

export const timetableRunsTable = pgTable("timetable_runs", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  status: text("status").notNull().default("draft"),
  solverStatus: text("solver_status").notNull(),
  schedule: jsonb("schedule").notNull(),
  placements: jsonb("placements").notNull(),
  conflicts: jsonb("conflicts").notNull(),
  objectiveValue: real("objective_value").notNull().default(0),
  solveTimeMs: integer("solve_time_ms").notNull().default(0),
  message: text("message").notNull(),
  offeringCount: integer("offering_count").notNull().default(0),
  placementCount: integer("placement_count").notNull().default(0),
  conflictCount: integer("conflict_count").notNull().default(0),
  createdAt: timestamp("created_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true })
    .notNull()
    .defaultNow()
    .$onUpdate(() => new Date()),
});

export const insertTimetableRunSchema = createInsertSchema(
  timetableRunsTable,
).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type InsertTimetableRun = z.infer<typeof insertTimetableRunSchema>;
export type TimetableRun = typeof timetableRunsTable.$inferSelect;