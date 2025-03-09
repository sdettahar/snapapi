# TODO
1.  Better documentation
2.  Replace dependency starlette.responses di SNAPResponse
3.  Make default `@app.exception_handler` di `class SNAP-API` [lihat](https://github.com/sdettahar/snapapi/blob/02d7df907b69504c679d5dbc1ec49f17e699d4fa/snapapi/applications.py#L103)
4.  Replace `aiocache` dengan subclass yang lebih simple, agar tidak terlalu banyak dependency [lihat](https://github.com/sdettahar/snapapi/blob/02d7df907b69504c679d5dbc1ec49f17e699d4fa/snapapi/cache.py#L110)
5.  Add Model lain untuk Virtual Account
6.  Pakai `ProcessPoolExecutor` buat `class SNAPCrypto` karena CPU-bond? Overkill?