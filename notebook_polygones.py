
import tkinter as tk
from tkinter import ttk
from turtle import width
from utility import ToolTip
import utility
import database
import sqlite3


def fill_points_frame(viewer):
    """Remplir le frame """
    
    #Création d'un frame contenant les deux list box et les boutons
    viewer.polygone_points_frame = tk.Frame( viewer.polygone_utility_frame)
    viewer.polygone_points_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
    viewer.polygone_points_frame.grid_columnconfigure(0, weight=1,uniform="listbox")
    viewer.polygone_points_frame.grid_columnconfigure(1, weight=0)
    viewer.polygone_points_frame.grid_columnconfigure(2, weight=1,uniform="listbox")

    #Création des frames gauche, centre et droite
    left_frame_polygon = tk.Frame(viewer.polygone_points_frame)
    left_frame_polygon.grid(row=0, column=0, sticky="nsew")

    viewer.center_frame_polygon = tk.Frame(viewer.polygone_points_frame, width=40)
    viewer.center_frame_polygon.grid(row=0, column=1, sticky="ns", padx=5)
    viewer.center_frame_polygon.grid_propagate(False)

    right_frame_polygon = tk.Frame(viewer.polygone_points_frame)
    right_frame_polygon.grid(row=0, column=2, sticky="nsew")

    #Création de la liste des points de la base
    viewer.points_label_polygon = tk.Label(left_frame_polygon, text="Base de points", font=("Arial", 10),justify='center')
    viewer.points_label_polygon.pack(anchor=tk.CENTER, padx=(5, 5))
    viewer.points_listbox_polygon = tk.Listbox(left_frame_polygon, height=8)
    viewer.points_listbox_polygon.pack(fill=tk.BOTH, expand=True, pady=(5, 5), padx=(5, 5))        
    
    viewer.add_button_polygon = tk.Button(viewer.center_frame_polygon, text=">>", command=lambda: utility.add_point_to_line(viewer,viewer.points_listbox_polygon,viewer.line_points_listbox_polygon), width=6)
    viewer.add_button_polygon.pack(pady=(50, 20))
    utility.ToolTip(viewer.add_button_polygon, "Rajoute le point selectionné au polygone\n")  
            
        
    viewer.remove_button_polygon = tk.Button(viewer.center_frame_polygon, text="<<", command=lambda: utility.remove_point_from_line(viewer,viewer.line_points_listbox_polygon), width=6)
    viewer.remove_button_polygon.pack(pady=5)
    utility.ToolTip(viewer.remove_button_polygon, "Retire le point selectionné du polygone\n")        
        
    viewer.ligne_label_polygon = tk.Label(right_frame_polygon, text="Polygones", font=("Arial", 10),justify='center')
    viewer.ligne_label_polygon.pack(anchor=tk.CENTER, padx=(5, 5))
    viewer.line_points_listbox_polygon = tk.Listbox(right_frame_polygon, height=8)
    viewer.line_points_listbox_polygon.pack(fill=tk.BOTH, expand=True, pady=(5, 5), padx=(5, 5))
    utility.ToolTip(viewer.line_points_listbox_polygon, "Réordonnement des points possible par glisser-déposer\n")
         
    #Implémente le drag and drop dans la liste des points de la ligne
    utility.enable_line_points_drag_reorder(viewer,viewer.line_points_listbox_polygon)

    # Charge la base des points dans la liste pour créer la route  
    database.load_points_line(viewer,viewer.points_listbox_polygon)
 
