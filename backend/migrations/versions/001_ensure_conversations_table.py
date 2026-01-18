"""Ensure conversations table has correct structure

Revision ID: 001
Revises: 
Create Date: 2026-01-17 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if conversations table exists
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT EXISTS (
           SELECT FROM information_schema.tables 
           WHERE table_name = 'conversations'
        );
    """))
    
    table_exists = result.fetchone()[0]
    
    if not table_exists:
        # Create the conversations table with all required columns
        op.create_table('conversations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("now()")),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    else:
        # Table exists, add missing columns
        # Check for user_id column
        result = conn.execute(sa.text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'conversations' AND column_name = 'user_id';
        """))
        
        user_id_exists = result.fetchone() is not None
        if not user_id_exists:
            op.add_column('conversations', sa.Column('user_id', sa.String(), nullable=True))
        
        # Check for created_at column
        result = conn.execute(sa.text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'conversations' AND column_name = 'created_at';
        """))
        
        created_at_exists = result.fetchone() is not None
        if not created_at_exists:
            op.add_column('conversations', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text("now()")))
        
        # Check for updated_at column
        result = conn.execute(sa.text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'conversations' AND column_name = 'updated_at';
        """))
        
        updated_at_exists = result.fetchone() is not None
        if not updated_at_exists:
            op.add_column('conversations', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text("now()")))


def downgrade() -> None:
    # Drop the conversations table
    op.drop_table('conversations')