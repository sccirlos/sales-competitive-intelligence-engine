# Sales Competitive Intelligence Engine 🔎

An AI-powered competitive research tool built to help Sales teams quickly understand competitors, keep competitive intel fresh, and eventually give Sales agents a reliable source of competitive context.

The goal is pretty simple: **research competitors once, structure the intel, and make that intel reusable across different Sales workflows.**

Instead of every battlecard, agent, or Sales workflow independently researching a competitor, the engine creates a structured competitive intelligence layer that other tools can consume.

---

## What It Does

The engine uses Firecrawl Agent to research a competitor and return structured competitive intelligence across areas like:

- Company and market positioning
- Target customers
- Products and services
- Pricing
- Core platform capabilities
- Group practice capabilities
- Billing and insurance
- AI capabilities
- Integrations
- Onboarding and migration
- Customer support
- Strengths and limitations
- Source URLs

Research is stored as structured `CompetitorIntel` JSON so it can be reused without having to research the competitor again every time.

---

## How It Works

```text
Competitor
    ↓
Firecrawl Agent
    ↓
Structured CompetitorIntel
    ↓
Stored Competitive Intelligence
    ↓
┌─────────────────┬─────────────────┐
↓                 ↓                 ↓
Battlecards    Sales Agent      Future Uses
```

### Research Layer

Firecrawl Agent performs the deeper competitor research and maps its findings into the `CompetitorIntel` schema.

The full structured output is saved as JSON and acts as the reusable competitive intelligence artifact.

### Consumption Layer

Downstream workflows consume the stored intel rather than starting their own research.

For example, battlecard generation:

```text
Stored CompetitorIntel
        ↓
Sales-Relevant Context Builder
        ↓
Battlecard Generation
        ↓
Sales Battlecard
```

This keeps the expensive/deeper research separate from the ways Sales might want to use it.

---

## Current Capabilities

### 🔎 Competitor Research

Run research for a configured competitor:

```bash
python3 mainreal.py --competitor Jane
```

This performs competitor research and generates the research output.

### ⚔️ Sales Battlecards

Generate a Sales battlecard using previously stored competitive intelligence:

```bash
python3 mainreal.py --battlecard Jane
```

The battlecard workflow:

1. Loads the stored competitor intel
2. Selects the most relevant Sales context
3. Keeps the context within the Agent's prompt limits
4. Generates a concise SimplePractice vs. competitor battlecard

It **does not need to research the competitor again** just to create the battlecard.

---

## Why I Built This

Competitive intel gets stale quickly, and the same competitor research can end up being recreated across different teams and workflows.

I wanted to explore a model where we:

1. Research a competitor deeply
2. Store the findings in a consistent structure
3. Keep that intelligence fresh
4. Let different tools and agents use the same source of truth

Battlecards are the first use case, but the longer-term goal is for this to become a reusable competitive intelligence layer for Sales.

---

## Architecture Today

```text
                 RESEARCH / PRODUCER

                     Competitor
                         ↓
                  Firecrawl Agent
                         ↓
               CompetitorIntel Schema
                         ↓
                  Stored Intel JSON
                         ↓
               Competitive Intel Layer
                         ↓
              ┌──────────┴──────────┐
              ↓                     ↓
        Sales Battlecard      Future Sales Agent
```

The important separation is between **producing competitive intelligence** and **consuming competitive intelligence**.

Research can happen independently of the workflows that use the research.

---

## What's Next 08/21/2026

The next phase is focused on making the intelligence layer persistent and reliably fresh:

- Store a `latest` version of each competitor's intel
- Maintain historical research snapshots
- Add freshness metadata
- Define when competitor research should be refreshed
- Schedule recurring research
- Explore a human-readable publishing layer, such as Notion
- Make the latest competitive intel available to future Sales agents or skills

The end goal is:

> **Research once → keep it fresh → use it everywhere.**

---

## Setup

### 1. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

### 2. Install dependencies

```bash
python3 -m pip install "firecrawl-py>=4.12.0" "pandas>=2.3.3" "python-dotenv>=1.2.1" "tabulate>=0.9.0"
```

### 3. Add your environment variables

Create a `.env` file in the project root:

```text
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

The `.env` file is ignored by Git and should never be committed.

---

## Example Workflow

Research a competitor:

```bash
python3 mainreal.py --competitor Jane
```

The engine creates structured competitor intelligence.

Then generate a battlecard from that stored intelligence:

```bash
python3 mainreal.py --battlecard Jane
```

This allows multiple downstream Sales workflows to eventually use the same competitive research without independently researching the competitor every time.

---

## Longer-Term Vision

The battlecard is only the first consumer of the competitive intelligence layer.

The longer-term architecture could support workflows like:

```text
Sales Rep
   ↓
"Help me prep for my Jane call"
   ↓
Sales Agent / Competitive Skill
   ↓
Retrieve Latest Jane Intel
   ↓
Competitive Intelligence Layer
   ↓
Contextual Sales Guidance
```

This creates a foundation where competitive research can be refreshed on a regular basis while Sales tools and agents always have access to the latest available intelligence.

**Research once → keep it fresh → use it everywhere.**
