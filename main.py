from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
import psycopg2
import os

app = FastAPI(redoc=None)
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
    cursor.execute('CREATE TABLE IF NOT EXISTS files('
                   'id INTEGER PRIMARY KEY,'
                   'name TEXT NOT NULL,'
                   'owner TEXT NULL)')
    connect.commit()
    cursor.close()
    connect.close()


@app.post("/upload", tags=['Upload file'])
async def upload_file(file: UploadFile = File(...)):
    global url
    connect, cursor = db_connect()
    try:
        name = f"{datetime.utcnow().strftime('%d-%m-%Y_%H:%M:%S.%f')[:-3]}{file.filename}"
        name.replace(':', '')
        with open(f"storage/{name}", "wb") as out_file:
            out_file.write(await file.read())
        print(name)
        # print(os.stat(file.filename).st_size)
        cursor.execute("SELECT count(id) FROM files")
        max_id = int(cursor.fetchone()[0]) + 1
        cursor.execute(f"INSERT INTO files (id, name) VALUES ({max_id}, '{name}')")
        connect.commit()
        return f"{url}/get/file_{max_id}"
    finally:
        cursor.close()
        connect.close()


@app.get("/get/file_{id}", tags=['Get file'])
async def get_file(id: int):
    connect, cursor = db_connect()
    cursor.execute(f"SELECT name FROM files WHERE id={id}")
    try:
        return FileResponse(f"storage/{cursor.fetchone()[0]}")
    except IndexError:
        return JSONResponse(status_code=404)
    finally:
        cursor.close()
        connect.close()


@app.get("/get/owner_files", tags=['Get file'])
async def get_owner_files(owner: str):
    connect, cursor = db_connect()
    cursor.execute(f"SELECT name FROM files")
    try:
        return FileResponse(f"{cursor.fetchall()[0][0]}")
    except IndexError:
        return JSONResponse(status_code=404)
    finally:
        cursor.close()
        connect.close()


create_tables()
