from pydantic import BaseModel, Field
from pydantic import BaseModel, ConfigDict, Field

class TaskCreate(BaseModel):
    title: str = Field(
        min_length=1, 
        max_length=120, 
        description="任务标题", 
    )
    priority: int = Field(
        default=3,
        ge=1,
        le=5,
        description="优先级，1最高，5最低",
    )

class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
    )
    completed: bool | None = None,
    priority: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

class TaskReplace(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=120,
    )
    completed: bool
    priority: int = Field(
        ge=1,
        le=5,
    )

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    completed: bool
    priority: int

class TaskPage(BaseModel):
    items: list[TaskResponse]
    page: int
    page_size: int
    total: int