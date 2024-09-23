from pydantic import BaseModel


class SnippetCreate(BaseModel):
    title: str
    code: str
    is_public: bool = True


class SnippetResponse(BaseModel):
    id: int
    uuid: str
    title: str
    code: str
    is_public: bool = True
