import { apiRequest } from "@/lib/api/client";
import type {
  ConfluenceReadResponse,
  JiraReadResponse,
  ProcessResponse,
  SourceSummaryResponse,
  TopicDetailResponse,
  TopicSummary,
  WorkMemoryRun,
} from "@/types/api";

export const shadowPoApi = {
  getTopics: () => apiRequest<TopicSummary[]>("/topics"),
  getTopic: (topicId: string) => apiRequest<TopicDetailResponse>(`/topics/${topicId}`),
  process: (payload: { user_input: string; context_hint?: string | null; target_output: string }) =>
    apiRequest<ProcessResponse>("/process", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getRun: (runId: string) => apiRequest<WorkMemoryRun>(`/runs/${runId}`),
  continueRun: (runId: string, action: string) =>
    apiRequest<ProcessResponse>(`/runs/${runId}/continue`, {
      method: "POST",
      body: JSON.stringify({ action }),
    }),
  sourceSummary: (payload: { source_type: string; source_ref: string; context_hint?: string | null }) =>
    apiRequest<SourceSummaryResponse>("/source-summary", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  jiraRead: (payload: { issue_key: string }) =>
    apiRequest<JiraReadResponse>("/jira-read", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  confluenceRead: (payload: { page_id: string }) =>
    apiRequest<ConfluenceReadResponse>("/confluence-read", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
