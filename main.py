from fastapi import FastAPI, Query, Header, HTTPException
import os
import psycopg

app = FastAPI()

DATABASE_URL = os.environ.get("DATABASE_URL")
API_KEY = os.environ.get("API_KEY")

def get_conn():
    return psycopg.connect(DATABASE_URL)

@app.get("/")
def home():
    return {"message": "Rungus API is running"}

@app.get("/words")
def get_words(
    rungus_text: str | None = Query(default=None),
    english_meaning: str | None = Query(default=None),
    type: str | None = Query(default=None),
    category: str | None = Query(default=None),
    x_api_key: str | None = Header(default=None)
):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    query = """
        SELECT id, rungus_text, english_meaning, category, type
        FROM words
        WHERE 1=1
    """
    params = []

    if rungus_text:
        query += " AND rungus_text ILIKE %s"
        params.append(f"%{rungus_text}%")

    if english_meaning:
        query += " AND english_meaning ILIKE %s"
        params.append(f"%{english_meaning}%")

    if type:
        query += " AND type = %s"
        params.append(type)

    if category:
        query += " AND category = %s"
        params.append(category)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

    return {
        "results": [
            {
                "id": r[0],
                "rungus_text": r[1],
                "english_meaning": r[2],
                "category": r[3],
                "type": r[4],
            }
            for r in rows
        ]
    }