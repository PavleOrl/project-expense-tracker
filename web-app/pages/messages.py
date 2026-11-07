from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse

from dependencies import get_messaging_service
from services.messaging_service import MessagingService

router = APIRouter()


@router.post("/messages/clear")
def clear_messages(
    request: Request,
    messaging_service: Annotated[MessagingService, Depends(get_messaging_service)],
):
    messaging_service.clear()

    # back to the page on which the button was pressed (the browser sends its address)
    return RedirectResponse(request.headers.get("referer", "/"), status_code=status.HTTP_303_SEE_OTHER)
