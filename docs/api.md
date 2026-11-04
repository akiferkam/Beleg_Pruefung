# HTTP-API

`api/app.py` stellt eine Flask-API bereit. Der direkte Programmeinstieg startet sie auf `127.0.0.1:5050`, mit `debug=False` und mehreren Request-Threads. Die HTML-Oberfläche gehört zum separaten `web/`-Projekt.

## Endpunkte

| Methode und Pfad | Eingabe | Wirkung |
|---|---|---|
| `GET /` | keine | Service-Status als JSON |
| `POST /api/analyze` | JSON: `folder`, `policy`, beide optional | Pipeline ohne persistente Ledger-Schreibung; Cache-Schreibung möglich |
| `POST /api/commit` | wie Analyze | Pipeline mit Ledger-Schreibung, Berichten und Extraktionskopien |
| `POST /api/upload` | Multipart-Feld `files`, mehrfach | Dateien in einen neuen Batch-Ordner schreiben |
| `POST /api/override` | JSON mit Dokument-ID und Entscheidung | Manuellen Override sofort speichern |
| `GET /doc?path=...` | Dateipfad | Originaldatei ausliefern |
| `GET /thumb?path=...` | Dateipfad | PNG-Vorschaubild liefern beziehungsweise erzeugen |

## Analyse-Beispiel

```json
{
  "folder": "C:/Users/akife/Desktop/beleg_pruefer_akif/belege",
  "policy": {
    "extra_items_tolerance_pct": 10,
    "mandatory_review_amount_eur": 50000,
    "no_po_match_means_hinschauen": true,
    "line_arithmetic_tolerance_per_unit_eur": 0.005
  }
}
```

Ohne Ordner wird `belege/` im Projektstamm verwendet. Die Bestell-CSV wird zuerst im gewählten Eingabeordner gesucht, danach über den konfigurierten Projektpfad. Ein nicht vorhandener Ordner liefert HTTP 400.

`apply_overrides` erlaubt nur die vier oben genannten Policy-Felder. Die drei Zahlenwerte werden mit `float` konvertiert; der Bestellbezug mit `bool`. Clients müssen dafür echte JSON-Booleans senden: Ein String wie `"false"` wäre in Python wahr. Eine umfassende Wertebereichsvalidierung ist nicht vorhanden.

Die Overrides gelten nur für diesen Lauf. Ein Endpunkt zum Speichern dieser Policy in `config.yaml` existiert im untersuchten Stand nicht.

## Antwortformat

```json
{
  "docs": [],
  "summary": {"freigeben": 0, "hinschauen": 0, "gesamt": 0},
  "committed": false,
  "policy_used": {}
}
```

Dies ist ein Formbeispiel mit leerer Dokumentliste. Tatsächliche Dokumentobjekte enthalten `doc_id`, `datei`, `pfad`, `entscheidung`, `endstatus`, `manuell`, Lieferanten- und Rechnungsfelder, Beträge, Positionen, `gruende`, `info_notes` und `fehler`. Befunde werden als `{ "id": "A1", "nachricht": "..." }` übertragen. Die Liste wird nach Dokument-ID sortiert, unabhängig von der internen Prüfungsreihenfolge.

`summary` zählt die nach manuellen Overrides wirksamen Endstatus. `policy_used` enthält die tatsächlich verwendete Policy inklusive weiterer konfigurierter Werte.

## Upload

Uploads werden unter `api/uploads/<Zeitstempel>-<Zufall>/` gespeichert. Der Server übernimmt den Basisdateinamen und gibt `folder` sowie `dateien` zurück. Der Client muss den zurückgegebenen Ordner für die folgende Analyse und den Commit verwenden.

Ein Request ohne Dateien liefert HTTP 400. Die Upload-Funktion besitzt keine eigene Liste zulässiger Dateiendungen und keine konfigurierte Größenobergrenze. Die spätere Aufnahme bewertet nicht unterstützte Formate.

## Manuelle Entscheidung

```json
{
  "doc_id": "beispielrechnung",
  "decision": "freigeben",
  "note": "Original geprüft",
  "original_decision": "hinschauen"
}
```

Ohne Dokument-ID oder mit einer anderen Entscheidung als `freigeben`/`hinschauen` folgt HTTP 400. Der Server prüft hier nicht, ob die Dokument-ID tatsächlich Teil eines zuvor analysierten Laufs war.

## Dateiabruf und Betriebsgrenzen

`/doc` und `/thumb` erlauben PDF, JPG/JPEG, PNG, TIF/TIFF und WEBP. Eine fehlende Datei führt zu 404, eine andere Endung zu 403. Der Dateipfad wird auf Existenz und Endung geprüft, jedoch nicht auf Zugehörigkeit zu einem bestimmten Projektordner beschränkt.

CORS ist für `/api/*` auf lokale HTTP-Ursprünge mit Port beschränkt. Authentifizierung und Nutzerrollen sind nicht implementiert. Die lokale Bindung gehört zum vorgesehenen Betriebsmodell. Da Ledger und Overrides ohne Sperren als JSON geschrieben werden, sind konkurrierende schreibende Requests nicht transaktional abgesichert.

## Quellen

`api/app.py`, `scripts/pipeline.py`, `scripts/overrides.py`, `scripts/thumbnails.py`, `web/src/lib/api/rest.ts`.

[Zur Übersicht](overview.md) · [Web-Oberfläche](frontend.md)
