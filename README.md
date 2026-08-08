# Multi-Step Research Agent

Give it a question. It decides how many times it needs to search the web,
gathers real, current information from multiple sources, and writes a
structured, cited report — saved as a Markdown file.

## What makes this genuinely "agentic," not just a search wrapper

Most simple demos do ONE search, then answer. This agent runs a real
**think \u2192 act \u2192 observe loop**:

1. **Think**: Claude reasons about what it still needs to know
2. **Act**: it calls the web_search tool if it needs more information
3. **Observe**: it looks at the results and decides \u2014 search again, or write
   the final answer?

This loop repeats (up to a safety cap of 6 steps) until Claude itself decides
it has enough real information to answer well \u2014 the *number of searches isn't
fixed in the code*, it's a decision the agent makes each time, based on the
actual question and what it's found so far.

## 1. Set up

```bash
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

## 2. Set your Anthropic API key

**Windows (Command Prompt):**
```
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```
*(Only lasts for the current terminal session \u2014 you'll need to set it again in
a new Command Prompt window, unless you set it permanently via Windows System
Environment Variables.)*

**Mac/Linux:**
```
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

## 3. Run it

```bash
python research_agent.py "What are the current best practices for RAG systems?"
```

Or just run it with no arguments and it'll ask you for a question interactively:
```bash
python research_agent.py
```

## What you'll see

The terminal shows each search the agent decides to run, in real time, so you
can actually watch its reasoning process rather than just getting a final
answer with no visibility into how it got there. Once done, it prints the
full report and saves it as a `.md` file named after your question.

## Cost note

Each run typically costs a small fraction of a cent to a few cents, depending
on how many searches the agent decides it needs \u2014 genuinely cheap for testing,
but worth knowing this uses real, metered API calls, unlike your earlier
free/local projects.

## What to actually say about this project

> "Built a multi-step research agent that autonomously decides how many web
> searches it needs \u2014 rather than a fixed single search \u2014 gathering from
> multiple sources and producing a structured, cited report. Implemented using
> Claude's server-side web search tool and a genuine agentic think-act-observe
> loop, with an explicit instruction to flag disagreement between sources
> rather than silently picking one."

**Be ready to explain:**
- Why a fixed single-search approach is often insufficient for real research
  questions, and how this agent's step count varies based on the actual
  question's complexity
- The safety cap (`MAX_AGENT_STEPS`) as a deliberate design choice \u2014 real
  agentic systems need bounds to prevent runaway loops, not unlimited autonomy
- The explicit "flag disagreement, don't guess" instruction in the system
  prompt as a direct application of the honesty/grounding principles from your
  earlier tutor agent project
