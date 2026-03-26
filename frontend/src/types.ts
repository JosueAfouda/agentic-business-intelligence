export interface PipelineResultSummary {
  id: string;
  questionName: string;
  questionText: string;
  databaseName: string;
  schemaName: string;
  providerName: string;
  timestamp: number;
}

export interface ArtifactUrls {
  sql: string;
  csv: string;
  metadata: string;
  chart: string;
  report: string;
  logs: string;
}

export interface PipelineResult extends PipelineResultSummary {
  sql: string;
  csvData: Record<string, unknown>[];
  metadata: {
    question?: string;
    rows_returned: number;
    columns: Array<{ name: string; type: string }>;
    sql_file?: string;
    database?: string;
    schema?: string;
    execution_time_ms?: number;
    query_hash?: string;
  };
  report: string;
  logs: string;
  chartHtml: string;
  artifactUrls: ArtifactUrls;
}

export interface AppState {
  databases: string[];
  schemas: string[];
  providers: string[];
  selectedDatabase: string;
  selectedSchema: string;
  selectedProvider: string;
  overwriteExisting: boolean;
  history: PipelineResultSummary[];
  activeResultId: string | null;
  activeResult: PipelineResult | null;
  isLoading: boolean;
  isBootstrapping: boolean;
  errorMessage: string | null;
}
