import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
from transformers import pipeline

MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Instantiate/load the Hugging Face RoBERTa pretrained NLP model.
tf_model = TFAutoModelForSequenceClassification.from_pretrained(MODEL)

# Load the default configuration for the RoBERTa pretrained NLP model.
tf_config = AutoConfig.from_pretrained(MODEL)

# Load the RoBERTa pretrained NLP model tokenizer.
tf_tokenizer = AutoTokenizer.from_pretrained(MODEL)

labels = ["negative", "neutral", "positive"]


def get_sentiment_scores_tf(input_str: str) -> dict:
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
    encoded_inputs = tf_tokenizer.encode(input_str, return_tensors="tf")

    # The output from the model is a OHE list of scores and the position
    # with the highest score represents the most likely sentiment.
    output = tf_model(encoded_inputs)

    scores = np.array(output.logits[0]).tolist()

    return {
        "scores": np.round(scores, 4).tolist(),
        "sentiment": labels[np.argmax(scores)],
    }


tf_pipeline = pipeline(
    task="sentiment-analysis",
    model=tf_model,
    config=tf_config,
    tokenizer=tf_tokenizer,
    framework="tf",
    top_k=1,
    device=-1,
)


def get_sentiment_probability_tf(input_str: str) -> dict:
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

    output = tf_pipeline(input_str)[0][0]

    return {
        "probability": round(output["score"], 4),
        "sentiment": output["label"].lower(),
    }
