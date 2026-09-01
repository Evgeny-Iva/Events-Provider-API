import re

def parser_seats_patern(pattern: str) -> list[dict]:
    """Парсит строку паттерна мест"""
    if not pattern:
        return []

    parts = pattern.split(",")
    result = []

    for part in parts:
        match = re.match(r"([A-Z])(\d+)-(\d+)", part)
        if not match:
            raise ValueError(f"Некорректный паттерн: {part}")

        section = match.group(1)
        start = int(match.group(2))
        end = int(match.group(3))

        if start > end:
            raise ValueError(f"Начало ({start}) больше конца ({end}) в {part}")

        if start < 0 or end < 0:
            raise ValueError(
                f"Номера мест не могут быть отрицательными: {part}"
            )

        result.append({
            "section": section,
            "start": start,
            'end': end
        })

    return result
