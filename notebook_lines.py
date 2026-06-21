
import tkinter as tk
from tkinter import ttk
import database
import mbtiles_manager
import utility


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
        
        viewer.add_button = tk.Button(viewer.center_frame, text=">>", command=lambda: utility.add_point_to_line(viewer,viewer.points_listbox,viewer.line_points_listbox), width=6)
        viewer.add_button.pack(pady=(50, 20))            
        
        viewer.remove_button = tk.Button(viewer.center_frame, text="<<", command=lambda: utility.remove_point_from_line(viewer,viewer.line_points_listbox), width=6)
        viewer.remove_button.pack(pady=5)        
        
        viewer.ligne_label = tk.Label(right_frame, text="Ligne", font=("Arial", 10),justify='center')
        viewer.ligne_label.pack(anchor=tk.CENTER, padx=(5, 5))
        viewer.line_points_listbox = tk.Listbox(right_frame, height=8)
        viewer.line_points_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 5), padx=(5, 5))
        utility.ToolTip(viewer.line_points_listbox, "● Possibilité de déplacer la position des points dans la ligne (clic gauche maintenu)")
         
        #Implémente le drag and drop dans la liste des points de la ligne
        utility.enable_line_points_drag_reorder(viewer,viewer.line_points_listbox)

        # Charge la base des points dans la liste pour créer la route  
        database.load_points_line(viewer,viewer.points_listbox)

        # TODO :Réinitialiser les points cliqués
        # viewer.clicked_points = []
        # clear_temp_line(viewer)

    elif viewer.ligne_creation_mode.get() == "carte":
        # Configurer la colonne 1 pour qu'elle s'étende
        viewer.ligne_points_transfer_frame.grid_columnconfigure(1, weight=1)

        # Longueur totale de la ligne
        tk.Label(viewer.ligne_points_transfer_frame, text="Longueur totale :", width=25, anchor="w").grid(row=0, column=0, padx=5, pady=5)
        line_length_frame = tk.Frame(viewer.ligne_points_transfer_frame)
        line_length_frame.grid(row=0, column=1, padx=(0, 5), sticky="ew")

        viewer.line_length_entry = tk.Entry(line_length_frame, justify="center", state="readonly", width=12)
        viewer.line_length_entry.grid(row=0, column=0, padx=(0, 12), sticky="w")

        viewer.line_length_combo = ttk.Combobox(
            line_length_frame,
            justify="center",
            values=["Nm", "m"],
            width=5,
            state="readonly",
        )
        viewer.line_length_combo.grid(row=0, column=1, padx=(0, 2), sticky="w")
        viewer.line_length_combo.set("Nm")

        # Longueur du dernier segment
        tk.Label(viewer.ligne_points_transfer_frame, text="Longueur du dernier segment :", width=25, anchor="w").grid(row=1, column=0, padx=5, pady=5)
        line_last_segment_length_frame = tk.Frame(viewer.ligne_points_transfer_frame)
        line_last_segment_length_frame.grid(row=1, column=1, padx=(0, 5), sticky="ew")

        viewer.line_last_segment_length_entry = tk.Entry(line_last_segment_length_frame, justify="center", state="readonly", width=12)
        viewer.line_last_segment_length_entry.grid(row=0, column=0, padx=(0, 12), sticky="w")

        viewer.line_last_segment_length_combo = ttk.Combobox(
            line_last_segment_length_frame,
            justify="center",
            values=["Nm", "m"],
            width=5,
            state="readonly",
        )
        viewer.line_last_segment_length_combo.grid(row=0, column=1, padx=(0, 2), sticky="w")
        viewer.line_last_segment_length_combo.set("Nm")

        # Gisement du dernier segment
        tk.Label(viewer.ligne_points_transfer_frame, text="Gisement du dernier segment :", width=25, anchor="w").grid(row=2, column=0, padx=5, pady=5)
        viewer.line_last_segment_gisement_entry = tk.Entry(viewer.ligne_points_transfer_frame, justify="center",state="readonly")
        viewer.line_last_segment_gisement_entry.grid(row=2, column=1, padx=(0, 5), sticky="ew") 
       

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
        command=lambda: database.create_ligne(viewer),
    ).grid(row=3, column=1, columnspan=2, sticky="ew", pady=5, padx=(0, 10))            
        
    
    # Charge les lignes presents dans la base de données et gere l'affichage sur la carte
    database.load_item_treeview(viewer,"lignes.db",viewer.lines_checked_items,viewer.lines_tree,"lines")
    
    # Réinitialiser les points cliqués et la ligne temporaire
    viewer.clicked_points = []
    viewer.mbtiles_manager.clear_temp_line()

