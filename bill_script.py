import pandas as pd
import fitz  # PyMuPDF
import re

def extract_kwh_and_cost_from_pdf(path):
    with fitz.open(path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()

    # Extract billing period
    billing_period_match = re.search(r"Billing period: (.*?)\n", text)
    billing_period = billing_period_match.group(1).strip() if billing_period_match else "Unknown"

    # Extract kWh and ¢/kWh from the "Supply" line
    supply_match = re.search(r"Supply\s+([\d,.]+)\s+kWh\s+@([\d.]+)¢/kWh", text)
    if supply_match:
        kwh = float(supply_match.group(1).replace(",", ""))
        cents_per_kwh = float(supply_match.group(2))
        cost_per_kwh = round(cents_per_kwh / 100, 5)  # convert to dollars
    else:
        kwh = None
        cost_per_kwh = None

    # Extract balance
    balance_match = re.search(r"Total amount due\s*\$([\d,.]+)", text)
    balance = float(balance_match.group(1).replace(",", "")) if balance_match else None

    return {
        "billing period": billing_period,
        "kWh": kwh,
        "balance": balance,
        "cost per kWh": cost_per_kwh
    }

# List of PDFs
pdf_paths = [
    "feb.pdf",
    "march.pdf",
    "april.pdf",
    "may.pdf",
    "june.pdf",
    "july.pdf"
]

# Extract and format
extracted_data = [extract_kwh_and_cost_from_pdf(path) for path in pdf_paths]
df = pd.DataFrame(extracted_data)

# Display calculated effective cost per kWh (balance ÷ kWh) for comparison
df["effective cost per kWh"] = (df["balance"] / df["kWh"]).round(5)

# Show results
print(df.to_string(index=False))
