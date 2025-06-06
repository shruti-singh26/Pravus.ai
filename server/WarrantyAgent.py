import re
from datetime import datetime, timedelta

class WarrantyAgent:
    def __init__(self, retriever, default_warranty_months=12):
        self.retriever = retriever  # Should be a function or object that can search docs
        self.default_warranty_months = default_warranty_months

    def is_warranty_query(self, user_input: str) -> bool:
        return bool(re.search(r'\bwarranty\b|\bbill\s*number\b', user_input, re.IGNORECASE))

    def extract_bill_number(self, user_input: str) -> str:
        match = re.search(r'bill\s*number\s*[:\-]?\s*(\w+)', user_input, re.IGNORECASE)
        return match.group(1) if match else None

    def extract_purchase_date(self, user_input: str) -> str:
        # Looks for a date in the format YYYY-MM-DD or similar
        match = re.search(r'(\d{4}-\d{2}-\d{2})', user_input)
        return match.group(1) if match else None

    def act(self, user_input: str) -> str:
        bill_number = self.extract_bill_number(user_input)
        purchase_date_str = self.extract_purchase_date(user_input)
        if not bill_number:
            return "Could you please provide your bill number to check the warranty status?"

        # Try to retrieve warranty info from vector DB
        docs = self.retriever(f"warranty information for bill number {bill_number}")
        warranty_months = None
        if docs:
            # Try to extract warranty period from docs (simple example)
            for doc in docs:
                text = doc.page_content if hasattr(doc, "page_content") else str(doc)
                match = re.search(r'(\d+)\s*(month|months|year|years)', text, re.IGNORECASE)
                if match:
                    num = int(match.group(1))
                    if "year" in match.group(2):
                        warranty_months = num * 12
                    else:
                        warranty_months = num
                    break

        if not warranty_months:
            warranty_months = self.default_warranty_months

        # Calculate warranty status if purchase date is available
        if purchase_date_str:
            try:
                purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d")
                warranty_end = purchase_date + timedelta(days=30 * warranty_months)
                today = datetime.now()
                if today <= warranty_end:
                    return f"Your product (Bill No: {bill_number}) is under warranty until {warranty_end.date()}."
                else:
                    return f"Your product (Bill No: {bill_number}) is no longer under warranty (expired on {warranty_end.date()})."
            except Exception:
                return f"Could not parse the purchase date. Please provide it in YYYY-MM-DD format."
        else:
            return f"Warranty period for your product (Bill No: {bill_number}) is {warranty_months} months from the purchase date. Please provide the purchase date in YYYY-MM-DD format to check if it's still under warranty."