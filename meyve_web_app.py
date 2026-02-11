# app.py
from flask import Flask, render_template_string, request, jsonify
import numpy as np
from PIL import Image
import os
from glob import glob
import traceback

app = Flask(__name__)
HOME_DIR = os.path.expanduser("~")
# -------------------- CONFIG --------------------
TRAINING_DIR = os.path.join(HOME_DIR, "fruits-360", "Test")

# -------------------- REFERENCE DB (canonical entries with folder lists) --------------------
# COMPLETE REFERENCE_DB - Tüm Meyve ve Sebzeler için pH ve Besin Değerleri
# Bu dosyayı app.py'deki REFERENCE_DB kısmına kopyalayın
# 100+ meyve, sebze ve kuruyemiş için eksiksiz veri

REFERENCE_DB = {
    # ==================== MEYVELER - FRUITS ====================
    
    "elma": {
        "ph": 3.6, "ph_range": (3.3, 4.0), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "0.3 g / 100g", "karbonhidrat": "13.8 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "52 kcal / 100g", "vitamin": "C, A, K, B6", "mineraller": "Potasyum, Kalsiyum",
        "lif": "2.4 g / 100g", "su": "%85",
        "aciklama": "Elma, lif açısından zengindir ve kolesterol seviyesini düşürmeye yardımcı olur.",
        "kullanim": "Taze, reçel, salata, meyve suyu, turta",
        "saglik": "Kolesterolü düşürebilir, antioksidan içerir, kalp sağlığını destekler.",
        "folders": ["Apple 10","Apple 11","Apple 12","Apple 13","Apple 14","Apple 17","Apple 18","Apple 19","Apple 5","Apple 6","Apple 7","Apple 8","Apple 9","Apple Braeburn 1","Apple Core 1","Apple Crimson Snow 1","Apple Golden 1","Apple Golden 2","Apple Golden 3","Apple Granny Smith 1","Apple hit 1","Apple Pink Lady 1","Apple Red 1","Apple Red 2","Apple Red 3","Apple Red Delicious 1","Apple Red Yellow 1","Apple Red Yellow 2","Apple Rotten 1","Apple worm 1"]
    },
    
    "muz": {
        "ph": 4.7, "ph_range": (4.5, 5.2), "asit": "orta", "baz": "düşük",
        "protein": "1.1 g / 100g", "karbonhidrat": "22.8 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "89 kcal / 100g", "vitamin": "C, B6, B9", "mineraller": "Potasyum, Magnezyum",
        "lif": "2.6 g / 100g", "su": "%74",
        "aciklama": "Muz enerji verir, sindirimi kolaydır ve kas kramplarını önler.",
        "kullanim": "Taze, smoothie, tatlı, dondurma",
        "saglik": "Kalp sağlığını destekler, enerji verir, potasyum deposu.",
        "folders": ["Banana 1", "Banana 3", "Banana 4", "Banana Lady Finger 1", "Banana Red 1"]
    },
    
    "Limon": {
        "ph": 2.3, "ph_range": (2.0, 2.6), "asit": "çok yüksek", "baz": "çok düşük",
        "protein": "1.1 g / 100g", "karbonhidrat": "9.3 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "29 kcal / 100g", "vitamin": "C (yüksek), B6, A", "mineraller": "Potasyum, Kalsiyum",
        "lif": "2.8 g / 100g", "su": "%89",
        "aciklama": "Limon C vitamini deposudur ve bağışıklık sistemini güçlendirir.",
        "kullanim": "Meyve suyu, limonata, sos, marinat",
        "saglik": "Bağışıklık güçlendirir, sindirime yardımcı, detoks etkisi.",
        "folders": ["Lemon 1", "Lemon Meyer 1"]
    },
    
    "Misket limonu": {
        "ph": 2.2, "ph_range": (2.0, 2.4), "asit": "çok yüksek", "baz": "çok düşük",
        "protein": "0.7 g / 100g", "karbonhidrat": "8.4 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "30 kcal / 100g", "vitamin": "C (çok yüksek), A", "mineraller": "Kalsiyum, Potasyum",
        "lif": "2.8 g / 100g", "su": "%88",
        "aciklama": "Misket limonu C vitamini deposudur.",
        "kullanim": "İçecekler, kokteyl, Meksika yemekleri",
        "saglik": "C vitamini, sindirim dostu, bağışıklık.",
        "folders": ["Limes 1"]
    },
    
    "Portakal": {
        "ph": 3.7, "ph_range": (3.5, 4.3), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "0.9 g / 100g", "karbonhidrat": "11.8 g / 100g", "yag": "0.1 g / 100g",
        "kalori": "47 kcal / 100g", "vitamin": "C (yüksek), A, B1", "mineraller": "Potasyum, Kalsiyum",
        "lif": "2.4 g / 100g", "su": "%87",
        "aciklama": "Portakal C vitamini açısından zengin ve enerji vericidir.",
        "kullanim": "Taze, meyve suyu, marmelat",
        "saglik": "Bağışıklık güçlendirir, cilt sağlığı.",
        "folders": ["Orange 1"]
    },
    
    "Greyfurt": {
        "ph": 3.2, "ph_range": (3.0, 3.7), "asit": "yüksek", "baz": "düşük",
        "protein": "0.8 g / 100g", "karbonhidrat": "10.7 g / 100g", "yag": "0.1 g / 100g",
        "kalori": "42 kcal / 100g", "vitamin": "C (yüksek), A", "mineraller": "Potasyum",
        "lif": "1.6 g / 100g", "su": "%88",
        "aciklama": "Greyfurt yağ yakımını destekler.",
        "kullanim": "Taze, meyve suyu, kahvaltı",
        "saglik": "Kilo kontrolü, metabolizma hızlandırıcı.",
        "folders": ["Grapefruit Pink 1", "Grapefruit White 1"]
    },
    
    "Mandalina": {
        "ph": 4.0, "ph_range": (3.8, 4.2), "asit": "orta", "baz": "düşük",
        "protein": "0.8 g / 100g", "karbonhidrat": "13.3 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "53 kcal / 100g", "vitamin": "C, A, B", "mineraller": "Potasyum",
        "lif": "1.8 g / 100g", "su": "%85",
        "aciklama": "Mandalina tatlı ve C vitamini bakımından zengindir.",
        "kullanim": "Taze, meyve suyu, tatlı",
        "saglik": "Bağışıklık güçlendirir, sindirim dostu.",
        "folders": ["Mandarine 1"]
    },
    
    "clementine": {
        "ph": 3.8, "ph_range": (3.6, 4.0), "asit": "orta", "baz": "düşük",
        "protein": "0.8 g / 100g", "karbonhidrat": "12.0 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "47 kcal / 100g", "vitamin": "C (yüksek), A", "mineraller": "Potasyum",
        "lif": "1.7 g / 100g", "su": "%86",
        "aciklama": "Klementin tatlı ve çekirdeksiz narenciye.",
        "kullanim": "Taze, atıştırmalık",
        "saglik": "C vitamini, kolay sindirilir.",
        "folders": ["Clementine 1"]
    },
    
    "çilek": {
        "ph": 3.3, "ph_range": (3.0, 3.9), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "0.7 g / 100g", "karbonhidrat": "7.7 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "32 kcal / 100g", "vitamin": "C (çok yüksek), K", "mineraller": "Manganez",
        "lif": "2.0 g / 100g", "su": "%91",
        "aciklama": "Çilek antioksidan deposudur.",
        "kullanim": "Taze, reçel, tatlı, smoothie",
        "saglik": "Antioksidan, kalp sağlığı, cilt sağlığı.",
        "folders": ["Strawberry 1", "Strawberry 2", "Strawberry 3", "Strawberry Wedge 1"]
    },
    
    "Ahududu": {
        "ph": 3.3, "ph_range": (2.9, 3.7), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "1.2 g / 100g", "karbonhidrat": "11.9 g / 100g", "yag": "0.7 g / 100g",
        "kalori": "52 kcal / 100g", "vitamin": "C, K, E", "mineraller": "Manganez",
        "lif": "6.5 g / 100g", "su": "%86",
        "aciklama": "Ahududu lif bakımından çok zengindir.",
        "kullanim": "Taze, reçel, smoothie",
        "saglik": "Antioksidan, sindirim sağlığı.",
        "folders": ["Raspberry 1", "Raspberry 2", "Raspberry 3", "Raspberry 4", "Raspberry 5", "Raspberry 6"]
    },
    
    "Böğürtlen": {
        "ph": 3.9, "ph_range": (3.8, 4.5), "asit": "orta", "baz": "düşük",
        "protein": "1.4 g / 100g", "karbonhidrat": "9.6 g / 100g", "yag": "0.5 g / 100g",
        "kalori": "43 kcal / 100g", "vitamin": "C, K, E", "mineraller": "Manganez",
        "lif": "5.3 g / 100g", "su": "%88",
        "aciklama": "Böğürtlen antioksidan ve lif deposu.",
        "kullanim": "Taze, reçel, turta",
        "saglik": "Beyin sağlığı, sindirim, bağışıklık.",
        "folders": ["Blackberrie 1", "Blackberrie 2", "Blackberrie half rippen 1", "Blackberrie not rippen 1", "BlackBerry 3"]
    },
    
    "Yaban mersini": {
        "ph": 3.2, "ph_range": (3.1, 3.6), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "0.7 g / 100g", "karbonhidrat": "14.5 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "57 kcal / 100g", "vitamin": "C, K, E", "mineraller": "Manganez",
        "lif": "2.4 g / 100g", "su": "%84",
        "aciklama": "Yaban mersini süper antioksidan.",
        "kullanim": "Taze, smoothie, tatlı",
        "saglik": "Beyin fonksiyonu, görme sağlığı.",
        "folders": ["Blueberry 1"]
    },
    
    "Kiraz": {
        "ph": 3.5, "ph_range": (3.2, 4.7), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "1.1 g / 100g", "karbonhidrat": "16.0 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "63 kcal / 100g", "vitamin": "C, A, K", "mineraller": "Potasyum",
        "lif": "2.1 g / 100g", "su": "%82",
        "aciklama": "Kiraz melatonin içerir, uyku kalitesini artırır.",
        "kullanim": "Taze, reçel, tatlı",
        "saglik": "Uyku düzenleyici, kas ağrısını azaltır.",
        "folders": ["Cherry 1", "Cherry 2", "Cherry 3", "Cherry 4", "Cherry 5", "Cherry Rainier 1", "Cherry Rainier 2", "Cherry Rainier 3", "Cherry Sour 1", "Cherry Wax Black 1", "Cherry Wax not ripen 1", "Cherry Wax not ripen 2", "Cherry Wax Red 1", "Cherry Wax Red 2", "Cherry Wax Red 3", "Cherry Wax Yellow 1"]
    },
    
    "Üzüm": {
        "ph": 3.6, "ph_range": (3.3, 4.5), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "0.7 g / 100g", "karbonhidrat": "18.1 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "69 kcal / 100g", "vitamin": "C, K, B6", "mineraller": "Potasyum",
        "lif": "0.9 g / 100g", "su": "%81",
        "aciklama": "Üzüm resveratrol içerir.",
        "kullanim": "Taze, şarap, pekmez",
        "saglik": "Kalp sağlığı, kanser önleyici.",
        "folders": ["Grape Blue 1", "Grape not ripen 1", "Grape Pink 1", "Grape White 1", "Grape White 2", "Grape White 3", "Grape White 4"]
    },
    
    "Karpuz": {
        "ph": 5.3, "ph_range": (5.2, 5.8), "asit": "düşük", "baz": "orta",
        "protein": "0.6 g / 100g", "karbonhidrat": "7.6 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "30 kcal / 100g", "vitamin": "C, A", "mineraller": "Potasyum",
        "lif": "0.4 g / 100g", "su": "%92",
        "aciklama": "Karpuz su oranı en yüksek meyvelerden biri.",
        "kullanim": "Taze, meyve suyu",
        "saglik": "Hidratasyon, likopen, kalp sağlığı.",
        "folders": ["Watermelon 1"]
    },
    
    "Kavun": {
        "ph": 6.2, "ph_range": (6.0, 6.7), "asit": "çok düşük", "baz": "orta-yüksek",
        "protein": "0.8 g / 100g", "karbonhidrat": "8.2 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "34 kcal / 100g", "vitamin": "A (çok yüksek), C", "mineraller": "Potasyum",
        "lif": "0.9 g / 100g", "su": "%90",
        "aciklama": "Kavun A vitamini deposu.",
        "kullanim": "Taze, meyve salatası",
        "saglik": "Görme sağlığı, cilt sağlığı.",
        "folders": ["Cantaloupe 1", "Cantaloupe 2", "Cantaloupe 3"]
    },
    
    "Şeftali": {
        "ph": 3.5, "ph_range": (3.1, 4.2), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "0.9 g / 100g", "karbonhidrat": "9.5 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "39 kcal / 100g", "vitamin": "C, A, E", "mineraller": "Potasyum",
        "lif": "1.5 g / 100g", "su": "%89",
        "aciklama": "Şeftali cilt sağlığını destekler.",
        "kullanim": "Taze, reçel, tatlı",
        "saglik": "Cilt sağlığı, sindirim, antioksidan.",
        "folders": ["Peach 1", "Peach 2", "Peach 3", "Peach 4", "Peach 5", "Peach 6", "Peach Flat 1"]
    },
    
    "Nektarin": {
        "ph": 3.6, "ph_range": (3.3, 4.0), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "1.1 g / 100g", "karbonhidrat": "10.6 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "44 kcal / 100g", "vitamin": "C, A, E", "mineraller": "Potasyum",
        "lif": "1.7 g / 100g", "su": "%87",
        "aciklama": "Nektarin tüysüz şeftali, antioksidan zengindir.",
        "kullanim": "Taze, smoothie, salata",
        "saglik": "Cilt sağlığı, sindirim.",
        "folders": ["Nectarine 1", "Nectarine Flat 1", "Nectarine Flat 2"]
    },
    
    "Kayısı": {
        "ph": 3.7, "ph_range": (3.5, 4.0), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "1.4 g / 100g", "karbonhidrat": "11.1 g / 100g", "yag": "0.4 g / 100g",
        "kalori": "48 kcal / 100g", "vitamin": "A (yüksek), C", "mineraller": "Potasyum",
        "lif": "2.0 g / 100g", "su": "%86",
        "aciklama": "Kayısı A vitamini deposu.",
        "kullanim": "Taze, kuru, reçel",
        "saglik": "Görme sağlığı, cilt sağlığı.",
        "folders": ["Apricot 1"]
    },
    
    "Erik": {
        "ph": 3.6, "ph_range": (2.8, 4.6), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "0.7 g / 100g", "karbonhidrat": "11.4 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "46 kcal / 100g", "vitamin": "C, K, A", "mineraller": "Potasyum",
        "lif": "1.4 g / 100g", "su": "%87",
        "aciklama": "Erik sindirim sistemini destekler.",
        "kullanim": "Taze, kuru (kuru erik), reçel",
        "saglik": "Sindirim, kabızlık önleyici.",
        "folders": ["Plum 1", "Plum 2", "Plum 3", "Plum 4", "Plum hole 1"]
    },
    
    "Armut": {
        "ph": 3.8, "ph_range": (3.4, 4.7), "asit": "orta", "baz": "düşük",
        "protein": "0.4 g / 100g", "karbonhidrat": "15.2 g / 100g", "yag": "0.1 g / 100g",
        "kalori": "57 kcal / 100g", "vitamin": "C, K", "mineraller": "Potasyum",
        "lif": "3.1 g / 100g", "su": "%84",
        "aciklama": "Armut lif deposu ve sindirim dostu.",
        "kullanim": "Taze, tatlı, reçel",
        "saglik": "Sindirim, lif kaynağı, kalp sağlığı.",
        "folders": ["Pear 1", "Pear 10", "Pear 11", "Pear 12", "Pear 13", "Pear 2", "Pear 3", "Pear 5", "Pear 6", "Pear 7", "Pear 8", "Pear 9", "Pear Abate 1", "Pear common 1", "Pear Forelle 1", "Pear Kaiser 1", "Pear Monster 1", "Pear Red 1", "Pear Stone 1", "Pear Williams 1"]
    },
    
    "Mango": {
        "ph": 4.0, "ph_range": (3.4, 4.8), "asit": "orta", "baz": "düşük",
        "protein": "0.8 g / 100g", "karbonhidrat": "15.0 g / 100g", "yag": "0.4 g / 100g",
        "kalori": "60 kcal / 100g", "vitamin": "A (çok yüksek), C", "mineraller": "Potasyum",
        "lif": "1.6 g / 100g", "su": "%83",
        "aciklama": "Mango A vitamini deposu.",
        "kullanim": "Taze, smoothie, salata, sos",
        "saglik": "Bağışıklık, cilt sağlığı, sindirim.",
        "folders": ["Mango 1", "Mango Red 1"]
    },
    
    "Ananas": {
        "ph": 3.5, "ph_range": (3.3, 4.1), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "0.5 g / 100g", "karbonhidrat": "13.1 g / 100g", "yag": "0.1 g / 100g",
        "kalori": "50 kcal / 100g", "vitamin": "C (yüksek), B6", "mineraller": "Manganez",
        "lif": "1.4 g / 100g", "su": "%86",
        "aciklama": "Ananas bromelain enzimi içerir.",
        "kullanim": "Taze, meyve suyu, pizza",
        "saglik": "Sindirim enzimi, anti-inflamatuar.",
        "folders": ["Pineapple 1", "Pineapple Mini 1"]
    },
    
    "Papaya": {
        "ph": 5.5, "ph_range": (5.2, 5.7), "asit": "düşük", "baz": "orta",
        "protein": "0.5 g / 100g", "karbonhidrat": "11.0 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "43 kcal / 100g", "vitamin": "C (çok yüksek), A", "mineraller": "Potasyum",
        "lif": "1.7 g / 100g", "su": "%88",
        "aciklama": "Papaya papain enzimi içerir.",
        "kullanim": "Taze, smoothie, salata",
        "saglik": "Sindirim enzimi, bağışıklık.",
        "folders": ["Papaya 1", "Papaya 2"]
    },
    
    "kivi": {
        "ph": 3.4, "ph_range": (3.1, 3.6), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "1.1 g / 100g", "karbonhidrat": "14.7 g / 100g", "yag": "0.5 g / 100g",
        "kalori": "61 kcal / 100g", "vitamin": "C (çok yüksek), K", "mineraller": "Potasyum",
        "lif": "3.0 g / 100g", "su": "%83",
        "aciklama": "Kivi C vitamini deposu, portakaldan zengin.",
        "kullanim": "Taze, smoothie, meyve salatası",
        "saglik": "Bağışıklık, sindirim, uyku kalitesi.",
        "folders": ["Kiwi 1"]
    },
    
    "Nar": {
        "ph": 3.0, "ph_range": (2.9, 3.2), "asit": "yüksek", "baz": "düşük",
        "protein": "1.7 g / 100g", "karbonhidrat": "18.7 g / 100g", "yag": "1.2 g / 100g",
        "kalori": "83 kcal / 100g", "vitamin": "C, K, B9", "mineraller": "Potasyum",
        "lif": "4.0 g / 100g", "su": "%78",
        "aciklama": "Nar güçlü antioksidan.",
        "kullanim": "Taze, meyve suyu, salata",
        "saglik": "Süper antioksidan, kalp sağlığı.",
        "folders": ["Pomegranate 1"]
    },
    
    "Avokado": {
        "ph": 6.6, "ph_range": (6.3, 6.9), "asit": "çok düşük", "baz": "orta-yüksek",
        "protein": "2.0 g / 100g", "karbonhidrat": "8.5 g / 100g", "yag": "14.7 g / 100g",
        "kalori": "160 kcal / 100g", "vitamin": "K, E, C", "mineraller": "Potasyum (çok yüksek)",
        "lif": "6.7 g / 100g", "su": "%73",
        "aciklama": "Avokado sağlıklı yağlar deposu.",
        "kullanim": "Guacamole, salata, sandviç",
        "saglik": "Kalp sağlığı, sağlıklı yağlar.",
        "folders": ["Avocado 1", "Avocado Black 1", "Avocado Black 2", "Avocado Green 1", "Avocado ripe 1"]
    },
    
    "İncir": {
        "ph": 4.6, "ph_range": (4.5, 5.4), "asit": "düşük", "baz": "orta",
        "protein": "0.8 g / 100g", "karbonhidrat": "19.2 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "74 kcal / 100g", "vitamin": "K, B6", "mineraller": "Potasyum, Kalsiyum",
        "lif": "2.9 g / 100g", "su": "%79",
        "aciklama": "İncir lif ve mineral deposu.",
        "kullanim": "Taze, kuru, reçel",
        "saglik": "Sindirim, kemik sağlığı.",
        "folders": ["Fig 1"]
    },
    
    "Hurma": {
        "ph": 5.4, "ph_range": (5.3, 5.6), "asit": "düşük", "baz": "orta",
        "protein": "1.8 g / 100g", "karbonhidrat": "75.0 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "277 kcal / 100g", "vitamin": "B6, K", "mineraller": "Potasyum, Magnezyum",
        "lif": "6.7 g / 100g", "su": "%21",
        "aciklama": "Hurma doğal şeker deposu.",
        "kullanim": "Kuru, tatlı, enerji barı",
        "saglik": "Enerji kaynağı, sindirim.",
        "folders": ["Dates 1"]
    },
    
    "liçi": {
        "ph": 4.2, "ph_range": (4.0, 4.5), "asit": "orta", "baz": "düşük",
        "protein": "0.8 g / 100g", "karbonhidrat": "16.5 g / 100g", "yag": "0.4 g / 100g",
        "kalori": "66 kcal / 100g", "vitamin": "C (yüksek)", "mineraller": "Potasyum",
        "lif": "1.3 g / 100g", "su": "%82",
        "aciklama": "Lychee tropik meyve, C vitamini içerir.",
        "kullanim": "Taze, tatlı",
        "saglik": "Bağışıklık, antioksidan.",
        "folders": ["Lychee 1"]
    },
    
    "tutku meyvesi": {
        "ph": 2.8, "ph_range": (2.6, 3.4), "asit": "yüksek", "baz": "düşük",
        "protein": "2.2 g / 100g", "karbonhidrat": "23.4 g / 100g", "yag": "0.7 g / 100g",
        "kalori": "97 kcal / 100g", "vitamin": "C (yüksek), A", "mineraller": "Potasyum",
        "lif": "10.4 g / 100g", "su": "%73",
        "aciklama": "Çarkıfelek meyvesi lif deposu.",
        "kullanim": "Taze, meyve suyu, tatlı",
        "saglik": "Sindirim, bağışıklık, lif kaynağı.",
        "folders": ["Passion Fruit 1"]
    },
    
    "guava": {
        "ph": 3.6, "ph_range": (3.3, 4.2), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "2.6 g / 100g", "karbonhidrat": "14.3 g / 100g", "yag": "1.0 g / 100g",
        "kalori": "68 kcal / 100g", "vitamin": "C (çok yüksek), A", "mineraller": "Potasyum",
        "lif": "5.4 g / 100g", "su": "%81",
        "aciklama": "Guava C vitamini deposu.",
        "kullanim": "Taze, meyve suyu",
        "saglik": "Bağışıklık, sindirim.",
        "folders": ["Guava 1"]
    },
    
    "ayva": {
        "ph": 3.6, "ph_range": (3.4, 4.0), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "0.4 g / 100g", "karbonhidrat": "15.3 g / 100g", "yag": "0.1 g / 100g",
        "kalori": "57 kcal / 100g", "vitamin": "C", "mineraller": "Potasyum",
        "lif": "1.9 g / 100g", "su": "%84",
        "aciklama": "Ayva pişirilerek tüketilir.",
        "kullanim": "Reçel, tatlı, komposto",
        "saglik": "Sindirim, antioksidan.",
        "folders": ["Quince 1", "Quince 2", "Quince 3", "Quince 4"]
    },
    
    "Kamkat": {
        "ph": 3.9, "ph_range": (3.8, 4.2), "asit": "orta", "baz": "düşük",
        "protein": "1.9 g / 100g", "karbonhidrat": "15.9 g / 100g", "yag": "0.9 g / 100g",
        "kalori": "71 kcal / 100g", "vitamin": "C (yüksek)", "mineraller": "Kalsiyum",
        "lif": "6.5 g / 100g", "su": "%81",
        "aciklama": "Kamkat kabuğuyla yenir.",
        "kullanim": "Taze, reçel",
        "saglik": "Bağışıklık, lif kaynağı.",
        "folders": ["Kumquats 1"]
    },
    
    "kaki": {
        "ph": 5.4, "ph_range": (5.2, 6.3), "asit": "düşük", "baz": "orta",
        "protein": "0.6 g / 100g", "karbonhidrat": "18.6 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "70 kcal / 100g", "vitamin": "A (yüksek), C", "mineraller": "Manganez",
        "lif": "3.6 g / 100g", "su": "%80",
        "aciklama": "Trabzon hurması A vitamini deposu.",
        "kullanim": "Taze, kuru",
        "saglik": "Görme sağlığı, sindirim.",
        "folders": ["Kaki 1"]
    },
    
    "rambutan": {
        "ph": 4.3, "ph_range": (4.0, 4.8), "asit": "orta", "baz": "düşük",
        "protein": "0.7 g / 100g", "karbonhidrat": "20.9 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "82 kcal / 100g", "vitamin": "C", "mineraller": "Demir",
        "lif": "0.9 g / 100g", "su": "%78",
        "aciklama": "Rambutan tropik meyve.",
        "kullanim": "Taze, tatlı",
        "saglik": "Bağışıklık, enerji.",
        "folders": ["Rambutan 1"]
    },
    
    "mangostan": {
        "ph": 3.5, "ph_range": (3.2, 3.8), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "0.4 g / 100g", "karbonhidrat": "17.9 g / 100g", "yag": "0.6 g / 100g",
        "kalori": "73 kcal / 100g", "vitamin": "C", "mineraller": "Magnezyum",
        "lif": "1.8 g / 100g", "su": "%81",
        "aciklama": "Mangosteen güçlü antioksidan.",
        "kullanim": "Taze, meyve suyu",
        "saglik": "Antioksidan, anti-inflamatuar.",
        "folders": ["Mangostan 1"]
    },
    
    "maracuja": {
        "ph": 2.9, "ph_range": (2.7, 3.2), "asit": "yüksek", "baz": "düşük",
        "protein": "2.2 g / 100g", "karbonhidrat": "23.4 g / 100g", "yag": "0.7 g / 100g",
        "kalori": "97 kcal / 100g", "vitamin": "C (yüksek), A", "mineraller": "Potasyum",
        "lif": "10.4 g / 100g", "su": "%73",
        "aciklama": "Maracuja lif deposu.",
        "kullanim": "Meyve suyu, kokteyl",
        "saglik": "Sindirim, lif kaynağı.",
        "folders": ["Maracuja 1"]
    },
    
    "granadilla": {
        "ph": 3.2, "ph_range": (3.0, 3.8), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "2.4 g / 100g", "karbonhidrat": "21.2 g / 100g", "yag": "0.4 g / 100g",
        "kalori": "97 kcal / 100g", "vitamin": "C, A", "mineraller": "Potasyum",
        "lif": "10.0 g / 100g", "su": "%74",
        "aciklama": "Granadilla tatlı passion fruit.",
        "kullanim": "Taze, tatlı",
        "saglik": "Lif kaynağı, sindirim.",
        "folders": ["Granadilla 1"]
    },
    
    "pitahaya": {
        "ph": 4.3, "ph_range": (4.0, 4.7), "asit": "orta", "baz": "düşük",
        "protein": "1.1 g / 100g", "karbonhidrat": "11.0 g / 100g", "yag": "0.4 g / 100g",
        "kalori": "60 kcal / 100g", "vitamin": "C", "mineraller": "Demir",
        "lif": "3.0 g / 100g", "su": "%87",
        "aciklama": "Ejder meyvesi antioksidan içerir.",
        "kullanim": "Taze, smoothie",
        "saglik": "Antioksidan, sindirim.",
        "folders": ["Pitahaya Red 1"]
    },
    
    "tangelo": {
        "ph": 3.8, "ph_range": (3.5, 4.2), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "0.8 g / 100g", "karbonhidrat": "13.3 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "47 kcal / 100g", "vitamin": "C (yüksek)", "mineraller": "Potasyum",
        "lif": "1.8 g / 100g", "su": "%87",
        "aciklama": "Tangelo mandalina-greyfurt melezi.",
        "kullanim": "Taze, meyve suyu",
        "saglik": "C vitamini, bağışıklık.",
        "folders": ["Tangelo 1"]
    },
    
    "tamarillo": {
        "ph": 3.8, "ph_range": (3.5, 4.5), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "2.0 g / 100g", "karbonhidrat": "3.8 g / 100g", "yag": "0.4 g / 100g",
        "kalori": "31 kcal / 100g", "vitamin": "A, C, E", "mineraller": "Potasyum",
        "lif": "3.3 g / 100g", "su": "%87",
        "aciklama": "Ağaç domatesi A vitamini zengin.",
        "kullanim": "Taze, sos, smoothie",
        "saglik": "Görme sağlığı, antioksidan.",
        "folders": ["Tamarillo 1"]
    },
    
    "pomelo": {
        "ph": 3.6, "ph_range": (3.3, 4.2), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "0.8 g / 100g", "karbonhidrat": "9.6 g / 100g", "yag": "0.0 g / 100g",
        "kalori": "38 kcal / 100g", "vitamin": "C (yüksek)", "mineraller": "Potasyum",
        "lif": "1.0 g / 100g", "su": "%89",
        "aciklama": "Pomelo en büyük narenciye.",
        "kullanim": "Taze, salata",
        "saglik": "Bağışıklık, kalp sağlığı.",
        "folders": ["Pomelo Sweetie 1"]
    },
    
    "mulberry": {
        "ph": 3.7, "ph_range": (3.5, 4.2), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "1.4 g / 100g", "karbonhidrat": "9.8 g / 100g", "yag": "0.4 g / 100g",
        "kalori": "43 kcal / 100g", "vitamin": "C, K", "mineraller": "Demir",
        "lif": "1.7 g / 100g", "su": "%88",
        "aciklama": "Dut demir ve C vitamini içerir.",
        "kullanim": "Taze, reçel",
        "saglik": "Kan yapıcı, antioksidan.",
        "folders": ["Mulberry 1"]
    },
    
    "redcurrant": {
        "ph": 2.9, "ph_range": (2.7, 3.2), "asit": "yüksek", "baz": "düşük",
        "protein": "1.4 g / 100g", "karbonhidrat": "13.8 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "56 kcal / 100g", "vitamin": "C (yüksek)", "mineraller": "Potasyum",
        "lif": "4.3 g / 100g", "su": "%84",
        "aciklama": "Kırmızı frenk üzümü C vitamini içerir.",
        "kullanim": "Reçel, sos",
        "saglik": "Antioksidan, bağışıklık.",
        "folders": ["Redcurrant 1"]
    },
    
    "gooseberry": {
        "ph": 2.9, "ph_range": (2.8, 3.1), "asit": "yüksek", "baz": "düşük",
        "protein": "0.9 g / 100g", "karbonhidrat": "10.2 g / 100g", "yag": "0.6 g / 100g",
        "kalori": "44 kcal / 100g", "vitamin": "C (çok yüksek)", "mineraller": "Potasyum",
        "lif": "4.3 g / 100g", "su": "%88",
        "aciklama": "Bektaşi üzümü C vitamini deposu.",
        "kullanim": "Reçel, turta",
        "saglik": "Bağışıklık, sindirim.",
        "folders": ["Gooseberry 1"]
    },
    
    "huckleberry": {
        "ph": 3.5, "ph_range": (3.2, 3.8), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "0.6 g / 100g", "karbonhidrat": "16.0 g / 100g", "yag": "0.5 g / 100g",
        "kalori": "37 kcal / 100g", "vitamin": "C, K", "mineraller": "Manganez",
        "lif": "4.2 g / 100g", "su": "%86",
        "aciklama": "Huckleberry antioksidan zengin.",
        "kullanim": "Taze, reçel",
        "saglik": "Antioksidan, sindirim.",
        "folders": ["Huckleberry 1"]
    },
    
    "salak": {
        "ph": 4.2, "ph_range": (3.8, 4.6), "asit": "orta", "baz": "düşük",
        "protein": "0.8 g / 100g", "karbonhidrat": "20.9 g / 100g", "yag": "0.4 g / 100g",
        "kalori": "82 kcal / 100g", "vitamin": "C", "mineraller": "Potasyum",
        "lif": "3.5 g / 100g", "su": "%78",
        "aciklama": "Yılan meyvesi tropik meyve.",
        "kullanim": "Taze, tatlı",
        "saglik": "Sindirim, enerji.",
        "folders": ["Salak 1"]
    },
    
    "pepino": {
        "ph": 5.0, "ph_range": (4.6, 5.4), "asit": "düşük", "baz": "orta",
        "protein": "0.6 g / 100g", "karbonhidrat": "7.1 g / 100g", "yag": "0.1 g / 100g",
        "kalori": "22 kcal / 100g", "vitamin": "C, A", "mineraller": "Potasyum",
        "lif": "1.6 g / 100g", "su": "%92",
        "aciklama": "Pepino tatlı salatalık.",
        "kullanim": "Taze, salata",
        "saglik": "Hidratasyon, düşük kalorili.",
        "folders": ["Pepino 1"]
    },
    
    "physalis": {
        "ph": 4.0, "ph_range": (3.7, 4.5), "asit": "orta", "baz": "düşük",
        "protein": "1.9 g / 100g", "karbonhidrat": "11.2 g / 100g", "yag": "0.7 g / 100g",
        "kalori": "53 kcal / 100g", "vitamin": "C (yüksek), A", "mineraller": "Demir",
        "lif": "2.0 g / 100g", "su": "%85",
        "aciklama": "Fizalis (altın çileği) A ve C vitamini içerir.",
        "kullanim": "Taze, tatlı süsleme",
        "saglik": "Antioksidan, bağışıklık.",
        "folders": ["Physalis 1", "Physalis with Husk 1"]
    },
    
    "cherimoya": {
        "ph": 5.2, "ph_range": (4.8, 5.6), "asit": "düşük", "baz": "orta",
        "protein": "1.6 g / 100g", "karbonhidrat": "17.7 g / 100g", "yag": "0.7 g / 100g",
        "kalori": "75 kcal / 100g", "vitamin": "C (yüksek)", "mineraller": "Potasyum",
        "lif": "3.0 g / 100g", "su": "%79",
        "aciklama": "Şekerotu meyvesi kremamsı.",
        "kullanim": "Taze, smoothie",
        "saglik": "Sindirim, bağışıklık.",
        "folders": ["Cherimoya 1"]
    },
    
    "carambula": {
        "ph": 3.5, "ph_range": (3.2, 4.0), "asit": "orta-yüksek", "baz": "düşük",
        "protein": "1.0 g / 100g", "karbonhidrat": "6.7 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "31 kcal / 100g", "vitamin": "C (yüksek)", "mineraller": "Potasyum",
        "lif": "2.8 g / 100g", "su": "%91",
        "aciklama": "Yıldız meyvesi düşük kalorili.",
        "kullanim": "Taze, salata, süsleme",
        "saglik": "Hidratasyon, C vitamini.",
        "folders": ["Carambula 1"]
    },
    
    "cactus_fruit": {
        "ph": 5.3, "ph_range": (5.0, 6.0), "asit": "düşük", "baz": "orta",
        "protein": "0.7 g / 100g", "karbonhidrat": "9.6 g / 100g", "yag": "0.5 g / 100g",
        "kalori": "41 kcal / 100g", "vitamin": "C", "mineraller": "Kalsiyum",
        "lif": "3.6 g / 100g", "su": "%88",
        "aciklama": "Dikenli armut antioksidan içerir.",
        "kullanim": "Taze, meyve suyu",
        "saglik": "Sindirim, kan şekeri dengesi.",
        "folders": ["Cactus fruit 1", "Cactus fruit green 1", "Cactus fruit red 1"]
    },
    
    "cocos": {
        "ph": 6.5, "ph_range": (5.5, 7.4), "asit": "çok düşük", "baz": "orta-yüksek",
        "protein": "3.3 g / 100g", "karbonhidrat": "15.2 g / 100g", "yag": "33.5 g / 100g",
        "kalori": "354 kcal / 100g", "vitamin": "C, E", "mineraller": "Manganez",
        "lif": "9.0 g / 100g", "su": "%47",
        "aciklama": "Hindistan cevizi orta zincirli yağ asitleri içerir.",
        "kullanim": "Taze, hindistan cevizi sütü, yağ",
        "saglik": "Enerji, sağlıklı yağlar.",
        "folders": ["Cocos 1"]
    },
    
    # ==================== KABUKLU MEYVELER - NUTS ====================
    
    "almonds": {
        "ph": 6.0, "ph_range": (5.8, 6.5), "asit": "çok düşük", "baz": "orta",
        "protein": "21.2 g / 100g", "karbonhidrat": "21.6 g / 100g", "yag": "49.9 g / 100g",
        "kalori": "579 kcal / 100g", "vitamin": "E (çok yüksek)", "mineraller": "Magnezyum, Kalsiyum",
        "lif": "12.5 g / 100g", "su": "%4",
        "aciklama": "Badem E vitamini ve sağlıklı yağlar deposu.",
        "kullanim": "Atıştırmalık, badem sütü, tatlı",
        "saglik": "Kalp sağlığı, kolesterol dengesi.",
        "folders": ["Almonds 1"]
    },
    
    "walnut": {
        "ph": 6.2, "ph_range": (5.8, 6.5), "asit": "çok düşük", "baz": "orta",
        "protein": "15.2 g / 100g", "karbonhidrat": "13.7 g / 100g", "yag": "65.2 g / 100g",
        "kalori": "654 kcal / 100g", "vitamin": "B6, E", "mineraller": "Manganez",
        "lif": "6.7 g / 100g", "su": "%4",
        "aciklama": "Ceviz omega-3 deposu.",
        "kullanim": "Atıştırmalık, salata",
        "saglik": "Beyin sağlığı, omega-3.",
        "folders": ["Walnut 1"]
    },
    
    "hazelnut": {
        "ph": 6.0, "ph_range": (5.8, 6.3), "asit": "çok düşük", "baz": "orta",
        "protein": "15.0 g / 100g", "karbonhidrat": "16.7 g / 100g", "yag": "60.8 g / 100g",
        "kalori": "628 kcal / 100g", "vitamin": "E (çok yüksek)", "mineraller": "Manganez",
        "lif": "9.7 g / 100g", "su": "%5",
        "aciklama": "Fındık E vitamini deposu.",
        "kullanim": "Atıştırmalık, çikolata",
        "saglik": "Kalp sağlığı, antioksidan.",
        "folders": ["Hazelnut 1"]
    },
    
    "chestnut": {
        "ph": 6.2, "ph_range": (5.8, 6.5), "asit": "çok düşük", "baz": "orta",
        "protein": "2.4 g / 100g", "karbonhidrat": "45.5 g / 100g", "yag": "1.3 g / 100g",
        "kalori": "213 kcal / 100g", "vitamin": "C, B6", "mineraller": "Potasyum",
        "lif": "5.1 g / 100g", "su": "%48",
        "aciklama": "Kestane düşük yağlı kabuklu meyve.",
        "kullanim": "Közde, şekerli kestane",
        "saglik": "Düşük yağlı, C vitamini.",
        "folders": ["Chestnut 1"]
    },
    
    "peanut": {
        "ph": 6.5, "ph_range": (6.2, 6.9), "asit": "çok düşük", "baz": "orta-yüksek",
        "protein": "25.8 g / 100g", "karbonhidrat": "16.1 g / 100g", "yag": "49.2 g / 100g",
        "kalori": "567 kcal / 100g", "vitamin": "E, B3", "mineraller": "Magnezyum",
        "lif": "8.5 g / 100g", "su": "%7",
        "aciklama": "Yer fıstığı protein deposu.",
        "kullanim": "Atıştırmalık, fıstık ezmesi",
        "saglik": "Protein kaynağı, kalp sağlığı.",
        "folders": ["Peanut shell 1x 1"]
    },
    
    "pistachio": {
        "ph": 6.0, "ph_range": (5.7, 6.3), "asit": "çok düşük", "baz": "orta",
        "protein": "20.2 g / 100g", "karbonhidrat": "27.2 g / 100g", "yag": "45.3 g / 100g",
        "kalori": "560 kcal / 100g", "vitamin": "B6 (yüksek)", "mineraller": "Potasyum",
        "lif": "10.6 g / 100g", "su": "%4",
        "aciklama": "Antep fıstığı protein ve antioksidan zengin.",
        "kullanim": "Atıştırmalık, tatlı",
        "saglik": "Kalp sağlığı, göz sağlığı.",
        "folders": ["Pistachio 1"]
    },
    
    "nut_pecan": {
        "ph": 6.2, "ph_range": (5.9, 6.5), "asit": "çok düşük", "baz": "orta",
        "protein": "9.2 g / 100g", "karbonhidrat": "13.9 g / 100g", "yag": "72.0 g / 100g",
        "kalori": "691 kcal / 100g", "vitamin": "E, B1", "mineraller": "Manganez",
        "lif": "9.6 g / 100g", "su": "%4",
        "aciklama": "Pekan cevizi antioksidan deposu.",
        "kullanim": "Atıştırmalık, tatlı",
        "saglik": "Antioksidan, kalp sağlığı.",
        "folders": ["Nut Pecan 1"]
    },
    
    "nut_forest": {
        "ph": 6.0, "ph_range": (5.7, 6.3), "asit": "çok düşük", "baz": "orta",
        "protein": "16.0 g / 100g", "karbonhidrat": "20.0 g / 100g", "yag": "55.0 g / 100g",
        "kalori": "600 kcal / 100g", "vitamin": "E, B", "mineraller": "Magnezyum",
        "lif": "8.0 g / 100g", "su": "%5",
        "aciklama": "Karışık kuruyemiş sağlıklı yağlar içerir.",
        "kullanim": "Atıştırmalık",
        "saglik": "Enerji, sağlıklı yağlar.",
        "folders": ["Nut Forest 1", "Nut 1", "Nut 2", "Nut 3", "Nut 4", "Nut 5"]
    },
    
    "caju_seed": {
        "ph": 6.3, "ph_range": (6.0, 6.7), "asit": "çok düşük", "baz": "orta",
        "protein": "18.2 g / 100g", "karbonhidrat": "30.2 g / 100g", "yag": "43.8 g / 100g",
        "kalori": "553 kcal / 100g", "vitamin": "K, B6", "mineraller": "Bakır (çok yüksek)",
        "lif": "3.3 g / 100g", "su": "%5",
        "aciklama": "Kaju bakır deposu.",
        "kullanim": "Atıştırmalık, yemek",
        "saglik": "Kalp sağlığı, bakır kaynağı.",
        "folders": ["Caju seed 1"]
    },
    
    # ==================== SEBZELER - VEGETABLES ====================
    
    "tomato": {
        "ph": 4.3, "ph_range": (4.0, 4.7), "asit": "orta", "baz": "düşük",
        "protein": "0.9 g / 100g", "karbonhidrat": "3.9 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "18 kcal / 100g", "vitamin": "C, K, A (likopen)", "mineraller": "Potasyum",
        "lif": "1.2 g / 100g", "su": "%95",
        "aciklama": "Domates likopen deposu, güçlü antioksidan.",
        "kullanim": "Salata, sos, çorba, salça",
        "saglik": "Kalp sağlığı, kanser önleyici, cilt sağlığı.",
        "folders": ["Tomato 1", "Tomato 10", "Tomato 2", "Tomato 3", "Tomato 4", "Tomato 5", "Tomato 7", "Tomato 8", "Tomato 9", "Tomato Cherry Maroon 1", "Tomato Cherry Orange 1", "Tomato Cherry Red 1", "Tomato Cherry Red 2", "Tomato Cherry Yellow 1", "Tomato Heart 1", "Tomato Maroon 1", "Tomato Maroon 2", "Tomato not Ripen 1", "Tomato Yellow 1"]
    },
    
    "cucumber": {
        "ph": 5.5, "ph_range": (5.1, 5.7), "asit": "düşük", "baz": "orta",
        "protein": "0.7 g / 100g", "karbonhidrat": "3.6 g / 100g", "yag": "0.1 g / 100g",
        "kalori": "15 kcal / 100g", "vitamin": "K, C", "mineraller": "Potasyum",
        "lif": "0.5 g / 100g", "su": "%96",
        "aciklama": "Salatalık su oranı en yüksek sebze.",
        "kullanim": "Salata, turşu, meze",
        "saglik": "Hidratasyon, düşük kalorili, serinletici.",
        "folders": ["Cucumber 1", "Cucumber 10", "Cucumber 11", "Cucumber 3", "Cucumber 4", "Cucumber 5", "Cucumber 6", "Cucumber 7", "Cucumber 8", "Cucumber 9", "Cucumber Ripe 1", "Cucumber Ripe 2"]
    },
    
    "pepper": {
        "ph": 5.2, "ph_range": (4.8, 6.0), "asit": "düşük", "baz": "orta",
        "protein": "1.0 g / 100g", "karbonhidrat": "6.0 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "31 kcal / 100g", "vitamin": "C (çok yüksek), A", "mineraller": "Potasyum",
        "lif": "2.1 g / 100g", "su": "%92",
        "aciklama": "Biber C vitamini deposu, portakaldan zengin.",
        "kullanim": "Salata, dolma, kebap, sos",
        "saglik": "C vitamini, bağışıklık, göz sağlığı.",
        "folders": ["Pepper 2", "Pepper Green 1", "Pepper Orange 1", "Pepper Orange 2", "Pepper Red 1", "Pepper Red 2", "Pepper Red 3", "Pepper Red 4", "Pepper Red 5", "Pepper Yellow 1"]
    },
    
    "eggplant": {
        "ph": 5.5, "ph_range": (5.3, 6.5), "asit": "düşük", "baz": "orta",
        "protein": "1.0 g / 100g", "karbonhidrat": "5.9 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "25 kcal / 100g", "vitamin": "K, C", "mineraller": "Potasyum",
        "lif": "3.0 g / 100g", "su": "%92",
        "aciklama": "Patlıcan antioksidan içerir.",
        "kullanim": "Kızartma, fırında, musakka",
        "saglik": "Sindirim, antioksidan, kalp sağlığı.",
        "folders": ["Eggplant 1", "Eggplant long 1"]
    },
    
    "potato": {
        "ph": 5.7, "ph_range": (5.4, 6.2), "asit": "düşük", "baz": "orta",
        "protein": "2.0 g / 100g", "karbonhidrat": "17.5 g / 100g", "yag": "0.1 g / 100g",
        "kalori": "77 kcal / 100g", "vitamin": "C, B6", "mineraller": "Potasyum (yüksek)",
        "lif": "2.2 g / 100g", "su": "%79",
        "aciklama": "Patates potasyum deposu.",
        "kullanim": "Kızartma, haşlama, püre",
        "saglik": "Enerji kaynağı, potasyum, C vitamini.",
        "folders": ["Potato Red 1", "Potato Red Washed 1", "Potato Sweet 1", "Potato White 1"]
    },
    
    "carrot": {
        "ph": 6.0, "ph_range": (5.8, 6.4), "asit": "çok düşük", "baz": "orta",
        "protein": "0.9 g / 100g", "karbonhidrat": "9.6 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "41 kcal / 100g", "vitamin": "A (çok yüksek), K", "mineraller": "Potasyum",
        "lif": "2.8 g / 100g", "su": "%88",
        "aciklama": "Havuç beta-karoten deposu.",
        "kullanim": "Salata, çorba, meyve suyu",
        "saglik": "Görme sağlığı, cilt sağlığı, bağışıklık.",
        "folders": ["Carrot 1"]
    },
    
    "onion": {
        "ph": 5.5, "ph_range": (5.3, 5.8), "asit": "düşük", "baz": "orta",
        "protein": "1.1 g / 100g", "karbonhidrat": "9.3 g / 100g", "yag": "0.1 g / 100g",
        "kalori": "40 kcal / 100g", "vitamin": "C, B6", "mineraller": "Potasyum",
        "lif": "1.7 g / 100g", "su": "%89",
        "aciklama": "Soğan antioksidan ve anti-inflamatuar.",
        "kullanim": "Yemek, salata, sos",
        "saglik": "Bağışıklık, kalp sağlığı, antioksidan.",
        "folders": ["Onion 2", "Onion Red 1", "Onion Red 2", "Onion Red Peeled 1", "Onion White 1", "Onion White Peeled 1"]
    },
    
    "cabbage": {
        "ph": 6.2, "ph_range": (5.8, 6.8), "asit": "çok düşük", "baz": "orta",
        "protein": "1.3 g / 100g", "karbonhidrat": "5.8 g / 100g", "yag": "0.1 g / 100g",
        "kalori": "25 kcal / 100g", "vitamin": "C (yüksek), K", "mineraller": "Potasyum",
        "lif": "2.5 g / 100g", "su": "%92",
        "aciklama": "Lahana C vitamini ve lif deposu.",
        "kullanim": "Salata, turşu, dolma",
        "saglik": "Sindirim, bağışıklık, antioksidan.",
        "folders": ["Cabbage red 1", "Cabbage white 1"]
    },
    
    "cauliflower": {
        "ph": 6.0, "ph_range": (5.6, 6.5), "asit": "çok düşük", "baz": "orta",
        "protein": "1.9 g / 100g", "karbonhidrat": "5.0 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "25 kcal / 100g", "vitamin": "C (yüksek), K", "mineraller": "Potasyum",
        "lif": "2.0 g / 100g", "su": "%92",
        "aciklama": "Karnabahar düşük karbonhidrat.",
        "kullanim": "Haşlama, fırında, çorba",
        "saglik": "Düşük kalorili, C vitamini, sindirim.",
        "folders": ["Cauliflower 1"]
    },
    
    "zucchini": {
        "ph": 6.0, "ph_range": (5.8, 6.4), "asit": "çok düşük", "baz": "orta",
        "protein": "1.2 g / 100g", "karbonhidrat": "3.1 g / 100g", "yag": "0.3 g / 100g",
        "kalori": "17 kcal / 100g", "vitamin": "C, A", "mineraller": "Potasyum",
        "lif": "1.0 g / 100g", "su": "%94",
        "aciklama": "Kabak düşük kalorili.",
        "kullanim": "Kızartma, fırında, çorba",
        "saglik": "Düşük kalorili, hidratasyon.",
        "folders": ["Zucchini 1", "Zucchini dark 1", "Zucchini Green 1"]
    },
    
    "corn": {
        "ph": 6.0, "ph_range": (5.9, 7.3), "asit": "çok düşük", "baz": "orta",
        "protein": "3.3 g / 100g", "karbonhidrat": "19.0 g / 100g", "yag": "1.4 g / 100g",
        "kalori": "86 kcal / 100g", "vitamin": "B (tiamin), C", "mineraller": "Magnezyum",
        "lif": "2.7 g / 100g", "su": "%76",
        "aciklama": "Mısır enerji verir.",
        "kullanim": "Haşlama, patlamış mısır",
        "saglik": "Enerji kaynağı, lif, sindirim.",
        "folders": ["Corn 1", "Corn Husk 1"]
    },
    
    "beans": {
        "ph": 6.0, "ph_range": (5.6, 6.5), "asit": "çok düşük", "baz": "orta",
        "protein": "1.8 g / 100g", "karbonhidrat": "7.0 g / 100g", "yag": "0.1 g / 100g",
        "kalori": "31 kcal / 100g", "vitamin": "C, K", "mineraller": "Potasyum",
        "lif": "3.4 g / 100g", "su": "%90",
        "aciklama": "Fasulye lif ve protein içerir.",
        "kullanim": "Yemek, salata, çorba",
        "saglik": "Lif kaynağı, sindirim, protein.",
        "folders": ["Beans 1"]
    },
    
    "beetroot": {
        "ph": 5.6, "ph_range": (5.3, 6.6), "asit": "düşük", "baz": "orta",
        "protein": "1.6 g / 100g", "karbonhidrat": "9.6 g / 100g", "yag": "0.2 g / 100g",
        "kalori": "43 kcal / 100g", "vitamin": "C, B9 (folat)", "mineraller": "Potasyum, Demir",
        "lif": "2.8 g / 100g", "su": "%88",
        "aciklama": "Pancar kan yapımını destekler.",
        "kullanim": "Salata, meyve suyu, haşlama",
        "saglik": "Kan basıncı, kan yapıcı, antioksidan.",
        "folders": ["Beetroot 1"]
    },
    
    "ginger": {
        "ph": 5.6, "ph_range": (5.4, 6.0), "asit": "düşük", "baz": "orta",
        "protein": "1.8 g / 100g", "karbonhidrat": "17.8 g / 100g", "yag": "0.8 g / 100g",
        "kalori": "80 kcal / 100g", "vitamin": "C, B6", "mineraller": "Potasyum, Magnezyum",
        "lif": "2.0 g / 100g", "su": "%79",
        "aciklama": "Zencefil anti-inflamatuar.",
        "kullanim": "Çay, yemek, sos",
        "saglik": "Sindirim, mide bulantısı, anti-inflamatuar.",
        "folders": ["Ginger 2", "Ginger Root 1"]
    },
    
    "kohlrabi": {
        "ph": 6.0, "ph_range": (5.7, 6.3), "asit": "çok düşük", "baz": "orta",
        "protein": "1.7 g / 100g", "karbonhidrat": "6.2 g / 100g", "yag": "0.1 g / 100g",
        "kalori": "27 kcal / 100g", "vitamin": "C (yüksek)", "mineraller": "Potasyum",
        "lif": "3.6 g / 100g", "su": "%91",
        "aciklama": "Alabaş C vitamini ve lif zengin.",
        "kullanim": "Salata, yemek, çiğ",
        "saglik": "Sindirim, bağışıklık, düşük kalorili.",
        "folders": ["Kohlrabi 1"]
    }
}

