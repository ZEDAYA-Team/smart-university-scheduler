import LoginPage from "@/components/auth/LoginPage";
import { PANELS } from "@/lib/auth-panels";

export const metadata = { title: "Student Sign In — SUTMS" };

export default function StudentLoginRoute() {
  return <LoginPage panel={PANELS.student} />;
}
