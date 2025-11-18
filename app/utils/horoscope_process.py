import asyncio
import json
from datetime import datetime
from typing import List

import aiohttp
from langgraph.graph import END, StateGraph
from loguru import logger

from app.config import SERVER_SETTINGS
from app.models.horoscop import (
    BASE_PROMPT_TEMPLATE,
    SYSTEM_PROMPT,
    ContentResponse,
    HoroscopeState,
    HoroscopeType,
)
from app.utils.helper import (
    astrological_number,
    get_zodiac,
    validate_dob,
    validate_name,
)


def input_validator(state: HoroscopeState) -> HoroscopeState:
    if not validate_name(state.name):
        state.error = "Neplatné jméno. Jméno nesmí být prázdné."
        return state
    dt = validate_dob(state.dob)
    if not dt:
        state.error = "Neplatný formát data narození. Použijte formát DD.MM.RRRR."
        return state
    state.dt = dt
    return state


def enrich_state(state: HoroscopeState) -> HoroscopeState:
    if state.dt:
        state.zodiac = get_zodiac(state.dt.day, state.dt.month)
        state.astro_number = astrological_number(state.dob)
    return state


async def generate_content_gemini(
    session: aiohttp.ClientSession,
    key: str,
    user_prompt: str,
) -> ContentResponse:
    """Generates content using the Gemini API.

    REST documentation: https://ai.google.dev/api/generate-content#v1beta.GenerationConfig
    ---
    Args:
        session (aiohttp.ClientSession): The HTTP session to use for the request.
        key (str): A unique key to identify the prompt.
        user_prompt (str): The prompt text to send to the Gemini API.
    """
    time_start = datetime.now()
    logger.debug(f"Running generation for '{key}' at {time_start.isoformat()}")

    # TODO: try different temperature values - default for gemini-2.5-flash is 1.0
    for attempt in range(SERVER_SETTINGS.REQUEST_RETRY_COUNT):
        try:
            async with session.post(
                f"{SERVER_SETTINGS.GEMINI_API_URL}?key={SERVER_SETTINGS.GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": user_prompt}]}],
                    "tools": [{"google_search": {}}],
                    "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                    "generationConfig": {
                        "candidateCount": 1,
                    },
                },
            ) as response:
                response.raise_for_status()
                data: dict = await response.json()

                """ with open(
                    f"debug_response_{key}_{datetime.now().strftime("%d.%m.%Y_%H:%M:%S")}.json",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(json.dumps(data, ensure_ascii=False, indent=4)) """

                text_content = (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )

                usage_metadata: dict = data.get("usageMetadata", {})
                input_tokens = usage_metadata.get("promptTokenCount", 0)
                output_tokens = usage_metadata.get("candidatesTokenCount", 0)

                return ContentResponse(
                    key=key,
                    content=text_content,
                    error=None,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )

        except aiohttp.ClientResponseError as err:
            if (
                err.status in {500, 503}
                and attempt < SERVER_SETTINGS.REQUEST_RETRY_COUNT - 1
            ):
                delay = 2**attempt
                await asyncio.sleep(delay)
            else:
                raise err
        finally:
            time_end = datetime.now()
            logger.debug(
                f"Generation for key '{key}' ended in {time_end.isoformat()}, it takes {time_end - time_start}"
            )

    return ContentResponse(
        key=key,
        content="",
        error="Nepodařilo se vygenerovat odpověď.",
        input_tokens=0,
        output_tokens=0,
    )


async def generate_all_outputs(state: HoroscopeState) -> HoroscopeState:

    prompts_to_run = state.horoscope_type.get_prompts()

    if not prompts_to_run:
        state.error = "Neznámý typ horoskopu."
        return state

    base_prompt = BASE_PROMPT_TEMPLATE.format(
        name=state.name,
        dob=state.dob,
        astro_number=state.astro_number,
        zodiac=state.zodiac.get_czech_name() if state.zodiac else "Unknown",
    )

    async with aiohttp.ClientSession() as session:
        tasks = {}
        for key, data in prompts_to_run.items():
            full_prompt = f"{base_prompt} {data.prompt}"
            tasks[key] = generate_content_gemini(session, key, full_prompt)

        results: List[ContentResponse] = await asyncio.gather(*tasks.values())

        # Collect results
        for key, response in zip(tasks.keys(), results):

            if response.error is not None:
                error_msg = (
                    f"Error in generating response for key {key}: {response.error}"
                )
                if state.error is None:
                    state.error = error_msg
                else:
                    state.error += f"\n{error_msg}"

                continue

            response.title = prompts_to_run[key].title
            state.results.append(response)
            state.total_input_tokens += response.input_tokens
            state.total_output_tokens += response.output_tokens

    return state


def should_continue(state: HoroscopeState) -> str:
    return "end" if state.error else "continue"


workflow = StateGraph(HoroscopeState)
workflow.add_node("validate", input_validator)
workflow.add_node("enrich", enrich_state)
workflow.add_node("generate_outputs", generate_all_outputs)
workflow.set_entry_point("validate")
workflow.add_conditional_edges(
    "validate", should_continue, {"continue": "enrich", "end": END}
)
workflow.add_edge("enrich", "generate_outputs")
workflow.add_edge("generate_outputs", END)
compiled_graph = workflow.compile()


async def run_horoscope_flow(
    name: str, dob: str, horoscope_type: HoroscopeType
) -> HoroscopeState:
    user_state = HoroscopeState(name=name, dob=dob, horoscope_type=horoscope_type)
    final_state_dict = await compiled_graph.ainvoke(user_state)
    return HoroscopeState.model_validate(final_state_dict)


if __name__ == "__main__":

    draw_mmd = compiled_graph.get_graph().draw_mermaid()

    with open("horoscope_workflow.mmd", "w", encoding="utf-8") as f:
        f.write(draw_mmd)
