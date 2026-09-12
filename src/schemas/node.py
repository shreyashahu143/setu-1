from pydantic import BaseModel, Field
from typing import List, Literal

class StreetInsightNode(BaseModel):
    area_name: str = Field(description="Broad locality, e.g., Sitabuldi, Chitaroli, Itwari, Dharampeth")
    sub_lane_or_landmark: str = Field(description="Specific sub-lane, e.g., Modi No. 2, Modi No. 3")
    specialty_goods_or_food: List[str] = Field(description="Items/services traded in this lane")
    price_band: str = Field(description="Typical street price range, e.g., 'Budget (₹1,200 - ₹1,800)'")
    bargaining_tactics: str = Field(description="Counter-offer percentages, peak negotiation times")
    accessibility_notes: str = Field(description="Two-wheeler access only, parking availability")
    category: Literal["Shopping", "Tech Repair", "Food", "Culture", "Services"]
    
    # Trust and Quarantine metadata
    status: Literal["verified", "unverified", "quarantine"] = "verified"
    mention_frequency: int = Field(default=1)
    upvote_weight: int = Field(default=0)
    source_threads: List[str] = Field(default_factory=list)
