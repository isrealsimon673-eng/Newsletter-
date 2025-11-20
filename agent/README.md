# Business Growth & Strategy Agent

This small Python scaffold provides a starting point for an agent that helps founders and business teams generate growth strategies, prioritize initiatives, and produce actionable tasks.

Goals

What's included

Usage

Run locally (Python 3.11+):

```bash
python agent/main.py --profile examples/sample_profile.txt
```

LLM integration (OpenAI)

1. Install requirements:

```bash
python -m pip install -r agent/requirements.txt
```

2. Set your `OPENAI_API_KEY` environment variable, or create an `.env` from `.env.example`.

3. Run the agent in LLM mode:

```bash
export OPENAI_API_KEY="sk-..."
python agent/main.py --profile agent/examples/sample_profile.txt --mode llm
```

Notes
- The LLM mode delegates strategy generation to the OpenAI model and attempts
	to parse JSON output. If parsing fails, the agent will return a fallback
	entry containing the raw LLM text. Use LLM mode only when you have an API key
	and accept external network calls.
- Add unit tests and CI
