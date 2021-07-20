from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
import psycopg2
import os

app = FastAPI()
url = os.environ.get("url")


def db_connect():
    con = psycopg2.connect(
        host=os.environ.get('host'),
        database=os.environ.get('database'),
        user=os.environ.get('user'),
        port=os.environ.get('port'),
        password=os.environ.get('password'))
    cur = con.cursor()
    return con, cur


def create_tables():
    connect, cursor = db_connect()
    cursor.execute('CREATE TABLE IF NOT EXISTS files(id INTEGER PRIMARY KEY, name TEXT)')
    connect.commit()
    cursor.close()
    connect.close()


create_tables()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global url
    connect, cursor = db_connect()
    try:
        with open(f"{file.filename}", "wb") as out_file:
            content = await file.read()
            out_file.write(content)
        # print(os.stat(file.filename).st_size)
        cursor.execute("SELECT count(id) FROM files")
        max_id = int(cursor.fetchall()[0][0]) + 1
        cursor.execute(f"INSERT INTO files VALUES({max_id}, '{file.filename}')")
        connect.commit()
        return f"{url}/get/file_{max_id}"
    finally:
        cursor.close()
        connect.close()


@app.get("/get/file_{id}")
async def get_file(id):
    connect, cursor = db_connect()
    try:
        cursor.execute(f"SELECT name FROM files WHERE id={id}")
        try:
            res = cursor.fetchall()[0][0]
            print(res)
        except IndexError:
            return JSONResponse(status_code=404)
        return FileResponse(f"{res}")
    finally:
        cursor.close()
        connect.close()
