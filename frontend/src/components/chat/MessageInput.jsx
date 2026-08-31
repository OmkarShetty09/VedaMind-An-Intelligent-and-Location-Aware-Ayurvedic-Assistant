import { useState } from "react";

import { Spinner } from "../common/Button.jsx";

export function MessageInput({ onSend, disabled, placeholder = "Ask about herbs, daily routines, seasons..." }) {
  const [text, setText] = useState("");

  const submit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text);
    setText("");
  };

  return (
    <form onSubmit={submit} className="flex items-end gap-3 border-t border-line bg-surface p-4">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit(e);
          }
        }}
        rows={2}
        disabled={disabled}
        placeholder={placeholder}
        className="flex-1 resize-none rounded-xl border border-line bg-white px-4 py-3 text-sm leading-relaxed outline-none transition-all duration-150 placeholder:text-text-faint focus:border-brand focus:ring-2 focus:ring-brand/10 disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={!text.trim() || disabled}
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand text-white shadow-sm transition-all duration-150 hover:bg-brand-dark hover:shadow-md disabled:opacity-40 disabled:hover:bg-brand disabled:hover:shadow-sm"
        aria-label="Send message"
      >
        {disabled ? (
          <Spinner size="sm" className="text-white" />
        ) : (
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
          </svg>
        )}
      </button>
    </form>
  );
}
