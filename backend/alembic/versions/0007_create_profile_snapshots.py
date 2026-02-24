"""
Revision ID: 0007_create_profile_snapshots
Revises: 0006_create_profile_calibration
Create Date: 2026-02-18

Create profile_snapshots table
"""

revision = '0007_create_profile_snapshots'
down_revision = '0006_create_profile_calibration'
branch_labels = None
depends_on = None
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'profile_snapshots',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('profile_id', sa.String, index=True),
        sa.Column('profile_json', sa.String),
        sa.Column('score', sa.Integer),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )

def downgrade():
    op.drop_table('profile_snapshots')
