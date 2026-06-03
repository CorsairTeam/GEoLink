import os
import sqlite3
from tkinter import messagebox
import tkinter as tk
import utility

def delete_selected_points(viewer):
    """Supprimer les points cochés de la base de données et du treeview"""
    to_delete = [item for item, info in viewer.points_checked_items.items() if info["checked"]]
    if not to_delete:
        messagebox.showwarning("Suppression", "Aucun point sélectionné.")
        return
    
    try:
        conn = sqlite3.connect("points.db")
        cursor = conn.cursor()
        for item in to_delete:
            name = viewer.tree.item(item)["values"][1]
            cursor.execute("DELETE FROM points WHERE name = ?", (name,))
        conn.commit()
        conn.close()
        
        load_points_treeview(viewer)
        messagebox.showinfo("Suppression", f"{len(to_delete)} point(s) supprimé(s).")
        
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def load_points_treeview(viewer):
    """Met a jour le Tree view et affiche les points sur la carte"""
    for item in viewer.tree.get_children():
        viewer.tree.delete(item)
    
    #Checked_items : Stocke les informations des points enregistrés dans le treeview
    viewer.points_checked_items = {}
    conn = sqlite3.connect("points.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, lat, lon, alt, scale, icon, color, hotspot_x, hotspot_y, label_color FROM points")
    for row in cursor.fetchall():
        item_id = viewer.tree.insert("", tk.END, values=("⬜", row[0]))
        viewer.points_checked_items[item_id] = {"checked": False, "data": row}
    conn.close()
    
    # # Mettre à jour l'affichage sur la carte
    # viewer.mbtiles_manager.draw_points()

def load_points_line(viewer):
    """Charger tous les points depuis points.db"""
    viewer.points_listbox.delete(0, tk.END)
    try:
        conn = sqlite3.connect("points.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM points ORDER BY name")
        points = cursor.fetchall()
        conn.close()
        
        for point in points:
            viewer.points_listbox.insert(tk.END, point[0])
    except sqlite3.Error:
        pass

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
    load_points_treeview(viewer)
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
    load_points_treeview(viewer)
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
    load_points_treeview(viewer)
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
    load_points_treeview(viewer)
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
    load_points_treeview(viewer)
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
    load_points_treeview(viewer)
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
