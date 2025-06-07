import re
from datetime import datetime, timedelta

class WarrantyAgent:
    def __init__(self, retriever, default_warranty_months=12):
        self.retriever = retriever  # Should be a function or object that can search docs
        self.default_warranty_months = default_warranty_months
        # Common warranty-related terms and patterns
        self.warranty_terms = [
            r'\bwarranty\b',
            r'\bguarantee\b',
            r'\bcoverage\b',
            r'\bwarrant[iy]es?\b',
            r'\bextended warranty\b',
            r'\bwarranty period\b',
            r'\bwarranty status\b',
            r'\bwarranty claim\b',
            r'\bwarranty registration\b',
            r'\bwarranty card\b',
            r'\bunder warranty\b',
            r'\bstill covered\b',
            r'\bexpired?\b',
            r'\bbill\s*number\b',
            r'\bpurchase\s*(?:date|proof)\b',
            r'\breceipt\b'
        ]
        self.warranty_pattern = '|'.join(self.warranty_terms)

    def is_warranty_query(self, user_input: str) -> bool:
        """Enhanced detection of warranty-related queries"""
        return bool(re.search(self.warranty_pattern, user_input, re.IGNORECASE))

    def extract_bill_number(self, user_input: str) -> str:
        """Enhanced bill number extraction supporting various formats"""
        # Common bill number patterns
        patterns = [
            # Standard formats with various prefixes
            r'(?:bill|receipt|invoice|order|ref|reference|ticket|id|number|#|no\.?)\s*[:\-#]?\s*([A-Za-z0-9\-_]{4,})',
            # Standalone alphanumeric format
            r'(?<!\w)([A-Za-z0-9]{4,}(?:\-[A-Za-z0-9]+)*)(?!\w)',
            # Any word containing both letters and numbers, min 4 chars
            r'\b([A-Za-z0-9]*?[A-Za-z][A-Za-z0-9]*?[0-9][A-Za-z0-9]*)\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None

    def _convert_date_to_iso(self, date_str: str, date_format: str) -> str:
        """Helper function to convert various date formats to ISO format (YYYY-MM-DD)"""
        try:
            # Remove any leading/trailing whitespace
            date_str = date_str.strip()
            
            # Handle various separators
            if '/' in date_str:
                date_str = date_str.replace('/', '-')
            
            # Parse the date
            date_obj = datetime.strptime(date_str, date_format)
            
            # Validate year is reasonable
            current_year = datetime.now().year
            if date_obj.year > current_year:
                raise ValueError(f"Purchase date cannot be in the future (year: {date_obj.year})")
            if date_obj.year < 1990:
                raise ValueError(f"Purchase date seems too old (year: {date_obj.year})")
            
            # Convert to ISO format
            return date_obj.strftime('%Y-%m-%d')
        except ValueError as e:
            print(f"Date conversion error: {str(e)}")
            return None

    def extract_purchase_date(self, user_input: str) -> str:
        """Enhanced purchase date extraction supporting multiple formats"""
        print(f"Extracting purchase date from: {user_input}")
        
        # Common date formats with their strptime format strings
        date_formats = [
            # DD/MM/YYYY or MM/DD/YYYY
            (r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})', [
                '%d-%m-%Y',  # DD-MM-YYYY
                '%m-%d-%Y',  # MM-DD-YYYY
                '%Y-%m-%d'   # YYYY-MM-DD (also try this format)
            ]),
            # YYYY-MM-DD
            (r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', ['%Y-%m-%d']),
            # DD Month YYYY or Month DD YYYY
            (r'(\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4})', ['%d %B %Y']),
            (r'((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}\s*,?\s*\d{4})', ['%B %d %Y']),
        ]
        
        # First look for dates with context
        context_patterns = [
            r'(?:purchase|bought|received|delivery|invoice|receipt|order)\s*(?:date|on)?\s*[:\-]?\s*([^\n.]+)',
            r'(?:date\s+of\s+(?:purchase|order|receipt|invoice))\s*[:\-]?\s*([^\n.]+)',
            r'(?:purchased|bought|received)\s+on\s+([^\n.]+)'
        ]
        
        # Try context patterns first
        for pattern in context_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                date_text = match.group(1).strip()
                print(f"Found date with context: {date_text}")
                # Try all date formats with this text
                for _, formats in date_formats:
                    for date_format in formats:
                        iso_date = self._convert_date_to_iso(date_text, date_format)
                        if iso_date:
                            print(f"Successfully parsed contextual date to: {iso_date}")
                            return iso_date
        
        # If no contextual date found, try direct date patterns
        for pattern, formats in date_formats:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                date_text = match.group(1).strip()
                print(f"Found direct date match: {date_text}")
                for date_format in formats:
                    iso_date = self._convert_date_to_iso(date_text, date_format)
                    if iso_date:
                        print(f"Successfully parsed direct date to: {iso_date}")
                        return iso_date
        
        print("No valid date found")
        return None

    def get_warranty_info(self, bill_number: str) -> dict:
        """Retrieve warranty information from the vector database"""
        docs = self.retriever(f"warranty information for bill number {bill_number}")
        warranty_info = {
            'warranty_months': None,
            'extended_warranty': False,
            'special_conditions': [],
            'product_info': {}
        }
        
        if docs:
            for doc in docs:
                text = doc.page_content if hasattr(doc, "page_content") else str(doc)
                # Extract warranty period
                match = re.search(r'(\d+)\s*(month|months|year|years)', text, re.IGNORECASE)
                if match:
                    num = int(match.group(1))
                    if "year" in match.group(2).lower():
                        warranty_info['warranty_months'] = num * 12
                    else:
                        warranty_info['warranty_months'] = num
                
                # Check for extended warranty
                if re.search(r'extended warranty', text, re.IGNORECASE):
                    warranty_info['extended_warranty'] = True
                
                # Extract product information
                product_matches = {
                    'brand': re.search(r'brand[:\s]+([A-Za-z]+)', text, re.IGNORECASE),
                    'model': re.search(r'model[:\s]+([A-Za-z0-9\-]+)', text, re.IGNORECASE),
                    'type': re.search(r'type[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
                }
                for key, match in product_matches.items():
                    if match:
                        warranty_info['product_info'][key] = match.group(1)
                
                # Extract special conditions
                conditions = re.findall(r'(?:condition|note|important)[:\s]+([^.]+)', text, re.IGNORECASE)
                warranty_info['special_conditions'].extend(conditions)
        
        if not warranty_info['warranty_months']:
            warranty_info['warranty_months'] = self.default_warranty_months
        
        return warranty_info

    def calculate_warranty_status(self, purchase_date_str: str, warranty_months: int) -> dict:
        """Calculate detailed warranty status"""
        try:
            print(f"Calculating warranty status for purchase date: {purchase_date_str}, warranty months: {warranty_months}")
            
            # Parse purchase date
            purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d')
            print(f"Parsed purchase date: {purchase_date}")
            
            # Calculate warranty end date
            warranty_end = purchase_date + timedelta(days=30 * warranty_months)
            print(f"Calculated warranty end date: {warranty_end}")
            
            # Get current date with time set to midnight for fair comparison
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            print(f"Current date (normalized): {today}")
            
            # Calculate days
            days_remaining = (warranty_end - today).days
            total_warranty_days = warranty_months * 30
            days_used = min(total_warranty_days, (today - purchase_date).days)
            
            print(f"Days remaining: {days_remaining}")
            print(f"Total warranty days: {total_warranty_days}")
            print(f"Days used: {days_used}")
            
            # Determine if warranty is valid
            is_valid = today <= warranty_end
            print(f"Warranty valid: {is_valid}")
            
            # Calculate percentage remaining
            percentage_remaining = 0
            if days_remaining > 0:
                percentage_remaining = max(0, round(days_remaining / total_warranty_days * 100, 1))
            print(f"Percentage remaining: {percentage_remaining}%")
            
            return {
                'is_valid': is_valid,
                'purchase_date': purchase_date.date(),
                'warranty_end_date': warranty_end.date(),
                'days_remaining': max(0, days_remaining),
                'days_used': days_used,
                'total_days': total_warranty_days,
                'percentage_remaining': percentage_remaining
            }
        except ValueError as e:
            print(f"Error parsing date: {e}")
            raise ValueError(f"Invalid date format. Please provide date in YYYY-MM-DD format. Error: {str(e)}")
        except Exception as e:
            print(f"Error calculating warranty status: {e}")
            raise Exception(f"Error calculating warranty status: {str(e)}")

    def format_warranty_response(self, bill_number: str, warranty_info: dict, status: dict) -> str:
        """Format a detailed warranty response"""
        product_info = warranty_info['product_info']
        product_desc = ''
        if product_info:
            parts = []
            if 'brand' in product_info:
                parts.append(f"Brand: {product_info['brand']}")
            if 'model' in product_info:
                parts.append(f"Model: {product_info['model']}")
            if 'type' in product_info:
                parts.append(f"Type: {product_info['type']}")
            product_desc = f"\nProduct Information:\n{', '.join(parts)}\n"

        if status['is_valid']:
            response = [
                f"✅ Your product (Bill No: {bill_number}) is currently under warranty.",
                f"{product_desc}",
                f"Purchase Date: {status['purchase_date']}",
                f"Warranty End Date: {status['warranty_end_date']}",
                f"Days Remaining: {status['days_remaining']} days ({status['percentage_remaining']}% of warranty remaining)",
                f"Warranty Duration: {warranty_info['warranty_months']} months"
            ]
            
            if warranty_info['extended_warranty']:
                response.append("📋 Note: Extended warranty is active for this product.")
            
            if status['days_remaining'] < 30:
                response.append("⚠️ Warning: Your warranty is expiring soon!")
            
        else:
            response = [
                f"❌ Your product (Bill No: {bill_number}) is no longer under warranty.",
                f"{product_desc}",
                f"Purchase Date: {status['purchase_date']}",
                f"Warranty Expired On: {status['warranty_end_date']}",
                f"Original Warranty Duration: {warranty_info['warranty_months']} months"
            ]
        
        if warranty_info['special_conditions']:
            response.append("\nSpecial Conditions:")
            for condition in warranty_info['special_conditions']:
                response.append(f"• {condition}")
        
        return "\n".join(response)

    def act(self, user_input: str) -> str:
        """Process warranty-related queries and return detailed information"""
        try:
            bill_number = self.extract_bill_number(user_input)
            purchase_date_str = self.extract_purchase_date(user_input)
            
            print(f"Extracted bill number: {bill_number}")
            print(f"Extracted purchase date: {purchase_date_str}")
            
            if not bill_number:
                return "Could you please provide your bill number? This helps me check your warranty status accurately."
            
            warranty_info = self.get_warranty_info(bill_number)
            print(f"Retrieved warranty info: {warranty_info}")
            
            if not purchase_date_str:
                months = warranty_info['warranty_months']
                product_info = warranty_info['product_info']
                product_desc = ''
                if product_info:
                    parts = []
                    if 'brand' in product_info:
                        parts.append(f"Brand: {product_info['brand']}")
                    if 'model' in product_info:
                        parts.append(f"Model: {product_info['model']}")
                    if 'type' in product_info:
                        parts.append(f"Type: {product_info['type']}")
                    product_desc = f"\nProduct Information:\n{', '.join(parts)}"
                
                return (
                    f"I found your product information (Bill No: {bill_number})."
                    f"{product_desc}\n"
                    f"The warranty period for your product is {months} months from the purchase date.\n"
                    "Could you please provide the purchase date (in YYYY-MM-DD format) to check if it's still under warranty?"
                )
            
            status = self.calculate_warranty_status(purchase_date_str, warranty_info['warranty_months'])
            print(f"Calculated warranty status: {status}")
            
            return self.format_warranty_response(bill_number, warranty_info, status)
        except ValueError as e:
            return f"⚠️ {str(e)}"
        except Exception as e:
            print(f"Error in warranty agent: {e}")
            return "I apologize, but I encountered an error while checking your warranty status. Please make sure you provided the correct bill number and purchase date in YYYY-MM-DD format."