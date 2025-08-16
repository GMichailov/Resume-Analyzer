from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from docx2python import docx2python
from pathlib import Path

def read_resume(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError("File not found.")
    file_type = p.suffix.lower()
    if file_type == ".pdf":
        return parse_pdf_resume(p)
    elif file_type == ".docx":
        return parse_docx_resume(p)
    else:
        raise ValueError(f"Unsopported file type: Expected pdf or docx.")
    
def parse_pdf_resume(path: Path):
    layout_params = LAParams(line_margin=0.2, word_margin=0.1, char_margin=2.0)
    text = extract_text(str(path), laparams=layout_params) or ""
    return text

def parse_docx_resume(path: Path):
    result = docx2python(str(path))
    return result.text

def get_important_info(resume_text):
    prompt = (
        "The following content is a resume. Your job is to go over and extract the important information for an ATS system."
        "Return a dictionary of string keys (education, skills, work experience, projects, and certifications)"
        "For skills, normalize everything to the nonabreviated version: i.e. AWS becomes Amazon Web Services or TF becomes tensorflow. Include soft skills written down. Only add the skills under the skills section, not anywhere else."
        "For education, return this as a dictionary of school, start_date, end_date, gpa, degree type (so bs, ba, ms, msc, phd)"
        "For work experience, the value should be a list of dictionaries where each job should have company, role, start_date, end_date, skills that are listed explicitly, do not infer anything, and finally an echoing of all of the bullet points concatenated into one paragraph under the section 'text'."
        "For projects, the return should be a list of dictionaries where each project should have skills, and text as it was for work experience."
        "For certifications, it should be a list of dictionaries that has a certifier key and a skills key to a list of skills that this certifies."
        "If something is not found, set it as the default value. The output should be this json object and ONLY this json object."
        f"\nResume:\n:{resume_text}"
    )
    