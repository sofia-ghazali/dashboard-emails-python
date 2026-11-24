import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import pandas as pd
import smtplib, imaplib, email
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parsedate_to_datetime

EMAIL_USER = "votre.email@gmail.com"
EMAIL_PASS = "votre_mot_de_passe_application"
SMTP_SERVER = "smtp.gmail.com"
IMAP_SERVER = "imap.gmail.com"

def decoder(txt):
    if not txt: return ""
    return "".join(c.decode(e or "utf-8", errors="ignore") if isinstance(c, bytes) else str(c) for c, e in decode_header(txt))

def charger_emails(limite=40):
    data = []
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        _, msgs = mail.search(None, "ALL")
        for eid in msgs[0].split()[-limite:]:
            _, msg_data = mail.fetch(eid, "(RFC822)")
            for part in msg_data:
                if isinstance(part, tuple):
                    msg = email.message_from_bytes(part[1])
                    suj, exp = decoder(msg["subject"]) or "(Sans sujet)", decoder(msg["from"]) or "Inconnu"
                    try: dt = parsedate_to_datetime(msg["date"])
                    except: dt = pd.Timestamp.now()
                    s = suj.lower()
                    cat = "Factures" if any(w in s for w in ["facture","paiement","reçu","commande"]) else \
                          "Projets" if any(w in s for w in ["projet","tp","cours","réunion","python"]) else \
                          "Alertes" if any(w in s for w in ["alerte","sécurité","urgent","code"]) else "Autres"
                    data.append({"Type": "Entrant", "Contact": exp, "Sujet": suj, "Date": dt.strftime("%Y-%m-%d"), "Heure": f"{dt.hour:02d}h", "Catégorie": cat})

        for d in ['"[Gmail]/Sent Mail"', '"[Gmail]/Messages envoy&AOk-s"', "Sent"]:
            status, _ = mail.select(d)
            if status == "OK":
                _, s_msgs = mail.search(None, "ALL")
                for sid in s_msgs[0].split()[-limite:]:
                    _, msg_data = mail.fetch(sid, "(RFC822)")
                    for part in msg_data:
                        if isinstance(part, tuple):
                            msg = email.message_from_bytes(part[1])
                            try: dt = parsedate_to_datetime(msg["date"])
                            except: dt = pd.Timestamp.now()
                            data.append({"Type": "Sortant", "Contact": decoder(msg["to"]), "Sujet": decoder(msg["subject"]), "Date": dt.strftime("%Y-%m-%d"), "Heure": f"{dt.hour:02d}h", "Catégorie": "Envoyé"})
                break
        mail.logout()
    except Exception as e:
        print("Erreur IMAP:", e)
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["Type", "Contact", "Sujet", "Date", "Heure", "Catégorie"])

app = dash.Dash(__name__)
card = {"backgroundColor": "white", "padding": "18px", "borderRadius": "10px", "boxShadow": "0 2px 5px rgba(0,0,0,0.08)"}
inp = {"width": "94%", "padding": "9px", "marginBottom": "10px", "borderRadius": "5px", "border": "1px solid #cbd5e1"}

