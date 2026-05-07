import customtkinter as ctk
from database import Database
from ui import DashboardFrame, EquiposFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de CustomTkinter
        ctk.set_appearance_mode("Light")  # Por solicitud del usuario
        ctk.set_default_color_theme("blue")
        
        self.title("Sistema de Gestión de Inventario TI")
        self.geometry("1100x700")
        
        # Grid Layout (1 fila, 2 columnas)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Instanciar Base de Datos
        self.db = Database()
        
        # Crear Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Inventario TI", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))
        
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_equipos = ctk.CTkButton(self.sidebar_frame, text="Gestión de Equipos", command=self.show_equipos)
        self.btn_equipos.grid(row=2, column=0, padx=20, pady=10)
        
        # Selector de Tema
        self.theme_label = ctk.CTkLabel(self.sidebar_frame, text="Tema de Interfaz:", anchor="w")
        self.theme_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.theme_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_theme)
        self.theme_menu.grid(row=6, column=0, padx=20, pady=(10, 20))
        
        # Instanciar Frames
        self.dashboard_frame = DashboardFrame(self, self.db)
        self.equipos_frame = EquiposFrame(self, self.db, self.actualizar_dashboard)
        
        # Vista inicial
        self.show_dashboard()

    def show_dashboard(self):
        self.equipos_frame.grid_forget()
        self.dashboard_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.actualizar_dashboard()

    def show_equipos(self):
        self.dashboard_frame.grid_forget()
        self.equipos_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def actualizar_dashboard(self):
        self.dashboard_frame.actualizar_metricas()

    def change_theme(self, new_theme: str):
        ctk.set_appearance_mode(new_theme)
        # Actualizar colores del treeview si es necesario re-invocando la creación de estilos
        self.equipos_frame._crear_tabla()

if __name__ == "__main__":
    app = App()
    app.mainloop()
