from pydantic import BaseModel,Field
from typing import List,Optional,Literal


class Extract(BaseModel):
    content: str = Field(..., description="The handwritten content extracted from the image")
    roll_number: int = Field(..., description="The roll number found on the image")
    page_number: int = Field(..., description="The page number found on the image")
class ChoiceBlock(BaseModel):
    choice_id: str = Field(description="Identifier like 'A', 'B', 'OR-1'")
    question_text: str = Field(description="Text of this choice in LaTeX")
    model_answer: str = Field(description="Reference answer for this choice")
    marks: float = Field(description="Marks for this choice")
    diagram_description: str = Field(default="")



class SubQuestion(BaseModel):
    question_number: str
    question_text: str
    marks: float
    choices: List["ChoiceBlock"] = Field(default_factory=list)
    diagram_description: str = ""
class QuestionDetail(BaseModel):
    question_number: str
    question_type: Literal[
        "MCQ",
        "Subjective",
        "AssertionReason",
        "CaseStudy"
    ]
    question_text: str
    marks: float
    choices: List["ChoiceBlock"] = Field(default_factory=list)
    sub_questions: List[SubQuestion] = Field(default_factory=list)
    diagram_description: str = ""

class QuestionPaper(BaseModel):
    questions: List[QuestionDetail] = Field(description="A list of all questions found in the paper.")
    total_max_marks: float = Field(description="The calculated total maximum marks for the entire paper.")
