"""
Revision ID: 0008_create_profile_scores
Revises: 0007_create_profile_snapshots
Create Date: 2026-02-18

Create profile_scores table
"""

revision = '0008_create_profile_scores'
down_revision = '0007_create_profile_snapshots'
branch_labels = None
depends_on = None
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'profile_scores',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('profile_id', sa.String, index=True, nullable=False),
        sa.Column('model', sa.String, nullable=False),
        sa.Column('score', sa.Integer, nullable=False),
        sa.Column('calibrated_score', sa.Integer),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_index('idx_profile_scores_profile_model', 'profile_scores', ['profile_id', 'model', 'created_at'], unique=False)

def downgrade():
    op.drop_index('idx_profile_scores_profile_model', table_name='profile_scores')
    op.drop_table('profile_scores')
