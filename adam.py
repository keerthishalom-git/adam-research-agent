"""
research_agent.py — Multi-Step Research Agent

This agent takes a research question, decides how much searching it actually needs
(not just one search), gathers information from multiple real web sources using
Claude's built-in web search tool, and synthesizes a structured, cited report.

This is genuinely "agentic" in the think -> act -> observe sense: the agent reasons
about what it's found so far and decides whether to search again or whether it has
enough to write a good answer, rather than doing one fixed search and stopping.
"""

import os
import sys
import anthropic

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.status import Status
from rich.rule import Rule

MODEL = "claude-sonnet-4-6"
MAX_AGENT_STEPS = 6  # safety cap so the agent can't loop forever

console = Console()


def run_research_agent(client, question):
    """Runs the agent loop: Claude decides when to search vs. when to write the
    final answer, using the server-side web_search tool."""

    system_prompt = (
        "You are a careful research assistant. When given a question, use the "
        "web_search tool as many times as needed to gather enough real, current "
        "information from multiple distinct sources before answering \u2014 do not "
        "rely on a single source if the topic would benefit from cross-checking. "
        "Once you have enough information, write a clear, well-organized answer "
        "in Markdown with a '## Sources' section at the end listing the URLs you "
        "actually used. If sources disagree, say so explicitly rather than picking "
        "one silently. If you cannot find reliable information on part of the "
        "question, say so honestly instead of guessing."
    )

    messages = [{"role": "user", "content": question}]
    tools = [{"type": "web_search_20250305", "name": "web_search"}]

    console.print()
    console.print(Panel(f"[bold cyan]{question}[/bold cyan]", title="\U0001F9E0 Adam is researching", border_style="cyan"))
    console.print()

    for step in range(MAX_AGENT_STEPS):
        with Status(f"[dim]Adam is thinking (step {step + 1}/{MAX_AGENT_STEPS})...[/dim]", spinner="dots"):
            response = client.messages.create(
                model=MODEL,
                max_tokens=2000,
                system=system_prompt,
                messages=messages,
                tools=tools,
            )

        # Show the agent's reasoning/searching as it happens
        for block in response.content:
            if block.type == "server_tool_use" and block.name == "web_search":
                query = block.input.get("query", "")
                console.print(f"  [yellow]\U0001F50D  Step {step + 1}:[/yellow] searching [italic]\"{query}\"[/italic]")

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Agent decided it's done searching and has written its final answer
            final_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            console.print()
            console.print(Rule(f"[bold green]Adam is done \u2014 {step + 1} step(s)[/bold green]", style="green"))
            console.print()
            return final_text

        # If stop_reason is "tool_use", the loop continues automatically —
        # Anthropic's API executes server-side web_search itself, so we just
        # need to keep calling with the updated message history.

    console.print()
    console.print(Rule("[bold red]Hit the step limit \u2014 returning best available answer[/bold red]", style="red"))
    console.print()
    final_text = "".join(
        block.text for block in messages[-1]["content"] if hasattr(block, "text")
    )
    return final_text or "(Agent hit step limit before producing a final answer.)"


def save_report(question, report_text):
    safe_name = "".join(c if c.isalnum() or c == " " else "" for c in question)[:50].strip()
    safe_name = safe_name.replace(" ", "_") or "research_report"
    filename = f"{safe_name}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Research: {question}\n\n{report_text}\n")
    console.print(f"[dim]\U0001F4BE Saved report to[/dim] [bold]{filename}[/bold]")


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[bold red]ERROR:[/bold red] ANTHROPIC_API_KEY environment variable not set.")
        console.print("See README.md for how to set this.")
        return

    client = anthropic.Anthropic(api_key=api_key)

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = console.input("[bold]What would you like Adam to research? [/bold]").strip()

    if not question:
        console.print("[red]No question provided.[/red]")
        return

    report = run_research_agent(client, question)
    console.print(Panel(Markdown(report), title="\U0001F4C4 Adam's Research Report", border_style="blue"))
    save_report(question, report)


if __name__ == "__main__":
    main()
