import requests
import yaml


# =============================================================================
#  KVK – Automatikus lead-értékelő ügynök (agentic flow)
# -----------------------------------------------------------------------------
#  Mit csinál a script? Végigmegy a Typeform-on beérkezett érdeklődőkön,
#  mindegyiket kiértékeli egy AI-modellel, javaslatot ír az értékesítésnek,
#  majd az eredményt kiküldi a csapat Telegram-csoportjába.
#
#  Az AGENTIC FLOW 4 lépésben (a folyamat "gerince"):
#     STEP 1  →  Adatgyűjtés:   leadek behúzása a Typeform-ból
#     STEP 2  →  Gondolkodás:   minden lead pontozása AI-jal (0-100)
#     STEP 2b →  Gondolkodás:   értékesítési kulcsmondat írása AI-jal
#     STEP 3  →  Cselekvés:     eredmény kiküldése Telegram-ra
# =============================================================================


# === API KULCS (sajátot adj meg a config.yaml-ben!) =========================
# Az összes titkos kulcsot a config.yaml-ből olvassuk be, hogy ne kerüljön
# bele a kódba. Itt kapcsolódunk a 3 külső szolgáltatáshoz: OpenAI, Typeform,
# Telegram.
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

open_ai_api_key = config["open_ai_api_key"]
typeform_api_key = config["typeform_api_key"]
typeform_form_id = "AKEYp0Gi"
telegram_bot_token = config["telegram_bot_token"]
telegram_chat_id = config["telegram_chat_id"]


# #############################################################################
# ==== STEP 1: LEADEK BEHÚZÁSA A TYPEFORM-BÓL (adatgyűjtés) ===================
# #############################################################################
# Az ügynök első dolga: megszerezni a "nyersanyagot". Lekérdezzük a Typeform
# form összes beérkezett válaszát, ezekből lesznek a leadek, amiket értékelünk.
url = f"https://api.typeform.com/forms/{typeform_form_id}/responses"

response = requests.get(
    url,
    headers={"Authorization": "Bearer " + typeform_api_key},
    params={"page_size": 1000},
)

def answer_value(answer):
    """Egy Typeform válasz értékének kinyerése a típusától függetlenül."""
    answer_type = answer["type"]
    if answer_type == "choice":
        return answer["choice"].get("label", "")
    if answer_type == "choices":
        return ", ".join(answer["choices"].get("labels", []))
    return answer.get(answer_type, "")


# A form 5 mezője a Google Sheet 2-6. oszlopának felel meg:
# ceg_nev, iparag, bejovo_uzenet, tavalyi_arbevetel, tavalyi_profit
# A lead_id nincs a formban, ezért a Typeform válasz azonosítóját használjuk.
# Végeredmény: a `rows` lista, ahol minden sor egy lead adatait tartalmazza.
rows = []
for item in response.json()["items"]:
    row = [item["token"]] + [answer_value(a) for a in item["answers"]]
    rows.append(row)


