import os
import sqlite3
from tkinter import messagebox
import tkinter as tk
import utility

def load_item_treeview(viewer,database_name,checked_items,treeview,table_name):
    """Charger toutes les lignes depuis lignes.db"""
    
    for item in treeview.get_children():
        treeview.delete(item)

    #Checked_items : Stocke les informations des points enregistrés dans le treeview
    checked_items.clear()

    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM {table_name}")
        lines = cursor.fetchall()
        conn.close()
        
        for row in lines:
            item_id = treeview.insert("", tk.END, values=("⬜", row[0]))
            checked_items[item_id] = {"checked": False, "data": row}
    except sqlite3.Error:
        pass

    #TODO :  # Mettre à jour l'affichage sur la carte
    # viewer.mbtiles_manager.draw_points()

def delete_selected_items(viewer,database_name,checked_items,treeview,table_name):
    """Supprimer les éléments cochés de la base de données et du treeview"""
    to_delete = [item for item, info in checked_items.items() if info["checked"]]
    
    if not to_delete:
        messagebox.showwarning("Suppression", "Aucun élément sélectionné.")
        return
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        for item in to_delete:
            name = treeview.item(item)["values"][1]
            cursor.execute(f"DELETE FROM {table_name} WHERE name = ?", (name,))
        conn.commit()
        conn.close()

        # Recharger les données
        if table_name == "points":
            load_item_treeview(viewer,"points.db",viewer.points_checked_items,viewer.tree,"points")
        elif table_name == "lines":
            load_item_treeview(viewer,"lignes.db",viewer.lines_checked_items,viewer.lines_tree,"lines")
        messagebox.showinfo("Suppression", f"{len(to_delete)} élément(s) supprimé(s).")

    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def load_points_line(viewer,listbox):
    """Charger tous les points depuis points.db"""
    listbox.delete(0, tk.END)
    try:
        conn = sqlite3.connect("points.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM points ORDER BY name")
        points = cursor.fetchall()
        conn.close()
        
        for point in points:
            listbox.insert(tk.END, point[0])
    except sqlite3.Error:
        pass

def line_add(name, color, width, points_list):
    """Ajouter une ligne à la base de données"""
    print("Dans line_add")

    try:
        conn = sqlite3.connect("lignes.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM lines WHERE name = ?", (name,))

        if cursor.fetchone():   
            answer=messagebox.askyesno(
                "Ligne existante",
                f"Une ligne avec le nom '{name}' existe déja.\n Voulez-vous modifier cette ligne avec les nouvelles valeurs ?",
            )

            if not answer:
                return "cancelled"
            
            cursor.execute(
                "UPDATE lines SET color = ?, width = ?, points_list = ? WHERE name = ?",
                (color, width, points_list, name)
            )
                    
            conn.commit()
            return "updated"

        print("Insertion de la ligne")

        cursor.execute("INSERT INTO lines (name, color, width, points_list) VALUES (?, ?, ?, ?)",
                          (name, color, width, points_list))
        conn.commit()
        return "created"
        
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création de la ligne: {e}")
        return "error"
    finally:
        if "conn" in locals():
            conn.close()

