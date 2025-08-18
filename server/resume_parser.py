from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from docx2python import docx2python
from pathlib import Path
from utils import query_router
import json
from textwrap import wrap

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

def get_skills_from_resume(resume_text: str) -> dict:
    base = (
        "The following content is from a resume. Your job is to extract the skills "
        "for an ATS system. Return a JSON object list in the format of []. "
        "Normalize abbreviations: AWS -> Amazon Web Services, TF -> TensorFlow, "
        "Py -> Python, etc. Include both hard and soft skills if explicitly written. "
        "Do NOT infer skills that are not written. The skills may not only be in the skills section, they may be under work or certificates."
    )

    chunks = wrap(resume_text, 500)
    all_skills = set()

    for chunk in chunks:
        prompt = f"{base}\n\nResume Section:\n{chunk}"
        parsed = query_router(prompt=prompt)

        try:
            json_part = parsed[parsed.find('{') : parsed.rfind('}') + 1]
            data = json.loads(json_part)
            skills = data
            for s in skills:
                all_skills.add(s.lower())
        except Exception as e:
            print(f"Warning: Failed to parse chunk -> {e}")
            continue

    return sorted(all_skills)

def hand_parse(resume_text) -> list[dict[str, str]]:
    common_sections = {
        "skills" : ["Skills\n", "\nSkills" "\nskills\n", "\nSkills:", "\nskills:", "Core Skills"],
        "experience" : ["\nExperience", "\nWork History", "Work Experience"],
        "projects" : ["Projects", "Personal Projects"],
        "certificates" : ["\nCertificates", "\nCertifications"],
        "education" : ["Education"]
    }

    start_idxs = {}

    for section, options in common_sections.items():
        for s in options:
            idx = resume_text.find(s)
            if idx != -1:
                start_idxs[section] = idx
                break
    
    sorted_sections = sorted(start_idxs.items(), key=lambda x: x[1])

    chunks = []
    for i, (section, start_idx) in enumerate(sorted_sections):
        if i + 1 < len(sorted_sections):
            end_idx = sorted_sections[i + 1][1]
        else:
            end_idx = len(resume_text)

        chunk_text = resume_text[start_idx:end_idx].strip()
        chunks.append({section: chunk_text})

    return chunks


def format_parsed_info_for_index(parsed_info):
    pass

    