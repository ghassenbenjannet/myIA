export type AvailableAction = "refine_analysis" | "draft_ticket" | "draft_documentation";

// ── Result types (discriminated union via result_type) ────────────────────────

export type AnalysisResult = {
  result_type: "analysis";
  reformulation: string;
  request_summary: string;
  detected_type: string;
  context_hint?: string | null;
  current_behavior?: string | null;
  expected_behavior?: string | null;
  business_impacts: string[];
  technical_impacts: string[];
  dependencies: string[];
  ambiguities: string[];
  risks: string[];
  open_questions: string[];
  recommended_output: string;
  recommended_next_step: string;
};

export type TicketResult = {
  result_type: "ticket";
  title: string;
  ticket_type: string;
  context?: string | null;
  business_goal?: string | null;
  description?: string | null;
  current_behavior?: string | null;
  expected_behavior?: string | null;
  business_impacts: string[];
  technical_impacts: string[];
  dependencies: string[];
  open_points: string[];
  acceptance_criteria: string[];
};

export type DocumentationSection = {
  title: string;
  content: string[] | string;
};

export type DocumentationResult = {
  result_type: "documentation";
  title: string;
  document_type?: string | null;
  summary?: string | null;
  context?: string | null;
  sections: DocumentationSection[];
  detected_type?: string | null;
};

export type SourceSummaryResult = {
  result_type: "source_summary";
  source_type: string;
  source_ref: string;
  source_title?: string | null;
  summary: string;
  key_points: string[];
  open_questions: string[];
  next_step_hint?: string | null;
};

export type JiraIssueResult = {
  result_type: "jira_read";
  issue_key: string;
  title: string;
  description?: string | null;
  status?: string | null;
  issue_type?: string | null;
  priority?: string | null;
  assignee?: string | null;
  labels: string[];
  url?: string | null;
  summary: string;
  open_points: string[];
};

export type ConfluencePageResult = {
  result_type: "confluence_read";
  page_id: string;
  title: string;
  space_key?: string | null;
  url?: string | null;
  summary: string;
  content_preview?: string | null;
  key_points: string[];
  open_points: string[];
};

export type ContextUsed = {
  source_name: string;
  confidence_hint?: string | null;
  summary: string;
  snippets: string[];
};

export type ArtifactResult =
  | AnalysisResult
  | TicketResult
  | DocumentationResult
  | SourceSummaryResult
  | JiraIssueResult
  | ConfluencePageResult;

// ── Process ───────────────────────────────────────────────────────────────────

export type ProcessMode = "deterministic" | "assisted";

export type ProcessRequest = {
  user_input: string;
  context_hint?: string | null;
  target_output: string;
  mode?: ProcessMode;
};

export type ProcessResponse = {
  run_id: string;
  topic_id: string;
  request_type: string;
  selected_workflow: string;
  confidence: number;
  result: AnalysisResult | TicketResult | DocumentationResult;
  intermediate_analysis?: AnalysisResult | null;
  context_used?: ContextUsed | null;
  quality_checks: string[];
  warnings: string[];
  mode_used?: string;
  llm_provider?: string | null;
};

// ── Work memory ───────────────────────────────────────────────────────────────

export type WorkMemoryRun = {
  run_id: string;
  topic_id?: string | null;
  created_at: string;
  status: string;
  parent_run_id?: string | null;
  continuation_action?: string | null;
  raw_input: string;
  target_output: string;
  request_type: string;
  final_workflow: string;
  result: ArtifactResult;
  intermediate_analysis?: AnalysisResult | null;
  context_used?: ContextUsed | null;
};

// ── Topics ────────────────────────────────────────────────────────────────────

export type TopicSummary = {
  topic_id: string;
  topic_label: string;
  created_at: string;
  updated_at: string;
  root_run_id: string;
  latest_run_id: string;
  status: string;
  run_count: number;
};

export type TopicRunView = WorkMemoryRun & {
  available_actions: AvailableAction[];
};

export type WorkTopic = {
  topic_id: string;
  topic_label: string;
  created_at: string;
  updated_at: string;
  root_run_id: string;
  latest_run_id: string;
  run_ids: string[];
  status: string;
};

export type TopicDetailResponse = {
  topic: WorkTopic;
  runs: TopicRunView[];
  root_run?: TopicRunView | null;
  latest_run?: TopicRunView | null;
};

// ── Read responses ────────────────────────────────────────────────────────────

export type SourceSummaryResponse = {
  run_id: string;
  topic_id: string;
  result: SourceSummaryResult;
};

export type JiraReadResponse = {
  run_id: string;
  topic_id: string;
  result: JiraIssueResult;
};

export type ConfluenceReadResponse = {
  run_id: string;
  topic_id: string;
  result: ConfluencePageResult;
};
