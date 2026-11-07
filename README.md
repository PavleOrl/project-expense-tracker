# My Expenses - the project

A complete system for tracking personal expenses: **a web application, a RESTful service and a database**.
It is Homework 2 (the expense tracker) grown into the architecture of module 07:

```text
browser  <-- HTML -->  web application  <-- JSON -->  RESTful service  <-->  database
                       web-app                         rest-service           expenses.db (SQLite)
                       localhost:8000                  localhost:8001
```

It is built the same way as the course sample `07-python-fastapi-rest-sqlite/02-complete-system-db`
(actors and countries); here the two resources are **expenses** and **categories**, and an expense refers to its
category by `category_id`. If something is unclear, look at the same file in that sample.

## Starting the system

Once, in this folder (the folder with `requirements.txt`):

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

The system consists of two programs. Start them in **two terminals** (in VS Code: the `+` in the terminal panel),
the service first. In each terminal, activate the environment first: `.venv\Scripts\activate`.

```text
cd rest-service
python main.py
```

```text
cd web-app
python main.py
```

Then open <http://localhost:8000> (the application) and <http://localhost:8001/docs> (the service - here every
request can be tried with the button *Try it out*). If the service is not running, the application shows a page that says so.

The database `rest-service/expenses.db` is made, with sample categories and expenses, the first time the service
is started. **To start again from the sample data, stop the service and delete `expenses.db`.**

## What the system can do

| Page | Address | What it does |
|---|---|---|
| Dashboard | `/dashboard` | one month: the total, the number of expenses, the largest one; for every category, spending **against its monthly budget** (green, yellow from 80%, red with *over budget*); the five newest expenses; arrows for the previous and next month |
| Expenses | `/expenses` | the table of the expenses with the total; adding; deleting; filtering by category, month and text |
| Expense detail | `/expensedetail/3` | one expense, and a form for changing it |
| Categories | `/categories` | adding, renaming, deleting categories, and setting their monthly budgets |

## The database

Two tables, connected by a foreign key (one category has many expenses):

```text
category                              expense
-----------------------------         -----------------------------------------
category_id   INTEGER  PK      1 ---<  expense_id    INTEGER  PK
name          VARCHAR(100) UNIQUE      date          DATE  (with an index)
monthly_budget NUMERIC(12,2)           description   VARCHAR(255)
                                       amount        NUMERIC(12,2)
                                       category_id   INTEGER  FK -> category
```

The tables are not written in SQL by hand: SQLModel makes them from the classes in `rest-service/models`
(`SQLModel.metadata.create_all(engine)` in `database.py`). The database itself guards two rules:

- **foreign key** - a category that still has expenses can not be deleted;
- **unique** - two categories can not have the same name.

When a rule is broken, SQLAlchemy raises `IntegrityError`, and the service answers `409 Conflict` (`main.py`).

## The RESTful service (`rest-service`, port 8001)

| Method | Address | What it does | Answer |
|---|---|---|---|
| GET | `/api/categories` | all the categories | 200 + list |
| GET | `/api/categories/{id}` | one category | 200, or 404 |
| POST | `/api/categories` | add a category | 201 + the new category + header `Location`; 409 if the name exists |
| PUT | `/api/categories/{id}` | change a category | 204; 404; 400 if the ids differ |
| DELETE | `/api/categories/{id}` | delete a category | 204; 404; 409 if it has expenses |
| GET | `/api/expenses?category_id=&month=&text=` | the expenses, the newest first; the parameters are optional filters | 200 + list; 422 for a bad month |
| GET | `/api/expenses/{id}` | one expense | 200, or 404 |
| POST | `/api/expenses` | add an expense | 201 + the new expense + `Location`; 400 for an unknown category |
| PUT | `/api/expenses/{id}` | change an expense | 204; 404; 400 |
| DELETE | `/api/expenses/{id}` | delete an expense | 204; 404 |

Data that breaks the rules of the DTOs (an empty description, an amount that is not greater than zero,
a negative budget) is refused with `422` before our code is even called.

The layers of the service:

