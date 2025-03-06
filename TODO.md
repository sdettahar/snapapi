# TODO
1.  Replace dependency starlette.responses di SNAPResponse
2.  Make default `@app.exception_handler` di `class SNAP-API` [lihat](https://github.com/sdettahar/snapapi/blob/02d7df907b69504c679d5dbc1ec49f17e699d4fa/snapapi/applications.py#L103)
3.  Replace `aiocache` dengan subclass yang lebih simple, agar tidak terlalu banyak dependency [lihat](https://github.com/sdettahar/snapapi/blob/02d7df907b69504c679d5dbc1ec49f17e699d4fa/snapapi/cache.py#L110)
4.  Add Model lain untuk Virtual Account
5.  Fitur Logger untuk menyimpan JSON Request dan Response beserta dengan Exception error + traceback (jika HTTP Status Code >= 500) ke Backend, agar compliance dengan SNAP
6.  Pakai `ProcessPoolExecutor` buat `class SNAPCrypto` karena CPU-bond? Overkill?