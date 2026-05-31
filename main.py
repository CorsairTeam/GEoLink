import os
import tkinter as tk
from tkinter import Menu, ttk, filedialog
from mbtiles_manager import MbtilesManager
import database
import notebook

# Ligne de commande compilation : pyinstaller --noconsole main.py


class MBTilesViewer:
    # fonction d'attente pour les commandes du menu
    def fonction_temporaire():
        pass

    def __init__(self, root, map_path_init):
        """
        self : instance de la classe MBTilesViewer\n
        root : fenêtre tkinter\n
        map_path_init : carte MBTiles sélectionnée"""

        # Formatage de la fenêtre tkinter
        self.root = root
        self.map_path_init = map_path_init
        self.root.title("Préparation Mission")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = int(screen_width * 0.8)
        height = int(screen_height * 0.8)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Instancie la classe MbtilesManager et lui passe une référence à l'instance principale
        self.mbtiles_manager = MbtilesManager(self)

        # Génération des menus de la fenêtre principale
        self.setup_menu()

        # Initialisation des bases SQLite uniquement si elles n'existent pas déjà
        if not all(
            os.path.exists(db_file)
            for db_file in ["points.db", "lignes.db", "polygones.db"]
        ):
            database.create_database()

        # Création de l'interface utilisateur
        self.setup_ui()

        # Gérer la fermeture du programme en effacant les bases de données
        self.root.protocol("WM_DELETE_WINDOW", lambda: database.database_closing(self))

    def setup_ui(self):
        """Crée l'interface utilisateur"""
        # Frame principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook à gauche de largeur fixe 350px
        self.notebook = ttk.Notebook(self.main_frame, width=350)
        self.notebook.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 2), pady=(5, 5))
        self.notebook.pack_propagate(False)

        # Canvas à droite complétant l'espace restant
        self.canvas = tk.Canvas(
            self.main_frame, bg="lightgray", relief=tk.GROOVE, borderwidth=2
        )
        self.canvas.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(2, 5), pady=(5, 5)
        )

        # Status Bar
        self.status_bar = tk.Label(
            self.root,
            text="Barre de statut",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.E,
            padx=5,
            pady=2,
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Création de l'onglet points du notebook
        notebook.setup_points_tabs(self)

    def setup_menu(self):
        """Gestion des options du menu"""

        # fonction d'attente pour les commandes du menu
        def fonction_temporaire():
            pass

        # Instanciation du menu de ma fenêtre principale
        self.menu_bar = Menu(self.root)

        # Création du menu "Cartes"
        cartes_menu = Menu(self.menu_bar, tearoff=0)
        cartes_menu.add_command(
            label="Charger Carte MBTiles", command=lambda: fonction_temporaire()
        )
        cartes_menu.add_command(
            label="Fermer Carte", command=lambda: fonction_temporaire()
        )
        self.menu_bar.add_cascade(label="Cartes", menu=cartes_menu)

        # Création du menu "Couches"
        couches_menu = Menu(self.menu_bar, tearoff=0)
        gestion_kml_menu = Menu(couches_menu, tearoff=0)
        gestion_kml_menu.add_command(
            label="Importer fichier .kml", command=lambda: fonction_temporaire()
        )
        gestion_kml_menu.add_command(
            label="Exporter objets selectionnés ", command=lambda: fonction_temporaire()
        )
        gestion_kml_menu.add_command(
            label="Export all ", command=lambda: fonction_temporaire()
        )
        couches_menu.add_cascade(label="Fichiers KML", menu=gestion_kml_menu)
        gestion_csv_menu = Menu(couches_menu, tearoff=0)
        gestion_csv_menu.add_command(
            label="Importer fichier .csv", command=lambda: fonction_temporaire()
        )
        gestion_csv_menu.add_command(
            label="Exporter points selectionnés ", command=lambda: fonction_temporaire()
        )
        gestion_csv_menu.add_command(
            label="Export all ", command=lambda: fonction_temporaire()
        )
        couches_menu.add_cascade(label="Fichiers CSV", menu=gestion_csv_menu)
        gestion_mbtiles_menu = Menu(couches_menu, tearoff=0)
        gestion_mbtiles_menu.add_command(
            label="Exporter objets selectionnés ", command=lambda: fonction_temporaire()
        )
        gestion_mbtiles_menu.add_command(
            label="Export all ", command=lambda: fonction_temporaire()
        )
        couches_menu.add_cascade(label="Fichiers MBTiles", menu=gestion_mbtiles_menu)
        gestion_geojson_menu = Menu(couches_menu, tearoff=0)
        gestion_geojson_menu.add_command(
            label="Exporter objets selectionnés ", command=lambda: fonction_temporaire()
        )
        gestion_geojson_menu.add_command(
            label="Export all ", command=lambda: fonction_temporaire()
        )
        couches_menu.add_cascade(label="Fichiers GeoJSON", menu=gestion_geojson_menu)
        self.menu_bar.add_cascade(label="Couches", menu=couches_menu)

        # Aide menu
        aide_menu = Menu(self.menu_bar, tearoff=0)
        aide_menu.add_command(
            label="Fichier Aide", command=lambda: fonction_temporaire()
        )
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
