# agents/use_case_generator_agent.py  
"""  
AGENT 2: USE CASE GENERATOR AGENT  
Responsibilities:  
- Generate 8 AI/ML use cases per sub-function using Claude Sonnet 4.5  
- Apply 27-column enrichment with sub-headings  
- Ensure proper UC ID numbering  
- Validate JSON output  
- Direct Anthropic API calls (no LangChain agent framework)  
"""
  
import json  
from typing import List, Dict  
from config.config_tr_auth import get_anthropic_client, ANTHROPIC_MODEL
  
class UseCaseGeneratorAgent:  
    """Agent responsible for generating use cases with Claude Sonnet 4.5 via direct API calls"""
      
    def __init__(self):  
        self.name = "Use Case Generator Agent"  
        self.client = get_anthropic_client()  
        self.model = ANTHROPIC_MODEL  
        print(f"🤖 {self.name} initialized with model: {self.model}")
      
    def generate_use_cases(  
        self,   
        sub_function_name: str,   
        activities: List[Dict],   
        bu_context: str,   
        uc_counter: int  
    ) -> List[Dict]:  
        """  
        Generate 8 use cases for a sub-function using Claude Sonnet 4.5
          
        Args:  
            sub_function_name: Name of the sub-function (e.g., "Demand Generation")  
            activities: List of top 8 activities with time_spent_pct and current_tools  
            bu_context: Business context from BU Intelligence document  
            uc_counter: Running counter for UC ID numbering
          
        Returns:  
            List of 8 use case dictionaries (27 columns each)  
        """  
        print(f"\n{'='*70}")  
        print(f"🤖 {self.name} - GENERATING USE CASES")  
        print(f"{'='*70}")  
        print(f"   Sub-function: {sub_function_name}")  
        print(f"   Activities: {len(activities)}")  
        print(f"   Starting UC ID: {uc_counter + 1}")
          
        # Build activities text for prompt  
        activities_text = "\n".join([  
            f"{i+1}. {a['activity']} (Time Spent: {a['time_spent_pct']}%, Current Tools: {a['current_tools']})"   
            for i, a in enumerate(activities)  
        ])
          
        # Generate sub-function abbreviation for UC ID  
        abbrev = ''.join([c for c in sub_function_name if c.isupper()])[:4]  
        if not abbrev:  
            abbrev = sub_function_name[:4].upper()
          
        # Build prompt  
        prompt = self._build_prompt(  
            sub_function_name,   
            activities_text,   
            bu_context,   
            abbrev,   
            uc_counter  
        )
          
        # Call Claude Sonnet 4.5  
        print(f"   🤖 Calling Claude Sonnet 4.5...")
          
        try:  
            response = self.client.messages.create(  
                model=self.model,  
                max_tokens=16000,  
                temperature=0.7,  
                messages=[{"role": "user", "content": prompt}]  
            )
              
            # Parse response  
            response_text = response.content[0].text
              
            # Extract JSON (Claude might wrap in markdown)  
            if "```json" in response_text:  
                response_text = response_text.split("```json")[1].split("```")[0].strip()  
            elif "```" in response_text:  
                response_text = response_text.split("```")[1].split("```")[0].strip()
              
            use_cases = json.loads(response_text)
              
            print(f"   ✅ Generated {len(use_cases)} use cases for '{sub_function_name}'")
              
            return use_cases
              
        except json.JSONDecodeError as e:  
            print(f"   ❌ JSON parsing error: {e}")  
            print(f"   Response (first 500 chars): {response_text[:500]}...")  
            return []  
        except Exception as e:  
            print(f"   ❌ Error generating use cases: {e}")  
            return []
      
    def _build_prompt(  
        self,   
        sub_function_name: str,   
        activities_text: str,   
        bu_context: str,   
        abbrev: str,   
        uc_counter: int  
    ) -> str:  
        """Build the Claude prompt for use case generation"""
          
        # Calculate UC IDs  
        uc_start = uc_counter + 1  
        uc_end = uc_counter + 8
          
        prompt = f"""You are an AI consultant generating AI/ML use cases for the **{sub_function_name}** sub-function of Thomson Reuters Marketing organization.
  
**BUSINESS CONTEXT (Summary):**  
{bu_context[:1500]}
  
**TARGET ACTIVITIES (Top 8 by Time Spent %):**  
{activities_text}
  
**TASK:**  
Generate exactly **8 AI/ML use cases** (one per activity) with the following 27 columns in JSON format.
  
**COLUMN DEFINITIONS:**  
1. use_case_id: Format "UC-{abbrev}-{uc_start:03d}" through "UC-{abbrev}-{uc_end:03d}" (increment by 1 for each use case)  
2. use_case_title: Concise, descriptive title (e.g., "AI-Powered Campaign Content Generation")  
3. functional_non_functional: Always "Functional"  
4. company: Always "Thomson Reuters"  
5. status: Always "Proposed"  
6. detailed_description: 150-200 words with 4 sub-headings:  
   - **Use Case Overview:** Brief description  
   - **Key Capabilities:** Main features  
   - **User Workflow:** How users interact  
   - **Expected Outcomes:** Results and benefits  
7. ai_technology: Specify technology (e.g., "GenAI", "ML", "NLP", "Computer Vision")  
8. business_impact: 120-150 words with 4 sub-headings:  
   - **Efficiency Gains (FTE/Time Impact):** Include specific percentages and FTE numbers (MANDATORY)  
   - **Quality Improvements:** Quality benefits  
   - **Cost Savings:** Financial impact  
   - **Strategic Benefits:** Strategic advantages  
9. business_impact_category: Choose one: "Efficiency", "Innovation", "Risk Reduction", "Customer Experience"  
10. solution_complexity: Choose one: "Low", "Medium", "High"  
11. implementation_complexity: Choose one: "Low", "Medium", "High"  
12. implementation_priority: Choose one: "High", "Medium", "Low"  
13. target_process_area: Use the exact activity name from the list above  
14. current_tools: List current tools (e.g., "Writer, Adobe Firefly, Salesforce")  
15. impacted_roles: List relevant roles (e.g., "Content Marketers, Campaign Managers")  
16. impacted_activities: Use the exact activity name from the list above  
17. current_tool_adaptation: 80-120 words with 5 sub-headings:  
    - **Current Tool Leverage:** How existing tools support this  
    - **Hybrid Approach:** Combining tools  
    - **Tool Gaps:** What's missing  
    - **Recommendations:** Tool suggestions  
    - **Integration:** How to integrate  
18. adaptation_to_marketing: 60-100 words describing how this applies to 2-3 Marketing sub-functions (e.g., Demand Generation, Product Marketing, Digital Marketing)  
19. implementation_insights: 80-120 words with 4 sub-headings:  
    - **Competitive Implementations:** Examples from Bloomberg, LexisNexis, etc.  
    - **Vendor Solutions:** Case studies from Writer.ai, Adobe, etc.  
    - **Best Practices:** Industry best practices  
    - **Implementation Approach:** How to implement  
20. risks_mitigations: List 3-5 risks with mitigations (e.g., "1. Risk: Data quality issues, Mitigation: Implement data validation, 2. ...")  
21. industry_alignment: 80-120 words with 4 sub-headings:  
    - **Industry Relevance:** Relevance to legal/tax/accounting  
    - **Competitive Benchmarks:** Industry benchmarks  
    - **Regulatory Considerations:** Compliance requirements  
    - **Market Trends:** Current trends  
22. success_metrics: 60-100 words with 4 sub-headings:  
    - **Quantitative:** Measurable metrics (e.g., "30% time savings")  
    - **Qualitative:** Quality metrics  
    - **Baseline & Targets:** Current vs. target state  
    - **Measurement:** How to measure  
23. source_publication: Source of information (e.g., "Industry research, competitor analysis")  
24. source_url: Example URL (e.g., "https://example.com/research")  
25. source_date: Date in format "YYYY-MM-DD" (e.g., "2025-01-15")  
26. information_gaps: 80-120 words with 4 MANDATORY sub-headings:  
    - **Source:** Where data came from (File 3 activity analysis, competitive research)  
    - **Confidence Level:** High/Medium/Low with justification  
    - **Activity Context:** Activity details (time spent %, FTE)  
    - **Information Gaps:** What's missing or needs validation  
27. sub_function: Always "{sub_function_name}"
  
**EXAMPLE OUTPUT (for reference only):**  
[  
  {{  
    "use_case_id": "UC-{abbrev}-{uc_start:03d}",  
    "use_case_title": "AI-Powered Campaign Content Generation",  
    "functional_non_functional": "Functional",  
    "company": "Thomson Reuters",  
    "status": "Proposed",  
    "detailed_description": "**Use Case Overview:** Automate campaign content creation using GenAI to accelerate marketing workflows. **Key Capabilities:** Generate blog posts, social media content, email campaigns, and landing page copy with consistent brand voice. **User Workflow:** Marketer inputs campaign brief and target audience, AI generates multiple content variations, human reviews and approves final content. **Expected Outcomes:** 70% faster content creation, consistent brand messaging across channels, reduced dependency on external agencies.",  
    "ai_technology": "GenAI (Large Language Models)",  
    "business_impact": "**Efficiency Gains (FTE/Time Impact):** 30% time savings in content creation, equivalent to 2 FTE reduction across the team. Content production time reduced from 5 days to 1.5 days per campaign. **Quality Improvements:** Consistent brand voice across all channels, improved messaging clarity. **Cost Savings:** $200K annual savings from reduced agency spend and faster time-to-market. **Strategic Benefits:** Enables rapid response to market trends, scales content production without proportional headcount increase.",  
    "business_impact_category": "Efficiency",  
    "solution_complexity": "Medium",  
    "implementation_complexity": "Medium",  
    "implementation_priority": "High",  
    "target_process_area": "Campaign Planning",  
    "current_tools": "Writer, Adobe Firefly, Salesforce",  
    "impacted_roles": "Content Marketers, Campaign Managers, Creative Directors",  
    "impacted_activities": "Campaign Planning",  
    "current_tool_adaptation": "**Current Tool Leverage:** Writer and Adobe Firefly provide baseline content generation capabilities for text and visual content. **Hybrid Approach:** Combine GenAI content generation with human creative review and brand compliance checks. **Tool Gaps:** Limited multi-language support and industry-specific terminology. **Recommendations:** Integrate Claude.ai for advanced reasoning and translations, fine-tune models on Thomson Reuters brand guidelines. **Integration:** API-based workflow connecting Writer, Salesforce, and content approval systems.",  
    "adaptation_to_marketing": "This use case applies to Demand Generation (campaign content creation), Product Marketing (product messaging and collateral), and Digital Marketing (social media content and ad copy). Each sub-function can leverage GenAI for content creation with sub-function-specific templates and brand guidelines.",  
    "implementation_insights": "**Competitive Implementations:** Bloomberg uses GPT-4 for financial content generation achieving 40% time savings. LexisNexis deployed GenAI for legal content with 35% productivity gains. **Vendor Solutions:** Writer.ai case study with Prudential shows 10x content output increase with 75% time savings. Adobe Firefly enables rapid visual content creation. **Best Practices:** Implement human-in-the-loop review, fine-tune models on brand voice, establish content governance framework. **Implementation Approach:** Start with pilot campaign, measure quality and speed metrics, scale gradually to all content types.",  
    "risks_mitigations": "1. Risk: Brand voice inconsistency, Mitigation: Fine-tune models on brand guidelines and implement approval workflows. 2. Risk: Factual inaccuracies in content, Mitigation: Implement fact-checking workflow and human review for all claims. 3. Risk: Legal and compliance issues, Mitigation: Legal review for regulated content, automated compliance checks. 4. Risk: Over-reliance on AI reducing creative quality, Mitigation: Maintain human creative oversight and use AI as augmentation tool.",  
    "industry_alignment": "**Industry Relevance:** Legal and financial services sectors require high-quality, compliant marketing content that balances technical accuracy with accessibility. **Competitive Benchmarks:** 87% of B2B marketers use AI for content creation (Gartner 2024), with average productivity gains of 40%. **Regulatory Considerations:** FINRA and SEC compliance required for financial product marketing, GDPR compliance for customer data usage. **Market Trends:** GenAI adoption in B2B marketing growing 45% YoY, with focus shifting from basic content generation to strategic content planning.",  
    "success_metrics": "**Quantitative:** 30% time savings in content creation, 50% faster campaign launch, 10x increase in content volume, 25% reduction in agency costs. **Qualitative:** Improved brand consistency scores, higher engagement rates, better message clarity. **Baseline & Targets:** Current baseline of 10 content pieces per week, target 50 pieces per week with same team size. **Measurement:** Track content output volume, time spent per piece, engagement metrics (CTR, conversions), brand consistency scores, cost per content piece.",  
    "source_publication": "Gartner Marketing AI Report 2024, Writer.ai case studies, Bloomberg Technology Blog",  
    "source_url": "https://www.gartner.com/marketing-ai-2024",  
    "source_date": "2024-11-15",  
    "information_gaps": "**Source:** File 3 activity analysis (Campaign Planning consumes 70% of time) combined with competitive research from Bloomberg and LexisNexis implementations, vendor case studies from Writer.ai and Adobe. **Confidence Level:** High confidence based on industry benchmarks and vendor-validated case studies, medium confidence on specific Thomson Reuters implementation timeline. **Activity Context:** Campaign Planning activity consumes 70% of Demand Generation time (approximately 3.5 FTE), representing significant automation opportunity. **Information Gaps:** Specific Writer.ai enterprise tier pricing for Thomson Reuters scale requires vendor quote, exact brand voice training dataset requirements need validation with Marketing team, integration complexity with existing Salesforce workflows needs technical assessment.",  
    "sub_function": "{sub_function_name}"  
  }}  
]
  
**CRITICAL REQUIREMENTS:**  
1. Generate exactly 8 use cases (one per activity in the TARGET ACTIVITIES list)  
2. Each use case MUST have all 27 fields  
3. Use case IDs must increment: UC-{abbrev}-{uc_start:03d}, UC-{abbrev}-{uc_start+1:03d}, ..., UC-{abbrev}-{uc_end:03d}  
4. Map "target_process_area" and "impacted_activities" to actual activity names from the TARGET ACTIVITIES list  
5. Include specific FTE/Time Impact calculations in "business_impact" (MANDATORY)  
6. Apply sub-headings (using **bold**) in columns 6, 8, 17, 18, 19, 21, 22, 26  
7. Word counts: detailed_description (150-200), business_impact (120-150), current_tool_adaptation (80-120), etc.  
8. Return ONLY a valid JSON array with 8 objects, no additional text before or after
  
Generate the 8 use cases now in JSON format."""
          
        return prompt