def create_line_from_database(viewer):
    """Créer une nouvelle ligne et l'enregistrer dans lignes.db"""
    name = viewer.line_name_entry.get().strip()

    if not name:
        messagebox.showerror("Erreur", "Veuillez entrer un nom pour la ligne")
        return
    
    mode = viewer.ligne_creation_mode.get()
    coordinates_list = []
    
    if mode == "points":
        # Création de la liste des points à partir des noms sélectionnés
        point_names = [viewer.line_points_listbox.get(i) for i in range(viewer.line_points_listbox.size())]
        
        if len(point_names) < 2:
            messagebox.showerror("Erreur", "Une ligne doit contenir au moins 2 points")
            return
        
        try:
            # Récupérer les coordonnées des points depuis point.db
            conn_points = sqlite3.connect("points.db")
            cursor_points = conn_points.cursor()
            
            for point_name in point_names:
                cursor_points.execute("SELECT lat, lon FROM points WHERE name = ?", (point_name,))
                result = cursor_points.fetchone()
                if result:
                    lat, lon = result
                    # Stocker les coordonnées au format "lon,lat,0"
                    coordinates_list.append(f"{lon},{lat},0")
                else:
                    messagebox.showerror("Erreur", f"Point '{point_name}' introuvable dans la base de données")
                    conn_points.close()
                    return
            
            conn_points.close()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la récupération des points: {e}")
            return
            
    elif mode == "carte":
        print("Mode carte non implémenté pour le moment")
        # # Mode carte : utiliser les points cliqués
        # if len(viewer.clicked_points) < 2:
        #     messagebox.showerror("Erreur", "Une ligne doit contenir au moins 2 points. Cliquez sur la carte pour ajouter des points.")
        #     return
        
        # # Convertir les points cliqués au format requis
        # for lat, lon in viewer.clicked_points:
        #     coordinates_list.append(f"{lon},{lat},0")
        return            

    points_str = " ".join(coordinates_list)
        
    # Ajouter à la base de données
    result=line_add(name,                         
                    viewer.line_color_entry.get(), 
                    viewer.taille_entry.get(), 
                    points_str)

    if result == "error" or result == "cancelled":
        return        
        
    # Recharger la liste des lignes dans le treeview
    load_item_treeview(viewer,"lignes.db",viewer.lines_checked_items,viewer.lines_tree,"lines")

    if result == "updated":
        messagebox.showinfo("Succès", f"Ligne '{name}' mise à jour avec succès")
    else:
        messagebox.showinfo("Succès", f"Ligne '{name}' créée avec succès")

    # Réinitialiser les champs
    viewer.line_name_entry.delete(0, tk.END)
    
    if mode == "points":
        viewer.line_points_listbox.delete(0, tk.END)        
        
    # else:  # mode == "carte"
    #     viewer.clicked_points = []
    #     clear_temp_line(viewer)
               
    # Redessiner les lignes sur la carte
    # if hasattr(app, 'mbtiles_manager'):
        #     app.mbtiles_manager.draw_lines()        

def point_coord_polygone(viewer):
    # Récupérer les noms des points du polygone
    point_names = [viewer.line_points_listbox_polygon.get(i) for i in range(viewer.line_points_listbox_polygon.size())]
    if len(point_names) < 3:
        messagebox.showerror("Erreur", "Un polygone doit contenir au moins 3 points")
        return
    
    coordinates_list =[]
    conn_points = sqlite3.connect("points.db")
    cursor_points = conn_points.cursor()
    
    for point_name in point_names:
        cursor_points.execute("SELECT lat, lon FROM points WHERE name = ?", (point_name,))
        result = cursor_points.fetchone()
        if result:  
            lat, lon = result
            # Stocker les coordonnées au format "lon,lat,0" (z=0 par défaut)
            coordinates_list.append(f"{lon},{lat},0")
        else:
            messagebox.showerror("Erreur", f"Point '{point_name}' introuvable dans la base de données")
            conn_points.close()
            return
    
    conn_points.close()
    return coordinates_list

def polygone_add(name, color, width, fill, fill_color, points_list):
    """Ajouter un polygone à la base de données"""

    print("Dans polygone_add")

    try:
        conn = sqlite3.connect("polygones.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM polygons WHERE name = ?", (name,))

        if cursor.fetchone():   

            answer=messagebox.askyesno(
                "Polygone existant",
                f"Un polygone avec le nom '{name}' existe déja.\n Voulez-vous modifier ce polygone avec les nouvelles valeurs ?",
            )

            if not answer:
                return "cancelled"

            cursor.execute(
                "UPDATE polygons SET color = ?, width = ?, fill = ?, fill_color = ?, points_list = ? WHERE name = ?",
                (color, width, fill, fill_color, points_list, name),
            )
                    
            conn.commit()
            return "updated"

        print("Insertion du polygone")
        cursor.execute("INSERT INTO polygons (name, color, width, fill, fill_color, points_list) VALUES (?, ?, ?, ?, ?, ?)",
            (name, color, width, fill, fill_color, points_list),)
        conn.commit()
        return "created"    
    
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création du polygone: {e}")
        return "error"
    finally:
        if "conn" in locals():
            conn.close()


