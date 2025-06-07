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
        match = re.search(r'(\d{4}-\d{2}-\d{2})', user_input)
        return match.group(1) if match else None

    def is_end_date_query(self, user_input: str) -> bool:
        return bool(re.search(r'(warranty.*end|end.*warranty|warranty.*expire|expire.*warranty)', user_input, re.IGNORECASE))


    def act(self, user_input: str, memory=None) -> str:
     print(f"DEBUG: user_input={user_input}, is_end_date_query={self.is_end_date_query(user_input)}")

     # 1. Handle explicit warranty end date queries
     if self.is_end_date_query(user_input):
        last_agent = memory.get('last_agent') if memory else None
        last_prompt = memory.get('last_prompt') if memory else None
        purchase_date_str = self.extract_purchase_date(user_input)
        bill_number = self.extract_bill_number(user_input)
        if memory:
            if not bill_number:
                bill_number = memory.get('bill_number')
            if not purchase_date_str:
                purchase_date_str = memory.get('purchase_date')
        if not purchase_date_str:
            return "Please provide the purchase date to calculate the warranty end date. Please provide it in YYYY-MM-DD format."
        # Retrieve warranty period from docs or use default
        docs = self.retriever(f"warranty information for bill number {bill_number}") if bill_number else []
        warranty_months = None
        if docs:
            for doc in docs:
                text = doc.page_content if hasattr(doc, "page_content") else str(doc)
                match = re.search(r'(\d+)\s*(month|months|year|years)', text, re.IGNORECASE)
                if match:
                    num = int(match.group(1))
                    warranty_months = num * 12 if "year" in match.group(2) else num
                    break
        if not warranty_months:
            warranty_months = self.default_warranty_months
        try:
            purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d")
            warranty_end = purchase_date + timedelta(days=30 * warranty_months)
            return f"Your warranty ends on {warranty_end.date()}."
        except Exception:
            return (
                "I couldn't understand the purchase date. "
                "Please provide the purchase date in YYYY-MM-DD format (for example: 2023-05-01)."
            )

     # 2. Handle follow-up: user provides only a date after being prompted
     if memory:
        last_agent = memory.get('last_agent')
        last_prompt = memory.get('last_prompt')
        purchase_date_str = self.extract_purchase_date(user_input)
        if (
            purchase_date_str
            and last_agent == 'warranty'
            and last_prompt == 'ask_purchase_date'
        ):
            bill_number = memory.get('bill_number')
            warranty_months = self.default_warranty_months
            try:
                purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d")
                warranty_end = purchase_date + timedelta(days=30 * warranty_months)
                return f"Your warranty ends on {warranty_end.date()}."
            except Exception:
                return (
                    "I couldn't understand the purchase date. "
                    "Please provide the purchase date in YYYY-MM-DD format (for example: 2023-05-01)."
                )

     # 3. General warranty queries
     if self.is_warranty_query(user_input):
        return (
            "I can help you with your warranty. "
            "If you want to check your warranty end date, please provide your purchase date in YYYY-MM-DD format."
        )

     # 4. Fallback for non-warranty queries
     return "How can I assist you with your appliance?"