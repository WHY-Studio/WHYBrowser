# mini_browser.py  (komplett korrigiert)
# Anforderungen: pip install PySide6
# Start: python mini_browser.py

import sys
import json
from pathlib import Path
from urllib.parse import quote_plus
from PySide6.QtWidgets import QToolButton, QSizePolicy
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
import subprocess, shlex


from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLineEdit, QLabel, QToolBar,
    QInputDialog, QColorDialog, QMessageBox, QStackedLayout
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QUrl, QRect, QPropertyAnimation
from PySide6.QtWidgets import QToolButton
from PySide6.QtWidgets import QSizePolicy  # Ganz oben im Code einfügen!
from PySide6.QtWidgets import QLabel, QGridLayout, QWidget
from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QPalette
import json, os
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QTransform, QPixmap, QIcon
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QLabel, QPushButton
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor
import random
from PySide6.QtCore import QEvent
from PySide6.QtCore import Signal
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtWidgets import QProgressBar, QLabel, QScrollArea, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMessageBox, QFileDialog
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest
from datetime import datetime
from PySide6.QtWidgets import QScrollArea, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QToolButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMessageBox
from PySide6.QtNetwork import QNetworkProxy
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QCheckBox, QSpinBox, QMessageBox
import os, json, subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLineEdit,
    QLabel, QTabWidget, QListWidget, QListWidgetItem, QSplitter
)
from PySide6.QtCore import Signal, QObject, QDateTime
from PySide6.QtGui import QTextCursor

# Request-Interceptor: sammelt Netzwerkanfragen
from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineProfile
from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QMessageBox, QFormLayout
)
from PySide6.QtGui import QPixmap, QIcon, QAction
from PySide6.QtCore import Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtWebEngineWidgets import QWebEngineView
import winreg


SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_stylesheet(app, accent_color="#61afef"):
    style_path = Path("style.css")
    if not style_path.exists():
        print("⚠️ style.css nicht gefunden")
        return

    css = style_path.read_text(encoding="utf-8")
    css = css.replace("{{ACCENT}}", accent_color)
    app.setStyleSheet(css)


HISTORY_FILE = "history.json"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

AUTOFILL_FILE = "autofill_data.json"

