import tkinter as tk
import math
import sqlite3

# Constantes WGS84
WGS84_A = 6378137.0  # Demi-grand axe (m)
WGS84_F = 1/298.257223563  # Aplatissement
WGS84_B = WGS84_A * (1 - WGS84_F)  # Demi-petit axe


def create_point_from_bearing_distance(start_point, distance_km, bearing_deg):
    """Créer un point depuis un point de départ, une distance en km et un gisement en degrés"""
    lat1 = math.radians(float(start_point["lat"]))
    lon1 = math.radians(float(start_point["lon"]))
    bearing = math.radians(bearing_deg)
    angular_distance = (distance_km * 1000) / WGS84_A

    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular_distance)
        + math.cos(lat1) * math.sin(angular_distance) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(angular_distance) * math.cos(lat1),
        math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2)
    )

    lat = math.degrees(lat2)
    lon = (math.degrees(lon2) + 540) % 360 - 180

    return lat, lon


def calculate_arrow_points(center_lat, center_lon, length_forward, length_backward, length_right, length_left, orientation):
    """Calcul d'une barre d'orientation positionnée au milieu du côté avant du rectangle.

    Args:
        center_lat, center_lon: Coordonnées du centre du rectangle
        length_km: Distance du centre au côté avant (longueur avant) en km
        bearing_deg: Orientation du rectangle en degrés (0° = Nord)
        width_km: Largeur totale du rectangle en km (pour calculer la longueur de la barre)

    Returns:
        Liste des points (lon, lat) formant la barre d'orientation.
    """
    center_point = {"lat": center_lat, "lon": center_lon}

    # Point de départ : milieu du côté avant du rectangle
    if (length_right-length_left > 0) :
        bearing = orientation + math.degrees(math.atan2((length_right-length_left)/2, length_forward))  # Côté droit
        distance= math.hypot(length_forward, (length_right-length_left)/2)
    else:
        bearing = orientation - math.degrees(math.atan2(-(length_right-length_left)/2, length_forward))  # Côté gauche
        distance= math.hypot(length_forward, (length_left-length_right)/2)

    arrow_start_lat, arrow_start_lon = create_point_from_bearing_distance(center_point, distance, bearing)

    # Longueur de la barre : par défaut la moitié de la largeur disponible
    arrow_length_km = ((length_right+length_left) / 2) 
    arrow_end_lat, arrow_end_lon = create_point_from_bearing_distance(
        {"lat": arrow_start_lat, "lon": arrow_start_lon},
        arrow_length_km,
        orientation
    )

    return [
        (arrow_start_lon, arrow_start_lat),
        (arrow_end_lon, arrow_end_lat)
    ]

def calculate_rectangle_points(center_lat, center_lon, length_forward_km, length_backward_km, length_right_km, length_left_km, bearing_deg):
    """Calcul de rectangles avec précision Vincenty.

    Les longueurs sont exprimées depuis le centre vers les côtés :
    - length_forward_km : distance du centre vers l'avant, dans l'azimut bearing_deg
    - length_backward_km : distance du centre vers l'arrière, dans l'azimut opposite
    - length_right_km : distance du centre vers la droite
    - length_left_km : distance du centre vers la gauche
    """
    center_point = {"lat": center_lat, "lon": center_lon}

    corners_local = [
        (length_forward_km, length_right_km),
        (length_forward_km, -length_left_km),
        (-length_backward_km, -length_left_km),
        (-length_backward_km, length_right_km)
    ]
    
    rectangle_points = []

    for x_local, y_local in corners_local:
        dist_to_corner = math.hypot(x_local, y_local)
        angle_relative = math.degrees(math.atan2(y_local, x_local))
        absolute_bearing = (bearing_deg + angle_relative) % 360
        
        new_lat, new_lon = create_point_from_bearing_distance(center_point, dist_to_corner, absolute_bearing)
        rectangle_points.append((new_lon, new_lat))
    
    rectangle_points.append(rectangle_points[0])  # Fermer le rectangle
    return rectangle_points

