import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from django.conf import settings


TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")
STOPWORDS = {
    "about", "above", "after", "again", "against", "being", "between", "could", "during",
    "each", "from", "have", "into", "more", "most", "other", "should", "than", "that",
    "their", "there", "these", "this", "those", "through", "under", "what", "when", "where",
    "which", "while", "with", "would", "your",
}

SAFETY_RULES_DIR = Path(__file__).resolve().parent / "knowledge_base" / "safety"
KNOWLEDGE_BASE_DIR = Path(getattr(settings, "MEDIA_ROOT", Path(__file__).resolve().parent.parent / "media")) / "chat_knowledge_base"
CHUNKS_PATH = KNOWLEDGE_BASE_DIR / "chunks.jsonl"

SOURCE_DOCUMENTS = [
    {
        "source": "ICMR-NIN Dietary Guidelines for Indians 2024",
        "organization": "ICMR-National Institute of Nutrition",
        "topic": "diet",
        "country": "India",
        "condition": "general",
        "population": "general",
        "filename": "diet/icmr_nin_dietary_guidelines_indians_2024.pdf",
        "url": "https://www.nin.res.in/dietaryguidelines/pdfjs/locale/DGI_2024.pdf",
        "last_verified": "2026-05-06",
    },
    {
        "source": "WHO Healthy Diet",
        "organization": "World Health Organization",
        "topic": "diet",
        "country": "global",
        "condition": "general",
        "population": "general",
        "filename": "diet/who_healthy_diet.html",
        "url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
        "last_verified": "2026-05-06",
    },
    {
        "source": "WHO Guidelines on Physical Activity and Sedentary Behaviour",
        "organization": "World Health Organization",
        "topic": "exercise",
        "country": "global",
        "condition": "general",
        "population": "general",
        "filename": "exercise/who_physical_activity_guidelines.pdf",
        "url": "https://iris.who.int/server/api/core/bitstreams/f3885485-e7eb-4504-8026-edd9bb53a6ee/content",
        "last_verified": "2026-05-06",
    },
    {
        "source": "CDC Physical Activity Basics for Adults",
        "organization": "CDC",
        "topic": "exercise",
        "country": "United States",
        "condition": "general",
        "population": "adults",
        "filename": "exercise/cdc_physical_activity_adults.html",
        "url": "https://www.cdc.gov/physical-activity-basics/guidelines/adults.html",
        "last_verified": "2026-05-06",
    },
    {
        "source": "NHLBI Aim for a Healthy Weight",
        "organization": "NHLBI",
        "topic": "weight_management",
        "country": "United States",
        "condition": "general",
        "population": "adults",
        "filename": "weight_management/nhlbi_aim_for_healthy_weight.pdf",
        "url": "https://www.nhlbi.nih.gov/sites/default/files/publications/05-5213.pdf",
        "last_verified": "2026-05-06",
    },
    {
        "source": "NHS Eatwell Guide",
        "organization": "NHS",
        "topic": "diet",
        "country": "United Kingdom",
        "condition": "general",
        "population": "general",
        "filename": "diet/nhs_eatwell_guide.html",
        "url": "https://www.nhs.uk/live-well/eat-well/food-guidelines-and-food-labels/the-eatwell-guide/",
        "last_verified": "2026-05-06",
    },
    {
        "source": "NIDDK Diet and Nutrition",
        "organization": "NIDDK",
        "topic": "medical_conditions",
        "country": "United States",
        "condition": "diabetes obesity kidney disease digestive disease",
        "population": "general",
        "filename": "medical_conditions/niddk_diet_nutrition_pages.html",
        "url": "https://www.niddk.nih.gov/health-information/diet-nutrition",
        "last_verified": "2026-05-06",
    },
]

