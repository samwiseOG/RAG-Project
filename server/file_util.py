from extractor import create_extractor

def get_text_from_pdf(file: str):
    extractor = create_extractor(file)
    content = extractor.extract(file)
    return content