from pydantic import BaseModel


class SnippetCreate(BaseModel):
    title: str
    code: str
    is_public: bool = True


class SnippetResponse(BaseModel):
    uuid: str
    title: str
    code: str
    author_name: str
    is_public: bool = True


class SnippetDisplay(BaseModel):
    uuid: str
    title: str
    code: str
    author_name: str
    is_public: bool = True
    share_link: str
