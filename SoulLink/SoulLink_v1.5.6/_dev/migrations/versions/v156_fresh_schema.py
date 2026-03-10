"""v156_fresh_schema

Revision ID: v156_fresh
Revises: 
Create Date: 2026-02-18

Single clean migration for v1.5.6 schema.
Replaces the old 3-migration chain (baseline → split_soul_pillars → add_index).
Run on a fresh (nuked) database only.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = 'v156_fresh'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ────────────────────────────────────────────────────────────────
    op.create_table('users',
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(length=36), nullable=False),
        sa.Column('username', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('display_name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column('bio', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('account_tier', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False, server_default='free'),
        sa.Column('gems', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('energy', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('lifetime_tokens_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_ad_at', sa.DateTime(), nullable=True),
        sa.Column('last_energy_refill', sa.DateTime(), nullable=False),
        sa.Column('current_location', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False, server_default='linkside_apartment'),
        sa.Column('current_time_slot', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False, server_default='morning'),
        sa.Column('subscription_status', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column('subscription_start', sa.DateTime(), nullable=True),
        sa.Column('subscription_end', sa.DateTime(), nullable=True),
        sa.Column('total_ads_watched', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ad_cooldown_until', sa.DateTime(), nullable=True),
        sa.Column('stability_overdrive_until', sa.DateTime(), nullable=True),
        sa.Column('stripe_customer_id', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column('stripe_subscription_id', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('user_id')
    )

    # ── souls ────────────────────────────────────────────────────────────────
    op.create_table('souls',
        sa.Column('soul_id', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False, server_default='A mysterious soul...'),
        sa.Column('portrait_url', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False, server_default='/assets/images/souls/default_01.jpeg'),
        sa.Column('archetype', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column('version', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False, server_default='1.5.6'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('soul_id')
    )

    # ── soul_pillars ─────────────────────────────────────────────────────────
    op.create_table('soul_pillars',
        sa.Column('soul_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('routines', sa.JSON(), nullable=True),
        sa.Column('personality', sqlmodel.sql.sqltypes.AutoString(length=2000), nullable=True),
        sa.Column('background', sa.Text(), nullable=True),
        sa.Column('identity_pillar', sa.JSON(), nullable=True),
        sa.Column('aesthetic_pillar', sa.JSON(), nullable=True),
        sa.Column('interaction_engine', sa.JSON(), nullable=True),
        sa.Column('llm_instruction_override', sa.JSON(), nullable=True),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['soul_id'], ['souls.soul_id'], ),
        sa.PrimaryKeyConstraint('soul_id')
    )

    # ── soul_states ──────────────────────────────────────────────────────────
    op.create_table('soul_states',
        sa.Column('soul_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('current_location_id', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False, server_default='soul_plaza'),
        sa.Column('energy', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('mood', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False, server_default='neutral'),
        sa.Column('anxiety_level', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('performance_mode', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['soul_id'], ['souls.soul_id'], ),
        sa.PrimaryKeyConstraint('soul_id')
    )

    # ── locations ────────────────────────────────────────────────────────────
    op.create_table('locations',
        sa.Column('location_id', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('display_name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('category', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('music_track', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False, server_default='ambient_city_loop.mp3'),
        sa.Column('image_url', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('system_modifiers', sa.JSON(), nullable=True),
        sa.Column('system_prompt_anchors', sa.JSON(), nullable=True),
        sa.Column('game_logic', sa.JSON(), nullable=True),
        sa.Column('lore', sa.JSON(), nullable=True),
        sa.Column('source_metadata', sa.JSON(), nullable=True),
        sa.Column('min_intimacy', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('location_id')
    )

    # ── soul_relationships ───────────────────────────────────────────────────
    op.create_table('soulrelationship',
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(length=36), nullable=False),
        sa.Column('soul_id', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('intimacy_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('intimacy_tier', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False, server_default='STRANGER'),
        sa.Column('current_location', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column('is_architect', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('nsfw_unlocked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_interaction', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['soul_id'], ['souls.soul_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('user_id', 'soul_id')
    )

    # ── conversations ────────────────────────────────────────────────────────
    op.create_table('conversations',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(length=36), nullable=False),
        sa.Column('soul_id', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('location_id', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['soul_id'], ['souls.soul_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_user_soul', 'conversations', ['user_id', 'soul_id'])


def downgrade() -> None:
    op.drop_index('ix_conversations_user_soul', table_name='conversations')
    op.drop_table('conversations')
    op.drop_table('soulrelationship')
    op.drop_table('locations')
    op.drop_table('soul_states')
    op.drop_table('soul_pillars')
    op.drop_table('souls')
    op.drop_table('users')
