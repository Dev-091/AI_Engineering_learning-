# Resume Parser: Code ki Full Hinglish Explanation

## 1. Program ka overall purpose

Ye program job description ko pehle structured data mein convert karta hai, phir `resumes` folder se PDF aur DOCX files read karta hai. Har resume ke liye ye:

1. Resume ka text nikalta hai.
2. Groq LLM se resume ki details parse karta hai.
3. Job description aur parsed resume compare karke match score aur details mangta hai.
4. Sab candidates ko score ke hisaab se sort karke top aur lowest 2 print karta hai.

High-level flow:

```text
Job description input
    -> JobD JSON extraction
    -> resumes folder scan
    -> PDF/DOCX se text extraction
    -> Resume JSON extraction
    -> Job vs resume scoring
    -> Top 2 aur lowest 2 print
```

## 2. Imports aur dependencies

File ke start mein:

- `os`: environment variable se API key read karne ke liye.
- `time`: API calls ke beech delay dene ke liye.
- `Path` from `pathlib`: `resumes` folder aur file paths handle karne ke liye.
- `load_dotenv`: `.env` file se environment variables load karne ke liye.
- `Groq`: Groq chat-completion API client.
- `BaseModel`: Pydantic models define karke LLM ke JSON response ko validate karne ke liye.
- `Field`: import hua hai, lekin current code mein use nahi ho raha.
- `json`: LLM ke JSON string ko Python object banane ke liye.
- `PdfReader`: PDF pages se text extract karne ke liye.
- `Document`: DOCX paragraphs aur tables se text nikalne ke liye.

`pyproject.toml` mein in packages ke distribution names hain:

- `groq`
- `pydantic`
- `python-dotenv`
- `pypdf`
- `python-docx`

Dhyan rahe: import naam `docx` hai, lekin `uv add` mein package ka naam `python-docx` hota hai.

## 3. API key aur Groq client

```python
load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")
```

`load_dotenv()` `.env` file se `GROQ_API_KEY` load karne ki koshish karta hai. `os.getenv(...)` us value ko Python mein read karta hai.

```python
if not my_api_key:
    raise ValueError("API key kaha hai bhai")
```

Key na milne par program yahin rukta hai. Isse API request bina key ke nahi jaati.

```python
client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-120b"
```

Yahan Groq client aur use hone wala model select hota hai. Model ko script mein teen tarah ke kaam ke liye call kiya jata hai: job description parse karne, resume parse karne, aur resume-job match score dene ke liye.

## 4. Job description input aur `JobD` model

```python
job_description = input("Enter the job description: ")
```

`input()` terminal se **sirf ek line** read karta hai. Agar aap multi-line job description paste karte hain, to aam taur par pehli line hi `job_description` mein jaati hai. Baaki lines program ke khatam hone ke baad PowerShell commands ki tarah interpret ho sakti hain.

```python
class JobD(BaseModel):
    role: str
    required_skills: list[str]
    preferred_skills: list[str]
    minimum_experience: float | None
    education_requirements: list[str]
    responsibilities: list[str]
```

`JobD` Pydantic model batata hai ki parsed job description ka expected structure kya hai:

- `role`: job title ya role.
- `required_skills`: zaroori skills ki list.
- `preferred_skills`: achhi hongi, lekin mandatory na bhi hon, aisi skills.
- `minimum_experience`: minimum experience; `None` ka matlab information nahi mili.
- `education_requirements`: education requirements ki list.
- `responsibilities`: job duties ki list.

```python
jobd_schema = JobD.model_json_schema()
```

Pydantic class se JSON Schema banta hai. Ye schema LLM ko batata hai ki output ka format aur fields kya hone chahiye.

## 5. Job description LLM request

`system_prompt` model ko uska role aur output rules batata hai:

- Job description analyze karni hai.
- Schema ke format mein JSON dena hai.
- Schema khud output nahi karna.
- Missing lists ke liye empty list aur missing experience ke liye `null` dena hai.
- Information invent nahi karni.

`user_prompt` mein actual job description bheji jaati hai.

