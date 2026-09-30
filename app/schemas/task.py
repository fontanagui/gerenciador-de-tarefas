from pydantic import BaseModel, ConfigDict, Field, model_validator


class TaskBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=150)
    descricao: str | None = Field(default=None, max_length=350)
    concluida: bool = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str | None = Field(default=None, min_length=1, max_length=150)
    descricao: str | None = Field(default=None, max_length=350)
    concluida: bool | None = None

    @model_validator(mode="after")
    def validate_non_nullable_fields(self):
        for name in ("title", "concluida"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} não pode ser nulo")
        return self


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True, extra="forbid")
    id: int
    user_id: int
