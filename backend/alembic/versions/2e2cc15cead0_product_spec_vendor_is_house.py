"""product spec + vendor is_house

Renames product.attributes -> product.spec (the validated physical
specification) and adds vendor.is_house (the shop's own milled mouldings).

Revision ID: 2e2cc15cead0
Revises: 6c2d60a84d33
Create Date: 2026-09-06
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "2e2cc15cead0"
down_revision: str | Sequence[str] | None = "6c2d60a84d33"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("product", schema=None) as batch_op:
        batch_op.alter_column("attributes", new_column_name="spec")
    with op.batch_alter_table("vendor", schema=None) as batch_op:
        batch_op.add_column(sa.Column("is_house", sa.Boolean(), server_default="0", nullable=False))


def downgrade() -> None:
    with op.batch_alter_table("vendor", schema=None) as batch_op:
        batch_op.drop_column("is_house")
    with op.batch_alter_table("product", schema=None) as batch_op:
        batch_op.alter_column("spec", new_column_name="attributes")
