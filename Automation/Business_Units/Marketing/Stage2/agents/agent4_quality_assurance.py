"""Agent 4: Quality Assurance & Validation
Ensures premium consulting-level quality and completeness
"""
from typing import Dict, List, Any, Tuple
import re


class QualityAssuranceAgent:
    """Agent responsible for quality assurance and validation"""

    def __init__(self):
        self.validation_results = []

    def check_sub_headings(self, section: str, expected_sub_headings: List[str]) -> Tuple[bool, List[str]]:
        """Check if all required sub-headings are present"""
        missing = []
        for sub_heading in expected_sub_headings:
            if sub_heading not in section:
                missing.append(sub_heading)
        return len(missing) == 0, missing

    def check_quantification(self, text: str) -> Dict[str, Any]:
        """Check if text contains quantified metrics"""
        # Look for numbers, percentages, dollar signs, etc.
        has_numbers = bool(re.search(r'\d+', text))
        has_percentage = bool(re.search(r'\d+%', text))
        has_dollar = bool(re.search(r'\$\d+', text))
        has_time = bool(re.search(r'\d+\s*(hour|day|week|month|year|minute|second)', text, re.IGNORECASE))

        return {
            "has_metrics": has_numbers,
            "has_percentage": has_percentage,
            "has_dollar_amount": has_dollar,
            "has_time_metric": has_time,
            "quantified": has_numbers or has_percentage or has_dollar or has_time
        }

    def check_competitor_vendor_count(self, industry_alignment: str) -> Dict[str, Any]:
        """Check if minimum 2-3 competitors/vendors are named"""
        # Simple heuristic: look for company names (capitalized words)
        # In production, this could be more sophisticated
        potential_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', industry_alignment)
        unique_names = set(potential_names) - {'The', 'This', 'These', 'Those', 'When', 'Where', 'What', 'Which'}

        return {
            "competitor_vendor_count": len(unique_names),
            "meets_minimum": len(unique_names) >= 2,
            "identified_names": list(unique_names)[:5]  # Show first 5
        }

    def check_source_citations(self, annotation: str) -> Dict[str, Any]:
        """Check if sources and confidence levels are cited"""
        has_source = "Source:" in annotation or "source:" in annotation
        has_confidence = "Confidence Level:" in annotation or "confidence" in annotation.lower()
        has_urls = bool(re.search(r'https?://', annotation))

        return {
            "has_source_section": has_source,
            "has_confidence_level": has_confidence,
            "has_urls": has_urls,
            "properly_cited": has_source and has_confidence
        }

    def check_sentence_count(self, text: str, min_sentences: int = 3) -> Dict[str, Any]:
        """Check if section has minimum required sentences"""
        # Simple sentence count by periods
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        sentence_count = len(sentences)

        return {
            "sentence_count": sentence_count,
            "meets_minimum": sentence_count >= min_sentences
        }

    def validate_enriched_use_case(self, enriched: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single enriched use case"""
        use_case_name = enriched['original_use_case']['original_name']
        print(f"  Validating: {use_case_name}")

        if not enriched.get('success', False):
            return {
                "use_case_name": use_case_name,
                "passed": False,
                "error": enriched.get('error', 'Unknown error')
            }

        enriched_data = enriched.get('enriched_data', {})

        validations = {
            "use_case_name": use_case_name,
            "passed": True,
            "issues": [],
            "warnings": []
        }

        # Check detailed description
        detailed_desc = enriched_data.get('detailed_description', '')
        if detailed_desc:
            has_all, missing = self.check_sub_headings(detailed_desc, [
                "Business Context & Problem",
                "Solution & Technology",
                "Integration & Process",
                "Current Status & Outcomes"
            ])
            if not has_all:
                validations["issues"].append(f"Missing sub-headings in Detailed Description: {missing}")
                validations["passed"] = False

            quant = self.check_quantification(detailed_desc)
            if not quant["quantified"]:
                validations["warnings"].append("Detailed Description lacks quantified metrics")
        else:
            validations["issues"].append("Missing Detailed Description")
            validations["passed"] = False

        # Check business outcomes
        outcomes = enriched_data.get('business_outcomes', '')
        if outcomes:
            has_all, missing = self.check_sub_headings(outcomes, [
                "Productivity & Efficiency",
                "Quality & Consistency",
                "Cost & Financial Impact",
                "Strategic Benefits"
            ])
            if not has_all:
                validations["issues"].append(f"Missing sub-headings in Business Outcomes: {missing}")
                validations["passed"] = False
        else:
            validations["issues"].append("Missing Business Outcomes")
            validations["passed"] = False

        # Check industry alignment
        industry = enriched_data.get('industry_alignment', '')
        if industry:
            has_all, missing = self.check_sub_headings(industry, [
                "Competitive Landscape",
                "Technology & Vendors",
                "Industry Benchmarks",
                "Strategic Positioning"
            ])
            if not has_all:
                validations["issues"].append(f"Missing sub-headings in Industry Alignment: {missing}")
                validations["passed"] = False

            comp_check = self.check_competitor_vendor_count(industry)
            if not comp_check["meets_minimum"]:
                validations["warnings"].append(f"Only {comp_check['competitor_vendor_count']} competitors/vendors identified (need 2-3)")
        else:
            validations["issues"].append("Missing Industry Alignment")
            validations["passed"] = False

        # Check implementation considerations
        impl = enriched_data.get('implementation', '')
        if impl:
            has_all, missing = self.check_sub_headings(impl, [
                "Technical & Integration",
                "Change Management",
                "Risk & Compliance",
                "Operational & Scaling"
            ])
            if not has_all:
                validations["issues"].append(f"Missing sub-headings in Implementation: {missing}")
                validations["passed"] = False
        else:
            validations["issues"].append("Missing Implementation Considerations")
            validations["passed"] = False

        # Check KPIs
        kpis = enriched_data.get('kpis', '')
        if kpis:
            has_all, missing = self.check_sub_headings(kpis, [
                "Operational Metrics",
                "Financial Metrics",
                "Quality Metrics",
                "Strategic Metrics"
            ])
            if not has_all:
                validations["issues"].append(f"Missing sub-headings in KPIs: {missing}")
                validations["passed"] = False
        else:
            validations["issues"].append("Missing KPIs")
            validations["passed"] = False

        # Check annotation
        annotation = enriched_data.get('annotation', '')
        if annotation:
            citation_check = self.check_source_citations(annotation)
            if not citation_check["properly_cited"]:
                validations["warnings"].append("Annotation missing proper source citations or confidence level")
        else:
            validations["issues"].append("Missing Information Gaps & Annotation")
            validations["passed"] = False

        return validations

    def run(self, enrichment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute quality assurance for all enriched use cases"""
        print("=" * 80)
        print("AGENT 4: QUALITY ASSURANCE & VALIDATION")
        print("=" * 80)

        enriched_use_cases = enrichment_data.get("enriched_use_cases", [])

        validation_results = []
        passed_count = 0
        failed_count = 0

        for enriched in enriched_use_cases:
            validation = self.validate_enriched_use_case(enriched)
            validation_results.append(validation)

            if validation["passed"]:
                passed_count += 1
                print(f"    ✓ {validation['use_case_name']}")
            else:
                failed_count += 1
                print(f"    ✗ {validation['use_case_name']}")
                # Handle both error format and issues format
                if "error" in validation:
                    print(f"        - Error: {validation['error']}")
                elif "issues" in validation:
                    for issue in validation["issues"]:
                        print(f"        - {issue}")

            if validation.get("warnings"):
                for warning in validation["warnings"]:
                    print(f"        ⚠ {warning}")

        print(f"\n{'=' * 80}")
        print(f"VALIDATION SUMMARY: {passed_count} passed, {failed_count} failed")
        print("=" * 80)

        return {
            "validation_results": validation_results,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "all_passed": failed_count == 0
        }


if __name__ == "__main__":
    print("Quality Assurance Agent - requires enriched data to run")