| Folder | What it contains |
|---|---|
| `routers/` | receive the requests and send the answers; check what the database can not (e.g. that the category exists) |
| `repositories/` | read and write the database - the only place that builds queries (`select(...).where(...)`) |
| `models/` | `Category`, `Expense` - the classes mapped to the tables (`table=True`) |
| `dtos/` | `CategoryDTO`, `ExpenseDTO` - the shape of the JSON; `ExpenseDTO` also carries `category_name`, taken from the other table |
| `database.py` | the engine, the session, the repositories for dependency injection, the sample data |

## The web application (`web-app`, port 8000)

The same structure as Homework 2, with one big difference: **it has no data of its own**.

| File or folder | What it contains |
|---|---|
| `services/expense_service.py`, `category_service.py` | the abstract classes - WHAT can be done |
| `services/rest_expense_service.py`, `rest_category_service.py` | HOW: HTTP requests to the service with `httpx2`, JSON turned into `Expense` / `Category` objects |
| `dependencies.py` | makes the services and hands them to the pages; the address of the service is `REST_SERVICE_URL` |
| `pages/` | one module per page; they know only the abstract classes |
| `templates/components/` | `ExpenseForm` (used for adding and for changing), `BudgetBars`, `AppMessages` |
| `main.py` | the error page when the service does not answer (`httpx2.HTTPError`), and the page *Invalid input* |

**Compare with Homework 2:** `FileExpenseService` was replaced by `RestExpenseService`, and `dependencies.py`
now hands over the new class. The pages and templates hardly changed - that is what the abstract class was for.

## What happens when an expense is added - from the click to the database and back

1. The browser sends the form `ExpenseForm` with POST to the web application: `/expenses`.
2. `add()` in `web-app/pages/expenses.py` receives the values (FastAPI converts the date and the amount)
   and calls `expense_service.add(...)`.
3. `RestExpenseService.add()` sends `POST http://localhost:8001/api/expenses` with a JSON body.
4. In the service, FastAPI turns the JSON into an `ExpenseDTO` and checks its rules (422 if broken);
   `create()` in `routers/expense.py` checks that the category exists (400 if not).
5. `ExpenseRepository.create()` makes an `Expense`, `session.add()` + `session.commit()` write a row
   into the table `expense` (an `INSERT`), `refresh()` reads back its new `expense_id`.
6. The service answers `201 Created` with the new expense as JSON.
7. The web application adds a message and answers the browser with a redirect (`303`) to `/expenses`.
8. The browser asks for `/expenses` with GET; the web application asks the service for `GET /api/expenses`,
   and the template `expenses.html` turns the list into an HTML table.

## Things to be able to explain

- **Why two programs?** The service can have other clients too (a mobile app, another web site), and the database
  is reachable only through the service, which checks every change. The web application only shows the data.
- **What is a DTO and why is it not the same as the model?** The model is a row of a table; the DTO is what the
  client needs. `ExpenseDTO` has `category_name`, which is not a column of `expense`.
- **Why `Location` and `201`?** That is how REST says "created, and here is where it lives".
- **Why does the web application check the form, when the service checks it anyway?** To give a friendly
  message; the service has the last word, because a request can come from any client.
- **Where is the SQL?** SQLModel writes it from the Python code in the repositories; the comment in
  `ExpenseRepository.get_all()` shows the statement it produces. Run the service and look at the table data with
  any SQLite viewer (e.g. the VS Code extension *SQLite Viewer*) to see the rows.
- **Why `Decimal` and `NUMERIC(12,2)`?** Money must be exact. The amount even travels as text in the JSON (`"990.50"`).
- **What happens if the service is down?** `httpx2` raises an error, and `service_error()` in `web-app/main.py`
  shows a page that explains it, instead of a crash.

## Ideas, if you want to add something of your own

- income as well as expenses (a new table, or a column `kind`), and the balance of the month;
- an endpoint `GET /api/reports/{month}` that adds up the totals with SQL (`GROUP BY category_id`) in the service;
- a page with the twelve months of a year, side by side;
- moving to Supabase (PostgreSQL): see `07-python-fastapi-rest-supabase`.

## Publishing on GitHub

Create a new repository on GitHub (without a README), then, in this folder:

```text
git init
git add .
git commit -m "Project: My Expenses - web application, RESTful service and database"
git branch -M main
git remote add origin https://github.com/YOUR-NAME/my-expenses.git
git push -u origin main
```

The file `.gitignore` keeps `.venv`, `__pycache__` and the database file out of the repository -
the service makes a new database on its first start.
