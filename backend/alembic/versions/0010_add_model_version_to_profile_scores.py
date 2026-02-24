"""
Revision ID: 0010_add_model_version_to_profile_scores
Revises: 0009_update_profile_calibration
Create Date: 2026-02-18

Add model_version column to profile_scores
"""

revision = '0010_add_model_version_to_profile_scores'
down_revision = '0009_update_profile_calibration'
branch_labels = None
depends_on = None
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('profile_scores', sa.Column('model_version', sa.String))

def downgrade():
    op.drop_column('profile_scores', 'model_version')
