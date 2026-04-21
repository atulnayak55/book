import { api } from "../../lib/api";
import type { Department, Program } from "../../types/domain";

export async function fetchDepartments(search?: string): Promise<Department[]> {
  const response = await api.get<Department[]>("/taxonomy/departments", {
    params: search ? { search } : undefined,
  });
  return response.data;
}

export async function fetchPrograms(departmentId: number): Promise<Program[]> {
  const response = await api.get<Program[]>("/taxonomy/programs", {
    params: { department_id: departmentId },
  });
  return response.data;
}
