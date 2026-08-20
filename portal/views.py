import os
import zipfile
import shutil
import csv
import io
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Import seluruh model
from .models import (
    MateriPembelajaran,
    SoalPostTest,
    SlideBanner,
    BeritaArtikel,
    JadwalPelajaran,
    BankSoal,
    
    
)


# ==========================================
# 1. AUTHENTICATION VIEWS
# ==========================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('backend_dashboard')

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f'Selamat datang kembali, {user.username}!')
            return redirect('backend_dashboard')
        else:
            messages.error(request, 'User ID atau Password salah!')

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Anda telah berhasil logout.')
    return redirect('login')


# ==========================================
# 2. FRONTEND VIEWS (SISWA / UMUM)
# ==========================================

def home_view(request):
    selected_mapel = request.GET.get('mapel', 'semua')

    # Filter materi berdasarkan dropdown mapel jika ada
    if selected_mapel and selected_mapel != 'semua':
        materi_list = MateriPembelajaran.objects.filter(mapel=selected_mapel).order_by('-id')
    else:
        materi_list = MateriPembelajaran.objects.all().order_by('-id')

    # Ambil daftar pilihan mapel unik dari model untuk dropdown
    daftar_mapel = [choice[0] for choice in getattr(MateriPembelajaran, 'MAPEL_CHOICES', [])]

    berita_list = BeritaArtikel.objects.all().order_by('-created_at')[:6]
    jadwal_list = JadwalPelajaran.objects.all()
    banner_list = SlideBanner.objects.filter(is_active=True).order_by('-id')
    bank_soal_list = BankSoal.objects.all().order_by('-id')
    
    context = {
        'berita_list': berita_list,
        'jadwal_list': jadwal_list,
        'banner_list': banner_list,
        'bank_soal_list': bank_soal_list,
        'materi_list': materi_list,
        'daftar_mapel': daftar_mapel,
        'selected_mapel': selected_mapel,
    }
    return render(request, 'frontend/index.html', context)


def detail_berita_view(request, id):
    berita = get_object_or_404(BeritaArtikel, id=id)
    berita_lainnya = BeritaArtikel.objects.exclude(id=id).order_by('-created_at')[:5]
    
    context = {
        'berita': berita,
        'berita_lainnya': berita_lainnya,
    }
    return render(request, 'frontend/detail_berita.html', context)


def buka_soal_view(request, soal_id):
    soal = get_object_or_404(BankSoal, id=soal_id)
    base_extract_path = os.path.join(settings.MEDIA_ROOT, 'bank_soal_html', f"soal_{soal.id}")

    relative_index_path = None
    if os.path.exists(base_extract_path):
        for root, dirs, files in os.walk(base_extract_path):
            if 'index.html' in files:
                rel_dir = os.path.relpath(root, base_extract_path)
                if rel_dir == '.':
                    relative_index_path = 'index.html'
                else:
                    relative_index_path = os.path.join(rel_dir, 'index.html').replace('\\', '/')
                break

    if relative_index_path:
        target_url = f"{settings.MEDIA_URL}bank_soal_html/soal_{soal.id}/{relative_index_path}"
        return redirect(target_url)
    else:
        raise Http404("File index.html tidak ditemukan dalam paket ZIP ini.")


def buka_soal_materi_view(request, materi_id):
    materi = get_object_or_404(MateriPembelajaran, id=materi_id)
    base_extract_path = os.path.join(settings.MEDIA_ROOT, 'materi_html', f"materi_{materi.id}")

    relative_index_path = None
    if os.path.exists(base_extract_path):
        for root, dirs, files in os.walk(base_extract_path):
            if 'index.html' in files:
                rel_dir = os.path.relpath(root, base_extract_path)
                if rel_dir == '.':
                    relative_index_path = 'index.html'
                else:
                    relative_index_path = os.path.join(rel_dir, 'index.html').replace('\\', '/')
                break

    if relative_index_path:
        target_url = f"{settings.MEDIA_URL}materi_html/materi_{materi.id}/{relative_index_path}"
        return redirect(target_url)
    else:
        raise Http404("File index.html tidak ditemukan dalam paket ZIP materi ini.")


# ==========================================
# 3. MANAJEMEN MATERI & POST TEST
# ==========================================

