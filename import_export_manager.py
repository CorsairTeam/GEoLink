import simplekml
import sqlite3
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox
import tkinter as tk
import os
import database
import pandas as pd
import csv


YLW_PUSHPIN_ICON = "http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png"
TARGET_ICON = "http://maps.google.com/mapfiles/kml/shapes/target.png"
FORBIDDEN_ICON = "http://maps.google.com/mapfiles/kml/shapes/forbidden.png"
PLACEMARK_CIRCLE_ICON = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
TRIANGLE_ICON = "http://maps.google.com/mapfiles/kml/shapes/triangle.png"
OPEN_DIAMOND_ICON = "http://maps.google.com/mapfiles/kml/shapes/open-diamond.png"
SQUARE_ICON = "http://maps.google.com/mapfiles/kml/shapes/square.png"

POINT_ICON_MAP = {
   
    "Punaise": YLW_PUSHPIN_ICON,    
    "Cible": TARGET_ICON,
    "Panneau": FORBIDDEN_ICON,
    "Carré": SQUARE_ICON,    
    "Cercle": PLACEMARK_CIRCLE_ICON,    
    "Triangle": TRIANGLE_ICON,
    "Diamant": OPEN_DIAMOND_ICON,
}

POINT_ICON_HREF_MAP = {href: label for label, href in POINT_ICON_MAP.items()}

def create_kml_SDVFR_from_databases(
    kml_filename,
    points_db,
    lines_db,
    polygons_db,
    selected_points=None,
    selected_lines=None,
    selected_polygons=None,):
    """
    Génère un fichier KML depuis 3 bases de données SQLite
    
    Args:
        kml_filename: nom du fichier KML à créer
        points_db: chemin vers point.db (name, lat, lon)
        lines_db: chemin vers ligne.db (name, color, width, points_list)
        polygons_db: chemin vers polygone.db (name, color, width, fill, points_list)
        selected_points: liste optionnelle de noms de points a exporter
        selected_lines: liste optionnelle de noms de lignes a exporter
        selected_polygons: liste optionnelle de noms de polygones a exporter
    """
    kml = simplekml.Kml()
    
    # Mapping des couleurs
    color_map = {
        "rouge": simplekml.Color.red,
        "vert": simplekml.Color.green,
        "bleu": simplekml.Color.blue,
        "jaune": simplekml.Color.yellow,
        "orange": simplekml.Color.orange,
        "cyan": simplekml.Color.cyan,
        "magenta": simplekml.Color.magenta,
        "noir": simplekml.Color.black,
        "blanc": simplekml.Color.white
    }
    
    # Charger les points
    try:
        if selected_points is None or selected_points:
            conn = sqlite3.connect(points_db)
            cursor = conn.cursor()
            if selected_points is not None:
                placeholders = ",".join(["?"] * len(selected_points))
                try:
                    cursor.execute(
                        f"SELECT name, lat, lon, scale, icon FROM points WHERE name IN ({placeholders})",
                        tuple(selected_points),
                    )
                except sqlite3.OperationalError:
                    cursor.execute(
                        f"SELECT name, lat, lon FROM points WHERE name IN ({placeholders})",
                        tuple(selected_points),
                    )
            else:
                try:
                    cursor.execute("SELECT name, lat, lon, scale, icon FROM points")
                except sqlite3.OperationalError:
                    cursor.execute("SELECT name, lat, lon FROM points")

            points_folder = None
            for row in cursor.fetchall():
                if len(row) == 5:
                    name, lat, lon, scale, icon = row
                else:
                    name, lat, lon = row
                    scale, icon = 1.0, DEFAULT_POINT_ICON

                if points_folder is None:
                    points_folder = kml.newfolder(name="Points")

                point = points_folder.newpoint(name=name, coords=[(float(lon), float(lat))])
                point.style.iconstyle.icon.href = icon
                point.style.iconstyle.scale = float(scale)
            conn.close()
    except:
        pass
    
    # Charger les lignes
    try:
        if selected_lines is None or selected_lines:
            conn = sqlite3.connect(lines_db)
            cursor = conn.cursor()
            if selected_lines is not None:
                placeholders = ",".join(["?"] * len(selected_lines))
                cursor.execute(
                    f"SELECT name, color, width, points_list FROM lines WHERE name IN ({placeholders})",
                    tuple(selected_lines),
                )
            else:
                cursor.execute("SELECT name, color, width, points_list FROM lines")
            
            lines_folder = None
            for name, color, width, points_list in cursor.fetchall():
                if not lines_folder:
                    lines_folder = kml.newfolder(name="Lignes")
                
                # Parser la liste de coordonnées (format: "lon,lat,alt lon,lat,alt ...")
                coordinate_groups = points_list.split(' ')
                coords = []
                for coord_group in coordinate_groups:
                    coord_group = coord_group.strip()
                    if coord_group:
                        # Split lon,lat,alt
                        coord_parts = coord_group.split(',')
                        if len(coord_parts) >= 2:
                            try:
                                lon = float(coord_parts[0])
                                lat = float(coord_parts[1])
                                coords.append((lon, lat))
                            except ValueError:
                                continue
                
                if len(coords) >= 2:
                    line = lines_folder.newlinestring(name=name, coords=coords)
                    line.style.linestyle.color = color_map.get(color, simplekml.Color.red)
                    line.style.linestyle.width = int(width)
            
            conn.close()
    except:
        pass
    
    # Charger les polygones
    try:
        if selected_polygons is None or selected_polygons:
            conn = sqlite3.connect(polygons_db)
            cursor = conn.cursor()
            if selected_polygons is not None:
                placeholders = ",".join(["?"] * len(selected_polygons))
                cursor.execute(
                    f"SELECT name, color, width, fill, points_list FROM polygons WHERE name IN ({placeholders})",
                    tuple(selected_polygons),
                )
            else:
                cursor.execute("SELECT name, color, width, fill, points_list FROM polygons")
            
            polygons_folder = None
            for name, color, width, fill, points_list in cursor.fetchall():
                if not polygons_folder:
                    polygons_folder = kml.newfolder(name="Polygones")
                
                # Parser la liste de coordonnées (format: "lon,lat,alt lon,lat,alt ...")
                coordinate_groups = points_list.split(' ')
                coords = []
                for coord_group in coordinate_groups:
                    coord_group = coord_group.strip()
                    if coord_group:
                        # Split lon,lat,alt
                        coord_parts = coord_group.split(',')
                        if len(coord_parts) >= 2:
                            try:
                                lon = float(coord_parts[0])
                                lat = float(coord_parts[1])
                                coords.append((lon, lat))
                            except ValueError:
                                continue
                
                if len(coords) >= 3:
                    # Fermer le polygone
                    if coords[0] != coords[-1]:
                        coords.append(coords[0])
                    
                    poly = polygons_folder.newpolygon(name=name, outerboundaryis=coords)
                    poly.style.linestyle.color = color_map.get(color, simplekml.Color.red)
                    poly.style.linestyle.width = int(width)
                    
                    if str(fill).lower() in ['true', '1', 'yes']:
                        base_color = color_map.get(color, simplekml.Color.red)
                        poly.style.polystyle.color = simplekml.Color.changealphaint(150, base_color)
                        poly.style.polystyle.fill = 1
                    else:
                        poly.style.polystyle.fill = 0
            
            conn.close()
    except:
        pass
    
    # Sauvegarder le KML
    kml.save(kml_filename)
    return kml_filename

