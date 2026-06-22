import json
import random
from typing import Any

import requests

from .config import Settings
from .models import Slide, VideoPlan


LEVEL_DESCRIPTIONS = {
    "A1": "very simple English with basic examples",
    "A2": "simple English for everyday situations",
    "B1": "clear intermediate English with practical usage",
    "B2": "natural upper-intermediate English with nuance",
    "C1": "advanced English with precise phrasing",
    "C2": "near-native English with subtle distinctions",
}

TOPIC_BANK = {
    "daily vocabulary": ["order coffee", "ask for directions", "talk about routines", "describe weather"],
    "grammar": ["present simple", "present perfect", "conditionals", "relative clauses"],
    "pronunciation": ["word stress", "th sounds", "connected speech", "silent letters"],
    "phrasal verbs": ["look up", "run out of", "bring up", "come across"],
    "idioms": ["break the ice", "on the same page", "a blessing in disguise", "cut corners"],
    "common mistakes": ["say vs tell", "make vs do", "much vs many", "borrow vs lend"],
    "listening practice": ["airport announcements", "restaurant dialogue", "work meeting", "phone call"],
}


def create_video_plan(level: str, topic: str, settings: Settings) -> VideoPlan:
    level = level.upper()
    if settings.provider.lower() == "ollama":
        try:
            return _create_with_ollama(level, topic, settings)
        except Exception as exc:
            print(f"Ollama kullanilamadi, sablon ureticiye geciliyor: {exc}")
    return _create_with_template(level, topic)


def _create_with_template(level: str, topic: str) -> VideoPlan:
    focus = random.choice(TOPIC_BANK.get(topic.lower(), [topic]))
    style = LEVEL_DESCRIPTIONS.get(level, LEVEL_DESCRIPTIONS["A2"])
    title = f"{level} English: {focus.title()} in 60 Seconds"
    description = (
        f"Learn {focus} with {style}. Daily English practice for learners from A1 to C2.\n\n"
        "Practice aloud, pause the video, and write your own example sentence."
    )
    tags = ["English learning", "learn English", level, topic, focus, "daily English"]

    examples = _examples_for(level, focus)
    slides = [
        Slide(
            title=f"{level} English",
            narration=f"Today we will learn {focus}. This lesson uses {style}.",
            caption=f"Today: {focus}",
            visual_prompt=f"clean modern classroom scene, English learner notebook, topic {focus}, bright realistic illustration",
        ),
        Slide(
            title="Meaning",
            narration=f"The key idea is simple: use this language when you want to communicate about {focus}.",
            caption="Meaning first",
            visual_prompt=f"friendly teacher explaining {focus}, simple icons, realistic educational poster",
        ),
    ]

    for idx, example in enumerate(examples, start=1):
        slides.append(
            Slide(
                title=f"Example {idx}",
                narration=example["narration"],
                caption=example["caption"],
                visual_prompt=example["prompt"],
            )
        )

    slides.append(
        Slide(
            title="Your Turn",
            narration=f"Now make your own sentence with {focus}. Say it out loud three times.",
            caption="Your turn: make one sentence",
            visual_prompt=f"student practicing spoken English confidently, desk, microphone, warm daylight, {focus}",
        )
    )
    return VideoPlan(level=level, topic=topic, title=title, description=description, tags=tags, slides=slides)


def _examples_for(level: str, focus: str) -> list[dict[str, str]]:
    base = [
        {
            "narration": f"First example: I need to {focus} today. Repeat: I need to {focus} today.",
            "caption": f"I need to {focus} today.",
            "prompt": f"person using English in a real-life situation about {focus}, cinematic educational image",
        },
        {
            "narration": f"Second example: Could you help me with {focus}? This sounds polite and natural.",
            "caption": f"Could you help me with {focus}?",
            "prompt": f"two people having a polite English conversation about {focus}, realistic, bright",
        },
        {
            "narration": f"Common mistake: do not translate word by word. Learn the full phrase: {focus}.",
            "caption": "Do not translate word by word",
            "prompt": f"split screen showing wrong and correct English phrase learning, {focus}, clean design",
        },
        {
            "narration": f"Quick review: meaning, example, mistake, and practice. That is how you remember {focus}.",
            "caption": "Review: meaning + example + practice",
            "prompt": f"English study checklist, vocabulary cards, {focus}, high quality educational image",
        },
    ]
    if level in {"C1", "C2"}:
        base[1]["narration"] = f"A more advanced sentence: This expression is especially useful when discussing {focus} in a precise way."
        base[1]["caption"] = f"Useful for precise {focus}"
    return base


def _create_with_ollama(level: str, topic: str, settings: Settings) -> VideoPlan:
    prompt = f"""
Create a JSON plan for a 45-75 second YouTube Shorts lesson.
Language learning level: {level}
Topic: {topic}
Return only valid JSON with this shape:
{{
  "title": "...",
  "description": "...",
  "tags": ["..."],
  "slides": [
    {{"title": "...", "narration": "...", "caption": "...", "visual_prompt": "..."}}
  ]
}}
Use 6-8 slides. Narration must be in English. Make it useful, concise, and learner-friendly.
"""
    response = requests.post(
        f"{settings.ollama_url.rstrip('/')}/api/generate",
        json={"model": settings.ollama_model, "prompt": prompt, "stream": False, "format": "json"},
        timeout=120,
    )
    response.raise_for_status()
    raw = response.json()["response"]
    data: dict[str, Any] = json.loads(raw)
    slides = [Slide(**item) for item in data["slides"]]
    return VideoPlan(
        level=level,
        topic=topic,
        title=data["title"],
        description=data["description"],
        tags=data.get("tags", ["English learning", level, topic]),
        slides=slides,
    )
