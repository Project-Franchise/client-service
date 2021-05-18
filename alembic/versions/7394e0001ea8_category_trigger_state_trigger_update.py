"""Category trigger. State trigger update

Revision ID: 7394e0001ea8
Revises: d3ab13075552
Create Date: 2021-05-18 10:22:29.876407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7394e0001ea8'
down_revision = 'd3ab13075552'
branch_labels = None
depends_on = None


def upgrade():
    state_update_func = """
    CREATE
        OR REPLACE FUNCTION update_state_id ()
    RETURNS TRIGGER AS $UPDATE_STATE_ID$

    BEGIN
        UPDATE state_xref_service sts
        SET entity_id = NEW.id
        WHERE sts.entity_id IN (
                SELECT sts.entity_id
                FROM state_xref_service sts
                JOIN state ON sts.entity_id = state.id
                WHERE state.self_id = NEW.self_id
                    AND state.version is not null
                );

        UPDATE state_alias sa
        SET entity_id = NEW.id
        WHERE sa.entity_id IN (
                SELECT sa.entity_id
                FROM state_alias sa
                JOIN state ON sa.entity_id = state.id
                WHERE state.self_id = NEW.self_id
                    AND state.version is not null
                );

		UPDATE city c
        SET state_id = NEW.id
        WHERE c.state_id IN (
                SELECT ct.state_id
                FROM city ct
                JOIN state s ON ct.state_id = s.id
                WHERE s.self_id = NEW.self_id
                    AND s.version is not null
                );

        RETURN NEW;
    END $UPDATE_STATE_ID$

    LANGUAGE PLPGSQL;"""

    category_trigger = """
    CREATE
	OR REPLACE FUNCTION update_category_id ()
    RETURNS TRIGGER AS $UPDATE_CATEGORY_ID$

    BEGIN
        UPDATE category_xref_service cts
        SET entity_id=NEW.id
        WHERE cts.entity_id IN (
			SELECT cts.entity_id
                FROM category_xref_service cts
                JOIN category c ON cts.entity_id = c.id
                WHERE c.self_id = NEW.self_id
                    AND c.version is not null
		);

		UPDATE category_alias ca
        SET entity_id=NEW.id
        WHERE ca.entity_id IN (
			SELECT ca.entity_id
                FROM category_alias ca
                JOIN category c ON ca.entity_id = c.id
                WHERE c.self_id = NEW.self_id
                    AND c.version is not null
		);

		UPDATE realty_type rt
        SET category_id = NEW.id
        WHERE rt.category_id IN (
			SELECT rt.category_id
                FROM realty_type rt
                JOIN category c ON rt.category_id = c.id
                WHERE c.self_id = NEW.self_id
                    AND c.version is not null
		);
    RETURN NEW;
    END $UPDATE_CATEGORY_ID$
    LANGUAGE PLPGSQL;

    CREATE TRIGGER update_category_id
    AFTER INSERT ON category
    FOR EACH ROW
    EXECUTE PROCEDURE update_category_id();"""

    op.execute(state_update_func)
    op.execute(category_trigger)


def downgrade():
    state_update_func = """
    CREATE
        OR REPLACE FUNCTION update_state_id ()
    RETURNS TRIGGER AS $UPDATE_STATE_ID$

    BEGIN
        UPDATE state_xref_service sts
        SET entity_id = NEW.id
        WHERE sts.entity_id IN (
                SELECT sts.entity_id
                FROM state_xref_service sts
                JOIN state ON sts.entity_id = state.id
                WHERE state.self_id = NEW.self_id
                    AND state.version is not null
                );

        UPDATE state_alias sa
        SET entity_id = NEW.id
        WHERE sa.entity_id IN (
                SELECT sa.entity_id
                FROM state_alias sa
                JOIN state ON sa.entity_id = state.id
                WHERE state.self_id = NEW.self_id
                    AND state.version is not null
                );

        RETURN NEW;
    END $UPDATE_STATE_ID$

    LANGUAGE PLPGSQL;"""

    op.execute(state_update_func)
    op.execute("DROP TRIGGER update_category_id ON category")
