import os
import json
from typing import List, Optional

try:
    import openai
except Exception:  # pragma: no cover - optional dependency
    openai = None

from .prompt_templates import STRATEGY_GENERATION


class OpenAIClient:
    """Simple OpenAI wrapper for strategy generation.

    This class expects an environment variable `OPENAI_API_KEY` to be set,
    or an explicit `api_key` passed to the constructor.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set and no api_key provided")
        if openai is None:
            raise RuntimeError("openai package is not installed. Add it to requirements.")
        openai.api_key = self.api_key
        self.model = model

    def _build_prompt(self, profile: str, market: str) -> str:
        return STRATEGY_GENERATION.format(company=profile, market=market)

    def generate_strategies(self, profile: str, market: str = "") -> List[dict]:
        prompt = self._build_prompt(profile, market)

        # We ask the model to output JSON; callers should handle parsing errors.
        messages = [
            {"role": "system", "content": "You are a concise strategic growth advisor."},
            {"role": "user", "content": prompt},
        ]
        # First attempt: use function-calling with a JSON schema to force structured output
        functions = [
            {
                "name": "return_strategies",
                "description": "Return a JSON object with a top-level 'strategies' array of strategy objects.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "strategies": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "rationale": {"type": "string"},
                                    "effort": {"type": "string"},
                                    "impact": {"type": "string"},
                                    "actions": {"type": "array", "items": {"type": "string"}},
                                },
                                "required": ["title", "rationale", "actions"],
                            },
                        }
                    },
                    "required": ["strategies"],
                },
            }
        ]

        try:
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                functions=functions,
                function_call={"name": "return_strategies"},
                max_tokens=1000,
            )

            choices = resp.get("choices") or []
            if choices:
                message = choices[0].get("message", {})
                # If the model returned a function call, its arguments should be JSON
                if message.get("function_call"):
                    args_text = message["function_call"].get("arguments", "")
                    try:
                        parsed = json.loads(args_text)
                        if isinstance(parsed, dict) and parsed.get("strategies"):
                            return parsed["strategies"]
                    except Exception:
                        # fall through to legacy parsing
                        pass

                # If no function call, try to parse content directly
                content = message.get("content") or choices[0].get("text", "")
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict) and parsed.get("strategies"):
                        return parsed["strategies"]
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    # try to find JSON substring
                    import re

                    m = re.search(r"(\[\s*\{.+\}\s*\])", content, re.S)
                    if m:
                        try:
                            return json.loads(m.group(1))
                        except Exception:
                            pass

        except Exception:
            # If function-calling failed (e.g., older client), fall back to legacy call below
            pass

        # Legacy fallback: free-form chat completion + best-effort parsing
        try:
            resp = openai.ChatCompletion.create(model=self.model, messages=messages, max_tokens=1000)
            text = ""
            choices = resp.get("choices") or []
            if choices:
                text = choices[0].get("message", {}).get("content") or choices[0].get("text", "")
            else:
                text = resp.get("text", "")
        except Exception as e:
            text = str(e)

        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and parsed.get("strategies"):
                return parsed["strategies"]
            if isinstance(parsed, list):
                return parsed
        except Exception:
            import re

            m = re.search(r"(\[\s*\{.+\}\s*\])", text, re.S)
            if m:
                try:
                    return json.loads(m.group(1))
                except Exception:
                    pass

        return [
            {
                "title": "LLM output (unparsed)",
                "rationale": text[:1000],
                "effort": "medium",
                "impact": "medium",
                "actions": ["Review the LLM response and extract concrete experiments."],
            }
        ]
