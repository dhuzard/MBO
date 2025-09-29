from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class BehaviorRequest(BaseModel):
    identifier: str = Field(..., description="CURIE or IRI for the behavior instance")
    behavior_class: str = Field(..., description="IRI of the behavior class")
    performed_by: str = Field(..., description="Agent performing the behavior")
    has_start: str = Field(..., description="ISO8601 timestamp with timezone")
    has_end: Optional[str] = Field(None, description="ISO8601 timestamp with timezone")
    has_target: Optional[str] = Field(None, description="Target entity IRI/CURIE")
    has_duration: Optional[float] = Field(None, description="Duration in seconds")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    distance_to_target: Optional[float] = Field(None)
    heading_to_target: Optional[float] = Field(None)
    evidence: Optional[str] = Field(None)


class BehaviorResponse(BehaviorRequest):
    uid: str


class BehaviorClassResponse(BaseModel):
    iri: str
    label: Optional[str]
    comment: Optional[str]
    description: Optional[str]
    parents: List[str]
    category: Optional[str]


class PrefixUpdate(BaseModel):
    prefix: str
    iri: str


class ValidationResponse(BaseModel):
    conforms: bool
    report: str


class ExportResponse(BaseModel):
    ttl: str
    prefixes: Dict[str, str]