def create_treeview_lines(viewer):    

     # Titre du tableau de points
    lignes_title_label = tk.Label(
        viewer.lines_treeview_frame,
        text="Liste des lignes",
        anchor="center",
        font=("Arial", 10, "bold"),
    )
    lignes_title_label.pack(pady=5, fill=tk.X, padx=5)
    utility.ToolTip(lignes_title_label, "● Clic sur le nom de la ligne pour afficher ses informations dans le formulaire\n"
                                "\u25CF Clic sur la case à cocher pour selectionner la ligne\n"
                                "\u25CF Double-clic sur le nom de la ligne pour centrer la carte sur le premier point")
    
    # Création du Treeview lines_tree
    viewer.lines_tree = ttk.Treeview(viewer.lines_treeview_frame, columns=("selected", "nom"), show="headings", height=10)
    viewer.lines_tree.heading("selected", text="Export")
    viewer.lines_tree.heading("nom", text="Nom")

    viewer.lines_tree.column("selected", width=50, minwidth=50, stretch=False,anchor="center")
    viewer.lines_tree.column("nom", width=100, minwidth=100, stretch=True,anchor="center")   

    viewer.lines_tree.bind("<Button-1>", lambda event: utility.on_tree_click(viewer, event, viewer.lines_checked_items, viewer.lines_tree))  # Selectionne le point
    viewer.lines_tree.bind("<Double-1>", lambda event: viewer.mbtiles_manager.on_lines_tree_double_click(event))  # Centre l'affichage sur le point sélectionné
    viewer.lines_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Création des boutons du treeview
    btn_select_all = ttk.Button(
        viewer.lines_treeview_frame,
        text="Select All",
        width=16,
        command=lambda: utility.select_all_treeview(viewer.lines_checked_items, viewer.lines_tree),
    )  # fonction d'attente pour les commandes du menu
    btn_select_all.pack(side=tk.LEFT, padx=5)

    btn_deselect_all = ttk.Button(
        viewer.lines_treeview_frame,
        text="Deselect All",
        width=16,
        command=lambda: utility.deselect_all_treeview(viewer.lines_checked_items, viewer.lines_tree),
    )  # fonction d'attente pour les commandes du menu
    btn_deselect_all.pack(side=tk.LEFT, padx=5)

    btn_delete = ttk.Button(
        viewer.lines_treeview_frame,
        text="Delete",
        width=16,
        command=lambda: database.delete_selected_items(viewer,"lignes.db",viewer.lines_checked_items,viewer.lines_tree,"lines"),
    )  # fonction d'attente pour les commandes du menu
    btn_delete.pack(side=tk.LEFT, padx=5)

def create_mode_creation_lines(viewer):
    # Remplissage de type_creation_frame    
    ttk.Radiobutton(
        viewer.lignes_creation_frame,
        text="Utilisation des points de la base de données",
        width=40,
        variable=viewer.ligne_creation_mode,
        value="points",
        command=lambda: update_input_frame_lignes(viewer),
    ).grid(row=0, column=0, padx=5, pady=5) 

    ligne_carte_radiobutton = ttk.Radiobutton(
        viewer.lignes_creation_frame,
        text="Tracé de la ligne sur la carte",
        width=40,
        variable=viewer.ligne_creation_mode,
        value="carte",
        command=lambda: update_input_frame_lignes(viewer),
    )
    ligne_carte_radiobutton.grid(row=1, column=0, padx=5, pady=5)    
    utility.ToolTip(ligne_carte_radiobutton, "● Shift + Clic Gauche pour générer un point sur la carte.\n"
                                                "● Shift + Clic Droit pour effacer le dernier point.")

def setup_lignes_tabs(viewer):
    # Variable pour récuperer les choix de l'utilisateur ouverture par defaut "points"
    viewer.ligne_creation_mode = tk.StringVar(value="points")

    #Tableau tracage des cases cochées
    viewer.lines_checked_items = {}

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
    viewer.lines_input_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

    # Frame pour le Treeview
    viewer.lines_treeview_frame = tk.Frame(ligne_frame, relief="groove", borderwidth=1)
    viewer.lines_treeview_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, padx=5, pady=5)   
        
    # Création du mode de création de la ligne
    create_mode_creation_lines(viewer)
    
    # Création du Treeview
    create_treeview_lines(viewer)

    # Remplissage du frame input_frame
    update_input_frame_lignes(viewer)

    # Charge les lignes presents dans la base de données et gere l'affichage sur la carte
    #database.load_item_treeview(viewer,"lignes.db",viewer.lines_checked_items,viewer.lines_tree,"lines")