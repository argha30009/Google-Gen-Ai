"""
Fact-Check Agent using Gemini API
Analyzes headlines for contradictions and controversial claims
"""

import json
import os
from typing import Dict, Any, List
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class FactCheckAgent:
    """Agent for analyzing headlines for contradictions and controversial claims."""
    
    def __init__(self):
        """Initialize the fact-check agent with Gemini."""
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction="""You are a Fact Check Analysis Agent that reviews multiple news headlines
for factual accuracy, contradictions, and misleading claims.

Analyze the given headlines and produce both a JSON summary and
a Markdown-formatted report for user display.

✅ OUTPUT FORMAT (JSON)

{
  "query": "nvidia stocks news",
  "factcheck_summary": {
    "overall_assessment": "Concise overview of the factual consistency of headlines.",
    "contradictions": [
      {
        "claim": "string (the headline text or main claim)",
        "source": "string (e.g., The Guardian, Reuters)",
        "issue": "string (why it's wrong, biased, or inconsistent)",
        "severity": "Low|Medium|High",
        "explanation": "brief factual clarification"
      }
    ],
    "supporting_evidence": ["list of verified or consistent facts"],
    "context": "short background explanation",
    "conclusion": "final one-line verdict"
  },
  "formatted_markdown": "clean markdown representation for display"
}

🧱 MARKDOWN OUTPUT RULES

The Markdown should follow this exact, minimal, and beautiful structure:

## Overall Assessment

One or two sentences summarizing how consistent or accurate the headlines are.

## Contradictions or False Claims

**🔹 Claim:** "Exact headline or claim"  
**🔹 Source:** Publisher(s)  
**🔹 Issue:** Short description of the inaccuracy or inconsistency  
**🔹 Severity:** 🟢 Low | 🟠 Medium | 🔴 High  
**🔹 Explanation:** A short neutral clarification (one or two sentences).

## Supporting Evidence

✅ Fact 1 (verified data)  
🧾 Fact 2 (credible citation)  
📰 Fact 3 (consistent source)

## Context & Sources

Provide short factual background about the topic in 1–2 sentences.

## Conclusion

Final, concise statement summarizing factual accuracy or bias of the news cluster.

🧩 STYLE RULES

- Always bold the field names (Claim, Source, etc.)
- Always wrap the claim/headline in double quotes
- Use emojis for readability:
  - 🟢 Low severity
  - 🟠 Medium severity
  - 🔴 High severity
- Never start the report with "Fact Check Report:" — begin directly with "## Overall Assessment".
- Keep formatting clean with one blank line between sections.
- Be objective, factual, and concise — no redundant introductions.""",
            generation_config={
                "response_mime_type": "application/json"
            }
        )
    
    def analyze(self, headlines: List[str]) -> Dict[str, Any]:
        """
        Analyze headlines for contradictions and controversial claims.
        
        Args:
            headlines: List of headline strings
            
        Returns:
            Dictionary containing fact-check analysis with JSON summary and formatted markdown
        """
        try:
            # Create the prompt
            prompt = f"""Analyze these headlines for factual accuracy, contradictions, and misleading claims:

{chr(10).join(f"{i+1}. {h}" for i, h in enumerate(headlines))}

CRITICAL INSTRUCTION: You MUST respond with ONLY a valid JSON object. NO additional text before or after.

Required JSON structure:
{{
  "factcheck_summary": {{
    "overall_assessment": "one sentence summary",
    "contradictions": [
      {{
        "claim": "exact headline text",
        "source": "headline number or source",
        "issue": "what's wrong or inconsistent",
        "severity": "Low|Medium|High",
        "explanation": "brief clarification"
      }}
    ],
    "supporting_evidence": ["verified fact 1", "verified fact 2"],
    "context": "brief background",
    "conclusion": "final verdict"
  }},
  "formatted_markdown": "## Overall Assessment\\n\\n[Your formatted analysis with emojis as specified]\\n\\n## Contradictions or False Claims\\n\\n..."
}}

Remember: 
- Use 🔹 for claim markers
- Use 🟢🟠🔴 for severity indicators
- Use ✅🧾📰 for evidence markers
- Follow exact heading structure: ## Overall Assessment, ## Contradictions or False Claims, ## Supporting Evidence, ## Context & Sources, ## Conclusion"""

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
