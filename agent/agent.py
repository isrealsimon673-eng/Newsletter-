import json
import os
import re
from typing import Dict, List, Optional

class BusinessGrowthAgent:
    """A lightweight, extensible agent for business growth strategy.

    This implementation is intentionally rule-based to provide a working
    offline MVP without external API keys. It is structured so an LLM
    or external retriever can be slotted in later.
    """

    def __init__(self, mode: str = "rule", llm_client: Optional[object] = None):
        """Create an agent.

        mode: 'rule' (default) for rule-based behavior, or 'llm' to delegate
        strategy generation to an LLM client instance passed in `llm_client`.
        """
        self.mode = mode
        self.llm_client = llm_client

    def analyze_company(self, text: str) -> Dict:
        """Extract simple signals from a free-text company profile."""
        profile = {
            "raw": text.strip(),
            "tags": [],
            "revenue": None,
            "stage": None,
            "model": None,
        }

        lower = text.lower()
        if "saas" in lower:
            profile["tags"].append("saas")
            profile["model"] = "SaaS"
        if "marketplace" in lower:
            profile["tags"].append("marketplace")
        if "b2b" in lower:
            profile["tags"].append("b2b")
        if "b2c" in lower:
            profile["tags"].append("b2c")

        # naive revenue finder — look for currency amounts followed by k/m/million/thousand
        m = re.search(r"\$\s*([0-9,.]+)\s*(k|m|million|thousand|K|M)\b", text, re.I)
        if m:
            num = m.group(1).replace(',', '')
            mult = m.group(2) or ""
            try:
                val = float(num)
                if mult.lower().startswith('m'):
                    val *= 1_000_000
                elif mult.lower().startswith('k'):
                    val *= 1_000
                profile["revenue"] = int(val)
            except Exception:
                pass

        # stage heuristics
        if any(w in lower for w in ["seed", "pre-seed", "preseed"]):
            profile["stage"] = "pre-seed/seed"
        elif any(w in lower for w in ["series a", "series-a", "a round"]):
            profile["stage"] = "growth (Series A+)"
        elif profile["revenue"] and profile["revenue"] > 1_000_000:
            profile["stage"] = "revenue-generating"
        else:
            profile["stage"] = profile["stage"] or "early"

        return profile

    def suggest_strategies(self, company: Dict, market_notes: str = "") -> List[Dict]:
        """Generate a list of candidate strategies with rationale and effort/impact estimates.

        If the agent is in LLM mode and an `llm_client` is provided, delegate
        strategy generation to the LLM client. The LLM client should return a
        list of strategy dicts compatible with the rule-based output.
        """
        # If configured, use LLM to generate strategies
        if self.mode == "llm" and self.llm_client is not None:
            try:
                llm_out = self.llm_client.generate_strategies(company.get("raw", ""), market_notes)
                # Expecting a list of dicts; do a basic validation
                if isinstance(llm_out, list) and llm_out:
                    return llm_out
            except Exception:
                # Fall back to rule-based generation on any LLM error
                pass

        # fallback to rule-based
        tags = set(company.get("tags", []))
        strategies = []

        # Common strategies
        strategies.append({
            "title": "Improve onboarding conversion",
            "rationale": "Small onboarding improvements often increase activation and retention.",
            "effort": "medium",
            "impact": "high",
            "actions": [
                "Map current onboarding funnel and identify drop-off steps",
                "Run 3 A/B tests (copy, timing, and 1 UX change)",
                "Track activation metric for 30 days",
            ],
        })

        # Tag-driven suggestions
        if "saas" in tags or company.get("model") == "SaaS":
            strategies.append({
                "title": "Introduce usage-based pricing experiment",
                "rationale": "Align pricing with value and capture higher willingness-to-pay.",
                "effort": "medium",
                "impact": "medium",
                "actions": [
                    "Identify high-value usage metrics",
                    "Design a pilot pricing plan for select customers",
                    "Measure churn and ARR delta after 90 days",
                ],
            })

        if "b2b" in tags:
            strategies.append({
                "title": "Systematic outbound for ideal customer profile (ICP)",
                "rationale": "B2B channels scale if ICP and messaging are tuned.",
                "effort": "high",
                "impact": "high",
                "actions": [
                    "Define ICP by revenue, industry, and tech stack",
                    "Create 3 messaging sequences tailored to ICP",
                    "Pilot outreach to 50 accounts and measure meetings/bookings",
                ],
            })

        if "marketplace" in tags:
            strategies.append({
                "title": "Two-sided liquidity push",
                "rationale": "Marketplaces need simultaneous supply and demand growth.",
                "effort": "high",
                "impact": "high",
                "actions": [
                    "Run supply-side incentives for first 100 providers",
                    "Target demand via partnerships and paid channels",
                ],
            })

        # Market-driven heuristic: look for "enterprise" or big-market signals
        if "enterprise" in market_notes.lower() or (company.get("revenue") and company["revenue"] > 5_000_000):
            strategies.append({
                "title": "Enterprise GTM: strategic accounts and case studies",
                "rationale": "Large accounts increase ARR and drive references.",
                "effort": "very-high",
                "impact": "very-high",
                "actions": [
                    "Select 3 anchor customers to pilot enterprise features",
                    "Create case study and ROI calculator",
                ],
            })

        return strategies

    def prioritize_actions(self, strategies: List[Dict]) -> List[Dict]:
        """Prioritize by a simple impact/effort score (higher is better)."""
        score_map = {"very-low": 0, "low": 1, "medium": 2, "high": 3, "very-high": 4}

        def s(effort: str, impact: str) -> int:
            return score_map.get(impact, 2) * 10 - score_map.get(effort, 2) * 5

        prioritized = []
        for st in strategies:
            prioritized.append({
                "title": st["title"],
                "rationale": st.get("rationale", ""),
                "effort": st.get("effort", "medium"),
                "impact": st.get("impact", "medium"),
                "score": s(st.get("effort", "medium"), st.get("impact", "medium")),
                "actions": st.get("actions", []),
            })

        prioritized.sort(key=lambda x: x["score"], reverse=True)
        return prioritized

    def run_profile(self, profile_text: str, market_notes: str = "") -> Dict:
        company = self.analyze_company(profile_text)
        strategies = self.suggest_strategies(company, market_notes)
        prioritized = self.prioritize_actions(strategies)
        return {
            "company": company,
            "strategies": strategies,
            "prioritized": prioritized,
        }


if __name__ == "__main__":
    import sys
    text = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not text:
        print("Run this module as a library. Use agent/main.py for CLI.")
    else:
        a = BusinessGrowthAgent()
        print(json.dumps(a.run_profile(text), indent=2))
