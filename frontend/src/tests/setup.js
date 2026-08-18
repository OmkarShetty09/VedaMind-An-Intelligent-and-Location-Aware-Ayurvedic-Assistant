import "@testing-library/jest-dom/vitest";

window.matchMedia = window.matchMedia || (() => ({
  matches: false,
  addListener: () => {},
  removeListener: () => {},
  addEventListener: () => {},
  removeEventListener: () => {},
}));

globalThis.IS_REACT_ACT_ENVIRONMENT = true;
