import os
import sqlite3
from tkinter import messagebox
import tkinter as tk

def create_database():
    """Créer les bases de données SQLite points.db, lignes.db, polygones.db"""
    # Base point.db
    conn = sqlite3.connect("points.db")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS points')
    cursor.execute('''CREATE TABLE points (
                   name TEXT PRIMARY KEY,
                   lat REAL,
                   lon REAL,
                   alt REAL,
                   scale REAL DEFAULT 1.0,
                   icon TEXT,
                   color TEXT,
                   hotspot_x REAL,
                   hotspot_y REAL,
                   label_color TEXT)''')
    conn.commit()
    conn.close()
    
    # Base ligne.db
    conn = sqlite3.connect("lignes.db")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS lines')
    cursor.execute('''CREATE TABLE lines(
                   name TEXT PRIMARY KEY,
                   color TEXT,
                   width INTEGER,
                   points_list TEXT)''')
    conn.commit()
    conn.close()
    
    # Base polygone.db
    conn = sqlite3.connect("polygones.db")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS polygons')
    cursor.execute('''CREATE TABLE polygons (
                   name TEXT PRIMARY KEY,
                   color TEXT,
                   width INTEGER,
                   fill BOOLEAN,
                   fill_color TEXT,
                   points_list TEXT)''')
    conn.commit()
    conn.close()

def create_point_from_coords(viewer):
    """Créer un point dans la base puis efface les champs de saisie"""
    print("Création d'un point à partir des coordonnées saisies")
    nom = viewer.nom_entry.get().strip()
    lat_text = viewer.lat_entry.get().strip()
    lon_text = viewer.lon_entry.get().strip()

    # Vérifications
    if not nom:
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
    try:
        conn = sqlite3.connect("points.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO points (name, lat, lon) VALUES (?, ?, ?)", (nom, lat, lon)
        )
        conn.commit()
        conn.close()

        # # Recharger la liste des points
        # load_points(viewer)
        # messagebox.showinfo("Succès", f"Point '{nom}' créé avec succès")

        # Réinitialiser les champs
        viewer.nom_entry.delete(0, tk.END)
        viewer.lat_entry.delete(0, tk.END)
        viewer.lon_entry.delete(0, tk.END)

    except sqlite3.IntegrityError:
        messagebox.showerror("Erreur", f"Un point avec le nom '{nom}' existe déjà")
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création du point: {e}")
    finally:
        if "conn" in locals():
            conn.close()

def database_closing(self):
    """Gérer la fermeture du programme en proposant de sauver le travail."""
    answer = messagebox.askyesnocancel( "Quitter",       
        "Voulez-vous sauvegarder votre travail ?"       
    )

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

def create_database_point(nom, lat_text, lon_text, alt, scale_text, icon, color, hotspot_x_text, hotspot_y_text, label_color):
    """Créer un point dans la base de données apartir de coordonnées en degrés"""
    nom = "Point1"
    lat_text = "44.772087"
    lon_text = "-1.158371"
    scale_text= "1.0"
    alt = "0.0"
    icon = "http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png"
    color = "#FF0000"
    hotspot_x_text = "20"
    hotspot_y_text = "20"
    label_color = "#FF0000"

    # Vérifications
    if not nom:
        messagebox.showerror("Erreur", "Le nom du point est obligatoire")
        return
    
    if not lat_text or not lon_text:
        messagebox.showerror("Erreur", "Les coordonnées sont obligatoires")
        return
    
    try:
        lat = float(lat_text)
        lon = float(lon_text)
        alt= float(alt)
        scale=float(scale_text)
        hotspot_x=float(hotspot_x_text)
        hotspot_y=float(hotspot_y_text)
        
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
    try:
        conn = sqlite3.connect("points.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO points (name, lat, lon, alt, scale, icon, color, hotspot_x, hotspot_y, label_color) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (nom, lat, lon, alt, scale, icon, color, hotspot_x, hotspot_y, label_color)
        )
        conn.commit()
        conn.close()               
        
    except sqlite3.IntegrityError:
        messagebox.showerror("Erreur", f"Un point avec le nom '{nom}' existe déjà")
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la création du point: {e}")
    finally:
        if 'conn' in locals():
            conn.close()   

def delete_database_points(to_delete):
    """Supprimer les points dont les noms figurent dans la liste to_delete"""
    try:
        conn = sqlite3.connect("points.db")
        cursor = conn.cursor()
        for name in to_delete:
            cursor.execute("DELETE FROM points WHERE name = ?", (name,))
        conn.commit()
        conn.close()        
        
        messagebox.showinfo("Suppression", f"{len(to_delete)} point(s) supprimé(s).")
        
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")
    finally:
        if 'conn' in locals():
            conn.close()