def load_autofill_data():
        """Lädt gespeicherte AutoFill-Daten aus JSON."""
        if os.path.exists(AUTOFILL_FILE):
            try:
                with open(AUTOFILL_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

def save_autofill_data(data):
        """Speichert AutoFill-Daten in JSON."""
        with open(AUTOFILL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

# -------------------- Config --------------------
CONFIG_PATH = Path.home() / ".pybrowser_config.json"
DEFAULT_CONFIG = {
    "homepage": "https://www.google.com",
    "search_engines": {
        "google": "https://www.google.com/search?q={}",
        "bing": "https://www.bing.com/search?q={}",
        "duckduckgo": "https://duckduckgo.com/?q={}",
        "yahoo": "https://search.yahoo.com/search?p={}",
        "ecosia": "https://www.ecosia.org/search?q={}"
    }
}



def load_config():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
    return DEFAULT_CONFIG.copy()


def save_config(cfg):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")




from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor

class NetworkInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()
        self.log = []  # <--- NEU: Liste zum Speichern von Netzwerkaktivitäten

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        method = info.requestMethod().data().decode("utf-8")
        headers = {str(k, "utf-8"): str(v, "utf-8") for k, v in info.headers().items()}


        # Eintrag in den Log speichern
        entry = {
            "url": url,
            "method": method,
            "headers": headers,
        }
        self.log.append(entry)

        # Optional: Einfache Sicherheitswarnung
        if url.startswith("http://"):
            print(f"⚠️ Unsichere Verbindung erkannt: {url}")




# -------------------- Browser Tab --------------------
class BrowserTab(QWidget):
    def __init__(self, url=None, parent=None):
        super().__init__(parent)
        self.parent_browser = parent
        layout = QVBoxLayout(self)
        self.view = QWebEngineView()
        self.view.page().acceptNavigationRequest = self.accept_navigation_request
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.show_context_menu)
        self.view.load(QUrl(url))
        self.view.loadStarted.connect(self.parent().start_reload_animation)
        self.view.loadFinished.connect(self.parent().stop_reload_animation)
        layout.addWidget(self.view)
        
        from PySide6.QtWebChannel import QWebChannel

        channel = QWebChannel(self.view.page())
        channel.registerObject("browserApi", parent)  # <-- parent ist dein MiniBrowser
        self.view.page().setWebChannel(channel)
        
        # Nach self.interceptor = NetworkInterceptor()
        self.interceptor = NetworkInterceptor()

        # Standardprofil abrufen (global für alle Tabs)
        
        profile = QWebEngineProfile.defaultProfile()

        # Interceptor anwenden
        profile.setUrlRequestInterceptor(self.interceptor)








    def page(self):
        return self.view.page()

    def load(self, url):
        self.view.load(QUrl(url))

    def accept_navigation_request(self, url, nav_type, is_main_frame):
        if nav_type == QWebEnginePage.NavigationTypeLinkClicked:
            # Öffne Links, die auf eine neue Seite führen, in neuem Tab
            parent = self.parent()
            if parent and hasattr(parent, "add_tab"):
                new_tab = parent.add_tab(url.toString())
                parent.tabs.setCurrentWidget(new_tab)
                return False  # blockiere alte Navigation
        return True

    def check_site_security(self, url):
        """Überprüft URL auf HTTPS und bekannte gefährliche Domains"""
        

        # 1. HTTPS prüfen
        if not url.startswith("https://"):
            QMessageBox.warning(
                self, 
                "Unsichere Verbindung", 
                f"Die Website '{url}' ist nicht über HTTPS gesichert.\n"
                "Deine Verbindung könnte abgehört werden."
            )

        # 2. Bekannte gefährliche Seiten prüfen (lokale Blacklist)
        dangerous_sites = [
            "phishing.com", "malwaretest.com", "dangerous-site.org"
        ]
        if any(d in url for d in dangerous_sites):
            QMessageBox.critical(
                self,
                "Gefährliche Website blockiert",
                f"Die Website '{url}' ist als gefährlich bekannt.\n"
                "Der Zugriff wurde blockiert."
            )
            return False  # Laden verhindern

        return True

    def accept_navigation_request(self, url, nav_type, is_main_frame):
        if nav_type == QWebEnginePage.NavigationTypeLinkClicked:
            # Prüfe Sicherheit
            if not self.check_site_security(url.toString()):
                return False

            parent = self.parent()
            if parent and hasattr(parent, "add_tab"):
                new_tab = parent.add_tab(url.toString())
                parent.tabs.setCurrentWidget(new_tab)
                return False
        return True
    
    def show_security_overlay(self, message, color="#ff4d4d"):
        overlay = QLabel(message, self)
        overlay.setStyleSheet(f"""
            background-color: {color};
            color: white;
            padding: 10px;
            border-radius: 6px;
            font-weight: bold;
        """)
        overlay.setAlignment(Qt.AlignCenter)
        overlay.setFixedHeight(40)
        self.layout().insertWidget(0, overlay)

        # Nach 3 Sekunden ausblenden
        QTimer.singleShot(3000, overlay.deleteLater)



    def show_context_menu(self, position):
        menu = QMenu(self)
        menu.setObjectName("ContextMenu")

        # === Styling im Browser-Look ===
        menu.setStyleSheet("""
            QMenu {
                background-color: #181818;
                border: 1px solid #2c2c2c;
                border-radius: 10px;
                padding: 8px;
            }
            QMenu::item {
                color: #ddd;
                padding: 8px 24px;
                border-radius: 6px;
                font-size: 13px;
            
            }
            QMenu::item:selected {
                background-color: #333;
                color: white;
                border: 1px solid white; 
            }
            QMenu::separator {
                height: 1px;
                background: #333;
                margin: 6px 8px;
            }
        """)

        # === Hilfsfunktion für Icons ===
        def icon(name):
            return QIcon(f"icons/{name}.svg")

        # === Navigation ===
        act_back = QAction(icon("back1"), "Zurück", self)
        act_back.triggered.connect(self.view.back)

        act_forward = QAction(icon("forward2"), "Vorwärts", self)
        act_forward.triggered.connect(self.view.forward)

        act_reload = QAction(icon("reload3"), "Neu laden", self)
        act_reload.triggered.connect(self.view.reload)

        act_home = QAction(icon("home3"), "Startseite", self)
        act_home.triggered.connect(lambda: self.view.setUrl(QUrl(self.parent_browser.config["homepage"])))

        # === Seite / Tab Aktionen ===
        act_new_tab = QAction(icon("plus3"), "In neuem Tab öffnen", self)
        act_new_tab.triggered.connect(lambda: self.parent_browser.add_tab(self.view.url().toString()))

        act_dup_tab = QAction(icon("duplicate4"), "Tab duplizieren", self)
        act_dup_tab.triggered.connect(lambda: self.parent_browser.add_tab(self.view.url().toString()))

        act_close_tab = QAction(icon("close4"), "Diesen Tab schließen", self)
        act_close_tab.triggered.connect(lambda: self.parent_browser.close_current_tab())

        # === Inhalt / Tools ===
        act_copy_url = QAction(icon("link5"), "URL kopieren", self)
        act_copy_url.triggered.connect(lambda: QApplication.clipboard().setText(self.view.url().toString()))

        act_save_page = QAction(icon("download6"), "Seite speichern unter...", self)
        act_save_page.triggered.connect(self.save_current_page)

        act_source = QAction(icon("code7"), "Seitenquelle anzeigen", self)
        act_source.triggered.connect(lambda: self.view.page().toHtml(self.show_page_source))

        act_inspect = QAction(icon("dev8"), "Element untersuchen", self)
        act_inspect.triggered.connect(self.parent_browser.toggle_devtools)

        act_fullscreen = QAction(icon("fullscreen7"), "Vollbildmodus", self)
        act_fullscreen.triggered.connect(lambda: self.parent_browser.toggle_fullscreen())

        act_print = QAction(icon("print7"), "Seite drucken", self)
        act_print.triggered.connect(lambda: self.view.page().printToPdf("page.pdf"))

        act_translate = QAction(icon("translate7"), "Seite übersetzen", self)
        act_translate.triggered.connect(lambda: self.parent_browser.translate_page(self.view))

        act_screenshot = QAction(icon("camera7"), "Screenshot aufnehmen", self)
        act_screenshot.triggered.connect(self.take_screenshot)

        # === Menüstruktur ===
        menu.addSection("Navigation")
        menu.addAction(act_back)
        menu.addAction(act_forward)
        menu.addAction(act_reload)
        menu.addAction(act_home)

        menu.addSeparator()
        menu.addSection("Tab")
        menu.addAction(act_new_tab)
        menu.addAction(act_dup_tab)
        menu.addAction(act_close_tab)

        menu.addSeparator()
        menu.addSection("Seite & Tools")
        menu.addAction(act_copy_url)
        menu.addAction(act_save_page)
        menu.addAction(act_source)
        menu.addAction(act_inspect)

        menu.addSeparator()
        menu.addAction(act_fullscreen)
        menu.addAction(act_print)
        menu.addAction(act_translate)
        menu.addAction(act_screenshot)

        # === Anzeigen ===
        menu.exec_(self.view.mapToGlobal(position))


    def save_current_page(self):
        """Speichert aktuelle Seite als HTML."""
        self.view.page().toHtml(lambda html: self._save_html_callback(html))


    def _save_html_callback(self, html):
        path, _ = QFileDialog.getSaveFileName(self, "Seite speichern unter", "page.html", "HTML-Dateien (*.html)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            QMessageBox.information(self, "Gespeichert", f"✅ Seite gespeichert unter:\n{path}")


    def show_page_source(self, html):
        """Öffnet den HTML-Quelltext in einem neuen Tab."""
        src_tab = BrowserTab()
        src_tab.view.setHtml(f"<pre style='color:white;background:#111;padding:10px;font-family:monospace;'>{html.replace('<','&lt;').replace('>','&gt;')}</pre>")
        self.parent_browser.add_tab_widget(src_tab, "Seitenquelle")


    def take_screenshot(self):
        """Nimmt einen Screenshot der aktuellen Seite auf."""
        path, _ = QFileDialog.getSaveFileName(self, "Screenshot speichern", "screenshot.png", "PNG-Bild (*.png)")
        if not path:
            return
        self.view.grab().save(path)
        QMessageBox.information(self, "Screenshot", f"📸 Screenshot gespeichert unter:\n{path}")


# -------------------- Settings Sidebar --------------------
class ResponsiveSidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowFlags(Qt.SubWindow | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("Sidebar")

        # ⚠️ Die Zeile mit self.btn_close war zu früh – verschoben nach unten
        # self.btn_close.setObjectName("CloseButton")  <-- entfernt

        # Overlay (halbtransparent)
        self.overlay = QWidget(parent)
        self.overlay.setStyleSheet("background-color: rgba(0,0,0,120);")
        self.overlay.hide()
        self.overlay.mousePressEvent = lambda event: None  # blockiert Klicks

        # Layout der Sidebar
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top-Bar mit Titel und Close-Button
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(10, 10, 10, 10)

        # "Settings" Titel (links)
        title_label = QLabel("Settings")
        title_label.setObjectName("SidebarTitle")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        top_bar.addWidget(title_label)

        top_bar.addStretch()  # Abstand zwischen Titel und Close-Button

        # Close-Button (rechts)
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(25, 25)
        self.btn_close.setObjectName("CloseButton")
        self.btn_close.clicked.connect(self.hide_sidebar)
        top_bar.addWidget(self.btn_close)

        main_layout.addLayout(top_bar)


        # Tabs Buttons
        self.stack = QStackedLayout()
        tabs_layout = QHBoxLayout()
        tabs_layout.setContentsMargins(5, 0, 5, 0)
        tabs_layout.setSpacing(5)

        self.tab_buttons = []
        self.pages = []

        
        



        tab_info = [
            ("Theme", self.create_theme_page()),
            ("Search Engine", self.create_search_page()),
            ("Privacy", self.create_privacy_page()),
            ("Downloads", self.create_downloads_page()),
            ("Extensions", self.create_extensions_page())
        ]
        
        
        for name, page in tab_info:
            btn = QPushButton(name)
            btn.setFixedHeight(25)
            # Style kommt jetzt aus style.qss, also kein Inline-Style mehr
            btn.clicked.connect(lambda checked, p=page: self.stack.setCurrentWidget(p))
            tabs_layout.addWidget(btn)
            self.tab_buttons.append(btn)
            self.pages.append(page)
            self.stack.addWidget(page)

        main_layout.addLayout(tabs_layout)

        # Content Widget
        content_widget = QWidget()
        content_widget.setLayout(self.stack)
        main_layout.addWidget(content_widget)


    @staticmethod
    def load_accent_theme():
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    theme = cfg.get("theme", {})
                    return {
                        "name": theme.get("name", "Ocean Blue"),
                        "color": theme.get("color", "#61afef")
                    }
            except:
                pass
        return {"name": "Ocean Blue", "color": "#61afef"}


    @staticmethod
    def save_accent_theme(name, color):
        cfg = {}
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except:
                cfg = {}

        cfg.setdefault("theme", {})
        cfg["theme"]["name"] = name
        cfg["theme"]["color"] = color

        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)


    def show_sidebar(self):
        self.overlay.setGeometry(self.parent_window.rect())
        self.overlay.show()
        self.update_geometry()
        self.show()
        self.raise_()
        # Animation
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        start_rect = QRect(self.parent_window.width(), 0, self.width(), self.height())
        end_rect = QRect(self.parent_window.width() - self.width(), 0, self.width(), self.height())
        self.setGeometry(start_rect)
        self.anim.setStartValue(start_rect)
        self.anim.setEndValue(end_rect)
        self.anim.start()

    def hide_sidebar(self):
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        start_rect = QRect(self.x(), self.y(), self.width(), self.height())
        end_rect = QRect(self.parent_window.width(), self.y(), self.width(), self.height())
        self.anim.setStartValue(start_rect)
        self.anim.setEndValue(end_rect)
        self.anim.finished.connect(self._final_hide)
        self.anim.start()

    def _final_hide(self):
        self.hide()
        self.overlay.hide()

    THEME_PRESETS = {
                "Ocean Blue": "#61afef",
                "Lava Red": "#ff4d4d",
                "Forest Green": "#98c379",
                "Sun Gold": "#e5c07b",
                "Violet Dream": "#c678dd",
                "Aqua Breeze": "#56b6c2",
                "Autumn Brown": "#d19a66",
                "Pure White": "#ffffff",
                "Neon Orange": "#ff8f40",
                "Cherry Pink": "#f7768e",
            }



    


    # =========================================================
    # === Moderner Farbpicker =================================
    # =========================================================
    def create_color_picker(self, parent_layout=None):
        current_color = self.load_accent_color()

        label = QLabel("🎨 Akzentfarbe")
        label.setStyleSheet("font-weight: 600; font-size: 15px; color: white; margin-bottom: 6px;")
        parent_layout.addWidget(label)

        # Vorschau-Feld
        preview = QFrame()
        preview.setFixedHeight(30)
        preview.setStyleSheet(f"background-color: {current_color}; border-radius: 8px; border: 1px solid #444;")
        parent_layout.addWidget(preview)

        color_widget = QWidget()
        grid = QGridLayout(color_widget)
        grid.setSpacing(8)

        # Farbpalette (10 Farben)
        colors = [
            "#61afef", "#ff4d4d", "#98c379", "#e5c07b",
            "#c678dd", "#56b6c2", "#d19a66", "#ffffff",
            "#ff8f40", "#f7768e"
        ]

        row, col = 0, 0
        for c in colors:
            btn = QPushButton()
            btn.setFixedSize(QSize(30, 30))
            border = "2px solid white" if c == current_color else "1px solid #222"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c};
                    border-radius: 6px;
                    border: {border};
                    transition: 0.25s;
                }}
                QPushButton:hover {{
                    border: 2px solid {c};
                    box-shadow: 0 0 8px {c};
                }}
            """)
            btn.clicked.connect(lambda _, color=c: self.change_accent_color(color, preview))
            grid.addWidget(btn, row, col)
            col += 1
            if col > 4:
                col = 0
                row += 1

        parent_layout.addWidget(color_widget)

        # Benutzerdefinierte Farbe
        custom_btn = QPushButton("Benutzerdefinierte Farbe…")
        custom_btn.setFixedHeight(34)
        custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border-radius: 8px;
                border: 1px solid #444;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #61afef;
            }
        """)
        custom_btn.clicked.connect(lambda: self.choose_accent_color(preview))
        parent_layout.addWidget(custom_btn)

    # =========================================================
    # === Theme Page ==========================================
    # =========================================================
    def create_theme_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        header = QLabel("Erscheinungsbild – Theme auswählen")
        header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        """)
        layout.addWidget(header)

        # Scroll Area Container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(15)

        current = self.load_accent_theme()   # -> {"name": "...", "color": "..."}

        row, col = 0, 0
        self.tile_buttons = []

        for name, color in self.THEME_PRESETS.items():
            tile = QPushButton()
            tile.setFixedSize(150, 120)
            tile.setCursor(Qt.PointingHandCursor)

            border = "3px solid white" if current["name"] == name else "1px solid #333"

            tile.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1e1e1e;
                    border-radius: 10px;
                    border: {border};
                    padding: 8px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    border: 3px solid {color};
                }}
            """)

            # Farbe + Name im Tile anzeigen
            tile_layout = QVBoxLayout(tile)
            color_box = QFrame()
            color_box.setStyleSheet(f"background: {color}; border-radius: 6px;")
            color_box.setFixedHeight(40)
            tile_layout.addWidget(color_box)

            lbl = QLabel(name)
            lbl.setStyleSheet("color: white; font-weight: 600;")
            tile_layout.addWidget(lbl)

            tile.clicked.connect(lambda _, n=name, c=color: self.select_theme_tile(n, c))

            self.tile_buttons.append(tile)
            grid.addWidget(tile, row, col)

            col += 1
            if col >= 3:
                col = 0
                row += 1

        # --- Custom Theme Button ---
        add_btn = QPushButton("+ Eigene Farbe")
        add_btn.setFixedSize(150, 120)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e2e2e;
                border-radius: 10px;
                border: 1px dashed #555;
                color: #ccc;
                font-size: 16px;
            }
            QPushButton:hover {
                border: 2px dashed #61afef;
                color: white;
            }
        """)
        add_btn.clicked.connect(self.pick_custom_color)

        grid.addWidget(add_btn, row, col)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        return page


    # =========================================================
    # === Farb-Logik ==========================================
    # =========================================================
    def choose_accent_color(self, preview_frame=None):
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            preview_frame.setStyleSheet(f"background-color: {hex_color}; border-radius: 8px; border: 1px solid #444;")
            self.change_accent_color(hex_color, preview_frame)

    def change_accent_color(self, color, preview_frame=None):
        """Accentfarbe speichern & Stylesheet neu laden"""
        from main import load_stylesheet
        app = QApplication.instance()
        self.save_accent_color(color)
        load_stylesheet(app, color)

    def select_theme_tile(self, name, color):
        """Kachel optisch markieren + speichern + Theme anwenden"""
        for btn in self.tile_buttons:
            btn.setStyleSheet(btn.styleSheet().replace("3px solid white", "1px solid #333"))

        # ausgewählten Button highlighten
        sender = self.sender()
        style = sender.styleSheet()
        style = style.replace("1px solid #333", "3px solid white")
        sender.setStyleSheet(style)

        # Speichern
        self.save_accent_theme(name, color)

        # Anwenden
        from main import load_stylesheet
        app = QApplication.instance()
        load_stylesheet(app, color)

        QMessageBox.information(self, "Theme geändert", f"Neues Theme: {name}")

    def pick_custom_color(self):
        color = QColorDialog.getColor()
        if not color.isValid():
            return

        hex_color = color.name()
        name = f"Custom ({hex_color})"

        # Speichern + anwenden
        self.save_accent_theme(name, hex_color)

        from main import load_stylesheet
        app = QApplication.instance()
        load_stylesheet(app, hex_color)

        QMessageBox.information(self, "Eigene Farbe", f"Eigene Farbe gespeichert: {hex_color}")


    def update_geometry(self):
        w = self.parent_window.width() // 2
        h = self.parent_window.height()
        self.setFixedWidth(w)
        self.setFixedHeight(h)
        self.move(self.parent_window.width() - w, 0)
        self.overlay.setGeometry(0, 0, self.parent_window.width(), self.parent_window.height())

    # -------------------- Theme --------------------
    

    def apply_theme(self, colors):
        cfg = self.parent_window.config
        cfg["theme"] = colors
        save_config(cfg)
        QMessageBox.information(self, "Theme", f"Theme '{colors}' gespeichert!")

    # -------------------- Search Engine --------------------
    def create_search_page(self):
        from PySide6.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
            QComboBox, QCheckBox, QLineEdit, QMessageBox, QFrame
        )
        from PySide6.QtGui import QIcon
        from PySide6.QtCore import Qt, QSize

        page = QWidget()
        page.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-size: 14px;
            }
            QLabel {
                color: #dddddd;
            }
            QCheckBox {
                spacing: 10px;
                font-size: 14px;
                color: #dddddd;
            }
            QCheckBox::indicator {
                width: 10px;
                height: 10px;
                border-radius: 6px;
                border: 1px solid #555;
                background: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                background-color: white;
                image: url(icons/check.svg);
                border: 1px solid #333;
            }
        """)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(18)

        cfg = self.parent_window.config

        # --- Titelbereich ---
        title = QLabel("Such- & Startseiten-Einstellungen")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 6px;
        """)
        layout.addWidget(title)

        subtitle = QLabel("Passe dein Suchverhalten, deine Startseite und Privatsphäre-Einstellungen an.")
        subtitle.setStyleSheet("color: #999; font-size: 13px; margin-bottom: 16px;")
        layout.addWidget(subtitle)

        # ----------------------------------------------------
        # 🧭 Suchmaschine
        # ----------------------------------------------------
        section_label = QLabel(" Standard-Suchmaschine")
        section_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f0f0f0;")
        layout.addWidget(section_label)

        search_box = QHBoxLayout()
        self.engine_selector = QComboBox()
        self.engine_selector.addItems(["Google", "Bing", "DuckDuckGo", "Ecosia", "Yahoo"])
        self.engine_selector.setFixedHeight(36)
        self.engine_selector.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #444;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 1px solid #61afef;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #444;
                selection-background-color: #61afef;
            }
        """)
        current_engine = cfg.get("search_engine", "duckduckgo").capitalize()
        if current_engine in [self.engine_selector.itemText(i) for i in range(self.engine_selector.count())]:
            self.engine_selector.setCurrentText(current_engine)

        search_icon = QLabel()
        search_icon.setPixmap(QIcon("icons/search.svg").pixmap(QSize(24, 24)))
        search_icon.setStyleSheet("margin-right: 6px;")
        search_box.addWidget(search_icon)
        search_box.addWidget(self.engine_selector)
        layout.addLayout(search_box)

        # ----------------------------------------------------
        # 🏠 Startseite
        # ----------------------------------------------------
        home_label = QLabel("Startseite")
        home_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f0f0f0; margin-top: 10px;")
        layout.addWidget(home_label)

        self.home_input = QLineEdit()
        self.home_input.setText(cfg.get("homepage", "https://www.google.com"))
        self.home_input.setPlaceholderText("z. B. https://example.com oder file:///...")
        self.home_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #61afef;
            }
        """)
        layout.addWidget(self.home_input)

        # ----------------------------------------------------
        # ⚙️ Weitere Einstellungen
        # ----------------------------------------------------
        options_frame = QFrame()
        opt_layout = QVBoxLayout(options_frame)
        opt_layout.setSpacing(10)

        self.suggestions_checkbox = QCheckBox("Suchvorschläge aktivieren")
        self.suggestions_checkbox.setChecked(cfg.get("search_suggestions", True))
        opt_layout.addWidget(self.suggestions_checkbox)

        self.safe_search_checkbox = QCheckBox("SafeSearch aktivieren (ungeeignete Inhalte blockieren)")
        self.safe_search_checkbox.setChecked(cfg.get("safe_search", True))
        opt_layout.addWidget(self.safe_search_checkbox)

        self.incognito_checkbox = QCheckBox("Neue Tabs im Inkognito-Modus starten")
        self.incognito_checkbox.setChecked(cfg.get("default_incognito", False))
        opt_layout.addWidget(self.incognito_checkbox)



        btn_layout = QHBoxLayout()
        default_btn = QPushButton("Als Standardbrowser festlegen")
        default_btn.setFixedHeight(36)
        default_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 8px;
                border: 1px solid #555;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #555;
                border: 1px solid #61afef;
            }
        """)
        default_btn.clicked.connect(self.parent_window.register_as_default_browser)

        layout.addWidget(default_btn)



        layout.addWidget(options_frame)

        # ----------------------------------------------------
        # 💾 Buttons unten
        # ----------------------------------------------------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        reset_btn = QPushButton("↺ Standardwerte")
        reset_btn.setFixedHeight(36)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border-radius: 8px;
                border: 1px solid #444;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                border: 1px solid #ff6b6b;
            }
        """)

        save_btn = QPushButton("Änderungen speichern")
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2f6fef;
                color: white;
                border-radius: 8px;
                border: 1px solid #2a5ed7;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #478fff;
            }
        """)

        btn_layout.addWidget(reset_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        # ----------------------------------------------------
        # 💡 Funktionen
        # ----------------------------------------------------
        def save_search_settings():
            engine = self.engine_selector.currentText().lower()
            cfg["search_engine"] = engine
            cfg["homepage"] = self.home_input.text()
            cfg["search_suggestions"] = self.suggestions_checkbox.isChecked()
            cfg["safe_search"] = self.safe_search_checkbox.isChecked()
            cfg["default_incognito"] = self.incognito_checkbox.isChecked()

            save_config(cfg)
            QMessageBox.information(self, "Gespeichert", "Einstellungen erfolgreich gespeichert!")

            if hasattr(self.parent_window, "browserBridge"):
                self.parent_window.browserBridge.searchEngineChanged.emit(engine)

        def reset_defaults():
            self.engine_selector.setCurrentText("DuckDuckGo")
            self.home_input.setText("https://www.google.com")
            self.suggestions_checkbox.setChecked(True)
            self.safe_search_checkbox.setChecked(True)
            self.incognito_checkbox.setChecked(False)

        save_btn.clicked.connect(save_search_settings)
        reset_btn.clicked.connect(reset_defaults)

        layout.addStretch()
        return page
    


    def register_as_default_browser(self):
        import winreg
        import sys, os

        exe = os.path.abspath(sys.argv[0])
        prog_id = "WHYBrowserHTML"

        try:
            # 🔹 Hauptklassenschlüssel
            key_path = rf"Software\Classes\{prog_id}"
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)

            winreg.SetValue(key, "", winreg.REG_SZ, "WHY Browser HTML Document")
            winreg.SetValueEx(key, "FriendlyTypeName", 0, winreg.REG_SZ, "WHY Browser")

            # 🔹 Icon
            winreg.SetValueEx(key, "DefaultIcon", 0, winreg.REG_SZ, f'"{exe}",0')

            # 🔹 Öffnen-Kommando
            cmd_path = rf"{key_path}\shell\open\command"
            cmd_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_path)
            winreg.SetValue(cmd_key, "", winreg.REG_SZ, f'"{exe}" "%1"')

            QMessageBox.information(
                self,
                "Erfolg",
                "WHY Browser wurde als Standardbrowser registriert!\n"
                "Öffne nun Windows Einstellungen → Standard Apps → Browser."
            )

        except Exception as e:
            QMessageBox.warning(self, "Fehler", str(e))




    def apply_privacy_settings(self, settings):
        profile = QWebEngineProfile.defaultProfile()

        # 🔹 JavaScript
        profile.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, settings.get("javascript", True))

        # 🔹 Cookies
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.AllowPersistentCookies if settings.get("cookies", True)
            else QWebEngineProfile.NoPersistentCookies
        )

        # 🔹 Verlauf
        if not settings.get("history", True):
            profile.setPersistentStoragePath("")  # deaktiviert Speicherung
        else:
            profile.setPersistentStoragePath("webdata")

        # 🔹 Super-Stealth Mode
        if settings.get("stealth", False):
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
            profile.setPersistentStoragePath("")
            profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
            profile.setHttpCacheMaximumSize(0)
            profile.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, False)

        # 🔹 VPN (Proxy)
        vpn_choice = settings.get("vpn", "Kein VPN")
        if vpn_choice != "Kein VPN":
            if vpn_choice == "Germany (Frankfurt)":
                proxy = QNetworkProxy(QNetworkProxy.HttpProxy, "de.vpnserver.com", 8080)
            elif vpn_choice == "USA (New York)":
                proxy = QNetworkProxy(QNetworkProxy.HttpProxy, "us.vpnserver.com", 8080)
            elif vpn_choice == "UK (London)":
                proxy = QNetworkProxy(QNetworkProxy.HttpProxy, "uk.vpnserver.com", 8080)
            elif vpn_choice == "Netherlands (Amsterdam)":
                proxy = QNetworkProxy(QNetworkProxy.HttpProxy, "nl.vpnserver.com", 8080)
            QNetworkProxy.setApplicationProxy(proxy)
        else:
            QNetworkProxy.setApplicationProxy(QNetworkProxy())  # kein VPN


    def set_search_engine(self, engine):
        config = self.parent_window.config
        config["search_engine"] = engine.lower()
        save_config(config)
        view = self.parent_window.current_view()
        if view:
            view.setUrl(QUrl(config["search_engines"][engine.lower()].format("")))

    # -------------------- Dummy Pages --------------------
    def create_privacy_page(self):
        from PySide6.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
            QPushButton, QComboBox, QMessageBox, QFrame
        )
        from PySide6.QtGui import QIcon
        from PySide6.QtCore import QSize, Qt

        page = QWidget()
        page.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: white; }
            QLabel { color: #dddddd; font-size: 14px; }
            QCheckBox {
                spacing: 10px;
                font-size: 14px;
                color: #dddddd;
            }
            QCheckBox::indicator {
                width: 10px; 
                height: 10px;
                border-radius: 6px;
                border: 1px solid #555;
                background: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                background-color: white;
                image: url(icons/check.svg);
                border: 1px solid #333;
            }
        """)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(18)

        cfg = self.parent_window.config
        privacy = cfg.get("privacy", {})

        # --- Titel ---
        title = QLabel("Datenschutz & Sicherheit")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #fff;")
        layout.addWidget(title)
        subtitle = QLabel("Kontrolliere, wie dein Browser mit Daten, Cookies und Skripten umgeht.")
        subtitle.setStyleSheet("color: #999; font-size: 13px; margin-bottom: 10px;")
        layout.addWidget(subtitle)

        # --- Sektion 1: Allgemein ---
        general_label = QLabel("Allgemeine Einstellungen")
        general_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #f0f0f0;")
        layout.addWidget(general_label)

        self.js_checkbox = QCheckBox("JavaScript aktivieren (empfohlen)")
        self.js_checkbox.setChecked(privacy.get("javascript", True))
        layout.addWidget(self.js_checkbox)

        self.cookies_checkbox = QCheckBox("Cookies zulassen")
        self.cookies_checkbox.setChecked(privacy.get("cookies", True))
        layout.addWidget(self.cookies_checkbox)

        self.history_checkbox = QCheckBox("Verlauf speichern")
        self.history_checkbox.setChecked(privacy.get("history", True))
        layout.addWidget(self.history_checkbox)

        self.stealth_checkbox = QCheckBox("Super-Stealth-Modus aktivieren")
        self.stealth_checkbox.setToolTip("Verlauf, Cookies, Cache und Downloads werden vollständig deaktiviert.")
        self.stealth_checkbox.setChecked(privacy.get("stealth", False))
        layout.addWidget(self.stealth_checkbox)

        # --- Sektion 2: Sicherheit ---
        security_label = QLabel("Sicherheit & Tracking-Schutz")
        security_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #f0f0f0; margin-top: 10px;")
        layout.addWidget(security_label)

        self.adblock_checkbox = QCheckBox("Werbung & Tracker blockieren")
        self.adblock_checkbox.setChecked(privacy.get("adblock", True))
        layout.addWidget(self.adblock_checkbox)

        self.fingerprint_checkbox = QCheckBox("Fingerprinting-Schutz aktivieren")
        self.fingerprint_checkbox.setChecked(privacy.get("fingerprint_protection", False))
        layout.addWidget(self.fingerprint_checkbox)

        self.https_checkbox = QCheckBox("Immer HTTPS verwenden (wenn möglich)")
        self.https_checkbox.setChecked(privacy.get("force_https", True))
        layout.addWidget(self.https_checkbox)

        # --- Sektion 3: VPN ---
        vpn_label = QLabel("VPN / Proxy-Server")
        vpn_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #f0f0f0; margin-top: 10px;")
        layout.addWidget(vpn_label)

        self.vpn_selector = QComboBox()
        self.vpn_selector.addItems([
            "Kein VPN",
            "Germany (Frankfurt)",
            "USA (New York)",
            "UK (London)",
            "Netherlands (Amsterdam)"
        ])
        self.vpn_selector.setCurrentText(privacy.get("vpn", "Kein VPN"))
        self.vpn_selector.setFixedHeight(34)
        self.vpn_selector.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #444;
                border-radius: 8px;
                padding-left: 10px;
                font-size: 14px;
            }
            QComboBox:hover { border: 1px solid #61afef; }
        """)
        layout.addWidget(self.vpn_selector)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        reset_btn = QPushButton("↺ Standardwerte")
        reset_btn.setFixedHeight(36)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border-radius: 8px;
                border: 1px solid #444;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                border: 1px solid #ff6b6b;
            }
        """)

        save_btn = QPushButton("Änderungen speichern")
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2f6fef;
                color: white;
                border-radius: 8px;
                border: 1px solid #2a5ed7;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #478fff; }
        """)

        btn_layout.addWidget(reset_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        # --- Funktionen ---
        def save_privacy_settings():
            cfg.setdefault("privacy", {})
            cfg["privacy"] = {
                "javascript": self.js_checkbox.isChecked(),
                "cookies": self.cookies_checkbox.isChecked(),
                "history": self.history_checkbox.isChecked(),
                "stealth": self.stealth_checkbox.isChecked(),
                "vpn": self.vpn_selector.currentText(),
                "adblock": self.adblock_checkbox.isChecked(),
                "fingerprint_protection": self.fingerprint_checkbox.isChecked(),
                "force_https": self.https_checkbox.isChecked(),
            }
            save_config(cfg)
            QMessageBox.information(self, "Gespeichert", "✅ Datenschutzeinstellungen gespeichert.")
            self.apply_privacy_settings(cfg["privacy"])

        def reset_privacy_defaults():
            for cb in [
                self.js_checkbox, self.cookies_checkbox, self.history_checkbox,
                self.adblock_checkbox, self.fingerprint_checkbox, self.https_checkbox
            ]:
                cb.setChecked(True)
            self.stealth_checkbox.setChecked(False)
            self.vpn_selector.setCurrentText("Kein VPN")

        save_btn.clicked.connect(save_privacy_settings)
        reset_btn.clicked.connect(reset_privacy_defaults)

        layout.addStretch()
        return page




    DOWNLOADS_FILE = "downloads.json"

    def create_downloads_page(self):
        from PySide6.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
            QCheckBox, QSpinBox, QFileDialog, QMessageBox, QFrame, QProgressBar
        )
        from PySide6.QtCore import Qt
        from pathlib import Path
        import os

        page = QWidget()
        page.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: white; }
            QLabel { color: #ddd; font-size: 14px; }
            QCheckBox {
                spacing: 10px; font-size: 14px; color: #ddd;
            }
            QCheckBox::indicator {
                width: 10px; 
                height: 10px;
                border-radius: 6px;
                border: 1px solid #555;
                background: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                background-color: white;
                image: url(icons/check.svg);
                border: 1px solid #333;
            }
        """)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(18)

        cfg = self.parent_window.config

        # --- Titel & Beschreibung ---
        title = QLabel("Download-Einstellungen")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #fff;")
        layout.addWidget(title)

        subtitle = QLabel("Steuere, wo Downloads gespeichert, geöffnet und verwaltet werden.")
        subtitle.setStyleSheet("color: #999; font-size: 13px; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # --- Speicherort ---
        current_path = cfg.get("download_folder", str(Path.home() / "Downloads"))
        self.download_path_label = QLabel(f"Aktueller Speicherort: <b>{current_path}</b>")
        self.download_path_label.setStyleSheet("color: #ccc; font-size: 13px; margin-top: 5px;")
        layout.addWidget(self.download_path_label)

        change_btn = QPushButton("Speicherort ändern")
        change_btn.setFixedHeight(36)
        change_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border-radius: 8px;
                border: 1px solid #444;
            }
            QPushButton:hover { border: 1px solid #61afef; background-color: #333; }
        """)
        change_btn.clicked.connect(self.change_download_folder)
        layout.addWidget(change_btn)

        # --- Optionen ---
        self.auto_save_checkbox = QCheckBox("Dateien ohne Nachfrage speichern")
        self.auto_save_checkbox.setChecked(cfg.get("auto_save_downloads", False))
        layout.addWidget(self.auto_save_checkbox)

        self.auto_open_checkbox = QCheckBox("Dateien nach Download automatisch öffnen")
        self.auto_open_checkbox.setChecked(cfg.get("auto_open_downloads", False))
        layout.addWidget(self.auto_open_checkbox)

        # --- Neue Funktion: Benachrichtigungen ---
        self.notify_checkbox = QCheckBox("Benachrichtigung bei Downloadabschluss anzeigen")
        self.notify_checkbox.setChecked(cfg.get("notify_download_complete", True))
        layout.addWidget(self.notify_checkbox)

        # --- Neue Funktion: Maximal erlaubte Größe ---
        layout.addWidget(QLabel("Maximale Dateigröße (MB):"))
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(1, 5000)
        self.max_size_spin.setValue(cfg.get("max_download_size_mb", 1000))
        layout.addWidget(self.max_size_spin)

        # --- Gleichzeitige Downloads ---
        layout.addWidget(QLabel("Maximale gleichzeitige Downloads:"))
        self.max_downloads_spinbox = QSpinBox()
        self.max_downloads_spinbox.setRange(1, 10)
        self.max_downloads_spinbox.setValue(cfg.get("max_parallel_downloads", 3))
        layout.addWidget(self.max_downloads_spinbox)

        # --- Fortschrittsanzeige ---
        self.download_progress = QProgressBar()
        self.download_progress.setValue(0)
        self.download_progress.setTextVisible(True)
        self.download_progress.setFormat("Fortschritt: %p%")
        self.download_progress.setStyleSheet("""
            QProgressBar {
                background-color: #2a2a2a;
                border-radius: 8px;
                border: 1px solid #444;
                height: 16px;
                text-align: center;
                color: white;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background-color: #61afef;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.download_progress)

        # --- Analyse des Speicherorts ---
        analyze_btn = QPushButton("Speicherplatz analysieren")
        analyze_btn.setFixedHeight(34)
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                border-radius: 6px;
                border: 1px solid #444;
            }
            QPushButton:hover {
                border: 1px solid #61afef;
                background-color: #333;
            }
        """)
        analyze_btn.clicked.connect(lambda: self.analyze_download_folder(current_path))
        layout.addWidget(analyze_btn)

        # --- Verlauf / Löschen ---
        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        reset_btn = QPushButton("↺ Standardwerte")
        reset_btn.setFixedHeight(36)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border-radius: 8px;
                border: 1px solid #444;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                border: 1px solid #ff6b6b;
            }
        """)

        save_btn = QPushButton("Änderungen speichern")
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2f6fef;
                color: white;
                border-radius: 8px;
                border: 1px solid #2a5ed7;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #478fff; }
        """)

        btn_layout.addWidget(reset_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()
        return page

        # 📁 Download-Ordner ändern
    def change_download_folder(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        folder = QFileDialog.getExistingDirectory(self, "Download-Ordner auswählen")
        if folder:
            self.download_path_label.setText(f"Aktueller Speicherort: <b>{folder}</b>")
            cfg = self.parent_window.config
            cfg["download_folder"] = folder
            save_config(cfg)
            QMessageBox.information(self, "Gespeichert", f"Download-Ordner geändert auf:\n{folder}")

    # ✅ Automatisch speichern aktivieren/deaktivieren
    def toggle_auto_save(self, state):
        cfg = self.parent_window.config
        cfg["auto_save_downloads"] = bool(state)
        save_config(cfg)

    # ✅ Automatisch öffnen aktivieren/deaktivieren
    def toggle_auto_open(self, state):
        cfg = self.parent_window.config
        cfg["auto_open_downloads"] = bool(state)
        save_config(cfg)

    # ⚙️ Maximale gleichzeitige Downloads speichern
    def update_max_downloads(self, value):
        cfg = self.parent_window.config
        cfg["max_parallel_downloads"] = value
        save_config(cfg)

    # 🗑️ Download-Verlauf löschen
    def clear_download_history(self):
        import os
        from PySide6.QtWidgets import QMessageBox
        if os.path.exists(DOWNLOADS_FILE):
            os.remove(DOWNLOADS_FILE)
            QMessageBox.information(self, "Gelöscht", "Download-Verlauf wurde erfolgreich gelöscht.")
        else:
            QMessageBox.information(self, "Info", "Kein Download-Verlauf vorhanden.")

    # 🧮 Speicherplatz-Analyse
    def analyze_download_folder(self, folder):
        import os
        from PySide6.QtWidgets import QMessageBox
        total_size = 0
        file_count = 0
        for root, _, files in os.walk(folder):
            for f in files:
                try:
                    total_size += os.path.getsize(os.path.join(root, f))
                    file_count += 1
                except:
                    pass
        mb = round(total_size / (1024 * 1024), 2)
        QMessageBox.information(self, "Analyse abgeschlossen", f"📁 {file_count} Dateien\n💾 Gesamtgröße: {mb} MB")

    # 📜 Download-Verlauf ansehen
    def show_download_history(self):
        from PySide6.QtWidgets import QMessageBox
        import os
        if not os.path.exists(DOWNLOADS_FILE):
            QMessageBox.information(self, "Keine Daten", "Noch keine Downloads vorhanden.")
            return
        with open(DOWNLOADS_FILE, "r", encoding="utf-8") as f:
            history = f.read()
        msg = QMessageBox()
        msg.setWindowTitle("Download-Verlauf")
        msg.setText(f"<pre>{history}</pre>")
        msg.exec()


    from PySide6.QtSvgWidgets import QSvgWidget
    from PySide6.QtCore import QSize, Qt
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy



    def create_extensions_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)

        # 🔷 SVG-Icon – mittig und mit leichtem Glow-Effekt
        icon = QSvgWidget("icons/puzzle.svg")
        icon.setFixedSize(QSize(100, 100))
        icon.setStyleSheet("""
            background: transparent;
            margin-bottom: 10px;
        """)

        # 📘 Titel
        title_label = QLabel("Extensions coming soon!")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
            margin-top: 10px;
            letter-spacing: 0.5px;
        """)

        # 📄 Beschreibung
        desc_label = QLabel(
            "This feature is currently in development.\n"
            "It will be available in one of the next updates."
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            font-size: 14px;
            color: #aaaaaa;
            line-height: 1.4;
        """)

        # 🧩 Alles schön mittig platzieren
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(icon, alignment=Qt.AlignHCenter)
        layout.addWidget(title_label, alignment=Qt.AlignHCenter)
        layout.addWidget(desc_label, alignment=Qt.AlignHCenter)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 🌌 Hintergrund-Styling im Browser-Stil
        page.setStyleSheet("""
            QWidget {
                background-color: #1b1b1b;
                border-radius: 12px;
            }
        """)

        return page



    

    SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q=",
    "DuckDuckGo": "https://duckduckgo.com/?q=",
    "Bing": "https://www.bing.com/search?q=",
    "Ecosia": "https://www.ecosia.org/search?q=",
    "Yahoo": "https://search.yahoo.com/search?p=",
}


