\# CodeAlpha Internship Projects



A collection of three AI and machine learning projects developed as part of the CodeAlpha Internship.



\## Projects



\### 1. Language Translation Tool

A web-based language translation application built with Flask and the Gemini API.



\*\*Technologies:\*\* Python, Flask, Gemini API, HTML, CSS, JavaScript



\*\*Features\*\*

\- Translate text using an AI-powered API.

\- Simple web-based interface.

\- API credentials managed through environment variables.



\*\*Run locally\*\*

1\. Open the project folder:

&#x20;  `CodeAlpha\_LanguageTranslationTool`

2\. Install dependencies:

&#x20;  `pip install -r requirements.txt`

3\. Create a `.env` file and configure your `GEMINI\_API\_KEY`.

4\. Start the application:

&#x20;  `python app.py`

5\. Open `http://127.0.0.1:5000` in your browser.



Never upload your real API key to GitHub.



\### 2. FAQ Chatbot

A web-based FAQ chatbot that uses text preprocessing and TF-IDF similarity to find relevant answers.



\*\*Technologies:\*\* Python, Flask, NLTK, scikit-learn



\*\*Features\*\*

\- Processes user questions.

\- Uses TF-IDF and cosine similarity to match questions with FAQ entries.

\- Returns relevant answers through a web interface.



\*\*Run locally\*\*

1\. Open the project folder:

&#x20;  `CodeAlpha\_FAQChatbot`

2\. Install dependencies:

&#x20;  `pip install -r requirements.txt`

3\. Start the application:

&#x20;  `python app.py`

4\. Open `http://127.0.0.1:5000` in your browser.



\### 3. AI Music Generation

A web-based music generation project that uses an LSTM model to generate note sequences and export melodies as MIDI files.



\*\*Technologies:\*\* Python, Flask, TensorFlow, NumPy, pretty\_midi, music21, mido



\*\*Features\*\*

\- Generates melodies using a trained LSTM model.

\- Offers different music styles.

\- Exports generated melodies as MIDI files.

\- Includes scripts for preparing training data and training the model.



\*\*Run locally\*\*

1\. Open the project folder:

&#x20;  `CodeAlpha\_MusicGeneration`

2\. Install dependencies:

&#x20;  `pip install -r requirements.txt`

3\. Ensure the trained model, configuration and training data are available in the `models` folder.

4\. Start the application:

&#x20;  `python app.py`

5\. Open `http://127.0.0.1:5000` in your browser.



\*\*Important:\*\* The large `models/training\_data.pkl` file and the dataset are not included in this repository. The music generator requires compatible training data. Refer to `train\_model.py` and `train\_lstm.py` to prepare and train the model before running it on another computer.



\## Repository Structure



```text

CodeAlpha\_Internship\_Projects/

├── CodeAlpha\_LanguageTranslationTool/

├── CodeAlpha\_FAQChatbot/

├── CodeAlpha\_MusicGeneration/

└── README.md

```



\## Setup Notes

\- Python must be installed.

\- Install each project's dependencies from its own `requirements.txt`.

\- Configure API credentials locally when required.

\- Do not commit `.env` files, API keys, virtual environments or other secrets.



\## Internship

These projects were developed for learning and demonstrating practical skills in Python, web development, natural language processing and machine learning as part of the CodeAlpha Internship.