FALLBACK_CHUNKS = [
    {
        "source": "WHO Healthy Diet",
        "organization": "World Health Organization",
        "topic": "diet",
        "subtopic": "fruits vegetables whole foods",
        "population": "general",
        "condition": "general",
        "country": "global",
        "url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
        "last_verified": "2026-05-06",
        "chunk_text": "Healthy diet guidance emphasizes vegetables, fruits, legumes, nuts, and whole grains while limiting excess salt, free sugars, and unhealthy fats. Advice should be adapted to the user's medical status, culture, food availability, and goals.",
    },
    {
        "source": "WHO Guidelines on Physical Activity and Sedentary Behaviour",
        "organization": "World Health Organization",
        "topic": "exercise",
        "subtopic": "adult weekly activity",
        "population": "adults",
        "condition": "general",
        "country": "global",
        "url": "https://www.who.int/publications/i/item/9789240015128",
        "last_verified": "2026-05-06",
        "chunk_text": "Adults should generally build toward weekly aerobic physical activity and include muscle-strengthening activity on at least two days per week. Beginners and users with chronic conditions should start gradually and avoid pain-provoking activity.",
    },
    {
        "source": "NHLBI Aim for a Healthy Weight",
        "organization": "NHLBI",
        "topic": "weight_management",
        "subtopic": "safe weight loss",
        "population": "adults",
        "condition": "general",
        "country": "United States",
        "url": "https://www.nhlbi.nih.gov/resources/aim-healthy-weight-patient-booklet",
        "last_verified": "2026-05-06",
        "chunk_text": "Safe weight management is built around sustainable eating patterns, portion awareness, physical activity, self-monitoring, and realistic goals rather than extreme diets or rapid weight-loss promises.",
    },
    {
        "source": "FitGenius internal safety rules",
        "organization": "FitGenius",
        "topic": "safety",
        "subtopic": "red flags",
        "population": "general",
        "condition": "general",
        "country": "global",
        "url": "",
        "last_verified": "2026-05-06",
        "chunk_text": "Do not provide precise diet or exercise plans for chest pain, fainting, severe dizziness, suspected fracture, uncontrolled blood pressure, eating disorder risk, pregnancy complications, kidney disease restrictions, or blood glucose emergencies. Recommend medical care.",
    },
]


def build_profile_context(profile, latest_checkin):
    parts = []

    if profile:
        parts.append("Health profile:")
        for label, value in [
            ("Age", profile.age),
            ("Gender", profile.gender),
            ("Height cm", profile.height),
            ("Weight kg", profile.weight),
            ("BMI", profile.bmi),
            ("BMI level", profile.bmi_level),
            ("Chronic disease", profile.chronic_disease or "none"),
            ("Hypertension", profile.hypertension),
            ("Diabetes", profile.diabetes),
            ("Blood pressure", profile.blood_pressure or "not provided"),
            ("Cholesterol", profile.cholesterol),
            ("Activity level", profile.activity_level),
            ("Exercise frequency", profile.exercise_frequency),
            ("Sleep quality", profile.sleep_quality),
            ("Dietary preference", profile.dietary_preference),
            ("Food aversion", profile.food_aversion or "none"),
            ("Fitness goal", profile.fitness_goal),
            ("Experience level", profile.experience_level),
            ("Preferred workout type", profile.preferred_workout_type),
            ("Available equipment", profile.available_equipment),
        ]:
            if value not in (None, ""):
                parts.append(f"- {label}: {value}")
    else:
        parts.append("Health profile: not completed.")

    if latest_checkin:
        parts.append("\nLatest health status/check-in:")
        for label, value in [
            ("Date", latest_checkin.date),
            ("Current weight kg", latest_checkin.current_weight),
            ("Sleep quality", latest_checkin.sleep_quality),
            ("Sleep hours", latest_checkin.sleep_hours),
            ("Daily steps", latest_checkin.daily_steps),
            ("Energy level", latest_checkin.energy_level),
            ("Soreness level", latest_checkin.soreness_level),
            ("Stress level", latest_checkin.stress_level),
            ("Resting heart rate", latest_checkin.resting_heart_rate),
            ("Pain or injury", latest_checkin.pain_or_injury),
            ("Injury area", latest_checkin.injury_area),
            ("Available minutes", latest_checkin.available_minutes),
            ("Preferred intensity", latest_checkin.preferred_intensity),
            ("Notes", latest_checkin.notes),
        ]:
            if value not in (None, ""):
                parts.append(f"- {label}: {value}")
    else:
        parts.append("\nLatest health status/check-in: not available.")

    return "\n".join(parts)


