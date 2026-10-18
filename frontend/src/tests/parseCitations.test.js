import { describe, expect, it } from "vitest";

import { parseCitations } from "../utils/parseCitations.js";

describe("parseCitations", () => {
  it("reads ASCII and full-width citation brackets", () => {
    const ids = (text) => parseCitations(text).filter((s) => s.type === "citation").map((s) => s.id);
    expect(ids("A [S1]. B [S2, S3].")).toEqual(["S1", "S2", "S3"]);
    expect(ids("A【S1】. B［S4］. C【S5、S6】")).toEqual(["S1", "S4", "S5", "S6"]);
    expect(parseCitations("A【S1】 done")[0]).toEqual({ type: "text", value: "A" });
  });
});
