"""Added square and price fields

Revision ID: f41aa6ee5c2a
Revises: 4c7196bca03b
Create Date: 2021-04-23 04:30:08.056313

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f41aa6ee5c2a'
down_revision = '4c7196bca03b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('realty_details', sa.Column('price', sa.Float(), nullable=False))
    op.add_column('realty_details', sa.Column('square', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('realty_details', 'square')
    op.drop_column('realty_details', 'price')
    # ### end Alembic commands ###