def create_kml_foreflight_from_databases(
    kml_filename,
    points_db,
    lines_db,
    polygons_db,
    selected_points=None,
    selected_lines=None,
    selected_polygons=None,
    ):
    ns = "http://www.opengis.net/kml/2.2"
    gx_ns = "http://www.google.com/kml/ext/2.2"
    atom_ns = "http://www.w3.org/2005/Atom"
    ET.register_namespace("", ns)
    ET.register_namespace("gx", gx_ns)
    ET.register_namespace("atom", atom_ns)

    def kml_color(color_name, alpha="ff"):
        colors = {
            "rouge": "0000ff",
            "vert": "00ff00",
            "bleu": "ff0000",
            "jaune": "00ffff",
            "orange": "0080ff",
            "cyan": "ffff00",
            "magenta": "ff00ff",
            "noir": "000000",
            "blanc": "ffffff",
        }
        return f"{alpha}{colors.get(str(color_name).strip().lower(), '0000ff')}"

    def coordinates_from_points_list(points_list):
        coords = []
        for coord_group in str(points_list or "").split():
            coord_parts = coord_group.split(',')
            if len(coord_parts) >= 2:
                try:
                    lon = float(coord_parts[0])
                    lat = float(coord_parts[1])
                    alt = float(coord_parts[2]) if len(coord_parts) >= 3 else 0.0
                    coords.append(f"{lon:g},{lat:g},{alt:g}")
                except ValueError:
                    continue
        return coords

    def add_text(parent, tag, text):
        child = ET.SubElement(parent, tag if str(tag).startswith("{") else f"{{{ns}}}{tag}")
        child.text = str(text)
        return child

    def point_icon_href(icon):
        icon_name = str(icon).strip()
        return POINT_ICON_MAP.get(icon_name, TARGET_ICON)

    def selected_query(cursor, query_all, query_selected, selected_values):
        if selected_values is None:
            cursor.execute(query_all)
        elif selected_values:
            placeholders = ",".join(["?"] * len(selected_values))
            cursor.execute(query_selected.format(placeholders=placeholders), tuple(selected_values))
        else:
            return []
        return cursor.fetchall()

    kml_root = ET.Element(f"{{{ns}}}kml", {f"xmlns:kml": ns, f"xmlns:atom": atom_ns})
    document = ET.SubElement(kml_root, f"{{{ns}}}Document")
    add_text(document, "name", "Foreflight.kml")
    add_text(document, "open", "1")

    try:
        conn = sqlite3.connect(points_db)
        cursor = conn.cursor()
        points = selected_query(
            cursor,
            "SELECT name, lat, lon, alt, scale, icon, color, hotspot_x, hotspot_y, label_color FROM points",
            "SELECT name, lat, lon, alt, scale, icon, color, hotspot_x, hotspot_y, label_color FROM points WHERE name IN ({placeholders})",
            selected_points,
        )
        conn.close()

        for name, lat, lon, alt, scale, icon, color, hotspot_x, hotspot_y, label_color in points:
            point_icon = point_icon_href(icon)
            placemark = ET.SubElement(document, f"{{{ns}}}Placemark")
            add_text(placemark, "name", name)
            style = ET.SubElement(placemark, f"{{{ns}}}Style")
            icon_style = ET.SubElement(style, f"{{{ns}}}IconStyle")
            add_text(icon_style, "color", kml_color(color))
            add_text(icon_style, "scale", scale or 1.0)
            icon_elem = ET.SubElement(icon_style, f"{{{ns}}}Icon")
            add_text(icon_elem, "href", point_icon)
            hot_spot = ET.SubElement(icon_style, f"{{{ns}}}hotSpot")
            hot_spot.set("x", str(hotspot_x if hotspot_x is not None else 0.5))
            hot_spot.set("y", str(hotspot_y if hotspot_y is not None else 0.5))
            hot_spot.set("xunits", "pixels")
            hot_spot.set("yunits", "pixels")
            label_style = ET.SubElement(style, f"{{{ns}}}LabelStyle")
            add_text(label_style, "color", kml_color(label_color))
            point = ET.SubElement(placemark, f"{{{ns}}}Point")
            add_text(point, f"{{{gx_ns}}}drawOrder", "1")
            add_text(point, "coordinates", f"{float(lon):g},{float(lat):g},{float(alt or 0):g}")
    except sqlite3.Error:
        pass

    try:
        conn = sqlite3.connect(lines_db)
        cursor = conn.cursor()
        lines = selected_query(
            cursor,
            "SELECT name, color, width, points_list FROM lines",
            "SELECT name, color, width, points_list FROM lines WHERE name IN ({placeholders})",
            selected_lines,
        )
        conn.close()

        for name, color, width, points_list in lines:
            coords = coordinates_from_points_list(points_list)
            if len(coords) >= 2:
                placemark = ET.SubElement(document, f"{{{ns}}}Placemark")
                add_text(placemark, "name", name)
                style = ET.SubElement(placemark, f"{{{ns}}}Style")
                line_style = ET.SubElement(style, f"{{{ns}}}LineStyle")
                add_text(line_style, "color", kml_color(color))
                add_text(line_style, "width", width)
                line_string = ET.SubElement(placemark, f"{{{ns}}}LineString")
                add_text(line_string, "tessellate", "1")
                add_text(line_string, "coordinates", " ".join(coords))
    except sqlite3.Error:
        pass

    try:
        conn = sqlite3.connect(polygons_db)
        cursor = conn.cursor()
        polygons = selected_query(
            cursor,
            "SELECT name, color, width, fill, fill_color, points_list FROM polygons",
            "SELECT name, color, width, fill, fill_color, points_list FROM polygons WHERE name IN ({placeholders})",
            selected_polygons,
        )
        conn.close()

        for name, color, width, fill, fill_color, points_list in polygons:
            coords = coordinates_from_points_list(points_list)
            if len(coords) >= 3:
                if coords[0] != coords[-1]:
                    coords.append(coords[0])
                placemark = ET.SubElement(document, f"{{{ns}}}Placemark")
                add_text(placemark, "name", name)
                style = ET.SubElement(placemark, f"{{{ns}}}Style")
                line_style = ET.SubElement(style, f"{{{ns}}}LineStyle")
                add_text(line_style, "color", kml_color(color))
                add_text(line_style, "width", width)
                poly_style = ET.SubElement(style, f"{{{ns}}}PolyStyle")
                add_text(poly_style, "color", kml_color(fill_color, "96"))
                add_text(poly_style, "fill", "1" if fill in (1, True, "1", "True", "true") else "0")
                add_text(poly_style, "outline", "1")
                polygon = ET.SubElement(placemark, f"{{{ns}}}Polygon")
                add_text(polygon, "tessellate", "1")
                outer_boundary = ET.SubElement(polygon, f"{{{ns}}}outerBoundaryIs")
                linear_ring = ET.SubElement(outer_boundary, f"{{{ns}}}LinearRing")
                add_text(linear_ring, "coordinates", " ".join(coords))
    except sqlite3.Error:
        pass

    tree = ET.ElementTree(kml_root)
    ET.indent(tree, space="  ", level=0)
    tree.write(kml_filename, encoding="utf-8", xml_declaration=True)
    return kml_filename

