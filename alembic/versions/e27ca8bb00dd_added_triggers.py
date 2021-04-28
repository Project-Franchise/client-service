"""Added triggers

Revision ID: e27ca8bb00dd
Revises: bcc88fcccb0e
Create Date: 2021-04-28 16:58:48.483309

"""

from alembic import op

# revision identifiers, used by Andriy.
from service_api.grabbing_api.constants import PATH_TO_TRIGGERS_SQL

revision = 'e27ca8bb00dd'
down_revision = 'bcc88fcccb0e'
branch_labels = None
depends_on = None


def upgrade():
    with open(PATH_TO_TRIGGERS_SQL) as file:
        triggers = file.read()
        op.execute(triggers)


def downgrade():
    op.execute("DROP TRIGGER update_state ON state")
    op.execute("DROP TRIGGER update_city ON city")
    op.execute("DROP TRIGGER update_realty_type ON realty_type")
    op.execute("DROP TRIGGER update_operation_type ON operation_type")
