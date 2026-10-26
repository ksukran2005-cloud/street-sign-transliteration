import os

from functools import lru_cache


os.environ.setdefault(
    "TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD",
    "1"
)


from ai4bharat.transliteration import XlitEngine


SUPPORTED_LANGUAGES = {
    "hi",
    "te",
    "ta",
    "kn",
}


@lru_cache(maxsize=4)
def get_engine(language: str):

    if language not in SUPPORTED_LANGUAGES:

        raise ValueError(
            f"Unsupported language '{language}'. "
            f"Supported languages: "
            f"{', '.join(sorted(SUPPORTED_LANGUAGES))}"
        )

    return XlitEngine(
        lang2use=language,
        beam_width=10,
        rescore=True,
        src_script_type="indic",
    )


def transliterate(text: str, language: str) -> str:

    engine = get_engine(language)

    result = engine.translit_sentence(
        text,
        language
    )

    if isinstance(result, dict):

        value = result.get(language)

        if isinstance(value, list):

            return " ".join(value)

        if value is not None:

            return str(value)

    return str(result)