import React, { createContext, useCallback, useContext, useState } from "react";

export function LoadingState({ label = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-slate-500 gap-3">
      <div className="w-8 h-8 border-3 border-brand-200 border-t-brand-600 rounded-full animate-spin" />
      <p className="text-sm">{label}</p>
    </div>
  );
}

export function ErrorState({ message = "Something went wrong.", onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center gap-3">
      <div className="w-12 h-12 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center text-xl">!</div>
      <p className="text-sm text-slate-600 max-w-sm">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-sm font-medium text-brand-600 hover:underline"
        >
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ icon = "📭", title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center gap-2 bg-white border border-dashed border-slate-200 rounded-xl">
      <div className="text-3xl">{icon}</div>
      <p className="font-medium text-slate-800">{title}</p>
      {description && <p className="text-sm text-slate-500 max-w-sm">{description}</p>}
      {action}
    </div>
  );
}

// ---- Toast system ----
const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, type = "info") => {
    const id = Math.random().toString(36).slice(2);
    setToasts((t) => [...t, { id, message, type }]);
    setTimeout(() => {
      setToasts((t) => t.filter((toast) => toast.id !== id));
    }, 3500);
  }, []);

  const typeStyles = {
    info: "bg-slate-800",
    success: "bg-emerald-600",
    error: "bg-rose-600",
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 items-end">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`text-white text-sm font-medium px-4 py-2.5 rounded-lg shadow-lg ${typeStyles[t.type] || typeStyles.info}`}
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