# #############################################################################
# ==== FŐ CIKLUS: minden lead végigfut a teljes agentic flow-n ===============
# #############################################################################
# Innentől soronként (lead-enként) dolgozunk. Minden egyes leadre lefut a
# teljes gondolkodás → cselekvés lánc (STEP 2 → 2b → 3).
for row in rows:

    # -------------------------------------------------------------------------
    # ==== STEP 2: LEAD PONTOZÁSA AI-JAL (gondolkodás #1) =====================
    # -------------------------------------------------------------------------
    # Összeállítjuk a "promptot" (az utasítást az AI-nak), amiben pontos
    # szempontrendszert adunk: mitől jó és mitől gyenge egy lead. A modell
    # ez alapján ad egy 0-100 pontszámot + rövid indoklást.
    prompt = f"""Értékeld a leadet 0-100 pont között.
A jó lead jellemzői:
* konkrét digitális marketing problémát ír le
* van üzleti célja: több lead, több webshop rendelés, jobb ROAS, jobb mérés, automatizált riport
* van sürgősség vagy döntési helyzet
* van pénzügyi kapacitásra utaló jel: árbevétel/profit/büdzsé/növekedés
* nem csak "érdeklődöm", hanem konkrét következő lépést kér
* digitális marketing ügynökség számára releváns szolgáltatást keres
* akkor is lehet jó lead, ha EV vagy kisebb cég, amennyiben konkrét és fizetőképes igénye van
A gyenge lead jellemzői:
* nincs konkrét probléma
* nincs büdzsé vagy nagyon kicsi a cég
* csak általános érdeklődés
* nem releváns szolgáltatást kér
* nem döntéshozó vagy nem derül ki a szándék
* a pénzügyi adatok hiányosak vagy bizonytalanok, és az üzenetből sem derül ki erős üzleti potenciál
* az üzenet nagyon igénytelen, zavaros vagy nehezen érthető, és emiatt nem látszik tisztán a valódi igény
Fontos:
* a cégnév anonimizált, abból ne következtess valódi cégméretre vagy minőségre
* az üzenet minősége fontos szempont legyen: a rossz helyesírás rossz leadre utal
* ha az árbevétel vagy profit mező üres, "nem tudom" vagy "ez az első évem", akkor a bejövő üzenet alapján próbáld megítélni az üzleti potenciált

Lead adatok:
- Iparág: {row[2]}
- Üzenet: {row[3]}
- Tavalyi árbevétel: {row[4]}
- Tavalyi profit: {row[5]}

Válaszolj csak így: PONTSZÁM: [szám] | INDOKLÁS: [1-2 mondat]"""

    # Elküldjük a promptot az OpenAI modellnek, és kiolvassuk a válasz szövegét.
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": "Bearer " + open_ai_api_key},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    evaluation = response.json()["choices"][0]["message"]["content"]

    # -------------------------------------------------------------------------
    # ==== STEP 2b: ÉRTÉKESÍTÉSI KULCSMONDAT AI-JAL (gondolkodás #2) ==========
    # -------------------------------------------------------------------------
    # Egy MÁSODIK AI-hívás, ami az előző lépés eredményére (`evaluation`) épít:
    # a pontozás ismeretében megfogalmaz egy telefonos értékesítési
    # kulcsmondatot, ami épp erre a leadre van szabva.
    # (Ez a lépcsőzetes láncolás – az egyik AI kimenete a másik bemenete –
    #  az agentic flow lényege.)
    pitch_prompt = f"""Értékesítési szakértő vagy egy digitális marketing ügynökségnél.
A lenti adatok és a lead értékelése alapján fogalmazd meg a LEGFŐBB értékesítési kulcsmondatot,
amit telefonon mondhatunk ennek az érdeklődőnek, hogy ügyfél legyen.
Ez az a mondat, ami a leginkább megszólítja az ő konkrét problémáját/üzleti célját.

Lead adatok:
- Iparág: {row[2]}
- Üzenet: {row[3]}
- Tavalyi árbevétel: {row[4]}
- Tavalyi profit: {row[5]}

A lead értékelése: {evaluation}

Válaszolj csak így: KULCSMONDAT: [1 rövid, telefonon kimondható mondat] | MIÉRT: [1 rövid mondat, miért ez hat rá]"""

    # Második AI-hívás a kulcsmondatért.
    pitch_response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": "Bearer " + open_ai_api_key},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": pitch_prompt}]
        }
    )

    pitch = pitch_response.json()["choices"][0]["message"]["content"]

    # Összefűzzük az egy leadhez tartozó teljes üzenetet: azonosító +
    # értékelés + értékesítési vázlat. (A print csak arra való, hogy a
    # terminálban is lássuk, mi történik.)
    message = f"{row[0]}: {evaluation}\n\nÉRTÉKESÍTÉSI VÁZLAT:\n{pitch}"
    print(message)

    # -------------------------------------------------------------------------
    # ==== STEP 3: EREDMÉNY KIKÜLDÉSE TELEGRAM-RA (cselekvés) =================
    # -------------------------------------------------------------------------
    # Az ügynök utolsó lépése: a kész értékelést és értékesítési vázlatot
    # elküldi a csapat Telegram-csoportjába, ahol az értékesítők rögtön látják.
    requests.post(
        f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
        json={"chat_id": telegram_chat_id, "text": message},
    )
