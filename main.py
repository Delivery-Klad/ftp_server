from fastapi import FastAPI, Request, Depends, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
import psycopg2
import os

app = FastAPI()
url = "ftp-serv.herokuapp.com"


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
        cursor.execute('CREATE TABLE IF NOT EXISTS files(id INTEGER PRIMARY KEY, name TEXT)')
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


@app.get("/get/file_{id}")
async def get_file(id):
    connect, cursor = db_connect()
    try:
        cursor.execute(f"SELECT file FROM files WHERE id={id}")
        try:
            res = cursor.fetchall()[0][0]
            print(res)
        except IndexError:
            return JSONResponse(status_code=404)
        return FileResponse(f"{res}")
    except Exception as e:
        error_log(e)
    finally:
        cursor.close()
        connect.close()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global url
    connect, cursor = db_connect()
    try:
        with open(f"{file.filename}", "wb") as out_file:
            content = await file.read()
            out_file.write(content)
        print(os.stat(file.filename).st_size)
        cursor.execute("SELECT count(id) FROM files")
        max_id = int(cursor.fetchall()[0][0]) + 1
        cursor.execute(f"INSERT INTO files VALUES({max_id}, '{file.filename}')")
        connect.commit()
        return f"{url}/get/file_{max_id}"
    except Exception as e:
        error_log(e)
    finally:
        cursor.close()
        connect.close()