def show_source_tab(self, html):
    src_tab = BrowserTab()
    src_tab.view.setHtml(
        f"<pre style='white-space: pre-wrap; color:white; background:#1e1e1e; padding:10px;'>{html.replace('<', '&lt;').replace('>', '&gt;')}</pre>"
    )
    self.parent().addTab(src_tab, "Seitenquelle")

import os, json, sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)

USER_DATA_FILE = "user_data.json"
SESSION_FILE = "session.json"   # <--- speichert, ob jemand eingeloggt ist


# ====================== Hilfsfunktionen ======================

def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def save_session(username):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({"username": username}, f)

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def is_logged_in():
    return os.path.exists(SESSION_FILE)


# ====================== Login-Fenster ======================

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSizePolicy, QSpacerItem, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QIcon, QPixmap

# Falls du sie in separater Datei hast:
# from your_module import RegisterWindow, MiniBrowser, load_user_data, save_session


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WHY – Login")
        self.setFixedSize(420, 420)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # ========== STYLE ==========
        self.setStyleSheet("""
            QWidget {
                background-color: #1b1b1b;
                color: #f0f0f0;
                font-family: 'Segoe UI';
            }
            QLineEdit {
                background-color: #222;
                border: 1.5px solid #333;
                border-radius: 8px;
                padding: 10px 12px;
                color: #f5f5f5;
                font-size: 12px;
                min-height: 13px;
            }
            QLineEdit:focus {
                border: 1.5px solid #4c8bf5;
                background-color: #262626;
            }
            QPushButton {
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
                font-size: 11px;
                transition: 0.2s;
                min-height: 13px;
            }
            QPushButton:hover {
                background-color: #333;
            }
            QPushButton#register {
                background-color: transparent;
                border: 1px solid #444;
                color: #bbb;
                font-size: 11px;
                min-height: 13px;
            }
            QPushButton#register:hover {
                border: 1px solid white;
                color: white;
            }
            QLabel#title {
                font-size: 22px;
                font-weight: bold;
                color: white;
                margin-top: 8px;
            }
            QLabel#subtitle {
                font-size: 13px;
                color: #888;
                margin-bottom: 10px;
            }
            QWidget#TitleBar {
                background-color: #1a1a1a;
                border-bottom: 1px solid #2a2a2a;
            }
            QLabel#TitleLabel {
                color: #f0f0f0;
                font-size: 13px;
                font-weight: 600;
                min-height: 8px;
            }
            QPushButton.TitleBtn {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 6px;
                min-height: 8px;
                
            }
            QPushButton.TitleBtn:hover {
                background-color: #333;
            }
            QPushButton#CloseButton:hover {
                background-color: #e74c3c;
            }
        """)

        # ========== LAYOUT ==========
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === Titlebar ===
        self.title_bar = QWidget()
        self.title_bar.setObjectName("TitleBar")

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 4, 10, 4)
        title_layout.setSpacing(8)

        title_icon = QLabel()
        title_icon.setPixmap(QPixmap("icons/browser.svg").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_layout.addWidget(title_icon)

        title_label = QLabel("WHY Browser – Login")
        title_label.setObjectName("TitleLabel")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        self.btn_min = QPushButton()
        self.btn_min.setIcon(QIcon("icons/minimize.svg"))
        self.btn_min.setIconSize(QSize(14, 14))
        self.btn_min.setToolTip("Minimieren")

        self.btn_close = QPushButton()
        self.btn_close.setObjectName("CloseButton")
        self.btn_close.setIcon(QIcon("icons/close.svg"))
        self.btn_close.setIconSize(QSize(14, 14))
        self.btn_close.setToolTip("Schließen")

        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_close.clicked.connect(self.close)

        title_layout.addWidget(self.btn_min)
        title_layout.addWidget(self.btn_close)
        main_layout.addWidget(self.title_bar)

        # === Content ===
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignCenter)

        icon = QSvgWidget("icons/user.svg")
        icon.setFixedSize(QSize(80, 80))
        layout.addWidget(icon, alignment=Qt.AlignCenter)

        title = QLabel("Willkommen bei WHY Browser")
        title.setObjectName("title")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        subtitle = QLabel("Melde dich an, um fortzufahren")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle, alignment=Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Benutzername")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Passwort")
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)

        # === Buttons ===
        self.login_btn = QPushButton("Einloggen")
        layout.addWidget(self.login_btn)

        self.register_btn = QPushButton("Ich bin neu hier")
        self.register_btn.setObjectName("register")
        layout.addWidget(self.register_btn)

        # 🔹 Signal-Verbindungen
        self.login_btn.clicked.connect(self.handle_login)
        self.register_btn.clicked.connect(self.open_register)

        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addWidget(content)

    # ======== Login-Logik ========
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        data = load_user_data()

        if not data or data.get("username") != username or data.get("password") != password:
            QMessageBox.warning(self, "Fehler", "Falscher Benutzername oder Passwort!")
            return

        save_session(username)
        QMessageBox.information(self, "Erfolg", f"Willkommen zurück, {username}!")
        self.start_browser()

    # ======== Browser starten ========
    def start_browser(self):
        self.close()
        self.browser = MiniBrowser()
        self.browser.show()

    # ======== Registrierung öffnen ========
    def open_register(self):
        self.hide()
        self.register_window = RegisterWindow(self)
        self.register_window.show()

    # ======== Fensterbewegung ========
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.title_bar.underMouse():
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, "drag_pos"):
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None




