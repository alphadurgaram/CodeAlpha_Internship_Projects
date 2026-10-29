
const sourceText = document.getElementById("sourceText");
const sourceLanguage = document.getElementById("sourceLanguage");
const targetLanguage = document.getElementById("targetLanguage");
const translatedText = document.getElementById("translatedText");
const translateButton = document.getElementById("translateButton");
const swapButton = document.getElementById("swapButton");
const clearButton = document.getElementById("clearButton");
const copyButton = document.getElementById("copyButton");
const speakButton = document.getElementById("speakButton");
const characterCount = document.getElementById("characterCount");
const translationStatus = document.getElementById("translationStatus");
const errorMessage = document.getElementById("errorMessage");

const placeholder = "Your translation will appear here.";
let hasTranslation = false;

// ================================
// Translation input
// ================================

sourceText.addEventListener("input", () => {
    characterCount.textContent = `${sourceText.value.length} / 5000`;
    errorMessage.textContent = "";
});

clearButton.addEventListener("click", () => {
    sourceText.value = "";
    translatedText.textContent = placeholder;
    characterCount.textContent = "0 / 5000";
    translationStatus.textContent = "Ready to translate";
    errorMessage.textContent = "";
    hasTranslation = false;

    window.speechSynthesis?.cancel();
    sourceText.focus();
});

// ================================
// Swap languages
// ================================

swapButton.addEventListener("click", () => {
    const oldSource = sourceLanguage.value;
    sourceLanguage.value = targetLanguage.value;
    targetLanguage.value = oldSource;

    if (hasTranslation) {
        const oldInput = sourceText.value;
        sourceText.value = translatedText.textContent;
        translatedText.textContent = oldInput || placeholder;
        hasTranslation = Boolean(oldInput);
    }

    characterCount.textContent = `${sourceText.value.length} / 5000`;
    errorMessage.textContent = "";
    translationStatus.textContent = "Languages swapped";
});

// ================================
// Copy current translation
// ================================

copyButton.addEventListener("click", async () => {
    if (!hasTranslation) {
        errorMessage.textContent = "Translate some text first.";
        return;
    }

    try {
        await navigator.clipboard.writeText(translatedText.textContent);
        translationStatus.textContent = "Copied to clipboard!";
    } catch {
        errorMessage.textContent =
            "Clipboard access failed. Copy the text manually.";
    }
});

// ================================
// Speak translation
// ================================

speakButton.addEventListener("click", () => {
    if (!hasTranslation) {
        errorMessage.textContent = "Translate some text first.";
        return;
    }

    if (!("speechSynthesis" in window)) {
        errorMessage.textContent =
            "Speech is not supported in this browser.";
        return;
    }

    const voices = {
        en: "en-US",
        hi: "hi-IN",
        es: "es-ES",
        fr: "fr-FR",
        de: "de-DE",
        ja: "ja-JP",
        zh: "zh-CN",
        ar: "ar-SA",
        bn: "bn-IN",
        ta: "ta-IN",
        te: "te-IN",
        mr: "mr-IN",
        gu: "gu-IN",
        pa: "pa-IN",
        it: "it-IT",
        pt: "pt-PT",
        ru: "ru-RU",
        ko: "ko-KR"
    };

    window.speechSynthesis.cancel();

    const speech = new SpeechSynthesisUtterance(
        translatedText.textContent
    );

    speech.lang = voices[targetLanguage.value] || "en-US";
    window.speechSynthesis.speak(speech);
});

// ================================
// Translation History
// ================================

const HISTORY_KEY = "lingua_ai_translation_history";

function getTranslationHistory() {
    try {
        const saved = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
        return Array.isArray(saved) ? saved : [];
    } catch {
        return [];
    }
}

function saveTranslationHistory(item) {
    const history = getTranslationHistory();

    history.unshift({
        ...item,
        id: Date.now()
    });

    try {
        localStorage.setItem(
            HISTORY_KEY,
            JSON.stringify(history.slice(0, 20))
        );

        renderTranslationHistory();
    } catch {
        errorMessage.textContent =
            "Translation succeeded, but browser history could not be saved.";
    }
}

