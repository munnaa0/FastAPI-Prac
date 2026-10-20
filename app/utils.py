from datetime import UTC, datetime


def friendly_date(value: datetime | None) -> str:
    # SQLite drops the timezone, so naive values are UTC.
    if value is None:
        return ""
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone().strftime("%b %d, %Y at %I:%M %p")
