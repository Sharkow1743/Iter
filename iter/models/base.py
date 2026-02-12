from datetime import datetime
from typing import Annotated, Any, cast, Optional
from pydantic import BaseModel, ConfigDict, BeforeValidator, model_validator, computed_field
from pydantic.alias_generators import to_camel

def validate_datetime(v: Any):
    if isinstance(v, str) and "+" in v:
        parts = v.split("+")
        if len(parts[-1]) <= 2:
            v = f"{parts[0]}+{parts[-1].zfill(2)}:00"
    return v

PostgresDateTime = Annotated[datetime, BeforeValidator(validate_datetime)]

class IterBaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, serialize_by_alias=True)

    @model_validator(mode='before')
    @classmethod
    def unwrap_data_envelope(cls, data: Any) -> Any:
        if (not isinstance(data, dict)
            or len(data) != 1): return data

        first_key = next(iter(data))
        first_value = data[first_key]

        if first_key not in ['data', 'error']: return data

        return first_value

class Error(IterBaseModel):
    code: str
    message: str
    retry_after: Optional[int] = None
    found: Optional[dict] = None