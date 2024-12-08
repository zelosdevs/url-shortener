# file: url_shortener_gui.py

import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import base64

# Adatbázis inicializálása
DB_NAME = 'url_shortener.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_url TEXT UNIQUE,
                long_url TEXT UNIQUE
            )
        ''')
        conn.commit()

# URL rövidítése
def generate_short_url(long_url):
    url_hash = hashlib.md5(long_url.encode()).digest()
    short_url = base64.urlsafe_b64encode(url_hash[:6]).decode('utf-8')
    return short_url

# Rövid URL létrehozása és mentése adatbázisba
def shorten_url(long_url):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT short_url FROM urls WHERE long_url = ?', (long_url,))
        result = cursor.fetchone()

        if result:
            return result[0]

        short_url = generate_short_url(long_url)
        try:
            cursor.execute('INSERT INTO urls (short_url, long_url) VALUES (?, ?)', (short_url, long_url))
            conn.commit()
        except sqlite3.IntegrityError:
            return None

    return short_url

# GUI funkciók
def on_shorten():
    long_url = url_entry.get().strip()
    if not long_url:
        messagebox.showerror("Hiba", "Adj meg egy URL-t!")
        return

    short_url = shorten_url(long_url)
    if short_url:
        full_short_url = f"http://127.0.0.1/{short_url}"
        short_url_display.config(text=f"Rövidített URL: {full_short_url}")
        copy_button.config(state=tk.NORMAL)
        copy_button.full_short_url = full_short_url  # Tároljuk a rövidített URL-t a gombhoz
    else:
        messagebox.showerror("Hiba", "Nem sikerült rövidíteni az URL-t.")

def on_copy():
    full_short_url = copy_button.full_short_url
    window.clipboard_clear()
    window.clipboard_append(full_short_url)
    window.update()
    messagebox.showinfo("Másolás", "A rövidített URL a vágólapra került.")

# GUI létrehozása
def create_gui():
    global url_entry, short_url_display, copy_button, window

    window = tk.Tk()
    window.title("URL Rövidítő")
    window.geometry("400x250")

    # Címke és beviteli mező
    tk.Label(window, text="Add meg a hosszú URL-t:").pack(pady=10)
    url_entry = tk.Entry(window, width=50)
    url_entry.pack(pady=5)

    # Rövidítés gomb
    shorten_button = tk.Button(window, text="Rövidít", command=on_shorten)
    shorten_button.pack(pady=10)

    # Rövid URL megjelenítése
    short_url_display = tk.Label(window, text="")
    short_url_display.pack(pady=10)

    # Másolás gomb
    copy_button = tk.Button(window, text="Másolás", command=on_copy, state=tk.DISABLED)
    copy_button.pack(pady=10)

    window.mainloop()

if __name__ == '__main__':
    init_db()
    create_gui()