def calculate_circle_points(center_lat, center_lon, radius_km, num_segments, is_arc=False, start_angle_deg=0, end_angle_deg=360, close_arc=True):
    """Calcul de cercles ou arcs avec précision Vincenty"""
    points = []
    center_point = {"lat": center_lat, "lon": center_lon}

    if is_arc:
        if end_angle_deg < start_angle_deg:
            end_angle_deg += 360
        
        # Pour les arcs fermés, ajouter le centre au début
        if close_arc:
            points.append((center_lon, center_lat))
        
        angle_range = end_angle_deg - start_angle_deg
        effective_num_segments = max(num_segments, int(abs(angle_range)))
        
        # Générer les points de l'arc
        for i in range(effective_num_segments + 1):
            angle_deg = start_angle_deg + (angle_range / effective_num_segments) * i
            if angle_deg > 360:
                angle_deg -= 360
            
            new_lat, new_lon = create_point_from_bearing_distance(center_point, radius_km, angle_deg)
            points.append((new_lon, new_lat))
        
        # Pour les arcs fermés, fermer vers le centre
        if close_arc:
            points.append((center_lon, center_lat))
    else:
        # Cercle complet
        for i in range(num_segments + 1):
            angle_deg = (360 / num_segments) * i
            new_lat, new_lon = create_point_from_bearing_distance(center_point, radius_km, angle_deg)
            points.append((new_lon, new_lat))
    return points

def pixel_to_latlon(x, y, offset_x, offset_y, min_col, max_row, zoom):
    """Convertir coordonnées pixel en lat/lon exprimés en degrés décimaux"""
    # Position dans l'image
    image_x = x - offset_x
    image_y = y - offset_y
    
    # Coordonnées de tuile integrant la position du point dans la tuile dans les décimales
    tile_x = image_x / 256 + min_col
    tile_y = max_row - image_y / 256
    
    # Conversion en lat/lon (correction TMS)
    n = 2 ** zoom
    lon = tile_x / n * 360.0 - 180.0    

    # Inverser tile_y pour TMS (Y=0 au pole sud)
    tile_y_corrected = n - 1 - tile_y
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y_corrected / n)))
    lat = math.degrees(lat_rad)
    
    return lat, lon

def update_coordinates(x, y, offset_x, offset_y, min_col, max_row, zoom):
    """Récupère les coordonnées du pointeur de la souris en degrés"""
    return pixel_to_latlon(x, y, offset_x, offset_y, min_col, max_row, zoom)

def latlon_to_pixel(lat, lon, offset_x, offset_y, min_col, max_row, zoom):
    """Convertir lat/lon en coordonnées pixel dans le canvas"""
    n = 2 ** zoom
    
    # Conversion lon en tile_x
    tile_x = (lon + 180.0) / 360.0 * n
    
    # Conversion lat en tile_y (correction TMS)
    lat_rad = math.radians(lat)
    tile_y_corrected = (1 - math.asinh(math.tan(lat_rad)) / math.pi) / 2 * n
    tile_y = n - 1 - tile_y_corrected
    
    # Position dans l'image
    image_x = (tile_x - min_col) * 256
    image_y = (max_row - tile_y) * 256
    
    # Coordonnées pixel dans le canvas
    x = image_x + offset_x
    y = image_y + offset_y
    
    return x, y



def add_point_to_line(viewer,listbox_points,listbox_line):
    """Ajouter un point sélectionné à la ligne"""
    selection = listbox_points.curselection()
    if selection:
        point_name = listbox_points.get(selection[0])
        listbox_line.insert(tk.END, point_name)

def remove_point_from_line(viewer,listbox_line):
    """Retirer un point sélectionné de la ligne"""
    selection = listbox_line.curselection()
    if selection:
        listbox_line.delete(selection[0])

