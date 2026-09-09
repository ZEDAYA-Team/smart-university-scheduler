"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { PANELS, type PanelKey } from "@/lib/auth-panels";

type User = { name: string; role: string };

function isPanelKey(value: string): value is PanelKey {
  return value in PANELS;
}

export default function DashboardPage() {
  const { role } = useParams<{ role: string }>();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  const validRole = isPanelKey(role);
  const panel = validRole ? PANELS[role] : null;

  useEffect(() => {
    if (!validRole) return;
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/auth/me`, { credentials: "include" })
      .then(async (response) => {
        if (!response.ok) throw new Error("unauthenticated");
        const account: User = await response.json();
        if (account.role !== role) throw new Error("wrong portal");
        setUser(account);
      })
      .catch(() => router.replace(`/login/${role}`));
  }, [role, validRole, router]);

  async function signOut() {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
    } finally {
      router.replace(`/login/${role}`);
    }
  }

  if (!panel) return null;
  return (
    <main className="min-h-screen bg-surface px-6 py-12">
      <div className="mx-auto max-w-3xl rounded-lg border border-border bg-white p-8 shadow-sm">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm text-muted">SUTMS · {panel.label} portal</p>
            <h1 className="mt-1 text-2xl font-semibold">{user ? `Welcome, ${user.name}` : "Signing you in…"}</h1>
          </div>
          {user && <button onClick={signOut} className="rounded-md border border-border px-3 py-2 text-sm text-muted hover:text-primary">Sign out</button>}
        </div>
        {user && <p className="mt-8 text-sm text-muted">Your dashboard is connected to your authenticated SUTMS account. Timetable features come next.</p>}
      </div>
    </main>
  );
}