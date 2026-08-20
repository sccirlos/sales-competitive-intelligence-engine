import warnings
warnings.filterwarnings("ignore")

import os
import json
import asyncio
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field

load_dotenv()

COMPETITORS = {
    "SimplePractice": "https://www.simplepractice.com/",
    "Jane": "https://jane.app/",
    "TherapyNotes": "https://www.therapynotes.com/",
    "Theranest": "https://ensorahealth.com/product/theranest-mental-health/",
    "PracticeFusion": "https://www.practicefusion.com/",
    "Tebra": "https://www.tebra.com/",
    "OfficeAlly": "https://www.officeally.com/",
    "Valant": "https://www.valant.io/",
    "Healthie": "https://www.gethealthie.com/",
    "Blueprint": "https://www.blueprint.ai/",
    "Mentalyc": "https://www.mentalyc.com/",
    "YungSidekick": "https://yung-sidekick.com/",
    "Upheal": "https://www.upheal.io/",
    "Freed": "https://www.getfreed.ai/",
    "Streamline": "https://www.streamlinehealthcare.com/",
    "SessionsHealth": "https://www.sessionshealth.com/",
    "Ritten": "https://ritten.io/",
    "Qualifacts": "https://www.qualifacts.com/",
    "Therapyappointment": "https://www.therapyappointment.com/"
}


class PricingTier(BaseModel):
    tier_name: str
    price: str
    billing_cycle: Optional[str] = None
    key_features: List[str] = Field(default_factory=list)


class Feature(BaseModel):
    feature_name: str
    category: Optional[str] = None
    description: Optional[str] = None
    is_gated: bool = False
    available_in_tiers: List[str] = Field(default_factory=list)


class CompetitorData(BaseModel):
    pricing_tiers: List[PricingTier]
    all_features: List[Feature]
    technical_constraints: List[str] = Field(default_factory=list)
    additional_costs: List[str] = Field(default_factory=list)

"""Step 0 of v1 - Define CompetitorIntel, add these two classes below"""
class IntelFinding(BaseModel):
    """A factual competitor finding with supporting evidence."""
    finding: str
    source_url: Optional[str] = None
    evidence_status: str = "verified"
    # Suggested values:
    # verified
    # inferred
    # not_publicly_documented


class CompetitorIntel(BaseModel):
    """
    Reusable source-of-truth competitor research.

    This object should contain factual competitive intelligence only.
    Sales messaging, objection handling, and SimplePractice positioning
    should be generated downstream from this data.
    """

    # Identity
    competitor_name: str
    competitor_url: str

    # Company / market
    company_overview: str
    market_positioning: Optional[str] = None
    target_customers: List[str] = Field(default_factory=list)

    # Products
    products_and_services: List[IntelFinding] = Field(default_factory=list)
    pricing: List[IntelFinding] = Field(default_factory=list)
    core_capabilities: List[IntelFinding] = Field(default_factory=list)

    # Key competitive areas
    group_practice_capabilities: List[IntelFinding] = Field(default_factory=list)
    billing_and_insurance: List[IntelFinding] = Field(default_factory=list)
    ai_capabilities: List[IntelFinding] = Field(default_factory=list)
    integrations: List[IntelFinding] = Field(default_factory=list)

    # Customer experience
    onboarding_and_migration: List[IntelFinding] = Field(default_factory=list)
    customer_support: List[IntelFinding] = Field(default_factory=list)

    # Competitive assessment
    strengths: List[IntelFinding] = Field(default_factory=list)
    limitations: List[IntelFinding] = Field(default_factory=list)

    # Freshness / provenance
    researched_at: str
    sources: List[str] = Field(default_factory=list)


class ComparisonFeature(BaseModel):
    feature_name: str
    simple_practice_offering: str
    competitor_offering: str
    comparison_notes: str


