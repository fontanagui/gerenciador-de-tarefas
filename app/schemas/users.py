from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    username: str = Field(min_length=1, max_length=70)
    email: EmailStr = Field(max_length=255)


class UserCreate(UserUpdate):
    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("username não pode ser vazio")
        return value

    # Preserve password whitespace: it is part of the user's credential.
    password: str = Field(min_length=8, max_length=128)

    model_config = ConfigDict(str_strip_whitespace=False, extra="forbid")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
