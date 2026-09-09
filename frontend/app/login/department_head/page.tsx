import LoginPage from "@/components/auth/LoginPage";
import { PANELS } from "@/lib/auth-panels";

export const metadata = { title: "Department Head Sign In — SUTMS" };

export default function DepartmentHeadLoginRoute() {
  return <LoginPage panel={PANELS. department_head} />;
}
