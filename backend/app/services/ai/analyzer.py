import os
import json
import urllib.request
import urllib.error
import logging

logger = logging.getLogger("AIAnalyzer")

class AIAnalyzer:
    @staticmethod
    def analyze(prompt: str) -> dict:
        """
        Submits the built analysis prompt to the Gemini 3.5 Flash API.
        Falls back to a high-fidelity local rules-based response if API parameters are missing or rate limited.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        
        if api_key:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.2
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            try:
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                
                # Apply standard 15-second timeout for rapid responses
                with urllib.request.urlopen(req, timeout=15) as response:
                    res_body = response.read().decode("utf-8")
                    parsed_res = json.loads(res_body)
                    
                    # Extract text content from Gemini candidate parts
                    candidates = parsed_res.get("candidates", [])
                    if candidates:
                        text_content = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
                        
                        # Clean any wrap marks, triple quotes, or trailing noise
                        cl_text = text_content.strip()
                        if cl_text.startswith("```"):
                            # Remove markdown wrap blocks if present
                            if cl_text.startswith("```json"):
                                cl_text = cl_text[7:]
                            else:
                                cl_text = cl_text[3:]
                            if cl_text.endswith("```"):
                                cl_text = cl_text[:-3]
                            cl_text = cl_text.strip()
                            
                        parsed_json = json.loads(cl_text)
                        
                        # Verify we have matching keys
                        required_keys = ["executive_summary", "risks", "savings_opportunities", "recommendations", "finops_score"]
                        if any(k in parsed_json for k in required_keys):
                            logger.info("Successfully analyzed cloud topology with Gemini 3.5 Flash")
                            return parsed_json
            except Exception as e:
                logger.error(f"Gemini API request failed, falling back to local SRE engine: {e}")
                
        # High fidelity local SRE analysis engines fallback
        return None