def fill_map_frame(viewer):
    # Configurer la colonne 1 pour qu'elle s'étende
        viewer.polygone_utility_frame.grid_columnconfigure(1, weight=1)
        
        # Longueur du dernier segment
        tk.Label(viewer.polygone_utility_frame, text="Longueur du dernier segment :", width=25, anchor="w").grid(row=1, column=0, padx=5, pady=5)
        polygone_last_segment_length_frame = tk.Frame(viewer.polygone_utility_frame)
        polygone_last_segment_length_frame.grid(row=1, column=1, padx=(0, 5), sticky="ew")

        viewer.polygone_last_segment_length_entry = tk.Entry(polygone_last_segment_length_frame, justify="center", state="readonly", width=12)
        viewer.polygone_last_segment_length_entry.grid(row=0, column=0, padx=(0, 12), sticky="w")

        viewer.polygone_last_segment_length_combo = ttk.Combobox(
            polygone_last_segment_length_frame,
            justify="center",
            values=["Nm", "m"],
            width=5,
            state="readonly",
        )
        viewer.polygone_last_segment_length_combo.grid(row=0, column=1, padx=(0, 2), sticky="w")
        viewer.polygone_last_segment_length_combo.set("Nm")

        # Gisement du dernier segment
        tk.Label(viewer.polygone_utility_frame, text="Gisement du dernier segment :", width=25, anchor="w").grid(row=2, column=0, padx=5, pady=5)
        viewer.polygone_last_segment_gisement_entry = tk.Entry(viewer.polygone_utility_frame, justify="center",state="readonly")
        viewer.polygone_last_segment_gisement_entry.grid(row=2, column=1, padx=(0, 5), sticky="ew")

def fill_rectangle_frame(viewer):
        
    # polygone_utility_frame : Configurer la colonne 1 pour qu'elle s'étende
    viewer.polygone_utility_frame.grid_columnconfigure(1, weight=1)

    # Sélection du centre du rectangle
    tk.Label(viewer.polygone_utility_frame, text="Centre du rectangle :", width=25, anchor="w").grid(row=0, column=0, padx=5, pady=5)
    
    # Récupérer les points depuis la base
    try:
        conn = sqlite3.connect("points.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM points ORDER BY name")
        points = [row[0] for row in cursor.fetchall()]
        conn.close()
    except sqlite3.Error:
        points = []
    
    viewer.rectangle_center_combo = ttk.Combobox(viewer.polygone_utility_frame, values=points, state="readonly",justify="center")
    if points:
        viewer.rectangle_center_combo.current(0)
    viewer.rectangle_center_combo.grid(row=0, column=1, padx=(0, 10), sticky="ew")

    # Longueur
    tk.Label(viewer.polygone_utility_frame, text="Longueur :", width=25, anchor="w").grid(row=1, column=0, padx=5, pady=5)
    long_frame = tk.Frame(viewer.polygone_utility_frame)
    long_frame.grid(row=1, column=1, padx=(0, 10), sticky="ew")
    long_frame.grid_columnconfigure(0, weight=1)

    viewer.rectangle_length_entry = tk.Entry(long_frame,width=12,justify="center")
    viewer.rectangle_length_entry.grid(row=0, column=0, sticky="w")

    viewer.rectangle_length_unit = ttk.Combobox(long_frame, values=["m", "Nm"], state="readonly", width=5)
    viewer.rectangle_length_unit.current(0)
    viewer.rectangle_length_unit.grid(row=0, column=1, sticky="e")    

    # Largeur
    tk.Label(viewer.polygone_utility_frame, text="Largeur :", width=25, anchor="w").grid(row=3, column=0, padx=5, pady=5)
    width_frame = tk.Frame(viewer.polygone_utility_frame)
    width_frame.grid(row=3, column=1, padx=(0, 10), sticky="ew")
    width_frame.grid_columnconfigure(0, weight=1)

    viewer.rectangle_width_entry = tk.Entry(width_frame,width=12,justify="center")
    viewer.rectangle_width_entry.grid(row=0, column=0, sticky="w")
    viewer.rectangle_width_unit = ttk.Combobox(width_frame, values=["m", "Nm"], state="readonly", width=5)
    viewer.rectangle_width_unit.current(0)
    viewer.rectangle_width_unit.grid(row=0, column=1, sticky="e")    


    # Orientation
    tk.Label(viewer.polygone_utility_frame, text="Orientation (degrés) :", width=25, anchor="w").grid(row=5, column=0, padx=5, pady=5)
    viewer.rectangle_orientation_entry = ttk.Entry(viewer.polygone_utility_frame,width=12)
    viewer.rectangle_orientation_entry.grid(row=5, column=1, padx=(0, 10), sticky="ew")

    # Ajouter flèche d'orientation
    viewer.rectangle_add_arrow_var = tk.IntVar()
    viewer.rectangle_add_arrow_radio = ttk.Checkbutton(viewer.polygone_utility_frame, text="Ajouter flèche", variable=viewer.rectangle_add_arrow_var)
    viewer.rectangle_add_arrow_radio.grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

