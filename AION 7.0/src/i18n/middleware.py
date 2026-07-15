from starlette.datastructures import Headers


SUPPORTED_LANGS = ["pt", "en", "es"]
DEFAULT_LANG = "pt"


def detect_language(headers: Headers) -> str:
    accept_language = headers.get("accept-language", "")
    for part in accept_language.split(","):
        code = part.strip().split(";")[0].split("-")[0].lower()
        if code in SUPPORTED_LANGS:
            return code
    return DEFAULT_LANG


def get_lang_from_query(params: dict, headers: Headers) -> str:
    lang = params.get("lang", "")
    if lang in SUPPORTED_LANGS:
        return lang
    return detect_language(headers)
