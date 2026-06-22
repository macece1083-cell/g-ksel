from dataclasses import dataclass, field


@dataclass
class Slide:
    title: str
    narration: str
    visual_prompt: str
    caption: str


@dataclass
class VideoPlan:
    level: str
    topic: str
    title: str
    description: str
    tags: list[str]
    slides: list[Slide] = field(default_factory=list)

    @property
    def script(self) -> str:
        return "\n\n".join(slide.narration for slide in self.slides)
