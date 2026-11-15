import csv
import os
from pathlib import Path
from time import perf_counter

import pytest

BASE_URL = os.getenv("API_URL", "http://localhost:80").rstrip("/")


@pytest.fixture(scope="session")
def respondents():
    stats = {}
    csv_path = Path(__file__).resolve().parents[1] / "data.csv"

    with csv_path.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            respondent = int(row["respondent"])
            sex, age = int(row["Sex"]), int(row["Age"])
            if respondent not in stats:
                stats[respondent] = [sex, age, 0.0, 0]
            entry = stats[respondent]
            assert entry[:2] == [sex, age], "Пол или возраст меняется"
            entry[2] += float(row["Weight"])
            entry[3] += 1

    return [(sex, age, total / count) for sex, age, total, count in stats.values()]


@pytest.mark.parametrize(
    "audience1, audience2, matches1, matches2",
    [
        pytest.param(
            "Age >= 18",
            "Age >= 18",
            lambda sex, age: age >= 18,
            lambda sex, age: age >= 18,
            id="identical",
        ),
        pytest.param(
            "Sex = 1",
            "Sex = 2",
            lambda sex, age: sex == 1,
            lambda sex, age: sex == 2,
            id="disjoint",
        ),
        pytest.param(
            "Age >= 18",
            "Sex = 2 AND Age >= 18",
            lambda sex, age: age >= 18,
            lambda sex, age: sex == 2 and age >= 18,
            id="second-is-subset",
        ),
        pytest.param(
            "Sex = 2 AND Age >= 18",
            "Age >= 18",
            lambda sex, age: sex == 2 and age >= 18,
            lambda sex, age: age >= 18,
            id="first-is-subset",
        ),
        pytest.param(
            "Age BETWEEN 18 AND 35",
            "Sex = 2 AND Age >= 18",
            lambda sex, age: 18 <= age <= 35,
            lambda sex, age: sex == 2 and age >= 18,
            id="partial-overlap",
        ),
        pytest.param(
            "Age BETWEEN 18 AND 35",
            "Age = 18 OR Age = 35",
            lambda sex, age: 18 <= age <= 35,
            lambda sex, age: age in (18, 35),
            id="between-boundaries",
        ),
        pytest.param(
            "Age >= 18",
            "Age < 0",
            lambda sex, age: age >= 18,
            lambda sex, age: age < 0,
            id="empty-second",
        ),
        pytest.param(
            "Age < 0",
            "Age >= 18",
            lambda sex, age: age < 0,
            lambda sex, age: age >= 18,
            id="empty-first",
        ),
    ],
)
def test_get_percent(
    respondents,
    audience1,
    audience2,
    matches1,
    matches2,
    api_client,
    timings,
    request,
):
    total = sum(weight for sex, age, weight in respondents if matches1(sex, age))
    common = sum(
        weight
        for sex, age, weight in respondents
        if matches1(sex, age) and matches2(sex, age)
    )
    expected = common / total if total else 0.0

    samples = []
    for _ in range(10):
        started = perf_counter()
        response = api_client.get(
            f"{BASE_URL}/getPercent",
            params={"audience1": audience1, "audience2": audience2},
        )
        elapsed_ms = (perf_counter() - started) * 1000

        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, dict)
        assert set(data) == {"percent"}
        assert type(data["percent"]) in (int, float)
        # DOUBLE PRECISION может дать 1.0000000000000004 вместо 1.
        assert -1e-10 <= data["percent"] <= 1 + 1e-10
        assert data["percent"] == pytest.approx(expected, rel=1e-10, abs=1e-10)
        samples.append(elapsed_ms)

    timings.append((request.node.callspec.id, samples, BASE_URL))


@pytest.mark.parametrize(
    "audience1, audience2, matches1, matches2",
    [
        pytest.param(
            "Age IN (18, 35)",
            "NOT Sex = 1",
            lambda sex, age: age in (18, 35),
            lambda sex, age: sex != 1,
            id="in-not",
        ),
        pytest.param(
            "CASE WHEN Sex = 1 THEN Age > 30 ELSE Age > 20 END",
            "age % 2 = 0",
            lambda sex, age: age > 30 if sex == 1 else age > 20,
            lambda sex, age: age % 2 == 0,
            id="case-arithmetic",
        ),
    ],
)
def test_other_sql_syntax(respondents, audience1, audience2, matches1, matches2,
                          api_client):
    total = sum(weight for sex, age, weight in respondents if matches1(sex, age))
    common = sum(
        weight
        for sex, age, weight in respondents
        if matches1(sex, age) and matches2(sex, age)
    )
    response = api_client.get(
        f"{BASE_URL}/getPercent",
        params={"audience1": audience1, "audience2": audience2},
    )
    assert response.status_code == 200, response.text
    assert response.json()["percent"] == pytest.approx(common / total, rel=1e-10)


@pytest.mark.parametrize("condition", ["Age", "Age = 5 = 5"])
def test_condition_rejected_by_database_returns_422(api_client, condition):
    response = api_client.get(
        f"{BASE_URL}/getPercent",
        params={"audience1": condition, "audience2": "Sex = 2"},
    )
    assert response.status_code == 422, response.text
