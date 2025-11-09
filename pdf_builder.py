import markdown
import pdfkit

_wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
_pdfkit_config = pdfkit.configuration(wkhtmltopdf=_wkhtmltopdf_path)

def build_pdf(md_text, filename="resume.pdf"):
    html = markdown.markdown(md_text)
    pdfkit.from_string(html, filename, configuration=_pdfkit_config)
    return filename