# ====================== REGISTER ======================
class RegisterWindow(QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.setWindowTitle("WHY – Registrierung")
        self.setFixedSize(420, 480)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # ========== GLOBALER STYLE ==========
        self.setStyleSheet("""
            QWidget {
                background-color: #1b1b1b;
                color: #f0f0f0;
                font-family: 'Segoe UI';
            }
            QLineEdit {
                background-color: #222;
                border: 1.5px solid #333;
                border-radius: 8px;
                padding: 10px 12px;
                color: #f5f5f5;
                font-size: 12px;
                min-height: 13px;
            }
            QLineEdit:focus {
                border: 1.5px solid #4c8bf5;
                background-color: #262626;
            }
            QPushButton {
                background-color: #2f6fef;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4c8bf5;
            }
            QPushButton#register {
                background-color: transparent;
                border: 1px solid #444;
                color: #bbb;
            }
            QPushButton#register:hover {
                border: 1px solid white;
                color: white;
            }
            QLabel#title {
                font-size: 22px;
                font-weight: bold;
                color: white;
                margin-top: 8px;
            }
            QLabel#subtitle {
                font-size: 13px;
                color: #888;
                margin-bottom: 2px;
            }
            QWidget#TitleBar {
                background-color: #1a1a1a;
                border-bottom: 1px solid #2a2a2a;
            }
            QLabel#TitleLabel {
                color: #f0f0f0;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 4px;
                min-height: 17px;
                font-size: 12px;
                min-widht: 10px ; 
            }
            QPushButton:hover {
                background-color: #333;
            }
            QPushButton#CloseButton:hover {
                background-color: #e74c3c;
            }
        """)

        # ==================== HAUPTLAYOUT ====================
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==================== TITLE BAR ====================
        self.title_bar = QWidget()
        self.title_bar.setObjectName("TitleBar")

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 4, 10, 4)
        title_layout.setSpacing(8)

        title_icon = QLabel()
        title_icon.setPixmap(QPixmap("icons/browser.svg").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        title_layout.addWidget(title_icon)

        title_label = QLabel("WHY Browser – Registrierung")
        title_label.setObjectName("TitleLabel")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # --- Buttons ---
        self.btn_min = QPushButton()
        self.btn_min.setIcon(QIcon("icons/minimize.svg"))
        self.btn_min.setIconSize(QSize(12, 12))
        self.btn_min.setToolTip("Minimieren")
        self.btn_min.clicked.connect(self.showMinimized)

        self.btn_close = QPushButton()
        self.btn_close.setObjectName("CloseButton")
        self.btn_close.setIcon(QIcon("icons/close.svg"))
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.setToolTip("Schließen")
        self.btn_close.clicked.connect(self.close)

        title_layout.addWidget(self.btn_min)
        title_layout.addWidget(self.btn_close)

        main_layout.addWidget(self.title_bar)

        # ==================== INHALT ====================
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignCenter)

        # --- Icon ---
        icon = QSvgWidget("icons/user.svg")
        icon.setFixedSize(QSize(80, 80))
        layout.addWidget(icon, alignment=Qt.AlignCenter)

        # --- Titel ---
        title = QLabel("Konto erstellen")
        title.setObjectName("title")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        subtitle = QLabel("Erstelle dein persönliches WHY-Konto")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle, alignment=Qt.AlignCenter)

        # --- Eingabefelder ---
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("E-Mail-Adresse")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Benutzername")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Passwort")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.birth_input = QLineEdit()
        self.birth_input.setPlaceholderText("Geburtsdatum (z. B. 01.01.2000)")

        for widget in [self.email_input, self.username_input, self.password_input, self.birth_input]:
            layout.addWidget(widget)

        # --- Buttons ---
        register_btn = QPushButton("Registrieren")
        register_btn.clicked.connect(self.handle_register)
        layout.addWidget(register_btn)

        back_btn = QPushButton("Zurück zum Login")
        back_btn.setObjectName("register")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)

        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

        main_layout.addWidget(content)

    # ==================== LOGIK ====================
    def handle_register(self):
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        birthday = self.birth_input.text().strip()

        if not all([email, username, password, birthday]):
            QMessageBox.warning(self, "Fehler", "Bitte alle Felder ausfüllen!")
            return

        save_user_data({
            "email": email,
            "username": username,
            "password": password,
            "birthday": birthday
        })
        save_session(username)
        QMessageBox.information(self, "Erfolg", "Registrierung erfolgreich! Du wirst eingeloggt.")
        self.login_window.close()
        self.close()
        self.login_window.start_browser()

    def go_back(self):
        self.close()
        self.login_window.show()

    # ==================== FENSTER BEWEGBAR ====================
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.title_bar.underMouse():
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, "drag_pos"):
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None




# --- Custom DevTools (eigene Implementierung) ---


from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide6.QtCore import QDateTime

class SimpleRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.log = []

    def interceptRequest(self, info):
        try:
            url = info.requestUrl().toString()
            ts = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            self.log.append({"url": url, "time": ts})
        except Exception:
            pass