def create_polygone(viewer):    
        
    # Récupérer les paramètres du polygone
    name = viewer.polygone_name_entry.get().strip()
    color = viewer.line_color_entry.get().strip() 
    width = viewer.taille_entry.get().strip() 
    fill_color = viewer.fill_color_entry.get().strip()
    
    if not name:
        messagebox.showerror("Erreur", "Veuillez entrer un nom pour le polygone")
        return
    
    # Variable de remmplissage du polygone
    fill=bool(viewer.polygone_fill_var.get())

    #Variable du mode de création
    creation_mode=viewer.polygone_creation_mode.get()    

          
    #Génération des coordonnes et stockage dans coordinates_list
    try:
        if creation_mode == "points":
            coordinates_list = point_coord_polygone(viewer)    
            
        elif creation_mode == "carte":
            # Mode carte : utiliser les points cliqués
            if len(viewer.clicked_points_poly) < 3:
                messagebox.showerror("Erreur", "Un polygone doit contenir au moins 3 points. Cliquez sur la carte pour ajouter des points.")
                return
            
            # Convertir les points cliqués au format requis et fermer automatiquement le polygone
            for lat, lon in viewer.clicked_points_poly:
                coordinates_list.append(f"{lon},{lat},0")
            
            # Ajouter automatiquement le premier point à la fin pour fermer le polygone
            if len(viewer.clicked_points_poly) > 0:
                first_lat, first_lon = viewer.clicked_points_poly[0]
                coordinates_list.append(f"{first_lon},{first_lat},0")
            
        elif creation_mode == "rectangle":
            # Récupérer les paramètres du rectangle
            center_name = viewer.rectangle_center_combo.get().strip()
            if not center_name:
                messagebox.showerror("Erreur", "Veuillez sélectionner un point centre")
                return
                
            length_str = viewer.rectangle_length_entry.get().strip()
            width_str = viewer.rectangle_width_entry.get().strip()
            orientation_str = app.rectangle_orientation_entry.get().strip() or "0"
            
            if not length_str or not width_str:
                messagebox.showerror("Erreur", "Veuillez entrer la longueur et la largeur")
                return
            
            try:
                length = float(length_str)
                width = float(width_str)
                orientation = float(orientation_str)
            except ValueError:
                messagebox.showerror("Erreur", "Valeurs numériques invalides")
                return
            
            # Convertir les unités en kilomètres si nécessaire
            length_unit = app.rectangle_length_unit.get()
            width_unit = app.rectangle_width_unit.get()
            
            if length_unit == "Nm":
                length = length * 1.852  # Conversion miles nautiques vers km
            elif length_unit == "m":
                length = length / 1000  # Conversion mètres vers km
                
            if width_unit == "Nm":
                width = width * 1.852  # Conversion miles nautiques vers km
            elif width_unit == "m":
                width = width / 1000  # Conversion mètres vers km
            
            # Récupérer les coordonnées du point centre
            conn_points = sqlite3.connect("point.db")
            cursor_points = conn_points.cursor()
            cursor_points.execute("SELECT lat, lon FROM points WHERE name = ?", (center_name,))
            center_result = cursor_points.fetchone()
            conn_points.close()
            
            if not center_result:
                messagebox.showerror("Erreur", f"Point centre '{center_name}' introuvable")
                return
            
            center_lat, center_lon = center_result
            
            # Calculer les points du rectangle
            rectangle_points = Utility.calculate_rectangle_points(center_lat, center_lon, length, width, orientation)
            
            # Convertir au format attendu pour la base de données
            for lon, lat in rectangle_points:
                coordinates_list.append(f"{lon},{lat},0")
            
            # Ajouter la flèche d'orientation si demandée
            add_arrow = app.rectangle_add_arrow_var.get()
            if add_arrow:
                arrow_points = Utility.calculate_arrow_points(center_lat, center_lon, length, orientation, width)
                # Ajouter les points de la flèche après le rectangle
                for lon, lat in arrow_points:
                    coordinates_list.append(f"{lon},{lat},0")
        
        elif creation_mode == "cercles":
            # Récupérer les paramètres du cercle
            center_name = viewer.cercle_center_combo.get().strip()
            if not center_name:
                messagebox.showerror("Erreur", "Veuillez sélectionner un point centre")
                return
            
            radius_str = viewer.cercle_rayon_entry.get().strip()
            segments_str = app.cercle_segments_entry.get().strip() or "32"
            
            if not radius_str:
                messagebox.showerror("Erreur", "Veuillez entrer le rayon")
                return
            
            try:
                radius = float(radius_str)
                segments = int(segments_str)
            except ValueError:
                messagebox.showerror("Erreur", "Valeurs numériques invalides")
                return
            
            # Convertir les unités en kilomètres si nécessaire
            radius_unit = app.cercle_rayon_unit.get()
            if radius_unit == "Nm":
                radius = radius * 1.852  # Conversion miles nautiques vers km
            elif radius_unit == "m":
                radius = radius / 1000  # Conversion mètres vers km
            
            # Récupérer les coordonnées du point centre
            conn_points = sqlite3.connect("point.db")
            cursor_points = conn_points.cursor()
            cursor_points.execute("SELECT lat, lon FROM points WHERE name = ?", (center_name,))
            center_result = cursor_points.fetchone()
            conn_points.close()
            
            if not center_result:
                messagebox.showerror("Erreur", f"Point centre '{center_name}' introuvable")
                return
            
            center_lat, center_lon = center_result
            
            # Vérifier s'il s'agit d'un arc
            is_arc = app.cercle_arc_var.get()
            
            if is_arc:
                # Récupérer les paramètres de l'arc
                try:
                    start_angle = float(app.arc_start_entry.get().strip() or "0")
                    end_angle = float(app.arc_end_entry.get().strip() or "360")
                    close_arc = app.arc_relie_var.get()
                except (ValueError, AttributeError):
                    messagebox.showerror("Erreur", "Paramètres d'arc invalides")
                    return
                
                # Calculer les points de l'arc
                circle_points = Utility.calculate_circle_points(
                    center_lat, center_lon, radius, segments, 
                    is_arc=True, start_angle_deg=start_angle, 
                    end_angle_deg=end_angle, close_arc=close_arc
                )
            else:
                # Calculer les points du cercle complet
                circle_points = Utility.calculate_circle_points(
                    center_lat, center_lon, radius, segments, is_arc=False
                )
            
            # Convertir au format attendu pour la base de données
            for lon, lat in circle_points:
                coordinates_list.append(f"{lon},{lat},0")
        
        # Vérifier que nous avons des coordonnées
        if not coordinates_list:
            messagebox.showerror("Erreur", "Aucune coordonnée générée")
            return        
                
        #  Création de la chaine de coordonnées
        points_str = " ".join(coordinates_list)

        # Ajout à la base de données 
        result=polygone_add(name,                         
                        color, 
                        width, 
                        fill,
                        fill_color,
                        points_str)

        if result == "error" or result == "cancelled":
            return        
        
        # Rechargement de la liste des polygones dans le treeview
        load_item_treeview(viewer,"polygones.db",viewer.polygones_checked_items,viewer.polygones_tree,"polygons")

        if result == "updated":
            messagebox.showinfo("Succès", f"Polygone '{name}' mis à jour avec succès")
        else:
            messagebox.showinfo("Succès", f"Polygone '{name}' créé avec succès")
             
        
        # Réinitialise les champs de saisie
        viewer.polygone_name_entry.delete(0, tk.END)        
        
        if creation_mode == "points":
            # Vider la listbox des points du polygone
            viewer.line_points_listbox_polygon.delete(0, tk.END)
            
        
        elif creation_mode == "carte":
            #Vide la liste des points cliqués et efface le polygone temporaire
            # viewer.clicked_points_poly = []
            # clear_temp_polygon(viewer) 
            pass                           
                               
        # Redessiner les polygones sur la carte
        # if hasattr(viewer, 'mbtiles_manager'):
        #     viewer.mbtiles_manager.draw_polygones()            
        
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création du polygone: {e}")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inattendue: {e}")