def export_kml(viewer, export_all=False, foreflight=False):
    # Ouvre une boîte de dialogue pour choisir le nom et l'emplacement du fichier KML
    filename = filedialog.asksaveasfilename(
        title="Enregistrer le fichier KML",
        defaultextension=".kml",
        filetypes=[("KML files", "*.kml"), ("Tous les fichiers", "*.*")],
        initialfile="export_points.kml"
    )
    if not filename:
        return
    try:
        selected_points = None
        selected_lines = None
        selected_polygons = None

        if not export_all:
            if hasattr(viewer, "points_checked_items"):
                selected_points = [
                    info["data"][0]
                    for info in viewer.points_checked_items.values()
                    if info.get("checked")
                ]

            if hasattr(viewer, "lines_checked_items"):
                selected_lines = [
                    info["data"][0]
                    for info in viewer.lines_checked_items.values()
                    if info.get("checked")
                ]

            if hasattr(viewer, "polygones_checked_items"):
                selected_polygons = [
                    info["data"][0]
                    for info in viewer.polygones_checked_items.values()
                    if info.get("checked")
                ]

            if selected_points == [] and selected_lines == [] and selected_polygons == []:
                messagebox.showwarning("Attention", "Aucun objet coche pour l'export")
                return

        if foreflight is True:
            result_file = create_kml_foreflight_from_databases(
                filename,
                "points.db",
                "lignes.db",
                "polygones.db",
                selected_points=selected_points,
                selected_lines=selected_lines,
                selected_polygons=selected_polygons,
            )
            messagebox.showinfo("Succès", f"KML exporté dans {result_file}")
        else:
            result_file = create_kml_SDVFR_from_databases(
                filename,
                "points.db",
                "lignes.db",
                "polygones.db",
                selected_points=selected_points,
                selected_lines=selected_lines,
                selected_polygons=selected_polygons,
            )
            messagebox.showinfo("Succès", f"KML exporté dans {result_file}")

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")

