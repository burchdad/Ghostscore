"""Add password column to users

Revision ID: 0002_add_user_password
Revises: 0001_initial
Create Date: 2026-02-15 00:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_user_password'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('password', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('users', 'password')
