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
    "conversation", "business english", "travel english", "food and cooking",
    "sports and hobbies", "technology", "emotions and feelings",
]

TAGS_BASE = ["learn english", "english lesson", "english for beginners", "ESL",
             "english grammar", "english vocabulary", "english speaking", "english tips"]

VIDEO_FORMATS = [
    "story", "quiz", "dialogue", "mistakes",
    "scenario", "tips", "challenge", "breakdown",
]

TITLE_HOOKS = [
    "Did You Know", "Can You Answer This", "Watch and Learn",
    "Quick English", "English in 5 Minutes", "Learn This Today",
    "Stop Making This Mistake", "Native Speakers Say This",
    "You Need to Know This", "English Made Easy",
    "Speak Like a Native", "Master This", "Today's English Lesson",
    "English Tip of the Day", "Level Up Your English",
]

VISUAL_STYLES = [
    "bright classroom with colorful posters, cheerful atmosphere",
    "cozy coffee shop setting, warm lighting, urban feel",
    "modern flat design infographic style, bold colors",
    "outdoor scene, nature background, fresh and vibrant",
    "library setting, books and knowledge theme, warm tones",
    "city street scene, real-life context, dynamic",
    "minimalist white background with bold typography elements",
    "tech-themed dark background with glowing neon accents",
    "watercolor illustration style, soft pastel colors",
    "comic book style, pop art colors, energetic",
]


def _pick_format() -> str:
    weights = [2, 2, 2, 2, 2, 1, 1, 2]
    return random.choices(VIDEO_FORMATS, weights=weights, k=1)[0]


def _claude_plan(level: str, topic: str, settings: Settings):
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        fmt = _pick_format()
        hook = random.choice(TITLE_HOOKS)
        style = random.choice(VISUAL_STYLES)

        format_instructions = {
            "story": "Tell an engaging short story where vocabulary/grammar is learned naturally through the narrative.",
            "quiz": "Create a quiz-style video: pose questions, give learners time to think, then reveal answers with explanations.",
            "dialogue": "Write a realistic dialogue between 2 people in a real-life situation. Highlight key phrases and explain them.",
            "mistakes": "Show 3-4 common mistakes learners make, explain WHY they are wrong, and give the correct version.",
            "scenario": "Present a real-life scenario (ordering food, job interview, travel, etc.) and teach language used in that context.",
            "tips": "Give 3-5 quick practical tips that immediately improve speaking or writing. Each tip should be memorable.",
            "challenge": "Start with a language challenge or puzzle, then guide viewers to the answer with explanations.",
            "breakdown": "Take one interesting word, phrase, or grammar point and break it down completely with examples, etymology, usage.",
        }

        prompt = (
            f"Create a YouTube English learning video for {LEVEL_LABELS.get(level, level)} ({level}) level about '{topic}'. "
            f"Video format: {fmt.upper()} - {format_instructions[fmt]} "
            f"Title hook style: use '{hook}' style - make it catchy and curiosity-driven. "
            f"Visual style: {style} "
            f"Make this video DIFFERENT and ENGAGING. Avoid generic content. Use surprising facts, real examples, humor where appropriate. "
            f"Return ONLY valid JSON: "
            f'{{ "title": "...", "description": "...", "tags": ["...", "..."], '
            f'"slides": [{{"title": "...", "narration": "...", "visual_prompt": "...", "caption": "..."}}] }}'
            f"Include 4-6 slides. Visual prompts must incorporate this style: {style}. "
            f"Each slide narration should sound natural and engaging when spoken aloud. "
            f"Make the title click-worthy and unique."
        )

        message = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=2500,
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
            title=data.get("title", f"{hook}: {level} English - {topic.title()}"),
            description=data.get("description", ""),
            tags=data.get("tags", TAGS_BASE[:5]),
            slides=slides,
        )
    except Exception as exc:
        print(f"Claude kullanilamadi, template'e geciliyor: {exc}")
        return None


