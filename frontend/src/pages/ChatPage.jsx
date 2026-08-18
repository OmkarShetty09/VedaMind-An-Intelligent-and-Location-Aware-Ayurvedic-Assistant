import { ChatWindow } from "../components/chat/ChatWindow.jsx";

export function ChatPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-text">Ask VedaMind</h1>
        <p className="mt-1 text-sm text-text-muted">
          Grounded in classical texts, with safety checks on every answer.
        </p>
      </div>
      <ChatWindow />
    </div>
  );
}
