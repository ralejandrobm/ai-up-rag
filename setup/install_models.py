import os
from sentence_transformers import SentenceTransformer


def install():
    """
    Download and cache the model in the specified folder
    """
    SENTENCE_TRANSFORMERS_HOME = os.environ.get(
        "SENTENCE_TRANSFORMERS_HOME", "/var/lib/ai-models"
    )
    HF_MODEL_NAME_OR_PATH = os.environ.get(
        "HF_MODEL_NAME_OR_PATH", "sentence-transformers/all-mpnet-base-v2"
    )

    SentenceTransformer(
        model_name_or_path=HF_MODEL_NAME_OR_PATH,
        cache_folder=SENTENCE_TRANSFORMERS_HOME,
    )


if __name__ == "__main__":
    install()

# python3 - "import os;from sentence_transformers import SentenceTransformer;SentenceTransformer(model_name_or_path='sentence-transformers/all-mpnet-base-v2',cache_folder='/var/lib/ai-models');"
