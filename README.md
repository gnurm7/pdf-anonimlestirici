# 📄 PDF Anonimleştirme Servisi (Flask + PyMuPDF)

Bu proje, akademik makalelerde yer alan **yazar isimleri**, **e-posta adresleri** ve **kurum bilgilerini** belirli kurallar çerçevesinde bulanıklaştırarak (redact) anonimleştiren bir Flask servisidir. Özellikle çift-kör hakemli süreçlerde kullanılmak üzere geliştirilmiştir.

##  Özellikler

- `Abstract` ve `References` bölümleri arasındaki metinler **anonimleştirme dışında tutulur**.
- Yazar adlarını büyük harf / özel karakter duyarlı şekilde bulur.
- E-posta adreslerini gizler.
- "University", "Institute", "Faculty", "Department", "Technology" gibi kurum kelimelerini bulanıklaştırır.
- PyMuPDF (`fitz`) ile PDF'e doğrudan redaction uygulanır.



## API Kullanımı
- Sunucuyu Başlat
- ``` bash
  python app.py
