from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
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
    cursor.execute('DROP TABLE files')
    connect.commit()
    cursor.execute('CREATE TABLE IF NOT EXISTS files('
                   'id INTEGER PRIMARY KEY,'
                   'name TEXT NOT NULL,'
                   'owner TEXT NULL)')
    connect.commit()
    cursor.close()
    connect.close()


create_tables()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global url
    connect, cursor = db_connect()
    try:
        name = f"{datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S:%f')[:-3]}{file.filename}"
        with open(f"{name}", "wb") as out_file:
            content = await file.read()
            out_file.write(content)
        # print(os.stat(file.filename).st_size)
        cursor.execute("SELECT count(id) FROM files")
        max_id = int(cursor.fetchall()[0][0]) + 1
        cursor.execute(f"INSERT INTO files (id, name) VALUES ({max_id}, '{name}')")
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