def enable_line_points_drag_reorder(viewer,listbox):
    #Permet de faire du drag dans la liste des points de la ligne avec le clic gauche maintenu
    #En paramètre le nom de la listbox

    def start_drag(event):
        index = listbox.nearest(event.y)
        if 0 <= index < listbox.size():
            viewer.line_points_drag_index = index
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(index)
            listbox.activate(index)

    def drag_motion(event):
        if not hasattr(viewer, "line_points_drag_index"):
            return

        source_index = viewer.line_points_drag_index
        target_index = listbox.nearest(event.y)
        if target_index < 0:
            target_index = 0
        elif target_index >= listbox.size():
            target_index = listbox.size() - 1

        if target_index == source_index:
            return

        point_name = listbox.get(source_index)
        listbox.delete(source_index)
        listbox.insert(target_index, point_name)
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(target_index)
        listbox.activate(target_index)
        viewer.line_points_drag_index = target_index

    def stop_drag(event):
        if hasattr(viewer, "line_points_drag_index"):
            del viewer.line_points_drag_index

    listbox.bind("<ButtonPress-1>", start_drag)
    listbox.bind("<B1-Motion>", drag_motion)
    listbox.bind("<ButtonRelease-1>", stop_drag)

class ToolTip:
    """Classe pour créer des info-bulles (tooltips) sur les widgets"""
    enabled = True
    instances = []
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        ToolTip.instances.append(self)
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    @classmethod
    def set_enabled(cls, enabled):
        cls.enabled = enabled
        if not enabled:
            for tooltip in cls.instances:
                tooltip.hide_tooltip()
                
    
    def show_tooltip(self, event=None):
        """Afficher l'info-bulle"""
        if not ToolTip.enabled or self.tooltip_window or not self.text:
            return
        
        # Calculer la position de l'info-bulle
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Créer la fenêtre de l'info-bulle
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Pas de bordure de fenêtre
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Créer le label avec le texte
        tooltip_frame = tk.Frame(
            self.tooltip_window,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=6
        )
        tooltip_frame.pack()

        for line in self.text.splitlines():
            label = tk.Label(
                tooltip_frame,
                text=f" {line} ",
                background="#ffffe0",
                font=("Arial", 9),
                justify="left",
                anchor="w"
            )
            label.pack(fill=tk.X, pady=1)
    
    def hide_tooltip(self, event=None):
        """Masquer l'info-bulle"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def format_point_scale(scale):
    """Formate la valeur de taille d'un point sans la réduire à un entier."""
    try:
        scale_value = float(scale)
    except (TypeError, ValueError):
        return str(scale)

    return f"{scale_value:.1f}".rstrip("0").rstrip(".") or "0"

def point_field_fill(viewer, item):
    """Remplit les champs du point cliqué dans le Tree view.\n
    Bascule dans la page de création par coordonnées"""
    
    import notebook_points

    data = viewer.points_checked_items[item]["data"]
    name, lat, lon, alt, scale, icon, color, hotspot_x, hotspot_y, label_color = data
    viewer.creation_mode.set("coordonnees")
    viewer.coord_type.set("Degrés")
    
    #Affiche la page degrés
    if hasattr(viewer, "coord_combo"):
        viewer.coord_combo.set("Degrés")
    notebook_points.update_input_frame_points(viewer)

    if hasattr(viewer, "nom_entry"):
        viewer.nom_entry.delete(0, tk.END)
        viewer.nom_entry.insert(0, name)

    if hasattr(viewer, "taille_entry"):
        viewer.taille_entry.set(format_point_scale(scale))

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

def line_field_fill(viewer, item):
    """Remplit les champs de la ligne cliquée dans le Tree view."""

    data = viewer.lines_checked_items[item]["data"]

    try:
        coordinates_list = data[3].split()
        if coordinates_list and viewer.db_path:
            first_point = coordinates_list[0].split(',')
            if len(first_point) >= 2:
                lon = float(first_point[0])
                lat = float(first_point[1])
                viewer.mbtiles_manager.center_map_on_point(lat, lon)
    except Exception as e:
        print(f"Erreur lors du centrage sur la ligne: {e}")

    if hasattr(viewer, "line_name_entry"):
        viewer.line_name_entry.delete(0, tk.END)
        viewer.line_name_entry.insert(0, data[0])

    if hasattr(viewer, "taille_entry"):
        viewer.taille_entry.set(str(data[2]))

    if hasattr(viewer, "line_color_entry"):
        viewer.line_color_entry.set(data[1])

