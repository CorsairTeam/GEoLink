import os
import sys
import webbrowser
from tkinter import Tk, Frame, Canvas, DoubleVar, TOP, BOTH, LEFT, RIGHT, Y, GROOVE
from tkinter import Menu
from tkinter import ttk
from mbtiles_manager import MbtilesManager
import database
import notebook_points
import notebook_lines
import notebook_polygones
import import_export_manager

# Ligne de commande compilation : pyinstaller --noconsole --add-data "aide.html;." main.py

class MBTilesViewer:
    
    def fonction_temporaire(self):
        pass
    
    def open_help(self):
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        help_path = os.path.join(base_path, "aide.html")
        webbrowser.open(f"file:///{help_path}")
    
    def toggle_tooltips(self):
        from utility import ToolTip
        ToolTip.set_enabled(not ToolTip.enabled)
        label = "Afficher les Tooltips" if not ToolTip.enabled else "Masquer les Tooltips"
        self.aide_menu.entryconfig(self.tooltips_menu_index, label=label)  
        
            

    def on_tab_changed(self, event):
        """Gérer le changement d'onglet"""
        #L'onglet point est toujours a jour on met a jour les autres onglets
        
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text").strip()
        
        #Efface le point temporaire
        if hasattr(self, "clicked_point"):
            del self.clicked_point
        self.mbtiles_manager.clear_temp_point()

        #Efface la ligne temporaire
        self.clicked_points = []
        self.mbtiles_manager.clear_temp_line()
                
    
        if tab_text == "Lignes":
           notebook_lines.update_input_frame_lignes(self) 
                             
        elif tab_text == "Polygones":
            notebook_polygones.update_onglet_polygones(self)            
            
        
    def setup_menu(self):
        """Gestion des options du menu"""
        
        # Instanciation du menu 
        self.menu_bar = Menu(self.root)

        # Menu : "Cartes"
        cartes_menu = Menu(self.menu_bar, tearoff=0)
        cartes_menu.add_command(label="Charger Carte MBTiles", command=lambda: self.mbtiles_manager.import_carte(""))        
        self.menu_bar.add_cascade(label="Cartes", menu=cartes_menu)        

        # Menu : "Importer"        
        importer_menu = Menu(self.menu_bar, tearoff=0)
        importer_menu.add_command(label="Importer fichier KML", command=lambda: import_export_manager.import_kml_to_databases(self))
        importer_menu.add_command(label="Importer fichier CSV", command=lambda: import_export_manager.import_csv(self))        
        #importer_menu.add_command(label="Importer fichier .geojson", command=lambda: viewer.fonction_temporaire())
        self.menu_bar.add_cascade(label="Importer", menu=importer_menu)

        # Menu : "Exporter vers SDVFR"        
        exporter_menu = Menu(self.menu_bar, tearoff=0)
        sdvfr_menu = Menu(exporter_menu, tearoff=0)
        sdvfr_menu.add_command(label="KML : Exporte les objets sélectionnés", command=lambda: import_export_manager.export_kml(self, export_all=False, foreflight=False))
        sdvfr_menu.add_command(label="KML : Exporte tous les objets", command=lambda: import_export_manager.export_kml(self, export_all=True, foreflight=False))
        sdvfr_menu.add_separator()
        sdvfr_menu.add_command(label="CSV : Exporte les points sélectionnés", command=lambda: import_export_manager.export_csv_sdvfr(self, export_all=False))
        sdvfr_menu.add_command(label="CSV : Exporte tous les points", command=lambda: import_export_manager.export_csv_sdvfr(self, export_all=True))
        exporter_menu.add_cascade(label="Sdvfr", menu=sdvfr_menu)

        foreflight_menu = Menu(exporter_menu, tearoff=0)
        foreflight_menu.add_command(label="KML : Exporte les objets sélectionnés", command=lambda: import_export_manager.export_kml(self, export_all=False, foreflight=True))
        foreflight_menu.add_command(label="KML : Exporte tous les objets", command=lambda: import_export_manager.export_kml(self, export_all=True, foreflight=True))
        foreflight_menu.add_separator()
        foreflight_menu.add_command(label="CSV : Exporte les points sélectionnés", command=lambda: import_export_manager.export_csv_foreflight(self, export_all=False))
        foreflight_menu.add_command(label="CSV : Exporte tous les points", command=lambda: import_export_manager.export_csv_foreflight(self, export_all=True))
        exporter_menu.add_cascade(label="Foreflight", menu=foreflight_menu)
        self.menu_bar.add_cascade(label="Exporter", menu=exporter_menu)
        
        aide_menu = Menu(self.menu_bar, tearoff=0)
        aide_menu.add_command(label="Fichier Aide", command=lambda: self.open_help())
        aide_menu.add_command(label="Masquer les Tooltips", command=lambda: self.toggle_tooltips())
        self.tooltips_menu_index = 1
        self.aide_menu = aide_menu  # Stocker l'aide_menu pour l'utiliser plus tard
        self.menu_bar.add_cascade(label="Aide", menu=aide_menu)

        # Ajoute le menu dans la fenêtre principale
        self.root.config(menu=self.menu_bar)
  
    def setup_ui(self):
        """Crée l'interface utilisateur"""

        # Création du cadre principal
        self.main_frame = Frame(self.root)
        self.main_frame.pack(side=TOP, fill=BOTH, expand=True)

        # Création du notebook (côté gauche) contenant les onglets
        self.notebook = ttk.Notebook(self.main_frame, width=350)
        self.notebook.pack(side=LEFT, fill=Y, padx=(5, 2), pady=(5, 5))  # Padding pour éviter le chevauchement
        self.notebook.pack_propagate(False)

        # Création du canvas (côté droit) pour l'affichage des cartes
        self.canvas = Canvas(self.main_frame, bg="lightgray", relief=GROOVE, borderwidth=2)
        self.canvas.pack(side=RIGHT, fill=BOTH, expand=True, padx=(2, 5), pady=(5, 5))

        # Création de l'onglet points du notebook
        notebook_points.setup_points_tabs(self)

        # Création de l'onglet lignes du notebook
        notebook_lines.setup_lignes_tabs(self)

        # Création de l'onglet polygones du notebook
        notebook_polygones.setup_polygones_tabs(self)     

    def __init__(self, root):        

        #Variable : Position et altitude du hotspot Foreflight
        self.hotspot_x = DoubleVar(value=0.5)
        self.hotspot_y = DoubleVar(value=0.5) 
        self.altitude = DoubleVar(value=0.0)    

        # Fenêtre tkinter : Initialisation
        self.root = root        
        self.root.title("Préparation Mission")

        # Fenêtre tkinter : Taille et positionnement
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = int(screen_width * 0.85)
        height = int(screen_height * 0.85)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Variables de gestion de la carte
        self.db_path = None
        self.zoom = 12
        self.offset_x = 0
        self.offset_y = 0
        
        # Cache des tuiles contenant les images déjà chargées
        self.tile_cache = {}
        self.min_col = 0
        self.max_col = 0
        self.min_row = 0
        self.max_row = 0 

        #Variables pour la création de lignes ou polygones par clic
        self.clicked_points = []  # Points cliqués sur la carte
        self.temp_line_id = None  # ID de la ligne temporaire affichée
        # Liste de coordonnées accessible depuis l'instance

        # Instancie la classe MbtilesManager et lui passe une référence à l'instance principale
        self.mbtiles_manager = MbtilesManager(self)

        # Création des menus de la fenêtre principale
        self.setup_menu()

        # Création des bases SQLite (si non existantes)
        if not all(os.path.exists(db_file) for db_file in ["points.db", "lignes.db", "polygones.db"]):
            database.create_database()

        # Création de l'interface utilisateur et affichage de la carte
        self.setup_ui()

        # Rafraichit le calcule de la taille de la carte pour afficher correctement les objets
        self.root.update_idletasks()

        # Génération des événements de la carte apres la creation du canvas
        self.mbtiles_manager.bind_canvas_events()
        
        # Importation de la carte
        map_path = r"Cartes\Cazaux sud ouest avec gabarit-WGS84-EPSG3857.mbtiles"
        self.mbtiles_manager.import_carte(map_path)

        # Gestion des événements
        self.notebook.bind("<<NotebookTabChanged>>",lambda event: self.on_tab_changed(event))        
        self.root.protocol("WM_DELETE_WINDOW", lambda: database.database_closing(self))

def main():
    root = Tk()
    app = MBTilesViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
