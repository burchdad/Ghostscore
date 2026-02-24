"""
Revision ID: 0011_update_profile_snapshots_schema
Revises: 0010_add_model_version_to_profile_scores
Create Date: 2026-02-18

Update profile_snapshots table to use UUID id and add snapshot_hash
"""

revision = '0011_update_profile_snapshots_schema'
down_revision = '0010_add_model_version_to_profile_scores'
branch_labels = None
depends_on = None
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.alter_column('profile_snapshots', 'id',
        existing_type=sa.Integer(),
        type_=sa.dialects.postgresql.UUID(as_uuid=True),
        postgresql_using='uuid_generate_v4()',
        existing_nullable=False)
    op.add_column('profile_snapshots', sa.Column('snapshot_hash', sa.String()))


def downgrade():
    op.drop_column('profile_snapshots', 'snapshot_hash')
    # Downgrade UUID to Integer is not supported automatically
