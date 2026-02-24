"""
Revision ID: 0006_create_profile_calibration
Revises: 0005_add_feedback_to_scenario_history
Create Date: 2026-02-18

Alembic migration for profile_calibration table
"""

revision = '0006_create_profile_calibration'
down_revision = '0005_add_feedback_to_scenario_history'
branch_labels = None
depends_on = None
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'profile_calibration',
        sa.Column('profile_id', sa.Text(), primary_key=True),
        sa.Column('offset', sa.Float(), nullable=False),
        sa.Column('actual_score', sa.Integer()),
        sa.Column('estimated_score', sa.Integer()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

def downgrade():
    op.drop_table('profile_calibration')