function renderTranslationHistory() {
    const list = document.getElementById("historyList");
    if (!list) return;

    const history = getTranslationHistory();
    list.replaceChildren();

    if (history.length === 0) {
        const empty = document.createElement("p");
        empty.className = "history-empty";
        empty.textContent = "Your translations will appear here.";
        list.appendChild(empty);
        return;
    }

    history.forEach((item) => {
        const card = document.createElement("article");
        card.className = "history-card";

        const languages = document.createElement("p");
        languages.className = "history-languages";
        languages.textContent = `${item.sourceName} → ${item.targetName}`;

        const original = document.createElement("p");
        original.textContent = item.original;

        const translated = document.createElement("p");
        translated.textContent = item.translated;

        const copyHistoryButton = document.createElement("button");
        copyHistoryButton.type = "button";
        copyHistoryButton.textContent = "Copy Translation";

        copyHistoryButton.addEventListener("click", async () => {
            try {
                await navigator.clipboard.writeText(item.translated);
                copyHistoryButton.textContent = "Copied!";
                setTimeout(() => {
                    copyHistoryButton.textContent = "Copy Translation";
                }, 1500);
            } catch {
                copyHistoryButton.textContent = "Copy failed";
            }
        });

        card.append(languages, original, translated, copyHistoryButton);
        list.appendChild(card);
    });
}

document.getElementById("clearHistoryBtn")?.addEventListener("click", () => {
    localStorage.removeItem(HISTORY_KEY);
    renderTranslationHistory();
});

renderTranslationHistory();

// ================================
// Translate button
// ================================

translateButton.addEventListener("click", async () => {
    const text = sourceText.value.trim();
    const selectedSource = sourceLanguage.value;
    const selectedTarget = targetLanguage.value;

    errorMessage.textContent = "";

    if (!text) {
        errorMessage.textContent = "Please enter text to translate.";
        return;
    }

    if (selectedSource !== "auto" && selectedSource === selectedTarget) {
        errorMessage.textContent = "Choose two different languages.";
        return;
    }

    translateButton.disabled = true;
    translateButton.textContent = "Translating...";
    translationStatus.textContent = "Processing your text...";

    try {
        const response = await fetch("/translate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text,
                source: selectedSource,
                target: selectedTarget
            })
        });

        
const responseText = await response.text();

let data;

try {
    data = JSON.parse(responseText);
} catch (error) {
    console.error("Server returned HTML or invalid JSON:", responseText);
    throw new Error(
        "Server returned an HTML page instead of JSON. Check the Flask Terminal."
    );
}

if (!response.ok) {
    throw new Error(data.error || "Translation failed.");
}


        if (!response.ok) {
            throw new Error(data.error || "Translation failed.");
        }

        translatedText.textContent = data.translatedText;
        translationStatus.textContent = "Translation complete";
        hasTranslation = true;

        // Save successful translations to history
        const sourceOption = Array.from(sourceLanguage.options).find(
            option => option.value === selectedSource
        );

        const targetOption = Array.from(targetLanguage.options).find(
            option => option.value === selectedTarget
        );

        let sourceName = sourceOption?.text || selectedSource;

        // When Auto Detect is selected, use the backend-detected code
        if (selectedSource === "auto" && data.source) {
            const detectedOption = Array.from(sourceLanguage.options).find(
                option => option.value === data.source
            );

            sourceName = detectedOption?.text || data.source;
        }

        saveTranslationHistory({
            original: text,
            translated: data.translatedText,
            sourceName,
            targetName: targetOption?.text || selectedTarget
        });

    } catch (error) {
        errorMessage.textContent =
            error.message || "Could not connect to the translation service.";

        translationStatus.textContent = "Translation failed";
        hasTranslation = false;

    } finally {
        translateButton.disabled = false;
        translateButton.textContent = "Translate Text →";
    }
});
