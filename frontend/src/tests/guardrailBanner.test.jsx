import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { GuardrailWarningBanner } from "../components/chat/GuardrailWarningBanner.jsx";

describe("GuardrailWarningBanner", () => {
  it("renders nothing for a pass decision", () => {
    const { container } = render(<GuardrailWarningBanner decision={{ decision: "pass" }} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders a caution message", () => {
    render(<GuardrailWarningBanner decision={{ decision: "caution", reason_code: "classical_only" }} />);
    expect(screen.getByText(/caution/i)).toBeInTheDocument();
  });

  it("renders a block message with reason code", () => {
    render(<GuardrailWarningBanner decision={{ decision: "block", reason_code: "pregnancy_high_risk" }} />);
    expect(screen.getByText(/safety/i)).toBeInTheDocument();
    expect(screen.getByText(/pregnancy_high_risk/)).toBeInTheDocument();
  });
});
