from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from furl import furl

app = FastAPI()

fake_items_db = [
    {"id": 1, "title": "test meal 01", "date": "2023-08-28"},
    {"id": 2, "title": "test meal 02", "date": "2023-08-29"},
    {"id": 3, "title": "test meal 03", "date": "2023-09-01"},
]
base_path = furl("https://recipes.wooster.xyz/api")


def human_date_to_date(value: str | int) -> datetime:
    today = datetime.now().date()

    if isinstance(value, str):
        text = value.lower()
        if text == "yesterday":
            value = -1
        elif text == "today":
            value = 0
        elif text == "tomorrow":
            value = 1
        else:
            try:
                value = int(value)
            except ValueError as err:
                raise HTTPException(
                    status_code=400, detail="Invalid date entry."
                ) from err

    return today + timedelta(days=value)


def is_date(value: str) -> bool:
    try:
        value = datetime.strptime(value, "%Y-%m-%d")
        # value = datetime(value)
        return True
    except ValueError:
        return False


def make_date(value: str) -> bool:
    try:
        value = datetime.strptime(value, "%Y-%m-%d").date()
        return value
    except ValueError:
        value = human_date_to_date(value)
        return value


@app.get("/meal-plan")
async def get_data(
    from_date: int | str | None = None,
    to_date=None,
    offset: int | None = None,
    ordering: str | None = None,
):
    if from_date:
        from_date = make_date(from_date)

    if to_date:
        to_date = make_date(to_date)

    if all([from_date, to_date, offset]):
        raise HTTPException(
            status_code=400,
            detail="Only two of 'from_date', 'to_date', and 'offset' allowed.",
        )

    if from_date and offset:
        other_date = from_date + timedelta(days=offset)
        if offset > 0:
            to_date = other_date
        if offset < 0:
            to_date = from_date
            from_date = other_date

    elif to_date and offset:
        other_date = to_date + timedelta(days=offset)
        if offset < 0:
            from_date = other_date
        if offset > 0:
            from_date = to_date
            to_date = other_date

    if from_date and to_date:
        if to_date < from_date:
            raise HTTPException(
                status_code=404, detail="'to_date' cannot be before 'from_date'."
            )

    new_base_path = base_path.copy()
    new_base_path.path = new_base_path.path / "meal-plan/"
    api_url = generate_api_call(new_base_path, from_date, to_date)

    return api_url.url


def generate_api_call(
    base_url,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
):
    new_url = base_url.copy()
    if from_date:
        new_url.args["from_date"] = from_date
    if to_date:
        new_url.args["to_date"] = to_date

    return new_url
