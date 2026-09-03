import { describe, expect, it } from "vitest";

import { MessageBubble } from "../components/chat/MessageBubble.jsx";
import { render, screen } from "@testing-library/react";

describe("MessageBubble", () => {
  it("renders user message right-aligned", () => {
    const { container } = render(<MessageBubble message={{ role: "user", content: "Hello" }} />);
    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(container.querySelector(".justify-end")).toBeTruthy();
  });

  it("renders assistant citations", () => {
    render(
      <MessageBubble
        message={{
          role: "assistant",
          content: "Answer [S1]",
          citations: [{ id: "S1", source: "charaka_samhita", chapter: "S1", verse: "v.5" }],
        }}
      />
    );
    expect(screen.getByText(/Answer/)).toBeInTheDocument();
    expect(screen.getByText(/\[S1\]/)).toBeInTheDocument();
    expect(screen.getByText(/charaka_samhita/)).toBeInTheDocument();
  });

  it("renders plain text for streaming messages", () => {
    render(
      <MessageBubble
        message={{
          role: "assistant",
          content: "Answer [S1]",
          streaming: true,
        }}
      />
    );
    expect(screen.getByText("Answer [S1]")).toBeInTheDocument();
  });
});
