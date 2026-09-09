import "@/app/globals.css";

export const metadata = {
  title: "SUTMS",
  description: "Smart University Timetable Management System",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}