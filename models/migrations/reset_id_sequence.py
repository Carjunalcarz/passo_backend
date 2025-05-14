"""Module for handling database sequence reset operations in Alembic migrations."""
from alembic import op


def upgrade() -> None:
    """Upgrade the database by resetting the owner_id sequence.
    
    Creates a new sequence starting from the current maximum ID in the owner_details table.
    """
    # Drop existing sequence if any
    op.execute('DROP SEQUENCE IF EXISTS owner_id_seq')
    
    # Create new sequence
    op.execute("""
    CREATE SEQUENCE owner_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
    """)
    
    # Reset the current ID sequence to match the max ID in the table
    op.execute("""
    SELECT setval('owner_id_seq', (SELECT MAX(id) FROM owner_details))
    """)


def downgrade() -> None:
    """Revert the sequence changes by dropping the owner_id sequence."""
    op.execute('DROP SEQUENCE IF EXISTS owner_id_seq')
