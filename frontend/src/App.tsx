import React, { useCallback, useEffect, useRef, useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { ChatArea } from "./components/ChatArea";
import { PipelineInput } from "./components/PipelineInput";
import { AppState } from "./types";
import { clearHistory, fetchConfig, fetchHistory, fetchResult } from "./lib/api";

export default function App() {
  const activeResultRequestRef = useRef<string | null>(null);
  const [state, setState] = useState<AppState>({
    databases: [],
    schemas: [],
    providers: [],
    selectedDatabase: "",
    selectedSchema: "",
    selectedProvider: "gemini",
    overwriteExisting: false,
    history: [],
    activeResultId: null,
    activeResult: null,
    isLoading: false,
    isBootstrapping: true,
    errorMessage: null,
  });

  const refreshConfiguration = useCallback(async (preserveSelection = true) => {
    const [config, history] = await Promise.all([fetchConfig(), fetchHistory()]);

    setState((prev) => {
      const nextActiveResultId = preserveSelection && prev.activeResultId
        ? prev.activeResultId
        : (history[0]?.id ?? null);

      return {
        ...prev,
        databases: config.databases,
        schemas: config.schemas,
        providers: config.providers,
        selectedDatabase: preserveSelection && prev.selectedDatabase
          ? prev.selectedDatabase
          : config.selectedDatabase,
        selectedSchema: preserveSelection && prev.selectedSchema
          ? prev.selectedSchema
          : config.selectedSchema,
        selectedProvider: preserveSelection && prev.selectedProvider
          ? prev.selectedProvider
          : config.selectedProvider,
        history,
        activeResultId: nextActiveResultId,
        activeResult: prev.activeResult?.id === nextActiveResultId ? prev.activeResult : null,
        errorMessage: null,
      };
    });
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        await refreshConfiguration(false);
        if (cancelled) {
          return;
        }
        setState((prev) => ({
          ...prev,
          isBootstrapping: false,
        }));
      } catch (error) {
        if (cancelled) {
          return;
        }
        setState((prev) => ({
          ...prev,
          isBootstrapping: false,
          errorMessage: error instanceof Error ? error.message : "Unable to load the application.",
        }));
      }
    }

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, [refreshConfiguration]);

  useEffect(() => {
    if (!state.selectedDatabase) {
      return;
    }

    let cancelled = false;

    async function refreshSchemas() {
      try {
        const config = await fetchConfig(state.selectedDatabase);
        if (cancelled) {
          return;
        }

        setState((prev) => {
          const selectedSchema = config.schemas.includes(prev.selectedSchema)
            ? prev.selectedSchema
            : (config.selectedSchema || config.schemas[0] || "");

          return {
            ...prev,
            schemas: config.schemas,
            selectedSchema,
            errorMessage: prev.errorMessage,
          };
        });
      } catch (error) {
        if (cancelled) {
          return;
        }
        setState((prev) => ({
          ...prev,
          errorMessage: error instanceof Error ? error.message : "Unable to refresh schemas.",
        }));
      }
    }

    void refreshSchemas();
    return () => {
      cancelled = true;
    };
  }, [state.selectedDatabase]);

  useEffect(() => {
    if (!state.activeResultId) {
      return;
    }
    if (state.activeResult?.id === state.activeResultId) {
      return;
    }
    if (activeResultRequestRef.current === state.activeResultId) {
      return;
    }

    let cancelled = false;
    activeResultRequestRef.current = state.activeResultId;

    async function loadActiveResult() {
      try {
        const result = await fetchResult(state.activeResultId as string);
        if (cancelled) {
          return;
        }
        setState((prev) => ({
          ...prev,
          activeResult: result,
          errorMessage: null,
        }));
      } catch (error) {
        if (cancelled) {
          return;
        }
        setState((prev) => ({
          ...prev,
          errorMessage: error instanceof Error ? error.message : "Unable to load the selected result.",
        }));
      } finally {
        activeResultRequestRef.current = null;
      }
    }

    void loadActiveResult();
    return () => {
      cancelled = true;
      activeResultRequestRef.current = null;
    };
  }, [state.activeResultId, state.activeResult]);

  const handleClearHistory = useCallback(async () => {
    await clearHistory();
    setState((prev) => ({
      ...prev,
      history: [],
      activeResultId: null,
      activeResult: null,
      errorMessage: null,
    }));
  }, []);

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">
      <Sidebar
        state={state}
        setState={setState}
        onRefresh={() => void refreshConfiguration(true)}
        onClearHistory={() => void handleClearHistory()}
      />
      <main className="flex-1 flex flex-col relative">
        <ChatArea state={state} />
        <PipelineInput state={state} setState={setState} />
      </main>
    </div>
  );
}
