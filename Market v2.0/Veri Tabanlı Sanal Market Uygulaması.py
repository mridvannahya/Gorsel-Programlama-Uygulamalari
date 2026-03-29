import sys
import os
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QSlider, QSpinBox, 
                             QStackedWidget, QTableWidget, QTableWidgetItem, 
                             QRadioButton, QPushButton, QMessageBox, QDesktopWidget, QHeaderView) 
from PyQt5.QtCore import Qt
KLASOR = os.path.dirname(os.path.abspath(__file__))
DB_YOLU = os.path.join(KLASOR, "ürünler.db")
class MarketUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sanal Market Uygulaması v2.0 -")
        self.setGeometry(100, 100, 650, 750) 
        self.pencereyi_ortala()
        merkez_zemin = QWidget()
        self.setCentralWidget(merkez_zemin)
        self.ana_duzen = QVBoxLayout()
        merkez_zemin.setLayout(self.ana_duzen)
        self.secili_urun_fiyati = 0 
        self.arayuzu_olustur()
        self.sepet_arayuzunu_olustur() 
        self.katagorileri_yukle()
    def pencereyi_ortala(self):
        pencere_alani = self.frameGeometry()
        ekran_merkezi = QDesktopWidget().availableGeometry().center()
        pencere_alani.moveCenter(ekran_merkezi)
        self.move(pencere_alani.topLeft())
    def arayuzu_olustur(self):
        self.katagori_etiketi = QLabel("1. Reyon Seçiniz:")
        self.katagori_etiketi.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 5px;")
        self.ana_duzen.addWidget(self.katagori_etiketi)
        self.katagori_secimi = QComboBox()
        self.katagori_secimi.setStyleSheet("font-size: 14px; padding: 5px;")
        self.ana_duzen.addWidget(self.katagori_secimi)
        self.katagori_secimi.currentTextChanged.connect(self.urunleri_getir)
        self.urun_etiketi = QLabel("2. Ürün Seçiniz:")
        self.urun_etiketi.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        self.ana_duzen.addWidget(self.urun_etiketi)     
        self.urun_secimi = QComboBox()
        self.urun_secimi.setStyleSheet("font-size: 14px; padding: 5px;")
        self.urun_secimi.setEnabled(False) 
        self.ana_duzen.addWidget(self.urun_secimi)
        self.urun_secimi.currentTextChanged.connect(self.urun_detayini_getir)
    def sepet_arayuzunu_olustur(self):
        self.miktar_kutusu = QStackedWidget()
        self.ana_duzen.addWidget(self.miktar_kutusu)
        self.miktar_kutusu.addWidget(QWidget()) 
        kg_sayfasi = QWidget()
        kg_duzen = QHBoxLayout()
        self.kg_etiket = QLabel("Miktar: 0.5 KG")
        self.kg_etiket.setStyleSheet("font-weight: bold; font-size: 14px;")
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
        adet_etiket = QLabel("Adet:")
        adet_etiket.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.adet_spinbox = QSpinBox()
        self.adet_spinbox.setMinimum(1)
        self.adet_spinbox.setStyleSheet("font-size: 14px; padding: 5px;")
        adet_duzen.addWidget(adet_etiket)
        adet_duzen.addWidget(self.adet_spinbox)
        adet_duzen.addStretch()
        adet_sayfasi.setLayout(adet_duzen)
        self.miktar_kutusu.addWidget(adet_sayfasi)
        self.ekle_butonu = QPushButton("🛒 Sepete Ekle")
        self.ekle_butonu.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; font-size: 14px; padding: 10px; border-radius: 5px;")
        self.ekle_butonu.setEnabled(False) 
        self.ekle_butonu.clicked.connect(self.sepete_yaz)
        self.ana_duzen.addWidget(self.ekle_butonu)
        self.tablo = QTableWidget(0, 4)
        self.tablo.setHorizontalHeaderLabels(["Ürün", "Miktar", "Birim Fiyat", "Toplam Fiyat"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        self.ana_duzen.addWidget(self.tablo)
        odeme_etiketi = QLabel("💳 Ödeme Yöntemi Seçiniz:")
        odeme_etiketi.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        self.ana_duzen.addWidget(odeme_etiketi)
        odeme_duzen = QHBoxLayout()
        self.rb_nakit = QRadioButton("Kapıda Nakit")
        self.rb_kredi = QRadioButton("Kredi Kartı (Online)")
        self.rb_kapida_kredi = QRadioButton("Kapıda Kredi Kartı")
        self.rb_nakit.setChecked(True) 
        odeme_duzen.addWidget(self.rb_nakit)
        odeme_duzen.addWidget(self.rb_kredi)
        odeme_duzen.addWidget(self.rb_kapida_kredi)
        odeme_kutusu = QWidget()
        odeme_kutusu.setLayout(odeme_duzen)
        self.ana_duzen.addWidget(odeme_kutusu)
        alt_bilgi_duzeni = QHBoxLayout()
        self.genel_toplam_etiketi = QLabel("Genel Toplam: 0.00 TL")
        self.genel_toplam_etiketi.setStyleSheet("font-weight: bold; font-size: 20px; color: #D32F2F;") # Kırmızı ve büyük font
        self.siparis_butonu = QPushButton("✅ Siparişi Tamamla")
        self.siparis_butonu.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; font-size: 14px; padding: 10px; border-radius: 5px;")
        self.siparis_butonu.clicked.connect(self.siparisi_tamamla)
        alt_bilgi_duzeni.addWidget(self.genel_toplam_etiketi)
        alt_bilgi_duzeni.addStretch() # Aralarını açmak için
        alt_bilgi_duzeni.addWidget(self.siparis_butonu)
        alt_kutu = QWidget()
        alt_kutu.setLayout(alt_bilgi_duzeni)
        self.ana_duzen.addWidget(alt_kutu)
    def katagorileri_yukle(self):
        try:
            baglanti = sqlite3.connect(DB_YOLU)
            imlec = baglanti.cursor()
            imlec.execute("SELECT DISTINCT urunreyonu FROM Ürünler")
            katagoriler = [satir[0] for satir in imlec.fetchall()]
            self.katagori_secimi.addItem("Katagori Seçiniz")
            self.katagori_secimi.addItems(katagoriler)
            baglanti.close()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veritabanı okunamadı:\n{str(e)}")
    def urunleri_getir(self, secilen_katagori):
        if secilen_katagori == "Katagori Seçiniz" or secilen_katagori == "":
            self.urun_secimi.clear()
            self.urun_secimi.setEnabled(False)
            self.miktar_kutusu.setCurrentIndex(0)
            return
        self.urun_secimi.setEnabled(True)
        self.urun_secimi.clear()    
        self.urun_secimi.addItem("--*-- Ürün Seçiniz --*--")
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
        self.kg_etiket.setText(f"Miktar: {kg} KG")
    def urun_detayini_getir(self, secilen_urun):
        if secilen_urun == "--*-- Ürün Seçiniz --*--" or secilen_urun == "":
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
        self.tablo.setItem(mevcut_satir, 0, QTableWidgetItem(urun))
        self.tablo.setItem(mevcut_satir, 1, QTableWidgetItem(tur_yazisi))
        self.tablo.setItem(mevcut_satir, 2, QTableWidgetItem(f"{fiyat} TL"))
        self.tablo.setItem(mevcut_satir, 3, QTableWidgetItem(f"{toplam_fiyat:.2f} TL"))
        self.genel_toplami_hesapla()
    def genel_toplami_hesapla(self):
        toplam = 0.0
        for satir in range(self.tablo.rowCount()):
            fiyat_metni = self.tablo.item(satir, 3).text()
            fiyat_sayisi = float(fiyat_metni.replace(" TL", ""))
            toplam += fiyat_sayisi
        self.genel_toplam_etiketi.setText(f"Genel Toplam: {toplam:.2f} TL")
    def siparisi_tamamla(self):
        if self.tablo.rowCount() == 0:
            QMessageBox.warning(self, "Uyarı", "Sepetiniz şu an boş! Lütfen önce ürün ekleyin.")
            return
        if self.rb_nakit.isChecked():
            odeme_tipi = "Kapıda Nakit"
        elif self.rb_kredi.isChecked():
            odeme_tipi = "Kredi Kartı (Online)"
        else:
            odeme_tipi = "Kapıda Kredi Kartı"
        tutar = self.genel_toplam_etiketi.text()
        QMessageBox.information(self, "Fatura / Fiş", 
                                f"🎉 Siparişiniz Başarıyla Alındı!\n\n"
                                f"Seçilen Yöntem: {odeme_tipi}\n"
                                f"Ödenecek Tutar: {tutar}\n\n"
                                f"Bizi tercih ettiğiniz için teşekkür ederiz."
                                f"Siparişiniz en kısa sürede hazırlanıp size teslim edilecektir!")
        self.tablo.setRowCount(0)
        self.genel_toplami_hesapla()
        self.katagori_secimi.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = MarketUygulamasi()
    pencere.show()
    sys.exit(app.exec_())