def parse_kml_file(kml_content):
    """Parse un fichier KML et extrait les objets avec leurs styles"""
    try:
        root = ET.fromstring(kml_content)
        
        # Namespaces KML
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        points = []
        lines = []
        polygons = []
        
        def kml_color_to_name(kml_color, default="rouge"):
            if not kml_color:
                return default
            kml_color = kml_color.strip().lower()
            kml_color_map = {
                'ff0000ff': 'rouge',
                'ffff0000': 'bleu',
                'ff00ff00': 'vert',
                'ff008000': 'vert',
                'ffffff00': 'jaune',
                'ffff8000': 'orange',
                'ff00ffff': 'cyan',
                'ffff00ff': 'magenta',
                'ff000000': 'noir',
                'ffffffff': 'blanc',
            }
            if kml_color in kml_color_map:
                return kml_color_map[kml_color]
            try:
                if len(kml_color) == 8:
                    b = int(kml_color[2:4], 16)
                    g = int(kml_color[4:6], 16)
                    r = int(kml_color[6:8], 16)
                    if g > r and g > b and g > 100:
                        return "vert"
                    if r > g and r > b and r > 100:
                        return "rouge"
                    if b > r and b > g and b > 100:
                        return "bleu"
            except ValueError:
                pass
            return default

        def find_style(placemark):
            style_elem = placemark.find('.//kml:Style', ns)
            if style_elem is None:
                style_url_elem = placemark.find('kml:styleUrl', ns)
                if style_url_elem is not None and style_url_elem.text:
                    style_id = style_url_elem.text.replace('#', '')
                    style_elem = root.find(f'.//kml:Style[@id="{style_id}"]', ns)
            return style_elem

        def extract_line_style(placemark):
            color = "rouge"
            width = 2
            style_elem = find_style(placemark)
            if style_elem is not None:
                line_style = style_elem.find('.//kml:LineStyle/kml:color', ns)
                if line_style is not None:
                    color = kml_color_to_name(line_style.text, color)
                width_elem = style_elem.find('.//kml:LineStyle/kml:width', ns)
                if width_elem is not None:
                    try:
                        width = max(1, int(float(width_elem.text.strip())))
                    except:
                        width = 2
            return color, width

        def extract_polygon_style(placemark):
            color, width = extract_line_style(placemark)
            fill = False
            fill_color = color
            style_elem = find_style(placemark)
            if style_elem is not None:
                poly_color = style_elem.find('.//kml:PolyStyle/kml:color', ns)
                if poly_color is not None:
                    fill_color = kml_color_to_name(poly_color.text, fill_color)
                poly_fill = style_elem.find('.//kml:PolyStyle/kml:fill', ns)
                if poly_fill is not None and poly_fill.text:
                    fill = poly_fill.text.strip() == '1'
            return color, width, fill, fill_color

        def extract_point_style(placemark):
            scale = 1.0
            icon = "Punaise"
            color = "rouge"
            hotspot_x = 0.5
            hotspot_y = 0.5
            label_color = "rouge"
            style_elem = find_style(placemark)
            if style_elem is not None:
                icon_color = style_elem.find('.//kml:IconStyle/kml:color', ns)
                if icon_color is not None:
                    color = kml_color_to_name(icon_color.text, color)
                scale_elem = style_elem.find('.//kml:IconStyle/kml:scale', ns)
                if scale_elem is not None:
                    try:
                        scale = float(scale_elem.text.strip())
                    except:
                        scale = 1.0
                href_elem = style_elem.find('.//kml:IconStyle/kml:Icon/kml:href', ns)
                if href_elem is not None and href_elem.text:
                    icon = POINT_ICON_HREF_MAP.get(href_elem.text.strip(), icon)
                hot_spot = style_elem.find('.//kml:IconStyle/kml:hotSpot', ns)
                if hot_spot is not None:
                    try:
                        hotspot_x = float(hot_spot.get("x", hotspot_x))
                        hotspot_y = float(hot_spot.get("y", hotspot_y))
                    except:
                        hotspot_x = 0.5
                        hotspot_y = 0.5
                label_color_elem = style_elem.find('.//kml:LabelStyle/kml:color', ns)
                if label_color_elem is not None:
                    label_color = kml_color_to_name(label_color_elem.text, label_color)
            return scale, icon, color, hotspot_x, hotspot_y, label_color
        
        # Extraire les points (Placemark avec Point)
        for placemark in root.findall('.//kml:Placemark', ns):
            name_elem = placemark.find('kml:name', ns)
            name = name_elem.text if name_elem is not None else "Point sans nom"
            
            desc_elem = placemark.find('kml:description', ns)
            description = desc_elem.text if desc_elem is not None else ""
            
            point_elem = placemark.find('.//kml:Point/kml:coordinates', ns)
            if point_elem is not None:
                coords = point_elem.text.strip().split(',')
                if len(coords) >= 2:
                    lon, lat = float(coords[0]), float(coords[1])
                    alt = float(coords[2]) if len(coords) >= 3 else 0.0
                    scale, icon, color, hotspot_x, hotspot_y, label_color = extract_point_style(placemark)
                    points.append({
                        "type": "Point", "name": name, "lat": lat, "lon": lon,
                        "alt": alt, "scale": scale, "icon": icon, "color": color,
                        "hotspot_x": hotspot_x, "hotspot_y": hotspot_y,
                        "label_color": label_color, "description": description
                    })
            
            # Extraire les lignes (LineString)
            line_elem = placemark.find('.//kml:LineString/kml:coordinates', ns)
            if line_elem is not None:
                coords_text = line_elem.text.strip()
                coords_list = []
                for coord_pair in coords_text.split():
                    if ',' in coord_pair:
                        parts = coord_pair.split(',')
                        if len(parts) >= 2:
                            coords_list.append((float(parts[0]), float(parts[1])))
                
                if len(coords_list) >= 2:
                    color, width = extract_line_style(placemark)
                    lines.append({
                        "type": "Ligne", "name": name, "points": coords_list,
                        "description": description, "color": color, "width": width
                    })
            
            # Extraire les polygones
            poly_elem = placemark.find('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns)
            if poly_elem is not None:
                coords_text = poly_elem.text.strip()
                coords_list = []
                for coord_pair in coords_text.split():
                    if ',' in coord_pair:
                        parts = coord_pair.split(',')
                        if len(parts) >= 2:
                            coords_list.append((float(parts[0]), float(parts[1])))
                
                if len(coords_list) >= 3:
                    color, width, fill, fill_color = extract_polygon_style(placemark)
                    
                    polygons.append({
                        "type": "Polygone", "name": name, "points": coords_list,
                        "description": description, "color": color, "width": width,
                        "fill": fill, "fill_color": fill_color
                    })
        
        return points, lines, polygons
    
    except Exception as e:
        print(f"Erreur lors du parsing KML: {e}")
        return [], [], []

def import_kml_to_databases(viewer):
    """
    Importe un fichier KML et l'enregistre dans les bases de données
    Propose à l'utilisateur de remplacer ou d'ajouter aux données existantes
    """
    try:
        # Sélectionner le fichier KML
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier KML",
            filetypes=[("Fichiers KML", "*.kml"), ("Tous les fichiers", "*.*")]
        )
        
        if not file_path:
            return False
        
        # Lire le contenu du fichier KML
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                kml_content = f.read()
        except UnicodeDecodeError:
            # Essayer avec d'autres encodages
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    kml_content = f.read()
            except:
                messagebox.showerror("Erreur", "Impossible de lire le fichier KML")
                return False
        
        # Parser le fichier KML
        points, lines, polygons = parse_kml_file(kml_content)
        
        if not points and not lines and not polygons:
            messagebox.showwarning("Attention", "Aucun objet trouvé dans le fichier KML")
            return False
        
        # Afficher le résumé des objets trouvés
        summary = f"Objets trouvés dans le fichier KML:\n"
        summary += f"• Points: {len(points)}\n"
        summary += f"• Lignes: {len(lines)}\n"
        summary += f"• Polygones: {len(polygons)}\n\n"
        summary += "Que voulez-vous faire?"
        
        # Créer une fenêtre de dialogue personnalisée
        dialog = tk.Toplevel()
        dialog.title("Importation KML")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.grab_set()  # Rendre la fenêtre modale
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"400x250+{x}+{y}")
        
        result = {"action": None}
        
        # Label avec le résumé
        label = tk.Label(dialog, text=summary, justify=tk.LEFT, padx=20, pady=20)
        label.pack()
        
        # Frame pour les boutons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def add_to_existing():
            result["action"] = "add"
            dialog.destroy()
        
        def replace_existing():
            result["action"] = "replace"
            dialog.destroy()
        
        def cancel_import():
            result["action"] = "cancel"
            dialog.destroy()
        
        # Boutons
        tk.Button(button_frame, text="Ajouter aux objets existants", 
                 command=add_to_existing, width=25).pack(pady=5)
        tk.Button(button_frame, text="Remplacer les objets existants", 
                 command=replace_existing, width=25).pack(pady=5)
        tk.Button(button_frame, text="Annuler", 
                 command=cancel_import, width=25).pack(pady=5)
        
        # Attendre que l'utilisateur fasse son choix
        dialog.wait_window()
        
        if result["action"] == "cancel" or result["action"] is None:
            return False
        
        # Chemins des bases de données
        points_db = "points.db"
        lines_db = "lignes.db" 
        polygons_db = "polygones.db"
        
        success = True
        
        # Importer les points
        if points:
            if result["action"] == "replace":
                conn = sqlite3.connect(points_db)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM points")
                conn.commit()
                conn.close()

            for point in points:
                add_result = database.point_add(
                    point["name"],
                    point["lat"],
                    point["lon"],
                    point.get("alt", 0.0),
                    point.get("scale", 1.0),
                    point.get("icon", ""),
                    point.get("color", "Rouge"),
                    point.get("hotspot_x", 0.5),
                    point.get("hotspot_y", 0.5),
                    point.get("label_color", "Rouge")
                )
                if add_result == "error":
                    success = False

            database.load_item_treeview(viewer,"points.db",viewer.points_checked_items,viewer.tree,"points")
        
        # Importer les lignes
        if lines:
            if result["action"] == "replace":
                conn = sqlite3.connect(lines_db)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM lines")
                conn.commit()
                conn.close()

            for line in lines:
                points_str = " ".join([f"{lon},{lat},0" for lon, lat in line["points"]])
                add_result = database.line_add(line["name"], line["color"], line["width"], points_str)
                if add_result == "error":
                    success = False

                # Recharger la liste des lignes dans le treeview et mise à jour de l'affichage sur la carte
                database.load_item_treeview(viewer,"lignes.db",viewer.lines_checked_items,viewer.lines_tree,"lines")
        
        # Importer les polygones
        if polygons:
            if result["action"] == "replace":
                conn = sqlite3.connect(polygons_db)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM polygons")
                conn.commit()
                conn.close()

            for polygon in polygons:
                points_str = " ".join([f"{lon},{lat},0" for lon, lat in polygon["points"]])
                add_result = database.polygone_add(
                    polygon["name"],
                    polygon["color"],
                    polygon["width"],
                    polygon["fill"],
                    polygon.get("fill_color", polygon["color"]),
                    points_str
                )
                if add_result == "error":
                    success = False

            database.load_item_treeview(viewer,"polygones.db",viewer.polygones_checked_items,viewer.polygones_tree,"polygons")
        
        if success:
            messagebox.showinfo("Succès", 
                f"Importation terminée avec succès!\n"
                f"• {len(points)} points importés\n"
                f"• {len(lines)} lignes importées\n"
                f"• {len(polygons)} polygones importés")
            return True
        else:
            messagebox.showerror("Erreur", "Erreur lors de l'importation")
            return False

        
    
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'importation KML: {e}")
        return False


