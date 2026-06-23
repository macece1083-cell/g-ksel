import json
import random
import re
from dataclasses import dataclass

from .config import Settings
from .models import Slide, VideoPlan

LEVEL_LABELS = {
    "A1": "Beginner", "A2": "Elementary", "B1": "Intermediate",
    "B2": "Upper Intermediate", "C1": "Advanced", "C2": "Mastery",
}

TOPICS = [
    "daily vocabulary", "grammar", "phrasal verbs", "idioms",
    "pronunciation", "common mistakes", "listening practice", "short story",
]

TAGS_BASE = ["learn english", "english lesson", "english for beginners", "ESL",
             "english grammar", "english vocabulary", "english speaking", "english tips"]


def _claude_plan(level: str, topic: str, settings: Settings):
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        if topic == "short story":
            prompt = (
                f"Create a short English learning video script for {level} level students. "
                f"Tell a simple, engaging short story in 4-5 slides. "
                f"Each slide should have narration that's part of the story, with vocabulary explanations woven in naturally. "
                f"Return ONLY valid JSON with this exact structure: "
                f'{{ "title": "...", "description": "...", "tags": ["...", "..."], '
                f'"slides": [{{"title": "...", "narration": "...", "visual_prompt": "...", "caption": "..."}}] }}'
                f"Make the story simple, fun, and educational for {LEVEL_LABELS.get(level, level)} learners."
            )
        else:
            prompt = (
                f"Create a YouTube English learning video plan for {LEVEL_LABELS.get(level, level)} ({level}) level about '{topic}'. "
                f"Make it fresh, engaging, and educational with real examples. "
                f"Return ONLY valid JSON with this exact structure: "
                f'{{ "title": "...", "description": "...", "tags": ["...", "..."], '
                f'"slides": [{{"title": "...", "narration": "...", "visual_prompt": "...", "caption": "..."}}] }}'
                f"Include 4-5 slides. The title should be catchy for YouTube. "
                f"Visual prompts should describe vivid, educational scenes. "
                f"Narration should sound natural when spoken aloud."
            )

        message = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        data = json.loads(match.group())
        slides = [
            Slide(
                title=s.get("title", ""),
                narration=s.get("narration", ""),
                visual_prompt=s.get("visual_prompt", ""),
                caption=s.get("caption", ""),
            )
            for s in data.get("slides", [])
        ]
        return VideoPlan(
            level=level, topic=topic,
            title=data.get("title", f"{level} English: {topic.title()}"),
            description=data.get("description", ""),
            tags=data.get("tags", TAGS_BASE[:5]),
            slides=slides,
        )
    except Exception as exc:
        print(f"Claude kullanilamadi, template'e geciliyor: {exc}")
        return None


TEMPLATES = {
    "daily vocabulary": [
        {"title": "Word: Appreciate", "narration": "Our first word today is appreciate. It means to recognize the value of something. For example: I really appreciate your help. Or: She appreciates good music.", "visual_prompt": "person smiling gratefully, warm sunlight, positive emotions", "caption": "Appreciate — to value something"},
        {"title": "Word: Determine", "narration": "Next is determine. It means to decide firmly or to find out something. For example: She was determined to succeed. Or: We need to determine the cause.", "visual_prompt": "focused person writing goals, determination, motivation", "caption": "Determine — to decide firmly"},
        {"title": "Word: Elaborate", "narration": "Our third word is elaborate. As an adjective it means detailed and complex. As a verb it means to explain in more detail. For example: Can you elaborate on that point?", "visual_prompt": "complex detailed blueprint or diagram, professional design", "caption": "Elaborate — detailed or explain more"},
        {"title": "Word: Genuine", "narration": "Next is genuine. It means real, authentic, or sincere. For example: Is this a genuine diamond? Or: He showed genuine concern for others.", "visual_prompt": "authentic handmade product, artisan craft, genuine quality", "caption": "Genuine — real and authentic"},
        {"title": "Quick Review", "narration": "Let us review. Appreciate means to value something. Determine means to decide firmly. Elaborate means detailed or to explain more. And genuine means real or authentic. Practice using these words today!", "visual_prompt": "colorful vocabulary flashcards spread on a desk, studying", "caption": "Review your new words!"},
    ],
    "short story": [
        {"title": "The Lost Dog", "narration": "Today we have a short story. Maria was walking to the park when she saw a small dog sitting alone by a bench. The dog looked scared and confused.", "visual_prompt": "woman walking in park, small dog sitting alone near bench, sunny day", "caption": "Maria found a lost dog"},
        {"title": "Making Friends", "narration": "Maria sat next to the dog. She said: Hello little one, are you lost? The dog wagged its tail. Wag means to move back and forth. The dog seemed happy to see her.", "visual_prompt": "woman sitting on bench petting small dog, warm smile, park setting", "caption": "Wag — to move back and forth"},
        {"title": "Finding Help", "narration": "Maria decided to help the dog. She asked people nearby: Excuse me, do you know this dog? Nobody knew. So she called the local animal shelter. A shelter is a safe place for animals without a home.", "visual_prompt": "woman on phone, concerned expression, people in park background", "caption": "Shelter — a safe place for animals"},
        {"title": "A Happy Ending", "narration": "The shelter came quickly. They found the dog had a microchip with its owner contact. Soon, a young boy named Tom arrived. He was overjoyed to see his dog Max again. Overjoyed means extremely happy.", "visual_prompt": "happy boy hugging dog, joyful reunion, park scene, sunshine", "caption": "Overjoyed — extremely happy"},
        {"title": "Story Review", "narration": "Great story! Today we learned: wag means to move back and forth, shelter means a safe place, and overjoyed means extremely happy. Maria helped Max find his way home. Always help when you can!", "visual_prompt": "summary flashcards with story illustrations, educational review", "caption": "3 new words from our story!"},
    ],
}

FALLBACK_TOPICS = ["daily vocabulary", "short story"]


def _template_plan(level: str, topic: str) -> VideoPlan:
    key = topic.lower().strip()
    slides_data = TEMPLATES.get(key) or TEMPLATES.get(random.choice(FALLBACK_TOPICS))
    slides = [Slide(**s) for s in slides_data]
    if key == "short story":
        title = f"Short English Story for {LEVEL_LABELS.get(level, level)} Learners"
        description = f"A simple English short story for {level} learners with vocabulary explanations. Perfect for improving your reading and listening skills!\n\n#LearnEnglish #EnglishStory #{level}English #ESL"
    else:
        title = f"{level} English: Learn {topic.title()} Today"
        description = f"Learn English {topic} for {LEVEL_LABELS.get(level, level)} level students.\n\n#LearnEnglish #{level}English #ESL"
    tags = TAGS_BASE + [f"{level} english", topic.lower(), LEVEL_LABELS.get(level, level).lower()]
    return VideoPlan(level=level, topic=topic, title=title, description=description, tags=tags, slides=slides)


def pick_daily_topic() -> str:
    weights = [3, 2, 2, 2, 1, 2, 1, 2]
    return random.choices(TOPICS, weights=weights, k=1)[0]


def create_video_plan(level: str, topic: str, settings: Settings) -> VideoPlan:
    if topic == "auto":
        topic = pick_daily_topic()
        print(f"Gunun konusu: {topic}")
    if settings.provider.lower() == "claude" and settings.anthropic_api_key:
        plan = _claude_plan(level, topic, settings)
        if plan:
            return plan
    return _template_plan(level, topic)