def retrieve_chat_context(question, profile_context, document_text="", limit=8):
    query = f"{question}\n{profile_context}"
    chunks = []
    chunks.extend(retrieve_knowledge_chunks(query, limit=limit))
    chunks.extend(_source_wrap(retrieve_document_snippets(question, document_text, limit=3), "Attached user document"))

    if len(chunks) < 5:
        chunks.extend(search_official_sources(question, max_results=3))

    return rerank_chunks(query, _dedupe_chunks(chunks), limit=limit)


def retrieve_knowledge_chunks(query, limit=8):
    chunks = load_chunks()
    return rerank_chunks(query, chunks, limit=limit)


def load_chunks():
    chunks = []
    loaded_index = False
    if CHUNKS_PATH.exists():
        for line in CHUNKS_PATH.read_text(encoding="utf-8").splitlines():
            try:
                chunks.append(json.loads(line))
                loaded_index = True
            except json.JSONDecodeError:
                continue

    for path in SAFETY_RULES_DIR.glob("*.md"):
        chunks.extend(build_knowledge_chunks([{
            "source": path.stem.replace("_", " ").title(),
            "organization": "FitGenius",
            "topic": "safety",
            "country": "global",
            "condition": "general",
            "population": "general",
            "url": "",
            "last_verified": "2026-05-06",
            "text": path.read_text(encoding="utf-8"),
        }]))

    if not loaded_index:
        chunks.extend(FALLBACK_CHUNKS)
    return chunks or FALLBACK_CHUNKS


def retrieve_document_snippets(question, document_text, limit=4):
    if not document_text:
        return []
    chunks = _chunk_text(document_text)
    return rerank_chunks(question, [{"chunk_text": chunk} for chunk in chunks], limit=limit)


def search_official_sources(query, max_results=3):
    allowed_domains = [
        "site:who.int",
        "site:nin.res.in",
        "site:cdc.gov",
        "site:nih.gov",
        "site:nhlbi.nih.gov",
        "site:niddk.nih.gov",
        "site:nhs.uk",
    ]
    search_query = f"{query} ({' OR '.join(allowed_domains)})"
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS

        with DDGS(timeout=10) as ddgs:
            raw_results = list(ddgs.text(search_query, region="us-en", safesearch="moderate", max_results=max_results))
    except Exception:
        return []

    chunks = []
    for result in raw_results:
        url = result.get("href") or result.get("url") or ""
        body = result.get("body") or ""
        title = result.get("title") or url
        if not _is_official_health_url(url) or not body:
            continue
        domain = urllib.parse.urlparse(url).hostname or ""
        chunks.append({
            "source": title,
            "organization": domain,
            "topic": "web_search",
            "subtopic": "official source search result",
            "population": "general",
            "condition": "general",
            "country": "global",
            "url": url,
            "last_verified": "2026-05-06",
            "chunk_text": body,
        })
    return chunks


def build_knowledge_chunks(documents, chunk_size=3600, overlap=600):
    chunks = []
    for document in documents:
        text = _clean_text(document.get("text", ""))
        sections = _split_sections(text)
        chunk_index = 0
        for heading, section_text in sections:
            subtopic = _infer_subtopic(heading, section_text)
            population = _infer_population(section_text, document.get("population", "general"))
            condition = _infer_condition(section_text, document.get("condition", "general"))
            topic = _infer_topic(section_text, document.get("topic", "general"))
            for chunk_text in _chunk_text(section_text, size=chunk_size, overlap=overlap):
                chunks.append({
                    "source": document["source"],
                    "organization": document["organization"],
                    "topic": topic,
                    "subtopic": subtopic,
                    "population": population,
                    "condition": condition,
                    "country": document.get("country", "global"),
                    "url": document.get("url", ""),
                    "last_verified": document.get("last_verified", "2026-05-06"),
                    "chunk_index": chunk_index,
                    "chunk_text": chunk_text,
                })
                chunk_index += 1
    return chunks


def write_chunks(chunks):
    CHUNKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    for source in SOURCE_DOCUMENTS:
        (KNOWLEDGE_BASE_DIR / "sources" / Path(source["filename"]).parent).mkdir(parents=True, exist_ok=True)
    with CHUNKS_PATH.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(json.dumps(chunk, ensure_ascii=True) + "\n")
    return CHUNKS_PATH


