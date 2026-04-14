"use client";

import { useState, useCallback } from "react";
import { api } from "@/lib/api";
import type { MutationItem, OptimizeResponse, ApplyResponse } from "@/lib/types";

export type ChangeStatus = "pending" | "approved" | "rejected" | "edited";

export interface TrackedMutation extends MutationItem {
  id: string;
  status: ChangeStatus;
}

export function useOptimize(appId: string) {
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [result, setResult] = useState<OptimizeResponse | null>(null);
  const [changes, setChanges] = useState<TrackedMutation[]>([]);
  const [applyResult, setApplyResult] = useState<ApplyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runOptimize = useCallback(
    async (baseResumeId: string) => {
      setIsOptimizing(true);
      setError(null);
      try {
        const res = await api.optimize(appId, baseResumeId);
        setResult(res);
        setChanges(
          res.mutations.map((m, i) => ({
            ...m,
            id: `mut-${i}`,
            status: "pending" as ChangeStatus,
          }))
        );
      } catch (e) {
        setError(e instanceof Error ? e.message : "Optimization failed");
      } finally {
        setIsOptimizing(false);
      }
    },
    [appId]
  );

  const updateChange = useCallback(
    (id: string, update: Partial<TrackedMutation>) => {
      setChanges((prev) =>
        prev.map((c) => (c.id === id ? { ...c, ...update } : c))
      );
    },
    []
  );

  const approveAll = useCallback(() => {
    setChanges((prev) => prev.map((c) => ({ ...c, status: "approved" })));
  }, []);

  const applyChanges = useCallback(
    async (baseResumeId: string) => {
      setIsApplying(true);
      setError(null);
      const approved = changes.filter(
        (c) => c.status === "approved" || c.status === "edited"
      );
      try {
        const res = await api.applyMutations(appId, baseResumeId, approved);
        setApplyResult(res);
        return res;
      } catch (e) {
        setError(e instanceof Error ? e.message : "Apply failed");
        return null;
      } finally {
        setIsApplying(false);
      }
    },
    [appId, changes]
  );

  return {
    isOptimizing,
    isApplying,
    result,
    changes,
    applyResult,
    error,
    runOptimize,
    updateChange,
    approveAll,
    applyChanges,
  };
}
