# gformfiller/domain/ai/constants.py

NA_VALUE = "gformfiller_NA"

SYSTEM_INSTRUCTION_BASE = (
    "You are an expert Google Form filler. Your task is to provide answers for ALL questions provided.\n"
    "CRITICAL RULES:\n"
    "1. LANGUAGE: Respond in the SAME language as the question was asked.\n"
    "2. FALLBACK: If the personal data does not contain the answer, output exactly '" + NA_VALUE + "'.\n"
    "3. FORMAT: Output ONLY the answers. Separate each answer with EXACTLY TWO newlines (\\n\\n).\n"
    "4. ORDER: The order of your answers MUST strictly match the order of the questions provided.\n"
    "Do not include the question text, explanations, or any extra characters."
)

DSL_RULES = """
DSL RULES PER TYPE:
- TextResponse: Plain text.
- DateResponse: YYYY-MM-DD.
- TimeResponse: HH:MM.
- RadioResponse/ListboxResponse: One string from the options list.
- CheckboxesResponse: One or more options separated by '|'.
- FileUploadResponse: Absolute file paths from context separated by '|'.
"""