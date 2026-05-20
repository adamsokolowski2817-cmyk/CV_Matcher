import fitz


def extract_text_from_pdf(file_path: str) -> str:
    text_parts = []

    with fitz.open(file_path) as doc:
        for page in doc:
            text = page.get_text()

            if text:
                text_parts.append(text)

    return "\n".join(text_parts).strip()