# DevTools Widget
class DevToolsWidget(QWidget):
    closed = Signal()

    def __init__(self, target_view: QWebEngineView, parent=None, interceptor=None):
        super().__init__(parent)
        self.setWindowTitle("WHY DevTools")
        self.resize(900, 520)
        self.target_view = target_view
        self.interceptor = interceptor

        # --- Hauptlayout ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # ---------- Header mit Close-Button ----------
        header = QHBoxLayout()
        title = QLabel("")
        title.setStyleSheet("font-weight: bold; font-size: 15px; color: white; background: none;")
        header.addWidget(title)
        header.addStretch()

        # ✅ Runder Close-Button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: none;
                color: white;
                font-size: 16px;
                border-radius: 14px;
                
            }
            QPushButton:hover {
                background-color: #ff4d4d;
            }
        """)
        close_btn.clicked.connect(self.hide)
        header.addWidget(close_btn)

        layout.addLayout(header)

        # ---------- Tabs ----------
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # ========== CONSOLE TAB ==========
        console_tab = QWidget()
        console_layout = QVBoxLayout(console_tab)
        console_layout.addWidget(QLabel("Console (JavaScript & Logs):"))
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_input = QLineEdit()
        self.console_input.setPlaceholderText("JS ausführen (Enter drücken)...")
        console_layout.addWidget(self.console_output)
        console_layout.addWidget(self.console_input)
        self.tabs.addTab(console_tab, "Console")

        # ========== ELEMENTS TAB ==========
        elements_tab = QWidget()
        elements_layout = QVBoxLayout(elements_tab)
        self.html_view = QTextEdit()
        self.html_view.setReadOnly(True)
        btn_reload_html = QPushButton("HTML neu laden")
        btn_inspect = QPushButton("Inspect Element")
        btn_reload_html.clicked.connect(self.load_page_html)
        btn_inspect.clicked.connect(self.start_inspect_mode)
        button_bar = QHBoxLayout()
        button_bar.addWidget(btn_reload_html)
        button_bar.addWidget(btn_inspect)
        elements_layout.addLayout(button_bar)
        elements_layout.addWidget(self.html_view)
        self.tabs.addTab(elements_tab, "Elements")

        # ========== NETWORK TAB ==========
        network_tab = QWidget()
        net_layout = QVBoxLayout(network_tab)
        net_layout.addWidget(QLabel("Netzwerk-Anfragen:"))
        self.net_list = QListWidget()
        net_layout.addWidget(self.net_list)
        self.tabs.addTab(network_tab, "Network")

        # ========== SERVER INFO TAB ==========
        self.server_tab = QWidget()
        s_layout = QVBoxLayout(self.server_tab)
        self.server_info_label = QLabel("Noch keine Serverinformationen geladen.")
        s_layout.addWidget(self.server_info_label)
        self.tabs.addTab(self.server_tab, "Server Info")

        # Events
        self.console_input.returnPressed.connect(self.run_js_from_input)

        # JavaScript console hook
        try:
            page = self.target_view.page()
            page.javaScriptConsoleMessage = self._on_js_console_message
        except Exception:
            pass

        # Initialisiere Netzwerkanfragen
        if self.interceptor:
            self.refresh_network_list()

        # Beim Öffnen aktualisieren
        self.showEvent = self.on_show

    def init_tabs(self):
            # ========== CONSOLE TAB ==========
            console_tab = QWidget()
            console_layout = QVBoxLayout(console_tab)
            console_layout.addWidget(QLabel("Console (JavaScript & Logs):"))
            self.console_output = QTextEdit()
            self.console_output.setReadOnly(True)
            self.console_input = QLineEdit()
            self.console_input.setPlaceholderText("JS ausführen (Enter drücken)...")
            console_layout.addWidget(self.console_output)
            console_layout.addWidget(self.console_input)
            self.tabs.addTab(console_tab, "Console")
            # ========== ELEMENTS TAB ==========
            elements_tab = QWidget()
            elements_layout = QVBoxLayout(elements_tab)
            self.html_view = QTextEdit()
            self.html_view.setReadOnly(True)
            btn_reload_html = QPushButton("🔄 HTML neu laden")
            btn_inspect = QPushButton("🕵️ Inspect Element")
            btn_reload_html.clicked.connect(self.load_page_html)
            btn_inspect.clicked.connect(self.start_inspect_mode)
            button_bar = QHBoxLayout()
            button_bar.addWidget(btn_reload_html)
            button_bar.addWidget(btn_inspect)
            elements_layout.addLayout(button_bar)
            elements_layout.addWidget(self.html_view)
            self.tabs.addTab(elements_tab, "Elements")
            # ========== NETWORK TAB ==========
            network_tab = QWidget()
            net_layout = QVBoxLayout(network_tab)
            net_layout.addWidget(QLabel("Netzwerk-Anfragen:"))
            self.net_list = QListWidget()
            net_layout.addWidget(self.net_list)
            self.tabs.addTab(network_tab, "Network")
            # ========== SERVER INFO TAB ==========
            self.server_tab = QWidget()
            s_layout = QVBoxLayout(self.server_tab)
            self.server_info_label = QLabel("Noch keine Serverinformationen geladen.")
            s_layout.addWidget(self.server_info_label)
            self.tabs.addTab(self.server_tab, "Server Info")


    # ---------- Console ----------
    def _on_js_console_message(self, level, message, line_number, source_id):
        ts = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.console_output.append(f"[{ts}] {message}")

    def run_js_from_input(self):
        code = self.console_input.text().strip()
        if not code:
            return
        self.console_output.append(f">>> {code}")
        def callback(result):
            self.console_output.append(f"==> {repr(result)}")
        self.target_view.page().runJavaScript(code, callback)
        self.console_input.clear()

    # ---------- Elements ----------
    def load_page_html(self):
        def got_html(html):
            self.html_view.setPlainText(html)
        self.target_view.page().toHtml(got_html)

    def start_inspect_mode(self):
        js = """
        (function(){
            function handleClick(ev){
                ev.preventDefault();
                ev.stopPropagation();
                var el = ev.target;
                var html = el.outerHTML;
                document.removeEventListener('click', handleClick, true);
                return html;
            }
            document.addEventListener('click', handleClick, true);
            'INSPECT_READY';
        })();
        """
        def after_ready(_):
            self.console_output.append("[Inspect] Klicke auf ein Element in der Seite...")
            get_clicked_js = """
            new Promise(function(resolve){
                function once(ev){
                    ev.preventDefault(); ev.stopPropagation();
                    document.removeEventListener('click', once, true);
                    resolve(ev.target.outerHTML);
                }
                document.addEventListener('click', once, true);
            });
            """
            self.target_view.page().runJavaScript(get_clicked_js, lambda html: self.html_view.setPlainText(html))
        self.target_view.page().runJavaScript(js, after_ready)

    # ---------- Network ----------
    def refresh_network_list(self):
        if not self.interceptor or not hasattr(self.interceptor, "log"):
            return
        self.net_list.clear()
        for entry in reversed(self.interceptor.log[-200:]):
            item = QListWidgetItem(f"{entry['time']}  |  {entry['url']}")
            self.net_list.addItem(item)

    # ---------- Server Info ----------
    def update_server_info(self, url):
        """Lädt einfache Server-Infos für die aktuelle Seite."""
        try:
            import requests, socket, ssl
            parsed = QUrl(url)
            host = parsed.host()
            ip = socket.gethostbyname(host)
            info_text = f"<b>URL:</b> {url}<br><b>Host:</b> {host}<br><b>IP:</b> {ip}"
            try:
                cert = ssl.get_server_certificate((host, 443))
                info_text += "<br><b>SSL:</b> Ja (Zertifikat gefunden)"
            except Exception:
                info_text += "<br><b>SSL:</b> Nein oder nicht erreichbar"
            self.server_info_label.setText(info_text)
        except Exception as e:
            self.server_info_label.setText(f"Fehler beim Laden der Serverinfo: {e}")

    # ---------- Show ----------
    def on_show(self, event):
        """Beim Anzeigen des Fensters aktualisieren"""
        self.refresh_network_list()
        try:
            current_url = self.target_view.url().toString()
            self.update_server_info(current_url)
        except Exception:
            pass

from PySide6.QtCore import QObject, Slot, Signal

class BrowserBridge(QObject):
    searchEngineChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    @Slot(result=str)
    def get_search_engine(self):
        """Wird vom HTML aufgerufen, um die aktuelle Suchmaschine zu erfahren"""
        cfg = getattr(self.parent, "config", {})
        engine = cfg.get("search_engine", "duckduckgo")
        return engine

    @Slot(str)
    def set_search_engine(self, engine):
        """Kann optional verwendet werden, falls du vom JS aus ändern willst"""
        if hasattr(self.parent, "config"):
            self.parent.config["search_engine"] = engine
        self.searchEngineChanged.emit(engine)

from PySide6.QtCore import QRunnable, QThreadPool

class DownloadTask(QRunnable):
    def __init__(self, url, path):
        super().__init__()
        self.url = url
        self.path = path

    def run(self):
        import requests
        with open(self.path, "wb") as f:
            f.write(requests.get(self.url).content)
        print(f"[✓] Download complete: {self.url}")

# Beispiel-Aufruf:
pool = QThreadPool.globalInstance()
pool.start(DownloadTask("https://example.com/file.zip", "file.zip"))

# ===============================================================
# === AUTO-FILL / PASSWORD MANAGER ==============================
# ===============================================================
import json, os
from cryptography.fernet import Fernet
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QHBoxLayout

class AutoFillManager:
    def __init__(self, browser):
        self.browser = browser
        self.file_path = "user_data/autofill.json"
        self.key_path = "user_data/key.key"
        self._ensure_files()

    def _ensure_files(self):
        os.makedirs("user_data", exist_ok=True)
        if not os.path.exists(self.key_path):
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as f:
                f.write(key)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({"accounts": []}, f)

    def _get_cipher(self):
        key = open(self.key_path, "rb").read()
        return Fernet(key)

    def save_login(self, url, email, password):
        cipher = self._get_cipher()
        with open(self.file_path, "r") as f:
            data = json.load(f)

        enc_email = cipher.encrypt(email.encode()).decode()
        enc_pass = cipher.encrypt(password.encode()).decode()
        data["accounts"].append({"url": url, "email": enc_email, "password": enc_pass})

        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    def get_logins_for(self, url):
        cipher = self._get_cipher()
        with open(self.file_path, "r") as f:
            data = json.load(f)

        matches = []
        for acc in data.get("accounts", []):
            if acc["url"] in url:
                email = cipher.decrypt(acc["email"].encode()).decode()
                pw = cipher.decrypt(acc["password"].encode()).decode()
                matches.append((email, pw))
        return matches


# ===============================================================
# === AUTO-FILL POPUP (VISUELLES MENÜ) ==========================
# ===============================================================
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

class AutoFillPopup(QDialog):
    def __init__(self, parent, url, email, password):
        super().__init__(parent)
        self.setWindowTitle("Login-Daten speichern?")
        self.setFixedSize(320, 180)
        self.url = url
        self.email = email
        self.password = password

        self.setStyleSheet("""
            QDialog {
                background-color: #1f1f1f;
                border: 1px solid #333;
                border-radius: 8px;
                color: white;
                font-family: 'Segoe UI';
            }
            QLabel {
                color: #ccc;
                font-size: 13px;
            }
            QPushButton {
                background-color: #2f6fef;
                border: none;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4c8bf5;
            }
            QPushButton#cancel {
                background-color: #333;
                color: #ccc;
            }
            QPushButton#cancel:hover {
                background-color: #444;
                color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        layout.addWidget(QLabel(f"<b>Website:</b> {url}"))
        layout.addWidget(QLabel(f"E-Mail / Benutzername: {email or '(leer)'}"))
        layout.addWidget(QLabel("Möchtest du diese Login-Daten speichern?"))

        btns = QHBoxLayout()
        save_btn = QPushButton("Speichern")
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setObjectName("cancel")

        save_btn.clicked.connect(self.save_credentials)
        cancel_btn.clicked.connect(self.close)

        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def save_credentials(self):
        data = load_autofill_data()
        data[self.url] = {"email": self.email, "password": self.password}
        save_autofill_data(data)
        self.accept()




# -------------------- Mini Browser --------------------
class MiniBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        # Suchmaschinen-Einstellungen laden
        self.config = self.load_config()  # falls du sie noch nicht geladen hast
        self.search_engine = self.config.get("search_engine", "duckduckgo")
        self.search_url = self.config.get("search_engines", {}).get(
            self.search_engine, "https://duckduckgo.com/?q={}"
        )
        


        from PySide6.QtWebChannel import QWebChannel

        # Beispielhafte Reihenfolge
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("file:///path/to/homepage.html"))  # oder dein Startbildschirm

# ... nachdem self.browser erstellt wurde:
        self.channel = QWebChannel(self.browser.page())
        self.browserBridge = BrowserBridge(self)
        self.channel.registerObject("browserApi", self.browserBridge)
        self.browser.page().setWebChannel(self.channel)
        self.autofill = AutoFillManager(self)

        
        if hasattr(self, "tabs") and self.tabs.count() > 0:
            current_tab = self.tabs.currentWidget()
            if current_tab and hasattr(current_tab, "view"):
                url = current_tab.view.url().toString()
            else:
                url = "https://www.google.com"
        else:
            url = "https://www.google.com"

# Lade gespeicherte Anmeldedaten oder leere Strings
        credentials = load_autofill_data()  # eigene Funktion, lädt dict aus JSON
        site_data = credentials.get(url, {})
        email = site_data.get("email", "")
        password = site_data.get("password", "")

        # --- WEBVIEW INITIALISIEREN ---



        # Browser-Inhalt wird angezeigt
        self.setCentralWidget(self.browser)

        # ---- DEINE STARTSEITE ----
        self.browser.setUrl(QUrl.fromLocalFile(os.path.abspath("homepage.html")))

        # Autofill triggern wenn Seite fertig geladen
        self.browser.loadFinished.connect(self.check_autofill_data)

        # Beim Seitenaufruf prüfen, ob gespeicherte Login-Daten existieren
        self.browser.loadFinished.connect(self.check_autofill_data)

        AutoFillPopup(self, url, email, password)



        



        self.setWindowTitle("WHY Browser")
        self.resize(1200, 800)
        self.config = load_config()

        self.interceptor = NetworkInterceptor()  # Erstelle den Interceptor
        profile = QWebEngineProfile.defaultProfile()  # Hole das Standardprofil
        profile.setUrlRequestInterceptor(self.interceptor)  # Aktiviere Interceptor
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)




        

        # -------------------- Toolbar --------------------
        navtb = QToolBar("Navigation")


        # ==================== Custom Title Bar ====================
        self.title_bar = QWidget()
        self.title_bar.setObjectName("TitleBar")

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 2, 10, 2)
        title_layout.setSpacing(6)

        self.title_label = QLabel("WHY Browser")
        self.title_label.setObjectName("TitleLabel")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # Buttons
        from PySide6.QtGui import QIcon, QPixmap

        self.btn_min = QPushButton()
        self.btn_min.setIcon(QIcon("icons/minimize.svg"))
        self.btn_min.setIconSize(QSize(14, 14))

        self.btn_max = QPushButton()
        self.btn_max.setIcon(QIcon("icons/maximize.svg"))
        self.btn_max.setIconSize(QSize(14, 14))

        self.btn_close = QPushButton()
        self.btn_close.setIcon(QIcon("icons/close.svg"))
        self.btn_close.setIconSize(QSize(14, 14))


        for btn in (self.btn_min, self.btn_max, self.btn_close):
            btn.setFixedSize(12, 32)  # ⬅️ quadratisch!
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2a2a2a;
                    border: 0px solid #3a3a3a;
                    border-radius: 6px;
                    padding: 0px;
                    max-width:30px;
                    max-height:30px;
                    min-height:30px;
                    min-width:30px;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
            """)

            self.btn_close.setStyleSheet("""
    QPushButton {
        background-color: #2a2a2a;
        border: 0px solid #3a3a3a;
        border-radius: 6px;
        padding: 0px;
        max-width:30px;
        max-height:30px;
        min-height:30px;
        min-width:30px;
    }
    QPushButton:hover {
        background-color: #e74c3c;
    }
