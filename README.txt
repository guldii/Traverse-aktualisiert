BERECHNUNG LOCHABSTÄNDE – U-STAHLTRAVERSE
==============================================

Dieses Paket enthält den Quellcode, Tests und den GitHub-Actions-Workflow für
eine portable Windows-EXE. Die fertige EXE läuft offline und benötigt auf dem
Ziel-PC kein installiertes Python.

Änderungen in dieser Version
-----------------------------
- Neuer Fenstertitel: „Berechnung Lochabstände  U-Stahltraverse“
- Kein Untertitel zur Offline-Funktion.
- Eingabefelder starten leer.
- Die Einheit „mm“ steht direkt hinter jedem Eingabefeld.
- Ergebnis zeigt immer 2 Befestigungslöcher.
- Zusätzlich wird „Anzahl Löcher (ohne Befestigungslöcher)“ angezeigt.
- Der frühere Hinweis im Ergebnis wurde entfernt.
- Technische Übersicht mit hervorgehobenen Angaben für Traverse, Anzahl Löcher
  und Abstand.
- Die beiden äußersten Befestigungslöcher werden rot dargestellt.
- Alle übrigen Löcher werden blau dargestellt.
- Modernisierte Oberfläche mit Karten, klarer Typografie und Hervorhebungen.
- PNG-Export wurde an die neue Darstellung angepasst.

Berechnung
----------
Nutzbare Strecke = Traversenlänge - Anfangsabstand - Endabstand.

Die Anzahl der Lochabstände ist ganzzahlig. Geprüft werden die untere und
obere ganze Zahl von nutzbare Strecke / Soll-Lochabstand. Gewählt wird der
Kandidat mit der kleinsten Abweichung vom Sollwert. Bei Gleichstand wird der
größere tatsächliche Abstand gewählt.

Gesamtanzahl Löcher = Anzahl Lochabstände + 1.
Die beiden äußersten Löcher gelten als Befestigungslöcher. Deshalb:
Anzahl Löcher ohne Befestigungslöcher = Gesamtanzahl Löcher - 2.

Alle Berechnungen erfolgen mit ungerundeten Werten. Erst bei der Anzeige werden
Maße auf 2 Nachkommastellen formatiert.

EXE über GitHub erstellen
-------------------------
1. Lade den gesamten Ordnerinhalt in dein GitHub-Repository hoch.
2. Wichtig: Der Ordner .github/workflows mit build-windows.yml muss enthalten sein.
3. GitHub Actions erstellt die Windows-EXE automatisch nach einem Push auf main.
4. Unter „Actions“ kann der Lauf kontrolliert werden.
5. Das Ergebnis heißt „TraverseLochabstand-Windows-x64“ und enthält
   TraverseLochabstand.exe.

Alternativ kann der Workflow unter Actions manuell gestartet werden.

Lokaler Build
-------------
Auf einem Windows-10/11-PC mit Python 3.10 oder neuer:
build_windows.bat

Die fertige Datei liegt danach unter:
dist\TraverseLochabstand.exe

Die Ziel-PCs benötigen für die fertige EXE kein Python und keine Internetverbindung.
