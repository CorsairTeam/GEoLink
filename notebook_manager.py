from utility import ToolTip
from tkinter import ttk
import tkinter as tk
import database
import sqlite3

def deselect_all_treeview(checked_items, treeview):
    """Décoche toutes les cases du treeview"""
    for item in checked_items:
        checked_items[item]["checked"] = False
        values = list(treeview.item(item)["values"])
        values[0] = "⬜"
        treeview.item(item, values=values)

def select_all_treeview(checked_items, treeview):
    """Coche toutes les cases du treeview"""
    for item in checked_items:
        checked_items[item]["checked"] = True
        values = list(treeview.item(item)["values"])
        values[0] = "✅"
        treeview.item(item, values=values)

def point_field_fill(viewer, item):
    """Remplit les champs du point cliqué dans le Tree view.\n
    Bascule dans la page de création par coordonnées"""
    
    data = viewer.points_checked_items[item]["data"]
    name, lat, lon, alt, scale, icon, color, hotspot_x, hotspot_y, label_color = data
    viewer.creation_mode.set("coordonnees")
    viewer.coord_type.set("Degrés")
    if hasattr(viewer, "coord_combo"):
        viewer.coord_combo.set("Degrés")
    update_input_frame_points(viewer)

    if hasattr(viewer, "nom_entry"):
        viewer.nom_entry.delete(0, tk.END)
        viewer.nom_entry.insert(0, name)

    if hasattr(viewer, "taille_entry"):
        viewer.taille_entry.delete(0, tk.END)
        viewer.taille_entry.insert(0, f"{scale:g}")

    if hasattr(viewer, "point_color_entry"):
        viewer.point_color_entry.set(color)

    if hasattr(viewer, "type_points_entry"):
        viewer.type_points_entry.set(icon)

    if hasattr(viewer, "label_color_entry"):
        viewer.label_color_entry.set(label_color)

    if hasattr(viewer, "lat_entry"):
        viewer.lat_entry.delete(0, tk.END)
        viewer.lat_entry.insert(0, f"{lat:g}")

    if hasattr(viewer, "lon_entry"):
        viewer.lon_entry.delete(0, tk.END)
        viewer.lon_entry.insert(0, f"{lon:g}")

def on_tree_click(viewer, event):
    """En fonctiondu clic, coche la case ou remplit les champs de Input_frame"""
    region = viewer.tree.identify_region(event.x, event.y)
    if region == "cell":
        item = viewer.tree.identify_row(event.y)
        column = viewer.tree.identify_column(event.x)
        
        if column == "#1" and item in viewer.points_checked_items:
            toggle_checkbox(viewer, item)

        if column == "#2" and item in viewer.points_checked_items:
            point_field_fill(viewer, item)

def toggle_checkbox(viewer, item):
    """Gère le cochage/décochage de la coche du Treeview"""
    #Structure de  checked_items I00_": {"checked": False,"data": (...)}
    current_state = viewer.points_checked_items[item]["checked"]
    new_state = not current_state
    viewer.points_checked_items[item]["checked"] = new_state
    
    values = list(viewer.tree.item(item)["values"])
    values[0] = "✅" if new_state else "⬜"
    viewer.tree.item(item, values=values)

