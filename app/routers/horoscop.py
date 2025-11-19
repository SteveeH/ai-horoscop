import urllib.parse
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket

from app.config import DB_NAMES
from app.models.horoscop import HoroscopeDB, UserInput
from app.utils.database import DB, AsyncIOMotorDatabase
from app.utils.helper import debug_llm_result
from app.utils.horoscope_process import run_horoscope_flow
from app.utils.template_process import generate_html, generate_pdf

router = APIRouter(prefix="/horoscope", tags=["horoscope"])


@router.post("/horoscope-pdf")
async def create_horoscope_pdf(
    user_input: UserInput,
    db: AsyncIOMotorDatabase = Depends(DB.get_database),
) -> Response:

    start_time = datetime.now()
    # check validation code if exists
    db_validation_code = await db[DB_NAMES.ACCESS_CODES].find_one_and_update(
        {"code": user_input.code}, {"$set": {"lastUsed": start_time}}
    )

    if not db_validation_code:
        raise HTTPException(status_code=400, detail="Nevalidní přístupový kód.")

    try:
        llm_result = await run_horoscope_flow(
            name=user_input.name,
            dob=user_input.dob,
            horoscope_type=user_input.horoscope_type,
        )
    except Exception as e:
        logger.error(f"Error during horoscope generation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Hvězdy momentálně nepřejí. Zkuste to prosím později.",
        )
    """
    llm_result = debug_llm_result()
    """

    logger.info(f"LLM processing time: {datetime.now() - start_time}")

    """ 
    with open(f"{user_input.name}_horoskop.json", "w", encoding="utf-8") as f:
        f.write(llm_result.model_dump_json(indent=4, exclude_none=True)) 
    """

    start_pdf = datetime.now()

    if llm_result.error:
        raise HTTPException(status_code=400, detail=llm_result.error)

    # Process html and generate PDF
    html_content = generate_html(
        {
            **llm_result.model_dump(exclude_none=True),
            "zodiac_cz": (
                llm_result.zodiac.get_czech_name() if llm_result.zodiac else "Unknown"
            ),
        },
        template_name="basic_template.html",
    )
    pdf_content = await generate_pdf(html_content)
    end_time = datetime.now()

    filename = f"{user_input.name.replace(" ","_")}_{start_time.strftime("%Y-%m-%d_%H:%M:%S")}_horoskop.pdf"

    # Store PDF to MongoDB gridfs
    fs = AsyncIOMotorGridFSBucket(db, bucket_name=DB_NAMES.HOROSCOPES_PDF)

    file_id = await fs.upload_from_stream(
        filename=filename,
        source=pdf_content,
        metadata={"validation_code_id": db_validation_code["_id"]},
    )

    await db[DB_NAMES.HOROSCOPES].insert_one(
        HoroscopeDB(
            **llm_result.model_dump(exclude_none=True),
            processing_time=(datetime.now() - start_time).total_seconds(),
            validation_code_id=db_validation_code["_id"],
            file_id=file_id,
        ).model_dump(exclude_none=True)
    )

    logger.info(f"PDF processing time: {end_time - start_pdf}")

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{urllib.parse.quote(filename, safe="")}"
        },
    )
