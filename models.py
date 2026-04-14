"""
Pydantic models for validating structured responses from Claude.
Forces predictable shapes so the UI never breaks on creative LLM output.
"""

from pydantic import BaseModel, Field, field_validator


class Dimension(BaseModel):
    keyword_match: int = Field(ge=0, le=100)
    experience_level: int = Field(ge=0, le=100)
    skills_coverage: int = Field(ge=0, le=100)
    role_title_alignment: int = Field(ge=0, le=100)


class KeywordCategory(BaseModel):
    matched: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)


class Suggestion(BaseModel):
    gap: str
    action: str


class ATSReport(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    dimensions: Dimension
    technical_skills: KeywordCategory = Field(default_factory=KeywordCategory)
    tools_and_frameworks: KeywordCategory = Field(default_factory=KeywordCategory)
    soft_skills: KeywordCategory = Field(default_factory=KeywordCategory)
    suggestions: list[Suggestion] = Field(default_factory=list)
    verdict: str = ""

    @field_validator("overall_score", mode="before")
    @classmethod
    def clamp_score(cls, v: int) -> int:
        """Clamp score to 0-100 even if Claude goes out of range."""
        return max(0, min(100, int(v)))

    def to_dict(self) -> dict:
        """Return a plain dict for session saving and UI rendering."""
        return self.model_dump()
