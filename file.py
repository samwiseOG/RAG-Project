# import glob
# import os
# from pathlib import Path
# from abc import ABC, abstractmethod

# # Third-party libraries
# import docx
# import pptx
# import pdfplumber

# # root_dir needs a trailing slash (i.e. /root/dir/)
# root_dir = "/Users/bz/Developer/RAG-Project/demo/"
# # for filename in glob.iglob(root_dir + '**/*.txt', recursive=True):
# #      print(filename)

# def get_file(root_dir:str, type:str="txt"):
#     res = []
#     print(root_dir + '**/*.{_type}'.format(_type=type))
#     for filename in glob.iglob(root_dir + '**/*.{_type}'.format(_type=type), recursive=True):
#         res.append(filename)
#     return res

# file_types = ['txt', 'docx', 'pptx']

# for f in file_types:
#     print(get_file(root_dir=root_dir, type=f)) 

# import os
# from pathlib import Path
# from abc import ABC, abstractmethod

# # Third-party libraries
# import docx
# import pptx
# import pdfplumber

# # 1. The Strategy Interface
# class TextExtractor(ABC):
#     """
#     Declares an interface common to all supported extraction algorithms.
#     The client code will use this interface to call the algorithm defined by a
#     Concrete Strategy.
#     """
#     @abstractmethod
#     def extract(self, file_path: str) -> str:
#         """Extracts text content from a given file."""
#         pass

# # 2. Concrete Strategies
# class DocxExtractor(TextExtractor):
#     """Implements the text extraction algorithm for .docx files."""
#     def extract(self, file_path: str) -> str:
#         try:
#             doc = docx.Document(file_path)
#             return "\n".join([para.text for para in doc.paragraphs])
#         except Exception as e:
#             return f"Error processing DOCX file '{file_path}': {e}"

# class PptxExtractor(TextExtractor):
#     """Implements the text extraction algorithm for .pptx files."""
#     def extract(self, file_path: str) -> str:
#         try:
#             presentation = pptx.Presentation(file_path)
#             text_runs = []
#             for slide in presentation.slides:
#                 for shape in slide.shapes:
#                     if not shape.has_text_frame:
#                         continue
#                     for paragraph in shape.text_frame.paragraphs:
#                         text_runs.append(paragraph.text)
#             return "\n".join(text_runs)
#         except Exception as e:
#             return f"Error processing PPTX file '{file_path}': {e}"

# class PdfExtractor(TextExtractor):
#     """Implements the text extraction algorithm for .pdf files."""
#     def extract(self, file_path: str) -> str:
#         try:
#             with pdfplumber.open(file_path) as pdf:
#                 full_text = [p.extract_text() for p in pdf.pages if p.extract_text()]
#             return "\n---\n".join(full_text)
#         except Exception as e:
#             return f"Error processing PDF file '{file_path}': {e}"

# class TxtExtractor(TextExtractor):
#     """Implements the text extraction algorithm for .txt files."""
#     def extract(self, file_path: str) -> str:
#         try:
#             return Path(file_path).read_text(encoding='utf-8')
#         except Exception as e:
#             return f"Error processing TXT file '{file_path}': {e}"

# class UnsupportedFileExtractor(TextExtractor):
#     """A default strategy for unsupported file types."""
#     def extract(self, file_path: str) -> str:
#         file_extension = Path(file_path).suffix.lower()
#         return f"Unsupported file type: '{file_extension}'"

# # 3. The Simple Factory
# def create_extractor(file_path: str) -> TextExtractor:
#     """
#     Factory function that selects and returns the appropriate extractor
#     (Strategy) based on the file extension.
#     """
#     extension_map = {
#         ".docx": DocxExtractor,
#         ".pptx": PptxExtractor,
#         ".pdf": PdfExtractor,
#         ".txt": TxtExtractor,
#     }
#     file_extension = Path(file_path).suffix.lower()
#     # Get the class from the map, or default to UnsupportedFileExtractor
#     extractor_class = extension_map.get(file_extension, UnsupportedFileExtractor)
#     return extractor_class()

# # 4. Client Code
# if __name__ == "__main__":
#     print("### Text Extraction Demo (Strategy Pattern) ###\n")
   

#     # Create dummy files if they don't exist

#     # if not Path("sample.txt").exists():
#     #     Path("sample.txt").write_text("This is a simple text file.")
#     # if not Path("sample.docx").exists():
#     #     doc = docx.Document()
#     #     doc.add_paragraph("This is a sample DOCX file.")
#     #     doc.save("sample.docx")
#     # if not Path("sample.pptx").exists():
#     #     prs = pptx.Presentation()
#     #     slide = prs.slides.add_slide(prs.slide_layouts[5])
#     #     slide.shapes.title.text = "Sample PPTX Title"
#     #     prs.save("sample.pptx")

#     # files_to_process = [
#     #     "sample.docx",
#     #     "sample.pptx",
#     #     "sample.txt",
#     #     "sample.pdf",      # Manually create this file for the demo
#     #     "unsupported.zip"
#     # ]

#     files_to_process = []
#     file_types = ['txt', 'docx', 'pptx']

#     file_list = []
#     for f in file_types:
#         file_list.extend(get_file(root_dir=root_dir, type=f))

#     print(file_list)

#     for file in file_list:
#         print(f"--- Processing: {file} ---")
#         if not os.path.exists(file):
#             print(f"Result: File not found. Skipping.\n")
#             continue

#         # Use the factory to get the right strategy
#         extractor = create_extractor(file)
#         # Execute the strategy
#         content = extractor.extract(file)

#         print(f"Result:\n{content}")
#         print("-" * 25 + "\n")