def fill_cercles_frame(viewer):
    
    # polygone_utility_frame : Configurer la colonne 1 pour qu'elle s'étende
    viewer.polygone_utility_frame.grid_columnconfigure(1, weight=1)

    # Sélection du centre du cercle
    tk.Label(viewer.polygone_utility_frame, text="Centre du cercle :", width=25, anchor="w").grid(row=0, column=0, padx=5, pady=5)
    
    # Récupérer les points depuis la base
    try:
        conn = sqlite3.connect("points.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM points ORDER BY name")
        points = [row[0] for row in cursor.fetchall()]
        conn.close()
    except sqlite3.Error:
        points = []
    
    viewer.cercle_center_combo = ttk.Combobox(viewer.polygone_utility_frame, values=points, state="readonly",justify="center")
    if points:
        viewer.cercle_center_combo.current(0)
    viewer.cercle_center_combo.grid(row=0, column=1, padx=(0, 10), sticky="ew")


    # Rayon
    tk.Label(viewer.polygone_utility_frame, text="Rayon :", width=25, anchor="w").grid(row=1, column=0, padx=5, pady=5)
    rayon_frame = tk.Frame(viewer.polygone_utility_frame)
    rayon_frame.grid(row=1, column=1, padx=(0, 10), sticky="ew")
    rayon_frame.grid_columnconfigure(0, weight=1)

    viewer.cercle_rayon_entry = tk.Entry(rayon_frame,width=12,justify="center")
    viewer.cercle_rayon_entry.grid(row=0, column=0, sticky="w")

    viewer.cercle_rayon_unit = ttk.Combobox(rayon_frame, values=["m", "Nm"], state="readonly", width=5)
    viewer.cercle_rayon_unit.current(0)
    viewer.cercle_rayon_unit.grid(row=0, column=1, sticky="e")

    # Nombre de segments
    tk.Label(viewer.polygone_utility_frame, text="Nombre de segments :", width=25, anchor="w",justify="center").grid(row=2, column=0, padx=5, pady=5)
    viewer.cercle_segments_entry = ttk.Entry(viewer.polygone_utility_frame,width=12, justify="center")
    viewer.cercle_segments_entry.grid(row=2, column=1, padx=(0, 10), sticky="ew")

    # Arc de cercle
    viewer.cercle_arc_var = tk.IntVar()
    viewer.cercle_arc_radio = ttk.Checkbutton(viewer.polygone_utility_frame, text="Arc de cercle", variable=viewer.cercle_arc_var, command=lambda: update_arc_fields(viewer))
    viewer.cercle_arc_radio.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)   
        
    def update_arc_fields(viewer):
       
        if viewer.cercle_arc_var.get():
            
            # Angle de depart
            tk.Label(viewer.polygone_utility_frame, text="Angle de départ :", width=25, anchor="w",justify="center").grid(row=4, column=0, padx=5, pady=5)
            viewer.arc_start_entry = ttk.Entry(viewer.polygone_utility_frame, justify="center")
            viewer.arc_start_entry.grid(row=4, column=1, padx=(0, 10), sticky="ew")

            # Angle de fin
            tk.Label(viewer.polygone_utility_frame, text="Angle de fin :", width=25, anchor="w").grid(row=5, column=0, padx=5, pady=5)
            viewer.arc_end_entry = ttk.Entry(viewer.polygone_utility_frame, justify="center")
            viewer.arc_end_entry.grid(row=5, column=1, padx=(0, 10), sticky="ew")            
            
            # Relier au centre
            viewer.arc_relie_var = tk.IntVar()
            viewer.arc_relie_radio = ttk.Checkbutton(viewer.polygone_utility_frame, text="Relier au centre", variable=viewer.arc_relie_var)
            viewer.arc_relie_radio.grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        else:
            # Supprimer les champs si l'arc n'est pas sélectionné
            for widget in viewer.polygone_utility_frame.grid_slaves():
                if int(widget.grid_info()["row"]) in [4, 5, 6]:
                    widget.grid_forget()

