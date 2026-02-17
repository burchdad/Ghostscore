"""add tags column to scenario_history
Revision ID: 0003_add_tags_to_scenario_history
Revises: 0002_add_user_password
Create Date: 2026-02-16
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_add_tags_to_scenario_history'
down_revision = '0002_add_user_password'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('scenario_history', sa.Column('tags', sa.JSON(), nullable=True))

def downgrade():
    op.drop_column('scenario_history', 'tags')
