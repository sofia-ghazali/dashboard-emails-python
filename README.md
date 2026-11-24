# 📊 Dashboard de Gestion & Analyse des E-mails (Python)

Application web interactive développée en Python (**Dash, Plotly, Pandas**) connectée à Gmail via les protocoles **IMAP** et **SMTP**.

## ✨ Fonctionnalités réalisées
* **Suivi en temps réel :** Compteurs d'e-mails entrants, sortants et volume total.
* **Analyse temporelle :** Graphique comparatif du trafic par jour ou par heure.
* **Classification automatique :** Catégorisation des messages (*Factures*, *Projets*, *Alertes*, *Autres*).
* **Consultation rapide :** Tableau des 5 derniers e-mails reçus avec filtre dynamique.
* **Messagerie intégrée :** Envoi d'e-mails directement depuis l'interface.

📄 *Voir le fichier `apercu-dashboard-emails-v2.pdf` pour les captures d'écran du résultat.*

## 🚀 Installation & Lancement
1. Installer les bibliothèques : `pip install dash plotly pandas`
2. Renseigner son adresse Gmail et son mot de passe d'application dans `dashboard-emails.py`
3. Lancer l'application : `python dashboard-emails.py`
4. Ouvrir `http://127.0.0` dans le navigateur.

