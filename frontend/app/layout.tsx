import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SUTMS | Dashboard & Reports",
  description: "Smart University Timetable Management System reporting dashboard",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