def point_add(name, lat, lon, alt, scale, icon, color, hotspot_x, hotspot_y, label_color):
    """Ajouter un point à la base de données"""

    print("Dans point_add")

    try:
        conn = sqlite3.connect("points.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM points WHERE name = ?", (name,))

        if cursor.fetchone():   

            answer=messagebox.askyesno(
                "Point existant",
                f"Un point avec le nom '{name}' existe déja.\n Voulez-vous modifier ce point avec les nouvelles valeurs ?",
            )

            if not answer:
                return "cancelled"

            cursor.execute(
                "UPDATE points SET lat = ?, lon = ?, alt = ?, scale = ?, icon = ?, color = ?, hotspot_x = ?, hotspot_y = ?, label_color = ? WHERE name = ?",
                (lat, lon, alt, scale, icon, color, hotspot_x, hotspot_y, label_color, name),
            )
                    
            conn.commit()
            return "updated"

        print("Insertion du point")
        cursor.execute("INSERT INTO points (name, lat, lon, alt, scale, icon, color, hotspot_x, hotspot_y, label_color) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, lat, lon, alt, scale, icon, color, hotspot_x, hotspot_y, label_color),)
        conn.commit()
        return "created"    
    
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création du point: {e}")
        return "error"
    finally:
        if "conn" in locals():
            conn.close()

def create_database():
    """Créer les bases de données SQLite points.db, lignes.db, polygones.db"""
    # Base point.db
    conn = sqlite3.connect("points.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS points")
    cursor.execute("""CREATE TABLE points (
                   name TEXT PRIMARY KEY,
                   lat REAL,
                   lon REAL,
                   alt REAL,
                   scale REAL DEFAULT 1.0,
                   icon TEXT,
                   color TEXT,
                   hotspot_x REAL,
                   hotspot_y REAL,
                   label_color TEXT)""")
    conn.commit()
    conn.close()

    # Base ligne.db
    conn = sqlite3.connect("lignes.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS lines")
    cursor.execute("""CREATE TABLE lines(
                   name TEXT PRIMARY KEY,
                   color TEXT,
                   width INTEGER,
                   points_list TEXT)""")
    conn.commit()
    conn.close()

    # Base polygone.db
    conn = sqlite3.connect("polygones.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS polygons")
    cursor.execute("""CREATE TABLE polygons (
                   name TEXT PRIMARY KEY,
                   color TEXT,
                   width INTEGER,
                   fill BOOLEAN,
                   fill_color TEXT,
                   points_list TEXT)""")
    conn.commit()
    conn.close()

def create_point_from_deg(viewer):
    """Créer un point dans la base puis efface les champs de saisie"""
    
    name = viewer.nom_entry.get().strip()
    lat_text = viewer.lat_entry.get().strip()
    lon_text = viewer.lon_entry.get().strip()    

    # Vérifications
    if not name:
        messagebox.showerror("Erreur", "Le nom du point est obligatoire")
        return

    if not lat_text or not lon_text:
        messagebox.showerror("Erreur", "Les coordonnées sont obligatoires")
        return    

    try:
        lat = float(lat_text)
        lon = float(lon_text)       

        if not (-90 <= lat <= 90):
            messagebox.showerror("Erreur", "La latitude doit être entre -90 et 90")
            return

        if not (-180 <= lon <= 180):
            messagebox.showerror("Erreur", "La longitude doit être entre -180 et 180")
            return        

    except ValueError:
        messagebox.showerror("Erreur", "Format de coordonnées invalide")
        return

    # Ajouter à la base de données
    result=point_add(name,
                     lat,
                     lon, 
                     viewer.altitude.get(), 
                     viewer.taille_entry.get(), 
                     viewer.type_points_entry.get(), 
                     viewer.point_color_entry.get(), 
                     viewer.hotspot_x.get(), 
                     viewer.hotspot_y.get(), 
                     viewer.label_color_entry.get())

    if result == "error" or result == "cancelled":
        return

    # Recharger la liste des points
    #load_points_treeview(viewer)
    load_item_treeview(viewer,"points.db",viewer.points_checked_items,viewer.tree,"points")
    

    if result == "updated":
        messagebox.showinfo("Succès", f"Point '{name}' mis à jour avec succès")
    else:
        messagebox.showinfo("Succès", f"Point '{name}' créé avec succès")

    # Réinitialiser les champs
    viewer.nom_entry.delete(0, tk.END)
    viewer.lat_entry.delete(0, tk.END)
    viewer.lon_entry.delete(0, tk.END)

def create_point_from_deg_min(viewer):
    """Créer un point à partir des coordonnées degrés/minutes"""
    
    name = viewer.nom_entry.get().strip()
    lat_deg_text = viewer.lat_deg_entry.get().strip()
    lat_min_text = viewer.lat_min_entry.get().strip()
    lon_deg_text = viewer.lon_deg_entry.get().strip()
    lon_min_text = viewer.lon_min_entry.get().strip()

    if not name:
        messagebox.showerror("Erreur", "Le nom du point est obligatoire")
        return

    if not lat_deg_text or not lat_min_text or not lon_deg_text or not lon_min_text:
        messagebox.showerror("Erreur", "Les coordonnées sont obligatoires")
        return
    
    try:
        # Latitude
        lat_deg = int(lat_deg_text)
        lat_min = float(lat_min_text)
        lat_ns = viewer.lat_ns_combo.get()
        
        # Longitude
        lon_deg = int(lon_deg_text)
        lon_min = float(lon_min_text)
        lon_ew = viewer.lon_ew_combo.get()
        
        # Conversion en degrés décimaux
        lat = lat_deg + lat_min / 60
        if lat_ns == "S":
            lat = -lat
            
        lon = lon_deg + lon_min / 60
        if lon_ew == "O":
            lon = -lon
        
        # Vérifications
        if not (0 <= lat_deg <= 90) or not (0 <= lat_min < 60):
            messagebox.showerror("Erreur", "Latitude invalide")
            return
            
        if not (0 <= lon_deg <= 180) or not (0 <= lon_min < 60):
            messagebox.showerror("Erreur", "Longitude invalide")
            return
            
    except ValueError:
        messagebox.showerror("Erreur", "Format de coordonnées invalide")
        return

    # Ajouter à la base de données
    result=point_add(name,
                     lat,
                     lon, 
                     viewer.altitude.get(), 
                     viewer.taille_entry.get(), 
                     viewer.type_points_entry.get(), 
                     viewer.point_color_entry.get(), 
                     viewer.hotspot_x.get(), 
                     viewer.hotspot_y.get(), 
                     viewer.label_color_entry.get())

    if result == "error" or result == "cancelled":
        return

    # Recharger la liste des points
    load_item_treeview(viewer,"points.db",viewer.points_checked_items,viewer.tree,"points")
    if result == "updated":
        messagebox.showinfo("Succès", f"Point '{name}' mis à jour avec succès")
    else:
        messagebox.showinfo("Succès", f"Point '{name}' créé avec succès")    
        
    # Réinitialiser les champs
    viewer.nom_entry.delete(0, tk.END)
    viewer.lat_deg_entry.delete(0, tk.END)
    viewer.lat_min_entry.delete(0, tk.END)
    viewer.lon_deg_entry.delete(0, tk.END)
    viewer.lon_min_entry.delete(0, tk.END) 

def create_point_from_deg_min_sec(viewer):
    """Créer un point à partir des coordonnées degrés/minutes/secondes"""
    name = viewer.nom_entry.get().strip()
    
    if not name:
        messagebox.showerror("Erreur", "Le nom du point est obligatoire")
        return
    
    try:
        # Latitude
        lat_deg = int(viewer.lat_deg_entry.get())
        lat_min = int(viewer.lat_min_entry.get())
        lat_sec = float(viewer.lat_sec_entry.get())
        lat_ns = viewer.lat_ns_combo.get()
        
        # Longitude
        lon_deg = int(viewer.lon_deg_entry.get())
        lon_min = int(viewer.lon_min_entry.get())
        lon_sec = float(viewer.lon_sec_entry.get())
        lon_ew = viewer.lon_ew_combo.get()
        
        # Conversion en degrés décimaux
        lat = lat_deg + lat_min / 60 + lat_sec / 3600
        if lat_ns == "S":
            lat = -lat
            
        lon = lon_deg + lon_min / 60 + lon_sec / 3600
        if lon_ew == "O":
            lon = -lon
        
        # Vérifications
        if not (0 <= lat_deg <= 90) or not (0 <= lat_min < 60) or not (0 <= lat_sec < 60):
            messagebox.showerror("Erreur", "Latitude invalide")
            return
            
        if not (0 <= lon_deg <= 180) or not (0 <= lon_min < 60) or not (0 <= lon_sec < 60):
            messagebox.showerror("Erreur", "Longitude invalide")
            return
            
    except ValueError:
        messagebox.showerror("Erreur", "Format de coordonnées invalide")
        return       
        
    # Ajouter à la base de données
    result=point_add(name,
                     lat,
                     lon, 
                     viewer.altitude.get(), 
                     viewer.taille_entry.get(), 
                     viewer.type_points_entry.get(), 
                     viewer.point_color_entry.get(), 
                     viewer.hotspot_x.get(), 
                     viewer.hotspot_y.get(), 
                     viewer.label_color_entry.get())

    if result == "error" or result == "cancelled":
        return

    # Recharger la liste des points
    load_item_treeview(viewer,"points.db",viewer.points_checked_items,viewer.tree,"points")
    if result == "updated":
        messagebox.showinfo("Succès", f"Point '{name}' mis à jour avec succès")
    else:
        messagebox.showinfo("Succès", f"Point '{name}' créé avec succès")
        
    # Réinitialiser les champs
    viewer.nom_entry.delete(0, tk.END)
    viewer.lat_deg_entry.delete(0, tk.END)
    viewer.lat_min_entry.delete(0, tk.END)
    viewer.lat_sec_entry.delete(0, tk.END)
    viewer.lon_deg_entry.delete(0, tk.END)
    viewer.lon_min_entry.delete(0, tk.END)
    viewer.lon_sec_entry.delete(0, tk.END)     

def create_point_from_calamar(viewer):
    """Créer un point à partir des coordonnées Calamar"""
    name = viewer.nom_entry.get().strip()
    
    if not name:
        messagebox.showerror("Erreur", "Le nom du point est obligatoire")
        return
    
    try:
        y_val = float(viewer.calamar_x_entry.get())
        x_val = float(viewer.calamar_y_entry.get())
        y_unit = viewer.calamar_x_combo.get()
        x_unit = viewer.calamar_y_combo.get()
        
        # Conversion en GPS
        lat, lon = utility.convert_calamar_to_gps(x_val, y_val, x_unit, y_unit)
        
    except ValueError:
        messagebox.showerror("Erreur", "Format de coordonnées invalide")
        return
    
    # Ajouter à la base de données
    result=point_add(name,
                     lat,
                     lon, 
                     viewer.altitude.get(), 
                     viewer.taille_entry.get(), 
                     viewer.type_points_entry.get(), 
                     viewer.point_color_entry.get(), 
                     viewer.hotspot_x.get(), 
                     viewer.hotspot_y.get(), 
                     viewer.label_color_entry.get())

    if result == "error" or result == "cancelled":
        return

    # Recharger la liste des points
    load_item_treeview(viewer,"points.db",viewer.points_checked_items,viewer.tree,"points")
    if result == "updated":
        messagebox.showinfo("Succès", f"Point '{name}' mis à jour avec succès")
    else:
        messagebox.showinfo("Succès", f"Point '{name}' créé avec succès")
        
    # Vider les champs
    viewer.nom_entry.delete(0, tk.END)
    viewer.calamar_y_entry.delete(0, tk.END)
    viewer.calamar_x_entry.delete(0, tk.END)
    viewer.calamar_y_combo.set("mL")
    viewer.calamar_x_combo.set("mD")       

def create_point_from_radial(viewer):
    """Créer un point à partir d'un relèvement/distance"""
    name = viewer.nom_entry.get().strip()
    point_depart_nom = viewer.radial_point_combo.get()
    
    if not name:
        messagebox.showerror("Erreur", "Le nom du point est obligatoire")
        return
    
    if not point_depart_nom:
        messagebox.showerror("Erreur", "Sélectionnez un point de départ")
        return
    
    try:
        distance_val = float(viewer.radial_distance_entry.get())
        bearing_deg = float(viewer.radial_bearing_entry.get())
        distance_unit = viewer.radial_distance_combo.get()
        
        if distance_val <= 0:
            messagebox.showerror("Erreur", "La distance doit être positive")
            return
        
        if not (0 <= bearing_deg < 360):
            messagebox.showerror("Erreur", "Le gisement doit être entre 0 et 359°")
            return
        
    except ValueError:
        messagebox.showerror("Erreur", "Valeurs numériques invalides")
        return
    
    # Récupérer le point de départ
    conn = sqlite3.connect("points.db")
    cursor = conn.cursor()
    cursor.execute("SELECT lat, lon FROM points WHERE name = ?", (point_depart_nom,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        messagebox.showerror("Erreur", "Point de départ introuvable")
        return
    
    start_point = {"lat": result[0], "lon": result[1]}
    
    # Convertir la distance en km
    distance_km = distance_val * 1.852 if distance_unit == "nautiques" else distance_val / 1000
    
    # Calculer le nouveau point
    lat, lon = utility.create_point_from_bearing_distance(start_point, distance_km, bearing_deg)
    
    # Ajouter à la base de données
    result=point_add(name,
                     lat,
                     lon, 
                     viewer.altitude.get(), 
                     viewer.taille_entry.get(), 
                     viewer.type_points_entry.get(), 
                     viewer.point_color_entry.get(), 
                     viewer.hotspot_x.get(), 
                     viewer.hotspot_y.get(), 
                     viewer.label_color_entry.get())

    if result == "error" or result == "cancelled":
        return

    # Recharger la liste des points
    load_item_treeview(viewer,"points.db",viewer.points_checked_items,viewer.tree,"points")
    if result == "updated":
        messagebox.showinfo("Succès", f"Point '{name}' mis à jour avec succès")
    else:
        messagebox.showinfo("Succès", f"Point '{name}' créé avec succès")
        
    # Vider les champs
    viewer.nom_entry.delete(0, tk.END)
    viewer.radial_distance_entry.delete(0, tk.END)
    viewer.radial_bearing_entry.delete(0, tk.END)    

def create_point_from_click(viewer):
    """Créer un point dans la base de donnée à partir du mode click"""
        
    name = viewer.nom_entry.get().strip()
    lat_text = viewer.click_lat_entry.get()
    lon_text = viewer.click_lon_entry.get()

    print(name, lat_text, lon_text)

    if not name:
        messagebox.showerror("Erreur", "Le nom du point est obligatoire")
        return
    
    if not lat_text or not lon_text:
        messagebox.showerror("Erreur", "Cliquez d'abord sur la carte pour sélectionner les coordonnées")
        return
    
    try:
        lat = float(lat_text)
        lon = float(lon_text)
    except ValueError:
        messagebox.showerror("Erreur", "Coordonnées invalides")
        return
    
    # Ajouter à la base de données
    result=point_add(name,
                     lat,
                     lon, 
                     viewer.altitude.get(), 
                     viewer.taille_entry.get(), 
                     viewer.type_points_entry.get(), 
                     viewer.point_color_entry.get(), 
                     viewer.hotspot_x.get(), 
                     viewer.hotspot_y.get(), 
                     viewer.label_color_entry.get())

    if result == "error" or result == "cancelled":
        return

    # Recharger la liste des points
    load_item_treeview(viewer,"points.db",viewer.points_checked_items,viewer.tree,"points")
    if result == "updated":
        messagebox.showinfo("Succès", f"Point '{name}' mis à jour avec succès")
    else:
        messagebox.showinfo("Succès", f"Point '{name}' créé avec succès")
        
    # Réinitialiser les champs
    viewer.click_nom_entry.delete(0, tk.END)
    viewer.click_lat_entry.delete(0, tk.END)
    viewer.click_lon_entry.delete(0, tk.END)

def database_closing(self):
    """Gérer la fermeture du programme en proposant de sauver le travail."""
    answer = messagebox.askyesnocancel("Quitter", "Voulez-vous sauvegarder votre travail ?")

    if answer is None:
        # L'utilisateur annule la fermeture
        return

    if answer is False:
        # L'utilisateur ne souhaite pas sauver : supprimer les fichiers de base
        try:
            for db_file in ["points.db", "lignes.db", "polygones.db"]:
                if os.path.exists(db_file):
                    os.remove(db_file)
        except PermissionError:
            pass

    # Si answer is True, on conserve les bases et on quitte
    self.root.destroy()
