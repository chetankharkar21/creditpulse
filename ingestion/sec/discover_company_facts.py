import os

import requests
from dotenv import load_dotenv


APPLE_CIK = "0000320193"

SEC_COMPANY_FACTS_URL = (
    "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
)


def main():
    load_dotenv()

    user_agent = os.getenv("SEC_USER_AGENT")

    if not user_agent:
        raise ValueError("SEC_USER_AGENT is missing from .env")

    headers = {
        "User-Agent": user_agent,
        "Accept-Encoding": "gzip, deflate",
    }

    url = SEC_COMPANY_FACTS_URL.format(cik=APPLE_CIK)

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    print("SEC request successful.")
    print(f"CIK:        {data.get('cik')}")
    print(f"Company:    {data.get('entityName')}")
    print(f"Top keys:   {list(data.keys())}")

    facts = data.get("facts", {})

    print(f"Taxonomies: {list(facts.keys())}")

    us_gaap = facts.get("us-gaap", {})

    print(f"US-GAAP concepts available: {len(us_gaap)}")

    # Show a few available concepts
    print("\nSample concepts:")

    for concept in list(us_gaap.keys())[:10]:
        print(f" - {concept}")

    # Find revenue-related concepts
    print("\nRevenue-related concepts:")

    for concept_name in us_gaap:
        if "revenue" in concept_name.lower():
            print(f" - {concept_name}")

        # Compare likely total-revenue concepts
    revenue_candidates = [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
    ]

    print("\n--- Revenue candidate inspection ---")

    for revenue_concept_name in revenue_candidates:
        revenue_concept = us_gaap.get(revenue_concept_name)

        if not revenue_concept:
            print(f"\n{revenue_concept_name}: not found")
            continue

        print(f"\nConcept:     {revenue_concept_name}")
        print(f"Label:       {revenue_concept.get('label')}")
        print(f"Description: {revenue_concept.get('description')}")
        print(
            f"Units:       "
            f"{list(revenue_concept.get('units', {}).keys())}"
        )

        observations = (
            revenue_concept
            .get("units", {})
            .get("USD", [])
        )

        print(f"Observations: {len(observations)}")
        print("Latest 3:")

        for observation in observations[-3:]:
            print(observation)

            
    # Inspect Assets in detail
    concept_name = "Assets"
    concept = us_gaap.get(concept_name)

    if not concept:
        print(f"\nConcept '{concept_name}' not found.")
        return

    print(f"\n--- Inspecting concept: {concept_name} ---")
    print(f"Label:       {concept.get('label')}")
    print(f"Description: {concept.get('description')}")
    print(f"Units:       {list(concept.get('units', {}).keys())}")

    usd_observations = concept.get("units", {}).get("USD", [])

    print(f"USD observations: {len(usd_observations)}")

    print("\nLatest 5 observations:")

    for observation in usd_observations[-5:]:
        print(observation)


if __name__ == "__main__":
    main()