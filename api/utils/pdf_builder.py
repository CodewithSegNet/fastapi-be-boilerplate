from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

class PDFBuilder:

    def __init__(self, pdf_buffer):
        self.doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.story = []

    
    def build(self):
        self.doc.build(self.story)


    def add_title(self, title: str):
        title_style = self.styles["Title"]
        self.story.append(Paragraph(title, title_style))
        self.story.append(Spacer(1, 12))


    def add_body(self, text: str):
        normal_style = self.styles["Normal"]
        paragraphs = text.split("\n\n")

        for paragraph in paragraphs:
            self.story.append(Paragraph(paragraph, normal_style))
            self.story.append(Spacer(1, 12))
            
    
    def add_section(self, title: str, text: str):
        self.add_title(title)
        self.add_body(text)
        self.story.append(Spacer(1, 24))