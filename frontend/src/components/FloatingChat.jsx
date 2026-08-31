import React, { useState, useRef, useCallback, useEffect } from "react";
import ChatWindow from "./ChatWindow";

const ChatBubbleIcon = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" className={className} xmlns="http://www.w3.org/2000/svg">
    <path
      d="M4 5.5C4 4.67157 4.67157 4 5.5 4H18.5C19.3284 4 20 4.67157 20 5.5V14.5C20 15.3284 19.3284 16 18.5 16H9.5L5.5 19.5V16H5.5C4.67157 16 4 15.3284 4 14.5V5.5Z"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinejoin="round"
    />
  </svg>
);

const ExpandIcon = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" className={className} xmlns="http://www.w3.org/2000/svg">
    <path
      d="M9 4H4v5M15 4h5v5M9 20H4v-5M15 20h5v-5"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const CollapseIcon = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" className={className} xmlns="http://www.w3.org/2000/svg">
    <path
      d="M4 9h5V4M20 9h-5V4M4 15h5v5M20 15h-5v5"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const CloseIcon = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" className={className} xmlns="http://www.w3.org/2000/svg">
    <path d="M6 6L18 18M18 6L6 18" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
  </svg>
);

const NAVBAR_HEIGHT = 64; // px, matches Navbar's h-16
const PANEL_WIDTH_DEFAULT = 380;
const FULL_WIDTH_DEFAULT = 520;
const MIN_WIDTH = 320;

// "closed" -> just the round launcher button
// "panel"  -> small chat popup docked to the bottom-right corner
// "full"   -> chat docks along the right side, from below the navbar to
//             the bottom of the screen, with a draggable edge to resize width
export default function FloatingChat() {
  const [mode, setMode] = useState("closed");
  const [fullWidth, setFullWidth] = useState(FULL_WIDTH_DEFAULT);
  const draggingRef = useRef(false);

  const isFull = mode === "full";

  const onDragStart = useCallback((e) => {
    draggingRef.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
    e.preventDefault();
  }, []);

  useEffect(() => {
    function onMove(e) {
      if (!draggingRef.current) return;
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const maxWidth = window.innerWidth - 80; // keep a sliver of the page visible
      const next = Math.min(maxWidth, Math.max(MIN_WIDTH, window.innerWidth - clientX));
      setFullWidth(next);
    }
    function onUp() {
      if (!draggingRef.current) return;
      draggingRef.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    }
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    window.addEventListener("touchmove", onMove);
    window.addEventListener("touchend", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
      window.removeEventListener("touchmove", onMove);
      window.removeEventListener("touchend", onUp);
    };
  }, []);

  if (mode === "closed") {
    return (
      <button
        onClick={() => setMode("panel")}
        aria-label="Open AI assistant"
        className="fixed bottom-5 right-5 z-40 w-14 h-14 rounded-full bg-brand-600 text-white shadow-lg shadow-brand-600/30 flex items-center justify-center hover:bg-brand-700 transition-colors"
      >
        <ChatBubbleIcon className="w-6 h-6" />
      </button>
    );
  }

  return (
    <div
      style={
        isFull
          ? { top: NAVBAR_HEIGHT, width: fullWidth }
          : { width: Math.min(PANEL_WIDTH_DEFAULT, window.innerWidth - 40) }
      }
      className={
        isFull
          ? "fixed right-0 bottom-0 z-40 flex flex-col bg-white border-l border-slate-200 shadow-2xl overflow-hidden"
          : "fixed bottom-5 right-5 z-40 h-[32rem] max-h-[calc(100vh-2.5rem)] flex flex-col bg-white border border-slate-200 rounded-2xl shadow-2xl overflow-hidden"
      }
    >
      {/* drag handle to resize width, only shown in "full" mode */}
      {isFull && (
        <div
          onMouseDown={onDragStart}
          onTouchStart={onDragStart}
          className="absolute top-0 left-0 bottom-0 w-1.5 -ml-0.5 cursor-col-resize z-10 group"
        >
          <div className="w-full h-full group-hover:bg-brand-300 transition-colors" />
        </div>
      )}

      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 bg-white shrink-0">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-7 h-7 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center shrink-0">
            <ChatBubbleIcon className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-slate-800 leading-tight truncate">AI Assistant</p>
            <p className="text-xs text-slate-500 leading-tight truncate">Ask about your learning plan</p>
          </div>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          <button
            onClick={() => setMode(isFull ? "panel" : "full")}
            aria-label={isFull ? "Collapse" : "Expand"}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:bg-slate-100 hover:text-slate-800 transition-colors"
          >
            {isFull ? <CollapseIcon className="w-4 h-4" /> : <ExpandIcon className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setMode("closed")}
            aria-label="Close"
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:bg-slate-100 hover:text-slate-800 transition-colors"
          >
            <CloseIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
      <ChatWindow className="flex-1 min-h-0" />
    </div>
  );
}