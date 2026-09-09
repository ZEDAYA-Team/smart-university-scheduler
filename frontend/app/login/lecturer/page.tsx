import LoginPage from "@/components/auth/LoginPage";
import { PANELS } from "@/lib/auth-panels";

export const metadata = { title: "Lecturer Sign In — SUTMS" };

export default function LecturerLoginRoute() {
  return <LoginPage panel={PANELS.lecturer} />;
}
