import React, { useEffect, useRef, useState } from "react";
import { chatService } from "../services/resources";
import { getErrorMessage } from "../services/api";

const SUGGESTIONS = [
  "What should I learn today?",
  "How close am I to my goal?",
  "I only have 5 hours this week, modify my plan.",
  "I'm struggling with this topic.",
];

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    chatService
      .history()
      .then((res) => setMessages(res.data))
      .catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage(text) {
    const message = (text ?? input).trim();
    if (!message || sending) return;
    setError("");
    setInput("");
    setMessages((m) => [...m, { id: `local-${Date.now()}`, role: "user", content: message }]);
    setSending(true);
    try {
      const res = await chatService.send(message, sessionId);
      setSessionId(res.data.session_id);
      setMessages((m) => [
        ...m,
        { id: `local-${Date.now()}-r`, role: "assistant", content: res.data.reply },
      ]);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-11rem)] bg-white border border-slate-200 rounded-xl overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center gap-3 text-slate-500">
            <div className="text-3xl">💬</div>
            <p className="font-medium text-slate-700">Ask your AI learning assistant anything</p>
            <div className="flex flex-wrap gap-2 justify-center max-w-md">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => sendMessage(s)}
                  className="text-xs px-3 py-1.5 rounded-full border border-slate-200 hover:bg-slate-50"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap ${
                m.role === "user"
                  ? "bg-brand-600 text-white rounded-br-sm"
                  : "bg-slate-100 text-slate-800 rounded-bl-sm"
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex justify-start">
            <div className="bg-slate-100 text-slate-500 rounded-2xl rounded-bl-sm px-4 py-2.5 text-sm">
              Thinking…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      {error && <p className="text-xs text-rose-600 px-4">{error}</p>}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          sendMessage();
        }}
        className="border-t border-slate-200 p-3 flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your learning path..."
          className="flex-1 border border-slate-200 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-200"
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="px-4 py-2 rounded-full bg-brand-600 text-white text-sm font-medium disabled:opacity-40"
        >
          Send
        </button>
      </form>
    </div>
  );
}
