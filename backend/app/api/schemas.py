"""HTTP request/response schemas.

Response bodies for the rich Design read model are plain dicts built in the
service layer; these models cover request payloads and the simple list
responses.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None
    notes: str | None = None


class CustomerRead(BaseModel):
    id: int
    name: str
    phone: str | None = None
    email: str | None = None


class OrderCreate(BaseModel):
    customer_id: int


class ArtworkCreate(BaseModel):
    title: str = "Untitled"
    width_in: str | float
    height_in: str | float
    depth_in: str | float | None = None
    description: str | None = None
    notes: str | None = None


class ArtworkPatch(BaseModel):
    title: str | None = None
    width_in: str | float | None = None
    height_in: str | float | None = None
    depth_in: str | float | None = None
    description: str | None = None
    notes: str | None = None


class ComponentInput(BaseModel):
    id: int | None = None
    kind: str
    params: dict = Field(default_factory=dict)
    layer_role: str | None = None
    product_id: int | None = None
    parent_index: int | None = None


class NestedCustomer(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None


class DesignStart(BaseModel):
    customer_id: int | None = None
    customer: NestedCustomer | None = None
    order_id: int | None = None
    artwork_id: int | None = None
    artwork: ArtworkCreate | None = None
    name: str | None = None
    components: list[ComponentInput] | None = None


class DesignPatch(BaseModel):
    name: str | None = None
    status: str | None = None
    artwork: ArtworkPatch | None = None
    components: list[ComponentInput] | None = None
