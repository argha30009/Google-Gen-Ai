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
            system_instruction="""You are an Expert Fact Check Analysis Agent that reviews news headlines
for factual accuracy, contradictions, misleading claims, and provides clear TRUE/FALSE verdicts.

Your analysis must be visually appealing, well-structured, and easy to scan.

✅ OUTPUT FORMAT (JSON)

{
  "factcheck_summary": {
    "overall_assessment": "One sentence summary of factual consistency",
    "verdict": "MOSTLY_TRUE|MIXED|MOSTLY_FALSE|UNVERIFIABLE",
    "contradictions": [
      {
        "claim": "Exact headline or specific claim",
        "source": "Source name from headline",
        "verdict": "TRUE|FALSE|MISLEADING|UNVERIFIABLE",
        "issue": "What's problematic about this claim",
        "severity": "Low|Medium|High",
        "explanation": "Clear factual clarification (1-2 sentences)"
      }
    ],
    "supporting_evidence": ["✓ Verified fact 1", "✓ Verified fact 2"],
    "context": "Brief background (2-3 sentences)",
    "conclusion": "Final verdict statement"
  },
  "formatted_markdown": "Beautiful markdown with emojis and structure"
}

🎨 BEAUTIFUL MARKDOWN FORMAT

Create a visually stunning, easy-to-scan report with this EXACT structure:

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

CRITICAL: Respond with ONLY valid JSON. NO text before or after.

Required JSON structure:
{{
  "factcheck_summary": {{
    "overall_assessment": "one clear sentence",
    "verdict": "MOSTLY_TRUE|MIXED|MOSTLY_FALSE|UNVERIFIABLE",
    "contradictions": [
      {{
        "claim": "exact headline",
        "source": "publisher name",
        "verdict": "TRUE|FALSE|MISLEADING|UNVERIFIABLE",
        "issue": "what's wrong",
        "severity": "Low|Medium|High",
        "explanation": "factual clarification"
      }}
    ],
    "supporting_evidence": ["• fact 1", "• fact 2"],
    "context": "2-3 sentence background",
    "conclusion": "authoritative verdict"
  }},
  "formatted_markdown": "---\\n\\n## 📊 Overall Verdict: [VERDICT]\\n\\n[assessment]\\n\\n---\\n\\n## 🔍 Fact Check Analysis\\n\\n### ✅ Claim #1: \\"[claim]\\"\\n\\n**📍 Source:** [source]\\n**⚖️ Verdict:** [✓ TRUE / ✗ FALSE / ⚠️ MISLEADING / ❓ UNVERIFIABLE]\\n**🎯 Severity:** [🟢 Low / 🟠 Medium / 🔴 High]\\n\\n**💡 Analysis:**\\n[explanation]\\n\\n---\\n\\n## ✓ Supporting Facts\\n\\n• [fact 1]\\n• [fact 2]\\n\\n---\\n\\n## 📚 Context\\n\\n[context]\\n\\n---\\n\\n## 🎯 Final Verdict\\n\\n[conclusion]\\n\\n---"
}}

CRITICAL FORMATTING:
- Always assign clear verdict: ✓ TRUE / ✗ FALSE / ⚠️ MISLEADING / ❓ UNVERIFIABLE
- Use visual separators (---) between all sections
- Include all emojis as specified: 📊 🔍 ✅ ⚖️ 🎯 📚 ✓
- Make analysis punchy and authoritative"""

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
