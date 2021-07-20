from fastapi import FastAPI, Request, Depends, File, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.responses import StreamingResponse
import psycopg2
import os

app = FastAPI()
url = "ftp-serv.herokuapp.com/"


def db_connect():
    con = psycopg2.connect(
        host=os.environ.get('host'),
        database=os.environ.get('database'),
        user=os.environ.get('user'),
        port=os.environ.get('port'),
        password=os.environ.get('password'))
    cur = con.cursor()
    return con, cur


def error_log(error):  # просто затычка, будет дописано
    try:
        print(error)
    except Exception as e:
        print(e)
        print("Возникла ошибка при обработке errorLog (Это вообще как?)")


@app.get("/tables/create")  # потом удалить
async def create_tables():
    connect, cursor = db_connect()
    try:
        cursor.execute('CREATE TABLE IF NOT EXISTS files(id INTEGER NOT NULL UNIQUE PRIMARY KEY,'
                       'last_activity TIMESTAMP)')
        connect.commit()
        return True
    except Exception as e:
        error_log(e)
    finally:
        cursor.close()
        connect.close()


@app.get("/tables/check")  # потом удалить
async def check_tables():
    connect, cursor = db_connect()
    try:
        cursor.execute('SELECT * FROM files')
        return cursor.fetchall()
    except Exception as e:
        error_log(e)
    finally:
        cursor.close()
        connect.close()


@app.get("/get/")
async def get_file():
    pass


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global url
    connect, cursor = db_connect()
    try:
        with open(file.filename, "wb") as out_file:
            content = await file.read()
            out_file.write(content)
        print(os.stat(file.filename).st_size)
        cursor.execute("SELECT count(id) FROM links")
        max_id = int(cursor.fetchall()[0][0]) + 1
        cursor.execute(f"INSERT INTO links VALUES({max_id}, '{file.filename}')")
        connect.commit()
        return url + max_id
    except Exception as e:
        error_log(e)
    finally:
        cursor.close()
        connect.close()
