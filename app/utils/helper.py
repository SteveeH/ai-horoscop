import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.models.horoscop import HoroscopeSign, HoroscopeState


def validate_name(name: str) -> bool:
    return len(name.strip()) > 0


def validate_dob(date_of_birth: str | datetime) -> Optional[datetime]:
    try:
        if isinstance(date_of_birth, datetime):
            return date_of_birth
        else:
            dob_str = date_of_birth.strip()
            return datetime.strptime(dob_str, "%d.%m.%Y")

    except ValueError:
        return None


def get_zodiac(day: int, month: int) -> HoroscopeSign:
    zodiacs = [
        (HoroscopeSign.CAPRICORN, (1, 1), (1, 19)),
        (HoroscopeSign.AQUARIUS, (1, 20), (2, 18)),
        (HoroscopeSign.PISCES, (2, 19), (3, 20)),
        (HoroscopeSign.ARIES, (3, 21), (4, 19)),
        (HoroscopeSign.TAURUS, (4, 20), (5, 20)),
        (HoroscopeSign.GEMINI, (5, 21), (6, 20)),
        (HoroscopeSign.CANCER, (6, 21), (7, 22)),
        (HoroscopeSign.LEO, (7, 23), (8, 22)),
        (HoroscopeSign.VIRGO, (8, 23), (9, 22)),
        (HoroscopeSign.LIBRA, (9, 23), (10, 22)),
        (HoroscopeSign.SCORPIO, (10, 23), (11, 21)),
        (HoroscopeSign.SAGITTARIUS, (11, 22), (12, 21)),
        (HoroscopeSign.CAPRICORN, (12, 22), (12, 31)),
    ]
    # Korektní porovnání pro data napříč měsíci
    date = (month, day)
    for sign, start, end in zodiacs:
        if start <= date <= end:
            return sign
    # Speciální případ pro Kozoroha na přelomu roku
    if date >= (12, 22) or date <= (1, 19):
        return HoroscopeSign.CAPRICORN

    raise ValueError("Invalid date for zodiac sign determination")


def astrological_number(dob_str: str) -> int:
    total = sum(int(c) for c in dob_str if c.isdigit())
    return total % 9 or 9


def debug_llm_result() -> HoroscopeState:
    file_path = Path(__file__).parent / "debug_horoscope.json"
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return HoroscopeState.model_validate(data)
