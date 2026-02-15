"""
Add monetization tables: user_soul_state and ad_impressions

Revision ID: 001_monetization_tables
Revises: 
Create Date: 2026-02-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_monetization_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_soul_state table
    op.create_table(
        'user_soul_state',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('soul_id', sa.String(length=50), nullable=False),
        sa.Column('signal_stability', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('last_stability_decay', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('nsfw_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('total_messages_sent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_stability_boosts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'soul_id', name='uq_user_soul')
    )
    op.create_index('ix_user_soul_state_user_id', 'user_soul_state', ['user_id'])
    op.create_index('ix_user_soul_state_soul_id', 'user_soul_state', ['soul_id'])
    
    # Create ad_impressions table
    op.create_table(
        'ad_impressions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('ad_network', sa.String(length=50), nullable=False),
        sa.Column('ad_type', sa.String(length=50), nullable=False),
        sa.Column('placement', sa.String(length=100), nullable=False),
        sa.Column('reward_granted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reward_type', sa.String(length=50), nullable=True),
        sa.Column('reward_amount', sa.Float(), nullable=True),
        sa.Column('ssv_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('ssv_signature', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE')
    )
    op.create_index('ix_ad_impressions_user_id', 'ad_impressions', ['user_id'])
    op.create_index('ix_ad_impressions_ad_network', 'ad_impressions', ['ad_network'])
    op.create_index('ix_ad_impressions_placement', 'ad_impressions', ['placement'])
    op.create_index('ix_ad_impressions_created_at', 'ad_impressions', ['created_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_ad_impressions_created_at', table_name='ad_impressions')
    op.drop_index('ix_ad_impressions_placement', table_name='ad_impressions')
    op.drop_index('ix_ad_impressions_ad_network', table_name='ad_impressions')
    op.drop_index('ix_ad_impressions_user_id', table_name='ad_impressions')
    op.drop_table('ad_impressions')
    
    op.drop_index('ix_user_soul_state_soul_id', table_name='user_soul_state')
    op.drop_index('ix_user_soul_state_user_id', table_name='user_soul_state')
    op.drop_table('user_soul_state')
