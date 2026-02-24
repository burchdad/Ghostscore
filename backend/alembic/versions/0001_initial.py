"""Initial schema migration

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-15 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'credit_profiles',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'accounts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('profile_id', sa.String(length=36), sa.ForeignKey('credit_profiles.id'), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('balance', sa.Float(), nullable=True),
        sa.Column('limit', sa.Float(), nullable=True),
        sa.Column('open_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'derogatories',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('profile_id', sa.String(length=36), sa.ForeignKey('credit_profiles.id'), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'score_history',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('profile_id', sa.String(length=36), sa.ForeignKey('credit_profiles.id'), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('payment_history', sa.Integer(), nullable=True),
        sa.Column('utilization', sa.Integer(), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('new_credit', sa.Integer(), nullable=True),
        sa.Column('mix', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'scenario_history',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('profile_id', sa.String(length=36), sa.ForeignKey('credit_profiles.id'), nullable=False),
        sa.Column('actions', sa.JSON(), nullable=False),
        sa.Column('original_score', sa.Integer(), nullable=False),
        sa.Column('simulated_score', sa.Integer(), nullable=False),
        sa.Column('actual_gain', sa.Integer(), nullable=True),
        sa.Column('timeline', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('pinned', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('feedback', sa.String(), nullable=True),
    )
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'credit_profiles',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'accounts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('profile_id', sa.String(length=36), sa.ForeignKey('credit_profiles.id'), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('balance', sa.Float(), nullable=True),
        sa.Column('limit', sa.Float(), nullable=True),
        sa.Column('open_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'derogatories',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('profile_id', sa.String(length=36), sa.ForeignKey('credit_profiles.id'), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    op.create_table(
        'score_history',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('profile_id', sa.String(length=36), sa.ForeignKey('credit_profiles.id'), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('payment_history', sa.Integer(), nullable=True),
        sa.Column('utilization', sa.Integer(), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('new_credit', sa.Integer(), nullable=True),
        sa.Column('mix', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('scenario_history')
    op.drop_table('score_history')
    op.drop_table('derogatories')
    op.drop_table('accounts')
    op.drop_table('credit_profiles')
    op.drop_table('users')
