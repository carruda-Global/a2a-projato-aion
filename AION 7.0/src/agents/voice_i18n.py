"""Per-language content for the Voice Receptionist assistant prompt.

Existing US/UK/CA/AU customers all default to "en" (see the schema column's
DEFAULT 'en' in sql_para_supabase.sql) so adding pt/es support here changes
nothing for them.

Structured as layers (preamble, escalation rule, style rule, disclosure
reminder, response-language rule) rather than one long paragraph per
language -- matches Vapi's own documented pattern for multilingual agents
(one shared draft, per-language layers stacked on top). Editing a single
rule (e.g. the escalation instruction) now touches one named block per
language instead of hunting through a wall of text. The recording/
AI-analysis disclosure is a legal requirement in every market this product
serves, so each language's DISCLOSURE_REMINDER layer keeps that meaning
intact rather than a loose paraphrase.
"""

SUPPORTED_LANGUAGES = ("en", "pt", "es")
DEFAULT_LANGUAGE = "en"

# Deepgram (Vapi's default transcriber provider) locale codes -- "pt-BR" and
# "es-419" pick the Brazilian Portuguese and Latin American Spanish models
# instead of the generic European variants, matching the actual target market.
TRANSCRIBER_LANGUAGE = {"en": "en", "pt": "pt-BR", "es": "es-419"}

GREETING_DISCLOSURE = {
    "en": (
        "Thanks for calling {business_name}. This call may be recorded and "
        "analyzed by AI to help us follow up with you. How can I help today?"
    ),
    "pt": (
        "Obrigado por ligar para {business_name}. Esta chamada pode ser gravada e "
        "analisada por IA para nos ajudar a dar retorno a voce. Como posso ajudar?"
    ),
    "es": (
        "Gracias por llamar a {business_name}. Esta llamada puede ser grabada y "
        "analizada por IA para ayudarnos a darle seguimiento. ¿En qué puedo ayudarle hoy?"
    ),
}

ROLE_PREAMBLE = {
    "en": "You are the AI phone receptionist for {business_name}. Business hours: {hours_text}. {address_line}{knowledge_text}",
    "pt": "Voce e a recepcionista telefonica de IA de {business_name}. Horario de funcionamento: {hours_text}. {address_line}{knowledge_text}",
    "es": "Eres la recepcionista telefonica de IA de {business_name}. Horario de atencion: {hours_text}. {address_line}{knowledge_text}",
}

ADDRESS_LABEL = {"en": "Address", "pt": "Endereco", "es": "Direccion"}

ESCALATION_RULE = {
    "en": (
        "Greet callers warmly, answer questions about hours and location, and if you "
        "can't fully help, take their name, phone number, and reason for calling so the "
        "business can follow up. "
    ),
    "pt": (
        "Cumprimente quem ligar de forma calorosa, responda perguntas sobre horario e "
        "localizacao e, se nao conseguir ajudar totalmente, anote nome, telefone e motivo "
        "da ligacao para que a empresa retorne o contato. "
    ),
    "es": (
        "Saluda a quien llame con calidez, responde preguntas sobre horario y ubicacion y, "
        "si no puedes ayudar por completo, toma su nombre, telefono y motivo de la llamada "
        "para que la empresa le devuelva la llamada. "
    ),
}

STYLE_RULE = {
    "en": "Keep responses brief and natural, like a real receptionist, not a robot reading a script. ",
    "pt": "Mantenha as respostas breves e naturais, como uma recepcionista de verdade, nao um robo lendo um roteiro. ",
    "es": "Manten las respuestas breves y naturales, como una recepcionista real, no un robot leyendo un guion. ",
}

DISCLOSURE_REMINDER = {
    "en": (
        "Do not omit the recording/AI-analysis disclosure in your first message -- it is "
        "a legal requirement in every market this product serves (US two-party-consent "
        "states, UK, Canada, Australia), not optional phrasing. "
    ),
    "pt": (
        "Nao omita o aviso de gravacao/analise por IA na primeira mensagem -- e uma "
        "exigencia legal em todos os mercados atendidos por este produto, nao uma frase "
        "opcional. "
    ),
    "es": (
        "No omitas el aviso de grabacion/analisis por IA en tu primer mensaje -- es un "
        "requisito legal en todos los mercados que atiende este producto, no una frase "
        "opcional. "
    ),
}

RESPONSE_LANGUAGE_RULE = {
    "en": "Respond to the caller in English.",
    "pt": "Responda a quem ligar em portugues.",
    "es": "Responde a quien llame en espanol.",
}


def resolve_language(language: str | None) -> str:
    language = (language or "").strip().lower()
    return language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def first_message(language: str, business_name: str) -> str:
    lang = resolve_language(language)
    return GREETING_DISCLOSURE[lang].format(business_name=business_name)


def system_prompt(
    language: str,
    business_name: str,
    hours_text: str,
    address: str,
    knowledge_text: str,
) -> str:
    lang = resolve_language(language)
    address_line = f"{ADDRESS_LABEL[lang]}: {address}. " if address else ""
    preamble = ROLE_PREAMBLE[lang].format(
        business_name=business_name,
        hours_text=hours_text,
        address_line=address_line,
        knowledge_text=knowledge_text,
    )
    return (
        preamble
        + ESCALATION_RULE[lang]
        + STYLE_RULE[lang]
        + DISCLOSURE_REMINDER[lang]
        + RESPONSE_LANGUAGE_RULE[lang]
    )
