"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import type { PanelConfig } from "@/lib/auth-panels";
import type { LucideIcon } from "lucide-react";
import { 
  GraduationCap, 
  Shield, 
  Users, 
  Building2,
  Eye, 
  EyeOff, 
  AlertCircle 
} from "lucide-react";

// Typed against PanelKey itself — if a panel is ever added to
// auth-panels.ts without a matching entry here, this becomes a compile
// error instead of a silent runtime gap.
const PANEL_BADGE_ICON: Record<PanelConfig["key"], LucideIcon> = {
  student: GraduationCap,
  lecturer: Users,
  department_head: Building2,
  admin: Shield,
};

export default function LoginPage({ panel }: { panel: PanelConfig }) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const BadgeIcon = PANEL_BADGE_ICON[panel.key];

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/auth/login`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ email, password, panel: panel.key }),
        }
      );

      if (!res.ok) {
        throw new Error("invalid_credentials");
      }

      await res.json();
      router.push(panel.dashboardPath);
    } catch {
      setError("Invalid credentials. Please check your ID and password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen grid lg:grid-cols-2 bg-surface">
      {/* Branding panel */}
      <div className="hidden lg:flex relative flex-col justify-between overflow-hidden px-14 py-12 text-white">
        <Image
          src="/AAU_gate.webp"
          alt="Addis Ababa University Campus Gate"
          fill
          priority
          className="object-cover"
        />
        
        <div
          aria-hidden
          className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/50 to-black/90"
        />

        <div className="relative z-10 flex items-center gap-3">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-white p-1.5 shadow-md">
            <Image
              src="/AAU_logo.jpg"
              alt="Addis Ababa University seal"
              width={56}
              height={56}
              className="h-full w-full rounded-full object-contain"
            />
          </div>
          <div>
            <p className="text-base font-semibold leading-tight">Addis Ababa University</p>
            <p className="text-xs text-white/80 leading-tight">College of Natural &amp; Computational Sciences</p>
          </div>
        </div>

        <div className="relative z-10 max-w-md space-y-4">
          <h1 className="font-heading text-3xl sm:text-4xl font-bold leading-tight tracking-tight">
            Smart Timetable &amp; Course Scheduling System
          </h1>
          <p className="text-sm leading-relaxed text-white/80">
            Automated, conflict-free class scheduling for students, lecturers,
            and department admins across the university.
          </p>
        </div>

        <div className="relative z-10 flex items-center gap-2 text-xs text-white/70">
          <Shield className="h-4 w-4 text-white/80" />
          <span>Access is restricted to verified university accounts.</span>
        </div>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center px-6 py-12 lg:px-12">
        <div className="w-full max-w-md">
          {/* Mobile-only compact header */}
          <div className="flex items-center gap-3 mb-8 lg:hidden">
            <div className="w-11 h-11 rounded-full bg-white p-1 shadow-sm ring-1 ring-border shrink-0">
              <Image
                src="/AAU_logo.jpg"
                alt="Addis Ababa University seal"
                width={44}
                height={44}
                className="h-full w-full rounded-full object-contain"
              />
            </div>
            <div>
              <p className="font-semibold text-[#0D1117] leading-tight">SUTMS — AAU</p>
              <p className="text-xs text-muted leading-tight">{panel.label} portal</p>
            </div>
          </div>

          <div className="relative bg-white rounded-2xl border border-border/80 shadow-sm p-8 sm:p-10 overflow-hidden">
            <div className="hidden lg:flex items-center gap-2.5 mb-6">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                <BadgeIcon className="w-5 h-5 text-primary" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-wider text-muted">
                {panel.label} portal
              </span>
            </div>

            <h2 className="font-heading text-2xl sm:text-3xl font-bold text-[#0D1117] tracking-tight mb-1">
              Sign in
            </h2>
            <p className="text-sm text-muted mb-8">
              Use your official university credentials to continue.
            </p>

            {error && (
              <div className="mb-6 flex items-start gap-3 rounded-xl bg-accent-light border border-accent/20 p-4">
                <AlertCircle className="w-5 h-5 text-accent-hover shrink-0 mt-0.5" />
                <p className="text-sm text-accent-hover font-medium leading-snug">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5" noValidate>
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-[#0D1117] mb-1.5"
                >
                  {panel.idLabel}
                </label>
                <input
                  id="email"
                  type="text"
                  autoComplete="username"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={panel.idPlaceholder}
                  className="w-full rounded-xl border border-border/80 bg-white px-4 py-3 text-sm font-mono placeholder:font-sans placeholder:text-muted/60 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all shadow-sm"
                />
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-[#0D1117] mb-1.5"
                >
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full rounded-xl border border-border/80 bg-white pl-4 pr-11 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all shadow-sm"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    aria-pressed={showPassword}
                    tabIndex={-1}
                    className="absolute inset-y-0 right-0 flex items-center pr-3.5 text-muted hover:text-[#0D1117] transition-colors"
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-xl bg-primary hover:bg-primary-hover active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed text-white text-sm font-semibold py-3 mt-3 transition-all shadow-sm flex items-center justify-center gap-2"
              >
                {loading && (
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                )}
                {loading ? "Signing in…" : `Sign in as ${panel.label}`}
              </button>
            </form>
          </div>

          <div className="mt-8 flex items-center justify-between px-1">
            <p className="text-sm text-muted font-mono">
              © 2026 AAU CNCS — SUTMS v0.1.0
            </p>
            <a
              href="https://www.aau.edu.et/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-muted hover:text-primary transition-colors font-medium"
            >
              aau.edu.et
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}