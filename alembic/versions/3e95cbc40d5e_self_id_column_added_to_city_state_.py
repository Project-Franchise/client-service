"""Self_id column added to City, State, OperationType, RealtyType

Revision ID: 3e95cbc40d5e
Revises: c3b85d7a8bc7
Create Date: 2021-04-21 17:41:19.254693

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e95cbc40d5e'
down_revision = 'c3b85d7a8bc7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('city', sa.Column('self_id', sa.BIGINT(), nullable=False))
    op.add_column('operation_type', sa.Column('self_id', sa.BIGINT(), nullable=False))
    op.add_column('realty_type', sa.Column('self_id', sa.BIGINT(), nullable=False))
    op.add_column('state', sa.Column('self_id', sa.BIGINT(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('state', 'self_id')
    op.drop_column('realty_type', 'self_id')
    op.drop_column('operation_type', 'self_id')
    op.drop_column('city', 'self_id')
    # ### end Alembic commands ###
