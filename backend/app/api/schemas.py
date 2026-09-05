"""HTTP request/response schemas.

The rich Design read model is a plain dict built in the service layer; these
models cover request payloads and the simple list responses.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None
    notes: str | None = None
    is_trade: bool = False


class CustomerRead(BaseModel):
    id: int
    name: str
    phone: str | None = None
    email: str | None = None


class OrderCreate(BaseModel):
    customer_id: int
    due_date: date | None = None
    po_number: str | None = None


class ArtInput(BaseModel):
    title: str | None = None
    description: str | None = None
    art_type: str | None = None
    depth_in: str | float | None = None
    notes: str | None = None


class ComponentInput(BaseModel):
    id: int | None = None
    kind: str
    params: dict = Field(default_factory=dict)
    layer_role: str | None = None
    product_id: int | None = None
    provenance: str | None = None  # shop | customer
    parent_index: int | None = None


class DesignStart(BaseModel):
    name: str | None = None
    type: str | None = None
    base_ref: str | None = None
    base_width_in: str | float | None = None
    base_height_in: str | float | None = None
    art: ArtInput | None = None
    quantity: int | None = None
    customer_id: int | None = None
    order_id: int | None = None
    seed_starter: bool = False
    components: list[ComponentInput] | None = None


class DesignPatch(BaseModel):
    name: str | None = None
    status: str | None = None
    type: str | None = None
    base_ref: str | None = None
    base_width_in: str | float | None = None
    base_height_in: str | float | None = None
    art: ArtInput | None = None
    quantity: int | None = None
    customer_id: int | None = None
    components: list[ComponentInput] | None = None


class NestedCustomer(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None


class AddToOrder(BaseModel):
    order_id: int | None = None
    customer_id: int | None = None
    customer: NestedCustomer | None = None
    due_date: date | None = None
    po_number: str | None = None
