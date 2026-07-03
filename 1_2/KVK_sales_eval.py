import requests
import yaml


# === API KULCS (sajátot adj meg a config.yaml-ben!) ===
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

open_ai_api_key = config["open_ai_api_key"]
typeform_api_key = config["typeform_api_key"]
typeform_form_id = "AKEYp0Gi"
telegram_bot_token = config["telegram_bot_token"]
telegram_chat_id = config["telegram_chat_id"]

# === Minden sor automatikus kiértékelése a táblában ===
# --- STEP 1: Get leads from Typeform ---
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
rows = []
for item in response.json()["items"]:
    row = [item["token"]] + [answer_value(a) for a in item["answers"]]
    rows.append(row)

# --- STEP 2: Evaluate each lead ---
for row in rows:
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

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": "Bearer " + open_ai_api_key},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    evaluation = response.json()["choices"][0]["message"]["content"]
    message = f"{row[0]}: {evaluation}"
    print(message)

    # --- STEP 3: Send the evaluation to the Telegram group ---
    requests.post(
        f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
        json={"chat_id": telegram_chat_id, "text": message},
    )
