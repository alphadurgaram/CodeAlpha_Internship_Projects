
from pathlib import Path
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "models" / "training_data.pkl"
MODEL_FILE = BASE_DIR / "models" / "music_lstm.keras"
VOCAB_FILE = BASE_DIR / "models" / "music_config.pkl"

def main():
    if not DATA_FILE.exists():
        print("Training data not found. Run train_model.py first.")
        return

    with open(DATA_FILE, "rb") as f:
        data = pickle.load(f)

    X = data["X"]
    y = data["y"]
    pitch_to_token = data["pitch_to_token"]
    sequence_length = data["sequence_length"]
    vocab_size = len(pitch_to_token)

    if len(X) < 10 or vocab_size < 2:
        print("Not enough training data to train the model.")
        return

    # Limit memory usage on an 8 GB RAM laptop.
    rng = np.random.default_rng(42)
    if len(X) > 20000:
        indices = rng.choice(len(X), size=20000, replace=False)
        X, y = X[indices], y[indices]

    print(f"Training sequences: {len(X)}")
    print(f"Unique pitches: {vocab_size}")

    model = Sequential([
        Embedding(vocab_size, 64, input_length=sequence_length),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(64),
        Dense(64, activation="relu"),
        Dense(vocab_size, activation="softmax")
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    model.summary()

    early_stop = EarlyStopping(
        monitor="loss",
        patience=2,
        restore_best_weights=True
    )

    model.fit(
        X, y,
        epochs=8,
        batch_size=32,
        callbacks=[early_stop],
        verbose=1
    )

    model.save(MODEL_FILE)

    with open(VOCAB_FILE, "wb") as f:
        pickle.dump({
            "pitch_to_token": pitch_to_token,
            "sequence_length": sequence_length
        }, f)

    print("\nLSTM training complete!")
    print(f"Model saved at: {MODEL_FILE}")
    print(f"Configuration saved at: {VOCAB_FILE}")

if __name__ == "__main__":
    main()
