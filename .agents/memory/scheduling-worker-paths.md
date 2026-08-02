---
name: Scheduling worker paths
description: Runtime path behavior for the OR-Tools subprocess used by the timetable API
---

The managed API workflow can start with the API artifact directory as its current working directory, while local shell commands usually run from the workspace root. Any subprocess bridge for the scheduling worker must resolve both locations, and production must resolve the copied worker beside the built bundle.

**Why:** A root-relative worker path worked in direct shell checks but failed in the managed workflow with `ENOENT`, preventing the live API from invoking OR-Tools.

**How to apply:** When changing the scheduling worker, keep the path resolution and build-copy behavior together; verify through the routed `/api/scheduling/health` endpoint after restarting the API.