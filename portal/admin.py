from django.contrib import admin
from .models import (
    BeritaArtikel,
    SlideBanner,
    Kuis,
    JadwalPelajaran
)

# Register model ke Halaman Admin Django
@admin.register(BeritaArtikel)
class BeritaArtikelAdmin(admin.ModelAdmin):
    list_display = ('judul', 'kategori', 'author', 'created_at')
    search_fields = ('judul', 'konten')
    list_filter = ('kategori', 'created_at')

@admin.register(JadwalPelajaran)
class JadwalPelajaranAdmin(admin.ModelAdmin):
    list_display = ('kelas', 'mata_pelajaran', 'hari', 'jam_mulai', 'jam_selesai', 'pengajar')
    search_fields = ('kelas', 'mata_pelajaran', 'pengajar')
    list_filter = ('hari', 'kelas')

@admin.register(SlideBanner)
class SlideBannerAdmin(admin.ModelAdmin):
    list_display = ('judul', 'is_active')

@admin.register(Kuis)
class KuisAdmin(admin.ModelAdmin):
    list_display = ('nama_kuis',)
