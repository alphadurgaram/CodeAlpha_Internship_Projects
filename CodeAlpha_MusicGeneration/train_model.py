
from pathlib import Path
import numpy as np
import pretty_midi
import pickle

PROJECT_DIR = Path(__file__).resolve().parent
DATASET_DIR = PROJECT_DIR / "dataset"
MODEL_DIR = PROJECT_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

SEQUENCE_LENGTH = 32
MAX_FILES = 100

def extract_notes(midi_path):
    try:
        midi = pretty_midi.PrettyMIDI(str(midi_path))
        notes = []

        for instrument in midi.instruments:
            if instrument.is_drum:
                continue

            for note in instrument.notes:
                notes.append((note.start, note.pitch))

        notes.sort(key=lambda item: item[0])
        return [pitch for _, pitch in notes]
    except Exception as error:
        print(f"Skipped {midi_path.name}: {error}")
        return []

def main():
    midi_files = list(DATASET_DIR.rglob("*.mid"))
    midi_files += list(DATASET_DIR.rglob("*.midi"))
    midi_files = midi_files[:MAX_FILES]

    if not midi_files:
        print("No MIDI files found in the dataset folder.")
        print(f"Expected folder: {DATASET_DIR}")
        return

    print(f"Reading {len(midi_files)} MIDI files...")
    all_notes = []

    for index, midi_file in enumerate(midi_files, start=1):
        notes = extract_notes(midi_file)
        all_notes.extend(notes)

        if index % 10 == 0:
            print(f"Processed {index}/{len(midi_files)} files")

    if len(all_notes) <= SEQUENCE_LENGTH:
        print("Not enough notes found. Check your MIDI dataset.")
        return

    # Convert pitches into compact integer tokens.
    unique_pitches = sorted(set(all_notes))
    pitch_to_token = {pitch: i for i, pitch in enumerate(unique_pitches)}
    encoded_notes = [pitch_to_token[pitch] for pitch in all_notes]

    X, y = [], []
    for i in range(len(encoded_notes) - SEQUENCE_LENGTH):
        X.append(encoded_notes[i:i + SEQUENCE_LENGTH])
        y.append(encoded_notes[i + SEQUENCE_LENGTH])

    X = np.asarray(X, dtype=np.int32)
    y = np.asarray(y, dtype=np.int32)

    output_path = MODEL_DIR / "training_data.pkl"

    with open(output_path, "wb") as file:
        pickle.dump({
            "X": X,
            "y": y,
            "pitch_to_token": pitch_to_token,
            "sequence_length": SEQUENCE_LENGTH
        }, file)

    print("\nDataset preparation complete!")
    print(f"Files read: {len(midi_files)}")
    print(f"Notes extracted: {len(all_notes)}")
    print(f"Unique pitches: {len(unique_pitches)}")
    print(f"Training sequences: {len(X)}")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    main()