def update_input_frame_lignes(viewer):
    """Mettre à jour l'interface selon le mode de création sélectionné"""    

    # Vider le frame avant de reconfigurer
    for widget in viewer.ligne_points_transfer_frame.winfo_children():
        widget.destroy()

    if viewer.ligne_creation_mode.get() == "points":
    #On insere le Frame de transfert des points

        viewer.ligne_points_frame = tk.Frame( viewer.ligne_points_transfer_frame)
        viewer.ligne_points_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        viewer.ligne_points_frame.grid_columnconfigure(0, weight=1,uniform="listbox")
        viewer.ligne_points_frame.grid_columnconfigure(1, weight=0)
        viewer.ligne_points_frame.grid_columnconfigure(2, weight=1,uniform="listbox")

        left_frame = tk.Frame(viewer.ligne_points_frame)
        left_frame.grid(row=0, column=0, sticky="nsew")

        viewer.center_frame = tk.Frame(viewer.ligne_points_frame, width=40)
        viewer.center_frame.grid(row=0, column=1, sticky="ns", padx=5)
        viewer.center_frame.grid_propagate(False)

        right_frame = tk.Frame(viewer.ligne_points_frame)
        right_frame.grid(row=0, column=2, sticky="nsew")

        viewer.points_label = tk.Label(left_frame, text="Base de points", font=("Arial", 10),justify='center')
        viewer.points_label.pack(anchor=tk.CENTER, padx=(5, 5))
        viewer.points_listbox = tk.Listbox(left_frame, height=8)
        viewer.points_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 5), padx=(5, 5))        
        
        viewer.add_button = tk.Button(viewer.center_frame, text=">>", command=lambda: viewer.fonction_temporaire(), width=6)
        viewer.add_button.pack(pady=(50, 20))
        viewer.remove_button = tk.Button(viewer.center_frame, text="<<", command=lambda: viewer.fonction_temporaire(), width=6)
        viewer.remove_button.pack(pady=5)
        
        viewer.ligne_label = tk.Label(right_frame, text="Ligne", font=("Arial", 10),justify='center')
        viewer.ligne_label.pack(anchor=tk.CENTER, padx=(5, 5))
        viewer.line_points_listbox = tk.Listbox(right_frame, height=8)
        viewer.line_points_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 5), padx=(5, 5)) 

    elif viewer.ligne_creation_mode.get() == "carte":
        # Configurer la colonne 1 pour qu'elle s'étende
        viewer.ligne_points_transfer_frame.grid_columnconfigure(1, weight=1)

        # Longueur totale de la ligne
        tk.Label(viewer.ligne_points_transfer_frame, text="Longueur totale :", width=25, anchor="w").grid(row=0, column=0, padx=5, pady=5)
        viewer.line_length_entry = tk.Entry(viewer.ligne_points_transfer_frame, justify="center",state="readonly")
        viewer.line_length_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew") 

        # Longueur du dernier segment
        tk.Label(viewer.ligne_points_transfer_frame, text="Longueur du dernier segment :", width=25, anchor="w").grid(row=1, column=0, padx=5, pady=5)
        viewer.line_last_segment_length_entry = tk.Entry(viewer.ligne_points_transfer_frame, justify="center",state="readonly")
        viewer.line_last_segment_length_entry.grid(row=1, column=1, padx=(0, 10), sticky="ew")

        # Gisement du dernier segment
        tk.Label(viewer.ligne_points_transfer_frame, text="Gisement du dernier segment :", width=25, anchor="w").grid(row=2, column=0, padx=5, pady=5)
        viewer.line_last_segment_gisement_entry = tk.Entry(viewer.ligne_points_transfer_frame, justify="center",state="readonly")
        viewer.line_last_segment_gisement_entry.grid(row=2, column=1, padx=(0, 10), sticky="ew") 

    # Vider le frame avant de reconfigurer
    for widget in viewer.lines_input_frame.winfo_children():
        widget.destroy()

    # Configurer la colonne 1 pour qu'elle s'étende
    viewer.lines_input_frame.grid_columnconfigure(1, weight=1)

    # Nom
    tk.Label(viewer.lines_input_frame, text="Nom :", width=25, anchor="w").grid(row=0, column=0, padx=5, pady=5)
    viewer.line_name_entry = tk.Entry(viewer.lines_input_frame, justify="center")
    viewer.line_name_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew") 

    # Largeur
    tk.Label(viewer.lines_input_frame, text="Epaisseur de la ligne :", width=25, anchor="w").grid(row=1, column=0, padx=5, pady=5)
    taille_values = [str(i) for i in range(1, 11)]
    viewer.taille_entry = ttk.Combobox(viewer.lines_input_frame, values=taille_values, state="readonly", justify="center")
    viewer.taille_entry.set("1")
    viewer.taille_entry.grid(row=1, column=1, padx=(0, 10), sticky="ew")    

    # Couleur
    tk.Label(viewer.lines_input_frame, text="Couleur : ", width=25, anchor="w").grid(row=2, column=0, padx=5, pady=5)
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
    viewer.line_color_entry = ttk.Combobox(viewer.lines_input_frame, values=colors, state="readonly", justify="center")
    viewer.line_color_entry.current(0)
    viewer.line_color_entry.grid(row=2, column=1, padx=(0, 10), sticky="ew")  

    # Bouton créer
    tk.Button(
        viewer.lines_input_frame,
        text="Créer la ligne",
        command=lambda: viewer.fonction_temporaire(),
    ).grid(row=3, column=1, columnspan=2, sticky="ew", pady=5, padx=(0, 10))        
       

    # Charger les points depuis la base de données    
    database.load_points_line(viewer)
        
    # Réinitialiser les points cliqués
    #TODO: Réinitialiser les points cliqués

