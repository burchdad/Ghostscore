"""
Revision ID: 0009_update_profile_calibration
Revises: 0008_create_profile_scores
Create Date: 2026-02-18

Update profile_calibration table for per-model calibration
"""

revision = '0009_update_profile_calibration'
down_revision = '0008_create_profile_scores'
branch_labels = None
depends_on = None
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'profile_calibration',
        sa.Column('profile_id', sa.String, nullable=False),
        sa.Column('model', sa.String, nullable=False),
        sa.Column('offset', sa.Float),
        sa.Column('actual_score', sa.Integer),
        sa.Column('estimated_score', sa.Integer),
        sa.PrimaryKeyConstraint('profile_id', 'model')
    )

def downgrade():
    op.drop_table('profile_calibration')