@login_required(login_url='login')
def materi_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        materi_id = request.POST.get('materi_id')

        # --- A. TAMBAH MATERI BARU ---
        if action == 'create' or 'submit_tambah_materi' in request.POST:
            try:
                judul = request.POST.get('nama') or request.POST.get('judul')
                kelas = request.POST.get('kelas', 'X')
                mapel = request.POST.get('mapel', 'Informatika')
                deskripsi = request.POST.get('deskripsi', '')
                video_url = request.POST.get('video_url', '')
                kkm_raw = request.POST.get('kkm')
                file_pdf = request.FILES.get('file_pdf')
                file_zip = request.FILES.get('file_zip')

                if not judul:
                    messages.error(request, "Judul/Nama Materi wajib diisi!")
                    return redirect('materi_list')

                try:
                    kkm_val = int(kkm_raw) if kkm_raw else 75
                except (ValueError, TypeError):
                    kkm_val = 75

                materi = MateriPembelajaran.objects.create(
                    judul=judul,
                    kelas=kelas,
                    mapel=mapel,
                    deskripsi=deskripsi,
                    video_url=video_url,
                    kkm=kkm_val,
                    file_pdf=file_pdf,
                    file_zip=file_zip
                )
                
                # Ekstrak ZIP jika ada
                if file_zip and file_zip.name.endswith('.zip'):
                    folder_name = f"materi_{materi.id}"
                    extract_path = os.path.join(settings.MEDIA_ROOT, 'materi_html', folder_name)
                    
                    with zipfile.ZipFile(materi.file_zip.path, 'r') as zip_ref:
                        zip_ref.extractall(extract_path)

                    materi.folder_ekstrak = f"materi_html/{folder_name}"
                    materi.has_post_test = True
                    materi.save()

                messages.success(request, f"Materi '{judul}' berhasil ditambahkan!")
                return redirect('materi_list')

            except Exception as e:
                messages.error(request, f"Gagal menambahkan materi: {e}")
                return redirect('materi_list')

        # --- B. UPDATE / EDIT MATERI ---
        elif action == 'update' or 'update_materi' in request.POST:
            try:
                materi = get_object_or_404(MateriPembelajaran, id=materi_id)

                nama_baru = request.POST.get('nama') or request.POST.get('judul')
                if nama_baru:
                    materi.judul = nama_baru

                if 'kelas' in request.POST:
                    materi.kelas = request.POST.get('kelas')
                if 'mapel' in request.POST:
                    materi.mapel = request.POST.get('mapel')
                if 'deskripsi' in request.POST:
                    materi.deskripsi = request.POST.get('deskripsi', '')
                if 'video_url' in request.POST:
                    materi.video_url = request.POST.get('video_url', '')

                kkm_raw = request.POST.get('kkm')
                if kkm_raw:
                    try:
                        materi.kkm = int(kkm_raw)
                    except (ValueError, TypeError):
                        pass

                if 'file_pdf' in request.FILES:
                    materi.file_pdf = request.FILES['file_pdf']

                if 'file_zip' in request.FILES:
                    file_zip = request.FILES['file_zip']
                    if file_zip.name.endswith('.zip'):
                        materi.file_zip = file_zip
                        materi.save()

                        folder_name = f"materi_{materi.id}"
                        extract_path = os.path.join(settings.MEDIA_ROOT, 'materi_html', folder_name)
                        
                        if os.path.exists(extract_path):
                            shutil.rmtree(extract_path)

                        with zipfile.ZipFile(materi.file_zip.path, 'r') as zip_ref:
                            zip_ref.extractall(extract_path)

                        materi.folder_ekstrak = f"materi_html/{folder_name}"
                        materi.has_post_test = True

                materi.save()
                messages.success(request, f"Materi '{materi.judul}' berhasil diperbarui!")

            except Exception as e:
                messages.error(request, f"Gagal mengedit materi: {e}")

            return redirect('materi_list')

        # --- C. HAPUS MATERI ---
        elif action == 'delete' or 'delete_materi' in request.POST:
            try:
                materi = get_object_or_404(MateriPembelajaran, id=materi_id)
                extract_path = os.path.join(settings.MEDIA_ROOT, 'materi_html', f"materi_{materi.id}")
                if os.path.exists(extract_path):
                    shutil.rmtree(extract_path)

                judul_materi = materi.judul
                materi.delete()
                messages.success(request, f"Materi '{judul_materi}' berhasil dihapus!")
            except Exception as e:
                messages.error(request, f"Gagal menghapus materi: {e}")

            return redirect('materi_list')

    # --- GET REQUEST (TAMPILAN ADMIN MATERI) ---
    selected_mapel = request.GET.get('mapel', 'semua')
    
    if selected_mapel and selected_mapel != 'semua':
        materi_list = MateriPembelajaran.objects.filter(mapel=selected_mapel).order_by('-id')
    else:
        materi_list = MateriPembelajaran.objects.all().order_by('-id')

    daftar_mapel = [choice[0] for choice in getattr(MateriPembelajaran, 'MAPEL_CHOICES', [])]

    context = {
        'materi_list': materi_list,
        'daftar_mapel': daftar_mapel,
        'selected_mapel': selected_mapel,
        'total_jadwal': JadwalPelajaran.objects.count(),
        'total_berita': BeritaArtikel.objects.count(),
        'total_banner': SlideBanner.objects.count(),
        'total_kuis': BankSoal.objects.count(),
        'total_materi': materi_list.count(),
        'active_tab': 'materi'
    }
    return render(request, 'portal/materi.html', context)


