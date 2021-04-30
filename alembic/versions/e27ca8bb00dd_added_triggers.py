"""Added triggers

Revision ID: e27ca8bb00dd
Revises: bcc88fcccb0e
Create Date: 2021-04-28 16:58:48.483309

"""

from alembic import op

# revision identifiers, used by Andriy.

revision = 'e27ca8bb00dd'
down_revision = 'bacd8b480d1c'
branch_labels = None
depends_on = None


def upgrade():
    state_trigger = """
    CREATE
        OR REPLACE FUNCTION update_state_id ()
    RETURNS TRIGGER AS $UPDATE_STATE_ID$

    BEGIN
        UPDATE state_to_service sts
        SET entity_id = NEW.id
        WHERE sts.entity_id IN (
                SELECT sts.entity_id
                FROM state_to_service sts
                JOIN state ON sts.entity_id = state.id
                WHERE state.self_id = NEW.self_id
                    AND state.version <> NEW.version
                );

        UPDATE state_alias sa
        SET entity_id = NEW.id
        WHERE sa.entity_id IN (
                SELECT sa.entity_id
                FROM state_alias sa
                JOIN state ON sa.entity_id = state.id
                WHERE state.self_id = NEW.self_id
                    AND state.version <> NEW.version
                );

        RETURN NEW;
    END $UPDATE_STATE_ID$

    LANGUAGE PLPGSQL;

    CREATE TRIGGER update_state
    AFTER INSERT ON state
    FOR EACH ROW EXECUTE PROCEDURE update_state_id();"""

    city_trigger = """
    CREATE
        OR REPLACE FUNCTION update_city_id ()
    RETURNS TRIGGER AS $UPDATE_CITY_ID$

    BEGIN
        UPDATE city_to_service cts
        SET entity_id = NEW.id
        WHERE cts.entity_id IN (
                SELECT cts.entity_id
                FROM city_to_service cts
                JOIN city ON cts.entity_id = city.id
                WHERE city.self_id = NEW.self_id
                    AND city.version <> NEW.version
                );

        UPDATE city_alias ca
        SET entity_id = NEW.id
        WHERE ca.entity_id IN (
                SELECT ca.entity_id
                FROM city_alias ca
                JOIN city ON ca.entity_id = city.id
                WHERE city.self_id = NEW.self_id
                    AND city.version <> NEW.version
                );

        RETURN NEW;
    END $UPDATE_CITY_ID$

    LANGUAGE PLPGSQL;

    CREATE TRIGGER update_city
    AFTER INSERT ON city
    FOR EACH ROW EXECUTE PROCEDURE update_city_id();"""

    realty_type_trigger = """
    CREATE
        OR REPLACE FUNCTION update_realty_type_id ()
    RETURNS TRIGGER AS $UPDATE_REALTY_TYPE_ID$

    BEGIN
        UPDATE realty_type_to_service rtts
        SET entity_id = NEW.id
        WHERE rtts.entity_id IN (
                SELECT rtts.entity_id
                FROM realty_type_to_service rtts
                JOIN realty_type rt ON rtts.entity_id = rt.id
                WHERE rt.self_id = NEW.self_id
                    AND rt.version <> NEW.version
                );

        UPDATE realty_type_alias rta
        SET entity_id = NEW.id
        WHERE rta.entity_id IN (
                SELECT rta.entity_id
                FROM realty_type_alias rta
                JOIN realty_type rt ON rta.entity_id = rt.id
                WHERE rt.self_id = NEW.self_id
                    AND rt.version <> NEW.version
                );

        RETURN NEW;
    END $UPDATE_REALTY_TYPE_ID$

    LANGUAGE PLPGSQL;

    CREATE TRIGGER update_realty_type
    AFTER INSERT ON realty_type
    FOR EACH ROW

    EXECUTE PROCEDURE update_realty_type_id();"""

    operation_type_trigger = """
    CREATE
        OR REPLACE FUNCTION update_operation_type_id ()
    RETURNS TRIGGER AS $UPDATE_OPERATION_TYPE_ID$

    BEGIN
        UPDATE operation_type_to_service otts
        SET entity_id = NEW.id
        WHERE otts.entity_id = (
                SELECT otts.entity_id
                FROM operation_type_to_service otts
                JOIN operation_type ot ON otts.entity_id = ot.id
                WHERE ot.self_id = NEW.self_id
                    AND ot.version <> NEW.version
                );

        UPDATE operation_type_alias ota
        SET entity_id = NEW.id
        WHERE ota.entity_id IN (
                SELECT ota.entity_id
                FROM operation_type_alias ota
                JOIN operation_type ot ON ota.entity_id = ot.id
                WHERE ot.self_id = NEW.self_id
                    AND ot.version <> NEW.version
                );

        RETURN NEW;
    END $UPDATE_OPERATION_TYPE_ID$

    LANGUAGE PLPGSQL;

    CREATE TRIGGER update_operation_type
    AFTER INSERT ON operation_type
    FOR EACH ROW

    EXECUTE PROCEDURE update_operation_type_id();"""

    op.execute(state_trigger)
    op.execute(city_trigger)
    op.execute(realty_type_trigger)
    op.execute(operation_type_trigger)


def downgrade():
    op.execute("DROP TRIGGER update_state ON state")
    op.execute("DROP TRIGGER update_city ON city")
    op.execute("DROP TRIGGER update_realty_type ON realty_type")
    op.execute("DROP TRIGGER update_operation_type ON operation_type")