def update_input_frame_points(viewer):
    """MAJ du frame de saisie (input_frame) selon le type de coordonnées choisies"""

    # Effacer le contenu de input_frame
    for widget in viewer.input_frame.winfo_children():
        widget.destroy()        

    # Configurer la colonne 1 pour qu'elle s'étende
    viewer.input_frame.grid_columnconfigure(1, weight=1)

    # Nom
    tk.Label(viewer.input_frame, text="Nom :", width=18, anchor="w").grid(row=0, column=0, padx=5, pady=5)
    viewer.nom_entry = tk.Entry(viewer.input_frame, justify="center")
    viewer.nom_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")

    # Taille
    tk.Label(viewer.input_frame, text="Taille :", width=18, anchor="w").grid(row=1, column=0, padx=5, pady=5)
    taille_values = [f"{i / 10:g}" for i in range(2, 31)]
    viewer.taille_entry = ttk.Combobox(viewer.input_frame, values=taille_values, state="readonly", justify="center")
    viewer.taille_entry.set("1")
    viewer.taille_entry.grid(row=1, column=1, padx=(0, 10), sticky="ew")

    # Couleur
    tk.Label(viewer.input_frame, text="Couleur : ", width=18, anchor="w").grid(row=2, column=0, padx=5, pady=5)
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
    viewer.point_color_entry = ttk.Combobox(viewer.input_frame, values=colors, state="readonly", justify="center")
    viewer.point_color_entry.current(0)
    viewer.point_color_entry.grid(row=2, column=1, padx=(0, 10), sticky="ew")

    # Type de points
    tk.Label(viewer.input_frame, text="Type de points : ", width=18, anchor="w").grid(row=3, column=0, padx=5, pady=5)
    type_points = ["Cercle", "Carré", "Cible", "Epingle"]
    viewer.type_points_entry = ttk.Combobox(viewer.input_frame, values=type_points, state="readonly", justify="center")
    viewer.type_points_entry.current(0)
    viewer.type_points_entry.grid(row=3, column=1, padx=(0, 10), sticky="ew")

    # Couleur de fond du label
    tk.Label(viewer.input_frame, text="Couleur du label : ", width=18, anchor="w").grid(row=4, column=0, padx=5, pady=5)
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
    viewer.label_color_entry = ttk.Combobox(viewer.input_frame, values=colors, state="readonly", justify="center")
    viewer.label_color_entry.current(0)
    viewer.label_color_entry.grid(row=4, column=1, padx=(0, 10), sticky="ew")

    # Affiche les widgets d'entree des coordonnees en fonction du format des coordonnees
    if viewer.creation_mode.get() == "coordonnees":
        if viewer.coord_type.get() == "Degrés":
            # Latitude
            tk.Label(viewer.input_frame, text="Latitude :", width=18, anchor="w").grid(row=5, column=0, padx=5, pady=5)
            viewer.lat_entry = tk.Entry(viewer.input_frame, width=25, justify="center")
            viewer.lat_entry.grid(row=5, column=1, padx=(0, 10), sticky="ew")

            # Longitude
            tk.Label(viewer.input_frame, text="Longitude :", width=18, anchor="w").grid(row=6, column=0, padx=5, pady=5)
            viewer.lon_entry = tk.Entry(viewer.input_frame, width=25, justify="center")
            viewer.lon_entry.grid(row=6, column=1, padx=(0, 10), sticky="ew")

            # Bouton créer
            tk.Button(
                viewer.input_frame,
                text="Créer le point",
                command=lambda: database.create_point_from_deg(viewer),
            ).grid(row=7, column=1, columnspan=2, sticky="ew", pady=5, padx=(0, 10))            

        elif viewer.coord_type.get() == "Degrés/Minutes":
            # Latitude
            tk.Label(viewer.input_frame, text="Latitude :", width=18, anchor="w").grid(row=5, column=0, padx=5, pady=5)
            lat_frame = tk.Frame(viewer.input_frame)
            lat_frame.grid(row=5, column=1, padx=(0, 10), sticky="ew")

            viewer.lat_ns_combo = ttk.Combobox(lat_frame, values=["N", "S"], width=3, state="readonly")
            viewer.lat_ns_combo.grid(row=0, column=0, padx=(0, 2), sticky="w")
            viewer.lat_ns_combo.set("N")

            viewer.lat_deg_entry = tk.Entry(lat_frame, width=8)
            viewer.lat_deg_entry.grid(row=0, column=1, padx=(6, 3), sticky="w")

            tk.Label(lat_frame, text="°", width=1).grid(row=0, column=2, sticky="w")

            viewer.lat_min_entry = tk.Entry(lat_frame, width=8)
            viewer.lat_min_entry.grid(row=0, column=3, padx=(3, 3), sticky="w")

            tk.Label(lat_frame, text="'", width=1).grid(row=0, column=4, sticky="w")

            # Longitude
            tk.Label(viewer.input_frame, text="Longitude :", width=18, anchor="w").grid(row=6, column=0, padx=5, pady=5)
            lon_frame = tk.Frame(viewer.input_frame)
            lon_frame.grid(row=6, column=1, padx=(0, 10), sticky="ew")

            viewer.lon_ew_combo = ttk.Combobox(lon_frame, values=["E", "O"], width=3, state="readonly")
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
                command=lambda: database.create_point_from_deg_min(viewer),
            ).grid(row=7, column=1, columnspan=2, sticky="ew", pady=5, padx=(0, 10))            

        elif viewer.coord_type.get() == "Degrés/Minutes/Secondes":
            # Latitude
            tk.Label(viewer.input_frame, text="Latitude :", width=18, anchor="w").grid(row=5, column=0, padx=5, pady=5)
            lat_frame = tk.Frame(viewer.input_frame)
            lat_frame.grid(row=5, column=1, padx=(0, 10), sticky="ew")

            viewer.lat_ns_combo = ttk.Combobox(lat_frame, values=["N", "S"], width=2, state="readonly")
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
            tk.Label(viewer.input_frame, text="Longitude :", width=18, anchor="w").grid(row=6, column=0, padx=5, pady=5)
            # Creation d'un cadre contenant des colonnes décorellées
            lon_frame = tk.Frame(viewer.input_frame)
            lon_frame.grid(row=6, column=1, padx=(0, 10), sticky="ew")

            viewer.lon_ew_combo = ttk.Combobox(lon_frame, values=["E", "O"], width=2, state="readonly")
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
                command=lambda: database.create_point_from_deg_min_sec(viewer),
            ).grid(row=7, column=1, columnspan=2, sticky="ew", pady=5, padx=(0, 10))            

        elif viewer.coord_type.get() == "Calamar":
            # Axe X (correspond à Y dans Calamar)
            tk.Label(viewer.input_frame, text="Axe Y :", width=18, anchor="w").grid(row=5, column=0, padx=5, pady=5)
            X_frame = tk.Frame(viewer.input_frame)
            X_frame.grid(row=5, column=1, padx=(0, 10), sticky="ew")

            viewer.calamar_x_entry = tk.Entry(X_frame, width=15)
            viewer.calamar_x_entry.grid(row=0, column=0, padx=(0, 20), sticky="w")
            viewer.calamar_x_combo = ttk.Combobox(X_frame, values=["mD", "mG"], width=7, state="readonly")
            viewer.calamar_x_combo.grid(row=0, column=1, padx=(6, 3), sticky="w")
            viewer.calamar_x_combo.set("mD")

            # Axe Y (correspond à X dans Calamar)
            tk.Label(viewer.input_frame, text="Axe X :", width=18, anchor="w").grid(row=6, column=0, padx=5, pady=5)
            Y_frame = tk.Frame(viewer.input_frame)
            Y_frame.grid(row=6, column=1, padx=(0, 10), sticky="ew")

            viewer.calamar_y_entry = tk.Entry(Y_frame, width=15)
            viewer.calamar_y_entry.grid(row=0, column=0, padx=(0, 20), sticky="w")
            viewer.calamar_y_combo = ttk.Combobox(Y_frame, values=["mL", "mC"], width=7, state="readonly")
            viewer.calamar_y_combo.grid(row=0, column=1, padx=(6, 3), sticky="w")
            viewer.calamar_y_combo.set("mL")

            # Bouton créer
            tk.Button(
                viewer.input_frame,
                text="Créer le point",
                command=lambda: database.create_point_from_calamar(viewer),
            ).grid(row=7, column=1, columnspan=2, sticky="ew", pady=5, padx=(0, 10))
            
    elif viewer.creation_mode.get() == "radial":
        #Vérifier s'il y a des points disponibles
        conn = sqlite3.connect("points.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM points")
        points = [row[0] for row in cursor.fetchall()]
        conn.close()        

        if points:
            # Point de départ

            tk.Label(viewer.input_frame, text="Point de départ :", width=18, anchor="w").grid(
                row=5, column=0, sticky="w", padx=5, pady=5
            )
            viewer.radial_point_combo = ttk.Combobox(viewer.input_frame, values=points, state="readonly", justify="center")
            viewer.radial_point_combo.grid(row=5, column=1, padx=(0, 10), sticky="ew")
            if points:
                viewer.radial_point_combo.set(points[0])

            # Distance

            tk.Label(viewer.input_frame, text="Distance :", width=18, anchor="w").grid(row=6, column=0, padx=5, pady=5)
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

            tk.Label(viewer.input_frame, text="Gisement (°) :", width=18, anchor="w").grid(
                row=7, column=0, padx=5, pady=5
            )
            # Creation d'un cadre contenant les colonnes
            gisement_frame = tk.Frame(viewer.input_frame)
            gisement_frame.grid(row=7, column=1, padx=(0, 10), sticky="ew")

            viewer.radial_bearing_entry = tk.Entry(gisement_frame, width=14)
            viewer.radial_bearing_entry.grid(row=0, column=0, padx=(0, 15), sticky="w")

            tk.Label(gisement_frame, text="0-359°").grid(row=0, column=1, padx=5, pady=5, sticky="w")

            # Bouton créer
            tk.Button(
                viewer.input_frame,
                text="Créer le point",
                command=lambda: database.create_point_from_radial(viewer),
            ).grid(row=8, column=1, columnspan=2, sticky="ew", pady=5, padx=5)
            
        else:
            tk.Label(
                viewer.input_frame,
                text="Créez d'abord un point de référence",
                fg="gray",
            ).pack(pady=(10, 10))

    elif viewer.creation_mode.get() == "click":
        # Latitude
        tk.Label(viewer.input_frame, text="Latitude :", width=18, anchor="w").grid(row=5, column=0, padx=5, pady=5)
        viewer.click_lat_entry = tk.Entry(viewer.input_frame, state="readonly")
        viewer.click_lat_entry.grid(row=5, column=1, padx=(0, 10), sticky="ew")
        ToolTip(viewer.click_lat_entry, "Clic droit sur la carte pour récupérer les coordonnées du point.")

        # Longitude
        tk.Label(viewer.input_frame, text="Longitude :", width=18, anchor="w").grid(row=6, column=0, padx=5, pady=5)
        viewer.click_lon_entry = tk.Entry(viewer.input_frame, state="readonly")
        viewer.click_lon_entry.grid(row=6, column=1, padx=(0, 10), sticky="ew")        
        
        # Bouton créer
        tk.Button(
            viewer.input_frame,
            text="Créer le point",
            command=lambda: database.create_point_from_click(viewer),
        ).grid(row=7, column=1, columnspan=2, sticky="ew", pady=5, padx=(0, 10))

