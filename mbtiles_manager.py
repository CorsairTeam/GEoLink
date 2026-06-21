import io
import os
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import utility

class MbtilesManager:    
    
    def add_clicked_point(self, event):
        """Gérer les clics pour la création de lignes"""
        # Convertir les coordonnées pixel en lat/lon
        if not hasattr(self.viewer, 'min_col') or not hasattr(self.viewer, 'max_row'):
            return
            
        lat, lon = utility.pixel_to_latlon(event.x, event.y, 
                                          self.viewer.offset_x, self.viewer.offset_y,
                                          self.viewer.min_col, self.viewer.max_row, 
                                          self.viewer.zoom)
        
        if lat is not None and lon is not None:
           self.viewer.clicked_points.append((lat, lon))
           self.draw_temp_line()

    def remove_last_clicked_point(self):
        """Supprimer le dernier point cliqué"""
        if self.viewer.clicked_points:
            removed = self.viewer.clicked_points.pop()
            self.draw_temp_line()  # Redessiner sans le dernier point
            print(f"Point {len(self.viewer.clicked_points)+1} supprimé: {removed[0]:.6f}, {removed[1]:.6f} - Points restants: {len(self.viewer.clicked_points)}")
        else:
            print("Aucun point à supprimer")

    def draw_temp_line(self):
        """Dessiner la ligne temporaire et les points temporaires sur la carte"""
        self.clear_temp_line()
            
        if len(self.viewer.clicked_points) == 0:
                return
        
        if not hasattr(self.viewer, 'canvas') or not hasattr(self.viewer, 'min_col'):
                return
            
        # Convertir les coordonnées lat/lon en pixels et dessiner les points
        pixel_points = []
        for i, (lat, lon) in enumerate(self.viewer.clicked_points):
            px, py = utility.latlon_to_pixel(lat, lon, self.viewer.offset_x, self.viewer.offset_y, 
                                        self.viewer.min_col, self.viewer.max_row, self.viewer.zoom)
            pixel_points.extend([px, py])
            
            # Dessiner un point temporaire (cercle bleu) pour visualisation
            radius = 5
            self.viewer.canvas.create_oval(px-radius, py-radius, px+radius, py+radius, 
                                fill="blue", outline="darkblue", width=2, tags="temp_line")
            
            # Ajouter un numéro pour indiquer l'ordre des points
            self.viewer.canvas.create_text(px, py-12, text=str(i+1), fill="white", 
                                font=("Arial", 8, "bold"), tags="temp_line")
        
            # Dessiner la ligne temporaire en noir si au moins 2 points
            if len(pixel_points) >= 4:  # Au moins 2 points (4 coordonnées)
                self.viewer.temp_line_id = self.viewer.canvas.create_line(*pixel_points, fill="black", width=2, tags="temp_line")
            
            # Calculer la longueur de la ligne temporaire (en mètres) en sommant les segments
            try:
                total_m = 0.0
                last_seg_nm = None
                last_bearing = None

                for i in range(len(self.viewer.clicked_points) - 1):
                    lat1, lon1 = self.viewer.clicked_points[i]
                    lat2, lon2 = self.viewer.clicked_points[i + 1]
                    # utility.calculate_distance retourne la distance en mètres
                    total_m += utility.calculate_distance(lat1, lon1, lat2, lon2)

                # Convertir en milles nautiques (1 km = 0.539957 Nm)
                distance_nm = (total_m / 1000.0) * 0.539957

                # Calculer le dernier segment et le cap entre les deux derniers points            
                if len(self.viewer.clicked_points) >= 2:
                    lat_a, lon_a = self.viewer.clicked_points[-2]
                    lat_b, lon_b = self.viewer.clicked_points[-1]
                    last_seg_m = utility.calculate_distance(lat_a, lon_a, lat_b, lon_b)
                    last_seg_nm = (last_seg_m / 1000.0) * 0.539957
                    last_bearing = utility.calculate_bearing(lat_a, lon_a, lat_b, lon_b)

                self.viewer.line_length_entry.config(state="normal")
                self.viewer.line_length_entry.delete(0, tk.END)

                #Longueur totale de la ligne en mètres ou en Nm
                if self.viewer.line_length_combo.get() == "m":
                    self.viewer.line_length_entry.insert(0, f"{total_m:.0f}")
                else:
                    self.viewer.line_length_entry.insert(0, f"{distance_nm:.1f}")
                
                self.viewer.line_length_entry.config(state="readonly")

                if last_seg_nm is not None:
                    self.viewer.line_last_segment_length_entry.config(state="normal")
                    self.viewer.line_last_segment_length_entry.delete(0, tk.END)

                     #Longueur du dernier segment de la ligne en mètres ou en Nm
                    if self.viewer.line_last_segment_length_combo.get() == "m":
                        self.viewer.line_last_segment_length_entry.insert(0, f"{last_seg_m:.0f}")
                    else:
                        self.viewer.line_last_segment_length_entry.insert(0, f"{last_seg_nm:.1f}")


                    
                    self.viewer.line_last_segment_length_entry.config(state="readonly")

                self.viewer.line_last_segment_gisement_entry.config(state="normal")
                self.viewer.line_last_segment_gisement_entry.delete(0, tk.END)
                self.viewer.line_last_segment_gisement_entry.insert(0, f"{last_bearing:.0f}°")
                self.viewer.line_last_segment_gisement_entry.config(state="readonly")
                
            except Exception:
                pass
        
        # Si au moins 3 points et création carte dans l'onglet polygone, dessiner la ligne de fermeture en pointillés
        selected_tab = self.viewer.notebook.select()
        tab_text = self.viewer.notebook.tab(selected_tab, "text").strip()
        if len(self.viewer.clicked_points) >= 3 and self.viewer.polygone_creation_mode.get()=="carte" and tab_text == "Polygones":
            first_point = pixel_points[:2]  # Premier point (px, py)
            last_point = pixel_points[-2:]  # Dernier point (px, py)
            # Ligne de fermeture en pointillés
            self.viewer.canvas.create_line(last_point[0], last_point[1], first_point[0], first_point[1], 
                                          fill="darkblue", width=2, dash=(5, 5), tags="temp_line")

            # Mettre à jour les champs de longueur et gisement du dernier segment
            try:
                                
                self.viewer.polygone_last_segment_length_entry.config(state="normal")
                self.viewer.polygone_last_segment_length_entry.delete(0, tk.END)

                #Longueur du dernier segment du polygone en mètres ou en Nm
                if self.viewer.polygone_last_segment_length_combo.get() == "m":
                    self.viewer.polygone_last_segment_length_entry.insert(0, f"{last_seg_m:.0f}")
                else:
                    self.viewer.polygone_last_segment_length_entry.insert(0, f"{last_seg_nm:.1f}")

                self.viewer.polygone_last_segment_length_entry.config(state="readonly")

                self.viewer.polygone_last_segment_gisement_entry.config(state="normal")
                self.viewer.polygone_last_segment_gisement_entry.delete(0, tk.END)
                self.viewer.polygone_last_segment_gisement_entry.insert(0, f"{last_bearing:.0f}°")
                self.viewer.polygone_last_segment_gisement_entry.config(state="readonly")
                
            except Exception:
                pass
                
    def clear_temp_line(self):
        """Effacer la ligne temporaire et les points temporaires de la carte"""
        if hasattr(self.viewer, 'canvas'):
            self.viewer.canvas.delete("temp_line")  # Efface tous les objets avec le tag "temp_line"
            self.viewer.temp_line_id = None
    
    def calculate_line_total_distance(self, line_name):
        """Calculer la distance totale d'une ligne en utilisant les coordonnées de ses points"""
        try:
            # Récupérer les coordonnées de la ligne depuis ligne.db
            conn = sqlite3.connect("ligne.db")
            cursor = conn.cursor()
            cursor.execute("SELECT points_list FROM lines WHERE name = ?", (line_name,))
            result = cursor.fetchone()
            conn.close()
            
            if not result or not result[0]:
                return 0.0
            
            # Récupérer les points de la ligne (format: "lon,lat,0 lon,lat,0 ...")
            points_str = result[0]
            coordinates_list = points_str.split()
            
            if len(coordinates_list) < 2:
                return 0.0
            
            # Convertir les coordonnées en liste de points (lat, lon)
            points = []
            for coord_str in coordinates_list:
                parts = coord_str.split(',')
                if len(parts) >= 2:
                    lon = float(parts[0])
                    lat = float(parts[1])
                    points.append((lat, lon))
            
            # Calculer la distance totale en additionnant les segments
            total_distance = 0.0
            for i in range(len(points) - 1):
                lat1, lon1 = points[i]
                lat2, lon2 = points[i + 1]
                # Utiliser la fonction calculate_distance de Utility.py (retourne en mètres)
                distance = Utility.calculate_distance(lat1, lon1, lat2, lon2)
                total_distance += distance
            
            # Retourner la distance en kilomètres
            return total_distance / 1000.0
            
        except Exception as e:
            print(f"Erreur lors du calcul de la distance de la ligne '{line_name}': {e}")
            return 0.0


    def draw_lines(self):
        """Dessiner toutes les lignes sur la carte (points_list = noms de points)"""
        viewer = self.viewer
        if not hasattr(viewer, 'min_col') or not hasattr(viewer, 'max_row'):
            return
        viewer.canvas.delete("line")
        # Charger tous les points dans un dict {nom: (lat, lon)}
        conn_points = sqlite3.connect("points.db")
        cursor_points = conn_points.cursor()
        cursor_points.execute("SELECT name, lat, lon FROM points")
        points_data = {name: (lat, lon) for name, lat, lon in cursor_points.fetchall()}
        conn_points.close()

        # Charger les lignes
        conn_lines = sqlite3.connect("lignes.db")
        cursor_lines = conn_lines.cursor()
        cursor_lines.execute("SELECT name, color, width, points_list FROM lines")
        lines = cursor_lines.fetchall()
        conn_lines.close()

        color_map = {
            "rouge": "red",
            "vert": "green",
            "bleu": "blue",
            "jaune": "yellow",
            "orange": "orange",
            "cyan": "cyan",
            "magenta": "magenta",
            "noir": "black",
            "blanc": "white"
        }
        for name, color, width, points_list in lines:
            try:
                # Dans la base, les lignes sont enregistrées avec des coordonnées:
                # "lon,lat,0 lon2,lat2,0 ..." (séparées par des espaces)
                pixel_points = []
                if points_list:
                    coord_tokens = [tok.strip() for tok in points_list.split() if tok.strip()]
                    for tok in coord_tokens:
                        parts = tok.split(',')
                        if len(parts) >= 2:
                            try:
                                lon = float(parts[0])
                                lat = float(parts[1])
                            except ValueError:
                                continue
                            px = utility.latlon_to_pixel(lat, lon, viewer.offset_x, viewer.offset_y, viewer.min_col, viewer.max_row, viewer.zoom)
                            pixel_points.append(px)

                if len(pixel_points) >= 2:
                    tk_color = color_map.get(str(color).strip().lower(), "red")
                    viewer.canvas.create_line(*[coord for point in pixel_points for coord in point], fill=tk_color, width=int(width), tags="line")
            except Exception as e:
                print(f"Erreur ligne '{name}': points_list={points_list} | Exception: {e}")
                continue
    
    def draw_polygones(self):
        """Dessiner tous les polygones sur la carte"""
        viewer = self.viewer
        if not hasattr(viewer, 'min_col') or not hasattr(viewer, 'max_row'):
            return
        viewer.canvas.delete("polygone")

        # Charger les polygones
        try:
            conn_poly = sqlite3.connect("polygones.db")
            cursor_poly = conn_poly.cursor()
            cursor_poly.execute("SELECT name, color, width, fill, fill_color, points_list FROM polygons")
            polygones = cursor_poly.fetchall()
            conn_poly.close()
        except Exception as e:
            print(f"Erreur chargement polygones: {e}")
            return

        color_map = {
            "rouge": "red",
            "vert": "green",
            "bleu": "blue",
            "jaune": "yellow",
            "orange": "orange",
            "cyan": "cyan",
            "magenta": "magenta",
            "noir": "black",
            "blanc": "white"
        }
        for name, color, width, fill, fill_color, points_list in polygones:
            try:
                # Dans la base, les polygones sont maintenant enregistrés avec des coordonnées:
                # "lon,lat,0 lon2,lat2,0 ..." (séparées par des espaces)
                pixel_points = []
                if points_list:
                    coord_tokens = [tok.strip() for tok in points_list.split() if tok.strip()]
                    for tok in coord_tokens:
                        parts = tok.split(',')
                        if len(parts) >= 2:
                            try:
                                lon = float(parts[0])
                                lat = float(parts[1])
                            except ValueError:
                                continue
                            px = utility.latlon_to_pixel(lat, lon, viewer.offset_x, viewer.offset_y, viewer.min_col, viewer.max_row, viewer.zoom)
                            pixel_points.append(px)

                if len(pixel_points) >= 3:
                    tk_color = color_map.get(str(color).strip().lower(), "red")
                    outline_color = tk_color
                    fill_color_name = color_map.get(str(fill_color).strip().lower(), str(fill_color).strip().lower()) if int(fill) else ""
                    # Transparence 50% avec Pillow
                    if int(fill) and fill_color_name:
                        # Déterminer la bounding box du polygone
                        xs = [pt[0] for pt in pixel_points]
                        ys = [pt[1] for pt in pixel_points]
                        min_x, max_x = int(min(xs)), int(max(xs))
                        min_y, max_y = int(min(ys)), int(max(ys))
                        w, h = max_x - min_x + 1, max_y - min_y + 1
                        if w < 1 or h < 1:
                            continue
                        
                        # Créer une image RGBA transparente
                        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                        from PIL import ImageDraw
                        draw = ImageDraw.Draw(img)
                        
                        # Couleur de remplissage avec alpha 128
                        try:
                            rgb = viewer.canvas.winfo_rgb(fill_color_name)
                        except Exception:
                            rgb = viewer.canvas.winfo_rgb(outline_color)
                        r = int(rgb[0] / 256)
                        g = int(rgb[1] / 256)
                        b = int(rgb[2] / 256)
                        fill_rgba = (r, g, b, 128)
                        
                        # Décaler les points pour l'image locale
                        local_points = [(x - min_x, y - min_y) for x, y in pixel_points]
                        draw.polygon(local_points, fill=fill_rgba)
                        
                        # Convertir en PhotoImage et afficher
                        photo = ImageTk.PhotoImage(img)
                        viewer.canvas.create_image(min_x, min_y, image=photo, anchor=tk.NW, tags="polygone")
                        if not hasattr(viewer.canvas, "_poly_images"):
                            viewer.canvas._poly_images = []
                        viewer.canvas._poly_images.append(photo)
                    # Dessiner la bordure opaque
                    viewer.canvas.create_polygon(*[coord for point in pixel_points for coord in point], fill="", outline=outline_color, width=int(width), tags="polygone")
            except Exception as e:
                print(f"Erreur polygone '{name}': points_list={points_list} | Exception: {e}")
                continue

    def draw_points(self):
        """Dessiner tous les points sur la carte"""
        viewer = self.viewer
        if not hasattr(viewer, 'min_col') or not hasattr(viewer, 'max_row'):
            return
        
        # Effacer les points existants
        viewer.canvas.delete("point")
        
        # Récupérer tous les points de la base de données
        conn = sqlite3.connect("points.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, lat, lon FROM points")
        points = cursor.fetchall()
        conn.close()
        
        # Dessiner chaque point
        for nom, lat, lon in points:
            x, y = utility.latlon_to_pixel(lat, lon, viewer.offset_x, viewer.offset_y, viewer.min_col, viewer.max_row, viewer.zoom)
            # Vérifier si le point est visible dans le canvas
            canvas_width = viewer.canvas.winfo_width()
            canvas_height = viewer.canvas.winfo_height()
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 800, 600
            if 0 <= x <= canvas_width and 0 <= y <= canvas_height:
                # Dessiner le point (cercle rouge)
                radius = 4
                viewer.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                                      fill="red", outline="darkred", width=2, tags="point")
                # Ajouter le nom du point
                viewer.canvas.create_text(x, y-10, text=nom, fill="black", 
                                      font=("Arial", 8, "bold"), tags="point")
    

    def right_click_get_coordinate(self, event):
        """Gérer le clic droit sur la carte pour renvoyer les coordonneés si mode Click droit"""
        if self.viewer.creation_mode.get() != "click":
            return
        
        # Convertir coordonnées pixel en lat/lon
        lat, lon = utility.pixel_to_latlon(
            event.x, event.y, 
            self.viewer.offset_x, self.viewer.offset_y,
            self.viewer.min_col, self.viewer.max_row, self.viewer.zoom
        )
        
        # Mettre à jour les champs dans l'interface
        if hasattr(self.viewer, 'click_lat_entry') and hasattr(self.viewer, 'click_lon_entry'):
            self.viewer.click_lat_entry.config(state="normal")
            self.viewer.click_lat_entry.delete(0, tk.END)
            self.viewer.click_lat_entry.insert(0, f"{lat:.6f}")
            self.viewer.click_lat_entry.config(state="readonly")
            
            self.viewer.click_lon_entry.config(state="normal")
            self.viewer.click_lon_entry.delete(0, tk.END)
            self.viewer.click_lon_entry.insert(0, f"{lon:.6f}")
            self.viewer.click_lon_entry.config(state="readonly")

    def start_drag(self, event):        
        self.viewer.drag_start_x = event.x
        self.viewer.drag_start_y = event.y
    
    def right_click(self, event):
        """Gérer le clic droit selon l'onglet actif"""
        try:
            # Déterminer quel onglet est actif
            selected_tab = self.viewer.notebook.select()
            tab_text = self.viewer.notebook.tab(selected_tab, "text")
            
            if tab_text == "  Points  ":                
                self.right_click_get_coordinate(event)
                
        #     elif tab_text == "  Lignes  " and self.is_line_creation_mode():
        #         # Mode création de ligne par carte - ne rien faire ici
        #         # (géré par shift_right_click)
        #         pass
                
        #     # Ajouter d'autres onglets si nécessaire
        #     # elif tab_text == "  Polygones  ":
        #     #     # Futur: gestion polygones par clic droit
        #     #     pass
                
        except Exception as e:
            print(f"Erreur dans right_click: {e}")
    
    def shift_left_click(self, event):
        """Gérer Shift + clic gauche pour ajouter des points de ligne ou polygone"""
        
        # Vérifier si on est en mode création de ligne par clic
        if self.viewer.ligne_creation_mode.get() == "carte":
            self.add_clicked_point(event)
        
        # Vérifier si on est en mode création de polygone par clic
        elif self.viewer.polygone_creation_mode.get() == "carte":
            self.add_clicked_point(event)
        
    def shift_right_click(self, event):
        """Gérer Shift + clic droit pour supprimer des points de ligne ou polygone"""
        
        # Vérifier si on est en mode création de ligne par clic
        if self.viewer.ligne_creation_mode.get() == "carte":
            self.remove_last_clicked_point()
        
        # Vérifier si on est en mode création de polygone par clic
        elif self.viewer.polygone_creation_mode.get() == "carte":
            self.remove_last_clicked_point()
                
   
    def drag(self, event):        

        # Ne pas initier de drag si Shift était pressé (éviter conflit avec création ligne)
        if event.state & 0x1:  # 0x1 = Shift pressé
            return

        if hasattr(self.viewer, 'drag_start_x') and hasattr(self.viewer, 'drag_start_y'):
            dx = event.x - self.viewer.drag_start_x
            dy = event.y - self.viewer.drag_start_y
            
            self.viewer.offset_x += dx
            self.viewer.offset_y += dy
            
            self.viewer.drag_start_x = event.x
            self.viewer.drag_start_y = event.y
            
            self.draw_map()
    
    def zoom_map(self, event):
        if not self.viewer.db_path:
            return
        
        mouse_x = event.x
        mouse_y = event.y
        
        conn = sqlite3.connect(self.viewer.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT zoom_level FROM tiles ORDER BY zoom_level")
        available_zooms = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not available_zooms:
            return
            
        current_idx = available_zooms.index(self.viewer.zoom) if self.viewer.zoom in available_zooms else 0
        old_zoom_level = available_zooms[current_idx]
        
        if event.delta > 0 and current_idx < len(available_zooms) - 1:
            new_zoom_level = available_zooms[current_idx + 1]
        elif event.delta < 0 and current_idx > 0:
            new_zoom_level = available_zooms[current_idx - 1]
        else:
            return
        
        zoom_factor = 2 ** (new_zoom_level - old_zoom_level)
        
        old_min_col = self.viewer.min_col
        old_max_row = self.viewer.max_row
        
        abs_x = (mouse_x - self.viewer.offset_x) / 256 + old_min_col
        abs_y = old_max_row - (mouse_y - self.viewer.offset_y) / 256
        
        self.viewer.zoom = new_zoom_level
        
        conn = sqlite3.connect(self.viewer.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(tile_column), MAX(tile_column), MIN(tile_row), MAX(tile_row) FROM tiles WHERE zoom_level=?", (self.viewer.zoom,))
        new_bounds = cursor.fetchone()
        conn.close()
        
        if new_bounds and new_bounds[0] is not None:
            new_min_col, new_max_col, new_min_row, new_max_row = new_bounds
            
            new_abs_x = abs_x * zoom_factor
            new_abs_y = abs_y * zoom_factor
            
            new_image_x = (new_abs_x - new_min_col) * 256
            new_image_y = (new_max_row - new_abs_y) * 256
            
            self.viewer.offset_x = mouse_x - new_image_x
            self.viewer.offset_y = mouse_y - new_image_y
        
        self.viewer.tile_cache.clear()
        self.draw_map()

    def mouse_motion(self, event):
        # if not self.viewer.db_path or not hasattr(self.viewer, 'min_col') or not hasattr(self.viewer, 'max_row'):
        #     return
        
        #lat, lon = utility.update_coordinates(event.x, event.y, self.viewer.offset_x, self.viewer.offset_y, self.viewer.min_col, self.viewer.max_row, self.viewer.zoom)
                
        # if lat is not None and lon is not None:
        #     O_Infos.update_info_panel(self.viewer)
        #     coord_text = f"{lat:.4f}°{lon:.4f}°   "
        #     offset=f"({self.viewer.offset_x}, {self.viewer.offset_y})"
        #     tiles_count = len([item for item in self.viewer.canvas.find_all() if self.viewer.canvas.type(item) == 'image'])
        #     self.viewer.status_bar.config(text=f"Zoom: {self.viewer.zoom} | Tuiles: {tiles_count} | {coord_text} | Offset: {offset}")
        pass

    def bind_canvas_events(self):
        """Détecte les événements sur la carte"""
        self.viewer.canvas.bind("<Button-1>", self.start_drag)
        self.viewer.canvas.bind("<Button-3>", self.right_click)  
        self.viewer.canvas.bind("<Shift-Button-1>", self.shift_left_click)  
        self.viewer.canvas.bind("<Shift-Button-3>", self.shift_right_click)  
        self.viewer.canvas.bind("<B1-Motion>", self.drag)
        self.viewer.canvas.bind("<MouseWheel>", self.zoom_map)
        self.viewer.canvas.bind("<Motion>", self.mouse_motion)
        self.viewer.canvas.bind("<Shift-Button-1>", self.shift_left_click)  
        self.viewer.canvas.bind("<Shift-Button-3>", self.shift_right_click)

     
            
    def import_carte(self, map_path):
        """Importer une carte (fichier MBTiles)"""

        if not map_path or not os.path.exists(map_path):
            map_path = filedialog.askopenfilename(
                parent=self.viewer.root,
                title="Choisir une carte MBTiles",
                filetypes=[("MBTiles", "*.mbtiles"), ("Tous les fichiers", "*.*")]
            )

        if not map_path:
            return

        center_latlon = None
        if self.viewer.db_path and hasattr(self.viewer, 'min_col') and hasattr(self.viewer, 'max_row'):
            canvas_width = self.viewer.canvas.winfo_width()
            canvas_height = self.viewer.canvas.winfo_height()

            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 800, 600

            center_latlon = utility.pixel_to_latlon(
                canvas_width // 2, canvas_height // 2,
                self.viewer.offset_x, self.viewer.offset_y,
                self.viewer.min_col, self.viewer.max_row,
                self.viewer.zoom
            )

        self.viewer.db_path = map_path
        self.viewer.offset_x = 0
        self.viewer.offset_y = 0
        self.viewer.tile_cache = {}

        if center_latlon:
            self.viewer.root.after_idle(lambda: (self.draw_map(), self.center_map_on_point(*center_latlon)))
        else:
            self.viewer.root.after_idle(lambda: (self.centrage_carte(), self.draw_map()))
    
    def centrage_carte(self):
        """Centrer la carte dans the canvas"""
        #Au chargement de la carte l'ofset est (0,0) et coorespond au coin supérieur gauche de la carte chargée
        # Donc on doit ajuster l'offset pour centrer la carte au départ
        if self.viewer.offset_x == 0 and self.viewer.offset_y == 0:
            #Connection à la base de données MBTiles
            conn = sqlite3.connect(self.viewer.db_path)
            cursor = conn.cursor()
                    
            # Récupère les bornes des tuiles disponibles pour le niveau de zoom actuel (11 par défaut)
            cursor.execute("SELECT MIN(tile_column), MAX(tile_column), MIN(tile_row), MAX(tile_row) FROM tiles WHERE zoom_level=?", (self.viewer.zoom,))
            bounds = cursor.fetchone()
                    
            if bounds and bounds[0] is not None:
                min_col, max_col, min_row, max_row = bounds
                        
                # Calculer la largeur et hauteur totale de la carte en pixels
                map_width = (max_col - min_col + 1) * 256
                map_height = (max_row - min_row + 1) * 256

                try:
                    # Determine la taille de l'espace d'affichage
                    canvas_width = self.viewer.canvas.winfo_width()
                    canvas_height = self.viewer.canvas.winfo_height()
                
                    if canvas_width <= 1 or canvas_height <= 1:
                        canvas_width, canvas_height = 800, 600    

                    # Centrer la carte dans le canvas
                    self.viewer.offset_x = (canvas_width - map_width) // 2
                    self.viewer.offset_y = (canvas_height - map_height) // 2
                
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur: {e}")
            
            conn.close() 

    def draw_map(self):
        # Dessine la carte avec les Objets lignes,polygones et points
        if not self.viewer.db_path:
            return
            
        self.viewer.canvas.delete("all")
        
        try:
            # Determine la taille de l'espace d'affichage
            canvas_width = self.viewer.canvas.winfo_width()
            canvas_height = self.viewer.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 800, 600      
            

            # Définit la taille de l'image a creer en fonction de la taille du canvas + un buffer
            visible_left = -self.viewer.offset_x - 256
            visible_right = -self.viewer.offset_x + canvas_width + 256
            visible_top = -self.viewer.offset_y - 256
            visible_bottom = -self.viewer.offset_y + canvas_height + 256
            
            #Connection à la base de données MBTiles
            conn = sqlite3.connect(self.viewer.db_path)
            cursor = conn.cursor()
            
            # Récupère les bornes des tuiles disponibles pour le niveau de zoom actuel (11 par défaut)
            cursor.execute("SELECT MIN(tile_column), MAX(tile_column), MIN(tile_row), MAX(tile_row) FROM tiles WHERE zoom_level=?", (self.viewer.zoom,))
            bounds = cursor.fetchone()
            
            if not bounds or bounds[0] is None:
                conn.close()
                return
            
            # Récupère les numéros des tuiles disponibles pour le niveau de zoom actuel (11 par défaut)
            min_col, max_col, min_row, max_row = bounds
            self.viewer.min_col = min_col
            self.viewer.max_row = max_row
            self.viewer.min_row = min_row
            self.viewer.max_col = max_col
            
            # Les tuiles sont de 256x256 pixels dans le mbtiles
            # La tuile (0,0) se trouve au coin inférieur-gauche de la projection Mercator
            # Cela correspond approximativement à :
            # Longitude : -180° (côte ouest de l'Alaska/Sibérie)
            # Latitude : -85.05° (Antarctique)
            # Le résultat donne les indices [start_col, end_col] et [start_row, end_row] des tuiles pour couvrir exactement la zone visible de la carte.
            
            start_col = max(min_col, int(visible_left // 256) + min_col)
            end_col = min(max_col, int(visible_right // 256) + min_col + 1)
            start_row = max(min_row, max_row - int(visible_bottom // 256))
            end_row = min(max_row, max_row - int(visible_top // 256) + 1)
            
            # Référentiel d'affichage
            # (0,0) = coin supérieur-gauche du canvas
            # X positif = vers la droite
            # Y positif = vers le bas

            self.viewer.canvas.image = []
            tiles_loaded = 0
            
            for col in range(start_col, end_col + 1):
                for row in range(start_row, end_row + 1):
                    cache_key = (self.viewer.zoom, col, row)
                    if cache_key in self.viewer.tile_cache:
                        photo = self.viewer.tile_cache[cache_key]
                    else:
                        cursor.execute("SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?", (self.viewer.zoom, col, row))
                        result = cursor.fetchone()
                        
                        if not result:
                            continue

                        # result[0] données binaires d'une tuile d'image 
                        # io.BytesIO() crée un objet fichier en mémoire à partir de ces données binaires
                        # Image.open() (de la bibliothèque PIL/Pillow) ouvre l'image à partir de ce flux de données
                        # ImageTk.PhotoImage(image) Convertit l'objet PIL Image en PhotoImage de Tkinter
                       
                        try:
                            image = Image.open(io.BytesIO(result[0]))
                            photo = ImageTk.PhotoImage(image)
                            if len(self.viewer.tile_cache) < 100:
                                self.viewer.tile_cache[cache_key] = photo
                        except:
                            continue
                    
                    x = (col - min_col) * 256 + self.viewer.offset_x
                    y = (max_row - row) * 256 + self.viewer.offset_y
                    
                    self.viewer.canvas.create_rectangle(x, y, x+256, y+256, outline="black", width=1, fill="")
                    self.viewer.canvas.create_image(x, y, image=photo, anchor=tk.NW)
                    self.viewer.canvas.image.append(photo)                    
                    tiles_loaded += 1
            
            conn.close()
            
            #Trace les points, lignes et polygones sur la carte et lignes temporaires
            self.draw_points()
            self.draw_lines()
            self.draw_polygones()
            self.draw_temp_line()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")

    def center_map_on_point(self, lat, lon):
        """Centrer la carte sur un point donné en latitude/longitude"""
        viewer = self.viewer
        
        if not viewer.db_path or not hasattr(viewer, 'min_col') or not hasattr(viewer, 'max_row'):
            return
        
        # Obtenir les dimensions du canvas
        canvas_width = viewer.canvas.winfo_width()
        canvas_height = viewer.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 800, 600
        
        # Convertir lat/lon en coordonnées pixel pour le niveau de zoom actuel
        target_x, target_y = utility.latlon_to_pixel(
            lat, lon, 
            viewer.offset_x, viewer.offset_y, 
            viewer.min_col, viewer.max_row, viewer.zoom
        )
        
        # Calculer le décalage nécessaire pour centrer le point
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Ajuster les offsets pour que le point soit au centre
        viewer.offset_x += center_x - target_x
        viewer.offset_y += center_y - target_y
        
        # Redessiner la carte
        self.draw_map()



    def on_point_tree_double_click(self, event):
        """Gérer le double-clic sur le treeview pour centrer la carte"""
        # Identifier l'élément double-cliqué
        item = self.viewer.tree.identify_row(event.y)
        
        if item and item in self.viewer.points_checked_items:
            # Récupérer les données du point
            point_data = self.viewer.points_checked_items[item]["data"]
            name, lat, lon = point_data[0], point_data[1], point_data[2]
            
            # Vérifier qu'on a une carte chargée avant de centrer
            if self.viewer.db_path:
                # Centrer la carte sur ce point
                self.center_map_on_point(lat, lon)
                
                # Optionnel : afficher un message pour confirmer l'action
                print(f"Carte centrée sur le point '{name}' ({lat:.6f}, {lon:.6f})")
            else:
                print("Aucune carte chargée - impossible de centrer")

    def on_polygones_tree_double_click(self, event):
        """Gérer le double-clic sur le treeview pour centrer la carte sur le premier point du polygone"""
        # Identifier l'élément double-cliqué
        item = self.viewer.polygones_tree.identify_row(event.y)
        
        if item and item in self.viewer.polygones_checked_items:
            # Récupérer le nom du polygone
            polygone_name = self.viewer.polygones_tree.item(item)["values"][1]
            
            try:
                # Récupérer les coordonnées du polygone depuis polygones.db
                conn = sqlite3.connect("polygones.db")
                cursor = conn.cursor()
                cursor.execute("SELECT points_list FROM polygons WHERE name = ?", (polygone_name,))
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0]:
                    # Récupérer le premier point du polygone
                    points_str = result[0]
                    coordinates_list = points_str.split()
                    
                    if coordinates_list:
                        # Prendre le premier point (format: "lon,lat,0")
                        first_point = coordinates_list[0].split(',')
                        if len(first_point) >= 2:
                            lon = float(first_point[0])
                            lat = float(first_point[1])
                            
                            # Vérifier qu'on a une carte chargée avant de centrer
                            if self.viewer.db_path:
                                # Centrer la carte sur ce point
                                self.center_map_on_point(lat, lon)
                                
                                # Optionnel : afficher un message pour confirmer l'action
                                print(f"Carte centrée sur le premier point du polygone '{polygone_name}' ({lat:.6f}, {lon:.6f})")
                            else:
                                print("Aucune carte chargée - impossible de centrer")
                        else:
                            print(f"Format de coordonnées invalide pour le polygone '{polygone_name}'")
                    else:
                        print(f"Aucun point trouvé dans le polygone '{polygone_name}'")
                else:
                    print(f"Polygone '{polygone_name}' non trouvé ou sans points")
                    
            except Exception as e:
                print(f"Erreur lors de la récupération des coordonnées du polygone: {e}")

    def on_lines_tree_double_click(self, event):
        """Gérer le double-clic sur le treeview pour centrer la carte sur le premier point de la ligne"""
        # Identifier l'élément double-cliqué
        item = self.viewer.lines_tree.identify_row(event.y)
        
        if item and item in self.viewer.lines_checked_items:
            # Récupérer le nom de la ligne
            line_name = self.viewer.lines_tree.item(item)["values"][1]
            
            try:
                # Récupérer les coordonnées de la ligne depuis ligne.db
                conn = sqlite3.connect("lignes.db")
                cursor = conn.cursor()
                cursor.execute("SELECT points_list FROM lines WHERE name = ?", (line_name,))
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0]:
                    # Récupérer le premier point de la ligne
                    points_str = result[0]
                    coordinates_list = points_str.split()
                    
                    if coordinates_list:
                        # Prendre le premier point (format: "lon,lat,0")
                        first_point = coordinates_list[0].split(',')
                        if len(first_point) >= 2:
                            lon = float(first_point[0])
                            lat = float(first_point[1])
                            
                            # Vérifier qu'on a une carte chargée avant de centrer
                            if self.viewer.db_path:
                                # Centrer la carte sur ce point
                                self.center_map_on_point(lat, lon)
                                
                                # Optionnel : afficher un message pour confirmer l'action
                                print(f"Carte centrée sur le premier point de la ligne '{line_name}' ({lat:.6f}, {lon:.6f})")
                            else:
                                print("Aucune carte chargée - impossible de centrer")
                        else:
                            print(f"Format de coordonnées invalide pour la ligne '{line_name}'")
                    else:
                        print(f"Aucun point trouvé dans la ligne '{line_name}'")
                else:
                    print(f"Ligne '{line_name}' non trouvée ou sans points")
                    
            except Exception as e:
                print(f"Erreur lors de la récupération des coordonnées de la ligne: {e}")



    def __init__(self, viewer):
        #self.viewer pointe vers l'instance de la classe mbtiles_viewer pour y accéder
        self.viewer = viewer


   

