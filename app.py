import streamlit as st
import sqlite3

# Set Konfigurasi Halaman Web
st.set_page_config(page_title="Aplikasi Portal Sekolah", page_icon="🎓", layout="wide")

# Fungsi Koneksi Database
def get_db_connection():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

# Header Tampilan Depan
st.title("🎓 Portal Belajar & Game Sekolah")
st.write("Selamat datang! Pilih menu di bawah untuk mulai belajar atau bermain.")

# Membuat Navigation Tab (Tampilan UI)
tab1, tab2, tab3 = st.tabs(["📝 Kuis & Soal", "🧩 Crossword Game", "📚 Materi Pembelajaran"])

# --- TAB 1: KUIS ---
with tab1:
    st.header("Daftar Kuis Tersedia")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Ambil data dari tabel portal_kuis
        cursor.execute("SELECT * FROM portal_kuis;")
        kuis_list = cursor.fetchall()
        conn.close()

        if kuis_list:
            for kuis in kuis_list:
                with st.expander(f"📌 {kuis['judul']}"):
                    st.write(kuis.get('deskripsi', 'Tidak ada deskripsi'))
                    if st.button("Mulai Kuis", key=f"kuis_{kuis['id']}"):
                        st.info("Fitur pengerjaan kuis siap dimainkan!")
        else:
            st.info("Belum ada kuis yang ditambahkan.")
    except Exception as e:
        st.error(f"Gagal mengambil data kuis: {e}")

# --- TAB 2: CROSSWORD GAME ---
with tab2:
    st.header("Game Teka-Teki Silang")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Ambil data dari tabel portal_crosswordgame
        cursor.execute("SELECT * FROM portal_crosswordgame;")
        games = cursor.fetchall()
        conn.close()

        if games:
            for game in games:
                st.subheader(f"🎮 {game['judul']}")
                st.button("Mainkan Game", key=f"game_{game['id']}")
        else:
            st.info("Belum ada game teka-teki silang.")
    except Exception as e:
        st.error(f"Gagal mengambil data game: {e}")

# --- TAB 3: MATERI ---
with tab3:
    st.header("Materi Pembelajaran")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Ambil data dari tabel portal_materipembelajaran
        cursor.execute("SELECT * FROM portal_materipembelajaran;")
        materi_list = cursor.fetchall()
        conn.close()

        if materi_list:
            for materi in materi_list:
                st.markdown(f"### {materi['judul']}")
                st.write(materi.get('konten', ''))
                st.divider()
        else:
            st.info("Belum ada materi pembelajaran.")
    except Exception as e:
        st.error(f"Gagal mengambil data materi: {e}")
