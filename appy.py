from flask import Flask, render_template, request, jsonify, session
import sqlite3
import hashlib
import json
import urllib.request
import urllib.error
from datetime import datetime

app = Flask(__name__)
app.secret_key = "byMIRZA_gizli_anahtar_2024"

DENEME_HAKKI = 3
MODEL = "llama3.2"
DB_DOSYA = "byMIRZA_kullaniciler.db"

SISTEM_MESAJI = """Sen byMIRZA adında bir Türk yapay zeka asistansın.
KURAL 1: Yalnızca ve yalnızca Türkçe konuş. Hiçbir zaman İngilizce veya başka bir dil kullanma.
KURAL 2: Kısa, net ve yardımsever cevaplar ver.
KURAL 3: Eğer sana İngilizce sorulsa bile Türkçe cevap ver.
KURAL 4: Selamlama, vedalaşma, her şeyi Türkçe yap."""

def db_baslat():
    conn = sqlite3.connect(DB_DOSYA)
    conn.execute("""CREATE TABLE IF NOT EXISTS kullanicilar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_adi TEXT UNIQUE NOT NULL,
        sifre TEXT NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS sohbetler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_adi TEXT NOT NULL,
        baslik TEXT NOT NULL,
        olusturma_tarihi TEXT NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS mesajlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sohbet_id INTEGER NOT NULL,
        rol TEXT NOT NULL,
        icerik TEXT NOT NULL,
        FOREIGN KEY (sohbet_id) REFERENCES sohbetler(id)
    )""")
    conn.commit()
    conn.close()

def sifre_hashle(s):
    return hashlib.sha256(s.encode()).hexdigest()

@app.route("/api/kayit", methods=["POST"])
def kayit():
    d = request.json
    k, s = d.get("kullanici_adi","").strip(), d.get("sifre","").strip()
    if not k or not s:
        return jsonify({"ok": False, "mesaj": "Tüm alanları doldurun."})
    try:
        conn = sqlite3.connect(DB_DOSYA)
        conn.execute("INSERT INTO kullanicilar (kullanici_adi, sifre) VALUES (?,?)", (k, sifre_hashle(s)))
        conn.commit(); conn.close()
        session["kullanici"] = k
        return jsonify({"ok": True, "kullanici": k})
    except sqlite3.IntegrityError:
        return jsonify({"ok": False, "mesaj": "Bu kullanıcı adı alınmış."})

@app.route("/api/giris", methods=["POST"])
def giris():
    d = request.json
    k, s = d.get("kullanici_adi","").strip(), d.get("sifre","").strip()
    conn = sqlite3.connect(DB_DOSYA)
    cur = conn.execute("SELECT kullanici_adi FROM kullanicilar WHERE kullanici_adi=? AND sifre=?", (k, sifre_hashle(s)))
    sonuc = cur.fetchone(); conn.close()
    if sonuc:
        session["kullanici"] = k
        return jsonify({"ok": True, "kullanici": k})
    return jsonify({"ok": False, "mesaj": "Kullanıcı adı veya şifre hatalı."})

@app.route("/api/cikis", methods=["POST"])
def cikis():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/sohbetler", methods=["GET"])
def sohbetler():
    k = session.get("kullanici")
    if not k:
        return jsonify([])
    conn = sqlite3.connect(DB_DOSYA)
    cur = conn.execute("SELECT id, baslik, olusturma_tarihi FROM sohbetler WHERE kullanici_adi=? ORDER BY id DESC", (k,))
    sonuc = [{"id": r[0], "baslik": r[1], "tarih": r[2]} for r in cur.fetchall()]
    conn.close()
    return jsonify(sonuc)

@app.route("/api/sohbet/<int:sid>", methods=["GET"])
def sohbet_getir(sid):
    conn = sqlite3.connect(DB_DOSYA)
    cur = conn.execute("SELECT rol, icerik FROM mesajlar WHERE sohbet_id=? ORDER BY id", (sid,))
    mesajlar = [{"rol": r[0], "icerik": r[1]} for r in cur.fetchall()]
    conn.close()
    return jsonify(mesajlar)

@app.route("/api/sohbet/<int:sid>", methods=["DELETE"])
def sohbet_sil(sid):
    conn = sqlite3.connect(DB_DOSYA)
    conn.execute("DELETE FROM mesajlar WHERE sohbet_id=?", (sid,))
    conn.execute("DELETE FROM sohbetler WHERE id=?", (sid,))
    conn.commit(); conn.close()
    return jsonify({"ok": True})

@app.route("/api/mesaj", methods=["POST"])
def mesaj_gonder():
    d = request.json
    metin = d.get("metin", "").strip()
    gecmis = d.get("gecmis", [])
    sohbet_id = d.get("sohbet_id")
    kullanici = session.get("kullanici")

    if not metin:
        return jsonify({"ok": False, "mesaj": "Boş mesaj."})

    if kullanici and not sohbet_id:
        baslik = metin[:50]
        conn = sqlite3.connect(DB_DOSYA)
        cur = conn.execute("INSERT INTO sohbetler (kullanici_adi, baslik, olusturma_tarihi) VALUES (?,?,?)",
            (kullanici, baslik, datetime.now().strftime("%Y-%m-%d %H:%M")))
        sohbet_id = cur.lastrowid
        conn.commit(); conn.close()

    if sohbet_id:
        conn = sqlite3.connect(DB_DOSYA)
        conn.execute("INSERT INTO mesajlar (sohbet_id, rol, icerik) VALUES (?,?,?)", (sohbet_id, "user", metin))
        conn.commit(); conn.close()

    try:
        veri = json.dumps({
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SISTEM_MESAJI}
            ] + gecmis + [{"role": "user", "content": metin}],
            "stream": False
        }).encode("utf-8")
        req = urllib.request.Request("http://localhost:11434/api/chat",
            data=veri, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=60) as r:
            sonuc = json.loads(r.read().decode("utf-8"))
            cevap = sonuc["message"]["content"]

        if sohbet_id:
            conn = sqlite3.connect(DB_DOSYA)
            conn.execute("INSERT INTO mesajlar (sohbet_id, rol, icerik) VALUES (?,?,?)", (sohbet_id, "assistant", cevap))
            conn.commit(); conn.close()

        return jsonify({"ok": True, "cevap": cevap, "sohbet_id": sohbet_id})

    except Exception as e:
        return jsonify({"ok": False, "mesaj": f"Ollama bağlantı hatası: {e}"})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    db_baslat()
    app.run(host="0.0.0.0", port=5000, debug=False)
#son hal telefon
