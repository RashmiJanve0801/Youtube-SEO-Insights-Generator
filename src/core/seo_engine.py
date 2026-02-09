import os
import json
from openai import OpenAI
import google.genai as genai 
from google.genai import types

from src.common.logger import get_logger
from src.common.custom_exception import CustomException

class SEOEngine:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.info("SEOEngine initialized successfully... ")

        if "GOOGLE_API_KEY" not in os.environ or not os.environ["GOOGLE_API_KEY"] :
            raise CustomException("Google API Key not found")
        
        try:
            self.client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
            self.logger.info("OpenAI Client connected")
        
        except Exception as e:
            self.logger.error("Failed to connect to Google Client")
            raise CustomException("Failed to connect to Google Client", e)
        
    def _build_prompt(self, metadata):
        try:
            title = metadata["title"]
            duration = metadata["duration"]
            platform = metadata["platform"]

            minutes = duration // 60

            num_timestamps = min(15, max(5, int(minutes/2)))

            prompt="""
            You MUST respond with VALID JSON ONLY. No extra text.

            The video:
            Title: "{title}"
            Platform: {platform}
            Duration: {duration} seconds

            Return JSON EXACTLY in this format:

            {{
            "tags": ["tag1", ..., "tag35"],
            "audience": "Short paragraph describing the target audience...",
            "timestamps": [
                {{"time": "00:00", "description": "Intro"}},
                ...
            ],
            "flaws": [
                {{
                "issue": "Problem or flaw identified",
                "why_it_hurts": "Why this flaw reduces rank or performance",
                "fix": "Clear actionable improvement"
                }},
                ...
            ]
            }}

            Rules:
            - EXACTLY **35** SEO tags.
            - Generate **{num_timestamps} timestamps**.
            - Generate **2–3 flaws** in the 'flaws' array.
            - Everything MUST be in English.
            """
            return prompt
        except Exception as e:
            self.logger.error("Error while building prompt")
            raise CustomException("Error while building prompt")
        
    def _parse_json(self, raw_output):
        try:
            return json.loads(raw_output)
        except Exception as e:
            try:
                start = raw_output.find("{")
                end = raw_output.rfind("}")+1
                return json.loads(raw_output[start:end])
            except Exception as e:
                raise CustomException("Failed to parse JSON")
            
    def _validate_output(self, data):
        required_keys = ["tags", "audience", "timestamps", "flaws"]
        for key in required_keys:
            if key not in data:
                self.logger.info(f"AI output missing for the {key}")
                raise CustomException(f"AI output missing for the {key}")
            
    def generate(self, video_metadata:dict):
        try:
            self.logger.info("Starting the SEO Insights Generator... ")

            prompt = self._build_prompt(video_metadata)

            response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json",
                system_instruction=[
                    "Return ONLY valid JSON. No extra text."
                ],
             ),
            )
            raw = response.candidates[0].content.parts[0].text.strip()

            self.logger.info("Raw Output Generated")

            data = self._parse_json(raw)

            self._validate_output(data)

            return data
        
        except Exception as e:
            self.logger.error(f"Unexpected Error at SEO Insights Generation : {str(e)}")
            raise CustomException("Unexpected Error at SEO Insights Generation",e)
