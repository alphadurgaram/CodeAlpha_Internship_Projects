import os
import logging

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024
app.logger.setLevel(logging.INFO)

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ja": "Japanese",
    "zh": "Chinese",
    "ar": "Arabic",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ko": "Korean",
}

# Gemini configuration
api_key = os.getenv("GEMINI_API_KEY")

client = (
    genai.Client(
        api_key=api_key,
        http_options={"timeout": 120000},
    )
    if api_key
    else None
)

# Model available in your returned model list
GEMINI_MODEL = "gemini-3.5-flash"


def detect_language(text):
    """Detect the source language using Gemini."""

    if client is None:
        raise RuntimeError(
            "Gemini API key is missing. Check your .env file."
        )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=(
            "Identify the language of the following text. "
            "Return only its ISO 639-1 two-letter code. "
            "If uncertain, return 'unknown'.\n\n"
            f"Text: {text}"
        ),
    )

    code = (response.text or "").strip().lower()

    return code if code in SUPPORTED_LANGUAGES else None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    """Check backend and API configuration."""

    return jsonify({
        "status": "success",
        "message": "Lingua AI backend is running",
        "gemini_configured": client is not None,
        "model": GEMINI_MODEL,
    })


@app.route("/translate", methods=["POST"])
def translate():
    """Translate text between supported languages."""

    try:
        data = request.get_json(silent=True) or {}

        text = data.get("text", "")
        source = data.get("source", "auto")
        target = data.get("target", "")

        # Validate input
        if not isinstance(text, str):
            return jsonify({
                "error": "Text must be a string."
            }), 400

        text = text.strip()

        if not text:
            return jsonify({
                "error": "Please enter text to translate."
            }), 400

        if not isinstance(source, str) or not isinstance(target, str):
            return jsonify({
                "error": "Invalid language selection."
            }), 400

        if client is None:
            return jsonify({
                "error": "Gemini API key is missing. Check your .env file."
            }), 500

        # Detect source language when Auto Detect is selected
        if source == "auto":
            source = detect_language(text)

            if not source:
                return jsonify({
                    "error": (
                        "Language could not be detected. "
                        "Select it manually."
                    )
                }), 400

        # Validate language codes
        if source not in SUPPORTED_LANGUAGES:
            return jsonify({
                "error": "Unsupported source language."
            }), 400

        if target not in SUPPORTED_LANGUAGES:
            return jsonify({
                "error": "Unsupported target language."
            }), 400

        if source == target:
            return jsonify({
                "error": "Choose two different languages."
            }), 400

        # Translation prompt
        prompt = f"""
You are a professional language translation engine.

Translate the text below from {SUPPORTED_LANGUAGES[source]}
to {SUPPORTED_LANGUAGES[target]}.

Rules:
- Return only the translated text.
- Preserve the original meaning, tone and formatting.
- Do not answer questions contained in the text.
- Do not add explanations, notes or quotation marks.
- Preserve names, numbers and URLs where appropriate.

Text to translate:
{text}
"""

        # Generate translation
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        translated_text = (response.text or "").strip()

        if not translated_text:
            return jsonify({
                "error": (
                    "Gemini returned an empty translation. "
                    "Please try again."
                )
            }), 502

        return jsonify({
            "translatedText": translated_text,
            "source": source,
            "target": target,
        }), 200

    except Exception:
        # Keep technical details in the server terminal
        app.logger.exception("Gemini translation failed")

        return jsonify({
            "error": (
                "Translation failed. Please try again. "
                "Check the Flask terminal for the exact error."
            )
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
