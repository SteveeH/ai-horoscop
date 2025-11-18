from datetime import datetime
from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models import ObjectId

SYSTEM_PROMPT = (
    "Píšeš horoskop, který je inspirativní, podpůrný a má praktické rady. Používáš přátelský, ale zároveň profesionální tón. Text generuj v češtině."
    "Pokud budeš potřebovat použij standardní html značky pro formátování textu - např. <br>; pro nový řádek, <strong>; pro tučný text, <em>; pro kurzívu, <h3> a <h4>; pro nadpisy sekcí, <ul>; pro odrážky a podobně."
)

BASE_PROMPT_TEMPLATE = (
    "Na základě jména {name}, data narození {dob}, astrologického čísla {astro_number} a znamení zvěrokruhu {zodiac}, vytvoř text v češtině."
    "Pokud není specificky napsáno neopakuj datum narození a vyvaruj se oslovení na začátku, tento výstup je jenom jednou z částí celého horoskopu."
    "Vytvoř následující sekci:"
)


class HoroscopeSign(StrEnum):
    ARIES = "Aries"
    TAURUS = "Taurus"
    GEMINI = "Gemini"
    CANCER = "Cancer"
    LEO = "Leo"
    VIRGO = "Virgo"
    LIBRA = "Libra"
    SCORPIO = "Scorpio"
    SAGITTARIUS = "Sagittarius"
    CAPRICORN = "Capricorn"
    AQUARIUS = "Aquarius"
    PISCES = "Pisces"

    def get_czech_name(self) -> str:
        return sign_czech_map[self]


sign_czech_map = {
    HoroscopeSign.ARIES: "Beran",
    HoroscopeSign.TAURUS: "Býk",
    HoroscopeSign.GEMINI: "Blíženec",
    HoroscopeSign.CANCER: "Rak",
    HoroscopeSign.LEO: "Lev",
    HoroscopeSign.VIRGO: "Panna",
    HoroscopeSign.LIBRA: "Váhy",
    HoroscopeSign.SCORPIO: "Štír",
    HoroscopeSign.SAGITTARIUS: "Střelec",
    HoroscopeSign.CAPRICORN: "Kozoroh",
    HoroscopeSign.AQUARIUS: "Vodnář",
    HoroscopeSign.PISCES: "Ryba",
}


class PromptObj(BaseModel):
    title: str
    prompt: str


class HoroscopeType(StrEnum):
    BASIC = "HoroscopeBasic"
    PROFI = "HoroscopeProfi"

    def get_prompts(self) -> dict[str, PromptObj]:

        PROMPTS_BASIC = {
            "definition": PromptObj(
                title="Definice znamení",
                prompt=(
                    "Začni s neformálním pozdravem 'Ahoj <jméno> ...' a uveď datum narození, "
                    "dále napiš krátkou a zajímavou definici znamení zvěrokruhu, které reprezentuje v několika odstavcích. Zaměř se na klíčové vlastnosti a prvky."
                ),
            ),
            "strengths": PromptObj(
                title="Silné a slabé stránky",
                prompt=(
                    "Popiš kladné vlastnosti znamení a jejich dopad na okolí. Vysvětli, jak inspiruje ostatní, čím vyniká v přátelství a partnerství a jaké má talenty (kreativita, organizace, komunikace apod.)."
                    " Uveď, jaké slabé stránky a problematické rysy znamení se mohou projevit. Popiš, jak ovlivňují vztahy nebo profesní život. Nabídni způsoby, jak s těmito rysy vědomě pracovat a zmírnit je."
                ),
            ),
            "career": PromptObj(
                title="Práce a kariéra",
                prompt=(
                    "Vysvětli, jak znamení přistupuje k profesnímu životu – zda touží po vedení, stabilitě, tvořivosti nebo svobodě. Uveď konkrétní oblasti a profese, ve kterých vyniká. Popiš jeho "
                    "pracovní styl a motivace (např. touha po uznání, smysluplnosti, odměnách). Přidej doporučení, jak může v kariéře dosahovat nejlepších výsledků a udržet si spokojenost."
                ),
            ),
            "love": PromptObj(
                title="Vztahy a partnerství",
                prompt=(
                    "Napiš odstavec o milostných vztazích této osoby, včetně toho, s kým si nejlépe rozumí a jaké jsou pro ni ve vztazích výzvy."
                    " Vysvětli, jak znamení prožívá lásku a vztahy. Popiš jeho očekávání od partnera, dynamiku ve vztahu a nejvíce/nejméně kompatibilní znamení. Uveď, jaké vlastnosti hledá v partnerovi."
                ),
            ),
        }

        if self == HoroscopeType.BASIC:
            return PROMPTS_BASIC
        elif self == HoroscopeType.PROFI:
            return {
                **PROMPTS_BASIC,
                "health": PromptObj(
                    title="Zdraví a pohoda",
                    prompt=(
                        "Uveď, jak znamení obvykle pečuje o své zdraví a pohodu. Popiš citlivé oblasti těla a vysvětli, jaký vliv má jeho energie na fyzickou i psychickou stránku. Navrhni doporučené "
                        "aktivity, pohyb, způsoby relaxace a regenerace. Zahrň i tipy na vyvážený životní styl a způsoby zvládání stresu."
                    ),
                ),
                "finance": PromptObj(
                    title="Finance",
                    prompt="Napiš odstavec s finančními doporučeními pro osobu v tomto znamení. Jaké má předpoklady pro správu peněz a na co si dát pozor?",
                ),
                "spirituality": PromptObj(
                    title="Duchovní rozvoj a životní motto",
                    prompt=(
                        "Vytvoř originální životní motto, které vyjadřuje filozofii znamení a jeho přístup k životu. Uveď, jak toto motto může inspirovat k sebereflexi, motivovat k dosažení cílů a "
                        "připomínat hodnoty, které jsou pro znamení nejdůležitější."
                    ),
                ),
                "tips": PromptObj(
                    title="Praktické tipy pro každodenní život",
                    prompt=(
                        "Napiš praktické rady pro každodenní život znamení. Ukaž, jak může zlepšit své vztahy, komunikaci, profesní dráhu a osobní rovnováhu. Navrhni konkrétní kroky k "
                        "sebereflexi a osobnímu rozvoji. Přidej tipy, jak vyvážit jeho silné a slabé stránky pro harmonický život."
                    ),
                ),
                "personal_questions": PromptObj(
                    title="Odpovědi na osobní otázky",
                    prompt=(
                        "Zodpověz následující otázky, které jsou specifické pro osobu v tomto znamení: Měla bych jít do předčasného důchodu? Jaké hobby bych měla zkusit?"
                    ),
                ),
            }
        else:
            return {}


class ContentResponse(BaseModel):
    key: str = ""
    title: str = ""
    content: str = ""
    error: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0


class HoroscopeState(BaseModel):

    # user inputs
    name: str = ""
    dob: str = ""
    horoscope_type: HoroscopeType = HoroscopeType.BASIC

    # processed data
    dt: Optional[datetime] = None
    zodiac: Optional[HoroscopeSign] = None
    astro_number: Optional[int] = None
    results: List[ContentResponse] = Field(default_factory=list)
    error: Optional[str] = None
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    class Config:
        arbitrary_types_allowed = True


class HoroscopeDB(HoroscopeState):
    created_at: datetime = Field(default_factory=datetime.now)
    processing_time: Optional[float] = None
    validation_code_id: Optional[ObjectId] = None
    file_id: Optional[ObjectId] = None


class UserInput(BaseModel):
    name: str
    dob: str
    code: str
    horoscope_type: HoroscopeType
