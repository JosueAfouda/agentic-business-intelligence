import React, { useState } from "react";
import { Sparkles, Loader2 } from "lucide-react";
import { AppState } from "../types";
import { runPipeline } from "../lib/api";

interface PipelineInputProps {
  state: AppState;
  setState: React.Dispatch<React.SetStateAction<AppState>>;
}

export function PipelineInput({ state, setState }: PipelineInputProps) {
  const [question, setQuestion] = useState("");
  const [artifactName, setArtifactName] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setState((prev) => ({ ...prev, isLoading: true, errorMessage: null }));

    try {
      const newResult = await runPipeline({
        questionText: question,
        artifactName,
        databaseName: state.selectedDatabase,
        schemaName: state.selectedSchema,
        providerName: state.selectedProvider,
        overwriteExisting: state.overwriteExisting,
      });

      setState((prev) => {
        const nextHistory = [
          {
            id: newResult.id,
            questionName: newResult.questionName,
            questionText: newResult.questionText,
            databaseName: newResult.databaseName,
            schemaName: newResult.schemaName,
            providerName: newResult.providerName,
            timestamp: newResult.timestamp,
          },
          ...prev.history.filter((item) => item.id !== newResult.id),
        ];

        return {
          ...prev,
          isLoading: false,
          history: nextHistory,
          activeResultId: newResult.id,
          activeResult: newResult,
          errorMessage: null,
        };
      });
      setQuestion("");
      setArtifactName("");
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        errorMessage: error instanceof Error ? error.message : "Pipeline execution failed.",
      }));
    }
  };

  return (
    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-slate-50 via-slate-50 to-transparent pt-10 pb-6 px-6">
      <div className="max-w-4xl mx-auto">
        <form 
          onSubmit={handleSubmit}
          className="bg-white border border-slate-200 rounded-2xl shadow-lg shadow-slate-200/50 overflow-hidden transition-all focus-within:border-blue-400 focus-within:ring-4 focus-within:ring-blue-50"
        >
          <div className="p-4">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a business question... (e.g., What are the top 5 movies by revenue?)"
              className="w-full resize-none outline-none text-slate-900 placeholder:text-slate-400 text-[15px] min-h-[80px]"
              disabled={state.isLoading || state.isBootstrapping}
            />
          </div>
          
          <div className="bg-slate-50 border-t border-slate-100 px-4 py-3 flex items-center justify-between gap-4">
            <div className="flex-1 max-w-xs">
              <input
                type="text"
                value={artifactName}
                onChange={(e) => setArtifactName(e.target.value)}
                placeholder="Artifact name (optional)"
                className="w-full bg-white border border-slate-200 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block px-3 py-2 outline-none transition-all"
                disabled={state.isLoading || state.isBootstrapping}
              />
            </div>
            
            <button
              type="submit"
              disabled={!question.trim() || state.isLoading || state.isBootstrapping}
              className="flex items-center gap-2 bg-blue-600 text-white px-6 py-2.5 rounded-xl font-medium hover:bg-blue-700 focus:ring-4 focus:ring-blue-100 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {state.isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Ask
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
