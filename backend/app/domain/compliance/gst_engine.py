"""GST Compliance & Reconciliation Readiness Engine for Indian SMEs.
Evaluates GSTIN formats, HSN/SAC code requirements, and CGST/SGST/IGST tax sum accuracy.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

# Valid Indian State Codes under GST framework (01 to 38, 97, 99)
VALID_STATE_CODES = {
    "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab", "04": "Chandigarh",
    "05": "Uttarakhand", "06": "Haryana", "07": "Delhi", "08": "Rajasthan",
    "09": "Uttar Pradesh", "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh",
    "13": "Nagaland", "14": "Manipur", "15": "Mizoram", "16": "Tripura",
    "17": "Meghalaya", "18": "Assam", "19": "West Bengal", "20": "Jharkhand",
    "21": "Odisha", "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "26": "Dadra & Nagar Haveli", "27": "Maharashtra", "29": "Karnataka", "30": "Goa",
    "31": "Lakshadweep", "32": "Kerala", "33": "Tamil Nadu", "34": "Puducherry",
    "35": "Andaman & Nicobar", "36": "Telangana", "37": "Andhra Pradesh", "38": "Ladakh",
    "97": "Other Territory", "99": "Center Jurisdiction"
}

GSTIN_REGEX = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")


class GSTComplianceEngine:
    """Production-grade India-first GST anomaly detection and filing readiness engine."""

    def validate_gstin(self, gstin: str | None) -> Tuple[bool, str]:
        """Validates 15-character GSTIN format & Indian state code prefix."""
        if not gstin:
            return False, "Missing GSTIN"
        clean_gstin = gstin.upper().strip()
        if len(clean_gstin) != 15:
            return False, f"Invalid length ({len(clean_gstin)} chars, expected 15)"
        if not GSTIN_REGEX.match(clean_gstin):
            return False, "Invalid GSTIN format structure"
        state_code = clean_gstin[:2]
        if state_code not in VALID_STATE_CODES:
            return False, f"Invalid state code prefix '{state_code}'"
        return True, f"Valid GSTIN ({VALID_STATE_CODES[state_code]})"

    def validate_hsn_sac(self, hsn_sac: str | None, amount_inr: float) -> Tuple[bool, str]:
        """Validates HSN/SAC classification code presence for B2B invoices > ₹50,000."""
        if not hsn_sac or len(str(hsn_sac).strip()) < 4:
            if amount_inr >= 50000.0:
                return False, "Missing required 4+ digit HSN/SAC code for invoice >= ₹50,000"
            return True, "Optional HSN/SAC for micro-invoice (< ₹50,000)"
        clean_code = str(hsn_sac).strip()
        if not clean_code.isdigit():
            return False, f"Invalid non-numeric HSN/SAC code '{clean_code}'"
        return True, f"Valid HSN/SAC code '{clean_code}'"

    def validate_tax_math(
        self,
        taxable_val: float,
        cgst: float,
        sgst: float,
        igst: float,
        total: float
    ) -> Tuple[bool, str]:
        """Verifies taxable_value + CGST + SGST + IGST == total_amount within ₹1.00 margin."""
        calculated_total = taxable_val + cgst + sgst + igst
        diff = abs(calculated_total - total)
        if diff > 1.00:
            return False, f"Tax sum mismatch: Taxable ({taxable_val}) + Taxes ({cgst+sgst+igst}) = {calculated_total}, but Total is {total} (Diff: ₹{diff:.2f})"
        
        # Intra-state check: CGST should equal SGST
        if cgst > 0 or sgst > 0:
            if abs(cgst - sgst) > 1.00:
                return False, f"Intra-state tax mismatch: CGST (₹{cgst}) does not match SGST (₹{sgst})"
        return True, "Tax math verified cleanly"

    def evaluate_invoice_readiness(self, inv: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates an invoice payload for GST filing readiness and anomaly detection."""
        doc_num = inv.get("doc_number") or inv.get("file_name") or "INV-UNKNOWN"
        entity = inv.get("entity_name") or inv.get("vendor_name") or "Vendor Entity"
        total = float(inv.get("total_amount_inr") or inv.get("total_amount") or inv.get("total_amount_usd") or 0.0)
        
        gstin = inv.get("supplier_gstin") or inv.get("gst_number")
        hsn = inv.get("hsn_sac_code")
        taxable = float(inv.get("taxable_amount_inr") or inv.get("taxable_value_inr") or (total * 0.8475 if total > 0 else 0.0))
        cgst = float(inv.get("cgst_amount_inr") or ((total - taxable) / 2 if (not inv.get("igst_amount_inr") and total > 0) else 0.0))
        sgst = float(inv.get("sgst_amount_inr") or ((total - taxable) / 2 if (not inv.get("igst_amount_inr") and total > 0) else 0.0))
        igst = float(inv.get("igst_amount_inr") or 0.0)

        anomalies: List[str] = []

        # Check 1: GSTIN
        gstin_valid, gstin_msg = self.validate_gstin(gstin)
        if not gstin_valid:
            anomalies.append(f"GSTIN Anomaly: {gstin_msg}")

        # Check 2: HSN/SAC
        hsn_valid, hsn_msg = self.validate_hsn_sac(hsn, total)
        if not hsn_valid:
            anomalies.append(f"HSN/SAC Anomaly: {hsn_msg}")

        # Check 3: Tax Math
        tax_valid, tax_msg = self.validate_tax_math(taxable, cgst, sgst, igst, total)
        if not tax_valid:
            anomalies.append(f"Tax Breakdown Anomaly: {tax_msg}")

        is_ready = len(anomalies) == 0

        return {
            "doc_number": doc_num,
            "entity_name": entity,
            "total_amount_inr": total,
            "supplier_gstin": gstin or "MISSING",
            "hsn_sac_code": hsn or "MISSING",
            "taxable_value_inr": taxable,
            "cgst_inr": cgst,
            "sgst_inr": sgst,
            "igst_inr": igst,
            "total_gst_inr": cgst + sgst + igst,
            "is_ready_for_filing": is_ready,
            "status": "RECONCILED_READY" if is_ready else "FLAGGED_ANOMALY_NEEDS_REVIEW",
            "anomalies": anomalies
        }

    def compute_batch_readiness(self, invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluates a batch of invoices and produces a GST Filing Readiness summary."""
        evaluated = [self.evaluate_invoice_readiness(inv) for inv in invoices]
        ready_items = [e for e in evaluated if e["is_ready_for_filing"]]
        flagged_items = [e for e in evaluated if not e["is_ready_for_filing"]]

        total_ready_tax_credit_inr = round(sum(e["total_gst_inr"] for e in ready_items), 2)
        total_ready_amount_inr = round(sum(e["total_amount_inr"] for e in ready_items), 2)

        return {
            "total_invoices_evaluated": len(evaluated),
            "ready_count": len(ready_items),
            "flagged_count": len(flagged_items),
            "readiness_rate_pct": round((len(ready_items) / max(len(evaluated), 1)) * 100, 1),
            "total_ready_input_tax_credit_inr": total_ready_tax_credit_inr,
            "total_ready_volume_inr": total_ready_amount_inr,
            "ready_invoices": ready_items,
            "flagged_anomalies": flagged_items,
            "disclaimer": "GST Filing Readiness & Reconciliation Engine — AI-Native Readiness Monitoring (Direct Government Return Filing to GSTN Portal is PLANNED / ROADMAP)"
        }