def call_nvidia_chat(message, profile_context, snippets):
    api_key = getattr(settings, 'NVIDIA_API_KEY', '')
    if not api_key:
        return _fallback_response(message, snippets)

    system_prompt = (
        "You are FitGenius Help Chat, a concise health and fitness RAG assistant. "
        "Use only the user profile, latest health status, and retrieved official-source context. "
        "Prefer Indian dietary guidance when relevant. Cite source names in the answer. "
        "Do not diagnose disease, prescribe medication, or give unsafe plans. "
        "Escalate chest pain, fainting, severe dizziness, suspected serious injury, pregnancy complications, "
        "eating disorder risk, kidney disease diet restrictions, or diabetes medication questions to a clinician."
    )
    context = profile_context
    if snippets:
        context += "\n\nRetrieved context:\n" + "\n\n".join(
            f"[{i + 1}] {snippet.get('source', 'Source')} | {snippet.get('topic', 'general')} | "
            f"{snippet.get('population', 'general')} | {snippet.get('condition', 'general')}\n"
            f"{snippet.get('chunk_text', '')}"
            for i, snippet in enumerate(snippets)
        )

    payload = {
        "model": getattr(settings, 'NVIDIA_LLM_MODEL', 'meta/llama-3.1-70b-instruct'),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nUser question:\n{message}"},
        ],
        "temperature": 0.25,
        "max_tokens": 850,
    }

    request = urllib.request.Request(
        getattr(settings, 'NVIDIA_API_URL', 'https://integrate.api.nvidia.com/v1/chat/completions'),
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return _fallback_response(message, snippets, error=str(exc))


def rerank_chunks(query, chunks, limit=8):
    query_tokens = set(_tokens(query))
    scored = []
    for index, chunk in enumerate(chunks):
        text = _chunk_body(chunk)
        chunk_tokens = set(_tokens(text))
        overlap = len(query_tokens & chunk_tokens)
        phrase_bonus = sum(2 for token in query_tokens if token in text.lower())
        safety_bonus = 4 if chunk.get("topic") == "safety" and _has_safety_terms(query) else 0
        diabetes_bonus = 3 if "diabetes" in query_tokens and "diabetes" in _tokens(text) else 0
        score = overlap * 3 + phrase_bonus + safety_bonus + diabetes_bonus
        if score > 0:
            scored.append((score, index, chunk))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [chunk for _, _, chunk in scored[:limit]]


def _fallback_response(message, snippets, error=None):
    source_names = sorted({chunk.get("source", "retrieved source") for chunk in snippets[:4]})
    response = [
        "I could not reach the NVIDIA model right now, but I found relevant guidance from the local knowledge base.",
        "",
        "Use this as general education, not a medical diagnosis or prescription. For symptoms, medication questions, pregnancy, kidney disease, diabetes emergencies, chest pain, fainting, or serious injury, contact a qualified clinician.",
    ]
    if source_names:
        response.extend(["", "Relevant sources: " + ", ".join(source_names)])
    if snippets:
        response.extend(["", "Most relevant notes:"])
        response.extend(f"- {chunk.get('chunk_text', '')[:280].strip()}" for chunk in snippets[:3])
    if error:
        response.extend(["", f"Model status: {error[:180]}"])
    return "\n".join(response)


def _source_wrap(snippets, source):
    return [{**snippet, "source": source, "topic": "user_document", "url": ""} for snippet in snippets]


def _dedupe_chunks(chunks):
    seen = set()
    unique = []
    for chunk in chunks:
        key = (chunk.get("source"), chunk.get("url"), chunk.get("chunk_text", "")[:160])
        if key not in seen:
            seen.add(key)
            unique.append(chunk)
    return unique


def _chunk_text(text, size=3600, overlap=600):
    cleaned = _clean_text(text)
    if not cleaned:
        return []
    if overlap >= size:
        overlap = max(0, size // 3)

    chunks = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + size)
        chunk = cleaned[start:end]
        if end < len(cleaned):
            for separator in ("\n\n", ". ", "; ", "\n"):
                last_sep = chunk.rfind(separator)
                if last_sep > size // 2:
                    chunk = chunk[:last_sep + len(separator)]
                    end = start + len(chunk)
                    break
        chunks.append(chunk.strip())
        if end >= len(cleaned):
            break
        start = max(end - overlap, start + 1)
    return [chunk for chunk in chunks if chunk]


def _split_sections(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sections = []
    heading = "general"
    buffer = []
    for line in lines:
        is_heading = len(line) <= 90 and (
            line.endswith(":")
            or line.isupper()
            or re.match(r"^(\d+\.|[A-Z][A-Za-z ]{3,60}$)", line)
        )
        if is_heading and len(" ".join(buffer)) > 500:
            sections.append((heading, "\n".join(buffer)))
            heading = line.rstrip(":")
            buffer = []
        else:
            buffer.append(line)
    if buffer:
        sections.append((heading, "\n".join(buffer)))
    return sections or [("general", text)]


def _infer_subtopic(heading, text):
    haystack = f"{heading} {text[:1200]}".lower()
    patterns = [
        ("salt/sodium limits", ["salt", "sodium"]),
        ("sugar limits", ["sugar", "free sugars", "sweet"]),
        ("fats and oils", ["fat", "oil", "saturated", "trans"]),
        ("fruits and vegetables", ["fruit", "vegetable"]),
        ("whole grains", ["whole grain", "cereal", "millet"]),
        ("protein sources", ["protein", "pulses", "legumes", "meat", "fish", "egg"]),
        ("adult physical activity", ["150 minutes", "moderate", "vigorous"]),
        ("strength training", ["muscle", "strength"]),
        ("weight management", ["weight", "bmi", "obesity"]),
        ("diabetes diet safety", ["diabetes", "blood glucose"]),
        ("hypertension diet safety", ["hypertension", "blood pressure"]),
        ("red flags", ["chest pain", "fainting", "dizziness", "injury"]),
    ]
    for label, keywords in patterns:
        if any(keyword in haystack for keyword in keywords):
            return label
    return heading.lower()[:80] or "general"


def _infer_population(text, default):
    lowered = text.lower()
    if "pregnan" in lowered:
        return "pregnancy"
    if "older adult" in lowered or "aged 65" in lowered:
        return "older adults"
    if "children" in lowered or "adolescent" in lowered:
        return "children/adolescents"
    if "adult" in lowered:
        return "adults"
    return default


def _infer_condition(text, default):
    lowered = text.lower()
    conditions = []
    for condition in ["diabetes", "hypertension", "kidney disease", "heart disease", "obesity"]:
        if condition in lowered:
            conditions.append(condition)
    return ", ".join(conditions) if conditions else default


def _infer_topic(text, default):
    lowered = text.lower()
    if any(word in lowered for word in ["exercise", "physical activity", "sedentary", "aerobic", "muscle-strengthening"]):
        return "exercise"
    if any(word in lowered for word in ["diet", "food", "salt", "sugar", "fat", "vegetable", "fruit", "grain"]):
        return "diet"
    if any(word in lowered for word in ["weight", "bmi", "obesity"]):
        return "weight_management"
    return default


def _is_official_health_url(url):
    host = urllib.parse.urlparse(url).hostname or ""
    return any(host.endswith(domain) for domain in (
        "who.int", "nin.res.in", "cdc.gov", "nih.gov", "nhlbi.nih.gov", "niddk.nih.gov", "nhs.uk"
    ))


def _has_safety_terms(query):
    lowered = query.lower()
    return any(term in lowered for term in [
        "pain", "injury", "chest", "faint", "dizzy", "dizziness", "pregnant", "diabetes",
        "kidney", "heart disease", "blood pressure", "medication", "doctor",
    ])


def _chunk_body(chunk):
    return " ".join(str(chunk.get(key, "")) for key in (
        "source", "organization", "topic", "subtopic", "population", "condition", "country", "chunk_text"
    ))


def _clean_text(text):
    text = re.sub(r"\r\n?", "\n", text or "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _tokens(text):
    return [
        token.lower()
        for token in TOKEN_RE.findall(text or "")
        if len(token) > 2 and token.lower() not in STOPWORDS
    ]
