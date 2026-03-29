import sys
import os 
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QComboBox, QMessageBox, QDesktopWidget) 
from PyQt5.QtCore import Qt
KLASOR = os.path.dirname(os.path.abspath(__file__))
DB_YOLU = os.path.join(KLASOR, "ürünler.db")

class MarketUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sanal Market Uygulaması v3.0")
        self.setGeometry(100, 100, 500, 400) 
        self.pencereyi_ortala()
        merkez_zemin = QWidget()
        self.setCentralWidget(merkez_zemin)
        self.ana_duzen = QVBoxLayout()
        merkez_zemin.setLayout(self.ana_duzen)
        self.arayuzu_olustur()
        self.katagorileri_yukle()
    def pencereyi_ortala(self):
        pencere_alani = self.frameGeometry()
        ekran_merkezi = QDesktopWidget().availableGeometry().center()
        pencere_alani.moveCenter(ekran_merkezi)
        self.move(pencere_alani.topLeft())
    def arayuzu_olustur(self):
        self.katagori_etiketi = QLabel("1. Reyon Seçiniz:")
        self.katagori_etiketi.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
        self.ana_duzen.addWidget(self.katagori_etiketi)
        self.katagori_secimi = QComboBox()
        self.katagori_secimi.setStyleSheet("font-size: 14px; padding: 5px;")
        self.ana_duzen.addWidget(self.katagori_secimi)
        self.katagori_secimi.currentTextChanged.connect(self.urunleri_getir)
        self.urun_etiketi = QLabel("2. Ürün Seçiniz:")
        self.urun_etiketi.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 15px;")
        self.ana_duzen.addWidget(self.urun_etiketi)
        self.urun_secimi = QComboBox()
        self.urun_secimi.setStyleSheet("font-size: 14px; padding: 5px;")
        self.urun_secimi.setEnabled(False) 
        self.ana_duzen.addWidget(self.urun_secimi)
        self.ana_duzen.addStretch()
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
            QMessageBox.critical(self, "Hata", f"Ürünler getirilirken hata oluştu:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = MarketUygulamasi()
    pencere.show()
    sys.exit(app.exec_())