from utility import ToolTip
from tkinter import ttk
import tkinter as tk
import points_manager
import database


def update_input_frame(viewer):
    """MAJ du frame de saisie (input_frame) selon le type de coordonnées choisies"""

    # Effacer le contenu de input_frame
    for widget in viewer.input_frame.winfo_children():
        widget.destroy()

    # Configurer la colonne 1 pour qu'elle s'étende
    viewer.input_frame.grid_columnconfigure(1, weight=1)

    # Nom
    tk.Label(viewer.input_frame, text="Nom :", width=18, anchor="w").grid(
        row=0, column=0, padx=5, pady=5
    )
    viewer.nom_entry = tk.Entry(viewer.input_frame)
    viewer.nom_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")

    # Taille
    tk.Label(viewer.input_frame, text="Taille :", width=18, anchor="w").grid(
        row=1, column=0, padx=5, pady=5
    )
    viewer.taille_entry = tk.Entry(viewer.input_frame)
    viewer.taille_entry.grid(row=1, column=1, padx=(0, 10), sticky="ew")

    # Couleur
    tk.Label(viewer.input_frame, text="Couleur : ", width=18, anchor="w").grid(
        row=2, column=0, padx=5, pady=5
    )
    colors = [
        "Rouge",
        "Vert",
        "Bleu",
        "Jaune",
        "Orange",
        "Cyan",
        "Magenta",
        "Noir",
        "Blanc",
    ]
    viewer.line_color_entry = ttk.Combobox(
        viewer.input_frame, values=colors, state="readonly", justify="center"
    )
    viewer.line_color_entry.current(0)
    viewer.line_color_entry.grid(row=2, column=1, padx=(0, 10), sticky="ew")

    # Type de points
    tk.Label(viewer.input_frame, text="Type de points : ", width=18, anchor="w").grid(
        row=3, column=0, padx=5, pady=5
    )
    type_points = ["Cercle", "Carré", "Cible", "Epingle"]
    viewer.type_points_entry = ttk.Combobox(
        viewer.input_frame, values=type_points, state="readonly", justify="center"
    )
    viewer.type_points_entry.current(0)
    viewer.type_points_entry.grid(row=3, column=1, padx=(0, 10), sticky="ew")

    # Couleur de fond du label
    tk.Label(viewer.input_frame, text="Couleur du label : ", width=18, anchor="w").grid(
        row=4, column=0, padx=5, pady=5
    )
    colors = [
        "Rouge",
        "Vert",
        "Bleu",
        "Jaune",
        "Orange",
        "Cyan",
        "Magenta",
        "Noir",
        "Blanc",
    ]
    viewer.label_color_entry = ttk.Combobox(
        viewer.input_frame, values=colors, state="readonly", justify="center"
    )
    viewer.label_color_entry.current(0)
    viewer.label_color_entry.grid(row=4, column=1, padx=(0, 10), sticky="ew")

    # Affiche les widgets d'entree des coordonnees en fonction du format des coordonnees
    if viewer.creation_mode.get() == "coordonnees":
        if viewer.coord_type.get() == "Degrés":
            # Latitude
            tk.Label(viewer.input_frame, text="Latitude :", width=18, anchor="w").grid(
                row=5, column=0, padx=5, pady=5
            )
            viewer.lat_entry = tk.Entry(viewer.input_frame, width=25)
            viewer.lat_entry.grid(row=5, column=1, padx=(0, 10), sticky="ew")

            # Longitude
            tk.Label(viewer.input_frame, text="Longitude :", width=18, anchor="w").grid(
                row=6, column=0, padx=5, pady=5
            )
            viewer.lon_entry = tk.Entry(viewer.input_frame, width=25)
            viewer.lon_entry.grid(row=6, column=1, padx=(0, 10), sticky="ew")

            # Bouton créer
            tk.Button(
                viewer.input_frame,
                text="Créer le point",
                command=lambda: database.create_point_from_coords(viewer),
            ).grid(row=7, column=1, columnspan=2, sticky="ew", pady=5, padx=(0, 10))

            # Bind pour validation en temps réel
            viewer.lat_entry.bind(
                "<KeyRelease>", lambda e: viewer.fonction_temporaire()
            )  # Validate.validate_coords(viewer))
            viewer.lon_entry.bind(
                "<KeyRelease>", lambda e: viewer.fonction_temporaire()
            )  # Validate.validate_coords(viewer))

        elif viewer.coord_type.get() == "Degrés/Minutes":
            # Latitude
            tk.Label(viewer.input_frame, text="Latitude :", width=18, anchor="w").grid(
                row=5, column=0, padx=5, pady=5
            )
            lat_frame = tk.Frame(viewer.input_frame)
            lat_frame.grid(row=5, column=1, padx=(0, 10), sticky="ew")

            viewer.lat_ns_combo = ttk.Combobox(
                lat_frame, values=["N", "S"], width=3, state="readonly"
            )
            viewer.lat_ns_combo.grid(row=0, column=0, padx=(0, 2), sticky="w")
            viewer.lat_ns_combo.set("N")

            viewer.lat_deg_entry = tk.Entry(lat_frame, width=8)
            viewer.lat_deg_entry.grid(row=0, column=1, padx=(6, 3), sticky="w")

            tk.Label(lat_frame, text="°", width=1).grid(row=0, column=2, sticky="w")

            viewer.lat_min_entry = tk.Entry(lat_frame, width=8)
            viewer.lat_min_entry.grid(row=0, column=3, padx=(3, 3), sticky="w")

            tk.Label(lat_frame, text="'", width=1).grid(row=0, column=4, sticky="w")

            # Longitude
            tk.Label(viewer.input_frame, text="Longitude :", width=18, anchor="w").grid(
                row=6, column=0, padx=5, pady=5
            )
            lon_frame = tk.Frame(viewer.input_frame)
            lon_frame.grid(row=6, column=1, padx=(0, 10), sticky="ew")

            viewer.lon_ew_combo = ttk.Combobox(
                lon_frame, values=["E", "O"], width=3, state="readonly"
            )
            viewer.lon_ew_combo.grid(row=0, column=0, padx=(0, 2), sticky="w")
            viewer.lon_ew_combo.set("E")

            viewer.lon_deg_entry = tk.Entry(lon_frame, width=8)
            viewer.lon_deg_entry.grid(row=0, column=1, padx=(6, 3), sticky="w")

            tk.Label(lon_frame, text="°", width=1).grid(row=0, column=2, sticky="w")

            viewer.lon_min_entry = tk.Entry(lon_frame, width=8)
            viewer.lon_min_entry.grid(row=0, column=3, padx=(3, 3), sticky="w")

            tk.Label(lon_frame, text="'", width=1).grid(row=0, column=4, sticky="w")

            # Bouton créer
            tk.Button(
                viewer.input_frame,
                text="Créer le point",
                command=lambda: viewer.fonction_temporaire(),
            ).grid(row=7, column=1, columnspan=2, sticky="ew", pady=5, padx=(0, 10))

            # Bind pour validation
            viewer.lat_deg_entry.bind(
                "<KeyRelease>", lambda e: viewer.fonction_temporaire()
            )
            viewer.lat_min_entry.bind(
                "<KeyRelease>", lambda e: viewer.fonction_temporaire()
            )
            viewer.lon_deg_entry.bind(
                "<KeyRelease>", lambda e: viewer.fonction_temporaire()
            )
            viewer.lon_min_entry.bind(
                "<KeyRelease>", lambda e: viewer.fonction_temporaire()
            )

        elif viewer.coord_type.get() == "Degrés/Minutes/Secondes":
            # Latitude
            tk.Label(viewer.input_frame, text="Latitude :", width=18, anchor="w").grid(
                row=5, column=0, padx=5, pady=5
            )
            lat_frame = tk.Frame(viewer.input_frame)
            lat_frame.grid(row=5, column=1, padx=(0, 10), sticky="ew")

            viewer.lat_ns_combo = ttk.Combobox(
                lat_frame, values=["N", "S"], width=2, state="readonly"
            )
            viewer.lat_ns_combo.grid(row=0, column=0, padx=(0, 2), sticky="w")
            viewer.lat_ns_combo.set("N")
            viewer.lat_deg_entry = tk.Entry(lat_frame, width=5)
            viewer.lat_deg_entry.grid(row=0, column=1, padx=(6, 3), sticky="w")
            tk.Label(lat_frame, text="°").grid(row=0, column=2, padx=1, pady=5)
            viewer.lat_min_entry = tk.Entry(lat_frame, width=5)
            viewer.lat_min_entry.grid(row=0, column=3, padx=1, pady=5)
            tk.Label(lat_frame, text="'").grid(row=0, column=4, padx=1, pady=5)
            viewer.lat_sec_entry = tk.Entry(lat_frame, width=5)
            viewer.lat_sec_entry.grid(row=0, column=5, padx=1, pady=5)

            tk.Label(lat_frame, text='"').grid(row=0, column=6, padx=1, pady=5)

            # Longitude
            tk.Label(viewer.input_frame, text="Longitude :", width=18, anchor="w").grid(
                row=6, column=0, padx=5, pady=5
            )
            # Creation d'un cadre contenant des colonnes décorellées
            lon_frame = tk.Frame(viewer.input_frame)
            lon_frame.grid(row=6, column=1, padx=(0, 10), sticky="ew")

            viewer.lon_ew_combo = ttk.Combobox(
                lon_frame, values=["E", "O"], width=2, state="readonly"
            )
            viewer.lon_ew_combo.grid(row=0, column=0, padx=(0, 2))
            viewer.lon_ew_combo.set("E")

            viewer.lon_deg_entry = tk.Entry(lon_frame, width=5)
            viewer.lon_deg_entry.grid(row=0, column=1, padx=(6, 3))

            tk.Label(lon_frame, text="°").grid(row=0, column=2, padx=1, pady=5)

            viewer.lon_min_entry = tk.Entry(lon_frame, width=5)
            viewer.lon_min_entry.grid(row=0, column=3, padx=1, pady=5)

            tk.Label(lon_frame, text="'").grid(row=0, column=4, padx=1, pady=5)

            viewer.lon_sec_entry = tk.Entry(lon_frame, width=5)
            viewer.lon_sec_entry.grid(row=0, column=5, padx=1, pady=5)

            tk.Label(lon_frame, text='"').grid(row=0, column=6, padx=1, pady=5)

            # Bouton créer
            tk.Button(
                viewer.input_frame,
                text="Créer le point",
                command=lambda: viewer.fonction_temporaire(),
            ).grid(row=7, column=1, columnspan=2, sticky="ew", pady=5, padx=(0, 10))

            # Bind pour validation
            viewer.lat_deg_entry.bind(
                "<KeyRelease>", lambda e: Validate.validate_deg_min_sec(viewer)
            )
            viewer.lat_min_entry.bind(
                "<KeyRelease>", lambda e: Validate.validate_deg_min_sec(viewer)
            )
            viewer.lat_sec_entry.bind(
                "<KeyRelease>", lambda e: Validate.validate_deg_min_sec(viewer)
            )
            viewer.lon_deg_entry.bind(
                "<KeyRelease>", lambda e: Validate.validate_deg_min_sec(viewer)
            )
            viewer.lon_min_entry.bind(
                "<KeyRelease>", lambda e: Validate.validate_deg_min_sec(viewer)
            )
            viewer.lon_sec_entry.bind(
                "<KeyRelease>", lambda e: Validate.validate_deg_min_sec(viewer)
            )

        elif viewer.coord_type.get() == "Calamar":
            # Axe X (correspond à Y dans Calamar)
            tk.Label(viewer.input_frame, text="Axe Y :", width=18, anchor="w").grid(
                row=5, column=0, padx=5, pady=5
            )
            X_frame = tk.Frame(viewer.input_frame)
            X_frame.grid(row=5, column=1, padx=(0, 10), sticky="ew")

            viewer.calamar_x_entry = tk.Entry(X_frame, width=15)
            viewer.calamar_x_entry.grid(row=0, column=0, padx=(0, 20), sticky="w")
            viewer.calamar_x_combo = ttk.Combobox(
                X_frame, values=["mD", "mG"], width=7, state="readonly"
            )
            viewer.calamar_x_combo.grid(row=0, column=1, padx=(6, 3), sticky="w")
            viewer.calamar_x_combo.set("mD")

            # Axe Y (correspond à X dans Calamar)
            tk.Label(viewer.input_frame, text="Axe X :", width=18, anchor="w").grid(
                row=6, column=0, padx=5, pady=5
            )
            Y_frame = tk.Frame(viewer.input_frame)
            Y_frame.grid(row=6, column=1, padx=(0, 10), sticky="ew")

            viewer.calamar_y_entry = tk.Entry(Y_frame, width=15)
            viewer.calamar_y_entry.grid(row=0, column=0, padx=(0, 20), sticky="w")
            viewer.calamar_y_combo = ttk.Combobox(
                Y_frame, values=["mL", "mC"], width=7, state="readonly"
            )
            viewer.calamar_y_combo.grid(row=0, column=1, padx=(6, 3), sticky="w")
            viewer.calamar_y_combo.set("mL")

            # Bouton créer
            tk.Button(
                viewer.input_frame,
                text="Créer le point",
                command=lambda: viewer.fonction_temporaire(),
            ).grid(row=7, column=1, columnspan=2, sticky="ew", pady=5, padx=(0, 10))

            # Bind pour validation
            viewer.calamar_y_entry.bind(
                "<KeyRelease>", lambda e: Validate.validate_calamar(viewer)
            )
            viewer.calamar_x_entry.bind(
                "<KeyRelease>", lambda e: Validate.validate_calamar(viewer)
            )

    elif viewer.creation_mode.get() == "radial":
        # Vérifier s'il y a des points disponibles
        # conn = sqlite3.connect("point.db")
        # cursor = conn.cursor()
        # cursor.execute("SELECT name FROM points")
        # points = [row[0] for row in cursor.fetchall()]
        # conn.close()

        points = []  # Remplacez par la liste réelle des points disponibles

        if not points:
            # Point de départ

            tk.Label(
                viewer.input_frame, text="Point de départ :", width=18, anchor="w"
            ).grid(row=5, column=0, sticky="w", padx=5, pady=5)
            viewer.radial_point_combo = ttk.Combobox(
                viewer.input_frame, values=points, state="readonly"
            )
            viewer.radial_point_combo.grid(row=5, column=1, padx=(0, 10), sticky="ew")
            if points:
                viewer.radial_point_combo.set(points[0])

            # Distance

            tk.Label(viewer.input_frame, text="Distance :", width=18, anchor="w").grid(
                row=6, column=0, padx=5, pady=5
            )
            # Creation d'un cadre contenant les colonnes
            distance_frame = tk.Frame(viewer.input_frame)
            distance_frame.grid(row=6, column=1, padx=(0, 10), sticky="ew")

            viewer.radial_distance_entry = tk.Entry(distance_frame, width=14)
            viewer.radial_distance_entry.grid(row=0, column=0, padx=(0, 12), sticky="w")

            viewer.radial_distance_combo = ttk.Combobox(
                distance_frame,
                justify="center",
                values=["mètres", "nautiques"],
                width=10,
                state="readonly",
            )
            viewer.radial_distance_combo.grid(row=0, column=1, padx=(0, 2), sticky="w")
            viewer.radial_distance_combo.set("mètres")

            # Gisement

            tk.Label(
                viewer.input_frame, text="Gisement (°) :", width=18, anchor="w"
            ).grid(row=7, column=0, padx=5, pady=5)
            # Creation d'un cadre contenant les colonnes
            gisement_frame = tk.Frame(viewer.input_frame)
            gisement_frame.grid(row=7, column=1, padx=(0, 10), sticky="ew")

            viewer.radial_bearing_entry = tk.Entry(gisement_frame, width=14)
            viewer.radial_bearing_entry.grid(row=0, column=0, padx=(0, 15), sticky="w")

            tk.Label(gisement_frame, text="0-359°").grid(
                row=0, column=1, padx=5, pady=5, sticky="w"
            )

            # Bouton créer
            tk.Button(
                viewer.input_frame,
                text="Créer le point",
                command=lambda: viewer.fonction_temporaire(viewer),
            ).grid(row=8, column=1, columnspan=2, sticky="ew", pady=5, padx=5)

            # Bind pour validation
            viewer.radial_distance_entry.bind(
                "<KeyRelease>", lambda e: Validate.validate_radial(viewer)
            )
            viewer.radial_bearing_entry.bind(
                "<KeyRelease>", lambda e: Validate.validate_radial(viewer)
            )
        else:
            tk.Label(
                viewer.input_frame,
                text="Créez d'abord un point de référence",
                fg="gray",
            ).pack(pady=(10, 10))

    elif viewer.creation_mode.get() == "click":
        # Latitude
        tk.Label(viewer.input_frame, text="Latitude :", width=18, anchor="w").grid(
            row=5, column=0, padx=5, pady=5
        )
        viewer.click_lat_entry = tk.Entry(viewer.input_frame, state="readonly")
        viewer.click_lat_entry.grid(row=5, column=1, padx=(0, 10), sticky="ew")

        # Longitude
        tk.Label(viewer.input_frame, text="Longitude :", width=18, anchor="w").grid(
            row=6, column=0, padx=5, pady=5
        )
        viewer.click_lon_entry = tk.Entry(viewer.input_frame, state="readonly")
        viewer.click_lon_entry.grid(row=6, column=1, padx=(0, 10), sticky="ew")

        # Bouton créer
        tk.Button(
            viewer.input_frame,
            text="Créer le point",
            command=lambda: viewer.fonction_temporaire(),
        ).grid(row=7, column=1, columnspan=2, sticky="ew", pady=5, padx=(0, 10))

    else:
        viewer.coord_combo.pack_forget()  # A COMPRENDRE


