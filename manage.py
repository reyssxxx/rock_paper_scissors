import sqlite3 as sql
from hashlib import sha256
from main import LOGGED, NAME
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
        return True
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
    print(result)
    if result:
        print('HITLER')
        cur.execute(f'SELECT password FROM users WHERE password="{password_hash}"')
        result = cur.fetchone()
        if result:
            db.commit()
            db.close()
            return True
        return False
        
    else:
        db.commit()
        db.close()
        return False

def get_stat(username):
    db = sql.connect('database.db')
    cur = db.cursor()
    
    cur.execute(f'SELECT wins, loses, draws, rocks, scissors, paper FROM users WHERE username="{username}"')
    result = cur.fetchone()
    
    if result:
        result = {'wins': result[0], 'loses': result[1], 'draws': result[2], 'rocks':result[3], 'scissors':result[4], 'paper':result[5]}
    else:
        result = {'wins': 0, 'loses': 0, 'draws': 0, 'rocks':0, 'scissors':0, 'paper':0}

    db.commit()
    db.close()
    return result

def reg_game(win: str, choice: str, username: str):
    db = sql.connect('database.db')
    cur = db.cursor()
    if choice == 'Камень':
        choice = 'rocks'
    elif choice == 'Ножницы':
        choice = 'scissors'
    elif choice == 'Бумага':
        choice = 'paper'
    cur.execute(f'UPDATE users SET {win}={win}+1, {choice}={choice}+1 WHERE username="{username}"')
    db.commit()
    db.close()
    

