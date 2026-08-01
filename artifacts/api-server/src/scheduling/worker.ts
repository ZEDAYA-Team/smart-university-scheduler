import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";

type WorkerResult = Record<string, unknown>;

function firstExistingPath(candidates: string[]): string {
  const match = candidates.find((candidate) => existsSync(candidate));
  if (!match) {
    throw new Error(`Scheduling worker file was not found. Tried: ${candidates.join(", ")}`);
  }
  return match;
}

function workerFilePath(): string {
  const relativePath =
    process.env["NODE_ENV"] === "production"
      ? "dist/scheduling/solver.py"
      : "src/scheduling/solver.py";
  return firstExistingPath([
    path.resolve(process.cwd(), relativePath),
    path.resolve(process.cwd(), "artifacts/api-server", relativePath),
  ]);
}

function pythonCommand(): string {
  if (process.env["SCHEDULING_PYTHON"]) {
    return process.env["SCHEDULING_PYTHON"];
  }
  if (process.platform === "win32") return "python";
  return firstExistingPath([
    path.resolve(process.cwd(), ".pythonlibs/bin/python"),
    path.resolve(process.cwd(), "../../.pythonlibs/bin/python"),
    path.resolve(process.cwd(), "artifacts/api-server/../../.pythonlibs/bin/python"),
  ]);
}

export function runSchedulingWorker(
  input: Record<string, unknown>,
  timeoutMs = 125_000,
): Promise<WorkerResult> {
  return new Promise((resolve, reject) => {
    const child = spawn(pythonCommand(), [workerFilePath()], {
      stdio: ["pipe", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    let settled = false;

    const finish = (callback: () => void) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      callback();
    };

    const timer = setTimeout(() => {
      child.kill("SIGTERM");
      finish(() =>
        reject(
          new Error(
            `Scheduling worker exceeded the ${Math.round(timeoutMs / 1000)} second limit.`,
          ),
        ),
      );
    }, timeoutMs);

    child.stdout.on("data", (chunk: Buffer | string) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk: Buffer | string) => {
      stderr += chunk.toString();
    });
    child.on("error", (error) => finish(() => reject(error)));
    child.on("close", (code) => {
      finish(() => {
        if (code !== 0) {
          reject(
            new Error(
              `Scheduling worker exited with code ${code ?? "unknown"}: ${stderr.trim() || "no error details"}`,
            ),
          );
          return;
        }

        try {
          resolve(JSON.parse(stdout) as WorkerResult);
        } catch {
          reject(
            new Error(
              `Scheduling worker returned invalid JSON: ${stdout.slice(0, 500)}`,
            ),
          );
        }
      });
    });

    child.stdin.write(JSON.stringify(input));
    child.stdin.end();
  });
}