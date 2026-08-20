# Deep Competitor Research Scraper

An AI-powered tool using [Firecrawl](https://www.firecrawl.dev/) to discover, extract, and compare competitor features and pricing in the mental health and clinical management space.

## Features

- **Automated Research**: Uses Firecrawl's AI agent to browse competitor websites and extract structured pricing and feature data.
- **Side-by-Side Comparison**: Specifically designed to compare competitors against SimplePractice, identifying wins and gaps.
- **Data Compilation**: Compiles raw research data into a clean CSV format for further analysis.

## Prerequisites

- Python 3.10+
- A Firecrawl API Key (Get one at [firecrawl.dev](https://www.firecrawl.dev/))

## Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd comp_scraper_demo
    ```

2.  **Install dependencies**:
    This project uses `uv` for dependency management. If you have `uv` installed:
    ```bash
    uv sync
    ```
    Otherwise, you can use `pip`:
    ```bash
    pip install firecrawl-py pydantic-settings python-dotenv pandas
    ```
    python3 -m pip install firecrawl-py pydantic-settings python-dotenv pandas

3.  **Configure environment variables**:
    Create a `.env` file in the root directory and add your Firecrawl API key:
    ```env
    FIRECRAWL_API_KEY=your_api_key_here
    ```

## Usage



To research a specific competitor (e.g., Jane):
```bash
uv run main.py --competitor Jane
```

### 2. Run Detailed Comparisons
To compare SimplePractice against up to two specific competitors:
```bash
uv run main.py --compare Blueprint Jane
```

### 3. Compile Results to CSV
Once you have raw JSON data in the `outputs/` directory, you can compile it into a CSV:
```bash
uv run compile_results.py
```

## Adding New Competitors

To add a new competitor to the research list, modify the `COMPETITORS` dictionary at the top of `main.py`:

```python
COMPETITORS = {
    ...
    "NewCompetitor": "https://www.newcompetitor.com/",
}
```

## Configuration

The list of competitors and their URLs is maintained in `main.py` under the `COMPETITORS` dictionary.

## Output Structure

Results are stored in the `outputs/` directory, organized by date:
- `outputs/YYYY-MM-DD/raw/`: Individual JSON files for each researched competitor.
- `outputs/YYYY-MM-DD/comparisons/`: Detailed side-by-side comparison JSON files.
- `outputs/YYYY-MM-DD/summary_report.txt`: A quick text summary of the research phase.
- `outputs/YYYY-MM-DD/comparison_summary.txt`: A formatted text report of all comparisons run.
- `outputs/YYYY-MM-DD/compiled_features.csv`: A flattened CSV of all features discovered.
