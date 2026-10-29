import re
import logging

from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import TreebankWordTokenizer

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Tokenizer for basic NLP preprocessing
tokenizer = TreebankWordTokenizer()


# FAQ questions and answers
FAQS = [
    {
        "question": "What is your name?",
        "answer": "I am FAQ Bot, your virtual assistant."
    },
    {
        "question": "What can you do?",
        "answer": "I can answer frequently asked questions."
    },
    {
        "question": "How can I contact support?",
        "answer": "You can contact our support team through the contact page."
    },
    {
        "question": "What are your working hours?",
        "answer": "Our working hours are Monday to Friday, 9 AM to 5 PM."
    },
    {
        "question": "How do I reset my password?",
        "answer": "Click on Forgot Password on the login page to reset your password."
    },
    {
        "question": "How do I create an account?",
        "answer": "Open the Sign Up page and complete the registration form."
    },
    {
        "question": "Is registration free?",
        "answer": "Yes, registration is free in this demo chatbot."
    },
    {
        "question": "How can I get help?",
        "answer": "Please type your question, and I will try to help you."
    },
    {
        "question": "Thank you",
        "answer": "You're welcome! Let me know if you have another question."
    },
    {
        "question": "Bye",
        "answer": "Goodbye! Have a great day."
    }
]


def preprocess_text(text):
    """Clean and tokenize text for FAQ matching."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    tokens = tokenizer.tokenize(text)
    return " ".join(tokens)


# Prepare FAQ question vectors
processed_questions = [
    preprocess_text(faq["question"])
    for faq in FAQS
]


vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    sublinear_tf=True
)

faq_vectors = vectorizer.fit_transform(processed_questions)


def get_answer(question):
    """Return the answer for the most similar FAQ question."""
    question = question.strip()

    if not question:
        return "Please type a question."

    processed_question = preprocess_text(question)
    if any(word in processed_question.split()
           for word in ["weather", "temperature", "forecast"]):
        return (
            "Sorry, I couldn't find a relevant FAQ answer. "
            "Please try asking about accounts, support, working hours, or registration."
        )
   
    try:
        question_vector = vectorizer.transform([processed_question])
        similarities = cosine_similarity(
            question_vector,
            faq_vectors
        )[0]

        best_index = similarities.argmax()
        best_score = float(similarities[best_index])

        # Avoid returning unrelated answers for weak matches
        if best_score < 0.30:
            return (
                "Sorry, I couldn't find a relevant FAQ answer. "
                "Please try asking in a different way."
            )

        return FAQS[best_index]["answer"]

    except Exception:
        app.logger.exception("FAQ matching failed")
        return "Sorry, I couldn't process your question right now."


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")

    if not isinstance(question, str):
        return jsonify({
            "answer": "Please enter a valid question."
        }), 400

    answer = get_answer(question)

    return jsonify({"answer": answer})


@app.route("/health")
def health():
    return jsonify({
        "status": "success",
        "message": "FAQ Chatbot is running",
        "matching": "TF-IDF + Cosine Similarity",
        "preprocessing": "NLTK TreebankWordTokenizer"
    })


if __name__ == "__main__":
    app.run(debug=True)