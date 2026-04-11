import { create } from "zustand";

type RecentRun = {
  runId: string;
  topicId?: string;
  workflow: string;
  label: string;
};

type WorkspaceState = {
  selectedTopicId?: string;
  selectedRunId?: string;
  continuationRunId?: string;
  recentRuns: RecentRun[];
  setSelectedTopicId: (topicId?: string) => void;
  setSelectedRunId: (runId?: string) => void;
  setContinuationRunId: (runId?: string) => void;
  rememberRun: (run: RecentRun) => void;
};

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  recentRuns: [],
  setSelectedTopicId: (selectedTopicId) => set({ selectedTopicId }),
  setSelectedRunId: (selectedRunId) => set({ selectedRunId }),
  setContinuationRunId: (continuationRunId) => set({ continuationRunId }),
  rememberRun: (run) =>
    set((state) => ({
      recentRuns: [run, ...state.recentRuns.filter((item) => item.runId !== run.runId)].slice(0, 8),
      selectedRunId: run.runId,
      continuationRunId: run.runId,
      selectedTopicId: run.topicId ?? state.selectedTopicId,
    })),
}));
