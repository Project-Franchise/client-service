"""Updated models

Revision ID: f35ba61540e8
Revises:
Create Date: 2021-03-27 00:29:25.070536

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f35ba61540e8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('operation_type',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('original_id', sa.BIGINT(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('realty_details',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('floor', sa.BIGINT(), nullable=False),
    sa.Column('floors_number', sa.BIGINT(), nullable=False),
    sa.Column('square', sa.BIGINT(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('published_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('original_id', sa.BIGINT(), nullable=False),
    sa.Column('original_url', sa.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('realty_type',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('original_id', sa.BIGINT(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('state',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=128), nullable=False),
    sa.Column('original_id', sa.BIGINT(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('city',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=128), nullable=False),
    sa.Column('state_id', sa.BIGINT(), nullable=False),
    sa.Column('original_id', sa.BIGINT(), nullable=False),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('realty',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('city_id', sa.BIGINT(), nullable=False),
    sa.Column('state_id', sa.BIGINT(), nullable=False),
    sa.Column('realty_details_id', sa.BIGINT(), nullable=False),
    sa.Column('realty_type_id', sa.BIGINT(), nullable=False),
    sa.Column('operation_type_id', sa.BIGINT(), nullable=False),
    sa.ForeignKeyConstraint(['city_id'], ['city.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['operation_type_id'], ['operation_type.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['realty_details_id'], ['realty_details.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['realty_type_id'], ['realty_type.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('realty')
    op.drop_table('city')
    op.drop_table('state')
    op.drop_table('realty_type')
    op.drop_table('realty_details')
    op.drop_table('operation_type')
    # ### end Alembic commands ###
