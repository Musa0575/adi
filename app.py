import streamlit as st
import pymysql

import streamlit as st
import pymysql

st.title("Aplikasi Sekolah - Game & Quiz")

# Fungsi koneksi ke MySQL
def get_db_connection():
    return pymysql.connect(
        host='db.us-losa1.bengt.wasmernet.com',
        port=16751,
        user='user_870ac2a1',
        password='PASSWORD_MYSQL_WASMER_ANDA', # Ganti dengan password MySQL Wasmer Anda
        database='db_6292e6cc',
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10
    )

# Eksekusi Koneksi
connection = None
try:
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        st.success("Berhasil terhubung ke Database MySQL!")
        st.write("Daftar Tabel di Database:", tables)
except Exception as e:
    st.error("Gagal terhubung ke Database MySQL!")
    st.exception(e)
finally:
    if connection:
        connection.close()
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
