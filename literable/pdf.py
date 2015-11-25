from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO
import string


class PDF:
    def __init__(self, pdf_file):
        self.filename = pdf_file

    def count_words(self):
        """
        Thanks to http://pinkyslemma.com/2013/07/02/word-frequency-from-pdfs/
        and http://www.unixuser.org/~euske/python/pdfminer/programming.html
        """
        with open(self.filename, "rb") as fp:
            rsrcmgr = PDFResourceManager()
            retstr = StringIO()
            codec = 'utf-8'
            laparams = LAParams()
            laparams.all_texts = True
            device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

            parser = PDFParser(fp)
            # Create a PDF document object that stores the document structure.
            # Supply the password for initialization.
            document = PDFDocument(parser)
            # Check if the document allows text extraction. If not, abort.
            if not document.is_extractable:
                raise PDFTextExtractionNotAllowed

            # Create a PDF interpreter object.
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            # Process each page contained in the document.
            for page in PDFPage.create_pages(document):
                interpreter.process_page(page)

            full_text = retstr.getvalue()
            full_text = full_text.translate(string.maketrans("", ""), string.punctuation)

            return len(full_text.split())
