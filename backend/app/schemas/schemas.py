# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---

# --- Third-party ---
from pydantic import BaseModel, ConfigDict

# --- Project ---

# =============================================================================
# CONFIGURATION
# =============================================================================
class Country(BaseModel):
    country_id: int
    country_name: str
    code: str
    continent: str | None = None

    model_config = ConfigDict(from_attributes=True)


class Indicator(BaseModel):
    indicator_name: str

    model_config = ConfigDict(from_attributes=True)


class UnifiedData(BaseModel):
    country_name: str | None = None
    year: int | None = None
    value: float | None = None
    code: str | None = None

    model_config = ConfigDict(from_attributes=True)


class Data(BaseModel):
    iso_a3: str
    name: str
    value: float | None = None

    model_config = ConfigDict(from_attributes=True)


class IndicatorGroup(BaseModel):
    category: str
    indicators: list[Indicator]

    model_config = ConfigDict(from_attributes=True)
