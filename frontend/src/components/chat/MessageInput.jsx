import { useState } from "react";

import { Button } from "../common/Button.jsx";

export function MessageInput({ onSend, disabled, placeholder = "Ask about herbs, daily routines, seasons..." }) {
  const [text, setText] = useState("");

  const submit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text);
    setText("");
  };

  return (
    <form onSubmit={submit} className="flex items-end gap-2 border-t border-line bg-surface p-3">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) submit(e);
        }}
        rows={2}
        disabled={disabled}
        placeholder={placeholder}
        className="flex-1 resize-none rounded-xl border border-line bg-white px-3 py-2 text-sm outline-none focus:border-brand disabled:opacity-50"
      />
      <Button type="submit" disabled={!text.trim() || disabled}>
        Send
      </Button>
    </form>
  );
}
