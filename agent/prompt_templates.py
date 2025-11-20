# Placeholder templates for future LLM-driven prompts

COMPANY_ANALYSIS = """
You are an expert growth consultant. Given the following company profile, extract stage, revenue estimate, target customers, primary value proposition, and suggested top 3 growth experiments.

Profile:
{profile}

Respond as JSON with keys: stage, revenue_estimate, target_customers, value_prop, experiments
"""

STRATEGY_GENERATION = """
You are a strategic advisor. Given company profile and market notes, propose a prioritized list of growth strategies with rationale and 3 concrete actions each.

Company:
{company}

Market notes:
{market}
"""
