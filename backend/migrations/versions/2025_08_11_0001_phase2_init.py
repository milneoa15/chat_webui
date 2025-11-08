"""Phase 2 base schema."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "2025_08_11_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "installed_models",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False, unique=True),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("quantization", sa.String(), nullable=True),
        sa.Column("context_length", sa.Integer(), nullable=True),
        sa.Column("parameter_count", sa.Float(), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("checksum_sha256", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_loaded_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_installed_models_slug", "installed_models", ["slug"], unique=True)
    op.create_index(
        "ix_installed_models_is_active",
        "installed_models",
        ["is_active"],
        unique=False,
    )

    op.create_table(
        "runtime_config",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("context_length", sa.Integer(), nullable=False),
        sa.Column("gpu_layers", sa.Integer(), nullable=True),
        sa.Column("cpu_threads", sa.Integer(), nullable=False),
        sa.Column("eval_batch_size", sa.Integer(), nullable=False),
        sa.Column("kv_cache_placement", sa.String(), nullable=False),
        sa.Column("use_mmap", sa.Boolean(), nullable=False),
        sa.Column("keep_in_memory", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("runtime_config")
    op.drop_index("ix_installed_models_is_active", table_name="installed_models")
    op.drop_index("ix_installed_models_slug", table_name="installed_models")
    op.drop_table("installed_models")
