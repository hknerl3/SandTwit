from flask import Flask,render_template,request,redirect,url_for,session
from database import *
from uyarimesaj import UyariMesaj

app=Flask(__name__)
app.secret_key="aqun98ucc8y5d6gd#3"

@app.route("/")
def anasayfa():

    iletilersinifi = Database.startCon().classes.iletiler
    kullaniciSinifi = Database.startCon().classes.kullanici
    arkadaslarSinifi = Database.startCon().classes.arkadaslar

    if "id" in session:
        onerilenKullanicilar = Database.loadSession().query(kullaniciSinifi).filter(kullaniciSinifi.id!=session["id"]).all()
        takipEdilenListe = Database.loadSession().query(arkadaslarSinifi.takipedilenid).filter(arkadaslarSinifi.takipciid==session["id"]).all()
        sorguListe=[]
        for i in takipEdilenListe:
            sorguListe.append(i[0])
        sorguListe.append(session["id"])
        gelen = Database.loadSession().query(kullaniciSinifi,iletilersinifi).filter(kullaniciSinifi.id == iletilersinifi.iletikisiid, iletilersinifi.iletikisiid.in_(sorguListe)).order_by(iletilersinifi.id.desc()).all()
    else:
        gelen = Database.loadSession().query(kullaniciSinifi,iletilersinifi).filter(kullaniciSinifi.id == iletilersinifi.iletikisiid).order_by(iletilersinifi.id.desc()).all()
        onerilenKullanicilar = Database.loadSession().query(kullaniciSinifi).order_by(kullaniciSinifi.id.desc())

    return render_template("anasayfa.html",iletiler = gelen,kullanicilar = onerilenKullanicilar)

@app.route("/uyeol",methods=["POST","GET"])
def uyeol():
    
    mesaj=None
    if request.method=="POST":
        ad = request.form.get("inputad")
        soyad = request.form.get("inputsoyad")
        email = request.form.get("inputemail")
        sifre = request.form.get("inputsifre")
        sifretekrar = request.form.get("inputsifretekrar")
        if sifre == sifretekrar:
            KullaniciSinif = Database.startCon().classes.kullanici
            eklenecekKullanici = KullaniciSinif(ad=ad,soyad=soyad,eposta=email,sifre=sifre)
            sess = Database.loadSession()
            sess.add(eklenecekKullanici)
            try:
                sess.commit()
                mesaj=UyariMesaj(1,"Üyelik Başarılı")
            except :
                mesaj=UyariMesaj(2,"Üyelik Başarısız")
        else:
            mesaj=UyariMesaj(3,"Şifre ile Şifre tekrar birbiri ile uyuşmuyor !")

    return render_template("uyeol.html",sayfaMesaj=mesaj)

@app.route("/iletikaydet",methods=["POST"])
def iletikaydet():
    icerik = request.form.get("txt_ileti")
    IletilerSinifi = Database.startCon().classes.iletiler
    ileti = IletilerSinifi(iletikisiid=session["id"],iletiicerik=icerik)
    sess = Database.loadSession()
    sess.add(ileti)
    try:
        sess.commit()
    except:
        pass
    return redirect(url_for("anasayfa"))

@app.route("/profil/<id>")
def profil(id):

    iletilersinifi = Database.startCon().classes.iletiler
    gelen2 = Database.loadSession().query(iletilersinifi).filter(iletilersinifi.iletikisiid==id).all()
    KullaniciSinifi = Database.startCon().classes.kullanici
    gelen= Database.loadSession().query(KullaniciSinifi).filter(KullaniciSinifi.id==id).first()
    arkadaslarSinifi = Database.startCon().classes.arkadaslar
    arkadasmi=0
    if "id" in session:
        iliskiVarmi = Database.loadSession().query(arkadaslarSinifi).filter(arkadaslarSinifi.takipciid==session["id"],arkadaslarSinifi.takipedilenid == gelen.id).count()
        if iliskiVarmi>0:
            arkadasmi=1

    return render_template("profil.html",kisiBilgi = gelen,iletiler=gelen2,arkadasDurum=arkadasmi)

@app.route("/takipDurumlari",methods=["POST"])
def takipet():
    if request.method == "POST":
        takipci = session["id"]
        takipEdilecek = request.form.get("hidden_takipEdilecek")
        arkadaslarSinifi = Database.startCon().classes.arkadaslar
        arkadas = Database.loadSession().query(arkadaslarSinifi).filter(arkadaslarSinifi.takipciid==takipci,arkadaslarSinifi.takipedilenid == takipEdilecek).first()

        sess = Database.loadSession()
        if arkadas:
            sess.query(arkadaslarSinifi).filter(arkadaslarSinifi.arkadasid == arkadas.arkadasid).delete()
            sess.commit()
        else:
            arkadas =arkadaslarSinifi(takipciid=takipci,takipedilenid=takipEdilecek)
            sess.add(arkadas)

        sess.commit()
        return redirect(url_for("profil",id=takipEdilecek))

@app.route("/girisyap",methods=["POST","GET"])
def girisyap():
    mesaj=None
    if request.method=="POST":
        email = request.form.get("inputemail")
        sifre = request.form.get("inputsifre")
        KullaniciSinifi = Database.startCon().classes.kullanici
        gelen = Database.loadSession().query(KullaniciSinifi).filter(KullaniciSinifi.eposta==email,KullaniciSinifi.sifre==sifre).first()
        if gelen:
            session['adsoyad'] = gelen.ad+" "+gelen.soyad
            session['eposta'] =gelen.eposta
            session["id"] = gelen.id
                
            return redirect(url_for("profil",id=gelen.id))
        else:
            mesaj = UyariMesaj(2,"Kullanıcı adı veya Şifre Yanlış")

    return render_template("girisyap.html",sayfaMesaj=mesaj)

@app.route("/cikisyap")
def cikisyap():
    session.clear()
    return redirect(url_for("anasayfa"))

@app.route("/404error")
def error404():
    return render_template("error404.html")

if __name__ == "__main__":
    app.run(debug=True)
