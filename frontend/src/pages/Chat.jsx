import React from "react";
import ChatWindow from "../components/ChatWindow";

export default function Chat() {
  return (
    <div>
      <h1 className="text-2xl font-semibold mb-1">AI Learning Assistant</h1>
      <p className="text-slate-500 text-sm mb-6">
        Ask questions about your goal, recommendations, or plan.
      </p>
      <ChatWindow />
    </div>
  );
}
