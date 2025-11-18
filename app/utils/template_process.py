from pathlib import Path

import aiohttp
from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader

from app.config import SERVER_SETTINGS

TEMPLATE_DIR = Path(__file__).parent / "templates"

env_templates = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def generate_html(data: dict, template_name: str = "basic_template.html") -> str:
    template = env_templates.get_template(template_name)
    return template.render(data)


async def generate_pdf(html_content: str) -> bytes:
    # conect to Gotenberg to convert HTML to PDF
    # documentation: https://gotenberg.dev/docs/routes

    async with aiohttp.ClientSession() as session:
        form_data = aiohttp.FormData()
        form_data.add_field(
            "files", html_content, filename="index.html", content_type="text/html"
        )

        async with session.post(
            SERVER_SETTINGS.GOTENBERG_API_URL,
            data=form_data,
            auth=aiohttp.BasicAuth(
                SERVER_SETTINGS.GOTENBERG_AUTH_USERNAME,
                SERVER_SETTINGS.GOTENBERG_AUTH_PASSWORD,
            ),
        ) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=500, detail=f"PDF generation failed - {response.status}"
                )
            return await response.read()
