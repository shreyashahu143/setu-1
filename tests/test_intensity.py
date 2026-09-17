import os, json

# Load .env manually
with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from google import genai

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = (
    'You are an ultra street-smart local dialect and cultural coach in Nagpur, Maharashtra (Vidarbha).\n'
    '\n'
    'User Query: "how do i tell him to shut the fuck up and leave me alone"\n'
    'User Origin / Background: "North India"\n'
    '\n'
    '### CORE INTELLIGENCE:\n'
    '\n'
    '1. LANGUAGE COHESION: Pick ONE cohesive language (Nagpur Street Hindi OR Varhadi Marathi, never a mix).\n'
    '\n'
    '2. INTENSITY-MATCHED CONFRONTATION RESPONSES (CRITICAL):\n'
    '   - The spoken_script MUST match the user\'s emotional intensity.\n'
    '   - Read the user\'s actual words and frustration level:\n'
    '     * MILD (vendor pestering): \'Nahi chahiye bhai\'\n'
    '     * FIRM (someone won\'t stop): \'Aye, tang mat kar. Chal hat\' / \'Nikal yahan se\'\n'
    '     * HARD (user is angry, wants strong shutdown): \'Bhag yahan se, dimaag mat kha\' / \'Aye chal be, zyada mat bol\' / \'Ek dum chup. Aage badh.\'\n'
    '   - \'shut the fuck up\' = HARD intensity. Give a genuinely forceful Nagpur street equivalent.\n'
    '\n'
    '3. NEVER UNDER-DELIVER ON INTENSITY:\n'
    '   - User saying \'shut the fuck up\' and getting \'Chhod na bhai, nahi chahiye\' is a FAILURE.\n'
    '   - Match the user\'s fire with short, sharp, commanding Nagpur street phrases.\n'
    '\n'
    'Respond strictly in valid JSON:\n'
    '{\n'
    '  "local_term_replacement": "null or explanation",\n'
    '  "spoken_script": "Short forceful sentence in Nagpur street Hindi",\n'
    '  "phonetic_english": "Phonetic guide",\n'
    '  "literal_meaning": "English translation",\n'
    '  "tone_directive": "Posture, eye contact, voice",\n'
    '  "cultural_insight": "Why this works on the street"\n'
    '}'
)

resp = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
text = resp.text.strip()
if text.startswith("```"):
    text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
data = json.loads(text)
print(json.dumps(data, indent=2, ensure_ascii=False))
