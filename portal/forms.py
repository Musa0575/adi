from django import forms
from .models import Materi

class MateriForm(forms.ModelForm):
    # Field tambahan untuk upload file soal (bukan bagian langsung dari model Materi)
    file_soal_excel = forms.FileField(
        required=False,
        label="Upload Soal Post-Test (Excel / CSV)",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx, .xls, .csv'
        })
    )

    class Meta:
        model = Materi
        fields = ['judul', 'kelas', 'deskripsi', 'video_url', 'file_pdf']
        widgets = {
            'judul': forms.TextInput(attrs={'class': 'form-control'}),
            'kelas': forms.TextInput(attrs={'class': 'form-control'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'file_pdf': forms.FileInput(attrs={'class': 'form-control'}),
        }