""")

            btn.setCursor(Qt.PointingHandCursor)



        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(lambda: self.showNormal() if self.isMaximized() else self.showMaximized())
        self.btn_close.clicked.connect(self.close)

        title_layout.addWidget(self.btn_min)
        title_layout.addWidget(self.btn_max)
        title_layout.addWidget(self.btn_close)

        # Container Layout (Titlebar + Toolbar)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(self.title_bar)

        container_layout.addWidget(navtb)
        self.setMenuWidget(container)  # <- ersetzt setCentralWidget für Toolbar

        

        


        # -------------------- Toolbar --------------------
        

        # --- Back ---
        self.back_button = QToolButton()
        self.back_button.setIcon(QIcon("icons/back.svg"))
        self.back_button.setIconSize(QSize(20, 20))
        self.back_button.setToolTip("Zurück")
        self.back_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.back_button.clicked.connect(self.go_back)  # ✅ Funktion verknüpft!
        navtb.addWidget(self.back_button)

        # --- Forward ---
        self.forward_button = QToolButton()
        self.forward_button.setIcon(QIcon("icons/forward.svg"))
        self.forward_button.setIconSize(QSize(20, 20))
        self.forward_button.setToolTip("Vorwärts")
        self.forward_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.forward_button.clicked.connect(self.go_forward)  # ✅
        navtb.addWidget(self.forward_button)

        # --- Reload ---
        self.reload_button = QToolButton()
        self.reload_button.setIcon(QIcon("icons/reload.svg"))
        self.reload_button.setIconSize(QSize(20, 20))
        self.reload_button.setToolTip("Neu laden")
        self.reload_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.reload_button.clicked.connect(self.reload_page)  # ✅
        navtb.addWidget(self.reload_button)

        # --- Home ---
        self.home_button = QToolButton()
        self.home_button.setIcon(QIcon("icons/home.svg"))
        self.reload_icon = QPixmap("icons/reload.svg")
        self.rotating = False
        self.home_button.setIconSize(QSize(20, 20))
        self.home_button.setToolTip("Startseite")
        self.home_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.home_button.clicked.connect(self.go_home)  # ✅
        navtb.addWidget(self.home_button)




        navtb.addSeparator()


        # Reagiere auf verschobene Tabs
        

        from PySide6.QtWebEngineCore import QWebEngineSettings

        self.browser.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.browser.page().fullScreenRequested.connect(self.handle_fullscreen)




        
        from PySide6.QtGui import QIcon

        # === URL-Leiste mit überlagertem Stern ===
        url_container = QWidget()
        url_container.setStyleSheet("background: transparent;")
        url_layout = QHBoxLayout(url_container)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(0)

        # Eingabefeld
        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("URL oder Suchbegriff eingeben...")
        self.urlbar.returnPressed.connect(self.on_url_entered)
        self.urlbar.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                border: 1.5px solid #3b3b3b;
                border-radius: 8px;
                padding: 6px 36px 6px 10px; /* Platz rechts für Stern */
                color: #e6e6e6;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1.5px solid #white;
                background-color: #222;
            }
        """)

        # Überlagerter Stern-Button
        self.fav_btn = QToolButton(self.urlbar)
        self.fav_btn.setIcon(QIcon("icons/star_empty.svg"))
        self.fav_btn.setToolTip("Zu Favoriten hinzufügen")
        self.fav_btn.setCursor(Qt.PointingHandCursor)
        self.fav_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: none;
                padding: 0px;
                z-index: 2;
                margin-top: -2px;
                margin-right: -2px ; 
            }
            QToolButton:hover {
                transform: scale(1.1);
            }
        """)
        self.fav_btn.setGeometry(self.urlbar.width() - 30, 4, 22, 22)
        self.fav_btn.raise_()  # z-index wirklich anwenden

        # Repositioniere Stern beim Resizen der URL-Leiste
        def reposition_star():
            self.fav_btn.move(self.urlbar.width() - 30, (self.urlbar.height() - 22) // 2)
        self.urlbar.resizeEvent = lambda e: (reposition_star(), QLineEdit.resizeEvent(self.urlbar, e))

        self.fav_btn.clicked.connect(self.toggle_favorite)

        url_layout.addWidget(self.urlbar)
        url_container.setFixedHeight(34)
        navtb.addWidget(url_container)

        self.favorites = self.load_favorites()







        # Settings Sidebar
        self.settings_sidebar = ResponsiveSidebar(self)
        self.settings_sidebar.hide()



        # SETTINGS BUTTON (SVG)
        self.settings_button = QToolButton()
        self.settings_button.setIcon(QIcon("icons/settings.svg"))  # dein SVG-Icon
        self.settings_button.setIconSize(QSize(20, 20))
        self.settings_button.setToolTip("Einstellungen")
        self.settings_button.setObjectName("SettingsButton")
        self.settings_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.settings_button.clicked.connect(self.toggle_settings_sidebar)
        navtb.addWidget(self.settings_button)

        # NEW TAB BUTTON
        self.new_tab_button = QToolButton()
        self.new_tab_button.setIcon(QIcon("icons/plus.svg"))  # dein SVG-Icon
        self.new_tab_button.setIconSize(QSize(30, 30))
        self.new_tab_button.setToolTip("Neuer Tab")
        self.new_tab_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.new_tab_button.clicked.connect(lambda checked=False: self.add_tab(None))
        navtb.addWidget(self.new_tab_button)

                # --- MENU BUTTON ---
        self.menu_button = QToolButton()
        self.menu_button.setIcon(QIcon("icons/menu.svg"))
        self.menu_button.setIconSize(QSize(22, 22))
        self.menu_button.setToolTip("Hauptmenü")
        self.menu_button.clicked.connect(self.toggle_main_menu_popup)  # <-- Wichtig!
        navtb.addWidget(self.menu_button)



        




        # -------------------- Tabs --------------------
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)          # moderner Look
        self.tabs.setElideMode(Qt.ElideRight)   # lange Titel kürzen
        self.tabs.setTabsClosable(True)
        # === Stil für Tabs & Close-Button ==
  # oder 20, wenn du’s größer willst
        from PySide6.QtWidgets import QTabBar

        tabbar = self.tabs.tabBar()
        tabbar.setStyleSheet("""
        QTabBar::close-button {
            image: url('icons/close_tab.svg');
            width: 20px;
            height: 20px;
        }
        QTabBar::close-button:hover {
            image: url('icons/close_tab_hover.svg');
        }
        """)

        self.tabs.setMovable(True)  # ✅ Tabs können verschoben werden
        self.tabs.setElideMode(Qt.ElideRight)  # ✅ Titel kürzen, wenn zu lang
        self.tabs.setDocumentMode(True)  # ✅ moderner Look (wie Chrome)
        self.tabs.setTabBarAutoHide(False)
        self.tabs.tabCloseRequested.connect(self.close_tab)  # Tabs bleiben sichtbar
        self.setCentralWidget(self.tabs)

        # Downloads aktivieren
        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.handle_download)

        # Download-Historie
        self.downloads = self.load_downloads()

        # Favoriten laden
        self.favorites = self.load_favorites()

        self.homepage_path = os.path.join(os.getcwd(), "homepage.html")
        self.homepage_url = QUrl.fromLocalFile(self.homepage_path)
        homepage_path = os.path.abspath("homepage.html")
        homepage_url = QUrl.fromLocalFile(homepage_path)


        


        
        # Add first tab
        # Add first tab
        open_tabs = self.config.get("open_tabs", [])
        if open_tabs:
            for url in open_tabs:
                homepage_path = os.path.abspath("homepage.html")
                homepage_url = QUrl.fromLocalFile(homepage_path)

            active_index = self.config.get("active_tab", 0)
            self.tabs.setCurrentIndex(active_index)
 
        self.restore_tabs()

        # Suchmaschine aus Config laden
        self.search_engine = self.config.get("search_engine", "duckduckgo")
        self.search_url = self.config["search_engines"].get(self.search_engine, "https://duckduckgo.com/?q={}")

    def load_config(self):
        """Lädt die Browser-Konfiguration (z. B. Suchmaschinen, Startseite usw.)"""
        default_config = {
            "homepage": "file:///" + os.path.abspath("homepage.html"),
            "search_engine": "duckduckgo",
            "search_engines": {
                "duckduckgo": "https://duckduckgo.com/?q={}",
                "google": "https://www.google.com/search?q={}",
                "bing": "https://www.bing.com/search?q={}",
                "yahoo": "https://search.yahoo.com/search?p={}",
                "ecosia": "https://www.ecosia.org/search?q={}"
            }
        }

        if os.path.exists("config.json"):
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print("⚠️ Fehler beim Laden der config.json:", e)

        return default_config
    
    from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile

    def enable_browser_performance():
        profile = QWebEngineProfile.defaultProfile()

        # Cache & Persistenz
        profile.setCachePath("cache/")
        profile.setPersistentStoragePath("storage/")
        profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        profile.setHttpCacheMaximumSize(512 * 1024 * 1024)  # 512 MB Cache

        # GPU & Rendering
        s = QWebEngineSettings.defaultSettings()
        s.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        s.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        s.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        s.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        s.setAttribute(QWebEngineSettings.PluginsEnabled, True)

        # Ladeoptimierung
        profile.setHttpUserAgent("WHY-Browser/1.0 (Superfast Mode)")
        print("[✓] Browser performance optimizations enabled")


    from PySide6.QtCore import QTimer

    def init_ui(self):
        # splash screen oder startfenster anzeigen
        QTimer.singleShot(0, self.finish_startup)

    def finish_startup(self):
        self.init_browser()
        self.init_toolbar()
        self.show()

    def check_autofill_data(self):
        url = self.webview.url().toString()
        credentials = load_autofill_data()
        site_data = credentials.get(url, {})

        if site_data:
            # Popup anzeigen mit gespeicherten Daten
            email = site_data.get("email", "")
            password = site_data.get("password", "")
            AutoFillPopup(self, url, email, password).exec()


    def handle_fullscreen(self, request):
        if request.toggleOn():
            self.showFullScreen()
            request.accept()
        else:
            self.showNormal()
            request.accept()

    def register_as_default_browser(self):
        import winreg
        import sys, os
        import subprocess

        exe = os.path.abspath(sys.argv[0])
        prog_id = "WHYBrowserHTML"

        try:
            # === 1. Browser registrieren ===
            key_path = rf"Software\Classes\{prog_id}"
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)

            # Anzeigename
            winreg.SetValue(key, "", winreg.REG_SZ, "WHY Browser HTML Document")
            winreg.SetValueEx(key, "FriendlyTypeName", 0, winreg.REG_SZ, "WHY Browser")

            # Icon
            winreg.SetValueEx(key, "DefaultIcon", 0, winreg.REG_SZ, f'"{exe}",0')

            # Öffnen-Kommando
            cmd_path = rf"{key_path}\shell\open\command"
            cmd_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_path)
            winreg.SetValue(cmd_key, "", winreg.REG_SZ, f'"{exe}" "%1"')

            # === 2. Dem System mitteilen: "Ich bin ein Browser!" ===
            browser_key = r"Software\Clients\StartMenuInternet\WHYBrowser"
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, browser_key)
            winreg.SetValue(winreg.HKEY_CURRENT_USER, browser_key, winreg.REG_SZ, "WHY Browser")

            # Eintrag für das EXE
            exe_key = f"{browser_key}\\DefaultIcon"
            key2 = winreg.CreateKey(winreg.HKEY_CURRENT_USER, exe_key)
            winreg.SetValue(key2, "", winreg.REG_SZ, f'"{exe}",0')

            # === 3. Windows Default-Apps öffnen ===
            subprocess.Popen(["start", "ms-settings:defaultapps"], shell=True)

            QMessageBox.information(
                self,
                "Standardbrowser",
                "WHY Browser wurde registriert!\n\n"
                "Windows Einstellungen wurden geöffnet.\n"
                "Wähle dort WHY Browser als Standardbrowser aus."
            )

        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler: {str(e)}")


    def toggle_settings_sidebar(self):
        if self.settings_sidebar.isVisible():
            self.settings_sidebar.hide_sidebar()
        else:
            self.settings_sidebar.show_sidebar()

    # -------------------- Tabs --------------------
    def add_tab(self, url=None):
        # Standard: homepage
        if not url:
            url = self.homepage_url.toString()

        # wenn QUrl oder bool reinkommt -> konvertieren
        if isinstance(url, QUrl):
            url = url.toString()

        if not isinstance(url, str):
            url = str(url)

        # suchquery -> baue search url
        if not (url.startswith("http://") or url.startswith("https://") or url.startswith("file://")):
            url = self.search_url.format(url)

        # Vermeide, dass exakt gleiche URL bereits in letztem Tab existiert und doppelt angelegt wird,
        # aber trotzdem erlauben mehrere gleiche Tabs wenn bewusst gewünscht -> hier einfache check:
        if self.tabs.count() == 1:
            existing = ""
            try:
                existing = self.tabs.widget(0).view.url().toString()
            except Exception:
                pass
            # Wenn nur ein Tab offen ist und es genau die Homepage ist und wir wieder die Homepage öffnen,
            # ersetze statt neues Tab:
            if existing == url:
                # setze einfach aktuellen Tab URL (keine Duplikate)
                try:
                    self.tabs.widget(0).view.setUrl(QUrl(url))
                except Exception:
                    pass
                return self.tabs.widget(0)

        # Normales neues Tab anlegen
        tab = BrowserTab(url, parent=self)
        tab.parent_browser = self
        idx = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(idx)

        # Verbindungen
        tab.view.urlChanged.connect(lambda qurl, tab=tab: self.update_urlbar(qurl))
        tab.view.titleChanged.connect(lambda t, tab=tab: self.tabs.setTabText(self.tabs.indexOf(tab), t[:30] or "New Tab"))
        tab.view.iconChanged.connect(lambda icon, tab=tab: self.tabs.setTabIcon(self.tabs.indexOf(tab), icon))
        tab.view.loadFinished.connect(lambda ok, tab=tab: self.update_urlbar(tab.view.url()))

        # lade URL (nur einmal)
        try:
            tab.view.load(QUrl(url))
        except Exception:
            pass

        # speichere Tabs nach jeder Änderung
        self.save_tabs()
        return tab


    from PySide6.QtCore import Slot

    @Slot(str)
    def search_from_homepage(self, query):
        """Wird von homepage.html aufgerufen."""
        engine = self.config.get("search_engine", "duckduckgo")
        engines = self.config.get("search_engines", {
            "duckduckgo": "https://duckduckgo.com/?q={}",
            "google": "https://www.google.com/search?q={}",
            "bing": "https://www.bing.com/search?q={}"
        })
        base = engines.get(engine, "https://duckduckgo.com/?q={}")
        url = base.format(query)
        

    

    def run_external_tool(cmd):
        # cmd: string wie "nmap -v -A 127.0.0.1"  <- nur als Beispiel, Verantwortung liegt bei dir
        try:
            proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            out, err = proc.communicate(timeout=60)
            return out, err
        except Exception as e:
            return "", str(e)


    def close_tab(self, index):
        widget = self.tabs.widget(index)
        if widget:
            self.tabs.removeTab(index)
            widget.deleteLater()

        # Falls keine Tabs mehr offen sind: neuen Tab anlegen (Homepage)
        if self.tabs.count() == 0:
            self.add_tab(self.homepage_url.toString())

        # speichere neuen Zustand
        self.save_tabs()




    def _on_tab_changed(self, index):
        # speichere aktive Tab-Index
        try:
            self.config["active_tab"] = index
            self.save_tabs()
        except Exception:
            pass

    def _on_tab_close_requested(self, index):
        # wrapper damit close_tab auch config updatet
        self.close_tab(index)
        # save after close
        self.save_tabs()

    def save_tabs(self):
        """Schreibe offene Tabs + aktiven Index in config.json"""
        try:
            open_tabs = []
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                # jedes Tab hat .view (QWebEngineView)
                url = ""
                try:
                    url = w.view.url().toString()
                except Exception:
                    pass
                if url:
                    open_tabs.append(url)
            self.config["open_tabs"] = open_tabs
            self.config["active_tab"] = max(0, self.tabs.currentIndex())
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Fehler beim Speichern der Tabs:", e)

    def restore_tabs(self):
        """Lädt Tabs aus config. Ruft add_tab nur hier auf."""
        try:
            open_tabs = self.config.get("open_tabs", [])
            # Wenn nichts gespeichert → genau 1 Homepage-Tab
            if not open_tabs:
                self.add_tab(self.homepage_url.toString())
                return

            # Entferne vorhandene Tabs (falls restore mehrfach aufgerufen wurde)
            while self.tabs.count() > 0:
                self.close_tab(0)

            for url in open_tabs:
                # sichere String-URL übergeben
                self.add_tab(url)

            # aktiven Tab setzen
            active_index = int(self.config.get("active_tab", 0))
            if 0 <= active_index < self.tabs.count():
                self.tabs.setCurrentIndex(active_index)
        except Exception as e:
            print("Fehler beim Wiederherstellen der Tabs:", e)

    def closeEvent(self, event):
        self.save_tabs()
        super().closeEvent(event)

    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QProgressBar, QScrollArea, QFileDialog, QMessageBox
    )
    from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
    from datetime import datetime
    import os, json

    def handle_download(self, download: QWebEngineDownloadRequest):
        suggested = download.downloadFileName()
        path, _ = QFileDialog.getSaveFileName(self, "Datei speichern unter", suggested)

        if not path:
            download.cancel()
            return

        download.setDownloadFileName(os.path.basename(path))
        download.setDownloadDirectory(os.path.dirname(path))
        download.accept()

        entry = {
            "file": os.path.basename(path),
            "path": path,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "progress": 0,
            "status": "Downloading"
        }
        self.downloads.append(entry)
        self.save_downloads()

        download.downloadProgress.connect(lambda rec, tot, d=download, e=entry: self.update_download_progress(d, e, rec, tot))
        download.finished.connect(lambda d=download, e=entry: self.download_finished(d, e))

        QMessageBox.information(self, "Download Started", f"{entry['file']} wird heruntergeladen...")


    def show_download_progress(self, download, received, total):
        if total > 0:
            percent = int(received * 100 / total)
            self.title_label.setText(f"WHY Browser – Download: {percent}%")

    def update_download_progress(self, download, entry, received, total):
        if total > 0:
            entry["progress"] = int(received * 100 / total)
            self.refresh_download_popup()


    def download_finished(self, download, entry):
        if download.state() == QWebEngineDownloadRequest.DownloadCompleted:
            entry["status"] = "Abgeschlossen"
        else:
            entry["status"] = "Fehlgeschlagen"
        entry["progress"] = 100
        self.save_downloads()
        self.refresh_download_popup()

    def load_downloads(self):
        if os.path.exists("downloads.json"):
            with open("downloads.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_downloads(self):
        with open("downloads.json", "w", encoding="utf-8") as f:
            json.dump(self.downloads, f, indent=2, ensure_ascii=False)

    def toggle_download_popup(self):
        """Modernes Download-Menü"""
        # 🔒 Falls das Hauptmenü offen ist → automatisch schließen
        if hasattr(self, "main_menu_popup") and self.main_menu_popup.isVisible():
            self.main_menu_popup.hide()

        # Wenn das Popup schon offen ist → schließen
        if hasattr(self, "download_popup") and self.download_popup.isVisible():
            self.download_popup.hide()
            return

        # ... der Rest deiner Funktion (Popup erstellen etc.)


        # Popup erstellen
        self.download_popup = QWidget(self)
        self.download_popup.setObjectName("DownloadPopup")
        self.download_popup.setFixedSize(420, 340)

        layout = QVBoxLayout(self.download_popup)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # === Header ===
        header_layout = QHBoxLayout()
        title = QLabel("Downloads")
        title.setStyleSheet("font-size: 15px; font-weight: 600; color: white; background: transparent; ")
        header_layout.addWidget(title)
        header_layout.addStretch()

        close_btn = QPushButton("×")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #aaa;
                font-size: 20px;
                border: none;
            }
            QPushButton:hover { color: white; }
        """)
        close_btn.clicked.connect(lambda: self.download_popup.hide())
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)

        # === Scrollbereich ===
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(12)
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        # === Footer ===
        footer_layout = QHBoxLayout()
        clear_btn = QPushButton("Alle löschen")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #ccc;
                border: 1px solid white;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #3b3b3b;
                color: white;
            }
        """)
        clear_btn.clicked.connect(self.clear_downloads)
        footer_layout.addStretch()
        footer_layout.addWidget(clear_btn)
        layout.addLayout(footer_layout)

        self.refresh_download_popup()

        # === Popup-Styling ===
        self.download_popup.setStyleSheet("""
            #DownloadPopup {
                background-color:#2b2b2b;
                border: 1px solid #333;
                border-radius: 12px;
            }
            QScrollArea {
                background: transparent;
                border: none;
            }
            QLabel {
                color: #ddd;
                font-size: 13px;
            }
            QProgressBar {
                border: 1px solid #333;
                border-radius: 6px;
                background-color: #1e1e1e;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 6px;
            }
        """)

        # Position oben rechts
        x = self.width() - self.download_popup.width() - 25
        y = 65
        self.download_popup.move(x, y)
        self.download_popup.show()

    def refresh_download_popup(self):
        """Aktualisiert Download-Liste"""
        if not hasattr(self, "scroll_layout"):
            return

        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not self.downloads:
            empty = QLabel("Keine Downloads vorhanden.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color: #666; font-size: 13px;")
            self.scroll_layout.addWidget(empty)
            return

        for entry in self.downloads:
            item = QWidget()
            item_layout = QVBoxLayout(item)
            item_layout.setSpacing(4)

            # Dateiname & Zeit
            header = QHBoxLayout()
            file_label = QLabel(f"{entry['file']}")
            file_label.setStyleSheet("font-weight: 500; color: white;")
            header.addWidget(file_label)
            header.addStretch()
            time_label = QLabel(entry["time"])
            time_label.setStyleSheet("color: #777; font-size: 11px;")
            header.addWidget(time_label)
            item_layout.addLayout(header)

            # Fortschrittsanzeige
            if entry["status"] == "Downloading":
                progress = QProgressBar()
                progress.setValue(entry["progress"])
                item_layout.addWidget(progress)
            else:
                status_row = QHBoxLayout()
                status = QLabel(f"{entry['status']}")
                status.setStyleSheet("color: #999;")
                status_row.addWidget(status)
                status_row.addStretch()
                open_btn = QPushButton("Öffnen")
                open_btn.setFixedHeight(24)
                open_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3b82f6;
                        border-radius: 5px;
                        color: white;
                        font-size: 12px;
                        padding: 2px 10px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #2563eb;
                    }
                """)
                open_btn.clicked.connect(lambda checked=False, path=entry["path"]: os.startfile(path))
                status_row.addWidget(open_btn)
                item_layout.addLayout(status_row)

            # Trennlinie
            line = QLabel()
            line.setFixedHeight(1)
            line.setStyleSheet("background-color: #2a2a2a; margin-top: 4px;")
            item_layout.addWidget(line)

            self.scroll_layout.addWidget(item)

        self.scroll_layout.addStretch()

    def clear_downloads(self):
        """Löscht alle gespeicherten Downloads"""
        confirm = QMessageBox.question(self, "Löschen", "Alle Downloads löschen?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.downloads = []
            self.save_downloads()
            self.refresh_download_popup()


    def toggle_devtools(self):
        if not hasattr(self, "_devtools_widget") or self._devtools_widget is None:
            self._devtools_widget = DevToolsWidget(self.current_view(), parent=self, interceptor=self.interceptor)
        if self._devtools_widget.isVisible():
            self._devtools_widget.hide()
        else:
            # update target auf aktuellen Tab
            self._devtools_widget.target_view = self.current_view()
            self._devtools_widget.show()
            # refresh network + elements
            self._devtools_widget.refresh_network_list()
            self._devtools_widget.load_page_html()



    import json

    def toggle_user_popup(self):
        # Wenn offen → schließen
        if hasattr(self, "user_popup") and self.user_popup.isVisible():
            self.user_popup.hide()
            return

        if hasattr(self, "main_menu_popup") and self.main_menu_popup.isVisible():
            self.main_menu_popup.hide()

        # === Daten laden ===
        def load_user_data():
            if not os.path.exists("user_data.json"):
                return {}
            with open("user_data.json", "r", encoding="utf-8") as f:
                return json.load(f)

        user_data = load_user_data()
        email = user_data.get("email", "unknown@example.com")
        username = user_data.get("username", "Unknown User")
        birth = user_data.get("birthdate", "Not set")

        # === Popup ===
        self.user_popup = QWidget(self)
        self.user_popup.setObjectName("UserPopup")
        self.user_popup.setFixedSize(400, 360)

        layout = QVBoxLayout(self.user_popup)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(16)

        # === Header ===
        header = QHBoxLayout()
        title = QLabel("User Profile")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: white; letter-spacing: 0.5px; background: transparent;")
        header.addWidget(title)
        header.addStretch()

        close_btn = QPushButton("×")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background: none;
                color: #888;
                border: none;
                font-size: 20px;
            }
            QPushButton:hover { color: white; }
        """)
        close_btn.clicked.connect(lambda: self.user_popup.hide())
        header.addWidget(close_btn)
        layout.addLayout(header)


        # === Benutzer-Avatar im runden Container ===
        avatar_container = QWidget()
        avatar_container.setFixedSize(80, 80)
        avatar_container.setObjectName("AvatarContainer")

        # Layout
        avatar_layout = QVBoxLayout(avatar_container)
        avatar_layout.setContentsMargins(10, 10, 10, 10)
        avatar_layout.setAlignment(Qt.AlignCenter)

        from PySide6.QtSvgWidgets import QSvgWidget

        # SVG-Icon (bleibt scharf)
        avatar_svg = QSvgWidget("icons/user.svg")
        avatar_svg.setFixedSize(35, 35)  # bleibt vektorbasiert, kein Qualitätsverlust
        avatar_layout.addWidget(avatar_svg)

        # Stil des Containers
        avatar_container.setStyleSheet("""
            #AvatarContainer {
                background-color: #1f1f1f;
                border-radius: 40px;
                border: 1px solid #333;
                box-shadow: 0px 0px 8px rgba(0, 0, 0, 0.4);
            }
        """)

        # In Layout einfügen
        layout.addWidget(avatar_container, alignment=Qt.AlignCenter)
        layout.addSpacing(10)



        # === Formular ===
        form = QFormLayout()
        form.setSpacing(10)

        # Username (bearbeitbar nach Klick)
        self.username_edit = QLineEdit(username)
        self.username_edit.setEnabled(False)
        self.username_edit.setStyleSheet("""
            QLineEdit {
                background: #181818;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 6px 10px;
                color: #ddd;
                font-size: 13px;
                min-height: 13px ; 
            }
            QLineEdit:disabled {
                background: #202020;
                color: #777;
            }
            QLineEdit:focus {
                border: 1px solid #3b82f6;
            }
        """)
        form.addRow(QLabel("Username:"), self.username_edit)

        # E-Mail (fix)
        email_lbl = QLabel(email)
        email_lbl.setStyleSheet("color: #aaa; font-size: 13px;")
        form.addRow(QLabel("E-Mail:"), email_lbl)

        # Geburtsdatum
        birth_lbl = QLabel(birth)
        birth_lbl.setStyleSheet("color: #aaa; font-size: 13px;")
        form.addRow(QLabel("Birthdate:"), birth_lbl)

        layout.addLayout(form)

        # === Button-Bereich ===
        btns = QHBoxLayout()
        btns.setSpacing(10)

        # Bearbeiten
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b3b3b;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 14px;
            }
            QPushButton:hover { background-color: #4b4b4b; }
        """)
        self.edit_btn.clicked.connect(self.enable_user_edit)
        btns.addWidget(self.edit_btn)

        # Speichern
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 14px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        save_btn.clicked.connect(self.save_user_changes)
        btns.addWidget(save_btn)

        layout.addLayout(btns)

        # === Untere Aktionsleiste ===
        bottom = QHBoxLayout()
        bottom.setSpacing(12)

        delete_btn = QPushButton("Delete Account")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b0000;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 14px;
            }
            QPushButton:hover { background-color: #a40000; }
        """)
        delete_btn.clicked.connect(self.delete_user)
        bottom.addWidget(delete_btn)

        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #222;
                color: #ddd;
                border: 1px solid white;
                border-radius: 8px;
                padding: 7px 14px;
            }
            QPushButton:hover { background-color: #2f2f2f; }
        """)
        logout_btn.clicked.connect(self.logout_user)
        bottom.addWidget(logout_btn)

        layout.addLayout(bottom)

        layout.addStretch()

        # === Stil (modern dark flat) ===
        self.user_popup.setStyleSheet("""
            #UserPopup {
                background-color: #2b2b2b;
                border: 1px solid #2b2b2b;
                border-radius: 12px;
            }
            QLabel { color: #ddd; font-size: 13px; }
        """)

        # === Position ===
        x = self.width() - self.user_popup.width() - 25
        y = 70
        self.user_popup.move(x, y)
        self.user_popup.show()



    def enable_user_edit(self):
        """Aktiviert die Bearbeitung der Felder."""
        self.username_edit.setEnabled(True)
        self.username_edit.setFocus()
        self.edit_btn.setEnabled(False)


    def save_user_changes(self):
        """Speichert Änderungen am Benutzer."""
        username = self.username_edit.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Please enter a username.")
            return

        data = {}
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)

        data["username"] = username
        with open("user_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.username_edit.setEnabled(False)
        self.edit_btn.setEnabled(True)
        QMessageBox.information(self, "Saved", "Profile updated successfully!")


    def delete_user(self):
        """Löscht den Benutzer vollständig mit Abschiedsnachricht."""
        if not os.path.exists("user_data.json"):
            QMessageBox.warning(self, "Error", "No user data found.")
            return

        confirm = QMessageBox.question(
            self, "Delete Account", "Are you sure you want to delete your account?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            os.remove("user_data.json")
            self.user_popup.hide()

            goodbye = QMessageBox()
            goodbye.setWindowTitle("Goodbye 💔")
            goodbye.setIcon(QMessageBox.Information)
            goodbye.setText("We're sorry to see you go.\n\nHope to see you again someday!")
            goodbye.setStyleSheet("""
                QMessageBox { background-color: #1a1a1a; color: white; font-size: 13px; }
                QPushButton { background-color: #3b82f6; color: white; border-radius: 6px; padding: 4px 10px; }
                QPushButton:hover { background-color: #2563eb; }
            """)
            goodbye.exec()
            self.logout_user()




    def logout_user(self):
        clear_session()
        QMessageBox.information(self, "Abgemeldet", "Du wurdest abgemeldet.")
        self.close()
        # Login-Fenster wieder anzeigen
        login_window = LoginWindow()
        login_window.show()


    

    def toggle_history_popup(self):
        """Modern gestaltetes Verlaufspopup"""
        # Falls Hauptmenü offen ist → schließen
        if hasattr(self, "main_menu_popup") and self.main_menu_popup.isVisible():
            self.main_menu_popup.hide()

        # Falls Popup schon sichtbar → schließen
        if hasattr(self, "history_popup") and self.history_popup.isVisible():
            self.history_popup.hide()
            return

        # Neues Popup erstellen
        self.history_popup = QWidget(self)
        self.history_popup.setObjectName("HistoryPopup")
        self.history_popup.setFixedSize(420, 340)

        # === Layouts ===
        main_layout = QVBoxLayout(self.history_popup)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        # === Header ===
        header_layout = QHBoxLayout()
        title = QLabel("Browsing History")
        title.setStyleSheet("""
            font-size: 15px;
            font-weight: 600;
            color: white;
            letter-spacing: 0.3px;
            background: #2b2b2b; 
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()

        close_btn = QPushButton("×")
        close_btn.setFixedSize(26, 26)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #aaa;
                font-size: 20px;
                border: none;
            }
            QPushButton:hover { color: white; }
        """)
        close_btn.clicked.connect(lambda: self.history_popup.hide())
        header_layout.addWidget(close_btn)
        main_layout.addLayout(header_layout)

        # === Scroll-Bereich ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)

        # === Verlauf laden ===
        history = load_history()
        if not history:
            no_data = QLabel("No history entries yet.")
            no_data.setStyleSheet("color: #888; font-size: 13px; border-radius:12px ;")
            no_data.setAlignment(Qt.AlignCenter)
            scroll_layout.addWidget(no_data)
        else:
            for entry in reversed(history[-50:]):  # Zeige die letzten 50 Einträge
                item = QWidget()
                item_layout = QVBoxLayout(item)
                item_layout.setContentsMargins(8, 6, 8, 6)

                # Titel-Link
                title_label = QLabel(f"<a href='{entry['url']}'>{entry['title'] or entry['url']}</a>")
                title_label.setOpenExternalLinks(False)
                title_label.linkActivated.connect(lambda url, self=self: self.open_url_in_new_tab(url))
                title_label.setStyleSheet("""
                    QLabel {
                        color: #3b82f6;
                        font-size: 13px;
                        text-decoration: none;
                        border:none;
                        
                    }
                """)

                # Zeitstempel
                time_label = QLabel(entry.get("timestamp", ""))
                time_label.setStyleSheet("color: #999; font-size: 11px; border:none;")

                item_layout.addWidget(title_label)
                item_layout.addWidget(time_label)

                # Stil jedes Eintrags
                item.setStyleSheet("""
                    QWidget {
                        background-color: #333;
                        border: 1px solid white;
                        border-radius: 6px;
                    }
                """)

                scroll_layout.addWidget(item)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # === Footer ===
        clear_btn = QPushButton("Clear History")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border: 1px solid white;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        clear_btn.clicked.connect(self.clear_history)
        main_layout.addWidget(clear_btn, alignment=Qt.AlignRight)

        # === Popup-Styling ===
        self.history_popup.setStyleSheet("""
            #HistoryPopup {
                background-color: #2b2b2b;
                border: 1px solid #333;
                border-radius: 10px;
            }
        """)

        # === Position ===
        x = self.width() - self.history_popup.width() - 25
        y = 60
        self.history_popup.move(x, y)
        self.history_popup.show()

    def clear_history(self):
        """Löscht den gesamten Verlauf"""
        confirm = QMessageBox.question(
            self, "Clear History", "Are you sure you want to clear your browsing history?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            if os.path.exists("history.json"):
                os.remove("history.json")
            QMessageBox.information(self, "Cleared", "Browsing history cleared.")
            self.history_popup.hide()



    def open_url_in_new_tab(self, url):
        self.add_tab(url)

    def load_favorites(self):
        if os.path.exists("favorites.json"):
            try:
                with open("favorites.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_favorites(self):
        with open("favorites.json", "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, indent=2, ensure_ascii=False)



    def add_current_to_favorites(self):
        view = self.current_view()
        if not view:
            return

        url = view.url().toString()
        title = self.tabs.tabText(self.tabs.currentIndex()) or url

        # Prüfen, ob Favorit schon existiert
        if any(f["url"] == url for f in self.favorites):
            QMessageBox.information(self, "Favoriten", "Diese Seite ist bereits in deinen Favoriten.")
            return

        # Maximal 5 Favoriten
        if len(self.favorites) >= 5:
            QMessageBox.warning(self, "Favoriten", "Du kannst maximal 5 Favoriten speichern.")
            return

        # Favorit speichern
        self.favorites.append({"title": title, "url": url})
        self.save_favorites()
        QMessageBox.information(self, "Favoriten", f"'{title}' wurde zu deinen Favoriten hinzugefügt.")
        self.show_favorites_popup(refresh=True)

    def show_favorites_popup(self, refresh=False):
        """Modernes Favoriten-Popup"""
        # Hauptmenü schließen, falls offen
        if hasattr(self, "main_menu_popup") and self.main_menu_popup.isVisible():
            self.main_menu_popup.hide()

        # Falls Popup schon sichtbar ist → bei Refresh neu aufbauen, sonst schließen
        if hasattr(self, "favorites_popup") and self.favorites_popup.isVisible():
            if refresh:
                self.favorites_popup.close()
            else:
                self.favorites_popup.hide()
                return

        # Popup-Widget
        self.favorites_popup = QWidget(self)
        self.favorites_popup.setObjectName("FavoritesPopup")
        self.favorites_popup.setFixedSize(420, 320)

        # Layout
        main_layout = QVBoxLayout(self.favorites_popup)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(10)

        # === Header ===
        header_layout = QHBoxLayout()
        title = QLabel("Favorites")
        title.setStyleSheet("""
            font-size: 15px;
            font-weight: 600;
            color: #fff;
            letter-spacing: 0.3px;
            background: transparent;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()

        close_btn = QPushButton("×")
        close_btn.setFixedSize(26, 26)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #aaa;
                font-size: 20px;
                border: none;
            }
            QPushButton:hover { color: white; }
        """)
        close_btn.clicked.connect(lambda: self.favorites_popup.hide())
        header_layout.addWidget(close_btn)
        main_layout.addLayout(header_layout)

        # === Scrollbereich ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget()
        inner_layout = QVBoxLayout(content)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(8)

        # === Favoriten anzeigen ===
        if not getattr(self, "favorites", None):
            no_fav = QLabel("No favorites added yet.")
            no_fav.setStyleSheet("color: white; font-size: 13px;")
            no_fav.setAlignment(Qt.AlignCenter)
            inner_layout.addWidget(no_fav)
        else:
            for fav in self.favorites:
                row = QWidget()
                row.setObjectName("FavRow")
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(10, 6, 10, 6)

                # 🔗 Titel-Link
                link = QLabel(f"<a href='{fav['url']}'>{fav['title']}</a>")
                link.setOpenExternalLinks(False)
                link.linkActivated.connect(lambda url=fav['url']: self.add_tab(url))
                link.setStyleSheet("""
                    QLabel {
                        color: #fff;
                        font-size: 13px;
                        text-decoration: none;
                        background: transparent;
                    }
                    QLabel:hover {
                        color: #fff;
                    }
                """)
                row_layout.addWidget(link)

                # Spacer
                row_layout.addStretch()

                # 🗑 Delete Button (SVG optional)
                from PySide6.QtGui import QIcon
                from PySide6.QtCore import QSize

                # statt: btn_del = QPushButton("Remove")
                btn_del = QPushButton()
                btn_del.setToolTip("Favorit entfernen")
                btn_del.setCursor(Qt.PointingHandCursor)
                btn_del.setFixedSize(30, 30)                     # quadratischer Button
                btn_del.setIcon(QIcon("icons/trash.svg"))       # dein SVG
                btn_del.setIconSize(QSize(16, 16))              # Icon-Größe (scharf skalieren)
                btn_del.setFlat(True)                           # ohne 3D-Rand
                btn_del.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        border: none;
                        border-radius: 6px;
                        
                    }
                    QPushButton:hover {
                        background-color: rgba(255,255,255,0.03);
                    }
                    QPushButton:pressed {
                        background-color: rgba(255,255,255,0.06);
                    }
                """)
                btn_del.clicked.connect(lambda checked=False, url=fav['url']: self.remove_favorite(url))
                row_layout.addWidget(btn_del)

                # Stil der Zeile
                row.setStyleSheet("""
                    #FavRow {
                        background-color: #1e1e1e;
                        border: 1px solid white;
                        border-radius: 6px;
                    }
                    #FavRow:hover {
                        background-color: #252525;
                    }
                """)

                inner_layout.addWidget(row)

        inner_layout.addStretch()
        content.setLayout(inner_layout)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # === Footer mit "Add Favorite" & "Clear All" ===
        footer = QHBoxLayout()
        footer.addStretch()

        add_btn = QPushButton("Add Current Page")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                border: 1px solid white;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        add_btn.clicked.connect(self.add_current_to_favorites)
        footer.addWidget(add_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                border: none;
                color: #ccc;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        clear_btn.clicked.connect(self.clear_all_favorites)
        footer.addWidget(clear_btn)

        main_layout.addLayout(footer)

        # === Popup-Stil ===
        self.favorites_popup.setStyleSheet("""
            #FavoritesPopup {
                background-color: #2b2b2b;
                border: 1px solid #333;
                border-radius: 10px;
            }
        """)

        # === Position ===
        x = self.width() - self.favorites_popup.width() - 25
        y = 60
        self.favorites_popup.move(x, y)
        self.favorites_popup.show()



    def remove_favorite(self, url):
        """Entfernt einen Favoriten und aktualisiert das Popup."""
        self.favorites = [f for f in self.favorites if f["url"] != url]
        self.save_favorites()
        QMessageBox.information(self, "Favoriten", " Favorit gelöscht.")
        self.show_favorites_popup(refresh=True)
        self.update_fav_icon()


    def toggle_favorite(self):
        """Schaltet Favoritenstatus der aktuellen Seite um (fügt hinzu oder entfernt)."""
        view = self.current_view()
        if not view:
            return

        url = view.url().toString()
        title = self.tabs.tabText(self.tabs.currentIndex()) or url

        # Prüfen, ob Favorit bereits existiert
        is_fav = any(f["url"] == url for f in self.favorites)
        if is_fav:
            # Entfernen
            self.favorites = [f for f in self.favorites if f["url"] != url]
            self.save_favorites()
            QMessageBox.information(self, "Favoriten", f" '{title}' wurde entfernt.")
            self.update_fav_icon(url)
            self.show_favorites_popup(refresh=True)
        else:
            # Hinzufügen
            if len(self.favorites) >= 5:
                QMessageBox.warning(self, "Favoriten", "Du kannst maximal 5 Favoriten speichern.")
                return
            self.favorites.append({"title": title, "url": url})
            self.save_favorites()
            QMessageBox.information(self, "Favoriten", f" '{title}' wurde hinzugefügt.")
            self.update_fav_icon(url)
            self.show_favorites_popup(refresh=True)


    def update_fav_icon(self, current_url=None):
        """Setzt den Stern gefüllt oder leer je nach Favoritenstatus."""
        if not current_url:
            view = self.current_view()
            if not view:
                return
            current_url = view.url().toString()

        if any(f["url"] == current_url for f in self.favorites):
            self.fav_action.setIcon(QIcon("icons/star_filled.svg"))
        else:
            self.fav_action.setIcon(QIcon("icons/star_empty.svg"))

    def clear_all_favorites(self):
        confirm = QMessageBox.question(
            self, "Clear Favorites", "Do you really want to remove all favorites?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.favorites = []
            self.save_favorites()
            QMessageBox.information(self, "Cleared", "All favorites were removed.")
            self.show_favorites_popup(refresh=True)



    def create_close_button(self, parent_widget):
        """Erstellt einen modernen runden Schließen-Button für Popups."""
        btn = QPushButton("✕", parent_widget)
        btn.setObjectName("RoundCloseBtn")
        btn.setFixedSize(24, 24)
        btn.setStyleSheet("""
            #RoundCloseBtn {
                background-color: #ff5f57;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 13px;
            }
            #RoundCloseBtn:hover {
                background-color: #ff2d00;
            }
        """)
        btn.clicked.connect(parent_widget.hide)
        return btn


    def start_reload_animation(self):
        if self.rotating:
            return
        self.rotating = True
        self.rotation_angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_reload_icon)
        self.timer.start(40)   # statt 30 → 60 FPS
        self.rotation_angle = (self.rotation_angle + 5) % 360


    def rotate_reload_icon(self):
        self.rotation_angle = (self.rotation_angle + 10) % 360

        # Originalgröße beibehalten
        base_pixmap = self.reload_icon
        size = base_pixmap.size()
        w, h = size.width(), size.height()

        # Neues, transparentes Quadrat erstellen
        rotated_pixmap = QPixmap(w, h)
        rotated_pixmap.fill(Qt.transparent)

        # Painter mit Transformation um die Mitte
        painter = QPainter(rotated_pixmap)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.translate(w / 2, h / 2)
        painter.rotate(self.rotation_angle)
        painter.translate(-w / 2, -h / 2)
        painter.drawPixmap(0, 0, base_pixmap)
        painter.end()

        # Icon aktualisieren
        self.reload_button.setIcon(QIcon(rotated_pixmap))



    def stop_reload_animation(self):
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()
        self.reload_button.setIcon(QIcon("icons/reload.svg"))
        self.rotating = False


    # -------------------- Navigation --------------------
    def current_view(self):
        w = self.tabs.currentWidget()
        if w:
            return w.view
        return None
    
    def mousePressEvent(self, event):
            if event.button() == Qt.LeftButton and event.position().y() < 40:  # Klick oben
                self.dragPos = event.globalPosition().toPoint()
                event.accept()

    def mouseMoveEvent(self, event):
        if hasattr(self, "dragPos") and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def go_back(self):
        v = self.current_view()
        if v: v.back()

    def go_forward(self):
        v = self.current_view()
        if v: v.forward()

    def reload_page(self):
        v = self.current_view()
        if v: v.reload()

    def go_home(self):
        """Öffnet immer die lokale WHY-Startseite."""
        v = self.current_view()
        if v:
            homepage_path = os.path.abspath("homepage.html")
            v.setUrl(QUrl.fromLocalFile(homepage_path))


    @Slot(str)
    def search_from_homepage(self, query: str):
        """Suche von der Startseite mit der gespeicherten Suchmaschine."""
        if not query.strip():
            return

        # Hole gespeicherte Suchmaschine aus deiner bestehenden Config
        search_engine = self.config.get("search_engine", "duckduckgo").lower()

        # Nutze die gespeicherte Suchmaschine dynamisch
        if "google" in search_engine:
            url = f"https://www.google.com/search?q={query}"
        elif "bing" in search_engine:
            url = f"https://www.bing.com/search?q={query}"
        elif "brave" in search_engine:
            url = f"https://search.brave.com/search?q={query}"
        elif "yahoo" in search_engine:
            url = f"https://search.yahoo.com/search?p={query}"
        elif "ecosia" in search_engine:
            url = f"https://www.ecosia.org/search?q={query}"
        else:
            # Standard: DuckDuckGo
            url = f"https://duckduckgo.com/?q={query}"

        # Öffne die Suche im selben Tab (nicht in einem neuen)
        current_tab = self.current_view()
        if current_tab:
            current_tab.load(QUrl(url))
        else:
            self.add_tab(url)



    def update_urlbar(self, qurl):
        if isinstance(qurl, QUrl):
            url_text = qurl.toString()
        else:
            url_text = str(qurl)

        self.urlbar.setText(url_text)

        # Verlauf speichern — nur echte Seiten, keine Startseiten oder neuen Tabs
        if (
            url_text.startswith("http")
            and "about:blank" not in url_text
            and url_text.strip() != ""
            and url_text != self.config.get("homepage", "")
        ):
            from datetime import datetime
            history = load_history()

            # Prüfen, ob der gleiche Eintrag (URL + Datum) schon existiert
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            already_exists = any(
                h["url"] == url_text and h["timestamp"].split(" ")[0] == timestamp.split(" ")[0]
                for h in history
            )

            if not already_exists:
                history.append({
                    "url": url_text,
                    "title": self.tabs.tabText(self.tabs.currentIndex()) or "(Ohne Titel)",
                    "timestamp": timestamp
                })

                # Nach Datum sortieren (neueste zuerst)
                history = sorted(history, key=lambda x: x["timestamp"], reverse=True)
                save_history(history)

    def on_url_entered(self):
        text = self.urlbar.text().strip()
        if not text:
            return
        if text.startswith("http://") or text.startswith("https://"):
            url = text
        else:
            url = self.guess_url_or_search(text)
        v = self.current_view()
        if v:
            v.setUrl(QUrl(url))



    def guess_url_or_search(self, text: str) -> str:
        if "." in text and " " not in text:
            if not text.startswith("http"):
                return "http://" + text
            return text

        engine_key = self.config.get("search_engine", "duckduckgo")
        engine_url = self.config.get("search_engines", {}).get(engine_key)
        if not engine_url:
            engine_url = DEFAULT_CONFIG["search_engines"]["duckduckgo"]

        return engine_url.format(quote_plus(text))

    def closeEvent(self, event):
        """Speichert offene Tabs und aktiven Tab beim Schließen."""
        open_tabs = []
        for i in range(self.tabs.count()):
            view = self.tabs.widget(i).view
            if view and view.url().isValid():
                open_tabs.append(view.url().toString())

        # Aktives Tab merken
        active_index = self.tabs.currentIndex()

        # In config speichern
        self.config["open_tabs"] = open_tabs
        self.config["active_tab"] = active_index

        save_config(self.config)
        event.accept()

    def toggle_main_menu_popup(self):
        if hasattr(self, "main_menu_popup") and self.main_menu_popup.isVisible():
            self.main_menu_popup.hide()
            return

        # === Popup erstellen ===
        self.main_menu_popup = QWidget(self)
        self.main_menu_popup.setObjectName("MainMenuPopup")
        self.main_menu_popup.setFixedSize(280, 330)

        layout = QVBoxLayout(self.main_menu_popup)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # === Header ===
        header_layout = QHBoxLayout()
        title = QLabel("Browser Menü")
        title.setObjectName("MainMenuTitle")
        title.setStyleSheet("""
            font-size: 15px;
            font-weight: 600;
            color: #fff;
            background: transparent ; 
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()

        close_btn = QPushButton("×")
        close_btn.setObjectName("ClosePopupBtn")
        close_btn.setFixedSize(26, 26)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #bbb;
                font-size: 20px;
                border: none;
            }
            QPushButton:hover {
                color: #fff;
            }
        """)
        close_btn.clicked.connect(lambda: self.main_menu_popup.hide())
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)

        layout.addSpacing(6)

        # === Stil für Buttons ===
        btn_style = """
            QPushButton {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid white;
                border-radius: 8px;
                text-align: left;
                padding: 10px 12px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: white;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
        """

        # === Menü-Buttons ===
        buttons = [
            ("icons/user.svg", "Benutzerprofil", self.toggle_user_popup),
            ("icons/history.svg", "Verlauf anzeigen", self.toggle_history_popup),
            ("icons/download.svg", "Downloads", self.toggle_download_popup),
            ("icons/star_empty.svg", "Favoriten", self.show_favorites_popup),
            ("icons/dev.svg", "Dev Tools", self.toggle_devtools)
        ]

        for icon, label, func in buttons:
            btn = QPushButton(QIcon(icon), "  " + label)
            btn.setIconSize(QSize(18, 18))
            btn.setObjectName("MenuButton")
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(func)
            layout.addWidget(btn)

        layout.addStretch()

        # === Popup-Styling (Glass-Optik) ===
        self.main_menu_popup.setStyleSheet("""
            #MainMenuPopup {
                background-color: #2b2b2b;
                border-radius: 12px;
                backdrop-filter: blur(12px);
            }
        """)

        # === Positionierung ===
        x = self.width() - self.main_menu_popup.width() - 20
        y = 55
        self.main_menu_popup.move(x, y)
        self.main_menu_popup.show()


# -------------------- Main --------------------

SESSION_FILE = "session.json"

def save_session(username):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({"username": username}, f)

def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("username")
    except:
        return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def main():
    app = QApplication(sys.argv)
    cfg = load_config()
    accent = cfg.get("theme", {}).get("accent", "#61afef")
    load_stylesheet(app, accent)

    # Prüfe, ob bereits eingeloggt
    username = load_session()

    if username:
        # Benutzer ist eingeloggt → direkt Browser starten
        win = MiniBrowser()
        win.show()
        sys.exit(app.exec())
    else:
        # Kein Benutzer eingeloggt → Login anzeigen
        login_window = LoginWindow()
        login_window.show()

        # Nach Login oder Registrierung → Browser starten
        def start_browser():
            login_window.close()
            win = MiniBrowser()
            win.show()

        login_window.start_browser = start_browser
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
