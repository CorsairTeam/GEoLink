import os
import tkinter as tk
from tkinter import Menu, ttk
from mbtiles_manager import MbtilesManager
import database
import notebook_points
import notebook_lines
import notebook_polygones

# Ligne de commande compilation : pyinstaller --noconsole main.py

class MBTilesViewer:
    
    def fonction_temporaire(self):
        pass
    
    def toggle_tooltips(self):
        from utility import ToolTip
        ToolTip.set_enabled(not ToolTip.enabled)
        label = "Afficher les Tooltips" if not ToolTip.enabled else "Masquer les Tooltips"
        self.aide_menu.entryconfig(1, label=label)      

    def on_tab_changed(self, event):
        """Gérer le changement d'onglet"""
        #L'onglet point est toujours a jour on met a jour les autres onglets
        
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text").strip()
                
    
        if tab_text == "Lignes":
           notebook_lines.update_input_frame_lignes(self) 
           self.clicked_points = []
           self.mbtiles_manager.clear_temp_line()             
        #load_lines(self)      
                  
        elif tab_text == "Polygones":
            notebook_polygones.update_onglet_polygones(self)            
            self.clicked_points = []
            self.mbtiles_manager.clear_temp_line()

        elif tab_text == "Points":            
            self.clicked_points = []
            self.mbtiles_manager.clear_temp_line()
    
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
        importer_menu.add_command(label="Importer fichier .kml", command=lambda: viewer.fonction_temporaire())
        importer_menu.add_command(label="Importer fichier .csv", command=lambda: viewer.fonction_temporaire())        
        importer_menu.add_command(label="Importer fichier .geojson", command=lambda: viewer.fonction_temporaire())
        self.menu_bar.add_cascade(label="Importer", menu=importer_menu)


        # Menu : "Exporter"        
        exporter_menu = Menu(self.menu_bar, tearoff=0)
        exporter_menu.add_command(label="Exporter vers .kml", command=lambda: viewer.fonction_temporaire())
        exporter_menu.add_command(label="Exporter vers .csv", command=lambda: viewer.fonction_temporaire()) 
        exporter_menu.add_command(label="Exporter vers .geojson", command=lambda: viewer.fonction_temporaire())       
        self.menu_bar.add_cascade(label="Exporter", menu=exporter_menu)

        # Menu : "Aide"
        # aide_menu = Menu(self.menu_bar, tearoff=0)
        # aide_menu.add_command(label="Fichier Aide", command=lambda: viewer.fonction_temporaire())
        # aide_menu.add_command(label="Supprimer les Tooltips", command=lambda: self.toggle_tooltips())    
        # self.menu_bar.add_cascade(label="Aide", menu=aide_menu)

        aide_menu = Menu(self.menu_bar, tearoff=0)
        aide_menu.add_command(label="Fichier Aide", command=lambda: viewer.fonction_temporaire())
        self.tooltips_menu_index = aide_menu.add_command(label="Masquer les Tooltips", command=lambda: self.toggle_tooltips())
        self.aide_menu = aide_menu  # Stocker l'aide_menu pour l'utiliser plus tard
        self.menu_bar.add_cascade(label="Aide", menu=aide_menu)


        # Ajoute le menu dans la fenêtre principale
        self.root.config(menu=self.menu_bar)
  
    def setup_ui(self):
        """Crée l'interface utilisateur"""

        # Création de la barre de statut
        self.status_bar = tk.Label(self.root, text="Translation : Clic gauche maintenu et déplacement de la souris | Zoom : Molette de la souris", bd=1, relief=tk.SUNKEN, anchor=tk.E, padx=5, pady=2)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Création du cadre principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Création du notebook (côté gauche) contenant les onglets
        self.notebook = ttk.Notebook(self.main_frame, width=350)
        self.notebook.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 2), pady=(5, 5))  # Padding pour éviter le chevauchement
        self.notebook.pack_propagate(False)

        # Création du canvas (côté droit) pour l'affichage des cartes
        self.canvas = tk.Canvas(self.main_frame, bg="lightgray", relief=tk.GROOVE, borderwidth=2)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(2, 5), pady=(5, 5))

        # Création de l'onglet points du notebook
        notebook_points.setup_points_tabs(self)

        # Création de l'onglet lignes du notebook
        notebook_lines.setup_lignes_tabs(self)

        # Création de l'onglet polygones du notebook
        notebook_polygones.setup_polygones_tabs(self)     

    def __init__(self, root):        

        #Variable : Position et altitude du hotspot Foreflight
        self.hotspot_x = tk.DoubleVar(value=0.5)
        self.hotspot_y = tk.DoubleVar(value=0.5) 
        self.altitude = tk.DoubleVar(value=0.0)    

        # Fenêtre tkinter : Initialisation
        self.root = root        
        self.root.title("Préparation Mission")

        # Fenêtre tkinter : Taille et positionnement
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = int(screen_width * 0.8)
        height = int(screen_height * 0.8)
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
    root = tk.Tk()
    app = MBTilesViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
