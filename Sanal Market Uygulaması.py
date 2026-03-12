import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                             QVBoxLayout, QHBoxLayout, QCheckBox, QComboBox, 
                             QRadioButton, QSlider, QSpinBox, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QStackedWidget, QGroupBox, QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt

class MarketUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sanal Market Uygulaması")
        self.setGeometry(100, 100, 950, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Ürünler ve Birim Fiyatlar
        self.urun_fiyatlari = {
            "Domates": 5, "Muz": 12, "Elma": 4, "Salatalık": 3,
            "Cips": 45, "Çikolata": 20, "Bisküvi": 15, "Kraker": 10,
            "Kola": 40, "Su": 5, "Meyve Suyu": 30, "Ayran": 15,
            "Şampuan": 120, "Sabun": 25, "Diş Macunu": 80, "Deodorant": 95
        }
        
        self.urun_datalari = {
            "Manav": ["Domates", "Muz", "Elma", "Salatalık"],
            "Atıştırmalık": ["Cips", "Çikolata", "Bisküvi", "Kraker"],
            "İçecekler": ["Kola", "Su", "Meyve Suyu", "Ayran"],
            "Kişisel Bakım": ["Şampuan", "Sabun", "Diş Macunu", "Deodorant"]
        }
        
        self.ana_checkboxlar = {}
        self.aktif_miktar_kontroleri = {}

        self.arayuz_hazirla()

    def arayuz_hazirla(self):
        # --- SEKME 1: SEÇİM ---
        self.tab1 = QWidget()
        l1 = QVBoxLayout()
        self.kategori_combo = QComboBox()
        self.kategori_combo.addItems(self.urun_datalari.keys())
        self.kategori_combo.currentIndexChanged.connect(lambda i: self.reyon_stack.setCurrentIndex(i))
        l1.addWidget(QLabel("<b>1. Reyon Seçiniz:</b>"))
        l1.addWidget(self.kategori_combo)

        self.reyon_stack = QStackedWidget()
        for kat, urunler in self.urun_datalari.items():
            sayfa = QWidget(); sl = QVBoxLayout()
            for u in urunler:
                cb = QCheckBox(f"{u} (Birim Fiyat: {self.urun_fiyatlari[u]} TL)")
                self.ana_checkboxlar[u] = (kat, cb)
                sl.addWidget(cb)
            sl.addStretch(); sayfa.setLayout(sl); self.reyon_stack.addWidget(sayfa)
        
        l1.addWidget(self.reyon_stack)
        b1 = QPushButton("Miktarları Belirle >>")
        b1.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        l1.addWidget(b1); self.tab1.setLayout(l1); self.tabs.addTab(self.tab1, "1. Ürün Seçimi")

        # --- SEKME 2: MİKTAR ---
        self.tab2 = QWidget(); self.l2_ana = QVBoxLayout()
        self.m_scroll = QScrollArea(); self.m_scroll.setWidgetResizable(True)
        self.m_icerik = QWidget(); self.m_layout = QVBoxLayout(self.m_icerik)
        self.m_scroll.setWidget(self.m_icerik)
        self.l2_ana.addWidget(QLabel("<b>2. Miktar ve Gramaj Ayarı:</b>"))
        self.l2_ana.addWidget(self.m_scroll)
        b2 = QPushButton("Sepeti Hesapla ve Onayla")
        b2.clicked.connect(self.sepete_aktar)
        self.l2_ana.addWidget(b2); self.tab2.setLayout(self.l2_ana); self.tabs.addTab(self.tab2, "2. Miktar")

        # --- SEKME 3: SEPET VE FİYAT ---
        self.tab3 = QWidget(); l3 = QVBoxLayout()
        self.tablo = QTableWidget(0, 4)
        self.tablo.setHorizontalHeaderLabels(["Ürün", "Miktar", "Birim Fiyat", "Ara Toplam"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l3.addWidget(self.tablo)

        odeme_grup = QGroupBox("Ödeme Detayları")
        og_layout = QVBoxLayout()
        self.r_nakit = QRadioButton("Kapıda Nakit")
        self.r_kart = QRadioButton("Kredi Kartı (Hemen Öde)")
        self.r_kapida_kart = QRadioButton("Kredi Kartı (Kapıda Ödeme)")
        self.r_nakit.setChecked(True)
        og_layout.addWidget(self.r_nakit); og_layout.addWidget(self.r_kart); og_layout.addWidget(self.r_kapida_kart)
        odeme_grup.setLayout(og_layout); l3.addWidget(odeme_grup)

        self.toplam_etiket = QLabel("<b>TOPLAM TUTAR: 0.00 TL</b>")
        self.toplam_etiket.setStyleSheet("font-size: 18px; color: #2c3e50;")
        self.toplam_etiket.setAlignment(Qt.AlignRight)
        l3.addWidget(self.toplam_etiket)

        b3 = QPushButton("SİPARİŞİ TAMAMLA VE ÖDE")
        b3.setFixedHeight(50); b3.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        b3.clicked.connect(self.siparis_tamamla)
        l3.addWidget(b3); self.tab3.setLayout(l3); self.tabs.addTab(self.tab3, "3. Sepet ve Ödeme")

        self.tabs.currentChanged.connect(self.miktar_paneli_olustur)

    def miktar_paneli_olustur(self, index):
        if index == 1:
            # 2. sekmeyi her girişte temizle
            for i in reversed(range(self.m_layout.count())):
                item = self.m_layout.itemAt(i)
                if item.widget():
                    item.widget().setParent(None)
            
            self.aktif_miktar_kontroleri = {}
            
            for urun, (kat, cb) in self.ana_checkboxlar.items():
                if cb.isChecked():
                    row_w = QWidget(); row_l = QHBoxLayout()
                    row_l.addWidget(QLabel(f"<b>{urun}</b>"), 2)
                    
                    if kat == "Manav":
                        sld = QSlider(Qt.Horizontal)
                        sld.setRange(100, 5000)
                        sld.setSingleStep(100)
                        sld.setPageStep(100)
                        v_l = QLabel("100 gr")
                        
                        # Mouse ile çekince 100'e yuvarlama fonksiyonu
                        def yuvarla(deger, s=sld, l=v_l):
                            yeni = (deger // 100) * 100
                            if s.value() != yeni:
                                s.blockSignals(True)
                                s.setValue(yeni)
                                s.blockSignals(False)
                            l.setText(f"{yeni} gr")
                        
                        sld.valueChanged.connect(yuvarla)
                        row_l.addWidget(sld, 3); row_l.addWidget(v_l, 1)
                        self.aktif_miktar_kontroleri[urun] = (sld, "gr", kat)
                    else:
                        spn = QSpinBox()
                        spn.setRange(1, 50)
                        row_l.addWidget(spn, 3); row_l.addWidget(QLabel("Adet"), 1)
                        self.aktif_miktar_kontroleri[urun] = (spn, "Adet", kat)
                    
                    row_w.setLayout(row_l)
                    self.m_layout.addWidget(row_w)
            
            self.m_layout.addStretch()

    def sepete_aktar(self):
        self.tablo.setRowCount(0); genel_toplam = 0
        if not self.aktif_miktar_kontroleri:
            QMessageBox.Warning(self, "Hata", "Lütfen önce ürün seçiniz!")
            return

        for urun, (widget, birim, kat) in self.aktif_miktar_kontroleri.items():
            row = self.tablo.rowCount(); self.tablo.insertRow(row)
            miktar = widget.value()
            birim_fiyat = self.urun_fiyatlari[urun]
            
            if kat == "Manav":
                ara_toplam = (miktar / 100) * birim_fiyat
                miktar_metin = f"{miktar} gr"
            else:
                ara_toplam = miktar * birim_fiyat
                miktar_metin = f"{miktar} Adet"
            
            genel_toplam += ara_toplam
            self.tablo.setItem(row, 0, QTableWidgetItem(urun))
            self.tablo.setItem(row, 1, QTableWidgetItem(miktar_metin))
            self.tablo.setItem(row, 2, QTableWidgetItem(f"{birim_fiyat} TL"))
            self.tablo.setItem(row, 3, QTableWidgetItem(f"{ara_toplam:.2f} TL"))
            
        self.toplam_etiket.setText(f"<b>TOPLAM TUTAR: {genel_toplam:.2f} TL</b>")
        self.tabs.setCurrentIndex(2)

    def siparis_tamamla(self):
        if self.tablo.rowCount() == 0:
            QMessageBox.Warning(self, "Hata", "Sepetiniz boş!")
            return

        odeme = "Kapıda Nakit"
        if self.r_kart.isChecked(): odeme = "Kredi Kartı (Hemen)"
        elif self.r_kapida_kart.isChecked(): odeme = "Kredi Kartı (Kapıda)"
        
        QMessageBox.information(self, "Başarılı", f"Siparişiniz Alındı!\n\n{self.toplam_etiket.text().replace('<b>','').replace('</b>','')}\nÖdeme: {odeme}")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MarketUygulamasi()
    ex.show()
    sys.exit(app.exec_())