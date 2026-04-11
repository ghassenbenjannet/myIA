export type AvailableAction = "refine_analysis" | "draft_ticket" | "draft_documentation";

export type AnalysisResult = {
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
  recommended_next_step?: string | null;
};

export type TicketResult = {
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
  title: string;
  document_type?: string | null;
  summary?: string | null;
  context?: string | null;
  sections: DocumentationSection[];
};

export type SourceSummaryResult = {
  source_type: string;
  source_ref: string;
  source_title?: string | null;
  summary: string;
  key_points: string[];
  open_questions: string[];
  next_step_hint?: string | null;
};

export type JiraIssueResult = {
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

export type ProcessResult = AnalysisResult | TicketResult | DocumentationResult;

export type ProcessResponse = {
  run_id: string;
  topic_id: string;
  request_type: string;
  selected_workflow: string;
  confidence: number;
  result: ProcessResult;
  intermediate_analysis?: AnalysisResult | null;
  context_used?: ContextUsed | null;
  quality_checks: string[];
  warnings: string[];
};

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
  result: AnalysisResult | TicketResult | DocumentationResult | SourceSummaryResult | JiraIssueResult | ConfluencePageResult;
  intermediate_analysis?: AnalysisResult | null;
  context_used?: ContextUsed | null;
};

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
