"""Ondelete fixed

Revision ID: 213559dc2506
Revises: f35ba61540e8
Create Date: 2021-03-31 21:47:33.948321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '213559dc2506'
down_revision = 'f35ba61540e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'city', ['original_id'])
    op.drop_constraint('city_state_id_fkey', 'city', type_='foreignkey')
    op.create_foreign_key(None, 'city', 'state', ['state_id'], [
                          'id'], ondelete='CASCADE')
    op.create_unique_constraint(None, 'operation_type', ['original_id'])
    op.alter_column('realty', 'city_id',
                    existing_type=sa.BIGINT(),
                    nullable=True)
    op.alter_column('realty', 'operation_type_id',
                    existing_type=sa.BIGINT(),
                    nullable=True)
    op.create_unique_constraint(None, 'realty', ['realty_details_id'])
    op.drop_constraint('realty_state_id_fkey', 'realty', type_='foreignkey')
    op.drop_constraint('realty_realty_type_id_fkey',
                       'realty', type_='foreignkey')
    op.create_foreign_key(None, 'realty', 'state', [
                          'state_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'realty', 'realty_type', [
                          'realty_type_id'], ['id'], ondelete='CASCADE')
    op.add_column('realty_details', sa.Column(
        'description', sa.VARCHAR(length=2047), nullable=True))
    op.create_unique_constraint(None, 'realty_details', ['original_id'])
    op.create_unique_constraint(None, 'realty_details', ['original_url'])
    op.create_unique_constraint(None, 'realty_type', ['original_id'])
    op.create_unique_constraint(None, 'state', ['original_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'state', type_='unique')
    op.drop_constraint(None, 'realty_type', type_='unique')
    op.drop_constraint(None, 'realty_details', type_='unique')
    op.drop_constraint(None, 'realty_details', type_='unique')
    op.drop_column('realty_details', 'description')
    op.drop_constraint(None, 'realty', type_='foreignkey')
    op.drop_constraint(None, 'realty', type_='foreignkey')
    op.create_foreign_key('realty_realty_type_id_fkey', 'realty', 'realty_type', [
                          'realty_type_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('realty_state_id_fkey', 'realty', 'state', [
                          'state_id'], ['id'], ondelete='SET NULL')
    op.drop_constraint(None, 'realty', type_='unique')
    op.alter_column('realty', 'operation_type_id',
                    existing_type=sa.BIGINT(),
                    nullable=False)
    op.alter_column('realty', 'city_id',
                    existing_type=sa.BIGINT(),
                    nullable=False)
    op.drop_constraint(None, 'operation_type', type_='unique')
    op.drop_constraint(None, 'city', type_='foreignkey')
    op.create_foreign_key('city_state_id_fkey', 'city', 'state', [
                          'state_id'], ['id'], ondelete='SET NULL')
    op.drop_constraint(None, 'city', type_='unique')
    # ### end Alembic commands ###
