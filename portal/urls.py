from django.urls import path
from . import views

urlpatterns = [
    # --- AUTHENTICATION ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- FRONTEND (SISWA / UMUM) ---
    path('', views.home_view, name='frontend_home'), 
    path('home/', views.home_view, name='home'),
    
    # Detail Berita (Disediakan dua nama agar cocok dengan semua template)
    path('berita/<int:id>/', views.detail_berita_view, name='frontend_detail_berita'),
    path('berita/detail/<int:id>/', views.detail_berita_view, name='detail_berita'),
    
    # Buka Soal & Materi
    path('soal/buka/<int:soal_id>/', views.buka_soal_view, name='buka_soal'),
    path('soal/buka-frontend/<int:soal_id>/', views.buka_soal_view, name='frontend_buka_soal'),
    path('materi/buka-soal/<int:materi_id>/', views.buka_soal_materi_view, name='buka_soal_materi'),

    # --- BACKEND (ADMIN / DASHBOARD) ---
    path('dashboard/', views.dashboard_view, name='backend_dashboard'),
    path('banner/', views.banner_view, name='backend_banner'),
    path('banner/hapus/<int:banner_id>/', views.hapus_banner_view, name='hapus_banner'),
    path('jadwal/', views.jadwal_view, name='backend_jadwal'),
    path('bank-soal/', views.bank_soal_view, name='backend_bank_soal'),
    path('bank-soal/hapus/<int:soal_id>/', views.hapus_soal_view, name='backend_hapus_soal'),

    # --- MANAJEMEN MATERI ---
    path('materi/', views.materi_view, name='materi_list'),
    path('materi/hapus/<int:id>/', views.hapus_materi, name='hapus_materi'),
    path('materi/upload-post-test/', views.upload_post_test_soal, name='upload_post_test'),
  

]
