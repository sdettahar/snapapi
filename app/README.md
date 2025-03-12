# Contoh Implementas API SNAP dengan `snapapi`

### Tes Demo App
Langkah sebelum mencoba:
1.  Buat folder `~/.snapapi`
2.  Buat file konfigurasi `~/.snapapi/snapapi.conf`, dengan spt pada contoh pada `deployment/snapapi.conf.sample`
3.  Set permission file tsb ke 600

```shell    

$ mkdir ~/.snapapi
$ vim ~/.snapapi/snapapi.conf
$ chmod 600 ~/.snapapi/snapapi.conf

```

4.  Buat python `env` dan aktifkan, kemudian install module2 yang dibutuhkan
5.  Masuk ke dalam folder `{snapapi}/tests`
6.  Buat Private Key dan Public Certificate

```shell

snapapi/tests$ python test_demo.py certificate

```

7.  Di dalam parent folder `snapapi`, jalankan:

```shell
    
snapapi$ uvicorn app:demo --reload

```

8.  Buka browser dan akses Redoc di `http://localhost:8000/redoc` (http://localhost:8000/redoc)
9.  Tes dengan contoh script pada folder `tests`