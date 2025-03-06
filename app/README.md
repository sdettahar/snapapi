# Contoh Implementas API SNAP dengan `snapapi`

### Tes Demo App
Langkah sebelum mencoba:
1.  Buat folder `~/.snapapi`
2.  Buat file konfigurasi `~/.snapapi/snapapi.conf`, dengan spt pada contoh pada `snapapi.conf.sample`
3.  Set permission file tsb ke 600

```shell    

$ chmod 600 ~/.snapapi/snapapi.conf

```

4.  Buat python `env` dan aktifkan, kemudian install module2 yang dibutuhkan
5.  Masuk ke dalam folder `{snapapi}/tests`
6.  Jalankan `certificate.py` untuk membuat Private Key dan Public Certificate

```shell

{snapapi}/tests$ python certificate.py

```

7.  Di dalam parent folder, jalankan:

```shell
    
{snapapi}$ uvicorn app:demo --reload

```

8.  Buka browser dan akses Redoc di `http://localhost:8000/redoc` (http://localhost:8000/redoc)
7.  Tes dengan contoh script pada folder `tests`, dengan Postman, atau python console