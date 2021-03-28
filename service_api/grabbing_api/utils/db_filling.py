import sys
import os

sys.path.append(os.getcwd())

from service_api import Session
from service_api.models import RealtyType, OperationType


def fill_db(session):
    operation_types = []
    op_values = [
        (0, "Будь яка операція"), (1, "Продаж"),
        (3, "Довгострокова оренда"), (4, "Подобова оренда"),
    ]

    for val in op_values:
        id, name = val
        operation_types.append(OperationType(original_id=id, name=name))

    realty_types = []
    rt_values = [
        (2, "Квартира"), (3, "Кімнати"), (5, "Дім"), (6, "Ділянка"),
        (7, "Дачі"), (11, "Офісні приміщення"), (12, "Офісні будвілі"), (14, "Площі"),
        (15, "Склади"), (16, "Виробництво"), (17, "Ресторани"), (18, "Обєкт"),
        (19, "Готель"), (20, "Пансіонат"), (21, "Приміщення вільного призначення"), (22, "Бізнес")
    ]

    for val in rt_values:
        id, name = val
        operation_types.append(RealtyType(original_id=id, name=name))

    session.add_all(operation_types)
    session.add_all(realty_types)
    session.commit()
    session.close()


s = Session()
fill_db(s)
