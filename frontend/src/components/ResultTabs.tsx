import React, { useState } from "react";
import { PipelineResult } from "../types";
import { Code2, Table, Database, BarChart3, FileText, Terminal, Download } from "lucide-react";
import { cn } from "../lib/utils";
import Markdown from "react-markdown";
import { buildArtifactUrl } from "../lib/api";

interface ResultTabsProps {
  result: PipelineResult;
}

type TabType = "sql" | "results" | "metadata" | "chart" | "report" | "logs";

export function ResultTabs({ result }: ResultTabsProps) {
  const [activeTab, setActiveTab] = useState<TabType>("sql");

  const handleDownload = (artifactPath: string) => {
    window.open(buildArtifactUrl(artifactPath), "_blank", "noopener,noreferrer");
  };

  const tabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: "sql", label: "SQL", icon: <Code2 className="w-4 h-4" /> },
    { id: "results", label: "Results", icon: <Table className="w-4 h-4" /> },
    { id: "metadata", label: "Metadata", icon: <Database className="w-4 h-4" /> },
    { id: "chart", label: "Chart", icon: <BarChart3 className="w-4 h-4" /> },
    { id: "report", label: "Report", icon: <FileText className="w-4 h-4" /> },
    { id: "logs", label: "Logs", icon: <Terminal className="w-4 h-4" /> },
  ];

  return (
    <div className="mt-4 bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
      {/* Tab Header */}
      <div className="flex items-center gap-1 p-2 bg-slate-50 border-b border-slate-200 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap",
              activeTab === tab.id
                ? "bg-white text-blue-700 shadow-sm border border-slate-200/60"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50 border border-transparent"
            )}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === "sql" && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => handleDownload(result.artifactUrls.sql)}
                className="flex items-center gap-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-sm"
              >
                <Download className="w-4 h-4" /> Download SQL
              </button>
            </div>
            <div className="bg-slate-950 rounded-xl p-4 overflow-x-auto">
              <pre className="text-sm text-slate-50 font-mono leading-relaxed">
                <code>{result.sql}</code>
              </pre>
            </div>
          </div>
        )}

        {activeTab === "results" && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => handleDownload(result.artifactUrls.csv)}
                className="flex items-center gap-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-sm"
              >
                <Download className="w-4 h-4" /> Download CSV
              </button>
            </div>
            {result.csvData.length === 0 ? (
              <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center text-sm text-slate-500">
                No rows returned for this query.
              </div>
            ) : (
            <div className="border border-slate-200 rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left text-slate-600">
                  <thead className="text-xs text-slate-700 uppercase bg-slate-50 border-b border-slate-200">
                    <tr>
                      {Object.keys(result.csvData[0] || {}).map((key) => (
                        <th key={key} className="px-6 py-3 font-semibold">{key}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.csvData.map((row, i) => (
                      <tr key={i} className="bg-white border-b border-slate-100 last:border-0 hover:bg-slate-50 transition-colors">
                        {Object.values(row).map((val, j) => (
                          <td key={j} className="px-6 py-4 whitespace-nowrap">
                            {val === null || val === undefined ? "—" : String(val)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            )}
          </div>
        )}

        {activeTab === "metadata" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-bold text-slate-900">Raw Metadata</h3>
                <button
                  type="button"
                  onClick={() => handleDownload(result.artifactUrls.metadata)}
                  className="flex items-center gap-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-sm"
                >
                  <Download className="w-4 h-4" /> JSON
                </button>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 overflow-x-auto">
                <pre className="text-sm text-slate-700 font-mono">
                  <code>{JSON.stringify(result.metadata, null, 2)}</code>
                </pre>
              </div>
            </div>
            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-bold text-slate-900 mb-4">Summary</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
                    <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">Rows</p>
                    <p className="text-2xl font-bold text-slate-900">{result.metadata.rows_returned}</p>
                  </div>
                  <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
                    <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">Columns</p>
                    <p className="text-2xl font-bold text-slate-900">{result.metadata.columns?.length ?? 0}</p>
                  </div>
                  <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm col-span-2">
                    <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">Execution Time</p>
                    <p className="text-2xl font-bold text-slate-900">{result.metadata.execution_time_ms ?? 0} <span className="text-sm font-normal text-slate-500">ms</span></p>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 mb-3">Schema</h3>
                <div className="border border-slate-200 rounded-xl overflow-hidden">
                  <table className="w-full text-sm text-left text-slate-600">
                    <thead className="text-xs text-slate-700 uppercase bg-slate-50 border-b border-slate-200">
                      <tr>
                        <th className="px-4 py-2 font-semibold">Column</th>
                        <th className="px-4 py-2 font-semibold">Type</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(result.metadata.columns ?? []).map((col, i) => (
                        <tr key={i} className="bg-white border-b border-slate-100 last:border-0">
                          <td className="px-4 py-2 font-medium text-slate-900">{col.name}</td>
                          <td className="px-4 py-2 font-mono text-xs text-blue-600 bg-blue-50 rounded inline-block mt-1.5 mb-1.5 ml-4">{col.type}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "chart" && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => handleDownload(result.artifactUrls.chart)}
                className="flex items-center gap-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-sm"
              >
                <Download className="w-4 h-4" /> Download HTML
              </button>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-6 h-[500px] flex items-center justify-center shadow-sm">
              {result.chartHtml ? (
                <iframe
                  title={`${result.questionName}-chart`}
                  srcDoc={result.chartHtml}
                  sandbox="allow-scripts"
                  className="h-full w-full rounded-lg border border-slate-200"
                />
              ) : (
                <div className="text-sm text-slate-500">No chart was generated for this run.</div>
              )}
            </div>
          </div>
        )}

        {activeTab === "report" && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => handleDownload(result.artifactUrls.report)}
                className="flex items-center gap-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-sm"
              >
                <Download className="w-4 h-4" /> Download Markdown
              </button>
            </div>
            <div className="prose prose-slate max-w-none bg-white border border-slate-200 rounded-xl p-8 shadow-sm">
              <Markdown>{result.report}</Markdown>
            </div>
          </div>
        )}

        {activeTab === "logs" && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => handleDownload(result.artifactUrls.logs)}
                className="flex items-center gap-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-sm"
              >
                <Download className="w-4 h-4" /> Download Logs
              </button>
            </div>
            <div className="bg-slate-950 rounded-xl p-4 overflow-x-auto">
              <pre className="text-sm text-slate-400 font-mono leading-relaxed">
                <code>{result.logs}</code>
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