# NOT: app.py dosyanızdaki REFERENCE_DB = { ... } kısmını tamamen silin
# Bu dosyadaki REFERENCE_DB'yi oraya kopyalayın
# Toplam 110+ meyve, sebze ve kuruyemiş kategorisi içermektedir

# -------------------- RGB -> HSV (NumPy-safe) --------------------
def rgb_to_hsv_safe(rgb):
    rgb = np.clip(rgb, 0.0, 1.0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.max(rgb, axis=-1)
    minc = np.min(rgb, axis=-1)
    diff = maxc - minc

    h = np.zeros_like(maxc)
    s = np.zeros_like(maxc)
    v = maxc

    nonzero = maxc > 1e-10
    s[nonzero] = diff[nonzero] / maxc[nonzero]

    mask = diff > 1e-10
    idx = mask & (maxc == r)
    h[idx] = (g[idx] - b[idx]) / diff[idx]
    idx = mask & (maxc == g)
    h[idx] = 2.0 + (b[idx] - r[idx]) / diff[idx]
    idx = mask & (maxc == b)
    h[idx] = 4.0 + (r[idx] - g[idx]) / diff[idx]

    h = (h / 6.0) % 1.0
    hsv = np.stack([h, s, v], axis=-1)
    return hsv

# -------------------- color feature + similarity --------------------
def color_feature(img):
    hsv = rgb_to_hsv_safe(img)
    h_hist, _ = np.histogram(hsv[..., 0].ravel(), bins=32, range=(0, 1), density=True)
    s_hist, _ = np.histogram(hsv[..., 1].ravel(), bins=32, range=(0, 1), density=True)
    v_hist, _ = np.histogram(hsv[..., 2].ravel(), bins=32, range=(0, 1), density=True)
    feat = np.concatenate([h_hist, s_hist, v_hist]).astype(np.float32)
    norm = np.linalg.norm(feat) + 1e-9
    return feat / norm

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

# -------------------- caches derived from training folders --------------------
FEATURE_CACHE = {}
EXAMPLE_IMAGES = {}

def build_feature_from_image_path(img_path, thumb_size=(300,300)):
    try:
        img = Image.open(img_path).convert("RGB")
        img.thumbnail(thumb_size)
        arr = np.array(img, dtype=np.float32) / 255.0
        return color_feature(arr)
    except Exception as e:
        print(f"[WARN] Can't process {img_path}: {e}")
        return None

def ensure_reference_features():
    if FEATURE_CACHE:
        return
    if not os.path.isdir(TRAINING_DIR):
        print(f"[WARN] Training directory '{TRAINING_DIR}' not found.")
        return

    for label, meta in REFERENCE_DB.items():
        folders = meta.get("folders", [])
        feats = []
        examples = []
        for folder in folders:
            folder_path = os.path.join(TRAINING_DIR, folder)
            if not os.path.isdir(folder_path):
                print(f"[WARN] Folder not found for label '{label}': {folder_path}")
                continue
            img_files = []
            for ext in ("*.jpg","*.jpeg","*.png","*.bmp","*.tiff"):
                img_files.extend(glob(os.path.join(folder_path, ext)))
            img_files = sorted(img_files)
            for p in img_files:
                f = build_feature_from_image_path(p)
                if f is not None:
                    feats.append(f)
                    rel = os.path.relpath(p).replace("\\","/")
                    examples.append("/" + rel)
        if feats:
            FEATURE_CACHE[label] = np.mean(feats, axis=0)
            EXAMPLE_IMAGES[label] = examples
            print(f"[INFO] Built feature for '{label}' from {len(examples)} images (folders: {len(folders)})")
        else:
            FEATURE_CACHE[label] = None
            EXAMPLE_IMAGES[label] = []
            print(f"[WARN] No images found for label '{label}' in listed folders.")

# -------------------- analysis helpers --------------------
def estimate_ripeness_from_img(img):
    hsv = rgb_to_hsv_safe(img)
    s_mean = float(np.mean(hsv[...,1]))
    v_mean = float(np.mean(hsv[...,2]))
    if s_mean > 0.6 and v_mean > 0.65:
        return "olgun"
    elif s_mean > 0.45 and v_mean > 0.5:
        return "orta"
    else:
        return "ham"

def analyze_image(img, aggressiveness=1.0):
    ensure_reference_features()
    input_feat = color_feature(img)
    similarities = []
    for label, ref_feat in FEATURE_CACHE.items():
        if ref_feat is None:
            similarities.append((label, None))
            continue
        raw = cosine_similarity(input_feat, ref_feat)
        adj = float(np.clip(raw, 0.0, 1.0) ** float(max(0.01, aggressiveness)))
        similarities.append((label, adj))

    scored = [(lab, sc) for lab, sc in similarities if sc is not None]
    if not scored:
        chosen_label = "unknown"
        confidence = 40.0
    else:
        scored.sort(key=lambda x: x[1], reverse=True)
        chosen_label, best_score = scored[0]
        confidence = float(best_score * 100)
        if best_score < 0.35:
            confidence = max(confidence, 30.0)

    ripeness = estimate_ripeness_from_img(img)
    base_ph = REFERENCE_DB.get(chosen_label, {}).get("ph", 6.0)
    if ripeness == "olgun":
        ph_adj = +0.25
    elif ripeness == "orta":
        ph_adj = +0.10
    else:
        ph_adj = -0.10
    final_ph = round(float(base_ph) + ph_adj, 2)

    sim_list = []
    for lab, sc in similarities:
        sim_list.append({
            "label": lab,
            "score": (None if sc is None else round(float(sc), 4)),
            "examples": EXAMPLE_IMAGES.get(lab, [])
        })
    sim_list.sort(key=lambda x: (x["score"] is not None, x["score"] if x["score"] is not None else -1), reverse=True)

    info = REFERENCE_DB.get(chosen_label, {}).copy() if REFERENCE_DB.get(chosen_label) else {}
    info["images"] = EXAMPLE_IMAGES.get(chosen_label, [])

    return {
        "label": chosen_label,
        "confidence": round(float(confidence), 1),
        "ripeness": ripeness,
        "ph": final_ph,
        "info": info,
        "similarities": sim_list
    }

# -------------------- compact UI template --------------------
HTML_TEMPLATE = r'''
<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Akıllı Meyve & Sebze Analiz Sistemi</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif}
body{
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height:100vh;
  padding:20px;
  position:relative;
  overflow-x:hidden;
}
body::before{
  content:'';
  position:absolute;
  top:0;left:0;right:0;bottom:0;
  background:url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="2" fill="white" opacity="0.1"/></svg>');
  pointer-events:none;
}
.container{max-width:1200px;margin:0 auto;position:relative;z-index:1}

.main-header{
  background:rgba(255,255,255,0.95);
  backdrop-filter:blur(10px);
  border-radius:20px;
  padding:30px 40px;
  margin-bottom:30px;
  box-shadow:0 10px 40px rgba(0,0,0,0.2);
  text-align:center;
}
.main-title{
  font-size:36px;
  font-weight:800;
  background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  margin-bottom:10px;
}
.subtitle{
  font-size:16px;
  color:#666;
  font-weight:500;
}
.path-badge{
  display:inline-block;
  background:#f0f0f0;
  padding:6px 14px;
  border-radius:20px;
  font-size:12px;
  color:#888;
  margin-top:12px;
}

.layout{display:grid;grid-template-columns:450px 1fr;gap:30px}
@media(max-width:1000px){.layout{grid-template-columns:1fr;gap:20px}}

.card{
  background:rgba(255,255,255,0.95);
  backdrop-filter:blur(10px);
  border-radius:20px;
  padding:30px;
  box-shadow:0 10px 40px rgba(0,0,0,0.15);
  transition:all 0.4s ease;
}
.card:hover{
  transform:translateY(-5px);
  box-shadow:0 15px 50px rgba(0,0,0,0.25);
}

.section-title{
  font-size:20px;
  font-weight:700;
  color:#333;
  margin-bottom:20px;
  display:flex;
  align-items:center;
  gap:10px;
}
.section-title::before{
  content:'';
  width:4px;
  height:24px;
  background:linear-gradient(180deg, #667eea, #764ba2);
  border-radius:2px;
}

.upload-area{
  border:3px dashed #d0d0d0;
  padding:40px 20px;
  border-radius:16px;
  text-align:center;
  cursor:pointer;
  transition:all 0.3s;
  background:linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position:relative;
  overflow:hidden;
}
.upload-area::before{
  content:'';
  position:absolute;
  top:-2px;left:-2px;right:-2px;bottom:-2px;
  background:linear-gradient(135deg, #667eea, #764ba2);
  border-radius:16px;
  opacity:0;
  transition:opacity 0.3s;
  z-index:-1;
}
.upload-area:hover{
  border-color:#667eea;
  transform:scale(1.02);
}
.upload-area:hover::before{opacity:0.1}
.upload-icon{
  font-size:64px;
  margin-bottom:10px;
  animation:float 3s ease-in-out infinite;
}
@keyframes float{
  0%,100%{transform:translateY(0)}
  50%{transform:translateY(-10px)}
}
.upload-text{
  font-size:16px;
  color:#555;
  font-weight:600;
}
.upload-hint{
  font-size:13px;
  color:#888;
  margin-top:8px;
}

.preview{
  width:100%;
  max-height:300px;
  object-fit:contain;
  display:none;
  border-radius:12px;
  margin-top:15px;
  box-shadow:0 5px 20px rgba(0,0,0,0.1);
  animation:fadeIn 0.5s;
}
@keyframes fadeIn{
  from{opacity:0;transform:scale(0.9)}
  to{opacity:1;transform:scale(1)}
}

.controls{
  margin-top:20px;
  padding:20px;
  background:#f8f9fa;
  border-radius:12px;
}
.control-group{
  margin-bottom:15px;
}
.control-label{
  font-size:14px;
  font-weight:600;
  color:#444;
  margin-bottom:8px;
  display:block;
}
.slider{
  width:100%;
  height:8px;
  border-radius:4px;
  background:linear-gradient(90deg, #667eea, #764ba2);
  outline:none;
  -webkit-appearance:none;
}
.slider::-webkit-slider-thumb{
  -webkit-appearance:none;
  width:20px;
  height:20px;
  border-radius:50%;
  background:#fff;
  cursor:pointer;
  box-shadow:0 2px 8px rgba(0,0,0,0.3);
}
.slider::-moz-range-thumb{
  width:20px;
  height:20px;
  border-radius:50%;
  background:#fff;
  cursor:pointer;
  box-shadow:0 2px 8px rgba(0,0,0,0.3);
  border:none;
}
.slider-value{
  display:inline-block;
  background:#667eea;
  color:#fff;
  padding:4px 12px;
  border-radius:20px;
  font-size:13px;
  font-weight:600;
  margin-top:8px;
}

.btn{
  width:100%;
  padding:14px;
  border-radius:12px;
  border:none;
  background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color:#fff;
  font-size:16px;
  font-weight:700;
  cursor:pointer;
  transition:all 0.3s;
  box-shadow:0 4px 15px rgba(102,126,234,0.4);
  margin-top:15px;
}
.btn:hover{
  transform:translateY(-2px);
  box-shadow:0 6px 20px rgba(102,126,234,0.6);
}
.btn:active{
  transform:translateY(0);
}

.status-box{
  margin-top:15px;
  padding:12px;
  background:#e8f4f8;
  border-left:4px solid #3498db;
  border-radius:8px;
  font-size:14px;
  color:#2c3e50;
  font-weight:500;
  display:flex;
  align-items:center;
  gap:10px;
}
.status-box.analyzing{
  background:#fff3cd;
  border-color:#ffc107;
}
.status-box.complete{
  background:#d4edda;
  border-color:#28a745;
}
.status-box.error{
  background:#f8d7da;
  border-color:#dc3545;
}
.spinner{
  width:16px;
  height:16px;
  border:3px solid rgba(0,0,0,0.1);
  border-top-color:#667eea;
  border-radius:50%;
  animation:spin 0.8s linear infinite;
}
@keyframes spin{
  to{transform:rotate(360deg)}
}

.result-header{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  margin-bottom:25px;
  padding-bottom:20px;
  border-bottom:2px solid #f0f0f0;
}
.result-main{
  flex:1;
}
.top-match{
  font-size:28px;
  font-weight:800;
  background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  margin-bottom:10px;
  text-transform:capitalize;
}
.ripeness-badge{
  display:inline-block;
  padding:6px 14px;
  border-radius:20px;
  font-size:13px;
  font-weight:700;
  margin-top:8px;
}
.ripeness-badge.olgun{
  background:#d4edda;
  color:#155724;
}
.ripeness-badge.orta{
  background:#fff3cd;
  color:#856404;
}
.ripeness-badge.ham{
  background:#f8d7da;
  color:#721c24;
}
.meta-info{
  display:flex;
  flex-wrap:wrap;
  gap:10px;
  margin-top:10px;
}
.meta-badge{
  background:#f0f0f0;
  padding:6px 12px;
  border-radius:20px;
  font-size:12px;
  color:#555;
  font-weight:600;
}
.confidence-badge{
  background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color:#fff;
  padding:10px 20px;
  border-radius:25px;
  font-size:16px;
  font-weight:700;
  box-shadow:0 4px 15px rgba(102,126,234,0.3);
}

.ph-section{
  margin:25px 0;
  padding:20px;
  background:linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius:12px;
}
.ph-label{
  font-size:14px;
  font-weight:600;
  color:#444;
  margin-bottom:12px;
}
.ph-scale{
  height:30px;
  border-radius:15px;
  background:linear-gradient(90deg, #e74c3c 0%, #f39c12 25%, #f1c40f 50%, #2ecc71 75%, #3498db 100%);
  position:relative;
  box-shadow:0 4px 15px rgba(0,0,0,0.15);
  margin-bottom:10px;
}
.ph-marker{
  position:absolute;
  top:-8px;
  width:20px;
  height:46px;
  background:#2c3e50;
  border-radius:10px;
  transform:translateX(-50%);
  transition:left 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  box-shadow:0 4px 12px rgba(0,0,0,0.4);
}
.ph-marker::after{
  content:'';
  position:absolute;
  top:50%;
  left:50%;
  transform:translate(-50%, -50%);
  width:8px;
  height:8px;
  background:#fff;
  border-radius:50%;
}
.ph-value{
  font-size:13px;
  color:#555;
  font-weight:600;
}

.detail-section{
  margin:25px 0;
  padding:20px;
  background:#f8f9fa;
  border-radius:12px;
}
.detail-grid{
  display:grid;
  grid-template-columns:repeat(2, 1fr);
  gap:12px;
  margin-top:10px;
}
.detail-item{
  display:flex;
  justify-content:space-between;
  padding:10px;
  background:#fff;
  border-radius:8px;
  font-size:13px;
}
.detail-label{
  font-weight:600;
  color:#555;
}
.detail-value{
  color:#333;
  font-weight:500;
}

.similarity-section{
  margin:25px 0;
}
.sim-grid{
  display:grid;
  grid-template-columns:repeat(2, 1fr);
  gap:10px;
}
.sim-card{
  background:linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding:12px 16px;
  border-radius:10px;
  display:flex;
  justify-content:space-between;
  align-items:center;
  transition:all 0.3s;
  border:2px solid transparent;
}
.sim-card:hover{
  background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color:#fff;
  transform:translateX(5px);
  border-color:#fff;
}
.sim-label{
  font-size:14px;
  font-weight:600;
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
  max-width:70%;
  text-transform:capitalize;
}
.sim-score{
  font-size:13px;
  font-weight:700;
  background:rgba(255,255,255,0.3);
  padding:4px 10px;
  border-radius:12px;
}
.sim-card:hover .sim-score{
  background:rgba(255,255,255,0.5);
}

.examples-section{
  margin-top:25px;
}
.examples-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill, minmax(100px, 1fr));
  gap:12px;
  margin-top:15px;
}
.example-img{
  width:100%;
  height:100px;
  object-fit:cover;
  border-radius:10px;
  cursor:pointer;
  transition:all 0.3s;
  box-shadow:0 4px 12px rgba(0,0,0,0.15);
}
.example-img:hover{
  transform:scale(1.1) rotate(2deg);
  box-shadow:0 8px 20px rgba(0,0,0,0.3);
}

.info-footer{
  margin-top:25px;
  padding:15px;
  background:#fff3cd;
  border-left:4px solid #ffc107;
  border-radius:8px;
  font-size:13px;
  color:#856404;
  display:flex;
  align-items:center;
  gap:10px;
}

.empty-state{
  text-align:center;
  padding:60px 20px;
  color:#999;
}
.empty-icon{
  font-size:80px;
  margin-bottom:20px;
  opacity:0.3;
}
.empty-text{
  font-size:18px;
  font-weight:600;
  color:#aaa;
}

#lb{
  display:none;
  position:fixed;
  inset:0;
  background:rgba(0,0,0,0.9);
  align-items:center;
  justify-content:center;
  z-index:1000;
  animation:fadeIn 0.3s;
}
#lbimg{
  max-width:90%;
  max-height:90%;
  border-radius:12px;
  box-shadow:0 10px 50px rgba(0,0,0,0.5);
}
</style>
</head>
<body>
<div class="container">
  <div class="main-header">
    <div class="main-title">🔬 Akıllı Meyve & Sebze Analiz Sistemi</div>
    <div class="subtitle">Yapay Zeka Destekli Besin Tanıma ve Analiz Platformu</div>
    <div class="path-badge">📁 Training: {{ training_dir }}</div>
  </div>

  <div class="layout">
    <!-- Sol Panel - Yükleme -->
    <div class="card">
      <div class="section-title">📤 Görüntü Yükleme</div>
      
      <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
        <div id="hint">
          <div class="upload-icon">🍎</div>
          <div class="upload-text">Meyve veya Sebze Fotoğrafı Yükle</div>
          <div class="upload-hint">Tıklayın veya dosyayı sürükleyin</div>
        </div>
        <img id="preview" class="preview"/>
      </div>
      <input id="fileInput" type="file" accept="image/*" style="display:none" onchange="onFileChange(event)"/>

      <div class="controls">
        <div class="control-group">
          <label class="control-label">⚙️ Benzerlik Algılama Hassasiyeti</label>
          <input id="aggr" type="range" min="0.2" max="3.0" step="0.1" value="1.0" class="slider" oninput="document.getElementById('aggrVal').innerText=this.value"/>
          <div style="margin-top:8px">
            <span class="slider-value">Değer: <span id="aggrVal">1.0</span></span>
          </div>
        </div>
        <button class="btn" onclick="document.getElementById('fileInput').click()">
          🚀 Analizi Başlat
        </button>
      </div>

      <div id="statusBox" class="status-box">
        <span>✅</span>
        <span id="statusText">Sistem hazır - Görüntü yükleyebilirsiniz</span>
      </div>
    </div>

    <!-- Sağ Panel - Sonuçlar -->
    <div class="card">
      <div id="resultsContent">
        <div class="empty-state">
          <div class="empty-icon">🔍</div>
          <div class="empty-text">Henüz analiz yapılmadı</div>
          <div style="margin-top:10px;font-size:14px;color:#bbb">
            Sol panelden bir görüntü yükleyerek analizi başlatın
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div id="lb" onclick="this.style.display='none'">
  <img id="lbimg"/>
</div>

<script>
function onFileChange(e){
  const file = e.target.files[0];
  if(!file) return;
  
  const reader = new FileReader();
  const statusBox = document.getElementById('statusBox');
  const statusText = document.getElementById('statusText');
  
  statusBox.className = 'status-box analyzing';
  statusText.innerHTML = '<div class="spinner"></div> Görüntü analiz ediliyor...';
  
  reader.onload = function(ev){
    const preview = document.getElementById('preview');
    preview.src = ev.target.result;
    preview.style.display = 'block';
    document.getElementById('hint').style.display = 'none';
  };
  reader.readAsDataURL(file);

  const fd = new FormData();
  fd.append('image', file);
  fd.append('aggressiveness', document.getElementById('aggr').value);

  startMarkerPulse();

  fetch('/analyze', { method:'POST', body: fd })
    .then(r => r.json())
    .then(data => {
      stopMarkerPulse();
      statusBox.className = 'status-box complete';
      statusText.innerHTML = '✅ Analiz tamamlandı';
      
      if(data.error){ 
        statusBox.className = 'status-box error';
        statusText.innerHTML = '❌ Hata: ' + data.error;
        return; 
      }
      showResults(data);
    }).catch(err=>{
      stopMarkerPulse();
      statusBox.className = 'status-box error';
      statusText.innerHTML = '❌ Analiz sırasında hata oluştu';
      console.error(err);
    });
}

let pulseInterval = null;
function startMarkerPulse(){
  const marker = document.getElementById('phMarker');
  if(!marker) return;
  let dir = 1;
  let pos = 10;
  marker.style.left = pos + '%';
  pulseInterval = setInterval(()=>{
    pos += dir * 3;
    if(pos > 90) dir = -1;
    if(pos < 10) dir = 1;
    marker.style.left = pos + '%';
  }, 100);
}
function stopMarkerPulse(){ 
  if(pulseInterval){ 
    clearInterval(pulseInterval); 
    pulseInterval=null; 
  } 
}

function showResults(data){
  const info = data.info || {};
  
  // Ripeness badge
  const ripeness = data.ripeness || 'orta';
  const ripenessText = {
    'olgun': '🟢 Olgun',
    'orta': '🟡 Orta Olgunluk',
    'ham': '🔴 Ham'
  }[ripeness] || ripeness;
  
  // Meta badges
  const metaBadges = [];
  if(info.kalori) metaBadges.push(`🔥 ${info.kalori}`);
  if(info.protein) metaBadges.push(`💪 Protein: ${info.protein}`);
  if(info.karbonhidrat) metaBadges.push(`🌾 Karbonhidrat: ${info.karbonhidrat}`);
  if(info.yag) metaBadges.push(`🥑 Yağ: ${info.yag}`);
  if(info.lif) metaBadges.push(`🌿 Lif: ${info.lif}`);
  if(info.su) metaBadges.push(`💧 Su: ${info.su}`);
  
  const metaHTML = metaBadges.map(b => `<span class="meta-badge">${b}</span>`).join('');
  
  // Detail grid
  const details = [];
  if(info.vitamin) details.push({label: '🍊 Vitaminler', value: info.vitamin});
  if(info.mineraller) details.push({label: '⚡ Mineraller', value: info.mineraller});
  if(info.asit) details.push({label: '🧪 Asit Seviyesi', value: info.asit});
  if(info.baz) details.push({label: '🧪 Baz Seviyesi', value: info.baz});
  if(info.kullanim) details.push({label: '🍽️ Kullanım', value: info.kullanim});
  if(info.saglik) details.push({label: '💚 Sağlık Faydaları', value: info.saglik});
  
  const detailsHTML = details.length ? `
    <div class="detail-section">
      <div class="section-title">📋 Detaylı Bilgiler</div>
      <div class="detail-grid">
        ${details.map(d => `
          <div class="detail-item">
            <span class="detail-label">${d.label}</span>
            <span class="detail-value">${d.value}</span>
          </div>
        `).join('')}
      </div>
      ${info.aciklama ? `<p style="margin-top:15px;padding:12px;background:#fff;border-radius:8px;font-size:13px;color:#555;line-height:1.6">${info.aciklama}</p>` : ''}
    </div>
  ` : '';
  
  // Similarities
  const simHTML = (data.similarities || []).slice(0, 8).map(s => {
    const score = (s.score === null) ? '—' : (s.score * 100).toFixed(1) + '%';
    return `
      <div class="sim-card">
        <div class="sim-label">${s.label}</div>
        <div class="sim-score">${score}</div>
      </div>
    `;
  }).join('');
  
  // Examples
  const examplesHTML = (info.images && info.images.length) ? 
    info.images.slice(0, 12).map(u => 
      `<img src="${u}" class="example-img" onclick="showLightbox('${u}')"/>`
    ).join('') : '';
  
  const examplesSection = examplesHTML ? `
    <div class="examples-section">
      <div class="section-title">📸 Örnek Görseller</div>
      <div class="examples-grid">${examplesHTML}</div>
    </div>
  ` : '';
  
  // pH marker position
  const phPos = Math.max(0, Math.min(100, (data.ph / 14.0) * 100));
  
  document.getElementById('resultsContent').innerHTML = `
    <div class="result-header">
      <div class="result-main">
        <div class="top-match">${data.label}</div>
        <div class="ripeness-badge ${ripeness}">${ripenessText}</div>
        <div class="meta-info">${metaHTML}</div>
      </div>
      <div class="confidence-badge">Güven: ${data.confidence}%</div>
    </div>
    
    <div class="ph-section">
      <div class="ph-label">🧪 pH Seviyesi Analizi</div>
      <div class="ph-scale">
        <div class="ph-marker" id="phMarker" style="left:${phPos}%"></div>
      </div>
      <div class="ph-value">📊 pH Değeri: ${data.ph} / 14.0 (${getPhType(data.ph)})</div>
    </div>
    
    ${detailsHTML}
    
    <div class="similarity-section">
      <div class="section-title">📊 Benzerlik Skorları</div>
      <div class="sim-grid">${simHTML}</div>
    </div>
    
    ${examplesSection}
    
    <div class="info-footer">
      <span>💡</span>
      <span><strong>Bilgi:</strong> İlk analiz çağrısında dataset taranır. Büyük veri setlerinde ilk analiz biraz zaman alabilir.</span>
    </div>
  `;
}

function getPhType(ph){
  if(ph < 3) return 'Çok Asidik';
  if(ph < 5) return 'Asidik';
  if(ph < 6.5) return 'Hafif Asidik';
  if(ph < 7.5) return 'Nötr';
  if(ph < 9) return 'Hafif Bazik';
  if(ph < 11) return 'Bazik';
  return 'Çok Bazik';
}

function showLightbox(url){
  document.getElementById('lbimg').src = url;
  document.getElementById('lb').style.display = 'flex';
}

// Drag & Drop support
const uploadArea = document.getElementById('uploadArea');
uploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadArea.style.borderColor = '#667eea';
  uploadArea.style.transform = 'scale(1.02)';
});
uploadArea.addEventListener('dragleave', () => {
  uploadArea.style.borderColor = '#d0d0d0';
  uploadArea.style.transform = 'scale(1)';
});
uploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadArea.style.borderColor = '#d0d0d0';
  uploadArea.style.transform = 'scale(1)';
  const file = e.dataTransfer.files[0];
  if(file && file.type.startsWith('image/')){
    document.getElementById('fileInput').files = e.dataTransfer.files;
    onFileChange({target: {files: [file]}});
  }
});
</script>
</body>
</html>

'''

# -------------------- routes --------------------
from flask import render_template_string as _rts
@app.route('/')
def index():
    return _rts(HTML_TEMPLATE, training_dir=TRAINING_DIR)

@app.route('/analyze', methods=['POST'])
def analyze_route():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Görüntü bulunamadı'}), 400
        file = request.files['image']
        img = Image.open(file.stream).convert('RGB')
        img.thumbnail((400,400))
        arr = np.array(img, dtype=np.float32) / 255.0

        aggr_raw = request.form.get('aggressiveness', '1.0')
        try:
            aggressiveness = float(aggr_raw)
            aggressiveness = max(0.1, min(5.0, aggressiveness))
        except:
            aggressiveness = 1.0

        result = analyze_image(arr, aggressiveness=aggressiveness)
        return jsonify(result)
    except Exception as e:
        print("[ERROR] analyze:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/chemistry/<label>')
def chemistry(label):
    ensure_reference_features()
    key = None
    for k in REFERENCE_DB.keys():
        if k.lower() == label.lower():
            key = k
            break
    if key is None:
        return jsonify({'error':'Bilinmeyen label'}), 404
    out = REFERENCE_DB[key].copy()
    out['images'] = EXAMPLE_IMAGES.get(key, [])
    return jsonify(out)

# -------------------- run --------------------
if __name__ == '__main__':
    print("Starting local training-based analyzer...")
    if not os.path.isdir(TRAINING_DIR):
        print(f"[WARN] Training dir '{TRAINING_DIR}' does not exist. Create it and add folders.")
    app.run(debug=True, host='0.0.0.0', port=5000)
