from google import genai
import json
import re,os
import pandas as pd

class BrandJournalistAnalyzer:
    def __init__(self, api_key, model_id="gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_id
        self.results_data = []
        self.max_results = 15
        self.topic = "iPhone 17"

    def search_prompt(self):
        with open('prompt/prompt_search.txt', 'r', encoding='utf-8') as file:
            search_prompt = file.read() % {'max_results': self.max_results}
        return search_prompt
    
    def storytelling_prompt(self, data_result):
        with open('prompt/prompt_storytelling.txt', 'r', encoding='utf-8') as file:
            storytelling_prompt = file.read() % {
                'data_result': json.dumps(data_result, ensure_ascii=False),
                'topic': self.topic
            }
        return storytelling_prompt

    def _clean_json_response(self, response_text: str) -> str:
        """Elimina fences y deja solo el JSON."""
        if not isinstance(response_text, str):
            return response_text
        # si viene con ```json ... ```
        m = re.search(r"```(?:json)?\s*([\s\S]*?)```", response_text)
        if m:
            response_text = m.group(1)
        # recorta espacios, quita líneas vacías duplicadas
        response_text = re.sub(r'\n\s*\n+', '\n', response_text).strip()
        return response_text

    def _parse_json_strict(self, text: str):
        """Intenta json.loads con varias limpiezas suaves."""
        try:
            return json.loads(text)
        except Exception:
            cleaned = self._clean_json_response(text)
            return json.loads(cleaned)  # si falla aquí, deja que suba la excepción

    def _load_local_news(self, path="data/news_about_iphone.txt"):
        """Carga artículos desde un JSON local (lista de dicts)."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Local news file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = [data]
        self.results_data = data
        return data
    
    def _load_or_search(self, path="data/news_about_iphone.txt", force_refresh=False, create_dataframe=True):
        """
        Si existe el archivo local y no se fuerza refresh: lo carga.
        Si no, ejecuta search_news y guarda el resultado en el archivo.
        """
        if os.path.exists(path) and not force_refresh:
            print(f"📂 Loading cached news from {path}")
            return self._load_local_news(path)
        print("🌐 No cache found or refresh forced, searching online...")
        data = self.search_news(create_dataframe=create_dataframe)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return data

    def search_news(self, max_retries=1,create_dataframe=True):
        """Find the latest news about a specific topic using Google Search tool."""
        prompt = self.search_prompt()
        # Execute with retries
        for attempt in range(max_retries):
            try:
                print(f"🔍 Find news (retries {attempt + 1}/{max_retries})...")
                # Gemini with Google Search tool
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config={"tools": [{"google_search": {}}]}
                )
                # Extract and clean JSON from response
                txt = response.candidates[0].content.parts[0].text
                clean_text = self._clean_json_response(txt)
            except Exception as e:
                print(f"❌ Error in retries {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise e
        if create_dataframe:
            results_data = pd.DataFrame(self.results_data)
            results_data.to_parquet("data/news_about_iphone.parquet")
        return json.loads(clean_text)

    def get_storytelling(self, data_result):
        prompt = self.storytelling_prompt(data_result)
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config={
                "temperature": 0.4,
                "response_mime_type": "application/json"  # <-- fuerza JSON
            }
        )
        txt = response.candidates[0].content.parts[0].text
        # parseo robusto
        storytelling_json = self._parse_json_strict(txt)
        return storytelling_json  # <- dict listo para pasar al PDF
        
    def get_conclusion(self, data_result):
        prompt = (
            "You are an expert data analyst. "
            "You have the following data about news articles in JSON format:\n"
            f"{json.dumps(data_result, ensure_ascii=False)}\n\n"
            "Provide a concise summary of the key insights and trends observed in the data. "
            "Use only the provided data. Return plain text, no code fences."
        )
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config={
                "temperature": 0.4
            }
        )
        return response.candidates[0].content.parts[0].text.strip()
