from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class RawTransaction(BaseModel):
    date: str = Field(..., description="Transaction date (YYYY-MM-DD or as parsed)")
    description: str = Field(..., description="Raw description from the statement")
    amount: float = Field(..., description="Negative = debit, positive = credit")
    balance: Optional[float] = Field(None, description="Running balance if available")
    source_file: Optional[str] = Field(None, description="Originating filename")


class EnrichedTransaction(BaseModel):
    date: str
    description: str
    amount: float
    balance: Optional[float] = None
    merchant: str = Field(..., description="Cleaned merchant name")
    category: str = Field(..., description="Assigned category")
    subcategory: Optional[str] = None
    emoji: str = Field(..., description="Category emoji")
    note: str = Field(..., description="Human-readable context note")
    flagged: bool = Field(False, description="True if amount is unusually high for category")