class ComparisonData(BaseModel):
    competitor_name: str
    overall_summary: str
    feature_comparison: List[ComparisonFeature]
    pricing_comparison: str
    winning_points_simple_practice: List[str]
    winning_points_competitor: List[str]


class DeepCompScraper:
    def __init__(
        self,
        target_competitor: Optional[str] = None,
        compare_targets: Optional[List[str]] = None,
        battlecard_targets: Optional[List[str]] = None,
    ):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment")

        self.app = FirecrawlApp(api_key=api_key)
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.output_dir = f"outputs/{self.date_str}"
        self.target_competitor = target_competitor
        self.compare_targets = compare_targets
        self.battlecard_targets = battlecard_targets

        os.makedirs(f"{self.output_dir}/raw", exist_ok=True)
        os.makedirs(f"{self.output_dir}/comparisons", exist_ok=True)
        os.makedirs(f"{self.output_dir}/battlecards", exist_ok=True)

    async def discover_and_extract(self, name: str, url: str) -> Dict[str, Any]:
        print(f"\n--- Deep Researching {name} using Agent ---")

        prompt = (
            f"Find the pricing tiers, main features, technical constraints (like rate limits), "
            f"and any additional costs of {name} from their website {url}."
        )

        try:
            result = self.app.agent(
                prompt=prompt,
                schema=CompetitorData,
            )

            if result.success:
                if result.data:
                    if hasattr(result.data, "model_dump"):
                        return result.data.model_dump()
                    return result.data
                return {}
            else:
                print(f"Agent failed for {name}: {result.error}")
                return {}

        except Exception as e:
            print(f"Error during agent execution for {name}: {e}")
            return {}

    """Week 1 separate competitor research from battlecard generation, step 2 """
    async def research_competitor_intel(
        self,
        name: str,
        url: str,
    ) -> Dict[str, Any]:
        """
        Research a competitor and return reusable, structured competitive
        intelligence that can be consumed by battlecards, agents, or other tools.
        """

        print(f"\n--- Researching Competitor Intel: {name} ---")

        prompt = f"""
Research {name} ({url}) and create a comprehensive, factual competitive
intelligence profile.

This research will serve as a reusable source of truth for downstream
applications such as sales enablement, competitive battlecards, and
future AI agents.

Focus on factual competitor information. Do NOT generate sales messaging,
objection handling, or SimplePractice positioning.

Research the following:

1. COMPANY & MARKET
- Company overview
- Market positioning
- Primary target customers
- Practice sizes and specialties served

2. PRODUCTS & SERVICES
- Core products
- Add-on products
- Services
- Major product packages

3. PRICING
- Published pricing
- Pricing tiers
- Per-provider or per-location pricing
- Add-on costs
- Enterprise/custom pricing where documented

4. CORE PRODUCT CAPABILITIES
- Practice management
- Scheduling
- Documentation
- Client portal
- Telehealth
- Billing
- Payments
- Reporting
- Communications
- Other major capabilities

5. GROUP PRACTICE CAPABILITIES
- Multi-clinician support
- Roles and permissions
- Administrative workflows
- Multi-location support
- Group reporting
- Enterprise/group functionality

6. BILLING & INSURANCE
- Insurance claims
- Eligibility
- Clearinghouse capabilities
- ERA/EOB workflows
- Payments
- Revenue cycle management
- Billing services

7. AI CAPABILITIES
- AI documentation
- AI assistants
- Automation
- Agentic capabilities
- Other publicly documented AI features

8. INTEGRATIONS
- EHR integrations
- Third-party integrations
- APIs
- Clearinghouses
- Partner ecosystem

9. ONBOARDING & MIGRATION
- Implementation
- Data migration
- Import services
- Training
- Setup assistance

10. CUSTOMER SUPPORT
- Support channels
- Support hours
- Dedicated support
- Implementation/account management

11. STRENGTHS
Identify factual, evidence-backed areas where the competitor appears strong.

12. LIMITATIONS
Identify publicly documented limitations, constraints, missing capabilities,
or areas where information is unavailable.

EVIDENCE REQUIREMENTS:
- Prefer first-party competitor sources.
- Provide a source URL for findings whenever possible.
- Mark directly supported findings as "verified".
- Mark reasonable conclusions that are not directly stated as "inferred".
- If something cannot be established from public information, use
  "not_publicly_documented".
- Do not invent capabilities, pricing, or product claims.
"""

        try:
            result = self.app.agent(
                prompt=prompt,
                schema=CompetitorIntel,
            )

            if result.success:
                if result.data:
                    if hasattr(result.data, "model_dump"):
                        return result.data.model_dump()
                    return result.data

                return {}

            print(f"Competitor intel research failed for {name}: {result.error}")
            return {}

        except Exception as e:
            print(f"Error researching competitor intel for {name}: {e}")
            return {}

    # add storage helpers
    def save_competitor_intel(
        self,
        competitor_name: str,
        intel: Dict[str, Any],
    ) -> None:
        """
        Save competitor intelligence to both:
        - latest/<competitor>.json
        - history/<date>/<competitor>.json
        """

        base_dir = "intel"
        latest_dir = os.path.join(base_dir, "latest")
        history_dir = os.path.join(base_dir, "history", self.date_str)

        os.makedirs(latest_dir, exist_ok=True)
        os.makedirs(history_dir, exist_ok=True)

        filename = f"{competitor_name.lower()}_intel.json"

        latest_path = os.path.join(latest_dir, filename)
        history_path = os.path.join(history_dir, filename)

        with open(latest_path, "w") as f:
            json.dump(intel, f, indent=2)

        with open(history_path, "w") as f:
            json.dump(intel, f, indent=2)

        print(f"Latest intel saved to {latest_path}")
        print(f"Historical intel saved to {history_path}")



    async def run_detailed_comparison(self, competitor_name: str, competitor_url: str):
        print(f"\n--- Running Detailed Comparison: SimplePractice vs {competitor_name} ---")

        sp_url = COMPETITORS["SimplePractice"]

        prompt = (
            f"Compare SimplePractice ({sp_url}) and {competitor_name} ({competitor_url}) side-by-side. "
            "Focus on core clinical workflows (notes, scheduling, billing), AI capabilities, "
            "and pricing value. For each feature, explain what SimplePractice offers vs what "
            f"{competitor_name} offers. Identify where SimplePractice is stronger and where "
            f"{competitor_name} might have an edge."
        )

        try:
            result = self.app.agent(
                prompt=prompt,
                schema=ComparisonData,
            )

            if result.success:
                data = result.data
                output_data = data.model_dump() if hasattr(data, "model_dump") else data

                comp_file = f"{self.output_dir}/comparisons/sp_vs_{competitor_name.lower()}.json"
                with open(comp_file, "w") as f:
                    json.dump(output_data, f, indent=2)

                print(f"Detailed comparison saved to {comp_file}")
                return output_data
            else:
                print(f"Comparison agent failed for {competitor_name}: {result.error}")
                return None

        except Exception as e:
            print(f"Error during comparison agent execution for {competitor_name}: {e}")
            return None
        
    def load_competitor_intel(
        self,
        competitor_name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Load the most recently stored competitor intelligence for a competitor.
        """
        intel_file = (
            f"intel/latest/"
            f"{competitor_name.lower()}_intel.json"
        )

        if not os.path.exists(intel_file):
            print(
                f"No stored competitor intel found for {competitor_name}: "
                f"{intel_file}"
            )
            return None

        try:
            with open(intel_file, "r") as f:
                intel = json.load(f)

            print(f"Loaded latest competitor intel from {intel_file}")
            return intel

        except (OSError, json.JSONDecodeError) as e:
            print(
            f"Could not load stored competitor intel for "
            f"{competitor_name}: {e}"
        )
        return None
        
    async def run_sales_battlecard(
        self,
        competitor_name: str,
        competitor_intel: Dict[str, Any],
    ):
        print(
            f"\n--- Generating Sales Battlecard: SimplePractice vs {competitor_name} ---"
        )

        # Simplify the full competitor intel for the battlecard prompt.
        def simplify_findings(items, limit=5, max_chars=300):
            simplified = []

            for item in items[:limit]:
                if isinstance(item, dict):
                    finding_text = item.get("finding", "")
                else:
                    finding_text = str(item)

                if len(finding_text) > max_chars:
                    finding_text = finding_text[:max_chars].rstrip() + "..."

                simplified.append(finding_text)

            return simplified

        def truncate_text(value, max_chars=500):
            if not value:
                return ""

            value_text = str(value)

            if len(value_text) > max_chars:
                return value_text[:max_chars].rstrip() + "..."

            return value_text

        # Create a smaller, Sales-relevant context so the Agent prompt stays
        # under Firecrawl's character limit. The full CompetitorIntel JSON
        # remains the source-of-truth artifact saved separately.
        battlecard_context = {
            "competitor_name": competitor_name,
            "company_overview": truncate_text(
                competitor_intel.get("company_overview"),
                max_chars=500,
            ),
            "market_positioning": truncate_text(
                competitor_intel.get("market_positioning"),
                max_chars=500,
            ),
            "target_customers": [
                truncate_text(item, max_chars=200)
                for item in competitor_intel.get("target_customers", [])[:5]
            ],
            "products_and_services": simplify_findings(
                competitor_intel.get("products_and_services", []),
                limit=5,
            ),
            "pricing": simplify_findings(
                competitor_intel.get("pricing", []),
                limit=5,
            ),
            "group_practice_capabilities": simplify_findings(
                competitor_intel.get("group_practice_capabilities", []),
                limit=5,
            ),
            "billing_and_insurance": simplify_findings(
                competitor_intel.get("billing_and_insurance", []),
                limit=5,
            ),
            "onboarding_and_migration": simplify_findings(
                competitor_intel.get("onboarding_and_migration", []),
                limit=5,
            ),
            "customer_support": simplify_findings(
                competitor_intel.get("customer_support", []),
                limit=5,
            ),
            "strengths": simplify_findings(
                competitor_intel.get("strengths", []),
                limit=4,
            ),
            "limitations": simplify_findings(
                competitor_intel.get("limitations", []),
                limit=4,
            ),
        }

        prompt = f"""
You are a Competitive Intelligence Analyst supporting the SimplePractice Sales team.

Create a concise Sales Battlecard for SimplePractice vs {competitor_name}.

IMPORTANT:
- Use only the competitor intelligence provided below for claims about {competitor_name}.
- Do not independently research the competitor.
- Do not invent facts.
- If information is unavailable, say "Not publicly documented."

COMPETITOR INTELLIGENCE:
{json.dumps(battlecard_context, separators=(",", ":"))}

OUTPUT:

1. Company Overview
- Market focus
- Target customers
- Key positioning

2. Products & Pricing
- Main offerings
- Pricing/licensing
- Group-practice relevance

3. Competitor Strengths
- Top 3 evidence-backed strengths

4. Weaknesses & SimplePractice Opportunities
- Top 3 documented gaps or limitations
- Explain the potential SimplePractice opportunity without inventing SimplePractice capabilities

5. Service & Onboarding
- Migration
- Implementation
- Training
- Support

6. Sales Landmines
- 2-3 competitor strengths a prospect may raise
- Short suggested response for each

7. Key Takeaways
- 3-5 things Sales should remember

Tone: objective, concise, sales-ready, and scannable.
"""

        print(f"Battlecard prompt length: {len(prompt)} characters")

        # Leave some headroom below Firecrawl's 10,000-character limit.
        if len(prompt) > 9500:
            print(
                f"Battlecard prompt is too large ({len(prompt)} characters). "
                "Skipping Agent call."
            )
            return None

        try:
            result = self.app.agent(prompt=prompt)

            if result.success:
                output = result.data if hasattr(result, "data") else result

                file_path = (
                    f"{self.output_dir}/battlecards/"
                    f"battlecard_{competitor_name.lower()}.txt"
                )
                with open(file_path, "w") as f:
                    f.write(str(output))

                print(f"Battlecard saved to {file_path}")
                return output

            print(
                f"Battlecard generation failed for {competitor_name}: "
                f"{result.error}"
            )
            return None

        except Exception as e:
            print(f"Error generating battlecard for {competitor_name}: {e}")
            return None

    async def run(self):
       # Battlecard mode: run for a list of competitors and generate battlecards.
        if self.battlecard_targets:
            for name in self.battlecard_targets:
                if name not in COMPETITORS:
                     print(
                         f"Warning: Competitor '{name}' not found in configuration."
                     )
                     continue
                # Load existing strucured competitor intelligence
                intel = self.load_competitor_intel(
                        name,)

                if not intel:
                    print(
                        f"Could not generate battlecard for {name}: "
                        "competitor research returned no data."
                    )
                    print(
                        f"Run competitor intel reseearch for {name} first."
                    )

                    continue

                # Generate the sales artificat from stored intel.
                await self.run_sales_battlecard(
                    name,
                    intel,
                )
            return
        
        
        """Compare mode: run for up to two competitors and generate a side-by-side comparison report."""
        if self.compare_targets:
            all_comparisons = []

            for name in self.compare_targets[:2]:
                if name in COMPETITORS:
                    comp_data = await self.run_detailed_comparison(
                        name,
                        COMPETITORS[name]
                    )
                    if comp_data:
                        all_comparisons.append(comp_data)
                else:
                    print(
                        f"Warning: Competitor '{name}' not found in configuration."
                    )

            if all_comparisons:
                self.generate_comparison_reports(all_comparisons)
            return

        """General competitor research mode: run for all competitors or a specific one, and save raw JSON outputs."""
        targets = COMPETITORS
        if self.target_competitor:
            if self.target_competitor in COMPETITORS:
                targets = {self.target_competitor: COMPETITORS[self.target_competitor]}
            else:
                print(f"Error: Competitor '{self.target_competitor}' not found in configuration.")
                print(f"Available competitors: {', '.join(COMPETITORS.keys())}")
                return

        all_data = {}
        for name, url in targets.items():
            data = await self.discover_and_extract(name, url)
            all_data[name] = data

            with open(f"{self.output_dir}/raw/{name.lower()}.json", "w") as f:
                json.dump(data, f, indent=2)

        self.summarize_findings(all_data)

    def generate_comparison_reports(self, comparisons: List[Dict[str, Any]]):
        report_path = f"{self.output_dir}/comparison_summary.txt"
        with open(report_path, "w") as f:
            f.write(f"SimplePractice Competitor Comparison Summary - {self.date_str}\n")
            f.write("=" * 80 + "\n\n")

            for comp in comparisons:
                name = comp.get("competitor_name", "Unknown")
                f.write(f"VS {name.upper()}\n")
                f.write("-" * 40 + "\n")
                f.write(f"Summary: {comp.get('overall_summary', '')}\n\n")

                f.write("Feature Comparison Table:\n")
                f.write(f"{'Feature':<25} | {'SimplePractice':<30} | {name:<30}\n")
                f.write("-" * 90 + "\n")
                for feat in comp.get("feature_comparison", []):
                    f_name = feat.get("feature_name", "N/A")[:23]
                    sp_off = feat.get("simple_practice_offering", "N/A")[:28]
                    c_off = feat.get("competitor_offering", "N/A")[:28]
                    f.write(f"{f_name:<25} | {sp_off:<30} | {c_off:<30}\n")

                f.write("\nSimplePractice Wins:\n")
                for win in comp.get("winning_points_simple_practice", []):
                    f.write(f"  [+] {win}\n")

                f.write(f"\n{name} Wins:\n")
                for win in comp.get("winning_points_competitor", []):
                    f.write(f"  [-] {win}\n")

                f.write("\n" + "=" * 80 + "\n\n")

        print(f"Comprehensive comparison report generated: {report_path}")

    def summarize_findings(self, all_data: Dict[str, Any]):
        summary_path = f"{self.output_dir}/summary_report.txt"
        with open(summary_path, "w") as f:
            f.write(f"Competitor Research Summary - {self.date_str}\n")
            f.write("=" * 40 + "\n")
            for name, data in all_data.items():
                f.write(f"\nCOMPETITOR: {name}\n")
                f.write(f"Pricing Tiers found: {len(data.get('pricing_tiers', []))}\n")
                f.write(f"Total Features found: {len(data.get('all_features', []))}\n")

                tech_constraints = data.get("technical_constraints", [])
                if tech_constraints:
                    f.write(f"Technical Constraints: {', '.join(tech_constraints)}\n")

                add_costs = data.get("additional_costs", [])
                if add_costs:
                    f.write(f"Additional Costs: {', '.join(add_costs)}\n")

                f.write(f"Raw data stored in raw/{name.lower()}.json\n")

                if data.get("pricing_tiers"):
                    f.write("\n  Pricing Tiers:\n")
                    for tier in data["pricing_tiers"]:
                        if isinstance(tier, dict):
                            name_tier = tier.get("tier_name", "N/A")
                            price = tier.get("price", "N/A")
                        else:
                            name_tier = getattr(tier, "tier_name", "N/A")
                            price = getattr(tier, "price", "N/A")
                        f.write(f"  - {name_tier}: {price}\n")

        print(f"\nResearch phase complete. Reports generated in {self.output_dir}")


def run_competitor_research(name: str, url: str):
    scraper = DeepCompScraper(target_competitor=name)
    asyncio.run(scraper.run())

    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = f"outputs/{date_str}/raw/{name.lower()}.json"

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)

        features = data.get("all_features", [])
        tiers = data.get("pricing_tiers", [])
        return features, tiers

    return [], []

"""week 1 Separate competitor research from battlecard generation, part of step 2: wire up a tiny test path so we can run the new research_competitor_intel() 
function by itself and inspect the JSON it returns, 
without touching your existing battlecard flow yet."""
def run_competitor_intel_research(name: str, url: str):
    scraper = DeepCompScraper()

    data = asyncio.run(
        scraper.research_competitor_intel(name, url)
    )

    if data:
        scraper.save_competitor_intel(
            name,
            data,
        )

    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deep Competitor Research Scraper")
    parser.add_argument(
        "--competitor",
        type=str,
        help="Run only for a specific competitor (e.g., Jane)",
    )
    parser.add_argument(
        "--compare",
        nargs="+",
        help="Compare SimplePractice with up to two competitors (e.g., --compare Blueprint Jane)",
    )
    parser.add_argument(
        "--battlecard",
        nargs="+",
        help="Generate sales battlecards (e.g., --battlecard Jane TherapyNotes)",
    )
    parser.add_argument(
        "--intel",
        type=str,
        help="Research and store structured competitor intelligence (e.g., --intel Jane)",
    ) 

    args = parser.parse_args()

    if args.intel:
        competitor_name = args.intel

        if competitor_name not in COMPETITORS:
            print(
                f"Error: Competitor '{competitor_name}' "
                "not found in configuration."
            )
            print(
            f"Available competitors: {', '.join(COMPETITORS.keys())}"
        )
        else:
            run_competitor_intel_research(
                competitor_name,
                COMPETITORS[competitor_name],
            )
        exit()

    scraper = DeepCompScraper(
        target_competitor=args.competitor,
        compare_targets=args.compare,
        battlecard_targets=args.battlecard,
    )
    
    asyncio.run(scraper.run())