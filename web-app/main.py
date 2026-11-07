"""
The project, part 2: the web application of My Expenses.

    browser  <-- HTML -->  web application  <-- JSON -->  RESTful service  <-->  database
                           (this program)                 (the folder rest-service)

The application shows and changes expenses and categories. It has no data of its own:
its services call the RESTful service for everything.

Pages:
    /dashboard               one month: the total, and the spending against the budget of every category
    /expenses                all the expenses: filtering, adding, deleting
    /expensedetail/{id}      one expense: its details and a form for changing it
    /categories              the categories and their monthly budgets

Start the RESTful service first (python main.py in the folder rest-service), then
start this application with      python main.py
and open                         http://localhost:8000
"""

import httpx2
import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from dependencies import REST_SERVICE_URL
from pages import categories, dashboard, expense_detail, expenses, messages
from templating import BASE_DIR, templates

app = FastAPI(title="My Expenses")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(dashboard.router)
app.include_router(expenses.router)
app.include_router(expense_detail.router)
app.include_router(categories.router)
app.include_router(messages.router)


@app.get("/")
def index():
    """The application starts with the dashboard."""
    return RedirectResponse("/dashboard")


@app.exception_handler(httpx2.HTTPError)
def service_error(request: Request, error: httpx2.HTTPError):
    """Shown when the RESTful service does not answer, or answers with an error."""
    return templates.TemplateResponse(
        request,
        "error.html",
        {"service_url": REST_SERVICE_URL, "error": f"{type(error).__name__}: {error}"},
        status_code=503,
    )


@app.exception_handler(RequestValidationError)
def invalid_input(request: Request, exc: RequestValidationError):
    """
    FastAPI calls this function when a value cannot be converted
    (for example, a text where a number or a date is expected).
    Instead of an error in the JSON format, the user gets a page that explains it.
    """
    return templates.TemplateResponse(request, "invalid_input.html", {"errors": exc.errors()}, status_code=422)


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
