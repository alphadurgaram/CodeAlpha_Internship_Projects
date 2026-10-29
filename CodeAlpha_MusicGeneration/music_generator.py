
import random
import pickle
from pathlib import Path

import numpy as np
import pretty_midi
from tensorflow.keras.models import load_model

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "generated_music"

MODEL_FILE = MODEL_DIR / "music_lstm.keras"
CONFIG_FILE = MODEL_DIR / "music_config.pkl"
DATA_FILE = MODEL_DIR / "training_data.pkl"

OUTPUT_DIR.mkdir(exist_ok=True)

STYLE_SETTINGS = {
    "Energetic": {"bpm": (125, 150), "step": 0.5, "temperature": 0.9},
    "Calm":      {"bpm": (60, 85),   "step": 1.0, "temperature": 0.65},
    "Happy":     {"bpm": (100, 125), "step": 0.5, "temperature": 0.8},
    "Dark":      {"bpm": (65, 95),   "step": 1.0, "temperature": 0.75},
}

_model = None
_config = None
_seed_sequences = None


def load_music_model():
    global _model, _config, _seed_sequences

    if _model is None:
        if not MODEL_FILE.exists():
            raise FileNotFoundError(
                "Trained model missing. Run python train_lstm.py first."
            )

        if not CONFIG_FILE.exists() or not DATA_FILE.exists():
            raise FileNotFoundError(
                "Model configuration or training data is missing."
            )

        _model = load_model(MODEL_FILE)

        with open(CONFIG_FILE, "rb") as file:
            _config = pickle.load(file)

        with open(DATA_FILE, "rb") as file:
            training_data = pickle.load(file)

        _seed_sequences = training_data["X"]

    return _model, _config, _seed_sequences


def sample_next_token(probabilities, temperature):
    probabilities = np.asarray(probabilities, dtype=np.float64)
    probabilities = np.log(np.maximum(probabilities, 1e-9)) / temperature

    probabilities = np.exp(probabilities - np.max(probabilities))
    probabilities /= probabilities.sum()

    return int(np.random.choice(len(probabilities), p=probabilities))


def generate_music(style="Energetic", bars=8, bpm=None):
    if style not in STYLE_SETTINGS:
        style = "Energetic"

    settings = STYLE_SETTINGS[style]
    if bpm is None:
        bpm = random.randint(*settings["bpm"])

    model, config, seed_sequences = load_music_model()

    sequence_length = int(config["sequence_length"])
    pitch_to_token = config["pitch_to_token"]
    token_to_pitch = {
        int(token): int(pitch)
        for pitch, token in pitch_to_token.items()
    }

    if len(seed_sequences) == 0:
        raise ValueError("No seed sequences found in training data.")

    seed = random.choice(seed_sequences).tolist()
    generated_pitches = []

    # Generate 8 bars of notes, one note per selected rhythmic step.
    total_steps = max(1, int(bars * 4 / settings["step"]))
    current_sequence = list(seed[-sequence_length:])

    for _ in range(total_steps):
        model_input = np.asarray(
            [current_sequence], dtype=np.int32
        )

        probabilities = model.predict(model_input, verbose=0)[0]

        next_token = sample_next_token(
            probabilities, settings["temperature"]
        )

        if next_token not in token_to_pitch:
            next_token = random.choice(list(token_to_pitch.keys()))

        generated_pitches.append(token_to_pitch[next_token])
        current_sequence = current_sequence[1:] + [next_token]

    midi = pretty_midi.PrettyMIDI(
        initial_tempo=int(bpm)
    )
    piano = pretty_midi.Instrument(program=0)

    beat_duration = 60.0 / bpm
    note_duration = settings["step"] * beat_duration

    for index, pitch in enumerate(generated_pitches):
        start = index * note_duration

        piano.notes.append(
            pretty_midi.Note(
                velocity=random.randint(75, 105),
                pitch=int(pitch),
                start=start,
                end=start + note_duration * 0.9
            )
        )

    midi.instruments.append(piano)

    filename = (
        f"{style.lower()}_lstm_{bpm}_"
        f"{random.randrange(100000, 999999)}.mid"
    )

    output_path = OUTPUT_DIR / filename
    midi.write(str(output_path))

    return str(output_path)


if __name__ == "__main__":
    result = generate_music()
    print(f"AI music generated successfully: {result}")