@login_required(login_url='login')
def hapus_materi(request, id):
    materi = get_object_or_404(MateriPembelajaran, id=id)
    judul = materi.judul
    extract_path = os.path.join(settings.MEDIA_ROOT, 'materi_html', f"materi_{materi.id}")
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)
    
    materi.delete()
    messages.success(request, f"Materi '{judul}' berhasil dihapus.")
    return redirect('materi_list')


@login_required(login_url='login')
def upload_post_test_soal(request):
    if request.method == 'POST':
        materi_id = request.POST.get('materi_id')
        metode = request.POST.get('metode_upload')
        
        if not materi_id:
            messages.error(request, 'ID Materi tidak ditemukan!')
            return redirect('materi_list')
        
        materi = get_object_or_404(MateriPembelajaran, id=materi_id)
        
        if (metode == 'file' or metode == 'excel') and 'file_soal' in request.FILES:
            csv_file = request.FILES['file_soal']
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'File harus berformat CSV!')
                return redirect('materi_list')
                
            try:
                data_set = csv_file.read().decode('UTF-8')
                io_string = io.StringIO(data_set)
                next(io_string, None)
                
                for row in csv.reader(io_string, delimiter=','):
                    if len(row) >= 7:
                        SoalPostTest.objects.create(
                            materi=materi,
                            pertanyaan=row[0].strip(),
                            opsi_a=row[1].strip(), 
                            opsi_b=row[2].strip(), 
                            opsi_c=row[3].strip(), 
                            opsi_d=row[4].strip(), 
                            opsi_e=row[5].strip(),
                            kunci_jawaban=row[6].strip()
                        )
                
                materi.has_post_test = True  
                materi.save()
                messages.success(request, 'Soal Post-Test berhasil diunggah!')
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan membaca file CSV: {e}')
        
        elif metode == 'manual':
            materi.has_post_test = True
            materi.save()
            messages.success(request, 'Soal Post-Test manual berhasil ditambahkan!')
            
    return redirect('materi_list')


# ==========================================
# 4. BACKEND ADMIN DASHBOARD
# ==========================================

@login_required(login_url='login')
def dashboard_view(request):
    if request.method == 'POST' and 'submit_berita' in request.POST:
        judul = request.POST.get('judul')
        kategori = request.POST.get('kategori')
        konten = request.POST.get('konten')
        gambar = request.FILES.get('gambar')
        
        if judul and konten:
            BeritaArtikel.objects.create(
                judul=judul,
                kategori=kategori,
                konten=konten,
                gambar=gambar
            )
            messages.success(request, 'Berita / Artikel berhasil diterbitkan!')
            return redirect('backend_dashboard')
        else:
            messages.error(request, 'Judul dan Konten Berita wajib diisi!')

    berita_list = BeritaArtikel.objects.all().order_by('-created_at')
    
    context = {
        'total_jadwal': JadwalPelajaran.objects.count(),
        'total_berita': berita_list.count(),
        'total_banner': SlideBanner.objects.count(),
        'total_kuis': BankSoal.objects.count(),
        'total_materi': MateriPembelajaran.objects.count(),
        'berita_list': berita_list,
        'server_status': 'Server Normal - System Online',
        'server_id': 'SRV-LKL-01'
    }
    return render(request, 'backend/dashboard.html', context)


