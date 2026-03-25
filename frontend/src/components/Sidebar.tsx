import React from "react";
import { Database, LayoutTemplate, Cpu, RefreshCw, History, FileText, Settings2 } from "lucide-react";
import { AppState } from "../types";
import { cn } from "../lib/utils";

interface SidebarProps {
  state: AppState;
  setState: React.Dispatch<React.SetStateAction<AppState>>;
  onRefresh: () => void;
}

export function Sidebar({ state, setState, onRefresh }: SidebarProps) {
  return (
    <aside className="w-72 bg-white border-r border-slate-200 flex flex-col h-screen overflow-y-auto">
      <div className="p-5 border-b border-slate-100">
        <div className="flex items-center gap-2 text-blue-600 mb-1">
          <div className="bg-blue-100 p-1.5 rounded-lg">
            <Settings2 className="w-5 h-5" />
          </div>
          <h1 className="font-semibold text-lg text-slate-900 tracking-tight">Agentic BI</h1>
        </div>
        <p className="text-xs text-slate-500 font-medium">Business Intelligence Pipeline</p>
      </div>

      <div className="p-5 flex-1 flex flex-col gap-6">
        {/* Configuration Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Configuration</h2>
            <button
              type="button"
              onClick={onRefresh}
              className="text-slate-400 hover:text-blue-600 transition-colors"
              title="Refresh databases"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                <Database className="w-4 h-4 text-slate-400" /> Database
              </label>
              <select
                className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block p-2.5 outline-none transition-all"
                value={state.selectedDatabase}
                onChange={(e) =>
                  setState({
                    ...state,
                    selectedDatabase: e.target.value,
                    selectedSchema: "",
                  })
                }
              >
                {state.databases.map((db) => (
                  <option key={db} value={db}>{db}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                <LayoutTemplate className="w-4 h-4 text-slate-400" /> Schema
              </label>
              <select
                className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block p-2.5 outline-none transition-all"
                value={state.selectedSchema}
                onChange={(e) => setState({ ...state, selectedSchema: e.target.value })}
              >
                {state.schemas.map((schema) => (
                  <option key={schema} value={schema}>{schema}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-slate-400" /> LLM Provider
              </label>
              <select
                className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block p-2.5 outline-none transition-all"
                value={state.selectedProvider}
                onChange={(e) => setState({ ...state, selectedProvider: e.target.value })}
              >
                {state.providers.map((provider) => (
                  <option key={provider} value={provider}>{provider}</option>
                ))}
              </select>
            </div>

            <label className="flex items-center gap-2 cursor-pointer mt-4 group">
              <div className="relative">
                <input
                  type="checkbox"
                  className="sr-only"
                  checked={state.overwriteExisting}
                  onChange={(e) => setState({ ...state, overwriteExisting: e.target.checked })}
                />
                <div className={cn(
                  "block w-10 h-6 rounded-full transition-colors",
                  state.overwriteExisting ? "bg-blue-600" : "bg-slate-200"
                )}></div>
                <div className={cn(
                  "absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform",
                  state.overwriteExisting ? "transform translate-x-4" : ""
                )}></div>
              </div>
              <span className="text-sm font-medium text-slate-700 group-hover:text-slate-900 transition-colors">
                Overwrite existing
              </span>
            </label>
          </div>
        </div>

        {/* History Section */}
        <div className="space-y-4 mt-4">
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
            <History className="w-3.5 h-3.5" /> History
          </h2>
          
          {state.history.length === 0 ? (
            <p className="text-sm text-slate-500 italic">No previous runs.</p>
          ) : (
            <div className="space-y-2">
              {state.history.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() =>
                    setState({
                      ...state,
                      activeResultId: item.id,
                      activeResult: state.activeResult?.id === item.id ? state.activeResult : null,
                    })
                  }
                  className={cn(
                    "w-full text-left p-3 rounded-xl border transition-all flex flex-col gap-1",
                    state.activeResultId === item.id
                      ? "bg-blue-50 border-blue-200 shadow-sm"
                      : "bg-white border-slate-100 hover:border-slate-300 hover:bg-slate-50"
                  )}
                >
                  <div className="flex items-start justify-between">
                    <span className="text-sm font-semibold text-slate-900 truncate pr-2">
                      {item.questionName}
                    </span>
                    <FileText className={cn(
                      "w-4 h-4 shrink-0",
                      state.activeResultId === item.id ? "text-blue-500" : "text-slate-400"
                    )} />
                  </div>
                  <span className="text-xs text-slate-500 truncate">
                    {item.databaseName}.{item.schemaName}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