def polygon_field_fill(viewer, item):
    """Remplit les champs du polygone cliqué dans le Tree view."""    

    data = viewer.polygones_checked_items[item]["data"]          

    #Centrage de la carte sur le polygone sélectionné
    try:
        coordinates_list = data[5].split()
        if coordinates_list and viewer.db_path:
            first_point = coordinates_list[0].split(',')
            if len(first_point) >= 2:
                lon = float(first_point[0])
                lat = float(first_point[1])
                viewer.mbtiles_manager.center_map_on_point(lat, lon)
    except Exception as e:
        print(f"Erreur lors du centrage sur le polygone: {e}")

    #Mise a jour des champs
    if hasattr(viewer, "polygone_name_entry"):
        viewer.polygone_name_entry.delete(0, tk.END)
        viewer.polygone_name_entry.insert(0, data[0])

    if hasattr(viewer, "taille_entry"):
        viewer.taille_entry.set(str(data[2]))

    if hasattr(viewer, "line_color_entry"):
        viewer.line_color_entry.set(data[1])

    if hasattr(viewer, "fill_color_entry"):
        viewer.fill_color_entry.set(data[4])

    if hasattr(viewer, "polygone_fill_var"):
        viewer.polygone_fill_var.set(1 if data[3] in (1, True, "1", "True", "true") else 0)

def on_tree_click(viewer, event, checked_items, treeview):
    """En fonction du clic, coche la case ou remplit les champs de Input_frame"""
    region = treeview.identify_region(event.x, event.y)
    if region == "cell":
        item = treeview.identify_row(event.y)
        column = treeview.identify_column(event.x)
        
        if column == "#1" and item in checked_items:
            toggle_checkbox(item, checked_items, treeview)

        if column == "#2" and item in checked_items and checked_items is viewer.points_checked_items:
            point_field_fill(viewer, item)

        if column == "#2" and item in checked_items and checked_items is viewer.lines_checked_items and viewer.ligne_modif_var.get():
            line_field_fill(viewer, item)

        if column == "#2" and item in checked_items and checked_items is viewer.polygones_checked_items and viewer.polygone_modif_var.get():
            polygon_field_fill(viewer, item)

def toggle_checkbox(item, checked_items, treeview):
    """Gère le cochage/décochage de la coche du Treeview"""
    #Structure de  checked_items I00_": {"checked": False,"data": (...)}
    current_state = checked_items[item]["checked"]
    new_state = not current_state
    checked_items[item]["checked"] = new_state
    
    values = list(treeview.item(item)["values"])
    values[0] = "✅" if new_state else "⬜"
    treeview.item(item, values=values)

def convert_calamar_to_gps(x_val, y_val, x_unit, y_unit):
    """Convertit des coordonnées Calamar en GPS"""
    import numpy as np
    
    calamar_points = np.array([
        [0.0, 0.0],
        [683.0, 921.0],
        [284.73, -398.51]
    ])
    
    gps_points = np.array([
        [44.52041351, -1.11661145],
        [44.523935, -1.130166],
        [44.51600897, -1.11683657]
    ])
    
    y_calamar = x_val if x_unit == "mL" else -x_val
    x_calamar = y_val if y_unit == "mD" else -y_val
    
    A = np.column_stack([calamar_points, np.ones(3)])
    lat_params = np.linalg.lstsq(A, gps_points[:, 0], rcond=None)[0]
    lon_params = np.linalg.lstsq(A, gps_points[:, 1], rcond=None)[0]
    
    result_lat = lat_params[0] * y_calamar + lat_params[1] * x_calamar + lat_params[2]
    result_lon = lon_params[0] * y_calamar + lon_params[1] * x_calamar + lon_params[2]
    
    return result_lat, result_lon

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



