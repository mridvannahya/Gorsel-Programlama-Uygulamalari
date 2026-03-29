import sys
import os
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QSlider, QSpinBox, 
                             QStackedWidget, QTableWidget, QTableWidgetItem, 
                             QRadioButton, QPushButton, QMessageBox, QDesktopWidget, QHeaderView, QFrame) 
from PyQt5.QtCore import Qt
KLASOR = os.path.dirname(os.path.abspath(__file__))
DB_YOLU = os.path.join(KLASOR, "ürünler.db")
# ==========================================
# 🎨 SİHİRLİ DOKUNUŞ: MODERN TASARIM KODLARI (QSS)
# ==========================================
MODERN_TEMA = """
/* Ana Pencere Arka Planı */
QMainWindow {
    background-color: #f4f6f9;
}

/* Genel Yazı Tipi ve Varsayılan Renk */
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #2c3e50; /* Bütün standart yazıları koyu lacivert yaptık (Görünmezlik sorunu çözüldü) */
}

/* Üst Başlık Paneli */
#BaslikPaneli {
    background-color: #2c3e50;
    border-bottom-left-radius: 15px;
    border-bottom-right-radius: 15px;
}
#BaslikYazisi {
    color: white;
    font-size: 24px;
    font-weight: bold;
}

/* Açılır Menüler ve SpinBox */
QComboBox, QSpinBox {
    background-color: white;
    border: 1px solid #ced4da;
    border-radius: 5px;
    padding: 6px;
    font-size: 14px;
    color: #495057;
}
QComboBox:hover, QSpinBox:hover {
    border: 1px solid #4CAF50;
}

/* Butonlar */
QPushButton {
    font-size: 14px;
    font-weight: bold;
    border-radius: 6px;
    padding: 10px;
    color: white; /* Tüm buton yazıları beyaz olsun */
}
#EkleButonu {
    background-color: #4CAF50;
}
#EkleButonu:hover { background-color: #45a049; }
#EkleButonu:disabled { background-color: #a5d6a7; color: #f1f1f1; }

#SiparisButonu {
    background-color: #008CBA;
}
#SiparisButonu:hover { background-color: #007bb5; }

/* Tablo Tasarımı */
QTableWidget {
    background-color: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    gridline-color: #f1f3f5;
    selection-background-color: #e3f2fd;
    selection-color: black;
}
QHeaderView::section {
    background-color: #e9ecef;
    color: #495057;
    font-weight: bold;
    font-size: 13px;
    padding: 5px;
    border: none;
    border-right: 1px solid #dee2e6;
    border-bottom: 2px solid #dee2e6;
}

/* Bölüm Çerçeveleri (Kart Görünümü) */
.QFrame {
    background-color: white;
    border-radius: 10px;
    border: 1px solid #e9ecef;
}

/* ========================================= */
/* 🛠️ YENİ EKLENEN: MESAJ KUTUSU DÜZELTMESİ  */
/* ========================================= */
QMessageBox {
    background-color: white; /* Arka planı kesin beyaz yap */
}
QMessageBox QLabel {
    color: #2c3e50; /* Yazıları kesin koyu renk yap */
    font-size: 15px;
    font-weight: 500;
}
QMessageBox QPushButton {
    background-color: #2196F3;
    color: white;
    min-width: 100px;
    border-radius: 5px;
}
QMessageBox QPushButton:hover {
    background-color: #1976D2;
}
"""
class MarketUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sanal Market Uygulaması v2.5 -")
        self.setGeometry(100, 100, 700, 800) 
        self.pencereyi_ortala()
        self.setStyleSheet(MODERN_TEMA)
        merkez_zemin = QWidget()
        self.setCentralWidget(merkez_zemin)
        self.ana_duzen = QVBoxLayout()
        self.ana_duzen.setContentsMargins(20, 0, 20, 20) 
        self.ana_duzen.setSpacing(15) 
        merkez_zemin.setLayout(self.ana_duzen)
        
        self.secili_urun_fiyati = 0 
        
        self.baslik_olustur() 
        self.arayuzu_olustur()
        self.sepet_arayuzunu_olustur() 
        self.katagorileri_yukle()
    def pencereyi_ortala(self):
        pencere_alani = self.frameGeometry()
        ekran_merkezi = QDesktopWidget().availableGeometry().center()
        pencere_alani.moveCenter(ekran_merkezi)
        self.move(pencere_alani.topLeft())
    def baslik_olustur(self):
        baslik_kutusu = QFrame()
        baslik_kutusu.setObjectName("BaslikPaneli")
        baslik_duzen = QHBoxLayout()
        baslik_yazisi = QLabel("🛒 Rıdvan Market")
        baslik_yazisi.setObjectName("BaslikYazisi")
        baslik_yazisi.setAlignment(Qt.AlignCenter)
        baslik_duzen.addWidget(baslik_yazisi)
        baslik_kutusu.setLayout(baslik_duzen)
        self.ana_duzen.addWidget(baslik_kutusu)
    def arayuzu_olustur(self):
        islem_karti = QFrame()
        islem_duzeni = QVBoxLayout()
        islem_karti.setLayout(islem_duzeni)

        duzen_yatay = QHBoxLayout()
        reyon_kutu = QVBoxLayout()
        self.katagori_etiketi = QLabel("1. Reyon:")
        self.katagori_etiketi.setStyleSheet("font-weight: bold; color: #495057;")
        self.katagori_secimi = QComboBox()

        self.katagori_secimi.currentTextChanged.connect(self.urunleri_getir)
        reyon_kutu.addWidget(self.katagori_etiketi)
        reyon_kutu.addWidget(self.katagori_secimi)
        urun_kutu = QVBoxLayout()
        self.urun_etiketi = QLabel("2. Ürün:")
        self.urun_etiketi.setStyleSheet("font-weight: bold; color: #495057;")
        self.urun_secimi = QComboBox()

        self.urun_secimi.setEnabled(False) 

        self.urun_secimi.currentTextChanged.connect(self.urun_detayini_getir)
        urun_kutu.addWidget(self.urun_etiketi)
        urun_kutu.addWidget(self.urun_secimi)

        duzen_yatay.addLayout(reyon_kutu)
        duzen_yatay.addLayout(urun_kutu)
        
        islem_duzeni.addLayout(duzen_yatay)
        self.ana_duzen.addWidget(islem_karti)
        self.islem_duzeni = islem_duzeni 

    def sepet_arayuzunu_olustur(self):
        miktar_ve_buton_duzeni = QHBoxLayout()

        self.miktar_kutusu = QStackedWidget()

        self.miktar_kutusu.addWidget(QWidget()) 

        kg_sayfasi = QWidget()
        kg_duzen = QHBoxLayout()
        kg_duzen.setContentsMargins(0,0,0,0)
        self.kg_etiket = QLabel("0.5 KG")
        self.kg_etiket.setStyleSheet("font-weight: bold; color: #d35400;")
        self.kg_slider = QSlider(Qt.Horizontal)
        self.kg_slider.setMinimum(5)   
        self.kg_slider.setMaximum(100) 
        self.kg_slider.valueChanged.connect(self.slider_hareketi)
        kg_duzen.addWidget(self.kg_slider)
        kg_duzen.addWidget(self.kg_etiket)
        kg_sayfasi.setLayout(kg_duzen)
        self.miktar_kutusu.addWidget(kg_sayfasi)
        adet_sayfasi = QWidget()
        adet_duzen = QHBoxLayout()
        adet_duzen.setContentsMargins(0,0,0,0)
        adet_etiket = QLabel("Adet:")
        adet_etiket.setStyleSheet("font-weight: bold; color: #495057;")
        self.adet_spinbox = QSpinBox()
        self.adet_spinbox.setMinimum(1)
        self.adet_spinbox.setMaximum(10)
        adet_duzen.addWidget(adet_etiket)
        adet_duzen.addWidget(self.adet_spinbox)
        adet_duzen.addStretch()
        adet_sayfasi.setLayout(adet_duzen)
        self.miktar_kutusu.addWidget(adet_sayfasi)
        self.ekle_butonu = QPushButton("🛒 SEPETE EKLE")
        self.ekle_butonu.setObjectName("EkleButonu")
        self.ekle_butonu.setEnabled(False) 
        self.ekle_butonu.clicked.connect(self.sepete_yaz)
        miktar_ve_buton_duzeni.addWidget(self.miktar_kutusu)
        miktar_ve_buton_duzeni.addWidget(self.ekle_butonu)
        self.islem_duzeni.addLayout(miktar_ve_buton_duzeni)
        self.tablo = QTableWidget(0, 4)
        self.tablo.setHorizontalHeaderLabels(["🛍️ Ürün", "⚖️ Miktar", "🏷️ Birim Fiyat", "💰 Toplam Fiyat"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        self.tablo.setAlternatingRowColors(True)
        self.ana_duzen.addWidget(self.tablo)
        alt_kutu = QFrame()
        alt_kutu.setStyleSheet("background-color: white; border-top: 3px solid #e9ecef;")
        alt_duzen = QVBoxLayout()
        odeme_etiketi = QLabel("Ödeme Yöntemi:")
        odeme_etiketi.setStyleSheet("font-weight: bold; color: #495057;")
        odeme_secenekleri = QHBoxLayout()
        self.rb_nakit = QRadioButton("💵 Kapıda Nakit")
        self.rb_kredi = QRadioButton("💳 Online Kredi Kartı")
        self.rb_kapida_kredi = QRadioButton("📦 Kapıda Kart")
        self.rb_nakit.setChecked(True) 
        odeme_secenekleri.addWidget(self.rb_nakit)
        odeme_secenekleri.addWidget(self.rb_kredi)
        odeme_secenekleri.addWidget(self.rb_kapida_kredi)
        alt_duzen.addWidget(odeme_etiketi)
        alt_duzen.addLayout(odeme_secenekleri)
        cizgi = QFrame()
        cizgi.setFrameShape(QFrame.HLine)
        cizgi.setStyleSheet("color: #dee2e6;")
        alt_duzen.addWidget(cizgi)
        final_duzeni = QHBoxLayout()
        self.genel_toplam_etiketi = QLabel("Toplam: 0.00 TL")
        self.genel_toplam_etiketi.setStyleSheet("font-weight: bold; font-size: 26px; color: #e74c3c;") 
        # --- SİPARİŞ BUTONU DÜZELTMESİ ---
        self.siparis_butonu = QPushButton("✅ SEPETİ ONAYLA")
        self.siparis_butonu.setObjectName("SiparisButonu")
        
        # Sihirli Dokunuşlar: Butonun sıkışmasını engeller ve boyutunu sabitler
        self.siparis_butonu.setMinimumWidth(200) 
        self.siparis_butonu.setMinimumHeight(45) 
        
        # Ekran görüntüsündeki gibi güzel bir yeşil tonda olması için özel CSS:
        self.siparis_butonu.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; 
                color: white; 
                font-weight: bold; 
                font-size: 15px; 
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.siparis_butonu.clicked.connect(self.siparisi_tamamla)
        final_duzeni.addWidget(self.genel_toplam_etiketi)
        final_duzeni.addStretch() 
        final_duzeni.addWidget(self.siparis_butonu)
        alt_duzen.addLayout(final_duzeni)
        alt_kutu.setLayout(alt_duzen)
        self.ana_duzen.addWidget(alt_kutu)
    def katagorileri_yukle(self):
        try:
            baglanti = sqlite3.connect(DB_YOLU)
            imlec = baglanti.cursor()
            imlec.execute("SELECT DISTINCT urunreyonu FROM Ürünler")
            katagoriler = [satir[0] for satir in imlec.fetchall()]
            self.katagori_secimi.addItem("--- Reyon Seçiniz ---")
            self.katagori_secimi.addItems(katagoriler)
            baglanti.close()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veritabanı okunamadı:\n{str(e)}")
    def urunleri_getir(self, secilen_katagori):
        if secilen_katagori == "--- Reyon Seçiniz ---" or secilen_katagori == "":
            self.urun_secimi.clear()
            self.urun_secimi.setEnabled(False)
            self.miktar_kutusu.setCurrentIndex(0)
            return
        self.urun_secimi.setEnabled(True)
        self.urun_secimi.clear()    
        self.urun_secimi.addItem("--- Ürün Seçiniz ---")
        try:
            baglanti = sqlite3.connect(DB_YOLU)
            imlec = baglanti.cursor()
            imlec.execute("SELECT urunadı FROM Ürünler WHERE urunreyonu=?", (secilen_katagori,))
            urunler = [satir[0] for satir in imlec.fetchall()]
            baglanti.close()
            self.urun_secimi.addItems(urunler)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ürünler getirilemedi:\n{str(e)}")
    def slider_hareketi(self, deger):
        kg = deger / 10.0
        self.kg_etiket.setText(f"{kg} KG")

    def urun_detayini_getir(self, secilen_urun):
        if secilen_urun == "--- Ürün Seçiniz ---" or secilen_urun == "":
            self.miktar_kutusu.setCurrentIndex(0)
            self.ekle_butonu.setEnabled(False)
            return
        try:
            baglanti = sqlite3.connect(DB_YOLU)
            imlec = baglanti.cursor()
            imlec.execute("SELECT * FROM Ürünler WHERE urunadı=?", (secilen_urun,))
            sonuc = imlec.fetchone()
            baglanti.close()
            if sonuc:
                self.secili_urun_fiyati = float(sonuc[3]) 
                tur = str(sonuc[4]).strip().upper() 

                if "KG" in tur:
                    self.miktar_kutusu.setCurrentIndex(1) 
                    self.kg_slider.setValue(5)            
                else:
                    self.miktar_kutusu.setCurrentIndex(2) 
                    self.adet_spinbox.setValue(1)        

                self.ekle_butonu.setEnabled(True) 
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ürün detayı hatası:\n{str(e)}")
    def sepete_yaz(self):
        urun = self.urun_secimi.currentText()
        fiyat = self.secili_urun_fiyati
        if self.miktar_kutusu.currentIndex() == 1:
            miktar = self.kg_slider.value() / 10.0
            tur_yazisi = f"{miktar} KG"
        else:
            miktar = self.adet_spinbox.value()
            tur_yazisi = f"{miktar} Adet"
        toplam_fiyat = miktar * fiyat
        mevcut_satir = self.tablo.rowCount()
        self.tablo.insertRow(mevcut_satir)
        hucre1 = QTableWidgetItem(urun)
        hucre2 = QTableWidgetItem(tur_yazisi)
        hucre2.setTextAlignment(Qt.AlignCenter)
        hucre3 = QTableWidgetItem(f"{fiyat} TL")
        hucre3.setTextAlignment(Qt.AlignCenter)
        hucre4 = QTableWidgetItem(f"{toplam_fiyat:.2f} TL")
        hucre4.setTextAlignment(Qt.AlignCenter)
        self.tablo.setItem(mevcut_satir, 0, hucre1)
        self.tablo.setItem(mevcut_satir, 1, hucre2)
        self.tablo.setItem(mevcut_satir, 2, hucre3)
        self.tablo.setItem(mevcut_satir, 3, hucre4)
        self.genel_toplami_hesapla()
    def genel_toplami_hesapla(self):
        toplam = 0.0
        for satir in range(self.tablo.rowCount()):
            fiyat_metni = self.tablo.item(satir, 3).text() 
            fiyat_sayisi = float(fiyat_metni.replace(" TL", "")) 
            toplam += fiyat_sayisi
        self.genel_toplam_etiketi.setText(f"Toplam: {toplam:.2f} TL")
    def siparisi_tamamla(self):
        if self.tablo.rowCount() == 0:
            QMessageBox.warning(self, "Uyarı", "Sepetiniz şu an boş! Lütfen önce ürün ekleyin.")
            return
        if self.rb_nakit.isChecked(): odeme_tipi = "Kapıda Nakit"
        elif self.rb_kredi.isChecked(): odeme_tipi = "Kredi Kartı (Online)"
        else: odeme_tipi = "Kapıda Kredi Kartı"
        tutar = self.genel_toplam_etiketi.text()
        QMessageBox.information(self, "🧾 Fatura Onayı", 
                                f"🎉 Siparişiniz Başarıyla Alındı!\n\n"
                                f"Ödeme Türü: {odeme_tipi}\n"
                                f"Ödenecek Tutar: {tutar}\n\n"
                                f"Bizi tercih ettiğiniz için teşekkür ederiz."
                                f"\n\nNot: Siparişiniz en kısa sürede hazırlanıp gönderilecektir.")
        self.tablo.setRowCount(0)
        self.genel_toplami_hesapla()
        self.katagori_secimi.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = MarketUygulamasi()
    pencere.show()
    sys.exit(app.exec_())