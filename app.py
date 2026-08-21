import streamlit as st
import sqlite3

st.title("Aplikasi Sekolah - Game & Quiz")

# Fungsi koneksi ke SQLite
def get_db_connection():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

try:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ambil daftar tabel
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    st.success("Berhasil terhubung ke Database SQLite!")
    st.write("Daftar Tabel di Database:", [t['name'] for t in tables])
    conn.close()
except Exception as e:
    st.error("Gagal terhubung ke Database!")
    st.exception(e)
