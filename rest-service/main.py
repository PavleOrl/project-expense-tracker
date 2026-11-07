"""
The project, part 1: the RESTful service of My Expenses.

The service keeps the categories and the expenses in a SQLite database, and offers them
to its clients as JSON. Both resources have all the operations (reading, adding,
changing, deleting). The service is built in layers:

    routers       receive the requests and send the answers        (the folder routers)
    repositories  read and write the database                      (the folder repositories)
    models        the classes mapped to the tables                 (the folder models)
    DTOs          the shape of the data that travels to clients    (the folder dtos)

Start it with      python main.py
and then open      http://localhost:8001/docs

The second part of the system, the web application (the folder web-app),
is a client of this service - so start the service first.
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError

from database import create_database
from routers import category, expense

app = FastAPI(title="My Expenses - REST service")

# CORS: which web pages are allowed to call this service from JavaScript in a browser.
# Our web application calls the service from Python, on the server, where this rule
# does not apply - but a client that runs in a browser would need it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

create_database()

app.include_router(category.router)
app.include_router(expense.router)


@app.exception_handler(IntegrityError)
def change_refused(request: Request, error: IntegrityError):
    """
    The database refuses a change that would break its rules - e.g. deleting a category
    that has expenses (foreign key), or a second category with the same name (unique).
    """
    return JSONResponse(
        status_code=409,
        content={"detail": "The database refused the change, because it would break the integrity of the data"},
    )


@app.get("/", include_in_schema=False)
def index():
    """The home address leads to the documentation of the service."""
    return RedirectResponse("/docs")


if __name__ == "__main__":
    uvicorn.run("main:app", port=8001, reload=True)
