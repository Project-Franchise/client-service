"""category tables and schemas added

Revision ID: ea28a11e4797
Revises: a04cc8045c2d
Create Date: 2021-05-01 00:32:29.173477

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea28a11e4797'
down_revision = 'a04cc8045c2d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
                    sa.Column('id', sa.BIGINT(), nullable=False),
                    sa.Column('name', sa.VARCHAR(length=255), nullable=False),
                    sa.Column('self_id', sa.BIGINT(), nullable=False),
                    sa.Column('version', sa.TIMESTAMP(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('self_id', 'version')
                    )
    op.create_table('category_alias',
                    sa.Column('entity_id', sa.BIGINT(), nullable=False),
                    sa.Column('alias', sa.VARCHAR(length=255), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['entity_id'], ['category.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('entity_id', 'alias')
                    )
    op.create_table('category_to_service',
                    sa.Column('entity_id', sa.BIGINT(), nullable=False),
                    sa.Column('service_id', sa.BIGINT(), nullable=False),
                    sa.Column('original_id', sa.VARCHAR(
                        length=255), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['entity_id'], ['category.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(
                        ['service_id'], ['service.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('entity_id', 'service_id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('category_to_service')
    op.drop_table('category_alias')
    op.drop_table('category')
    # ### end Alembic commands ###
