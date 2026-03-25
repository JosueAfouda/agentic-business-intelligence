import React from "react";
import { AppState } from "../types";
import { ResultTabs } from "./ResultTabs";
import { Bot, User } from "lucide-react";
import { motion } from "motion/react";

interface ChatAreaProps {
  state: AppState;
}

export function ChatArea({ state }: ChatAreaProps) {
  const activeResult = state.activeResult;

  if (state.isBootstrapping) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 text-slate-500">
        Loading Agentic BI...
      </div>
    );
  }

  if (state.activeResultId && !activeResult) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 text-slate-500">
        Loading selected result...
      </div>
    );
  }

  if (!activeResult) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-center p-8 overflow-y-auto pb-48">
        {state.errorMessage ? (
          <div className="mb-6 max-w-2xl rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-left text-sm text-rose-700 shadow-sm">
            {state.errorMessage}
          </div>
        ) : null}
        <img 
          src="https://raw.githubusercontent.com/JosueAfouda/agentic-business-intelligence/main/agent_bi.png" 
          alt="Agentic BI Architecture" 
          className="w-full max-w-4xl rounded-2xl shadow-sm border border-slate-200 mb-8 object-contain bg-white p-2"
          referrerPolicy="no-referrer"
        />
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Ready to analyze your data</h2>
        <p className="text-slate-500 max-w-md">
          Select a database and schema from the sidebar, then ask a business question below to generate SQL, charts, and insights.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-8 pb-48">
      {/* User Message */}
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-end"
      >
        <div className="flex gap-4 max-w-[80%]">
          <div className="bg-blue-600 text-white px-6 py-4 rounded-2xl rounded-tr-sm shadow-sm">
            <p className="text-[15px] leading-relaxed">{activeResult.questionText}</p>
          </div>
          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center shrink-0 border border-blue-200">
            <User className="w-5 h-5 text-blue-700" />
          </div>
        </div>
      </motion.div>

      {/* Assistant Message */}
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex justify-start"
      >
        <div className="flex gap-4 max-w-[95%] w-full">
          <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center shrink-0 border border-slate-200">
            <Bot className="w-5 h-5 text-slate-700" />
          </div>
          <div className="w-full space-y-4">
            <div className="bg-white border border-slate-200 px-6 py-4 rounded-2xl rounded-tl-sm shadow-sm inline-block">
              <p className="text-[15px] text-slate-700 leading-relaxed">
                Pipeline executed on <strong className="text-slate-900">{activeResult.databaseName}.{activeResult.schemaName}</strong>.<br />
                Requested provider: <strong className="text-slate-900">{activeResult.providerName}</strong>.<br />
                Artifacts available in <code className="bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded text-sm">outputs/{activeResult.questionName}/</code>.
              </p>
            </div>

            {state.errorMessage ? (
              <div className="rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700 shadow-sm">
                {state.errorMessage}
              </div>
            ) : null}
            
            <ResultTabs result={activeResult} />
          </div>
        </div>
      </motion.div>
    </div>
  );
}
