"""initial

Revision ID: 001
Revises: 
Create Date: 2026-02-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('dispatcher', 'master', name='userrole'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    op.create_table('requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('clientName', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('problemText', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('new', 'assigned', 'in_progress', 'done', 'canceled', name='requeststatus'), nullable=False, server_default='new'),
        sa.Column('assignedTo', sa.Integer(), nullable=True),
        sa.Column('createdAt', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updatedAt', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['assignedTo'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_requests_id'), 'requests', ['id'], unique=False)

def downgrade():
    op.drop_table('requests')
    op.drop_table('users')
    op.execute('DROP TYPE userrole')
    op.execute('DROP TYPE requeststatus')