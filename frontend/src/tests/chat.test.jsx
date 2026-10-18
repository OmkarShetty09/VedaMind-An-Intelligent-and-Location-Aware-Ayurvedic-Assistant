import { describe, expect, it } from "vitest";

import { MessageBubble } from "../components/chat/MessageBubble.jsx";
import { fireEvent, render, screen } from "@testing-library/react";

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

  it("opens a source to show the full passage and a link", () => {
    render(
      <MessageBubble
        message={{
          role: "assistant",
          content: "Ashwagandha is a rasayana [S1].",
          citations: [
            {
              id: "S1",
              source: "ayurwiki_herbs",
              title: "Ayurwiki Herbs",
              chapter: "Withania somnifera",
              excerpt: "Ashwagandha root is used as a rasayana.",
              url: "https://ayurwiki.org/index.php?search=Withania",
              references: ["https://pubmed.ncbi.nlm.nih.gov/1/"],
            },
          ],
        }}
      />
    );
    expect(screen.queryByText("Ashwagandha root is used as a rasayana.")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Ayurwiki Herbs · Withania somnifera/ }));
    expect(screen.getByText("Ashwagandha root is used as a rasayana.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Open source/ })).toHaveAttribute(
      "href",
      "https://ayurwiki.org/index.php?search=Withania"
    );
    expect(screen.getByRole("link", { name: /pubmed/ })).toHaveAttribute("target", "_blank");
  });

  it("shows what not to take it with under the answer", () => {
    render(
      <MessageBubble
        message={{
          role: "assistant",
          content: "Turmeric supports digestion.",
          cautions: {
            herbs: ["turmeric"],
            items: [
              {
                herb: "turmeric",
                avoid_with: "Warfarin",
                kind: "medicine",
                severity: "high",
                evidence: "theoretical",
                recommendation: "Do not take therapeutic-dose turmeric with warfarin.",
                source_uri: "https://pubmed.ncbi.nlm.nih.gov/10484074/",
                examples: [],
                applies_to_you: true,
              },
            ],
            general: "Taking any modern (allopathic) medicine? Tell your doctor.",
            note: "",
          },
        }}
      />
    );
    expect(screen.getByText("What not to take it with")).toBeInTheDocument();
    expect(screen.getByText("Warfarin")).toBeInTheDocument();
    expect(screen.getByText("You take this")).toBeInTheDocument();
    expect(screen.getByText(/allopathic/)).toBeInTheDocument();
  });
});
