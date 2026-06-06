
import tkinter as tk
from tkinter import ttk
from utility import ToolTip
import utility
import database

def setup_polygones_tabs(viewer):
    # Variable pour récuperer les choix de l'utilisateur ouverture par defaut "coordonnees/Degrés"
    viewer.polygone_creation_mode = tk.StringVar(value="points")

    # Création de l'onglet Ligne dans "ligne_frame"
    polygone_frame = ttk.Frame(viewer.notebook)
    viewer.notebook.add(polygone_frame, text="  Polygones  ")    

    # Frame pour selectionner le mode de création du point
    viewer.polygones_creation_frame = tk.Frame(polygone_frame, relief="groove", borderwidth=1)
    viewer.polygones_creation_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

    # Frame pour positionner les champs de saisie
    viewer.polygones_input_frame = tk.Frame(polygone_frame, relief="groove", borderwidth=1)
    viewer.polygones_input_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

    # Frame pour le Treeview
    viewer.polygones_treeview_frame = tk.Frame(polygone_frame, relief="groove", borderwidth=1)
    viewer.polygones_treeview_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, padx=5, pady=5)

    # Remplissage de type_creation_frame    
    ttk.Radiobutton(
        viewer.polygones_creation_frame,
        text="Utilisation des points de la base de données",
        width=40,
        variable=viewer.polygone_creation_mode,
        value="points",
        command=lambda: viewer.fonction_temporaire(viewer),
    ).grid(row=0, column=0, padx=5, pady=5) 

    ttk.Radiobutton(
        viewer.polygones_creation_frame,
        text="Tracé du polygone sur la carte",
        width=40,
        variable=viewer.polygone_creation_mode,
        value="carte",
        command=lambda: viewer.fonction_temporaire(viewer),
    ).grid(row=1, column=0, padx=5, pady=5)

    ttk.Radiobutton(
        viewer.polygones_creation_frame,
        text="Création d'un rectangle",
        width=40,
        variable=viewer.polygone_creation_mode,
        value="rectangle",
        command=lambda: viewer.fonction_temporaire(viewer),
    ).grid(row=2, column=0, padx=5, pady=5)

    ttk.Radiobutton(
        viewer.polygones_creation_frame,
        text="Création d'un cercle",
        width=40,
        variable=viewer.polygone_creation_mode,
        value="cercle",
        command=lambda: viewer.fonction_temporaire(viewer),
    ).grid(row=3, column=0, padx=5, pady=5)



    # Titre du tableau de points
    polygones_title_label = tk.Label(
        viewer.polygones_treeview_frame,
        text="Liste des polygones",
        anchor="center",
        font=("Arial", 10, "bold"),
    )
    polygones_title_label.pack(pady=5, fill=tk.X, padx=5)
    ToolTip(polygones_title_label, "● Clic sur le nom du polygone pour afficher ses informations dans le formulaire\n"
                                   "\u25CF Clic sur la case à cocher pour selectionner le polygone")
    

    # Création du Treeview
    viewer.polygones_tree = ttk.Treeview(viewer.polygones_treeview_frame, columns=("selected", "nom"), show="headings", height=10)
    viewer.polygones_tree.heading("selected", text="Export")
    viewer.polygones_tree.heading("nom", text="Nom")

    viewer.polygones_tree.column("selected", width=50, minwidth=50, stretch=False,anchor="center")
    viewer.polygones_tree.column("nom", width=100, minwidth=100, stretch=True,anchor="center")

    viewer.polygones_checked_items = {}
    viewer.polygones_tree.bind("<Button-1>", lambda event: viewer.fonction_temporaire())  # Selectionne le point
    viewer.polygones_tree.bind("<Double-1>", lambda event: viewer.fonction_temporaire())  # Centre l'affichage sur le point sélectionné
    viewer.polygones_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Création des boutons du treeview
    btn_select_all = ttk.Button(
        viewer.polygones_treeview_frame,
        text="Select All",
        width=16,
        command=lambda: utility.select_all_treeview(viewer.polygones_checked_items, viewer.polygones_tree),
    )  # fonction d'attente pour les commandes du menu
    btn_select_all.pack(side=tk.LEFT, padx=5)

    btn_deselect_all = ttk.Button(
        viewer.polygones_treeview_frame,
        text="Deselect All",
        width=16,
        command=lambda: utility.deselect_all_treeview(viewer.polygones_checked_items, viewer.polygones_tree),
    )  # fonction d'attente pour les commandes du menu
    btn_deselect_all.pack(side=tk.LEFT, padx=5)

    btn_delete = ttk.Button(
        viewer.polygones_treeview_frame,
        text="Delete",
        width=16,
        command=lambda: viewer.fonction_temporaire(),
    )  # fonction d'attente pour les commandes du menu
    btn_delete.pack(side=tk.LEFT, padx=5)