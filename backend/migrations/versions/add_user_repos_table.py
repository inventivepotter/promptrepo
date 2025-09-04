# backend/migrations/versions/add_user_repos_table.py
"""Add user_repos table

Revision ID: add_user_repos_table
Revises: 2636b0b9ee6f
Create Date: 2025-09-03 12:00:00.000000

"""
from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_user_repos_table'
down_revision: Union[str, Sequence[str], None] = '2636b0b9ee6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user_repos table."""
    # Create enum type for repo status
    repo_status_enum = sa.Enum(
        'pending', 'cloning', 'cloned', 'failed', 'outdated',
        name='repostatus'
    )
    repo_status_enum.create(op.get_bind())

    # Create user_repos table
    op.create_table('user_repos',
                    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('repo_clone_url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('repo_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('status', repo_status_enum, nullable=False),
                    sa.Column('branch', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('local_path', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('last_clone_attempt', sa.DateTime(), nullable=True),
                    sa.Column('clone_error_message', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    # Create indexes
    op.create_index(op.f('ix_user_repos_user_id'), 'user_repos', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_repos_repo_clone_url'), 'user_repos', ['repo_clone_url'], unique=False)
    op.create_index(op.f('ix_user_repos_repo_name'), 'user_repos', ['repo_name'], unique=False)


def downgrade() -> None:
    """Remove user_repos table."""
    # Drop indexes
    op.drop_index(op.f('ix_user_repos_repo_name'), table_name='user_repos')
    op.drop_index(op.f('ix_user_repos_repo_clone_url'), table_name='user_repos')
    op.drop_index(op.f('ix_user_repos_user_id'), table_name='user_repos')

    # Drop table
    op.drop_table('user_repos')

    # Drop enum type
    sa.Enum(name='repostatus').drop(op.get_bind())