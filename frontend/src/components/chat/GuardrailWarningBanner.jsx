const config = {
  block: { tone: "border-red-200 bg-red-50 text-red-800", icon: "⛔" },
  needs_review: { tone: "border-red-200 bg-red-50 text-red-800", icon: "⚠️" },
  caution: { tone: "border-amber-200 bg-amber-50 text-amber-800", icon: "⚠️" },
  pass: { tone: "border-green-200 bg-green-50 text-green-800", icon: "✓" },
};

const messages = {
  block: "This request was not answered for your safety. Please consult a qualified practitioner.",
  needs_review: "We could not safely verify this. Please consult a qualified practitioner.",
  caution: "Answer provided with caution. This is general wellness information only.",
};

// Reason codes from the rules engine / RAG pipeline, in words a user understands.
const reasonText = {
  interaction_high_or_severe: "A serious herb–drug interaction was found.",
  interaction_moderate: "A moderate herb–drug interaction was found.",
  interaction_low_severity: "A minor herb–drug interaction is possible.",
  classical_caution: "Classical texts advise caution here.",
  polypharmacy_compounded: "Several interactions add up with your medications.",
  novel_pair_unverified: "This herb–medication combination is not in our verified interaction database.",
  entity_ambiguous: "We couldn't identify one of the herbs or medicines with confidence.",
  engine_error_fail_closed: "The safety check could not run, so we didn't answer.",
  jailbreak_attempt: "This request looks like an attempt to bypass the safety checks.",
  secondary_escalation: "A safety concern was flagged by our secondary review.",
  herb_drug_interaction: "A potential herb-drug interaction was detected.",
};

export function GuardrailWarningBanner({ decision }) {
  if (!decision || decision.decision === "pass") return null;
  const { tone, icon } = config[decision.decision] || config.caution;
  const reason = reasonText[decision.reason_code];
  const matches = (decision.matches || []).filter((m) => m.pair || m.recommendation);

  return (
    <div className={`mb-3 flex items-start gap-3 rounded-xl border px-4 py-3 text-sm ${tone}`}>
      <span className="mt-0.5 text-base">{icon}</span>
      <div className="flex-1">
        <p className="font-medium">{messages[decision.decision] || "Safety notice."}</p>
        {reason && <p className="mt-1 text-xs opacity-90">{reason}</p>}
        {matches.length > 0 && (
          <ul className="mt-1.5 space-y-1 text-xs opacity-90">
            {matches.map((m, i) => (
              <li key={i}>
                {m.pair && <span className="font-semibold">{m.pair}: </span>}
                {m.recommendation}
              </li>
            ))}
          </ul>
        )}
        {decision.message && <p className="mt-1 text-xs opacity-90">{decision.message}</p>}
        {decision.reason_code && !reason && <p className="mt-0.5 text-xs opacity-80">Code: {decision.reason_code}</p>}
      </div>
    </div>
  );
}