def fill_input_frame_polygones(viewer):
    # polygones_input_frame : Effacement du contenu
    for widget in viewer.polygones_input_frame.winfo_children():
        widget.destroy()

    # polygones_input_frame : Configurer la colonne 1 pour qu'elle s'étende
    viewer.polygones_input_frame.grid_columnconfigure(1, weight=1)

    # Nom
    tk.Label(viewer.polygones_input_frame, text="Nom :", width=25, anchor="w").grid(row=0, column=0, padx=5, pady=5)
    viewer.polygone_name_entry = tk.Entry(viewer.polygones_input_frame, justify="center")
    viewer.polygone_name_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew") 

    # Largeur
    tk.Label(viewer.polygones_input_frame, text="Epaisseur de la ligne :", width=25, anchor="w").grid(row=1, column=0, padx=5, pady=5)
    taille_values = [str(i) for i in range(1, 11)]
    viewer.taille_entry = ttk.Combobox(viewer.polygones_input_frame, values=taille_values, state="readonly", justify="center")
    viewer.taille_entry.set("1")
    viewer.taille_entry.grid(row=1, column=1, padx=(0, 10), sticky="ew")    

    # Couleur du contour
    tk.Label(viewer.polygones_input_frame, text="Couleur du contour : ", width=25, anchor="w").grid(row=2, column=0, padx=5, pady=5)
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
    viewer.line_color_entry = ttk.Combobox(viewer.polygones_input_frame, values=colors, state="readonly", justify="center")
    viewer.line_color_entry.current(0)
    viewer.line_color_entry.grid(row=2, column=1, padx=(0, 10), sticky="ew")  

    # Couleur de remplissage
    tk.Label(viewer.polygones_input_frame, text="Couleur du remplissage : ", width=25, anchor="w").grid(row=3, column=0, padx=5, pady=5)
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
    viewer.fill_color_entry = ttk.Combobox(viewer.polygones_input_frame, values=colors, state="readonly", justify="center")
    viewer.fill_color_entry.current(0)
    viewer.fill_color_entry.grid(row=3, column=1, padx=(0, 10), sticky="ew")
    
    #  Remplir
    viewer.polygone_fill_var = tk.IntVar()
    viewer.polygone_fill_radio = ttk.Checkbutton(viewer.polygones_input_frame, text="Remplir", variable=viewer.polygone_fill_var)
    viewer.polygone_fill_radio.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

    # Bouton créer
    tk.Button(
        viewer.polygones_input_frame,
        text="Créer le polygone",
        command=lambda: database.create_polygone(viewer),
    ).grid(row=5, column=1, columnspan=2, sticky="ew", pady=5, padx=(0, 10))  


def update_onglet_polygones(viewer):
    """Mettre à jour l'interface selon le mode de création sélectionné"""    

    # Remplissage du cadre contenant les champs liés au type de création

    for widget in viewer.polygone_utility_frame.winfo_children():
        widget.destroy()
    
    if viewer.polygone_creation_mode.get() == "points":        
        fill_points_frame(viewer)        

    elif viewer.polygone_creation_mode.get() == "carte":
        fill_map_frame(viewer)

    elif viewer.polygone_creation_mode.get() == "rectangle":
        fill_rectangle_frame(viewer)
    
    elif viewer.polygone_creation_mode.get() == "cercle":
        fill_cercles_frame(viewer)

    # Remplissage du cadre contenant les chamsp de saisie communs

    fill_input_frame_polygones(viewer)
    
    # Charge les polygones dans le treeview et rafraichie la carte

    database.load_item_treeview(viewer,"polygones.db",viewer.polygones_checked_items,viewer.polygones_tree,"polygons")
    
