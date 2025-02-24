from fastapi import APIRouter

from app.schemas.crawler import SearchForm
from app.schemas.request.search_request import SearchRequest
from app.services.crawler import crawler_service
from app.utils.logger import get_logger

logger = get_logger()

router = APIRouter(prefix="/flight")


@router.post("/search")
async def oneway(search_request: SearchRequest):
    search_form = SearchForm(
        departure_city=search_request.departure_city,
        arrival_city=search_request.arrival_city,
        departure_date=search_request.departure_date


    )
    crawler_service.crawl_plane_infos()
