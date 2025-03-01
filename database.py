import sqlite3 as sql
from hashlib import sha256

# колво игр, по категориям, винрейт, самый частоиспользуемый знак

def registration(username: str, password: str):
    m = sha256(password.encode())
    password_hash = m.hexdigest()

    db = sql.connect('database.db')
    cur = db.cursor()

    cur.execute(f'SELECT username FROM users WHERE username="{username}"')
    result = cur.fetchone()
    print(result)
    if not result:
        cur.execute(f'INSERT INTO users (username, password) VALUES ("{username}", "{password_hash}")')
        db.commit()
        db.close()
    else:
        db.commit()
        db.close()
        return False
    
def login(username: str, password: str):
    m = sha256(password.encode())
    password_hash = m.hexdigest()

    db = sql.connect('database.db')
    cur = db.cursor()

    cur.execute(f'SELECT username FROM users WHERE username="{username}"')
    result = cur.fetchone()
    if result:
        cur.execute(f'SELECT password FROM users WHERE password="{password_hash}"')
        db.commit()
        db.close()
        global logged
        global name
        logged = True
        name = username
        return True
    else:
        db.commit()
        db.close()
        return False

def get_stat():
    global logged
    global name
    if logged:
        db = sql.connect('database.db')
        cur = db.cursor()
        
        cur.execute(f'SELECT wins, loses, draws, rocks, scissors, paper FROM users WHERE username="{name}"')
        result = cur.fetchone()
        db.commit()
        db.close()
        return result

    else:
        return False
    

def reg_game(win: str, choice: str):
    global logged
    global name
    db = sql.connect('database.db')
    cur = db.cursor()
    if logged:
        cur.execute(f'UPDATE users SET {win}={win}+1, {choice}={choice}+1')
        db.commit()
        db.close()
        return True
    else:
        return False

