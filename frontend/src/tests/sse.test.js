import { describe, expect, it } from "vitest";

import { parseFrame } from "../utils/sse.js";

describe("parseFrame", () => {
  it("parses an event + data frame", () => {
    const frame = "event: token\ndata: {\"delta\":\"hello\"}";
    expect(parseFrame(frame)).toEqual({ event: "token", data: { delta: "hello" } });
  });

  it("defaults to message event", () => {
    const frame = "data: {\"type\":\"done\"}";
    expect(parseFrame(frame).event).toBe("message");
  });

  it("joins multi-line data", () => {
    const frame = "data: {\"a\"\ndata: :\"b\"}";
    const parsed = parseFrame(frame);
    expect(parsed.data.a).toBe("b");
  });

  it("returns null when no data", () => {
    expect(parseFrame("event: ping")).toBeNull();
  });
});
