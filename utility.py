import tkinter as tk
import math

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
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """Afficher l'info-bulle"""
        if self.tooltip_window or not self.text:
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

def on_tree_click(viewer, event, checked_items, treeview):
    """En fonctiondu clic, coche la case ou remplit les champs de Input_frame"""
    region = treeview.identify_region(event.x, event.y)
    if region == "cell":
        item = treeview.identify_row(event.y)
        column = treeview.identify_column(event.x)
        
        if column == "#1" and item in checked_items:
            toggle_checkbox(item, checked_items, treeview)

        if column == "#2" and item in checked_items and checked_items is viewer.points_checked_items:
            point_field_fill(viewer, item)

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

def create_point_from_bearing_distance(start_point, distance_km, bearing_deg):
    """Créer un point à partir d'un point de départ, distance et gisement (formule Vincenty)"""
    # Constantes WGS84
    WGS84_A = 6378137.0
    WGS84_F = 1/298.257223563
    WGS84_B = WGS84_A * (1 - WGS84_F)
    
    lat1_rad = math.radians(start_point["lat"])
    lon1_rad = math.radians(start_point["lon"])
    alpha1_rad = math.radians(bearing_deg)
    s = distance_km * 1000  # Convertir en mètres
    
    sin_alpha1, cos_alpha1 = math.sin(alpha1_rad), math.cos(alpha1_rad)
    tan_U1 = (1 - WGS84_F) * math.tan(lat1_rad)
    cos_U1 = 1 / math.sqrt(1 + tan_U1 ** 2)
    sin_U1 = tan_U1 * cos_U1
    
    sigma1 = math.atan2(tan_U1, cos_alpha1)
    sin_alpha = cos_U1 * sin_alpha1
    cos2_alpha = 1 - sin_alpha ** 2
    u2 = cos2_alpha * (WGS84_A ** 2 - WGS84_B ** 2) / (WGS84_B ** 2)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    
    sigma = s / (WGS84_B * A)
    for _ in range(100):
        cos_2sigma_m = math.cos(2 * sigma1 + sigma)
        sin_sigma, cos_sigma = math.sin(sigma), math.cos(sigma)
        delta_sigma = B * sin_sigma * (cos_2sigma_m + B / 4 * (cos_sigma * (-1 + 2 * cos_2sigma_m ** 2) - B / 6 * cos_2sigma_m * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos_2sigma_m ** 2)))
        sigma_prev = sigma
        sigma = s / (WGS84_B * A) + delta_sigma
        
        if abs(sigma - sigma_prev) < 1e-12:
            break
    
    tmp = sin_U1 * sin_sigma - cos_U1 * cos_sigma * cos_alpha1
    lat2_rad = math.atan2(sin_U1 * cos_sigma + cos_U1 * sin_sigma * cos_alpha1, (1 - WGS84_F) * math.sqrt(sin_alpha ** 2 + tmp ** 2))
    lambda_val = math.atan2(sin_sigma * sin_alpha1, cos_U1 * cos_sigma - sin_U1 * sin_sigma * cos_alpha1)
    C = WGS84_F / 16 * cos2_alpha * (4 + WGS84_F * (4 - 3 * cos2_alpha))
    L = lambda_val - (1 - C) * WGS84_F * sin_alpha * (sigma + C * sin_sigma * (cos_2sigma_m + C * cos_sigma * (-1 + 2 * cos_2sigma_m ** 2)))
    lon2_rad = (lon1_rad + L + 3 * math.pi) % (2 * math.pi) - math.pi
    
    return math.degrees(lat2_rad), math.degrees(lon2_rad)