import os
import re
from django.db import models


import re
from django.db import models

import re
from django.db import models

class MateriPembelajaran(models.Model):
    KELAS_CHOICES = [
        ('X', 'Kelas X'),
        ('XI', 'Kelas XI'),
        ('XII', 'Kelas XII'),
    ]

    # --- TAMBAHAN PILIHAN MATA PELAJARAN ---
    MAPEL_CHOICES = [
        ('Informatika', 'Informatika'),
        ('Matematika', 'Matematika'),
        ('Fisika', 'Fisika'),
        ('Kimia', 'Kimia'),
        ('Biologi', 'Biologi'),
        ('Bahasa Indonesia', 'Bahasa Indonesia'),
        ('Bahasa Inggris', 'Bahasa Inggris'),
        ('Sejarah', 'Sejarah'),
        ('Sosiologi', 'Sosiologi'),
        ('Ekonomi', 'Ekonomi'),
        ('Geografi', 'Geografi'),
        ('PJOK', 'PJOK'),
        ('Seni Budaya', 'Seni Budaya'),
        ('PPKn', 'PPKn'),
        ('PAI', 'Pendidikan Agama Islam'),
        ('Leadership', 'Leadership'),
    ]

    judul = models.CharField(max_length=255)
    kelas = models.CharField(max_length=5, choices=KELAS_CHOICES, default='X')
    mapel = models.CharField(max_length=100, choices=MAPEL_CHOICES, default='Informatika', verbose_name="Mata Pelajaran")
    deskripsi = models.TextField(blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True, null=True)
    file_pdf = models.FileField(upload_to='modul_pdf/', blank=True, null=True)
    kkm = models.IntegerField(default=75)
    
    # Field Post-Test / ZIP Soal
    has_post_test = models.BooleanField(default=False)
    file_zip = models.FileField(upload_to='materi_zip/', blank=True, null=True)
    folder_ekstrak = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def get_embed_url(self):
        if not self.video_url:
            return ""
        
        pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        match = re.search(pattern, self.video_url)
        
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}"
        
        return self.video_url

    def __str__(self):
        return f"{self.judul} - {self.mapel} ({self.kelas})"


# Alias kompatibilitas jika views.py memanggil 'Materi'
Materi = MateriPembelajaran


class SoalPostTest(models.Model):
    materi = models.ForeignKey(MateriPembelajaran, on_delete=models.CASCADE, related_name='soal_post_test')
    pertanyaan = models.TextField()
    opsi_a = models.CharField(max_length=255)
    opsi_b = models.CharField(max_length=255)
    opsi_c = models.CharField(max_length=255)
    opsi_d = models.CharField(max_length=255)
    opsi_e = models.CharField(max_length=255)
    kunci_jawaban = models.CharField(max_length=1)  # Menyimpan pilihan jawaban seperti 'A', 'B', 'C', 'D', atau 'E'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Soal: {self.pertanyaan[:30]}..."


def path_soal_zip(instance, filename):
    return os.path.join('zip_soal', filename)


class SlideBanner(models.Model):
    judul = models.CharField(max_length=200)
    gambar = models.ImageField(upload_to='banners/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.judul


class BeritaArtikel(models.Model):
    judul = models.CharField(max_length=200)
    kategori = models.CharField(max_length=50, default='Berita')
    konten = models.TextField()
    gambar = models.ImageField(upload_to='berita/', blank=True, null=True)
    author = models.CharField(max_length=100, default='Admin')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.judul


class JadwalPelajaran(models.Model):
    kelas = models.CharField(max_length=50)
    mata_pelajaran = models.CharField(max_length=100)
    hari = models.CharField(max_length=20, default='Senin')
    jam_mulai = models.TimeField(null=True, blank=True)
    jam_selesai = models.TimeField(null=True, blank=True)
    pengajar = models.CharField(max_length=100, default='-')

    def __str__(self):
        return f"{self.kelas} - {self.mata_pelajaran}"


Jadwal = JadwalPelajaran


class Kuis(models.Model):
    nama_kuis = models.CharField(max_length=200)
    mapel = models.CharField(max_length=100, default='Umum')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_kuis


class BankSoal(models.Model):
    nama_soal = models.CharField(max_length=200)
    mapel = models.CharField(max_length=100)
    file_zip = models.FileField(upload_to=path_soal_zip, blank=True, null=True)
    folder_ekstrak = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_soal

