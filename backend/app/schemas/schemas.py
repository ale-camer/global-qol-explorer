# =============================================================================
# IMPORTS
# =============================================================================
# --- Standard library ---

# --- Third-party ---
from pydantic import BaseModel

# --- Project ---

# =============================================================================
# CONFIGURATION
# =============================================================================
class Country(BaseModel):
    country_id: int
    country_name: str
    code: str
    continent: str | None = None

    class Config:
        from_attributes = True

class Indicator(BaseModel):
    indicator_name: str

    class Config:
        from_attributes = True

class UnifiedData(BaseModel):
    country_name: str | None = None
    year: int | None = None
    value: float | None = None
    code: str | None = None

    class Config:
        from_attributes = True

class Data(BaseModel):
    iso_a3: str
    name: str
    value: float | None = None

    class Config:
        from_attributes = True

class IndicatorGroup(BaseModel):
    category: str
    indicators: list[Indicator]

    class Config:
        from_attributes = True        