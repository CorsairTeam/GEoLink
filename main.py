import os
import tkinter as tk
from tkinter import Menu, ttk, filedialog
from mbtiles_manager import MbtilesManager
import database
import notebook_points
import notebook_lines
import notebook_polygones

# Ligne de commande compilation : pyinstaller --noconsole main.py

class MBTilesViewer:
    
    def fonction_temporaire(self):
        pass

    def on_tab_changed(self, event):
        """Gérer le changement d'onglet"""
        #L'onglet point est toujours a jour on synchronise les autres onglets
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text").strip()
        print(f"Tab text: '{tab_text}'")        
    
        if tab_text == "Lignes":
           notebook_lines.update_input_frame_lignes(self)        
        #load_lines(self)      
                  
        elif tab_text == "Polygones":
            notebook_polygones.update_onglet_polygones(self)
        # Si on quitte l'onglet lignes, nettoyer la ligne temporaire
        #self.clicked_points = []
        #clear_temp_line(self)

        elif tab_text == "Points":
            # Si on quitte l'onglet lignes, nettoyer la ligne temporaire
            #self.clicked_points = []
            #clear_temp_line(self)  
            pass          
        
    def __init__(self, root, map_path_init):        

        #Variable : Chemin de la carte MBTiles initiale
        self.map_path_init = map_path_init

        #Variable : Position et altitude du hotspot
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

        # Instancie la classe MbtilesManager et lui passe une référence à l'instance principale
        self.mbtiles_manager = MbtilesManager(self)

        # Création des menus de la fenêtre principale
        self.setup_menu()

        # Création des bases SQLite (si non existantes)
        if not all(os.path.exists(db_file) for db_file in ["points.db", "lignes.db", "polygones.db"]):
            database.create_database()

        # Création de l'interface utilisateur
        self.setup_ui()

        # Gestion des événements
        self.notebook.bind("<<NotebookTabChanged>>",lambda event: self.on_tab_changed(event))        
        self.root.protocol("WM_DELETE_WINDOW", lambda: database.database_closing(self))

    def setup_ui(self):
        """Crée l'interface utilisateur"""

        # Création du cadre principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Création du notebook (côté gauche) contenant les onglets
        self.notebook = ttk.Notebook(self.main_frame, width=350)
        self.notebook.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 2), pady=(5, 5))
        self.notebook.pack_propagate(False)

        # Création du canvas (côté droit) pour l'affichage des cartes
        self.canvas = tk.Canvas(self.main_frame, bg="lightgray", relief=tk.GROOVE, borderwidth=2)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(2, 5), pady=(5, 5))

        # Création de la barre de statut
        self.status_bar = tk.Label(self.root,text="Barre de statut",bd=1,relief=tk.SUNKEN,anchor=tk.E, padx=5,pady=2)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Création de l'onglet points du notebook
        notebook_points.setup_points_tabs(self)

        # Création de l'onglet lignes du notebook
        notebook_lines.setup_lignes_tabs(self)

        # Création de l'onglet polygones du notebook
        notebook_polygones.setup_polygones_tabs(self)       
        

    def setup_menu(self):
        """Gestion des options du menu"""
        
        # Instanciation du menu 
        self.menu_bar = Menu(self.root)

        # Menu : "Cartes"
        cartes_menu = Menu(self.menu_bar, tearoff=0)
        cartes_menu.add_command(label="Charger Carte MBTiles", command=lambda: viewer.fonction_temporaire())
        cartes_menu.add_command(label="Fermer Carte", command=lambda: viewer.fonction_temporaire())
        self.menu_bar.add_cascade(label="Cartes", menu=cartes_menu)

        # Menu : "Couches"
        couches_menu = Menu(self.menu_bar, tearoff=0)
        gestion_kml_menu = Menu(couches_menu, tearoff=0)
        gestion_kml_menu.add_command(label="Importer fichier .kml", command=lambda: viewer.fonction_temporaire())
        gestion_kml_menu.add_command(label="Exporter objets selectionnés ", command=lambda: viewer.fonction_temporaire())
        gestion_kml_menu.add_command(label="Export all ", command=lambda: viewer.fonction_temporaire())
        couches_menu.add_cascade(label="Fichiers KML", menu=gestion_kml_menu)
        
        gestion_csv_menu = Menu(couches_menu, tearoff=0)
        gestion_csv_menu.add_command(label="Importer fichier .csv", command=lambda: viewer.fonction_temporaire())
        gestion_csv_menu.add_command(label="Exporter points selectionnés ", command=lambda: viewer.fonction_temporaire())
        gestion_csv_menu.add_command(label="Export all ", command=lambda: viewer.fonction_temporaire())
        couches_menu.add_cascade(label="Fichiers CSV", menu=gestion_csv_menu)

        gestion_mbtiles_menu = Menu(couches_menu, tearoff=0)
        gestion_mbtiles_menu.add_command(label="Exporter objets selectionnés ", command=lambda: viewer.fonction_temporaire())
        gestion_mbtiles_menu.add_command(label="Export all ", command=lambda: viewer.fonction_temporaire())
        couches_menu.add_cascade(label="Fichiers MBTiles", menu=gestion_mbtiles_menu)
        
        gestion_geojson_menu = Menu(couches_menu, tearoff=0)
        gestion_geojson_menu.add_command(label="Exporter objets selectionnés ", command=lambda: viewer.fonction_temporaire())
        gestion_geojson_menu.add_command(label="Export all ", command=lambda: viewer.fonction_temporaire())
        couches_menu.add_cascade(label="Fichiers GeoJSON", menu=gestion_geojson_menu)
        self.menu_bar.add_cascade(label="Couches", menu=couches_menu)

        # Menu : "Aide"
        aide_menu = Menu(self.menu_bar, tearoff=0)
        aide_menu.add_command(label="Fichier Aide", command=lambda: viewer.fonction_temporaire())
        aide_menu.add_command(label="Supprimer les Tooltips", command=lambda: viewer.fonction_temporaire())
    
        self.menu_bar.add_cascade(label="Aide", menu=aide_menu)

        # Ajoute le menu dans la fenêtre principale
        self.root.config(menu=self.menu_bar)
  
def choisir_carte():
    root = tk.Tk()
    root.withdraw()  # cache la fenêtre principale
    map_path = filedialog.askopenfilename(
        title="Choisir une carte MBTiles",
        filetypes=[("MBTiles", "*.mbtiles"), ("Tous les fichiers", "*.*")],
    )
    root.destroy()
    return map_path

def main():
    # Selection de la carte MBTiles à charger
    map_path_init = "Retirer le commentaire"  # choisir_carte()
    if not map_path_init:
        print("Aucune carte sélectionnée, arrêt du programme.")
        return

    root = tk.Tk()
    app = MBTilesViewer(root, map_path_init)
    root.mainloop()

if __name__ == "__main__":
    main()