@login_required(login_url='login')
def banner_view(request):
    if request.method == 'POST' and 'submit_banner' in request.POST:
        judul = request.POST.get('judul')
        gambar = request.FILES.get('gambar')

        if judul and gambar:
            SlideBanner.objects.create(
                judul=judul,
                gambar=gambar,
                is_active=True
            )
            messages.success(request, f'Slide Banner "{judul}" berhasil ditambahkan!')
            return redirect('backend_banner')
        else:
            messages.error(request, 'Judul dan Gambar banner wajib diisi!')

    banner_list = SlideBanner.objects.all().order_by('-id')
    context = {
        'banner_list': banner_list,
        'total_jadwal': JadwalPelajaran.objects.count(),
        'total_berita': BeritaArtikel.objects.count(),
        'total_banner': banner_list.count(),
        'total_kuis': BankSoal.objects.count(),
    }
    return render(request, 'backend/banner.html', context)


@login_required(login_url='login')
def hapus_banner_view(request, banner_id):
    banner = get_object_or_404(SlideBanner, id=banner_id)
    if banner.gambar and os.path.exists(banner.gambar.path):
        os.remove(banner.gambar.path)
        
    nama = banner.judul
    banner.delete()
    messages.success(request, f'Banner "{nama}" berhasil dihapus!')
    return redirect('backend_banner')


@login_required(login_url='login')
def jadwal_view(request):
    if request.method == 'POST':
        kode_mapel = request.POST.get('kelas')
        nama_mapel = request.POST.get('mata_pelajaran')
        
        if kode_mapel and nama_mapel:
            JadwalPelajaran.objects.create(
                kelas=kode_mapel,
                mata_pelajaran=nama_mapel,
                hari='Senin',
                jam_mulai='07:00',
                jam_selesai='08:00',
                pengajar='-'
            )
            messages.success(request, 'Mata Pelajaran berhasil disimpan!')
            return redirect('backend_jadwal')
        else:
            messages.error(request, 'Kode/Kelas dan Nama Mata Pelajaran wajib diisi!')

    jadwal_list = JadwalPelajaran.objects.all().order_by('-id')
    context = {
        'jadwal_list': jadwal_list,
        'total_jadwal': jadwal_list.count(),
        'total_berita': BeritaArtikel.objects.count(),
        'total_banner': SlideBanner.objects.count(),
        'total_kuis': BankSoal.objects.count(),
    }
    return render(request, 'backend/jadwal.html', context)


@login_required(login_url='login')
def bank_soal_view(request):
    if request.method == 'POST' and 'submit_soal' in request.POST:
        nama_soal = request.POST.get('nama_soal')
        mapel = request.POST.get('mapel')
        file_zip = request.FILES.get('file_zip')

        if nama_soal and mapel and file_zip:
            if not file_zip.name.endswith('.zip'):
                messages.error(request, 'File yang diunggah harus berformat .ZIP!')
                return redirect('backend_bank_soal')

            soal_obj = BankSoal.objects.create(
                nama_soal=nama_soal,
                mapel=mapel,
                file_zip=file_zip
            )

            folder_name = f"soal_{soal_obj.id}"
            extract_path = os.path.join(settings.MEDIA_ROOT, 'bank_soal_html', folder_name)

            try:
                zip_file_path = soal_obj.file_zip.path
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)

                soal_obj.folder_ekstrak = f"bank_soal_html/{folder_name}"
                soal_obj.save()

                messages.success(request, f'Paket soal "{nama_soal}" berhasil diunggah & diekstrak!')
            except Exception as e:
                messages.error(request, f'Gagal mengekstrak file ZIP: {str(e)}')

            return redirect('backend_bank_soal')
        else:
            messages.error(request, 'Semua kolom form paket soal wajib diisi!')

    soal_list = BankSoal.objects.all().order_by('-id')
    context = {
        'soal_list': soal_list,
        'total_jadwal': JadwalPelajaran.objects.count(),
        'total_berita': BeritaArtikel.objects.count(),
        'total_banner': SlideBanner.objects.count(),
        'total_kuis': soal_list.count(),
    }
    return render(request, 'backend/bank_soal.html', context)


