const config = {
  block: { tone: "border-red-300 bg-red-50 text-red-800", icon: "⛔" },
  needs_review: { tone: "border-red-300 bg-red-50 text-red-800", icon: "⚠️" },
  caution: { tone: "border-amber-300 bg-amber-50 text-amber-800", icon: "⚠️" },
  pass: { tone: "border-green-300 bg-green-50 text-green-800", icon: "✓" },
};

export function GuardrailWarningBanner({ decision }) {
  if (!decision || decision.decision === "pass") return null;
  const { tone, icon } = config[decision.decision] || config.caution;
  const messages = {
    block: "This request was not answered for your safety. Please consult a qualified practitioner.",
    needs_review: "We could not safely verify this. Please consult a qualified practitioner.",
    caution: "Answer provided with caution. This is general wellness information only.",
  };
  return (
    <div className={`flex items-start gap-2 rounded-xl border px-4 py-3 text-sm ${tone}`}>
      <span className="text-base">{icon}</span>
      <div>
        <p className="font-medium">{messages[decision.decision] || "Safety notice."}</p>
        {decision.reason_code && <p className="mt-0.5 text-xs opacity-80">Code: {decision.reason_code}</p>}
      </div>
    </div>
  );
}