def setup_points_tabs(viewer):
    """Genere l'affichage de l'onglet Points"""

    # Variable pour récuperer les choix de l'utilisateur ouverture par defaut "coordonnees/Degrés"
    viewer.creation_mode = tk.StringVar(value="coordonnees")
    viewer.coord_type = tk.StringVar(value="Degrés")

    # Configurer le style des onglets
    style = ttk.Style()
    style.configure("TNotebook.Tab", font=("Arial", 10))  # Onglet normal
    style.map("TNotebook.Tab", font=[("selected", ("Arial", 10, "bold"))])  # Onglet sélectionné en gras

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
        command=lambda: update_input_frame_points(viewer),
    )
    viewer.rb_coords.grid(row=0, column=0, padx=5, pady=5)
    viewer.coord_combo = ttk.Combobox(
        viewer.type_creation_frame,
        textvariable=viewer.coord_type,
        values=["Degrés", "Degrés/Minutes", "Degrés/Minutes/Secondes", "Calamar"],
        state="readonly",
    )
    viewer.coord_combo.grid(row=0, column=1, padx=(0, 10), sticky="ew")
    viewer.coord_combo.bind("<<ComboboxSelected>>", lambda e: update_input_frame_points(viewer))

    rb_radial = ttk.Radiobutton(
        viewer.type_creation_frame,
        text="Radial distance",
        width=18,
        variable=viewer.creation_mode,
        value="radial",
        command=lambda: update_input_frame_points(viewer),
    )
    rb_radial.grid(row=1, column=0, padx=5, pady=5)

    rb_click = ttk.Radiobutton(
        viewer.type_creation_frame,
        text="Tracé sur la carte",
        width=18,
        variable=viewer.creation_mode,
        value="click",
        command=lambda: update_input_frame_points(viewer),
    )
    rb_click.grid(row=2, column=0, padx=5, pady=5)
    

    # Titre du tableau de points
    points_title_label = tk.Label(
        viewer.treeview_frame,
        text="Liste des points",
        anchor="center",
        font=("Arial", 10, "bold"),
    )
    points_title_label.pack(pady=5, fill=tk.X, padx=5)
    ToolTip(points_title_label, "● Clic sur le nom du point pour afficher ses informations dans le formulaire\n"
                                "\u25CF Clic sur la case à cocher pour selectionner le point")
    

    # Création du Treeview
    viewer.tree = ttk.Treeview(viewer.treeview_frame, columns=("selected", "nom"), show="headings", height=10)
    viewer.tree.heading("selected", text="Export")
    viewer.tree.heading("nom", text="Nom")

    viewer.tree.column("selected", width=50, minwidth=50, stretch=False,anchor="center")
    viewer.tree.column("nom", width=100, minwidth=100, stretch=True,anchor="center")

    viewer.points_checked_items = {}
    viewer.tree.bind("<Button-1>", lambda event: on_tree_click(viewer, event))  # Selectionne le point
    viewer.tree.bind("<Double-1>", lambda event: viewer.fonction_temporaire())  # Centre l'affichage sur le point sélectionné
    viewer.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Création des boutons du treeview
    btn_select_all = ttk.Button(
        viewer.treeview_frame,
        text="Select All",
        width=16,
        command=lambda: select_all_treeview(viewer.points_checked_items, viewer.tree),
    )  # fonction d'attente pour les commandes du menu
    btn_select_all.pack(side=tk.LEFT, padx=5)

    btn_deselect_all = ttk.Button(
        viewer.treeview_frame,
        text="Deselect All",
        width=16,
        command=lambda: deselect_all_treeview(viewer.points_checked_items, viewer.tree),
    )  # fonction d'attente pour les commandes du menu
    btn_deselect_all.pack(side=tk.LEFT, padx=5)

    btn_delete = ttk.Button(
        viewer.treeview_frame,
        text="Delete",
        width=16,
        command=lambda: database.delete_selected_points(viewer),
    )  # fonction d'attente pour les commandes du menu
    btn_delete.pack(side=tk.LEFT, padx=5)

    # Remplissage du frame input_frame
    update_input_frame_points(viewer)

    #Charge les points presents dans la base de données et gere l'affichage sur la carte
    database.load_points_treeview(viewer)

