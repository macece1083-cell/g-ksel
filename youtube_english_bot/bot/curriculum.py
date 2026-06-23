CURRICULUM = [
    {"unit": 1, "topic": "Hello", "outcomes": ["Greet people and introduce yourself", "Ask and answer questions about names and ages", "Use basic classroom language"]},
    {"unit": 1, "topic": "Hello", "outcomes": ["Say the alphabet and spell names", "Count numbers 1-20", "Use 'What is your name?' and 'How old are you?'"]},
    {"unit": 2, "topic": "My Town", "outcomes": ["Name places in town: school, park, hospital, market", "Ask for and give directions", "Use 'Where is the...?' and 'It is next to/near/between'"]},
    {"unit": 2, "topic": "My Town", "outcomes": ["Describe your neighbourhood", "Use prepositions of place", "Talk about things you can do in town"]},
    {"unit": 3, "topic": "Games and Hobbies", "outcomes": ["Name common hobbies and games", "Talk about what you like and dislike doing", "Use 'I like/love/enjoy + verb-ing'"]},
    {"unit": 3, "topic": "Games and Hobbies", "outcomes": ["Ask about others hobbies", "Use 'Do you like...?' and 'Yes I do / No I do not'", "Describe your free time activities"]},
    {"unit": 4, "topic": "My Body", "outcomes": ["Name body parts", "Describe physical appearance", "Use 'He/She has got...' for descriptions"]},
    {"unit": 4, "topic": "My Body", "outcomes": ["Talk about health problems", "Use 'I have got a headache/stomachache'", "Give simple health advice"]},
    {"unit": 5, "topic": "Cooking", "outcomes": ["Name common foods and ingredients", "Use countable and uncountable nouns", "Use 'some' and 'any' with food"]},
    {"unit": 5, "topic": "Cooking", "outcomes": ["Follow simple recipe instructions", "Use imperative forms: add, mix, cut, boil", "Talk about favourite foods"]},
    {"unit": 6, "topic": "Emotions", "outcomes": ["Name basic emotions: happy, sad, angry, scared, surprised, bored", "Ask and answer 'How do you feel?'", "Describe why you feel a certain way"]},
    {"unit": 6, "topic": "Emotions", "outcomes": ["Use adjectives to describe feelings", "Talk about situations that cause emotions", "Use 'I feel... because...'"]},
    {"unit": 7, "topic": "Movie Time", "outcomes": ["Name movie genres: action, comedy, horror, animation", "Express opinions about movies", "Use 'I think... / I believe... / In my opinion...'"]},
    {"unit": 7, "topic": "Movie Time", "outcomes": ["Talk about favourite actors and movies", "Use simple present to describe movie plots", "Ask and answer questions about movies"]},
    {"unit": 8, "topic": "Seasons and Weather", "outcomes": ["Name the four seasons", "Describe weather conditions", "Use 'It is sunny/rainy/snowy/windy'"]},
    {"unit": 8, "topic": "Seasons and Weather", "outcomes": ["Talk about activities in different seasons", "Use present continuous for current weather", "Compare seasons using adjectives"]},
]


def get_lesson(day_number: int) -> dict:
    idx = (day_number - 1) % len(CURRICULUM)
    lesson = CURRICULUM[idx]
    return {
        "unit": lesson["unit"],
        "topic": lesson["topic"],
        "outcome": lesson["outcomes"][(day_number - 1) // len(CURRICULUM) % len(lesson["outcomes"])],
        "lesson_number": day_number,
    }
