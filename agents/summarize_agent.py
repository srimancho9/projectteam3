import os, time
from openai import OpenAI
import pdfplumber
import PyPDF2

class SummarizeTool:
    def __init__(self, max_retries=2, verbose=True):
        self.max_retries = max_retries
        self.verbose = verbose

    def execute(self, text: str) -> str:
        return self._summarize(text)

    def execute_pdf(self, pdf_path: str) -> str:
        text = self._extract_pdf_text(pdf_path)
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF.")
        return self._summarize(text)

    def _extract_pdf_text(self, pdf_path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            if self.verbose:
                print("[SummarizeTool] Extracted text with pdfplumber")
        except Exception:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            if self.verbose:
                print("[SummarizeTool] Extracted text with PyPDF2")
        return text.strip()

    def _summarize(self, text: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set. Check your .env file.")

        client = OpenAI(api_key=api_key)
        models_to_try = ["gpt-4o-mini", "gpt-3.5-turbo"]

        system_prompt = (
            "You are a medical text summarizer. "
            "Summarize the given medical report into ONLY 5–6 lines. "
            "Be concise, professional, and focus on key clinical details."
        )

        last_error = None
        for model in models_to_try:
            for attempt in range(self.max_retries):
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": text},
                        ],
                    )
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    last_error = e
                    if self.verbose:
                        print(f"[SummarizeTool] Attempt {attempt+1} failed on {model}: {e}")
                    time.sleep(2)
        raise RuntimeError(f"Failed to summarize. Last error: {last_error}")
