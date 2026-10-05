# -*- coding: utf-8 -*-
"""Offline-Rechner für Lochabstände an U-Stahltraversen."""
import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import dataclass

APP_TITLE = "Berechnung Lochabstände  U-Stahltraverse"

# Modernes, zurückhaltendes Farbschema
NAVY = "#17324D"
BLUE = "#1976D2"
BLUE_DARK = "#125AA0"
RED = "#D83A3A"
RED_DARK = "#A92424"
BG = "#F4F7FA"
CARD = "#FFFFFF"
TEXT = "#17212B"
MUTED = "#64748B"
BORDER = "#D7E0E8"
TRAVERSE_FILL = "#E8EEF3"


@dataclass
class Result:
    length: float
    start: float
    end: float
    target: float
    usable: float
    intervals: int
    holes: int
    spacing: float
    deviation: float
    rounding: str

    @property
    def fastening_holes(self) -> int:
        """Die beiden äussersten Löcher sind die Befestigungslöcher."""
        return 2

    @property
    def holes_without_fastening(self) -> int:
        return max(0, self.holes - self.fastening_holes)


def calculate(length: float, start: float, end: float, target: float) -> Result:
    """Berechnet mit ungerundeten Werten; gerundet wird erst bei der Anzeige."""
    vals = (length, start, end, target)
    if not all(math.isfinite(v) for v in vals):
        raise ValueError("Bitte nur gültige Zahlen eingeben.")
    if length <= 0:
        raise ValueError("Die Traversenlänge muss grösser als 0 sein.")
    if start < 0 or end < 0:
        raise ValueError("Anfangs- und Endabstand dürfen nicht negativ sein.")
    if target <= 0:
        raise ValueError("Der Soll-Lochabstand muss grösser als 0 sein.")
    usable = length - start - end
    if usable <= 0:
        raise ValueError("Anfangs- und Endabstand müssen zusammen kleiner als die Traversenlänge sein.")

    ratio = usable / target
    lower = max(1, math.floor(ratio))
    upper = max(1, math.ceil(ratio))
    candidates = sorted(set((lower, upper)))

    # Kleinste Abweichung vom Sollwert; bei Gleichstand grösserer Ist-Abstand.
    scored = [(abs((usable / n) - target), -(usable / n), n) for n in candidates]
    deviation, _neg_spacing, intervals = min(scored)
    spacing = usable / intervals

    if intervals == lower and intervals == upper:
        rounding = "Exakt passend"
    elif intervals < ratio:
        rounding = "Abgerundet (weniger Lochabstände)"
    elif intervals > ratio:
        rounding = "Aufgerundet (mehr Lochabstände)"
    else:
        rounding = "Exakt passend"

    return Result(
        length, start, end, target, usable, intervals,
        intervals + 1, spacing, abs(spacing - target), rounding
    )


