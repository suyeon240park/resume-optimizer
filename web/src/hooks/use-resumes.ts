"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useResumes() {
  return useQuery({
    queryKey: ["resumes"],
    queryFn: () => api.listResumes(),
  });
}

export function useResume(id: string) {
  return useQuery({
    queryKey: ["resume", id],
    queryFn: () => api.getResume(id),
    enabled: !!id,
  });
}

export function useCreateResume() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; latex_source: string; preset_type?: string }) =>
      api.createResume(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["resumes"] }),
  });
}

export function useDeleteResume() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteResume(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["resumes"] }),
  });
}
