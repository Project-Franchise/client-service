"""RealtyDetails fileds nullable option changed

Revision ID: d0a2d093a902
Revises: 8de4d2189413
Create Date: 2021-04-01 03:46:49.968493

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0a2d093a902'
down_revision = '8de4d2189413'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('realty_details', 'floor',
               existing_type=sa.BIGINT(),
               nullable=True)
    op.alter_column('realty_details', 'floors_number',
               existing_type=sa.BIGINT(),
               nullable=True)
    op.drop_column('realty_details', 'description')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('realty_details', sa.Column('description', sa.VARCHAR(length=2047), autoincrement=False, nullable=True))
    op.alter_column('realty_details', 'floors_number',
               existing_type=sa.BIGINT(),
               nullable=False)
    op.alter_column('realty_details', 'floor',
               existing_type=sa.BIGINT(),
               nullable=False)
    # ### end Alembic commands ###
