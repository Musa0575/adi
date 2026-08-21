import streamlit as st
import pymysql

# Konfigurasi Koneksi MySQL Wasmer
def get_db_connection():
    return pymysql.connect(
        host='db.us-losa1.bengt.wasmernet.com',
        port=16751,
        user='user_870ac2a1',
        password='PASSWORD_MYSQL_WASMER_ANDA',
        database='db_6292e6cc',
        cursorclass=pymysql.cursors.DictCursor
    )

st.title("Aplikasi Sekolah - Game & Quiz")

# Contoh mengambil/menampilkan data dari MySQL
try:
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        st.success("Berhasil terhubung ke Database MySQL!")
        st.write("Daftar Tabel di Database:", tables)
finally:
    connection.close()
