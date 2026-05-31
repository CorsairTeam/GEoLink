import tkinter as tk

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
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Arial", 9),
            justify="left",
            padx=5,
            pady=3
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Masquer l'info-bulle"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None