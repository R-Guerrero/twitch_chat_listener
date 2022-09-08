import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
from transformers import pipeline

MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Instantiate/load the Hugging Face RoBERTa pretrained NLP model.
pt_model = AutoModelForSequenceClassification.from_pretrained(MODEL)

# Load the default configuration for the RoBERTa pretrained NLP model.
pt_config = AutoConfig.from_pretrained(MODEL)

# Load the RoBERTa pretrained NLP model tokenizer.
pt_tokenizer = AutoTokenizer.from_pretrained(MODEL)

labels = ["negative", "neutral", "positive"]


def get_sentiment_scores_pt(input_str: str) -> dict:
    """
    This function assigns the most likely sentiment label to the input string.

    Parameters:
    ---------------
        input_str:
            The string/message whose sentiment wants to be labeled.

    Returns:
    ---------------
        A dictionary containing the most likely sentiment and the score for each label.
    """

    # Encode the input string.
    encoded_inputs = pt_tokenizer.encode(input_str, return_tensors="pt")

    # The output from the model is a OHE list of scores and the position
    # with the highest score represents the most likely sentiment.
    output = pt_model(encoded_inputs)

    scores = output.logits.tolist()[0]

    return {
        "scores": np.round(scores, 4).tolist(),
        "sentiment": labels[np.argmax(scores)],
    }


pt_pipeline = pipeline(
    task="sentiment-analysis",
    model=pt_model,
    config=pt_config,
    tokenizer=pt_tokenizer,
    framework="pt",
    top_k=1,
    device=-1,
)


def get_sentiment_probability_pt(input_str: str) -> dict:
    """
    This function assigns the most likely sentiment label to the input string.

    Parameters:
    ---------------
        input_str:
            The string/message whose sentiment wants to be labeled.

    Returns:
    ---------------
        A dictionary containing the most likely sentiment and its probability.
    """

    output = pt_pipeline(input_str)[0][0]

    return {
        "probability": round(output["score"], 4),
        "sentiment": output["label"].lower(),
    }
