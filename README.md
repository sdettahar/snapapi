# SNAP-API
Framework/tookit berbasis pydantic dan FastAPI untuk implementasi SNAP (Standar Nasional Open API Pembayaran) Indonesia


## Transaksi
Virtual Account:
1.  Inquiry, Service Code '24'
2.  Payment, Service Code '25'

Iya, masih banyak Transaksi yang harus dibuat Modelnya :)


## Python
`snapapi` dibuat dengan menggunakan Python versi 3.8.20, semoga bisa digunakan dibanyak OS yang mungkin masih belum support python terbaru.

`snapapi` menggunakan type hints yang diverifikasi dengan `mypy`.


### Dependency
SNAP-API membutuhkan module sbb:
1.  `pydantic` https://pydantic.dev  
    Dasar dari validasi model agar sesuai dengan spesifikasi yang telah ditetapkan oleh Bank Indonesia dan ASPI (Asosiasi Sistem Pembayaran Indonesia)

2.  `pycryptodome` https://www.pycryptodome.org  
    Digunakan untuk membuat dan meverifikasi Asymmetric Signature dengan algorithma SHA256withRSA

3.  `PyJWT` https://pyjwt.readthedocs.io/en/latest  
    Dibutuhkan untuk membuat dan meverifikasi Access Token berbasis JWT

4.  `fastapi` https://fastapi.tiangolo.com  
    Lighweight and fast framework API berdasarkan OpenAPI

5.  `asyncer` https://asyncer.tiangolo.com  
    Thin layer module di atas `anyio` agar membuat sync method (spt `class Crypto`) menjadi async


### Optional
1.  `uvicorn` https://www.uvicorn.org  
    ASGI web server

2.  `aiocache` https://aiocache.aio-libs.org/en/latest  
    Digunakan untuk cache key X-External-Id pada API Transaksi. Backend untuk store keys bisa dipilih antara `memcached`, `redis` atau `memory`

3.  `orjson` https://github.com/ijl/orjson  
    Pengganti yang lebih baik daripada standar `json`


## Cara Pakai
Install package dengan pip.

```shell

$ pip install snapapi

```

Import `class SNAP-API` kemudian instantiate sama seperti `class FastAPI`, karena `class IDSAP` merupakan subclass dari `class FastAPI`.

```python

app = SNAP-API(
        title='SNAP-API Demo',
        version="0.1.1",
        description="""
### Standar Nasional Open API Pembayaran Versi 1.0.2
> Flow Inbound (Direct): Bank -> API
""")

```

Silakan lihat direktori `app/demo` untuk contoh implementasi. 
Untuk menjalankan aplikasi Demo, silakan baca `app/README.md` dan ikuti petunjuknya.


## Future Development
Module SNAP-API dibuat berdasarkan kebutuhan project profesional developer untuk implementasi SNAP dengan flow Inbound atau Direct; Bank -> API

> Bank yang melakukan initiate query (`inquiry` dan `payment`) untuk Virtual Account
> dimana Bill, Virtual Account dan Customer management dilakukan oleh Backend terlepas dari API ini.

Jadi module ini cukup jika digunakan untuk skenario di atas. Agar compliance dengan SNAP, masih banyak skenario yang harus diimplementasi.

Fokus pengembangan module ini adalah:
1.  Mengikuti perkembangan SNAP supaya compliance setiap kali ada versi terbaru.
2.  Implementasi Model lain agar sesuai dengan dokumentasi SNAP, terutama melengkapi fitur Virtual Account.
3.  Refactoring fitur yang sudah ada supaya lebih ringan, tidak terlalu banyak dependency, dan mudah digunakan.
4.  Tambah fitur seperti Logger (agar compliance dengan SNAP), API untuk Backend, dll.