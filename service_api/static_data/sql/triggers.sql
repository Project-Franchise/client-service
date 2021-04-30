CREATE OR REPLACE FUNCTION update_state_id() RETURNS TRIGGER AS $update_state_id$
BEGIN
UPDATE state_to_service
SET entity_id = NEW.id
WHERE entity_id IN (
    SELECT state_to_service.entity_id
    FROM state_to_service JOIN state ON state_to_service.entity_id = state.id
    WHERE state.self_id = NEW.self_id AND version <> NEW.version);
UPDATE state_alias
SET entity_id = NEW.id
WHERE entity_id IN (
    SELECT state_alias.entity_id
    FROM state_alias JOIN state ON state_alias.entity_id = state.id
    WHERE state.self_id = NEW.self_id AND version <> NEW.version);
RETURN NEW;
END
$update_state_id$ LANGUAGE PLPGSQL;

CREATE TRIGGER update_state AFTER INSERT ON state
    FOR EACH ROW EXECUTE PROCEDURE update_state_id();


CREATE OR REPLACE FUNCTION update_city_id() RETURNS TRIGGER AS $update_city_id$
BEGIN
UPDATE city_to_service
SET entity_id = NEW.id
WHERE entity_id IN (
    SELECT city_to_service.entity_id
    FROM city_to_service JOIN city ON city_to_service.entity_id = city.id
    WHERE city.self_id = NEW.self_id AND version <> NEW.version);
UPDATE city_alias
SET entity_id = NEW.id
WHERE entity_id IN (
    SELECT city_alias.entity_id
    FROM city_alias JOIN city ON city_alias.entity_id = city.id
    WHERE city.self_id = NEW.self_id AND version <> NEW.version);
RETURN NEW;
END
$update_city_id$ LANGUAGE PLPGSQL;

CREATE TRIGGER update_city AFTER INSERT ON city
    FOR EACH ROW EXECUTE PROCEDURE update_city_id();


CREATE OR REPLACE FUNCTION update_realty_type_id() RETURNS TRIGGER AS $update_realty_type_id$
BEGIN
UPDATE realty_type_to_service
SET entity_id = NEW.id
WHERE entity_id IN (
    SELECT realty_type_to_service.entity_id
    FROM realty_type_to_service JOIN realty_type ON realty_type_to_service.entity_id = realty_type.id
    WHERE realty_type.self_id = NEW.self_id AND version <> NEW.version);
UPDATE realty_type_alias
SET entity_id = NEW.id
WHERE entity_id IN (
    SELECT realty_type_alias.entity_id
    FROM realty_type_alias JOIN realty_type ON realty_type_alias.entity_id = realty_type.id
    WHERE realty_type.self_id = NEW.self_id AND version <> NEW.version);
RETURN NEW;
END
$update_realty_type_id$ LANGUAGE PLPGSQL;

CREATE TRIGGER update_realty_type AFTER INSERT ON realty_type
    FOR EACH ROW EXECUTE PROCEDURE update_realty_type_id();


CREATE OR REPLACE FUNCTION update_operation_type_id() RETURNS TRIGGER AS $update_operation_type_id$
BEGIN
UPDATE operation_type_to_service
SET entity_id = NEW.id
WHERE entity_id = (
    SELECT operation_type_to_service.entity_id
    FROM operation_type_to_service JOIN operation_type ON operation_type_to_service.entity_id = operation_type.id
    WHERE operation_type.self_id = NEW.self_id AND version <> NEW.version);
UPDATE operation_type_alias
SET entity_id = NEW.id
WHERE entity_id IN (
    SELECT operation_type_alias.entity_id
    FROM operation_type_alias JOIN operation_type ON operation_type_alias.entity_id = operation_type.id
    WHERE operation_type.self_id = NEW.self_id AND version <> NEW.version);
RETURN NEW;
END
$update_operation_type_id$ LANGUAGE PLPGSQL;

CREATE TRIGGER update_operation_type AFTER INSERT ON operation_type
    FOR EACH ROW EXECUTE PROCEDURE update_operation_type_id();