def create_treeview_polygones(viewer):
    
    # Titre du tableau de points
    polygones_title_label = tk.Label(
        viewer.polygones_treeview_frame,
        text="Liste des polygones",
        anchor="center",
        font=("Arial", 10, "bold"),
    )
    polygones_title_label.pack(pady=5, fill=tk.X, padx=5)

    #Info bulle sur le titre     
    ToolTip(polygones_title_label, "● Clic sur la case à cocher pour selectionner le polygone\n"
                                   "\u25CF Double-clic sur le nom du polygone pour centrer la carte sur le premier point")  

    # Création du Treeview
    viewer.polygones_tree = ttk.Treeview(viewer.polygones_treeview_frame, columns=("selected", "nom"), show="headings", height=10)
    viewer.polygones_tree.heading("selected", text="Export")
    viewer.polygones_tree.heading("nom", text="Nom")

    viewer.polygones_tree.column("selected", width=50, minwidth=50, stretch=False,anchor="center")
    viewer.polygones_tree.column("nom", width=100, minwidth=100, stretch=True,anchor="center")

    viewer.polygones_checked_items = {}
    viewer.polygones_tree.bind("<Button-1>", lambda event: utility.on_tree_click(viewer, event, viewer.polygones_checked_items, viewer.polygones_tree))  # Selectionne le point
    viewer.polygones_tree.bind("<Double-1>", lambda event: viewer.mbtiles_manager.on_polygones_tree_double_click(event))  # Centre l'affichage sur le point sélectionné
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
        command=lambda: database.delete_selected_items(viewer,"polygones.db",viewer.polygones_checked_items,viewer.polygones_tree,"polygons"),
    )  # fonction d'attente pour les commandes du menu
    btn_delete.pack(side=tk.LEFT, padx=5)

def create_mode_creation_polygone(viewer):
   
    # Remplissage de type_creation_frame    
    ttk.Radiobutton(
        viewer.polygones_creation_frame,
        text="Utilisation des points de la base de données",
        width=40,
        variable=viewer.polygone_creation_mode,
        value="points",
        command=lambda: update_onglet_polygones(viewer),
    ).grid(row=0, column=0, padx=5, pady=5) 

    polygone_carte_radiobutton = ttk.Radiobutton(
        viewer.polygones_creation_frame,
        text="Tracé du polygone sur la carte",
        width=40,
        variable=viewer.polygone_creation_mode,
        value="carte",
        command=lambda: update_onglet_polygones(viewer),
    )
    polygone_carte_radiobutton.grid(row=1, column=0, padx=5, pady=5)
    utility.ToolTip(polygone_carte_radiobutton, "● Shift + Clic Gauche pour générer un point sur la carte.\n"
                                                "● Shift + Clic Droit pour effacer le dernier point.")



    ttk.Radiobutton(
        viewer.polygones_creation_frame,
        text="Création d'un rectangle",
        width=40,
        variable=viewer.polygone_creation_mode,
        value="rectangle",
        command=lambda: update_onglet_polygones(viewer),
    ).grid(row=2, column=0, padx=5, pady=5)

    ttk.Radiobutton(
        viewer.polygones_creation_frame,
        text="Création d'un cercle",
        width=40,
        variable=viewer.polygone_creation_mode,
        value="cercle",
        command=lambda: update_onglet_polygones(viewer),
    ).grid(row=3, column=0, padx=5, pady=5)

def setup_polygones_tabs(viewer):
    # Variable pour récuperer les choix de l'utilisateur ouverture par defaut "coordonnees/Degrés"
    viewer.polygone_creation_mode = tk.StringVar(value="points")

    # Variable tracage des cases cochées
    viewer.polygones_checked_items = {}

    # Création de l'onglet Polygones 
    polygone_frame = ttk.Frame(viewer.notebook)
    viewer.notebook.add(polygone_frame, text="  Polygones  ")    

    # Frame : Mode de création du polygone
    viewer.polygones_creation_frame = tk.Frame(polygone_frame, relief="groove", borderwidth=1)
    viewer.polygones_creation_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

    #Frame : Multi usages pour paramétrer les polygones
    viewer.polygone_utility_frame = tk.Frame(polygone_frame, relief="groove", borderwidth=1)
    viewer.polygone_utility_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

    # Frame :  Champs de saisie
    viewer.polygones_input_frame = tk.Frame(polygone_frame, relief="groove", borderwidth=1)
    viewer.polygones_input_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

    # Frame :  Treeview
    viewer.polygones_treeview_frame = tk.Frame(polygone_frame, relief="groove", borderwidth=1)
    viewer.polygones_treeview_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, padx=5, pady=5)    

    #Implémentation du mode de création du polygone
    create_mode_creation_polygone(viewer)
    
    #Implémentation du Treeview
    create_treeview_polygones(viewer)   

    # Remplissage du cadre des widgets fonction du type de creation
    update_onglet_polygones(viewer)