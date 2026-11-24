from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Meter = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
Code = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class SubmitSwitch(BaseModel):
    model_config = ConfigDict(extra='forbid')
    code: Code
    old_meter: Meter
    new_meter: Meter
    handover_hour: int


class ApproveSwitch(BaseModel):
    model_config = ConfigDict(extra='forbid')
    code: Code
