INCOMPLETE

# Resume Analyser

All of these resume analyzers are paid, and let's be honest, absolute garbage. They make big promises and deliver close to nothing. I wanted to make something free or as close to free as possible because paying 8.99 a month for an AI wrapper is ridiculous.

I created this product for a few different uses. Using AI, you can either run these resume improvement tasks locally if you have a gpu, or using a cheap api or free api using a model like 40-mini or AliBaba (Qwen) usually has something free. Support for the latter will be added later.

## Functionality

### Resume Improvement Tips

### Get Best Resume

## How ATS works

Applicant Tracking Systems (ATS) will collect, parse, rank, and store your resume. Most people get rejected automatically because they get knocked too far down the list.

The resume parser will extract structured fields like your personal info and the sections on your resume like work history, education, and skills. Then, using string pattern matching and AI LLM models, they will normalize content like AWS = Amazon Web Services, or B.S. = Bachelor of Science, etc.

Finally, the resume is indexed, almost like how a search engine works and they will search keywords from the job description.

They will take the job description, take the keywords and skills, and compare them to your resume. They can do this using keyword match scoring (i.e. 10/12 keyword terms appear = high match) or they use semantic search which is where embeddings are created for the resumes in the database and compared against the job description. This works exactly like a RAG where the query is the job description, the resume database returns the n nearest neighbors.
