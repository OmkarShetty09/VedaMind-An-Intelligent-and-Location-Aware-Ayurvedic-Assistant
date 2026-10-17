import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { errorMessage } from "../api/client.js";
import { MessageBubble } from "../components/chat/MessageBubble.jsx";
import { RoutineTimeline } from "../components/dinacharya/RoutineTimeline.jsx";
import chatReducer, {
  appendAssistantChunk,
  appendUserMessage,
  finishAssistantMessage,
  setStreamError,
  updateAssistantMessage,
} from "../store/chatSlice.js";

const run = (...actions) => actions.reduce(chatReducer, undefined);

describe("chatSlice turn handling", () => {
  it("attaches a guardrail event that arrives before any token to the assistant turn", () => {
    const guardrail = { decision: "caution", reason_code: "classical_caution" };
    const state = run(
      appendUserMessage("tell me about brahmi"),
      updateAssistantMessage({ guardrail }),
      appendAssistantChunk("Brahmi supports memory [S1]."),
      updateAssistantMessage({ citations: [{ id: "S1", source: "nighantus" }] }),
      finishAssistantMessage({ blocked: false, question: "tell me about brahmi" })
    );
    expect(state.messages).toHaveLength(2);
    const reply = state.messages[1];
    expect(reply.role).toBe("assistant");
    expect(reply.guardrail).toEqual(guardrail);
    expect(reply.content).toBe("Brahmi supports memory [S1].");
    expect(reply.citations).toHaveLength(1);
    expect(reply.streaming).toBe(false);
    expect(state.streaming).toBe(false);
  });

  it("records a blocked turn that produced no tokens", () => {
    const state = run(
      appendUserMessage("turmeric with warfarin?"),
      finishAssistantMessage({ blocked: true, guardrail: { decision: "block" } })
    );
    expect(state.messages[1]).toMatchObject({ role: "assistant", blocked: true, content: "" });
  });

  it("keeps the original question for the clarifying-question quick reply", () => {
    const state = run(
      appendUserMessage("suggest a herb for sleep"),
      updateAssistantMessage({ clarifying_question: "Are you on any medication?" }),
      finishAssistantMessage({ question: "suggest a herb for sleep" })
    );
    expect(state.messages[1].clarifying_question).toBe("Are you on any medication?");
    expect(state.messages[1].question).toBe("suggest a herb for sleep");
  });

  it("drops an empty assistant bubble when the stream fails", () => {
    const state = run(appendUserMessage("hi"), updateAssistantMessage({}), setStreamError("Could not reach the server."));
    expect(state.messages).toHaveLength(1);
    expect(state.error).toBe("Could not reach the server.");
    expect(state.streaming).toBe(false);
  });
});

describe("MessageBubble", () => {
  it("explains a blocked turn instead of rendering an empty bubble", () => {
    render(<MessageBubble message={{ role: "assistant", content: "", blocked: true }} />);
    expect(screen.getByText(/can't answer this one safely/i)).toBeInTheDocument();
  });
});

describe("answer formatting", () => {
  it("renders markdown headings/bold without raw symbols and links grouped citations", () => {
    const { container } = render(
      <MessageBubble
        message={{
          role: "assistant",
          content: "### Waking\n* **Rise early** before sunrise [S1, S2].",
          citations: [
            { id: "S1", source: "charaka_samhita" },
            { id: "S2", source: "ashtanga_hridaya" },
          ],
        }}
      />
    );
    expect(container.textContent).not.toMatch(/[#*]/);
    expect(container.querySelector("strong")?.textContent).toBe("Waking");
    expect(screen.getByText("[S1]")).toBeInTheDocument();
    expect(screen.getByText("[S2]")).toBeInTheDocument();
  });
});

describe("RoutineTimeline", () => {
  it("renders the fields the Dinacharya API returns", () => {
    render(
      <RoutineTimeline
        seasonInfo={{ key: "sharad", label: "Sharad (Autumn)", emoji: "" }}
        activities={[
          {
            title: "Main meal",
            start: "12:00:00",
            end: "13:30:00",
            description: "Eat your largest meal now.",
            reasons: ["Midday is the classical peak of agni."],
            citations: [{ source: "Charaka Samhita", ref: "Vimanasthana 1" }],
          },
        ]}
      />
    );
    expect(screen.getByText("Main meal")).toBeInTheDocument();
    expect(screen.getByText("12:00 – 13:30")).toBeInTheDocument();
    expect(screen.getByText("Charaka Samhita, Vimanasthana 1")).toBeInTheDocument();
    expect(screen.getByText(/Sharad/)).toBeInTheDocument();
  });
});

describe("errorMessage", () => {
  it("uses the backend message when present", () => {
    expect(errorMessage({ error: { message: "Invalid email or password." } }, 401)).toBe("Invalid email or password.");
  });

  it("turns DRF field errors into readable text", () => {
    const data = { error: { code: "invalid", message: null, fields: { password: ["This password is too short."] } } };
    expect(errorMessage(data, 400)).toBe("password: This password is too short.");
  });

  it("falls back to the status code", () => {
    expect(errorMessage(null, 502)).toBe("Request failed (502)");
  });
});
