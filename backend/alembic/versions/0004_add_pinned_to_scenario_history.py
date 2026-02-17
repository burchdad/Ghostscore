"""add pinned column to scenario_history
Revision ID: 0004_add_pinned_to_scenario_history
Revises: 0003_add_tags_to_scenario_history
Create Date: 2026-02-16
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0004_add_pinned_to_scenario_history'
down_revision = '0003_add_tags_to_scenario_history'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('scenario_history', sa.Column('pinned', sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade():
    op.drop_column('scenario_history', 'pinned')