def calculate_distance(lat1, lon1, lat2, lon2):
    """Distance Vincenty inverse - précision sub-métrique"""
    if lat1 == lat2 and lon1 == lon2:
        return 0.0
    
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    
    L = lon2_rad - lon1_rad
    U1 = math.atan((1 - WGS84_F) * math.tan(lat1_rad))
    U2 = math.atan((1 - WGS84_F) * math.tan(lat2_rad))
    
    sin_U1, cos_U1 = math.sin(U1), math.cos(U1)
    sin_U2, cos_U2 = math.sin(U2), math.cos(U2)
    
    lambda_val = L
    for _ in range(100):
        sin_lambda, cos_lambda = math.sin(lambda_val), math.cos(lambda_val)
        sin_sigma = math.sqrt((cos_U2 * sin_lambda) ** 2 + (cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lambda) ** 2)
        
        if sin_sigma == 0:
            return 0.0
        
        cos_sigma = sin_U1 * sin_U2 + cos_U1 * cos_U2 * cos_lambda
        sigma = math.atan2(sin_sigma, cos_sigma)
        sin_alpha = cos_U1 * cos_U2 * sin_lambda / sin_sigma
        cos2_alpha = 1 - sin_alpha ** 2
        
        if cos2_alpha == 0:
            cos_2sigma_m = 0
        else:
            cos_2sigma_m = cos_sigma - 2 * sin_U1 * sin_U2 / cos2_alpha
        
        C = WGS84_F / 16 * cos2_alpha * (4 + WGS84_F * (4 - 3 * cos2_alpha))
        lambda_prev = lambda_val
        lambda_val = L + (1 - C) * WGS84_F * sin_alpha * (sigma + C * sin_sigma * (cos_2sigma_m + C * cos_sigma * (-1 + 2 * cos_2sigma_m ** 2)))
        
        if abs(lambda_val - lambda_prev) < 1e-12:
            break
    
    u2 = cos2_alpha * (WGS84_A ** 2 - WGS84_B ** 2) / (WGS84_B ** 2)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    delta_sigma = B * sin_sigma * (cos_2sigma_m + B / 4 * (cos_sigma * (-1 + 2 * cos_2sigma_m ** 2) - B / 6 * cos_2sigma_m * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos_2sigma_m ** 2)))
    
    return WGS84_B * A * (sigma - delta_sigma)

def calculate_bearing(lat1, lon1, lat2, lon2):
    """Gisement initial Vincenty - précision sub-métrique"""
    if lat1 == lat2 and lon1 == lon2:
        return 0.0
    
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    
    L = lon2_rad - lon1_rad
    U1 = math.atan((1 - WGS84_F) * math.tan(lat1_rad))
    U2 = math.atan((1 - WGS84_F) * math.tan(lat2_rad))
    
    sin_U1, cos_U1 = math.sin(U1), math.cos(U1)
    sin_U2, cos_U2 = math.sin(U2), math.cos(U2)
    
    lambda_val = L
    for _ in range(100):
        sin_lambda, cos_lambda = math.sin(lambda_val), math.cos(lambda_val)
        sin_sigma = math.sqrt((cos_U2 * sin_lambda) ** 2 + (cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lambda) ** 2)
        
        if sin_sigma == 0:
            return 0.0
        
        cos_sigma = sin_U1 * sin_U2 + cos_U1 * cos_U2 * cos_lambda
        sigma = math.atan2(sin_sigma, cos_sigma)
        sin_alpha = cos_U1 * cos_U2 * sin_lambda / sin_sigma
        cos2_alpha = 1 - sin_alpha ** 2
        
        if cos2_alpha == 0:
            cos_2sigma_m = 0
        else:
            cos_2sigma_m = cos_sigma - 2 * sin_U1 * sin_U2 / cos2_alpha
        
        C = WGS84_F / 16 * cos2_alpha * (4 + WGS84_F * (4 - 3 * cos2_alpha))
        lambda_prev = lambda_val
        lambda_val = L + (1 - C) * WGS84_F * sin_alpha * (sigma + C * sin_sigma * (cos_2sigma_m + C * cos_sigma * (-1 + 2 * cos_2sigma_m ** 2)))
        
        if abs(lambda_val - lambda_prev) < 1e-12:
            break
    
    alpha1 = math.atan2(cos_U2 * sin_lambda, cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lambda)
    return (math.degrees(alpha1) + 360) % 360