def export_csv_foreflight(viewer, export_all=False):
    """Exporte les points vers un fichier CSV au format user_waypoints"""
    selected_points = None

    if not export_all:
        selected_points = []
        if hasattr(viewer, "points_checked_items"):
            selected_points = [
                info["data"][0]
                for info in viewer.points_checked_items.values()
                if info.get("checked")
            ]

        if selected_points == []:
            messagebox.showwarning("Attention", "Aucun point coche pour l'export")
            return

    try:
        conn = sqlite3.connect("points.db")
        cursor = conn.cursor()
        if selected_points is None:
            cursor.execute("SELECT name, lat, lon, alt FROM points")
        else:
            placeholders = ",".join(["?"] * len(selected_points))
            cursor.execute(
                f"SELECT name, lat, lon, alt FROM points WHERE name IN ({placeholders})",
                tuple(selected_points),
            )
        points = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la lecture des points: {e}")
        return
    
    if not points:
        messagebox.showwarning("Export CSV", "Aucun point à exporter.")
        return
    
    messagebox.showinfo(
        "Export ForeFlight",
        "Pour un export vers ForeFlight, le nom du fichier ne doit pas être changé : user_waypoints.csv"
    )
    
    file_path = filedialog.asksaveasfilename(
        title="Enregistrer le fichier CSV",
        defaultextension=".csv",
        initialfile="user_waypoints.csv",
        filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["WAYPOINT_NAME", "Waypoint description", "Latitude", "Longitude", "Elevation"])
            for name, lat, lon, alt in points:
                writer.writerow([name, "", lat, lon, alt if alt is not None else 0.0])
        messagebox.showinfo("Export CSV", f"{len(points)} point(s) exporté(s) avec succès.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")

