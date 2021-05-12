"""Original ID to RealtyDetails added

Revision ID: a23a5ca33d0d
Revises: 9deac691669d
Create Date: 2021-05-12 00:52:40.530325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a23a5ca33d0d'
down_revision = '9deac691669d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('realty_details', sa.Column('original_id', sa.BIGINT(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('realty_details', 'original_id')
    # ### end Alembic commands ###