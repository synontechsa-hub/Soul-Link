"""v156_unified_soul_pillars

Revision ID: v156_unified_pillars
Revises: v156_fresh
Create Date: 2026-02-20

Migrates soul_pillars from the old 'Three Pillars' schema to the
v1.5.6 Unified Schema that mirrors the Standard JSON format 1:1.

Old columns removed:
  - personality, background, identity_pillar, aesthetic_pillar,
    interaction_engine, llm_instruction_override

New columns added:
  - identity, aesthetic, systems_config, routine, inventory,
    relationships, lore_associations, interaction_system, prompts

The 'routines' and 'meta_data' columns are unchanged.

Downgrade path restores the old columns and drops the new ones.
Data is NOT migrated (old data was never properly populated under
the old schema — this was the root cause of the v1.5.6 seeding audit failure).
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'v156_unified_pillars'
down_revision: Union[str, Sequence[str], None] = 'v156_fresh'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. DROP LEGACY COLUMNS ────────────────────────────────────────────────
    # These were the "Three Pillars" fields that caused schema mismatch.
    # They were never reliably populated, so data loss is not a concern.
    with op.batch_alter_table('soul_pillars') as batch_op:
        batch_op.drop_column('personality')
        batch_op.drop_column('background')
        batch_op.drop_column('identity_pillar')
        batch_op.drop_column('aesthetic_pillar')
        batch_op.drop_column('interaction_engine')
        batch_op.drop_column('llm_instruction_override')

    # ── 2. ADD NEW UNIFIED COLUMNS ────────────────────────────────────────────
    # Each column directly maps to a top-level key in the v1.5.6 Standard JSON.
    with op.batch_alter_table('soul_pillars') as batch_op:
        batch_op.add_column(sa.Column('identity', sa.JSON(), nullable=True, server_default='{}'))
        batch_op.add_column(sa.Column('aesthetic', sa.JSON(), nullable=True, server_default='{}'))
        batch_op.add_column(sa.Column('systems_config', sa.JSON(), nullable=True, server_default='{}'))
        batch_op.add_column(sa.Column('routine', sa.JSON(), nullable=True, server_default='{}'))
        batch_op.add_column(sa.Column('inventory', sa.JSON(), nullable=True, server_default='{}'))
        batch_op.add_column(sa.Column('relationships', sa.JSON(), nullable=True, server_default='{}'))
        batch_op.add_column(sa.Column('lore_associations', sa.JSON(), nullable=True, server_default='{}'))
        batch_op.add_column(sa.Column('interaction_system', sa.JSON(), nullable=True, server_default='{}'))
        batch_op.add_column(sa.Column('prompts', sa.JSON(), nullable=True, server_default='{}'))


def downgrade() -> None:
    # ── 1. DROP NEW UNIFIED COLUMNS ───────────────────────────────────────────
    with op.batch_alter_table('soul_pillars') as batch_op:
        batch_op.drop_column('prompts')
        batch_op.drop_column('interaction_system')
        batch_op.drop_column('lore_associations')
        batch_op.drop_column('relationships')
        batch_op.drop_column('inventory')
        batch_op.drop_column('routine')
        batch_op.drop_column('systems_config')
        batch_op.drop_column('aesthetic')
        batch_op.drop_column('identity')

    # ── 2. RESTORE LEGACY COLUMNS ─────────────────────────────────────────────
    with op.batch_alter_table('soul_pillars') as batch_op:
        batch_op.add_column(sa.Column('personality', sa.String(length=2000), nullable=True))
        batch_op.add_column(sa.Column('background', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('identity_pillar', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('aesthetic_pillar', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('interaction_engine', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('llm_instruction_override', sa.JSON(), nullable=True))
