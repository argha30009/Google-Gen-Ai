"""
Fact-Check Agent using Gemini API
Analyzes headlines for contradictions and controversial claims
"""

import json
import os
from typing import Dict, Any, List, Optional
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class FactCheckAgent:
    """Agent for analyzing headlines for contradictions and controversial claims."""
    
    def __init__(self):
        """Initialize the fact-check agent with Gemini."""
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction="""You are an Expert Fact Check Analysis Agent that provides comprehensive verification analysis of news headlines.

Your analysis must state clear VERIFIABILITY (verifiable/unverifiable/partially verifiable) and include detailed factual assessment.

✅ OUTPUT FORMAT (JSON)

{
  "factcheck_summary": {
    "verification_status": "VERIFIABLE|PARTIALLY_VERIFIABLE|UNVERIFIABLE|CONTRADICTORY",
    "overall_assessment": "Comprehensive 2-4 sentence summary stating what IS verifiable",
    "verdict": "MOSTLY_TRUE|MIXED|MOSTLY_FALSE|UNVERIFIABLE",
    "verifiable_facts": [
      "Specific verifiable fact 1 with details",
      "Specific verifiable fact 2 with numbers/dates",
      "Specific verifiable fact 3 about core event"
    ],
    "contradictions": [
      {
        "claim": "Exact headline",
        "source": "Source name",
        "verdict": "VERIFIED|UNVERIFIED|MISLEADING|FALSE",
        "issue": "What's problematic",
        "severity": "Low|Medium|High",
        "explanation": "Detailed clarification"
      }
    ],
    "areas_of_concern": ["Ethical concern 1", "Interpretive difference 1"],
    "context": "Background information (2-3 sentences)",
    "conclusion": "Comprehensive conclusion about verifiability and where discrepancies lie"
  },
  "formatted_markdown": "Detailed markdown report"
}

🎨 COMPREHENSIVE MARKDOWN FORMAT

Create a detailed, professional fact-check report that clearly states VERIFIABILITY:

---

## 📊 Overall Verdict: [MOSTLY TRUE / MIXED / MOSTLY FALSE / UNVERIFIABLE]

[One punchy sentence about the overall factual consistency]

---

## 🔍 Fact Check Analysis

### ✅ Claim #1: "[Exact headline or claim]"

**� Source:** [Publisher/Source]  
**⚖️ Verdict:** ✓ TRUE | ✗ FALSE | ⚠️ MISLEADING | ❓ UNVERIFIABLE  
**🎯 Severity:** 🟢 Low | 🟠 Medium | 🔴 High  

**� Analysis:**  
[Clear 1-2 sentence explanation of why this is true/false/misleading]

---

### ✅ Claim #2: "[Another claim if exists]"

[Same format as above]

---

## ✓ Supporting Facts

• [Verified fact 1 with source or context]  
• [Verified fact 2 with source or context]  
• [Verified fact 3 with source or context]

---

## 📚 Context

[2-3 sentences of relevant background information about the topic]

---

## 🎯 Final Verdict

[Clear, authoritative conclusion about the overall factual accuracy]

---

🧩 FORMATTING RULES

- Use clear visual separators (---) between sections
- Always show verdict with appropriate emoji: ✓ TRUE / ✗ FALSE / ⚠️ MISLEADING / ❓ UNVERIFIABLE
- Use consistent emojis:
  - � Overall Verdict
  - � Analysis sections
  - ✅ Individual claims
  - ✓ Supporting facts (bullet points)
  - 📚 Context
  - 🎯 Final Verdict
  - 🟢 Low severity / 🟠 Medium / 🔴 High
- Keep sections clean with proper spacing
- Be direct and authoritative, no fluff""",
            generation_config={
                "response_mime_type": "application/json"
            }
        )
    
    def analyze(self, headlines: List[str], query: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze headlines for contradictions and controversial claims.
        
        Args:
            headlines: List of headline strings
            query: Optional original user query for context
            
        Returns:
            Dictionary containing fact-check analysis with JSON summary and formatted markdown
        """
        try:
            # Add query context if provided
            query_context = f"User Query: '{query}'\n\n" if query else ""
            
            # Create the prompt
            prompt = f"""{query_context}Analyze these headlines for factual accuracy and verifiability:

{chr(10).join(f"{i+1}. {h}" for i, h in enumerate(headlines))}

IMPORTANT: Focus on verifying the FACTS in the headlines themselves, NOT the specific phrasing of the user query. Whether the user asks "trump qatar jet" or "Did trump get a private jet from Qatar?", your analysis should be consistent because you're analyzing the same headlines.

CRITICAL: Respond with ONLY valid JSON. NO text before or after.

Required JSON structure:
{{
  "factcheck_summary": {{
    "overall_assessment": "2-4 sentences that START with 'Based on the news headlines, it is VERIFIABLE/UNVERIFIABLE that...' and include specific details",
    "verdict": "MOSTLY_TRUE|MIXED|MOSTLY_FALSE|UNVERIFIABLE",
    "contradictions": [
      {{
        "claim": "exact headline",
        "source": "publisher name",
        "verdict": "VERIFIED|UNVERIFIED|MISLEADING|FALSE",
        "issue": "what's wrong or what's confirmed",
        "severity": "Low|Medium|High",
        "explanation": "detailed clarification"
      }}
    ],
    "supporting_evidence": ["specific verifiable fact 1", "specific verifiable fact 2"],
    "context": "2-3 sentence background",
    "conclusion": "comprehensive conclusion that states what aligns vs where discrepancies lie"
  }},
  "formatted_markdown": "Fact Check Report:\\n\\nBased on the news headlines, it is [VERIFIABLE/UNVERIFIABLE] that [detailed summary with specifics]. [Mention concerns or debates]. [State what aligns vs what differs].\\n\\n---\\n\\nVerifiable Facts:\\n\\n• [specific fact 1]\\n• [specific fact 2]\\n• [specific fact 3]\\n\\n---\\n\\nDiscrepancies/Differently Stated Information:\\n\\n• [different framing]\\n• [varying perspectives]\\n\\n---\\n\\nConclusion of Fact Check:\\n\\n[Comprehensive conclusion about factual consistency, where sources align, and where they differ]\\n\\nNote: Advanced AI-powered fact-check analysis is currently unavailable."
}}

CRITICAL REQUIREMENTS:
- MUST use "it is verifiable that" or "it is unverifiable that" language
- Include specific details: numbers, dates, entities, values
- Distinguish factual agreement from interpretive differences
- Be comprehensive and detailed
- State where headlines align on core facts vs differ in interpretation"""

            # Run the agent
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # Try to parse as JSON
            try:
                # Try direct JSON parsing first
                parsed_result = json.loads(result_text)
                
                return {
                    "factcheck_summary": parsed_result.get("factcheck_summary", {}),
                    "formatted_markdown": parsed_result.get("formatted_markdown", ""),
                    "analysis": parsed_result.get("formatted_markdown", result_text),  # Backward compatibility
                    "headlines_analyzed": len(headlines),
                    "status": "success"
                }
                
            except json.JSONDecodeError:
                # Fallback: treat entire response as markdown and parse it
                # Extract key information from markdown structure
                contradictions = []
                supporting_evidence = []
                overall_assessment = ""
                conclusion = ""
                context = ""
                
                # Try to extract sections
                lines = result_text.split('\n')
                current_section = None
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line.startswith("## Overall Assessment"):
                        current_section = "assessment"
                        # Get next non-empty line
                        for j in range(i+1, min(i+5, len(lines))):
                            if lines[j].strip():
                                overall_assessment = lines[j].strip()
                                break
                    elif line.startswith("## Contradictions"):
                        current_section = "contradictions"
                    elif line.startswith("## Supporting Evidence"):
                        current_section = "evidence"
                    elif line.startswith("## Context"):
                        current_section = "context"
                    elif line.startswith("## Conclusion"):
                        current_section = "conclusion"
                        # Get next non-empty line
                        for j in range(i+1, min(i+5, len(lines))):
                            if lines[j].strip():
                                conclusion = lines[j].strip()
                                break
                    elif current_section == "contradictions" and "Claim:" in line:
                        # Extract contradiction info (simplified)
                        claim = line.split("Claim:")[1].strip().strip('"') if "Claim:" in line else ""
                        severity = "Medium"  # default
                        if "🔴" in result_text[max(0,i-2):i+5]:
                            severity = "High"
                        elif "🟢" in result_text[max(0,i-2):i+5]:
                            severity = "Low"
                        if claim:
                            contradictions.append({
                                "claim": claim,
                                "source": "Analyzed headline",
                                "issue": "See markdown for details",
                                "severity": severity,
                                "explanation": "See formatted markdown"
                            })
                    elif current_section == "evidence" and (line.startswith("✅") or line.startswith("🧾") or line.startswith("📰")):
                        supporting_evidence.append(line[2:].strip() if len(line) > 2 else line)
                    elif current_section == "context" and line and not line.startswith("##"):
                        context += line + " "
                
                return {
                    "factcheck_summary": {
                        "overall_assessment": overall_assessment or "Analysis completed",
                        "contradictions": contradictions,
                        "supporting_evidence": supporting_evidence,
                        "context": context.strip() or "See formatted markdown for details",
                        "conclusion": conclusion or "Analysis available in markdown format"
                    },
                    "formatted_markdown": result_text,
                    "analysis": result_text,  # Backward compatibility
                    "headlines_analyzed": len(headlines),
                    "status": "success"
                }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "headlines_analyzed": len(headlines)
            }
    
def create_agent():
    """Factory function to create fact-check agent instance."""
    return FactCheckAgent()
