export type PanelKey = "student" | "lecturer" | "department_head" | "admin";

export interface PanelConfig {
  key: PanelKey;
  label: string;
  idLabel: string;
  idPlaceholder: string;
  dashboardPath: string;
}

export const PANELS: Record<PanelKey, PanelConfig> = {
  student: {
    key: "student",
    label: "Student",
    idLabel: "Student ID / Email",
    idPlaceholder: "e.g. student.id@aau.edu.et",
    dashboardPath: "/dashboard/student",
  },
  lecturer: {
    key: "lecturer",
    label: "Lecturer",
    idLabel: "Staff ID / Email",
    idPlaceholder: "e.g. staff.id@aau.edu.et",
    dashboardPath: "/dashboard/lecturer",
  },
  department_head: {
    key: "department_head",
    label: "Department Head",
    idLabel: "Staff ID / Email",
    idPlaceholder: "e.g. staff.id@aau.edu.et",
    dashboardPath: "/dashboard/department_head",
  },
  admin: {
    key: "admin",
    label: "Admin",
    idLabel: "University ID / Email",
    idPlaceholder: "e.g. staff.id@aau.edu.et",
    dashboardPath: "/dashboard/admin",
  },
};