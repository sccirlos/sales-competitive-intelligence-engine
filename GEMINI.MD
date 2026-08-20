# Competitor Research Scraper

## Target Competitors

- [SimplePractice](https://www.simplepractice.com/)
- [TherapyNotes](https://www.therapynotes.com/)
- [Jane](https://jane.app/)
- [Blueprint](https://www.blueprint-health.com/)
- [Upheal](https://www.upheal.io/)
- [Mentalyc](https://www.mentalyc.com/)

## Objective
The goal is to extract a comprehensive set of features and detailed pricing structures for each competitor. This data will be synthesized later to map competitor offerings against SimplePractice's product and feature sets.

## Research Areas
- **Core Features**: Documentation, scheduling, billing, telehealth, client portal, etc.
- **Advanced Tools**: AI note-taking, automation, clinical assessments, supervision tools.
- **Pricing Models**: Subscription tiers, per-user costs, add-on fees, transaction rates.
- **Platform Specifics**: Integration capabilities, mobile app availability, support levels.

## Project Plan

1.  **Environment Setup**:
    - [x] Initialize `uv` project.
    - [x] Install dependencies (`firecrawl-py`, `pandas`, `python-dotenv`).
    - [x] Create `.env` for Firecrawl API Key.

2.  **Discovery & Extraction (Per Competitor)**:
    - [ ] Use Firecrawl `search` to find "Pricing" and "Features" pages.
    - [ ] Execute `crawl` on identified pages to extract all available product modules and specific features.
    - [ ] Structure extraction to capture:
        - Feature Name
        - Description
        - Tier Availability (e.g., "Standard" vs "Pro")
        - Price Point (if applicable)
        - **Gating Status**: Identify which specific features are locked behind higher-priced tiers.

4.  **CLI Improvements**:
    - [ ] Add support for running research on a single competitor via flags (e.g., `--competitor SimplePractice`).
    - [ ] Implement verbose logging for easier prompt tuning.
