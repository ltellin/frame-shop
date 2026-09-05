"""design as fabrication spec: drop artwork table, add images, provenance, types

Revision ID: 6c2d60a84d33
Revises: d086bfaa4cdb
Create Date: 2026-09-05

Folds the former Artwork table onto the Design (base dimensions + optional art
metadata), makes a Design able to be a loose draft (nullable order_id, new
nullable customer_id), adds `type` / `provenance` / `quantity`, an image table,
and order due-date / PO fields.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "6c2d60a84d33"
down_revision: str | Sequence[str] | None = "d086bfaa4cdb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- new image table -------------------------------------------------
    op.create_table(
        "design_image",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("design_id", sa.Integer(), nullable=False),
        sa.Column("image_id", sa.String(length=64), nullable=False),
        sa.Column("filename", sa.String(length=300), nullable=True),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["design_id"], ["design.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("design_image", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_design_image_image_id"), ["image_id"], unique=True)

    # --- customer / order additions -----------------------------------
    with op.batch_alter_table("customer", schema=None) as batch_op:
        batch_op.add_column(sa.Column("is_trade", sa.Boolean(), server_default="0", nullable=False))
    with op.batch_alter_table("order", schema=None) as batch_op:
        batch_op.add_column(sa.Column("due_date", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("po_number", sa.String(length=80), nullable=True))

    with op.batch_alter_table("design_component", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("provenance", sa.String(length=20), server_default="shop", nullable=False)
        )

    # --- design: add the new columns (keep artwork_id for the copy) -----
    with op.batch_alter_table("design", schema=None) as batch_op:
        batch_op.add_column(sa.Column("customer_id", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("type", sa.String(length=30), server_default="framing", nullable=False)
        )
        batch_op.add_column(
            sa.Column("base_ref", sa.String(length=20), server_default="art", nullable=False)
        )
        batch_op.add_column(sa.Column("base_width_in", sa.Numeric(7, 3), nullable=True))
        batch_op.add_column(sa.Column("base_height_in", sa.Numeric(7, 3), nullable=True))
        batch_op.add_column(sa.Column("art_title", sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column("art_description", sa.String(length=2000), nullable=True))
        batch_op.add_column(sa.Column("art_type", sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column("art_depth_in", sa.Numeric(7, 3), nullable=True))
        batch_op.add_column(sa.Column("art_notes", sa.String(length=2000), nullable=True))
        batch_op.add_column(sa.Column("quantity", sa.Integer(), server_default="1", nullable=False))

    # --- copy artwork -> design for existing rows --------------------
    op.execute(
        """
        UPDATE design SET
            art_title = (SELECT title FROM artwork WHERE artwork.id = design.artwork_id),
            art_description = (SELECT description FROM artwork WHERE artwork.id = design.artwork_id),
            art_notes = (SELECT notes FROM artwork WHERE artwork.id = design.artwork_id),
            art_depth_in = (SELECT depth_in FROM artwork WHERE artwork.id = design.artwork_id),
            base_width_in = (SELECT width_in FROM artwork WHERE artwork.id = design.artwork_id),
            base_height_in = (SELECT height_in FROM artwork WHERE artwork.id = design.artwork_id)
        WHERE design.artwork_id IS NOT NULL
        """
    )
    # Copy the design's customer down from its order, where it has one.
    op.execute(
        """
        UPDATE design SET
            customer_id = (SELECT customer_id FROM "order" WHERE "order".id = design.order_id)
        WHERE design.order_id IS NOT NULL
        """
    )

    # --- design: drop artwork_id, relax order_id, wire customer FK -----
    with op.batch_alter_table("design", schema=None) as batch_op:
        batch_op.alter_column("order_id", existing_type=sa.INTEGER(), nullable=True)
        batch_op.drop_column("artwork_id")
        batch_op.create_foreign_key("fk_design_customer_id", "customer", ["customer_id"], ["id"])

    op.drop_table("artwork")


def downgrade() -> None:
    op.create_table(
        "artwork",
        sa.Column("id", sa.INTEGER(), nullable=False),
        sa.Column("order_id", sa.INTEGER(), nullable=False),
        sa.Column("title", sa.VARCHAR(length=300), nullable=False),
        sa.Column("description", sa.VARCHAR(length=2000), nullable=True),
        sa.Column("width_in", sa.NUMERIC(precision=7, scale=3), nullable=False),
        sa.Column("height_in", sa.NUMERIC(precision=7, scale=3), nullable=False),
        sa.Column("depth_in", sa.NUMERIC(precision=7, scale=3), nullable=True),
        sa.Column("notes", sa.VARCHAR(length=2000), nullable=True),
        sa.Column(
            "created_at",
            sa.DATETIME(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["order_id"], ["order.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("design", schema=None) as batch_op:
        batch_op.add_column(sa.Column("artwork_id", sa.INTEGER(), nullable=True))
        batch_op.drop_constraint("fk_design_customer_id", type_="foreignkey")
        batch_op.drop_column("quantity")
        batch_op.drop_column("art_notes")
        batch_op.drop_column("art_depth_in")
        batch_op.drop_column("art_type")
        batch_op.drop_column("art_description")
        batch_op.drop_column("art_title")
        batch_op.drop_column("base_height_in")
        batch_op.drop_column("base_width_in")
        batch_op.drop_column("base_ref")
        batch_op.drop_column("type")
        batch_op.drop_column("customer_id")

    with op.batch_alter_table("design_component", schema=None) as batch_op:
        batch_op.drop_column("provenance")
    with op.batch_alter_table("order", schema=None) as batch_op:
        batch_op.drop_column("po_number")
        batch_op.drop_column("due_date")
    with op.batch_alter_table("customer", schema=None) as batch_op:
        batch_op.drop_column("is_trade")

    with op.batch_alter_table("design_image", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_design_image_image_id"))
    op.drop_table("design_image")
