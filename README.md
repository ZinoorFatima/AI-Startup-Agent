# AI Startup Due-Diligence Agent

An AI analyst for VCs, angels, and accelerators. Enter a startup, a check size, and a
stage, and a **multi-agent pipeline** researches the company on the live web, analyzes
its financials, maps competitors, monitors news, models risk, and produces a scored
investment report with a recommendation.

```
                Streamlit form (app.py)
                        │
                LangGraph StateGraph  ← coordinator
                        │
   ┌──────────┬─────────┴────────┬──────────┐
   ▼          ▼                  ▼          ▼
Research   Financial        Competitor    News        (run in parallel)
   └──────────┴────────┬─────────┴──────────┘
                       ▼
              Risk Assessment agent
                       ▼
             Investment Report agent
                       ▼
            Rendered report + download
```

## Features

- **Six specialised agents** — Research, Financial, Competitor, News, Risk and Report.
- **Parallel research** — the four research agents run concurrently in the LangGraph.
- **Live web research** — free DuckDuckGo search + `trafilatura` extraction, Tavily optional.
- **Structured outputs** — every agent returns a validated Pydantic model.
- **Scored investment report** — risk model, recommendation, Markdown/JSON download.
- **Honest about gaps** — missing private financials are flagged, never invented.
- **Live progress UI** — watch each agent finish in Streamlit.

## Stack

- **LangGraph** — orchestration (the coordinator is the graph)
- **Gemini** via `langchain-google-genai` — `gemini-2.5-flash` for research agents, `gemini-2.5-pro` for risk + report
- **DuckDuckGo** (free, keyless) web search + `trafilatura` page extraction; **Tavily** optional
- **Streamlit** — UI
- **Pydantic** — every agent returns a validated structured object

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # then put your Gemini key in .env
python check_key.py         # verify the key works before anything else
```

> The Gemini key must be a Google **AI Studio** key (starts with `AIza…`) from
> https://aistudio.google.com/apikey. If `check_key.py` fails with an auth error,
> your key is the wrong type.

## Configuration (`.env`)

| Var | Purpose | Required |
|---|---|---|
| `GEMINI_API_KEY` | Google AI Studio key | Yes |
| `TAVILY_API_KEY` | Use Tavily instead of DuckDuckGo search | No |
| `GEMINI_FAST_MODEL` | Override research model (default `gemini-2.5-flash`) | No |
| `GEMINI_PRO_MODEL` | Override risk/report model (default `gemini-2.5-pro`) | No |

## Run

```bash
streamlit run app.py
```

Fill in the startup name, amount, stage, industry, and (optionally) website + any
financials you have. Click **Run due diligence**, watch each agent complete live, then
read and download the report (Markdown or JSON).

## Test

```bash
pytest tests/
```

## Project layout

| Path | Purpose |
|------|---------|
| `app.py` | Streamlit UI: form, live progress, report, downloads |
| `config.py` | env loading, model names, search-backend toggle |
| `src/graph.py` | LangGraph wiring (coordinator) |
| `src/state.py` | shared state + Pydantic output models |
| `src/llm.py` | Gemini factory |
| `src/tools/` | web search + page fetch |
| `src/agents/` | the 6 agents |

## Notes

- **Private financials** (ARR, burn, CAC…) aren't on the public web — enter what you
  know on the form. Missing inputs are flagged, not invented.
- **LinkedIn** isn't scraped directly; the research agent uses public search results
  mentioning the team.
- Each run is **stateless** (no database in v1).

---

## License

Released under the [MIT License](LICENSE).