```python
message_system = {"role": "system", "content": system_prompt}
message_user = {"role": "user", "content": user_prompt}
messages = [message_system, message_user]
```

Chat API ko system aur user messages isi list mein milte hain.

```python
response_format = {"type": "json_object"}
response = client.chat.completions.create(...)
```

`response_format` model se JSON object mangta hai. API call network ke through Groq ko jaati hai aur usage ke hisaab se API quota/cost lag sakti hai.

```python
answer = response.choices[0].message.content
job_data = json.loads(answer)
job = JobD(**job_data)
```

Yahan:

1. Response ke pehle choice ka message content liya jata hai.
2. `json.loads` JSON text ko Python dictionary mein badalta hai.
3. `JobD(**job_data)` dictionary ko Pydantic model mein convert aur validate karta hai.

`print` statements sirf parsed minimum experience aur education requirements dikhate hain.

## 6. Resume aur scoring ke Pydantic models

### `MatchResult`

```python
class MatchResult(BaseModel):
    score: float
    details: dict
```

Ye job-resume comparison ke output ko describe karta hai:

- `score`: model ka diya hua overall score.
- `details`: candidate name, matching skills, missing skills, verdict jaise fields rakhne wala dictionary.

`details` ka type general `dict` hai, isliye uske andar ke keys ka structure Pydantic yahan strictly validate nahi karta.

### `Experience`

Is model mein ek experience record ke fields hain: `company`, `role`, `duration`, `description`, aur `skills_used`. `None` ka matlab field missing ho sakta hai; `skills_used` ek list hai.

### `Resume`

`Resume` parsed candidate data ka structure define karta hai:

- `name`, `email`, `phone`
- `total_experience_years`
- `skills`
- `experiences`
- `education`
- `projects`
- `certifications`

`experiences` ke items `Experience` model hote hain. Pydantic nested data ko bhi validate karta hai.

List fields par code mein `=[]` defaults hain. Pydantic non-hashable defaults ko models ke beech copy karta hai, lekin aam taur par `Field(default_factory=list)` zyada clear practice hai. File mein `Field` isi kaam ke liye import hua lagta hai, par use nahi hua.

```python
resume_schema = Resume.model_json_schema()
```

Resume ke expected JSON output ka schema banta hai, jo agle prompt mein diya jata hai.

## 7. `final_score(job, resume)` function

Is function ka kaam parsed job aur parsed resume compare karna hai.

```python
job.model_dump_json(indent=2)
resume.model_dump_json(indent=2)
```

Pydantic models ko readable JSON strings mein convert kiya jata hai. Ye JSON prompt mein job aur resume ke roop mein include hota hai.

Prompt model se matching skills, missing important skills, experience requirement, overall percentage aur short verdict maangta hai. Function ek Groq API request bhejta hai, JSON response parse karta hai aur:

```python
return MatchResult(**data)
```

ke zariye result ko validate karke return karta hai.

**Important:** `score` model-generated judgment hai; code khud koi fixed mathematical scoring formula calculate nahi karta. Isliye score ko objective ya guaranteed-correct result nahi samajhna chahiye.

## 8. `parse_resume(resume_text)` function

Is function ko ek resume ka extracted text milta hai. System prompt LLM ko kehta hai:

- Resume headings alag ho sakte hain; meaning dekhkar experience aur skills identify karo.
- Information invent mat karo.
- Missing scalar values ko `null` aur missing lists ko empty list do.
- Internships ko experiences mein include karo.
- Poore resume mein se relevant skills collect karo.

Prompt mein `resume_schema` bhi bheja jata hai. Phir function:

1. `messages` aur JSON response format banata hai.
2. Groq API ko request bhejta hai.
3. Response content ko `json.loads` se dictionary banata hai.
4. `Resume(**data)` se Pydantic validation karta hai.
5. Validated resume model return karta hai.

## 9. PDF aur DOCX se text nikalna

### `read_pdf(file_path)`

`PdfReader(file_path)` PDF kholta hai. Har page ke liye `extract_text()` call hota hai. Agar page par text mila, to text result mein add kiya jata hai.

