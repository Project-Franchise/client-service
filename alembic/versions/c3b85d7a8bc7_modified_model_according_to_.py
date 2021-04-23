"""Modified model according to multiservice logic

Revision ID: c3b85d7a8bc7
Revises: d2611fc7c48a
Create Date: 2021-04-19 20:29:47.740846

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3b85d7a8bc7'
down_revision = 'd2611fc7c48a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('operation_type_alias',
    sa.Column('operation_type_id', sa.BIGINT(), nullable=False),
    sa.Column('alias', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['operation_type_id'], ['operation_type.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('operation_type_id', 'alias')
    )
    op.create_table('operation_type_to_service',
    sa.Column('operation_type_id', sa.BIGINT(), nullable=False),
    sa.Column('service_id', sa.BIGINT(), nullable=False),
    sa.Column('original_id', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['operation_type_id'], ['operation_type.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('operation_type_id', 'service_id')
    )
    op.create_table('realty_type_alias',
    sa.Column('realty_type_id', sa.BIGINT(), nullable=False),
    sa.Column('alias', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['realty_type_id'], ['realty_type.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('realty_type_id', 'alias')
    )
    op.create_table('realty_type_to_service',
    sa.Column('realty_type_id', sa.BIGINT(), nullable=False),
    sa.Column('service_id', sa.BIGINT(), nullable=False),
    sa.Column('original_id', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['realty_type_id'], ['realty_type.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('realty_type_id', 'service_id')
    )
    op.create_table('state_alias',
    sa.Column('state_id', sa.BIGINT(), nullable=False),
    sa.Column('alias', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('state_id', 'alias')
    )
    op.create_table('state_to_service',
    sa.Column('state_id', sa.BIGINT(), nullable=False),
    sa.Column('service_id', sa.BIGINT(), nullable=False),
    sa.Column('original_id', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['state_id'], ['state.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('state_id', 'service_id')
    )
    op.create_table('city_alias',
    sa.Column('city_id', sa.BIGINT(), nullable=False),
    sa.Column('alias', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['city_id'], ['city.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('city_id', 'alias')
    )
    op.create_table('city_to_service',
    sa.Column('city_id', sa.BIGINT(), nullable=False),
    sa.Column('service_id', sa.BIGINT(), nullable=False),
    sa.Column('original_id', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['city_id'], ['city.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('city_id', 'service_id')
    )
    op.drop_constraint('city_original_id_key', 'city', type_='unique')
    op.drop_column('city', 'original_id')
    op.drop_constraint('operation_type_original_id_key', 'operation_type', type_='unique')
    op.drop_column('operation_type', 'original_id')
    op.drop_constraint('realty_details_original_id_key', 'realty_details', type_='unique')
    op.drop_column('realty_details', 'original_id')
    op.drop_constraint('realty_type_original_id_key', 'realty_type', type_='unique')
    op.drop_column('realty_type', 'original_id')
    op.drop_constraint('state_original_id_key', 'state', type_='unique')
    op.drop_column('state', 'original_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('state', sa.Column('original_id', sa.BIGINT(), autoincrement=False, nullable=False))
    op.create_unique_constraint('state_original_id_key', 'state', ['original_id'])
    op.add_column('realty_type', sa.Column('original_id', sa.BIGINT(), autoincrement=False, nullable=False))
    op.create_unique_constraint('realty_type_original_id_key', 'realty_type', ['original_id'])
    op.add_column('realty_details', sa.Column('original_id', sa.BIGINT(), autoincrement=False, nullable=False))
    op.create_unique_constraint('realty_details_original_id_key', 'realty_details', ['original_id'])
    op.add_column('operation_type', sa.Column('original_id', sa.BIGINT(), autoincrement=False, nullable=False))
    op.create_unique_constraint('operation_type_original_id_key', 'operation_type', ['original_id'])
    op.add_column('city', sa.Column('original_id', sa.BIGINT(), autoincrement=False, nullable=False))
    op.create_unique_constraint('city_original_id_key', 'city', ['original_id'])
    op.drop_table('city_to_service')
    op.drop_table('city_alias')
    op.drop_table('state_to_service')
    op.drop_table('state_alias')
    op.drop_table('realty_type_to_service')
    op.drop_table('realty_type_alias')
    op.drop_table('operation_type_to_service')
    op.drop_table('operation_type_alias')
    op.drop_table('service')
    # ### end Alembic commands ###