def setup_lignes_tabs(viewer):
    # Variable pour récuperer les choix de l'utilisateur ouverture par defaut "points"
    viewer.ligne_creation_mode = tk.StringVar(value="points")

    # Création de l'onglet Ligne dans "ligne_frame"
    ligne_frame = ttk.Frame(viewer.notebook)
    viewer.notebook.add(ligne_frame, text="  Lignes  ")    

    # Frame pour selectionner le mode de création de la ligne
    viewer.lignes_creation_frame = tk.Frame(ligne_frame, relief="groove", borderwidth=1)
    viewer.lignes_creation_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

    #Frame pour le transfert des points vers la ligne
    viewer.ligne_points_transfer_frame = tk.Frame(ligne_frame, relief="groove", borderwidth=1)
    viewer.ligne_points_transfer_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

    # Frame pour positionner les champs de saisie
    viewer.lines_input_frame = tk.Frame(ligne_frame, relief="groove", borderwidth=1)
    viewer.lines_input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Frame pour le Treeview
    viewer.lines_treeview_frame = tk.Frame(ligne_frame, relief="groove", borderwidth=1)
    viewer.lines_treeview_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

    # Remplissage de type_creation_frame    
    ttk.Radiobutton(
        viewer.lignes_creation_frame,
        text="Utilisation des points de la base de données",
        width=40,
        variable=viewer.ligne_creation_mode,
        value="points",
        command=lambda: viewer.fonction_temporaire(viewer),
    ).grid(row=0, column=0, padx=5, pady=5) 

    ttk.Radiobutton(
        viewer.lignes_creation_frame,
        text="Tracé de la ligne sur la carte",
        width=40,
        variable=viewer.ligne_creation_mode,
        value="carte",
        command=lambda: viewer.fonction_temporaire(viewer),
    ).grid(row=1, column=0, padx=5, pady=5)

    # Titre du tableau de points
    lignes_title_label = tk.Label(
        viewer.lines_treeview_frame,
        text="Liste des lignes",
        anchor="center",
        font=("Arial", 10, "bold"),
    )
    lignes_title_label.pack(pady=5, fill=tk.X, padx=5)
    ToolTip(lignes_title_label, "● Clic sur le nom de la ligne pour afficher ses informations dans le formulaire\n"
                                "\u25CF Clic sur la case à cocher pour selectionner la ligne")
    
    # Remplissage du frame input_frame
    update_input_frame_lignes(viewer)


    # Création du Treeview
    viewer.lines_tree = ttk.Treeview(viewer.lines_treeview_frame, columns=("selected", "nom"), show="headings", height=10)
    viewer.lines_tree.heading("selected", text="Export")
    viewer.lines_tree.heading("nom", text="Nom")

    viewer.lines_tree.column("selected", width=50, minwidth=50, stretch=False,anchor="center")
    viewer.lines_tree.column("nom", width=100, minwidth=100, stretch=True,anchor="center")

    viewer.lines_checked_items = {}
    viewer.lines_tree.bind("<Button-1>", lambda event: viewer.fonction_temporaire())  # Selectionne le point
    viewer.lines_tree.bind("<Double-1>", lambda event: viewer.fonction_temporaire())  # Centre l'affichage sur le point sélectionné
    viewer.lines_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Création des boutons du treeview
    btn_select_all = ttk.Button(
        viewer.lines_treeview_frame,
        text="Select All",
        width=16,
        command=lambda: select_all_treeview(viewer.lines_checked_items, viewer.lines_tree),
    )  # fonction d'attente pour les commandes du menu
    btn_select_all.pack(side=tk.LEFT, padx=5)

    btn_deselect_all = ttk.Button(
        viewer.lines_treeview_frame,
        text="Deselect All",
        width=16,
        command=lambda: deselect_all_treeview(viewer.lines_checked_items, viewer.lines_tree),
    )  # fonction d'attente pour les commandes du menu
    btn_deselect_all.pack(side=tk.LEFT, padx=5)

    btn_delete = ttk.Button(
        viewer.lines_treeview_frame,
        text="Delete",
        width=16,
        command=lambda: viewer.fonction_temporaire(),
    )  # fonction d'attente pour les commandes du menu
    btn_delete.pack(side=tk.LEFT, padx=5)

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
    viewer.polygones_input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Frame pour le Treeview
    viewer.polygones_treeview_frame = tk.Frame(polygone_frame, relief="groove", borderwidth=1)
    viewer.polygones_treeview_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

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
        command=lambda: select_all_treeview(viewer.polygones_checked_items, viewer.polygones_tree),
    )  # fonction d'attente pour les commandes du menu
    btn_select_all.pack(side=tk.LEFT, padx=5)

    btn_deselect_all = ttk.Button(
        viewer.polygones_treeview_frame,
        text="Deselect All",
        width=16,
        command=lambda: deselect_all_treeview(viewer.polygones_checked_items, viewer.polygones_tree),
    )  # fonction d'attente pour les commandes du menu
    btn_deselect_all.pack(side=tk.LEFT, padx=5)

    btn_delete = ttk.Button(
        viewer.polygones_treeview_frame,
        text="Delete",
        width=16,
        command=lambda: viewer.fonction_temporaire(),
    )  # fonction d'attente pour les commandes du menu
    btn_delete.pack(side=tk.LEFT, padx=5)

def on_tab_changed(self, event):
    """Gérer le changement d'onglet"""
    #L'onglet point est toujours a jour on synchronise les autres onglets
    selected_tab = self.notebook.select()
    tab_text = self.notebook.tab(selected_tab, "text").strip()
    print(f"Tab text: '{tab_text}'")        
    
    if tab_text == "Lignes":
        database.load_points_line(self)        
        #load_lines(self)      
                  
    elif tab_text == "Polygones":
        self.fonction_temporaire()
        # Si on quitte l'onglet lignes, nettoyer la ligne temporaire
        #self.clicked_points = []
        #clear_temp_line(self)

    elif tab_text == "Points":
        # Si on quitte l'onglet lignes, nettoyer la ligne temporaire
        #self.clicked_points = []
        #clear_temp_line(self)  
            pass          
