import { api } from "../../lib/api";
import type { Listing } from "../../types/domain";

export async function fetchListings(subjectId?: number): Promise<Listing[]> {
  const response = await api.get<Listing[]>("/listings", {
    params: subjectId ? { subject_id: subjectId } : undefined,
  });
  return response.data;
}