def export_csv_sdvfr(viewer, export_all=False):
    """Exporte les points vers un fichier CSV au format SDVFR"""
    selected_points = None

    if not export_all:
        selected_points = []
        if hasattr(viewer, "points_checked_items"):
            selected_points = [
                info["data"][0]
                for info in viewer.points_checked_items.values()
                if info.get("checked")
            ]

        if selected_points == []:
            messagebox.showwarning("Attention", "Aucun point coche pour l'export")
            return

    try:
        conn = sqlite3.connect("points.db")
        cursor = conn.cursor()
        if selected_points is None:
            cursor.execute("SELECT name, lat, lon FROM points")
        else:
            placeholders = ",".join(["?"] * len(selected_points))
            cursor.execute(
                f"SELECT name, lat, lon FROM points WHERE name IN ({placeholders})",
                tuple(selected_points),
            )
        points = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la lecture des points: {e}")
        return
    
    if not points:
        messagebox.showwarning("Export CSV", "Aucun point à exporter.")
        return
    
    file_path = filedialog.asksaveasfilename(
        title="Enregistrer le fichier CSV",
        defaultextension=".csv",
        filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("name;description;type;latitude;longitude;shape;color\n")
            for name, lat, lon in points:
                f.write(f'{name};none;Aéronautique;{lat};{lon};circle;blue\n')
        messagebox.showinfo("Export CSV", f"{len(points)} point(s) exporté(s) avec succès.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")


def import_csv(viewer):
    """
    Fonction pour importer des points depuis un fichier CSV dans la base de données.
    
    Args:
        db_path (str): Chemin vers la base de données SQLite (par défaut "points.db")
    
    Returns:
        int: Nombre de points importés, ou -1 en cas d'erreur
    """
    try:
        # # Créer une fenêtre Tkinter temporaire pour la boîte de dialogue
        # root = tk.Tk()
        # root.withdraw()  # Masquer la fenêtre principale
        
        # Ouvrir la boîte de dialogue pour sélectionner le fichier CSV
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier CSV",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        
        if not file_path:
            #root.destroy()
            return 0  # Aucun fichier sélectionné
        
        # Lire le fichier CSV - essayer d'abord avec le point-virgule, puis avec la virgule
        try:
            # Détecter automatiquement le séparateur en lisant la première ligne
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
            
            # Compter les occurrences de chaque séparateur potentiel
            semicolon_count = first_line.count(';')
            comma_count = first_line.count(',')
            
            # Déterminer le séparateur le plus probable
            if semicolon_count > comma_count:
                separator = ';'
            else:
                separator = ','
            
            # Lire le fichier avec le séparateur détecté
            df = pd.read_csv(file_path, sep=separator)
            
            # Vérification : s'assurer qu'on a plus d'une colonne
            if len(df.columns) < 3:
                # Si moins de 3 colonnes, essayer avec l'autre séparateur
                other_separator = ',' if separator == ';' else ';'
                df_alt = pd.read_csv(file_path, sep=other_separator)
                if len(df_alt.columns) >= 3:
                    df = df_alt
                    separator = other_separator
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la lecture du fichier CSV: {e}")
            #root.destroy()
            return -1
        
        # Détecter les colonnes automatiquement (similaire au code streamlit)
        cols = df.columns.str.lower()
        name_col = None
        lat_col = None
        lon_col = None
        
        # Recherche des colonnes nom
        for col in df.columns:
            col_lower = cols[df.columns.get_loc(col)]
            if any(x in col_lower for x in ['nom', 'name', 'point']):
                name_col = col
                break
        
        # Recherche des colonnes latitude
        for col in df.columns:
            col_lower = cols[df.columns.get_loc(col)]
            if any(x in col_lower for x in ['lat', 'latitude']):
                lat_col = col
                break
        
        # Recherche des colonnes longitude
        for col in df.columns:
            col_lower = cols[df.columns.get_loc(col)]
            if any(x in col_lower for x in ['lon', 'lng', 'longitude']):
                lon_col = col
                break
        
        if not (name_col and lat_col and lon_col):
            available_cols = ", ".join(df.columns.tolist())
            messagebox.showerror(
                "Erreur", 
                f"Colonnes requises non trouvées.\n"
                f"Vérifiez que le fichier contient: nom/name, latitude/lat, longitude/lon\n"
                f"Séparateur détecté: '{separator}'\n"
                f"Colonnes disponibles: {available_cols}"
            )
            #root.destroy()
            return -1
        
        # Afficher un aperçu et demander confirmation
        preview_text = f"Colonnes détectées:\n- Nom: {name_col}\n- Latitude: {lat_col}\n- Longitude: {lon_col}\n\n"
        preview_text += f"Nombre de lignes: {len(df)}\n\n"
        preview_text += "Aperçu des 3 premières lignes:\n"
        
        for i, row in df.head(3).iterrows():
            preview_text += f"{i+1}. {row[name_col]} | {row[lat_col]} | {row[lon_col]}\n"
        
        preview_text += "\nVoulez-vous importer ces points ?"
        
        result = messagebox.askyesno("Confirmation d'import", preview_text)
        if not result:
            #root.destroy()
            return 0
        
        imported = 0
        updated = 0
        cancelled = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                name = str(row[name_col]).strip()
                lat = float(row[lat_col])
                lon = float(row[lon_col])
                
                if not name:
                    errors += 1
                    continue
                
                add_result = database.point_add(
                    name,
                    lat,
                    lon,
                    0.0,
                    1.0,
                    "Punaise",
                    "Rouge",
                    0.5,
                    0.5,
                    "Rouge"
                )
                
                if add_result == "created":
                    imported += 1
                elif add_result == "updated":
                    updated += 1
                elif add_result == "cancelled":
                    cancelled += 1
                else:
                    errors += 1
                    
            except (ValueError, TypeError):
                errors += 1
                continue
        
        database.load_item_treeview(viewer,"points.db",viewer.points_checked_items,viewer.tree,"points")
        
        result_msg = f"Import terminé!\n\n"
        result_msg += f"✅ {imported} point(s) importé(s) avec succès\n"
        if updated > 0:
            result_msg += f"🔄 {updated} point(s) modifié(s)\n"
        if cancelled > 0:
            result_msg += f"⏭️ {cancelled} point(s) existant(s) ignoré(s)\n"
        if errors > 0:
            result_msg += f"⚠️ {errors} ligne(s) ignorée(s) (coordonnées invalides, noms vides ou erreur)"
        
        messagebox.showinfo("Import réussi", result_msg)
        return imported + updated
    
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inattendue: {e}")
        return -1    
        