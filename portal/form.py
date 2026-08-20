from django import forms

class UploadSoalForm(forms.Form):
    nama_post_test = forms.CharField(
        max_length=200, 
        label="Nama Post-Test / Kuis",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Post-Test Bab 1'})
    )
    mapel = forms.CharField(
        max_length=100, 
        label="Mata Pelajaran",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Informatika'})
    )
    file_excel = forms.FileField(
        label="Upload File Excel / CSV",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls, .csv'})
    )
