
from flask import Flask, render_template, request, jsonify, send_from_directory
from music_generator import generate_music
from pathlib import Path
import random

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "generated_music"
OUTPUT_DIR.mkdir(exist_ok=True)

STYLE_BPM = {
    "Energetic": (125, 150),
    "Calm": (60, 85),
    "Happy": (100, 125),
    "Dark": (65, 95),
}

ALLOWED_STYLES = list(STYLE_BPM.keys())


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    style = data.get("style", "Energetic")

    if style not in ALLOWED_STYLES:
        return jsonify({
            "error": "Please select a valid music style."
        }), 400

    bpm = random.randint(*STYLE_BPM[style])

    try:
        output_path = Path(
            generate_music(style=style, bars=8, bpm=bpm)
        ).resolve()

        # Only serve files created inside generated_music.
        if output_path.parent != OUTPUT_DIR.resolve():
            app.logger.error("Generated file path is outside output folder.")
            return jsonify({
                "error": "Invalid generated file path."
            }), 500

        return jsonify({
            "message": "Your AI melody has been generated!",
            "file": f"/generated_music/{output_path.name}",
            "style": style,
            "bpm": bpm
        })

    except Exception:
        app.logger.exception("Music generation failed")
        return jsonify({
            "error": "Music generation failed. Check the terminal."
        }), 500


@app.route("/generated_music/<path:filename>")
def download_music(filename):
    return send_from_directory(
        str(OUTPUT_DIR),
        filename,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)
