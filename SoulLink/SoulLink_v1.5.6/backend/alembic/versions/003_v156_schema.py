"""
v1.5.6 Normandy SR-2 — Schema Migration
Drops legacy tables, creates the full v1.5.6 architecture.

What changed and why:
  - user_soul_state       → DROPPED  (replaced by link_states)
  - relationships         → DROPPED  (absorbed into link_states)
  - link_states           → CREATED  (the unified user↔soul mirror)
  - soul_pillars          → CREATED  (logic/lore/prompt data for each soul)
  - soul_states           → CREATED  (hot live data: location, mood, energy)
  - user_personas         → CREATED  (identity layer — multiple masks per user)
  - soul_memories         → CREATED  (long-term narrative storage, the Notebook)
  - user_progress         → CREATED  (achievements, lore unlocks, exploration)
  - subscription_history  → CREATED  (billing lifecycle audit trail)

Revision ID: 003_v156_schema
Revises: 002_user_world_state
Create Date: 2026-02-27
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '003_v156_schema'
down_revision = '002_user_world_state'
branch_labels = None
depends_on = None


# ---------------------------------------------------------------------------
# UPGRADE
# ---------------------------------------------------------------------------

def upgrade() -> None:

    # -----------------------------------------------------------------------
    # STEP 1: DROP LEGACY TABLES
    # Order matters — drop dependants before parents.
    # We use IF EXISTS so this is safe to run on a partially migrated DB.
    # -----------------------------------------------------------------------

    # Drop legacy user_soul_state (superseded by link_states)
    op.execute("DROP TABLE IF EXISTS user_soul_state CASCADE")

    # Drop legacy relationships table if it still exists
    # (some dev environments may have it from pre-1.5.4 migrations)
    op.execute("DROP TABLE IF EXISTS relationships CASCADE")


    # -----------------------------------------------------------------------
    # STEP 2: SOUL PILLARS
    # The logic/lore/prompt brain for each soul. Read-only in prod.
    # One row per soul, FK → souls.soul_id
    # -----------------------------------------------------------------------

    op.create_table(
        'soul_pillars',
        sa.Column('soul_id',           sa.String(50),  nullable=False),

        # v1.5.6 Unified JSON bindings — mirrors the soul JSON schema 1:1
        sa.Column('identity',          postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('aesthetic',         postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('systems_config',    postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('routine',           postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('inventory',         postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('relationships',     postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('lore_associations', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('interaction_system',postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('prompts',           postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('meta_data',         postgresql.JSONB(), nullable=False, server_default='{}'),

        # Legacy — kept for backward compat during rollout, migrate to 'routine'
        sa.Column('routines',          postgresql.JSONB(), nullable=False, server_default='{}'),

        sa.PrimaryKeyConstraint('soul_id'),
        sa.ForeignKeyConstraint(
            ['soul_id'], ['souls.soul_id'],
            ondelete='CASCADE',
            name='fk_soul_pillars_soul_id'
        ),
    )


    # -----------------------------------------------------------------------
    # STEP 3: SOUL STATES
    # Hot live data — location, mood, energy. Frequent writes.
    # One row per soul, FK → souls.soul_id
    # -----------------------------------------------------------------------

    op.create_table(
        'soul_states',
        sa.Column('soul_id',              sa.String(50),  nullable=False),
        sa.Column('current_location_id',  sa.String(100), nullable=False, server_default='soul_plaza'),
        sa.Column('energy',               sa.Integer(),   nullable=False, server_default='100'),
        sa.Column('mood',                 sa.String(50),  nullable=False, server_default='neutral'),
        sa.Column('anxiety_level',        sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('performance_mode',     sa.Integer(),   nullable=False, server_default='100'),
        sa.Column('last_updated',         sa.DateTime(),  nullable=False, server_default=sa.text('NOW()')),

        sa.PrimaryKeyConstraint('soul_id'),
        sa.ForeignKeyConstraint(
            ['soul_id'], ['souls.soul_id'],
            ondelete='CASCADE',
            name='fk_soul_states_soul_id'
        ),
    )


    # -----------------------------------------------------------------------
    # STEP 4: LINK STATES
    # The unified user↔soul mirror. Consolidates:
    #   - old Relationship (intimacy)
    #   - old UserSoulState (stability/monetization)
    # One row per user+soul pair.
    # -----------------------------------------------------------------------

    op.create_table(
        'link_states',
        sa.Column('id',                   sa.Integer(),   nullable=False),
        sa.Column('user_id',              sa.String(36),  nullable=False),
        sa.Column('soul_id',              sa.String(50),  nullable=False),

        # 1. The Volatile Mirror
        sa.Column('current_mood',         sa.String(50),  nullable=False, server_default='neutral'),
        sa.Column('current_location',     sa.String(50),  nullable=True),  # user-specific override
        sa.Column('energy_pool',          sa.Integer(),   nullable=False, server_default='100'),

        # 2. The Intimacy Ladder
        sa.Column('intimacy_score',       sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('intimacy_tier',        sa.String(20),  nullable=False, server_default='STRANGER'),

        # 3. The Mask (v1.5.6)
        sa.Column('mask_integrity',       sa.Float(),     nullable=False, server_default='1.0'),

        # 4. The Monetization Signal
        sa.Column('signal_stability',     sa.Float(),     nullable=False, server_default='100.0'),
        sa.Column('last_stability_decay', sa.DateTime(),  nullable=False, server_default=sa.text('NOW()')),

        # 5. Permissions & Gates
        sa.Column('unlocked_nsfw',        sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('is_architect',         sa.Boolean(),   nullable=False, server_default='false'),

        # 6. Flags (canon events, mechanics)
        sa.Column('flags',                postgresql.JSONB(), nullable=False, server_default='{}'),

        # 7. Stats & Timestamps
        sa.Column('total_messages_sent',  sa.Integer(),   nullable=False, server_default='0'),
        sa.Column('created_at',           sa.DateTime(),  nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_interaction',     sa.DateTime(),  nullable=False, server_default=sa.text('NOW()')),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.user_id'],
            ondelete='CASCADE',
            name='fk_link_states_user_id'
        ),
        sa.UniqueConstraint('user_id', 'soul_id', name='uq_link_state_user_soul'),
    )

    op.create_index('ix_link_states_user_id', 'link_states', ['user_id'])
    op.create_index('ix_link_states_soul_id', 'link_states', ['soul_id'])
    # Composite index — the most common query pattern (user + soul lookup)
    op.create_index('ix_link_states_user_soul', 'link_states', ['user_id', 'soul_id'])


    # -----------------------------------------------------------------------
    # STEP 5: USER PERSONAS
    # Identity layer — multiple masks per user account.
    # Souls see the user through their ACTIVE persona only.
    # -----------------------------------------------------------------------

    op.create_table(
        'user_personas',
        sa.Column('id',              sa.Integer(),   nullable=False),
        sa.Column('user_id',         sa.String(36),  nullable=False),
        sa.Column('screen_name',     sa.String(50),  nullable=False),
        sa.Column('bio',             sa.String(1000),nullable=True),
        sa.Column('age',             sa.Integer(),   nullable=True),
        sa.Column('gender',          sa.String(20),  nullable=True),

        # The Identity Anchor — a subtle detail souls fixate on to recognise
        # the user across persona swaps. e.g. "always wears a copper ring"
        sa.Column('identity_anchor', sa.String(200), nullable=True),

        sa.Column('is_active',       sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('created_at',      sa.DateTime(),  nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_used',       sa.DateTime(),  nullable=False, server_default=sa.text('NOW()')),
        sa.Column('meta_data',       postgresql.JSONB(), nullable=False, server_default='{}'),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.user_id'],
            ondelete='CASCADE',
            name='fk_user_personas_user_id'
        ),
    )

    op.create_index('ix_user_personas_user_id', 'user_personas', ['user_id'])
    # Partial index — fast lookup for the one active persona per user
    op.execute(
        "CREATE UNIQUE INDEX uq_user_persona_active "
        "ON user_personas (user_id) WHERE is_active = true"
    )


    # -----------------------------------------------------------------------
    # STEP 6: SOUL MEMORIES
    # Long-term narrative storage (The Notebook).
    # Separated from LinkState so we never load big text blobs on every tick.
    # One row per link_state, lazy-loaded only when needed.
    # -----------------------------------------------------------------------

    op.create_table(
        'soul_memories',
        sa.Column('id',            sa.Integer(),  nullable=False),
        sa.Column('link_state_id', sa.Integer(),  nullable=False),

        # LLM-generated relationship summary (the "pre-context" injected on load)
        sa.Column('summary',       sa.Text(),     nullable=False, server_default=''),

        # Verified facts about the user (user_job, favourite_color, etc.)
        sa.Column('facts',         postgresql.JSONB(), nullable=False, server_default='{}'),

        # Canon milestone events (first_kiss, secret_revealed_01, etc.)
        sa.Column('milestones',    postgresql.JSONB(), nullable=False, server_default='[]'),

        sa.Column('last_updated',  sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['link_state_id'], ['link_states.id'],
            ondelete='CASCADE',
            name='fk_soul_memories_link_state_id'
        ),
    )

    op.create_index('ix_soul_memories_link_state_id', 'soul_memories', ['link_state_id'])


    # -----------------------------------------------------------------------
    # STEP 7: USER PROGRESS
    # Gamification layer — achievements, lore unlocks, exploration.
    # Tied to the USER ACCOUNT (not persona) so progress persists across masks.
    # -----------------------------------------------------------------------

    op.create_table(
        'user_progress',
        sa.Column('user_id',               sa.String(36), nullable=False),
        sa.Column('unlocked_achievements', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('unlocked_lore',         postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('visited_locations',     postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('encountered_souls',     postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('total_messages_sent',   sa.Integer(),  nullable=False, server_default='0'),
        sa.Column('total_days_active',     sa.Integer(),  nullable=False, server_default='0'),
        sa.Column('last_updated',          sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),

        sa.PrimaryKeyConstraint('user_id'),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.user_id'],
            ondelete='CASCADE',
            name='fk_user_progress_user_id'
        ),
    )


    # -----------------------------------------------------------------------
    # STEP 8: SUBSCRIPTION HISTORY
    # Billing lifecycle audit trail.
    # Every tier change, cancellation, and refund gets a row here.
    # -----------------------------------------------------------------------

    op.create_table(
        'subscription_history',
        sa.Column('id',                   sa.Integer(),  nullable=False),
        sa.Column('user_id',              sa.String(36), nullable=False),
        sa.Column('tier',                 sa.String(20), nullable=False),
        sa.Column('status',               sa.String(20), nullable=False),
        sa.Column('started_at',           sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('ended_at',             sa.DateTime(), nullable=True),
        sa.Column('payment_provider',     sa.String(20), nullable=False, server_default='stripe'),
        sa.Column('transaction_id',       sa.String(100),nullable=True),
        sa.Column('amount_paid',          sa.Float(),    nullable=False, server_default='0.0'),
        sa.Column('currency',             sa.String(3),  nullable=False, server_default='USD'),
        sa.Column('cancellation_reason',  sa.String(200),nullable=True),
        sa.Column('notes',                sa.String(500),nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.user_id'],
            ondelete='CASCADE',
            name='fk_subscription_history_user_id'
        ),
    )

    op.create_index('ix_subscription_history_user_id', 'subscription_history', ['user_id'])
    op.create_index('ix_subscription_history_status',  'subscription_history', ['status'])


# ---------------------------------------------------------------------------
# DOWNGRADE
# ---------------------------------------------------------------------------

def downgrade() -> None:
    # Drop in reverse dependency order

    op.drop_index('ix_subscription_history_status',  table_name='subscription_history')
    op.drop_index('ix_subscription_history_user_id', table_name='subscription_history')
    op.drop_table('subscription_history')

    op.drop_table('user_progress')

    op.drop_index('ix_soul_memories_link_state_id', table_name='soul_memories')
    op.drop_table('soul_memories')

    op.execute('DROP INDEX IF EXISTS uq_user_persona_active')
    op.drop_index('ix_user_personas_user_id', table_name='user_personas')
    op.drop_table('user_personas')

    op.drop_index('ix_link_states_user_soul', table_name='link_states')
    op.drop_index('ix_link_states_soul_id',   table_name='link_states')
    op.drop_index('ix_link_states_user_id',   table_name='link_states')
    op.drop_table('link_states')

    op.drop_table('soul_states')
    op.drop_table('soul_pillars')

    # Restore legacy tables on downgrade
    op.create_table(
        'user_soul_state',
        sa.Column('id',                   sa.Integer(), nullable=False),
        sa.Column('user_id',              sa.String(36), nullable=False),
        sa.Column('soul_id',              sa.String(50), nullable=False),
        sa.Column('signal_stability',     sa.Float(),   nullable=False, server_default='100.0'),
        sa.Column('last_stability_decay', sa.DateTime(),nullable=False, server_default=sa.text('NOW()')),
        sa.Column('nsfw_enabled',         sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('total_messages_sent',  sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_stability_boosts',sa.Integer(),nullable=False, server_default='0'),
        sa.Column('created_at',           sa.DateTime(),nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at',           sa.DateTime(),nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'soul_id', name='uq_user_soul'),
    )
    op.create_index('ix_user_soul_state_user_id', 'user_soul_state', ['user_id'])
    op.create_index('ix_user_soul_state_soul_id', 'user_soul_state', ['soul_id'])