def setup_points_tabs(viewer):
    """Créer l'onglet point du notebook"""

    # Variable pour récuperer les choix de l'utilisateur ouverture par defaut "coordonnees/Degrés"
    viewer.creation_mode = tk.StringVar(value="coordonnees")
    viewer.coord_type = tk.StringVar(value="Degrés")

    # Configurer le style de l'onglet
    style = ttk.Style()
    style.configure("TNotebook.Tab", font=("Arial", 10))  # Onglet normal
    style.map(
        "TNotebook.Tab", font=[("selected", ("Arial", 10, "bold"))]
    )  # Onglet sélectionné en gras

    # Création de l'onglet Points
    points_frame = ttk.Frame(viewer.notebook)
    viewer.notebook.add(points_frame, text="  Points  ")

    # Frame pour selectionner le mode de création du point
    viewer.type_creation_frame = tk.Frame(points_frame, relief="groove", borderwidth=1)
    viewer.type_creation_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

    # Frame pour positionner les champs de saisie
    viewer.input_frame = tk.Frame(points_frame, relief="groove", borderwidth=1)
    viewer.input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Frame pour le Treeview
    viewer.treeview_frame = tk.Frame(points_frame, relief="groove", borderwidth=1)
    viewer.treeview_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

    # Remplissage de type_creation_frame
    viewer.type_creation_frame.grid_columnconfigure(1, weight=1)
    viewer.rb_coords = ttk.Radiobutton(
        viewer.type_creation_frame,
        text="Coordonnées",
        width=18,
        variable=viewer.creation_mode,
        value="coordonnees",
        command=lambda: update_input_frame(viewer),
    )
    viewer.rb_coords.grid(row=0, column=0, padx=5, pady=5)
    viewer.coord_combo = ttk.Combobox(
        viewer.type_creation_frame,
        textvariable=viewer.coord_type,
        values=["Degrés", "Degrés/Minutes", "Degrés/Minutes/Secondes", "Calamar"],
        state="readonly",
    )
    viewer.coord_combo.grid(row=0, column=1, padx=(0, 10), sticky="ew")
    viewer.coord_combo.bind(
        "<<ComboboxSelected>>", lambda e: update_input_frame(viewer)
    )

    rb_radial = ttk.Radiobutton(
        viewer.type_creation_frame,
        text="Radial distance",
        width=18,
        variable=viewer.creation_mode,
        value="radial",
        command=lambda: update_input_frame(viewer),
    )
    rb_radial.grid(row=1, column=0, padx=5, pady=5)

    rb_click = ttk.Radiobutton(
        viewer.type_creation_frame,
        text="Création sur la carte",
        width=18,
        variable=viewer.creation_mode,
        value="click",
        command=lambda: update_input_frame(viewer),
    )
    rb_click.grid(row=2, column=0, padx=5, pady=5)
    ToolTip(rb_click, "Clic droit pour récupérer les coordonnées")

    # Titre du tableau de points
    tk.Label(
        viewer.treeview_frame,
        text="Liste des points",
        anchor="center",
        font=("Arial", 10, "bold"),
    ).pack(pady=5, fill=tk.X, padx=5)

    # Création du Treeview
    viewer.tree = ttk.Treeview(
        viewer.treeview_frame, columns=("selected", "nom"), show="headings", height=10
    )
    viewer.tree.heading("selected", text="Export")
    viewer.tree.heading("nom", text="Nom")

    viewer.tree.column("selected", width=50, minwidth=50, stretch=False)
    viewer.tree.column("nom", width=100, minwidth=100, stretch=True)

    viewer.checked_items = {}
    viewer.tree.bind(
        "<Button-1>", lambda event: viewer.fonction_temporaire()
    )  # Selectionne le point
    viewer.tree.bind(
        "<Double-1>", lambda event: viewer.fonction_temporaire()
    )  # Centre l'affichage sur le point sélectionné
    viewer.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Création des boutons
    btn_select_all = ttk.Button(
        viewer.treeview_frame,
        text="Select All",
        width=16,
        command=lambda: viewer.fonction_temporaire(),
    )  # fonction d'attente pour les commandes du menu
    btn_select_all.pack(side=tk.LEFT, padx=5)
    btn_deselect_all = ttk.Button(
        viewer.treeview_frame,
        text="Deselect All",
        width=16,
        command=lambda: viewer.fonction_temporaire(),
    )  # fonction d'attente pour les commandes du menu
    btn_deselect_all.pack(side=tk.LEFT, padx=5)
    btn_delete = ttk.Button(
        viewer.treeview_frame,
        text="Delete",
        width=16,
        command=lambda: viewer.fonction_temporaire(),
    )  # fonction d'attente pour les commandes du menu
    btn_delete.pack(side=tk.LEFT, padx=5)

    # Remplissage du frame input_frame
    update_input_frame(viewer)
