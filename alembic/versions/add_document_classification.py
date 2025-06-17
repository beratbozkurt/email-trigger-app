"""add document classification

Revision ID: add_document_classification
Revises: 
Create Date: 2024-06-15 09:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_document_classification'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to attachments table
    op.add_column('attachments', sa.Column('document_type', sa.String(), nullable=True))
    op.add_column('attachments', sa.Column('classification_confidence', sa.Float(), nullable=True))
    op.add_column('attachments', sa.Column('page_count', sa.Integer(), nullable=True))
    op.add_column('attachments', sa.Column('classification_error', sa.String(), nullable=True))
    op.add_column('attachments', sa.Column('classification_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True))

def downgrade():
    # Remove columns from attachments table
    op.drop_column('attachments', 'classification_metadata')
    op.drop_column('attachments', 'classification_error')
    op.drop_column('attachments', 'page_count')
    op.drop_column('attachments', 'classification_confidence')
    op.drop_column('attachments', 'document_type') 