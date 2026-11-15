import sqlglot
from sqlalchemy import TextClause, text
from sqlglot import exp
from sqlglot.errors import ParseError

COLUMNS = {"respondent", "sex", "age", "avg_weight"}

# AND, OR и CASE sqlglot тоже считает функциями, их разрешаем
ALLOWED_FUNCS = (exp.Connector, exp.Case, exp.If)


def parse_condition(condition: str) -> TextClause:
    """Проверить условие и вернуть его как SQL-выражение.

    Разрешён любой SQL-синтаксис условия, кроме подзапросов, вызовов
    функций и параметров. Поля - только колонки respondent_stats.
    """
    try:
        tree = sqlglot.parse_one(condition, dialect="postgres")
    except ParseError as exc:
        raise ValueError("Некорректное условие") from exc

    if not isinstance(tree, exp.Condition):
        raise ValueError("Ожидалось условие")

    for node in tree.walk():
        if isinstance(node, (exp.Query, exp.Placeholder)):
            raise ValueError(f"Недопустимо: {node.sql()}")
        if isinstance(node, exp.Func) and not isinstance(node, ALLOWED_FUNCS):
            raise ValueError(f"Функции запрещены: {node.sql()}")
        if isinstance(node, exp.Column) and node.name.lower() not in COLUMNS:
            raise ValueError(f"Неизвестное поле: {node.name}")

    return text(f"({tree.sql(dialect='postgres')})")
