from PyPDF2 import PdfReader
from utils.memory import log_to_memory
import re

def process_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    full_text = "".join([page.extract_text() or "" for page in reader.pages])
    flags = {}

    lower_text = full_text.lower()

    # Invoice detection
    if "invoice" in lower_text:
        # Regex to match amounts like 1000, 1,000, 1000.00, 1,000.00, 1000.5,etc.
        amounts = re.findall(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b", full_text)
        numeric_amounts = []
        for amount in amounts:
            try:
                cleaned = amount.replace(",", "")
                numeric_amounts.append(float(cleaned))
            except ValueError:
                continue

        if any(amount > 10000 for amount in numeric_amounts):
            flags["invoice_alert"] = "Invoice total exceeds 10,000"
            log_to_memory("pdf_agent", {"invoice_alert_amounts": numeric_amounts})

    # Compliance flags for policy documents
    compliance_terms = ["gdpr", "fda", "hipaa", "iso"]
    for term in compliance_terms:
        if term in lower_text:
            flags["compliance_flag"] = term.upper()
            log_to_memory("pdf_agent", {"compliance_term_found": term})
            break

    if flags:
        # Return alert if invoice alert found, else compliance flag
        return "trigger_alert" if "invoice_alert" in flags else "flag_compliance"

    log_to_memory("pdf_agent", {"status": "ok"})
    return "ok"