app.layout = html.Div(style={"fontFamily": "Arial", "backgroundColor": "#f1f5f9", "padding": "20px"}, children=[
    html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "20px"}, children=[
        html.H1("📊 Dashboard Gestion & Analyse des E-mails", style={"margin": 0, "color": "#0f172a"}),
        html.Button("🔄 Actualiser", id="btn-refresh", n_clicks=0, style={"backgroundColor": "#2563eb", "color": "white", "border": "none", "padding": "10px 20px", "borderRadius": "6px", "cursor": "pointer"})
    ]),
    html.Div(id="kpis", style={"display": "flex", "gap": "20px", "marginBottom": "20px"}),
    html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "20px"}, children=[
        html.Div(style={**card, "flex": "2"}, children=[
            html.Div(style={"display": "flex", "justifyContent": "space-between"}, children=[
                html.H3("📈 Trafic (Entrants vs Sortants)", style={"margin": 0}),
                dcc.RadioItems(id="periode", options=[{"label": " Par Jour", "value": "Date"}, {"label": " Par Heure", "value": "Heure"}], value="Date", inline=True)
            ]),
            dcc.Graph(id="g-trafic")
        ]),
        html.Div(style={**card, "flex": "1"}, children=[html.H3("🗂️ Classification", style={"margin": 0}), dcc.Graph(id="g-cat")])
    ]),
    html.Div(style={"display": "flex", "gap": "20px"}, children=[
        html.Div(style={**card, "flex": "2"}, children=[
            html.Div(style={"display": "flex", "justifyContent": "space-between", "marginBottom": "10px"}, children=[
                html.H3("📩 Les 5 Derniers E-mails", style={"margin": 0}),
                dcc.Dropdown(id="filtre", options=[{"label": c, "value": c} for c in ["TOUT", "Factures", "Projets", "Alertes", "Autres"]], value="TOUT", clearable=False, style={"width": "180px"})
            ]),
            html.Div(id="table-5")
        ]),
        html.Div(style={**card, "flex": "1"}, children=[
            html.H3("📤 Envoyer un Message", style={"marginTop": 0}),
            dcc.Input(id="dest", type="email", placeholder="Destinataire", style=inp),
            dcc.Input(id="suj", type="text", placeholder="Sujet", style=inp),
            dcc.Textarea(id="corps", placeholder="Message...", style={**inp, "height": "80px"}),
            html.Button("Envoyer", id="btn-send", n_clicks=0, style={"backgroundColor": "#16a34a", "color": "white", "border": "none", "padding": "10px", "borderRadius": "6px", "width": "100%", "cursor": "pointer"}),
            html.Div(id="statut", style={"marginTop": "10px", "fontWeight": "bold"})
        ])
    ])
])

@app.callback([Output("kpis", "children"), Output("g-trafic", "figure"), Output("g-cat", "figure"), Output("table-5", "children")],
              [Input("btn-refresh", "n_clicks"), Input("periode", "value"), Input("filtre", "value")])
def update_ui(n, periode, cat):
    df = charger_emails()
    df_in = df[df["Type"] == "Entrant"]
    kpis = [
        html.Div(style={**card, "flex": "1", "textAlign": "center"}, children=[html.H4("📥 Entrants"), html.H2(len(df_in), style={"color": "#2563eb"})]),
        html.Div(style={**card, "flex": "1", "textAlign": "center"}, children=[html.H4("📤 Sortants"), html.H2(len(df[df["Type"] == "Sortant"]), style={"color": "#16a34a"})]),
        html.Div(style={**card, "flex": "1", "textAlign": "center"}, children=[html.H4("📊 Total"), html.H2(len(df), style={"color": "#6366f1"})])
    ]
    fig1 = px.bar(df.groupby([periode, "Type"]).size().reset_index(name="Nombre").sort_values(periode), x=periode, y="Nombre", color="Type", barmode="group", template="plotly_white") if not df.empty else px.bar()
    fig2 = px.pie(df_in.groupby("Catégorie").size().reset_index(name="Nombre"), names="Catégorie", values="Nombre", hole=0.4, template="plotly_white") if not df_in.empty else px.pie()
    df_tab = df_in if cat == "TOUT" else df_in[df_in["Catégorie"] == cat]
    last5 = df_tab.tail(5).iloc[::-1][["Date", "Heure", "Contact", "Sujet", "Catégorie"]]
    tab = dash_table.DataTable(data=last5.to_dict("records"), columns=[{"name": i, "id": i} for i in last5.columns], style_cell={"textAlign": "left", "padding": "8px", "fontSize": "12px"})
    return kpis, fig1, fig2, tab

@app.callback([Output("statut", "children"), Output("dest", "value"), Output("suj", "value"), Output("corps", "value")],
              Input("btn-send", "n_clicks"), [State("dest", "value"), State("suj", "value"), State("corps", "value")], prevent_initial_call=True)
def send_mail(n, dest, suj, corps):
    if not dest or not suj or not corps: return "⚠️ Remplissez tout.", dest, suj, corps
    try:
        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = EMAIL_USER, dest, suj
        msg.attach(MIMEText(corps, "plain"))
        with smtplib.SMTP(SMTP_SERVER, 587) as s:
            s.starttls(); s.login(EMAIL_USER, EMAIL_PASS); s.send_message(msg)
        return "✅ Envoyé !", "", "", ""
    except Exception as e:
        return f"❌ Erreur : {e}", dest, suj, corps

if __name__ == "__main__":
    app.run(debug=True)