def fmt(value: float) -> str:
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1180x800")
        self.minsize(900, 680)
        self.configure(bg=BG)
        self.result = None
        self._build_ui()
        self.bind("<Return>", lambda _event: self.do_calculate())

    def _build_ui(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", font=("Segoe UI", 10), foreground=TEXT)
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("Title.TLabel", background=BG, foreground=NAVY,
                        font=("Segoe UI", 21, "bold"))
        style.configure("Subtitle.TLabel", background=BG, foreground=MUTED,
                        font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=CARD, foreground=NAVY,
                        font=("Segoe UI", 11, "bold"))
        style.configure("Input.TLabel", background=CARD, foreground=TEXT,
                        font=("Segoe UI", 10))
        style.configure("Unit.TLabel", background=CARD, foreground=MUTED,
                        font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", padding=(9, 7), fieldbackground="white")
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"),
                        padding=(12, 9), foreground="white", background=BLUE)
        style.map("Primary.TButton", background=[("active", BLUE_DARK), ("pressed", BLUE_DARK)])
        style.configure("Secondary.TButton", font=("Segoe UI", 10),
                        padding=(12, 8), foreground=TEXT, background="#E9EEF3")
        style.map("Secondary.TButton", background=[("active", "#DCE5EC")])

        outer = ttk.Frame(self, padding=(22, 18, 22, 18))
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, 15))
        ttk.Label(header, text=APP_TITLE, style="Title.TLabel").pack(anchor="w")

        main = ttk.Panedwindow(outer, orient="horizontal")
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main, padding=(0, 0, 12, 0))
        right = ttk.Frame(main)
        main.add(left, weight=1)
        main.add(right, weight=3)

        # Eingabekarte
        inputs = ttk.Frame(left, style="Card.TFrame", padding=16)
        inputs.pack(fill="x")
        ttk.Label(inputs, text="Eingaben", style="Section.TLabel").pack(anchor="w", pady=(0, 12))

        self.entries = {}
        fields = [
            ("length", "Traversenlänge"),
            ("start", "Anfangsabstand"),
            ("end", "Endabstand"),
            ("target", "Soll-Lochabstand"),
        ]
        for key, label in fields:
            row = ttk.Frame(inputs, style="Card.TFrame")
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=label, style="Input.TLabel").pack(side="left", fill="x", expand=True)
            entry = ttk.Entry(row, width=12, justify="right")
            entry.pack(side="left")
            ttk.Label(row, text="mm", style="Unit.TLabel", width=4, anchor="w").pack(side="left", padx=(7, 0))
            self.entries[key] = entry

        actions = ttk.Frame(left, style="Card.TFrame", padding=(16, 4, 16, 14))
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Berechnen", style="Primary.TButton",
                   command=self.do_calculate).pack(fill="x", pady=(0, 6))
        ttk.Button(actions, text="Zurücksetzen", style="Secondary.TButton",
                   command=self.reset).pack(fill="x", pady=3)
        ttk.Button(actions, text="Ergebnisse kopieren", style="Secondary.TButton",
                   command=self.copy_results).pack(fill="x", pady=3)
        ttk.Button(actions, text="Zeichnung als PNG speichern", style="Secondary.TButton",
                   command=self.save_png).pack(fill="x", pady=3)

        # Ergebniskarte
        resbox = ttk.Frame(left, style="Card.TFrame", padding=16)
        resbox.pack(fill="both", expand=True, pady=(10, 0))
        ttk.Label(resbox, text="Ergebnis", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        self.result_text = tk.Text(
            resbox, height=15, width=36, wrap="word",
            font=("Segoe UI", 10), relief="flat", bd=0,
            bg=CARD, fg=TEXT, insertbackground=TEXT,
            padx=2, pady=4
        )
        self.result_text.pack(fill="both", expand=True)
        self.result_text.insert("1.0", "Noch keine Berechnung durchgeführt.")
        self.result_text.configure(state="disabled")

        # Rechte Seite: hervorgehobene Kennzahlen
        overview = ttk.Frame(right, style="Card.TFrame", padding=(16, 14, 16, 14))
        overview.pack(fill="x", pady=(0, 10))

        cards = ttk.Frame(overview, style="Card.TFrame")
        cards.pack(fill="x")
        self.card_values = {}
        for i, (key, label) in enumerate([
            ("length", "TRAVERSE"),
            ("holes", "ANZAHL BEFESTIGUNGSLÖCHER"),
            ("spacing", "ABSTAND"),
        ]):
            cards.columnconfigure(i, weight=1)
            card = tk.Frame(cards, bg="#F8FAFC", highlightthickness=1,
                            highlightbackground=BORDER, bd=0)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 5, 5 if i < 2 else 0))
            tk.Label(card, text=label, bg="#F8FAFC", fg=MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(10, 1))
            value = tk.Label(card, text="—", bg="#F8FAFC", fg=NAVY,
                             font=("Segoe UI", 16, "bold"))
            value.pack(anchor="w", padx=12, pady=(0, 10))
            self.card_values[key] = value

        drawbox = ttk.Frame(right, style="Card.TFrame", padding=10)
        drawbox.pack(fill="both", expand=True)

        title_row = ttk.Frame(drawbox, style="Card.TFrame")
        title_row.pack(fill="x", padx=5, pady=(2, 6))
        ttk.Label(title_row, text="Technische Zeichnung",
                  style="Section.TLabel").pack(side="left")

        self.canvas = tk.Canvas(
            drawbox, background="white", highlightthickness=1,
            highlightbackground=BORDER
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _e: self.draw())
        self.canvas.create_text(
            20, 25, anchor="nw",
            text="Nach der Berechnung wird hier die technische Zeichnung der Traverse angezeigt.",
            fill=MUTED, font=("Segoe UI", 10)
        )

    def read_number(self, key):
        raw = self.entries[key].get().strip().replace(" ", "").replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            labels = {
                "length": "Traversenlänge",
                "start": "Anfangsabstand",
                "end": "Endabstand",
                "target": "Soll-Lochabstand"
            }
            raise ValueError(f"Bitte für „{labels[key]}“ eine gültige Zahl eingeben.")

    def do_calculate(self):
        try:
            values = {k: self.read_number(k) for k in self.entries}
            self.result = calculate(
                values["length"], values["start"],
                values["end"], values["target"]
            )
        except ValueError as exc:
            messagebox.showerror("Eingabe prüfen", str(exc), parent=self)
            return

        r = self.result
        lines = [
            ("Nutzbare Strecke", f"{fmt(r.usable)} mm"),
            ("Lochabstände", f"{r.intervals}"),
            ("Befestigungslöcher", "2"),
            ("Löcher ohne Befestigung", f"{r.holes_without_fastening}"),
            ("Tatsächlicher Abstand", f"{fmt(r.spacing)} mm"),
            ("Abweichung zum Soll", f"{fmt(r.deviation)} mm"),
            ("Auswahl", r.rounding),
        ]
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        for label, value in lines:
            self.result_text.insert("end", f"{label:<26}")
            self.result_text.insert("end", f"{value:>18}\n")
        self.result_text.configure(state="disabled")

        self.card_values["length"].configure(text=f"{fmt(r.length)} mm")
        self.card_values["holes"].configure(text=f"{r.holes_without_fastening}")
        self.card_values["spacing"].configure(text=f"{fmt(r.spacing)} mm")
        self.draw()

    def reset(self):
        for entry in self.entries.values():
            entry.delete(0, "end")
        self.result = None

        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "Noch keine Berechnung durchgeführt.")
        self.result_text.configure(state="disabled")

        for value in self.card_values.values():
            value.configure(text="—")
        self.canvas.delete("all")
        self.canvas.create_text(
            20, 25, anchor="nw",
            text="Nach der Berechnung wird hier die technische Zeichnung der Traverse angezeigt.",
            fill=MUTED, font=("Segoe UI", 10)
        )

    def copy_results(self):
        if not self.result:
            messagebox.showinfo("Keine Ergebnisse", "Bitte zuerst eine Berechnung durchführen.", parent=self)
            return
        text = self.result_text.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        messagebox.showinfo("Kopiert", "Die Ergebnisse wurden in die Zwischenablage kopiert.", parent=self)

    def draw(self):
        c = self.canvas
        c.delete("all")
        r = self.result
        w, h = max(c.winfo_width(), 400), max(c.winfo_height(), 300)

        if not r:
            c.create_text(
                w / 2, h / 2, anchor="center",
                text="Noch keine Berechnung\n\nGib links die Masse ein und klicke auf „Berechnen“.",
                fill=MUTED, font=("Segoe UI", 11), justify="center"
            )
            return

        margin_x = 70
        usable_w = max(160, w - 2 * margin_x)
        bar_y = int(h * 0.43)
        bar_h = max(34, min(58, int(h * 0.095)))
        x0, x1 = margin_x, w - margin_x
        scale = usable_w / r.length

        # Technischer Zeichnungskopf
        c.create_text(w / 2, 22, text="U-STAHLTRAVERSE",
                      font=("Segoe UI", 12, "bold"), fill=NAVY)
        c.create_text(w / 2, 45,
                      text=f"L = {fmt(r.length)} mm    |    n = {r.intervals}    |    a = {fmt(r.spacing)} mm",
                      font=("Consolas", 10, "bold"), fill=TEXT)

        # Traverse als technische Seitenansicht mit Mittellinie
        c.create_rectangle(x0, bar_y, x1, bar_y + bar_h,
                           outline="#43515D", fill="#EEF2F5", width=2)
        c.create_line(x0, bar_y + bar_h / 2, x1, bar_y + bar_h / 2,
                      fill="#9AA6B2", dash=(4, 4))

        # Lochpositionen mit technischen Mittelpunktskreuzen
        radius = max(4, min(8, 0.38 * scale * r.spacing if r.intervals else 4))
        radius = min(radius, max(4, bar_h / 3))
        center_y = bar_y + bar_h / 2
        for i in range(r.holes):
            pos = r.start + i * r.spacing
            x = x0 + pos * scale
            is_fastening = i == 0 or i == r.holes - 1
            fill = RED if is_fastening else BLUE
            outline = RED_DARK if is_fastening else BLUE_DARK
            c.create_oval(x-radius, center_y-radius, x+radius, center_y+radius,
                          fill=fill, outline=outline, width=2)
            arm = radius + 5
            c.create_line(x-arm, center_y, x+arm, center_y, fill=outline, width=1)
            c.create_line(x, center_y-arm, x, center_y+arm, fill=outline, width=1)

        # Hilfslinien und Bemassung nach technischer Zeichnungslogik
        start_x = x0 + r.start * scale
        end_x = x0 + (r.length - r.end) * scale
        second_x = x0 + (r.start + r.spacing) * scale
        dim_top = bar_y - 86
        dim_mid = bar_y - 48
        dim_bottom = bar_y + bar_h + 62

        self._extension(x0, bar_y - 2, dim_top)
        self._extension(start_x, bar_y - 2, dim_top)
        self._extension(second_x, bar_y - 2, dim_top)
        self._extension(end_x, bar_y - 2, dim_top)
        self._extension(x1, bar_y - 2, dim_top)

        self._dimension(start_x, second_x, dim_top, f"a = {fmt(r.spacing)} mm", compact=True)
        self._dimension(x0, start_x, dim_mid, f"{fmt(r.start)} mm", compact=True)
        self._dimension(end_x, x1, dim_mid, f"{fmt(r.end)} mm", compact=True)
        self._dimension(x0, x1, dim_bottom, f"L = {fmt(r.length)} mm")

        # Nutzbare Lochstrecke als zweite technische Masslinie
        c.create_line(start_x, dim_bottom - 18, start_x, dim_bottom + 5, fill="#697783")
        c.create_line(end_x, dim_bottom - 18, end_x, dim_bottom + 5, fill="#697783")
        self._dimension(start_x, end_x, dim_bottom + 34, f"L1 = {fmt(r.usable)} mm", compact=True)

        # Technische Beschriftungen, ohne Legende
        c.create_text(x0, bar_y + bar_h + 10, anchor="nw",
                      text="0", fill=MUTED, font=("Consolas", 8))
        c.create_text(x1, bar_y + bar_h + 10, anchor="ne",
                      text=f"{fmt(r.length)}", fill=MUTED, font=("Consolas", 8))
        c.create_text(w - 12, h - 12, anchor="se",
                      text="SCHEMATISCH • NICHT MASSSTAEBLICH",
                      fill=MUTED, font=("Consolas", 8, "bold"))

    def _extension(self, x, y1, y2):
        c = self.canvas
        c.create_line(x, y1, x, y2, fill="#697783", width=1)

    def _dimension(self, x1, x2, y, label, compact=False):
        c = self.canvas
        if x2 < x1:
            x1, x2 = x2, x1
        line = "#52616D"
        c.create_line(x1, y, x2, y, fill=line, width=1)
        c.create_line(x1, y-5, x1, y+5, fill=line, width=1)
        c.create_line(x2, y-5, x2, y+5, fill=line, width=1)
        if x2 - x1 > 18:
            # offene technische Pfeilspitzen
            c.create_line(x1, y, x1+6, y-3, fill=line)
            c.create_line(x1, y, x1+6, y+3, fill=line)
            c.create_line(x2, y, x2-6, y-3, fill=line)
            c.create_line(x2, y, x2-6, y+3, fill=line)
        c.create_text((x1+x2)/2, y-7 if compact else y-9,
                      text=label, fill=TEXT,
                      font=("Consolas", 8, "bold"), anchor="s")

    def save_png(self):
        if not self.result:
            messagebox.showinfo("Keine Zeichnung", "Bitte zuerst eine Berechnung durchführen.", parent=self)
            return

        path = filedialog.asksaveasfilename(
            parent=self, title="Zeichnung speichern",
            defaultextension=".png",
            filetypes=[("PNG-Bild", "*.png")],
            initialfile="Traverse_Zeichnung.png"
        )
        if not path:
            return

        try:
            from PIL import Image, ImageDraw, ImageFont

            r = self.result
            W, H = 1500, 620
            im = Image.new("RGB", (W, H), "white")
            d = ImageDraw.Draw(im)

            try:
                font = ImageFont.truetype("arial.ttf", 22)
                small = ImageFont.truetype("arial.ttf", 18)
                titlefont = ImageFont.truetype("arial.ttf", 30)
                bigfont = ImageFont.truetype("arialbd.ttf", 25)
            except OSError:
                font = small = titlefont = bigfont = ImageFont.load_default()

            d.text((55, 30), APP_TITLE, fill=NAVY, font=titlefont)
            d.text(
                (55, 78),
                f"L = {fmt(r.length)} mm     n = {r.intervals}     a = {fmt(r.spacing)} mm",
                fill=BLUE_DARK, font=bigfont
            )

            x0, x1 = 90, 1410
            y0, y1 = 255, 315
            scale = (x1-x0) / r.length
            d.rectangle(
                (x0, y0, x1, y1),
                outline="#43515D", fill=TRAVERSE_FILL, width=3
            )
            d.line((x0, (y0+y1)//2, x1, (y0+y1)//2), fill="#9AA6B2", width=1)

            radius = max(4, min(10, int(0.42 * scale * r.spacing)))
            cy = (y0 + y1) // 2
            for i in range(r.holes):
                x = x0 + (r.start + i * r.spacing) * scale
                is_fastening = i == 0 or i == r.holes - 1
                fill = RED if is_fastening else BLUE
                outline = RED_DARK if is_fastening else BLUE_DARK
                d.ellipse(
                    (x-radius, cy-radius, x+radius, cy+radius),
                    fill=fill, outline=outline
                )

            def dim(a, b, y, label, f=small):
                d.line((a, y, b, y), fill="#52616D", width=2)
                d.line((a, y-8, a, y+8), fill="#52616D", width=2)
                d.line((b, y-8, b, y+8), fill="#52616D", width=2)
                if b-a > 24:
                    d.line((a, y, a+10, y-5), fill="#52616D", width=2)
                    d.line((a, y, a+10, y+5), fill="#52616D", width=2)
                    d.line((b, y, b-10, y-5), fill="#52616D", width=2)
                    d.line((b, y, b-10, y+5), fill="#52616D", width=2)
                bbox = d.textbbox((0, 0), label, font=f)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
                d.rectangle(
                    ((a+b-tw)//2-8, y-th-14, (a+b+tw)//2+8, y-4),
                    fill="white"
                )
                d.text(((a+b-tw)//2, y-th-12), label, fill=TEXT, font=f)

            first = x0 + r.start * scale
            last = x0 + (r.length-r.end) * scale
            second = x0 + (r.start + r.spacing) * scale
            # technische Hilfslinien
            for xx in (x0, first, second, last, x1):
                d.line((xx, y0-20, xx, y0-85), fill="#697783", width=1)
                d.line((xx, y1+10, xx, y1+65), fill="#697783", width=1)
            dim(first, second, 165, f"a = {fmt(r.spacing)} mm")
            dim(x0, first, 215, f"{fmt(r.start)} mm")
            dim(last, x1, 215, f"{fmt(r.end)} mm")
            dim(x0, x1, 445, f"L = {fmt(r.length)} mm")
            dim(first, last, 495, f"L1 = {fmt(r.usable)} mm")

            d.text(
                (90, 545),
                f"n = {r.intervals}   |   2 Befestigungslöcher   |   {r.holes_without_fastening} weitere Löcher",
                fill=TEXT, font=font
            )
            d.text(
                (90, 580),
                "TECHNISCHE SCHEMATISCHE DARSTELLUNG  •  NICHT MASSSTAEBLICH",
                fill=MUTED, font=small
            )

            im.save(path, "PNG")
            messagebox.showinfo(
                "Gespeichert",
                f"Die Zeichnung wurde gespeichert:\n{path}",
                parent=self
            )
        except ImportError:
            messagebox.showerror(
                "PNG-Export nicht verfügbar",
                "Die PNG-Bibliothek fehlt. Bitte verwenden Sie die mitgelieferte vollständige EXE "
                "oder installieren Sie Pillow für den Quellcodebetrieb.",
                parent=self
            )
        except Exception as exc:
            messagebox.showerror(
                "Speichern fehlgeschlagen",
                f"Die Zeichnung konnte nicht gespeichert werden:\n{exc}",
                parent=self
            )


if __name__ == "__main__":
    App().mainloop()
