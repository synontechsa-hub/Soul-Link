"""
Add calendar, weather, progression and settings columns to users table

Revision ID: 002_user_world_state
Revises: 001_monetization_tables
Create Date: 2026-02-26

Adds the following columns to the `users` table to support:
  - Per-user in-game calendar (calendar_day, calendar_month, calendar_year)
  - Per-user weather/season state (current_season, current_weather)
  - Progression tracking (total_sessions, total_days_played, souls_linked)
  - Server-side settings (nsfw_enabled, notifications_enabled, language)
  - Activity tracking (last_seen_at)

All columns use safe server_default values so existing rows are not broken.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002_user_world_state'
down_revision = '001_monetization_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── IDENTITY ─────────────────────────────────────────────────────
    op.add_column('users',
                  sa.Column('last_seen_at', sa.DateTime(),
                            nullable=True, server_default=None)
                  )

    # ── WORLD STATE: CALENDAR ────────────────────────────────────────
    op.add_column('users',
                  sa.Column('calendar_day', sa.Integer(),
                            nullable=False, server_default='1')
                  )
    op.add_column('users',
                  sa.Column('calendar_month', sa.Integer(),
                            nullable=False, server_default='1')
                  )
    op.add_column('users',
                  sa.Column('calendar_year', sa.Integer(),
                            nullable=False, server_default='1')
                  )
    op.add_column('users',
                  sa.Column('current_season', sa.String(length=20),
                            nullable=False, server_default='frostlink')
                  )
    op.add_column('users',
                  sa.Column('current_weather', sa.String(length=50),
                            nullable=False, server_default='clear_frost')
                  )

    # ── PROGRESSION ──────────────────────────────────────────────────
    op.add_column('users',
                  sa.Column('total_sessions', sa.Integer(),
                            nullable=False, server_default='0')
                  )
    op.add_column('users',
                  sa.Column('total_days_played', sa.Integer(),
                            nullable=False, server_default='0')
                  )
    op.add_column('users',
                  sa.Column('souls_linked', sa.Integer(),
                            nullable=False, server_default='0')
                  )

    # ── SETTINGS ─────────────────────────────────────────────────────
    op.add_column('users',
                  sa.Column('nsfw_enabled', sa.Boolean(),
                            nullable=False, server_default='false')
                  )
    op.add_column('users',
                  sa.Column('notifications_enabled', sa.Boolean(),
                            nullable=False, server_default='true')
                  )
    op.add_column('users',
                  sa.Column('language', sa.String(length=10),
                            nullable=False, server_default='en')
                  )


def downgrade() -> None:
    op.drop_column('users', 'language')
    op.drop_column('users', 'notifications_enabled')
    op.drop_column('users', 'nsfw_enabled')
    op.drop_column('users', 'souls_linked')
    op.drop_column('users', 'total_days_played')
    op.drop_column('users', 'total_sessions')
    op.drop_column('users', 'current_weather')
    op.drop_column('users', 'current_season')
    op.drop_column('users', 'calendar_year')
    op.drop_column('users', 'calendar_month')
    op.drop_column('users', 'calendar_day')
    op.drop_column('users', 'last_seen_at')