Scanned/image-only PDF mein selectable text na ho to `extract_text()` khaali ya `None` de sakta hai. Is code mein OCR nahi hai, isliye aise PDF ke liye alag OCR tool ki zaroorat padegi.

### `read_docx(file_path)`

`Document(file_path)` DOCX file kholta hai. Function non-empty paragraphs ke text ko collect karta hai, phir document tables ki rows aur cells se bhi text add karta hai.

Ye function paragraphs aur tables cover karta hai; images se text/OCR, comments, ya har possible Word feature extract nahi karta.

### `read_resume(file_path)`

File extension lowercase karke check hoti hai:

- `.pdf` ho to `read_pdf`.
- `.docx` ho to `read_docx`.
- Koi aur extension ho to `None`.

Main loop isse pehle unsupported file extensions skip kar deta hai.

## 10. `resumes` folder aur processing loop

```python
resume_folder = Path("resumes")
```

Ye relative path hai. Iska matlab program ko Day 5 project folder se run karna chahiye aur uske andar `resumes` folder hona chahiye. `iterdir()` sirf us folder ke immediate items dekhta hai; nested subfolders recursively scan nahi hote.

Har file ke liye:

1. Extension `.pdf` ya `.docx` na ho to skip.
2. File name print hota hai.
3. `read_resume` se text nikala jata hai.
4. `parse_resume` se pehli LLM call hoti hai.
5. `time.sleep(5)` 5 seconds rukta hai.
6. `final_score` se doosri LLM call hoti hai.
7. Phir 5 seconds rukkar score print hota hai.
8. Name, score aur details `all_results` mein store hote hain.

Har resume ke liye do LLM calls hain. Job description parse karne ki ek alag call pehle hoti hai. Isliye `N` resumes par total calls `1 + 2N` hoti hain. Har resume ke liye code mein total 10 seconds ka explicit delay bhi hai; API ka response time iske alawa hai.

## 11. Top aur lowest candidates

```python
all_results.sort(
    key=lambda candidate: candidate["score"],
    reverse=True
)
```

Results score ke basis par descending order mein sort hote hain.

- `all_results[:2]`: pehle do, yaani highest scores.
- `all_results[-2:]`: aakhri do, yaani lowest scores.

Phir dono groups ke names, scores aur details print hote hain. Agar do se kam resumes process huye, to slices jitne available hon utne results dikhayengi. Ek ya zero candidates par top aur lowest sections overlap kar sakte hain ya khaali ho sakte hain.

## 12. Program kaise run karein

PowerShell mein Day 5 folder par jaakar:

```powershell
cd "D:\ai eng\week1\day5"
uv run python .\resume_parser.py
```

`uv run` Day 5 ke project environment ko use karta hai. Current code job description ke liye sirf ek line ka `input()` leta hai, isliye poora multi-line text paste karne par pehli line hi capture ho sakti hai. Multi-line input chahiye to input loop ko badalna hoga.

API key `.env` mein honi chahiye:

```text
GROQ_API_KEY=your_key_here
```

Actual key ko source code ya Git mein commit na karein.

## 13. Zaroori limitations aur safety notes

- Job description khaali ya galat input ho to extracted requirements khaali aa sakti hain. Aisi situation mein model unrealistic 100% score de sakta hai. Pehle verify karein ki `JobD` ke fields meaningful hain.
- PDF/DOCX se extracted resume text Groq API ko bheja jata hai. Resume mein personal data ho sakta hai; sirf authorized resumes use karein aur organization ki privacy policy follow karein.
- LLM score mein bias ya factual mistakes ho sakti hain. Is output ko hiring decision ka akela basis na banayein; human review zaroor rakhein.
- `resumes` folder missing ho to `iterdir()` error dega. Current code is error ko handle nahi karta.
- Network/API failure, invalid JSON, ya unexpected response par code ruk sakta hai; in cases ke liye explicit retry/error handling abhi nahi likhi gayi.
- `time.sleep(5)` sirf delay hai; ye API call ko correct ya result ko fair nahi banata.
