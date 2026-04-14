"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useApplications(status?: string) {
  return useQuery({
    queryKey: ["applications", status],
    queryFn: () => api.listApplications(status),
  });
}

export function useApplication(id: string) {
  return useQuery({
    queryKey: ["application", id],
    queryFn: () => api.getApplication(id),
    enabled: !!id,
  });
}

export function useVersions(appId: string) {
  return useQuery({
    queryKey: ["versions", appId],
    queryFn: () => api.listVersions(appId),
    enabled: !!appId,
  });
}

export function useCreateApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { company: string; role_title: string; jd_snapshot: string; portal_url?: string }) =>
      api.createApplication(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["applications"] }),
  });
}

export function useUpdateApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }: { id: string; status?: string }) =>
      api.updateApplication(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["applications"] }),
  });
}