TEMPLATES = {
    "common mistakes": [
        {"title": "Mistake #1: Say vs Tell", "narration": "One of the most common mistakes is confusing say and tell. Wrong: I told that I was tired. Correct: I said that I was tired. Or: I told him I was tired. Remember: tell needs an object - tell someone. Say does not need an object.", "visual_prompt": "red X and green checkmark comparison, bold typography, mistake correction style, bright educational", "caption": "SAY vs TELL - common mistake fixed!"},
        {"title": "Mistake #2: Since vs For", "narration": "Another classic error. Wrong: I have lived here since three years. Correct: I have lived here for three years. Use FOR with a period of time: for three years, for a week. Use SINCE with a point in time: since 2020, since Monday.", "visual_prompt": "timeline graphic showing duration vs point in time, clean infographic style, blue and orange", "caption": "SINCE = point in time | FOR = duration"},
        {"title": "Mistake #3: Make vs Do", "narration": "Make or do? Wrong: I did a mistake. Correct: I made a mistake. The rule: Make is for creating or producing things. Do is for actions and tasks. Make a cake, make a decision. Do homework, do exercise.", "visual_prompt": "split screen make vs do examples, vibrant classroom style, colorful icons", "caption": "MAKE a mistake, DO homework - now you know!"},
        {"title": "Mistake #4: Fun vs Funny", "narration": "These words are NOT the same! Fun means enjoyable: The party was fun. Funny means it makes you laugh: That joke was funny. So never say: The movie was fun if you mean it made you laugh. Say: The movie was funny.", "visual_prompt": "laughing emoji vs happy emoji comparison, modern flat design, yellow and purple", "caption": "FUN = enjoyable | FUNNY = makes you laugh"},
        {"title": "Quick Review", "narration": "Let us review today's mistakes. Tell needs an object. For is for duration, since is for a point in time. Make a mistake, do homework. Fun means enjoyable, funny means it makes you laugh. Now you will never make these mistakes again!", "visual_prompt": "summary checklist with green ticks, success theme, bright and motivating", "caption": "4 mistakes fixed - you are improving!"},
    ],
    "dialogue": [
        {"title": "Scene: At a Coffee Shop", "narration": "Listen to this conversation. Customer: Excuse me, could I get a large coffee please? Barista: Of course! Would you like anything else? Customer: Actually, yes. Could you add some oat milk? Barista: Absolutely! That will be four fifty.", "visual_prompt": "cozy modern coffee shop, two people at counter, warm lighting, urban atmosphere", "caption": "Ordering politely: Could I get... / Would you like..."},
        {"title": "Key Phrases", "narration": "Let us look at the key phrases. Could I get is a polite way to order. It is more polite than: Give me a coffee. Would you like is used to offer something. Actually is used to add something or change your mind. Absolutely is a strong way to say yes.", "visual_prompt": "speech bubbles with key phrases highlighted, bright educational style, friendly colors", "caption": "Could I get / Would you like / Absolutely"},
        {"title": "Your Turn: Practice", "narration": "Now you try. Imagine you are at a restaurant. You want to order pasta and ask if they have vegetarian options. Use these phrases: Could I get, Do you have, and Actually. Pause the video and practice out loud. I will wait.", "visual_prompt": "restaurant setting with menu, person thinking, practice prompt style, warm inviting", "caption": "Pause and practice - speak out loud!"},
        {"title": "More Useful Phrases", "narration": "Here are more phrases for ordering and shopping. To get attention: Excuse me. To ask for help: Could you help me with this? To confirm: So that is one pasta, correct? To thank: Thank you so much, I appreciate it.", "visual_prompt": "various shopping and dining scenes collage, vibrant city life, real-world context", "caption": "Excuse me / Could you help / I appreciate it"},
        {"title": "Wrap Up", "narration": "Great work today! You learned how to have a polite conversation when ordering or shopping. Remember: being polite in English means using could, would, and please. Practice these phrases in real life and you will sound much more natural!", "visual_prompt": "happy confident person giving thumbs up, success and achievement theme, bright cheerful", "caption": "Sound natural - use polite phrases!"},
    ],
    "daily vocabulary": [
        {"title": "Word 1: Accomplish", "narration": "Today we start with accomplish. It means to successfully complete something. For example: She accomplished her goal of running a marathon. Or: I accomplished a lot today. The noun form is accomplishment. I am proud of my accomplishments.", "visual_prompt": "person reaching mountain summit, achievement and success theme, dramatic sky, inspiring", "caption": "Accomplish - to successfully complete something"},
        {"title": "Word 2: Tremendous", "narration": "Next: tremendous. It means very great or impressive. For example: The concert was a tremendous success. Or: She showed tremendous courage. You can use it instead of very big or very impressive. It makes your English sound much more advanced.", "visual_prompt": "massive impressive waterfall or landmark, stunning scale, vibrant nature photography style", "caption": "Tremendous - very great or impressive"},
        {"title": "Word 3: Reluctant", "narration": "Word three is reluctant. It means unwilling to do something. For example: He was reluctant to admit his mistake. Or: She reluctantly agreed to help. This is a great word to use instead of did not want to.", "visual_prompt": "person hesitating at crossroads, uncertainty mood, soft dramatic lighting, thoughtful atmosphere", "caption": "Reluctant - unwilling, hesitant"},
        {"title": "Word 4: Dedicate", "narration": "Our fourth word is dedicate. It means to give time and effort to something. For example: She dedicated her life to teaching. Or: I dedicate this song to my mother. The adjective is dedicated: He is a dedicated student.", "visual_prompt": "focused student or professional working hard, dedication and focus theme, warm productive atmosphere", "caption": "Dedicate - to commit time and effort"},
        {"title": "Review Challenge", "narration": "Time for a challenge! Can you use all four words in sentences? Accomplish, tremendous, reluctant, dedicate. Try: She accomplished something tremendous despite being reluctant at first, because she was dedicated. Did you follow that? Replay and listen again if needed!", "visual_prompt": "brain with lightbulb, challenge and thinking theme, colorful comic style, energetic", "caption": "4 advanced words - use them today!"},
    ],
    "short story": [
        {"title": "The Unexpected Upgrade", "narration": "Here is today's story. Marcus was at the airport, exhausted after a long business trip. He checked in for his flight home and expected his usual economy seat. But the agent smiled and said: Mr Marcus, we are upgrading you to first class today.", "visual_prompt": "busy airport terminal, tired businessman at check-in counter, agent smiling, realistic scene", "caption": "Upgrade - to move to a better version"},
        {"title": "First Class Surprise", "narration": "Marcus could not believe it. He had never flown first class. He settled into the wide leather seat and a flight attendant offered him a glass of champagne. He felt out of place at first, but gradually relaxed. Gradually means slowly, little by little.", "visual_prompt": "luxurious airplane first class cabin, champagne, wide comfortable seats, soft warm lighting", "caption": "Gradually - slowly, little by little"},
        {"title": "A New Friendship", "narration": "Sitting next to Marcus was Elena, a novelist. They began chatting and discovered they both grew up in the same small town. What a coincidence! A coincidence is when two things happen by chance with no planning. They talked the entire flight.", "visual_prompt": "two passengers laughing and talking on plane, warm friendly atmosphere, storytelling mood", "caption": "Coincidence - things happening by chance"},
        {"title": "The Lesson", "narration": "When they landed, Elena gave Marcus her book. She had written it about their hometown. On the first page she wrote: To Marcus, proof that coincidences are just waiting to happen. Marcus smiled. That upgrade had changed his day completely.", "visual_prompt": "person holding book with handwritten note, emotional meaningful moment, soft warm lighting", "caption": "Proof - evidence that something is true"},
        {"title": "Story Vocabulary Review", "narration": "Wonderful story! Let us review the vocabulary. Upgrade means to move to something better. Gradually means slowly, little by little. Coincidence means things happening by chance. And proof means evidence. Try to use these words today!", "visual_prompt": "book opening with words flying out, magical learning atmosphere, colorful and inspiring", "caption": "Upgrade / Gradually / Coincidence / Proof"},
    ],
}

FALLBACK_TOPICS = ["common mistakes", "dialogue", "daily vocabulary", "short story"]


def _template_plan(level: str, topic: str) -> VideoPlan:
    key = topic.lower().strip()
    slides_data = TEMPLATES.get(key) or TEMPLATES.get(random.choice(FALLBACK_TOPICS))
    slides = [Slide(**s) for s in slides_data]
    hook = random.choice(TITLE_HOOKS)
    title = f"{hook}: {LEVEL_LABELS.get(level, level)} English - {topic.title()}"
    description = f"Learn English {topic} for {LEVEL_LABELS.get(level, level)} level students.\n\n#LearnEnglish #{level}English #ESL"
    tags = TAGS_BASE + [f"{level} english", topic.lower(), LEVEL_LABELS.get(level, level).lower()]
    return VideoPlan(level=level, topic=topic, title=title, description=description, tags=tags, slides=slides)


def pick_daily_topic() -> str:
    weights = [3, 2, 2, 2, 1, 2, 1, 2, 2, 1, 1, 1, 1, 1, 1]
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