@login_required(login_url='login')
def hapus_soal_view(request, soal_id):
    soal = get_object_or_404(BankSoal, id=soal_id)
    
    if soal.file_zip and os.path.exists(soal.file_zip.path):
        os.remove(soal.file_zip.path)
        
    extract_path = os.path.join(settings.MEDIA_ROOT, 'bank_soal_html', f"soal_{soal.id}")
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)
        
    nama = soal.nama_soal
    soal.delete()
    
    messages.success(request, f'Paket soal "{nama}" berhasil dihapus!')
    return redirect('backend_bank_soal')


# ==========================================
# MANAJEMEN PERMAINAN CROSSWORD (BACKEND)
# ==========================================

@login_required(login_url='login')
def permainan_crossword_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        # --- A. BUAT GAME CROSSWORD BARU ---
        if action == 'create_game':
            judul = request.POST.get('judul')
            kategori = request.POST.get('kategori', 'Informatika')
            deskripsi = request.POST.get('deskripsi', '')
            pin_input = request.POST.get('pin', '').strip()

            if judul:
                game = CrosswordGame(
                    judul=judul,
                    kategori=kategori,
                    deskripsi=deskripsi,
                    pin=pin_input if pin_input else None  # jika kosong akan auto-generate di model
                )
                game.save()
                messages.success(request, f'Game "{judul}" berhasil dibuat! PIN Akses: {game.pin}')
            else:
                messages.error(request, 'Judul permainan wajib diisi!')

            return redirect('backend_permainan')

        # --- B. TAMBAH SOAL/KATA CROSSWORD ---
        elif action == 'add_item':
            game_id = request.POST.get('game_id')
            game = get_object_or_404(CrosswordGame, id=game_id)

            nomor = request.POST.get('nomor')
            orientasi = request.POST.get('orientasi')
            pertanyaan = request.POST.get('pertanyaan')
            jawaban = request.POST.get('jawaban')
            pos_row = request.POST.get('posisi_row', 0)
            pos_col = request.POST.get('posisi_col', 0)

            if nomor and pertanyaan and jawaban:
                CrosswordItem.objects.create(
                    game=game,
                    nomor=int(nomor),
                    orientasi=orientasi,
                    pertanyaan=pertanyaan,
                    jawaban=jawaban,
                    posisi_row=int(pos_row),
                    posisi_col=int(pos_col)
                )
                messages.success(request, f'Soal No.{nomor} berhasil ditambahkan!')
            else:
                messages.error(request, 'Semua field soal wajib diisi!')

            return redirect('backend_permainan')

    crossword_list = CrosswordGame.objects.all().prefetch_related('items').order_by('-id')

    context = {
        'crossword_list': crossword_list,
        'total_crossword': crossword_list.count(),
        'total_game': Game.objects.count(),
        'total_jadwal': JadwalPelajaran.objects.count(),
        'total_berita': BeritaArtikel.objects.count(),
        'total_banner': SlideBanner.objects.count(),
        'total_kuis': BankSoal.objects.count(),
        'total_materi': MateriPembelajaran.objects.count(),
        'active_tab': 'permainan'
    }
    return render(request, 'portal/materi.html', context)


# --- C. FUNGSI MAINKAN GAME DENGAN FORM PIN ---
def mainkan_crossword_view(request, game_id):
    game = get_object_or_404(CrosswordGame, id=game_id)
    error_msg = None
    pin_verified = False

    # Jika Admin yang sedang login, langsung izinkan tanpa masukan PIN
    if request.user.is_authenticated and request.user.is_staff:
        pin_verified = True

    # Jika disubmit via Form PIN oleh Siswa
    if request.method == 'POST':
        pin_entered = request.POST.get('pin_game', '').strip()
        if pin_entered == game.pin:
            pin_verified = True
            request.session[f'game_access_{game.id}'] = True  # Simpan status di session
        else:
            error_msg = "PIN Game Salah! Silakan tanyakan PIN kepada Guru/Admin."

    # Cek apakah sebelumnya sudah pernah verifikasi PIN via Session
    if request.session.get(f'game_access_{game.id}'):
        pin_verified = True

    context = {
        'game': game,
        'items': game.items.all().order_by('nomor'),
        'pin_verified': pin_verified,
        'error_msg': error_msg
    }
    return render(request, 'frontend/play_crossword.html', context)


