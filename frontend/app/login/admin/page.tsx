import LoginPage from "@/components/auth/LoginPage";
import { PANELS } from "@/lib/auth-panels";

export const metadata = { title: "Admin Sign In — SUTMS" };

export default function AdminLoginRoute() {
  return <LoginPage panel={PANELS.admin} />;
}
