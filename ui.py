import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import csv

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        lbl_titulo = ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_titulo.grid(row=0, column=0, columnspan=4, padx=20, pady=(20, 30), sticky="w")
        
        # Tarjetas principales
        self.card_total = self._crear_tarjeta(1, 0, "Total de Equipos", "0", "#1f538d")
        self.card_activos = self._crear_tarjeta(1, 1, "Equipos Activos", "0", "#2e7d32")
        self.card_reparacion = self._crear_tarjeta(1, 2, "En Reparación", "0", "#e65100")
        self.card_inactivos = self._crear_tarjeta(1, 3, "Inactivos/Baja", "0", "#c62828")
        
        # Sección secundaria
        self.frame_secundario = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_secundario.grid(row=2, column=0, columnspan=4, padx=10, pady=20, sticky="nsew")
        self.frame_secundario.grid_columnconfigure((0, 1), weight=1)
        
        # Resumen por Categoría
        self.frame_categorias = ctk.CTkFrame(self.frame_secundario, corner_radius=10)
        self.frame_categorias.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        lbl_cat_title = ctk.CTkLabel(self.frame_categorias, text="Distribución por Categoría", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_cat_title.pack(pady=10, padx=10, anchor="w")
        
        self.frame_cat_list = ctk.CTkFrame(self.frame_categorias, fg_color="transparent")
        self.frame_cat_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Últimos Registros
        self.frame_recientes = ctk.CTkFrame(self.frame_secundario, corner_radius=10)
        self.frame_recientes.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        lbl_rec_title = ctk.CTkLabel(self.frame_recientes, text="Últimos Equipos Registrados", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_rec_title.pack(pady=10, padx=10, anchor="w")
        
        self.frame_rec_list = ctk.CTkFrame(self.frame_recientes, fg_color="transparent")
        self.frame_rec_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.actualizar_metricas()
        
    def _crear_tarjeta(self, row, col, titulo, valor_inicial, color):
        frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=10)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        lbl_titulo = ctk.CTkLabel(frame, text=titulo, font=ctk.CTkFont(size=14))
        lbl_titulo.pack(pady=(15, 5))
        
        lbl_valor = ctk.CTkLabel(frame, text=valor_inicial, font=ctk.CTkFont(size=32, weight="bold"), text_color=color)
        lbl_valor.pack(pady=(5, 15))
        
        return lbl_valor

    def actualizar_metricas(self):
        # Actualizar KPIs
        metricas = self.db.get_metricas()
        self.card_total.configure(text=str(metricas["total"]))
        self.card_activos.configure(text=str(metricas["activos"]))
        self.card_reparacion.configure(text=str(metricas["reparacion"]))
        self.card_inactivos.configure(text=str(metricas.get("inactivos", 0)))
        
        # Limpiar listas
        for widget in self.frame_cat_list.winfo_children():
            widget.destroy()
            
        for widget in self.frame_rec_list.winfo_children():
            widget.destroy()
            
        # Llenar categorías
        categorias = self.db.get_metricas_por_categoria()
        if not categorias:
            ctk.CTkLabel(self.frame_cat_list, text="No hay equipos registrados.", text_color="gray").pack(pady=10)
        else:
            for cat, count in categorias.items():
                row = ctk.CTkFrame(self.frame_cat_list, fg_color="transparent")
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=cat, font=ctk.CTkFont(size=13)).pack(side="left")
                ctk.CTkLabel(row, text=str(count), font=ctk.CTkFont(size=13, weight="bold")).pack(side="right")
                
        # Llenar recientes
        recientes = self.db.get_ultimos_equipos(5)
        if not recientes:
            ctk.CTkLabel(self.frame_rec_list, text="No hay equipos recientes.", text_color="gray").pack(pady=10)
        else:
            for d in recientes:
                # d = (codigo, nombre, categoria, estado)
                row = ctk.CTkFrame(self.frame_rec_list, fg_color=("gray90", "gray25"), corner_radius=5)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=f"{d[0]} - {d[1]}", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(5,0))
                ctk.CTkLabel(row, text=f"{d[2]} | {d[3]}", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=10, pady=(0,5))

class EquiposFrame(ctk.CTkFrame):
    def __init__(self, master, db, callback_dashboard):
        super().__init__(master)
        self.db = db
        self.callback_dashboard = callback_dashboard
        self.equipo_seleccionado_id = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self._crear_formulario()
        self._crear_filtros()
        self._crear_tabla()
        
        self.cargar_datos()

    def _crear_formulario(self):
        form_frame = ctk.CTkFrame(self)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        form_frame.grid_columnconfigure((1, 3, 5), weight=1)
        
        # Variables
        self.var_codigo = ctk.StringVar()
        self.var_serie = ctk.StringVar()
        self.var_nombre = ctk.StringVar()
        self.var_cat = ctk.StringVar(value="PC Hardware")
        self.var_tipo = ctk.StringVar()
        self.var_estado = ctk.StringVar(value="Activo")
        self.var_mac = ctk.StringVar()
        self.var_asignado = ctk.StringVar()
        self.var_fecha = ctk.StringVar()
        self.var_notas = ctk.StringVar()
        
        # Fila 1
        ctk.CTkLabel(form_frame, text="Código:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(form_frame, textvariable=self.var_codigo).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="No. Serie:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(form_frame, textvariable=self.var_serie).grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Nombre:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(form_frame, textvariable=self.var_nombre).grid(row=0, column=5, padx=5, pady=5, sticky="ew")
        
        # Fila 2
        ctk.CTkLabel(form_frame, text="Categoría:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        categorias = ["PC Hardware", "Accesorios", "Monitores", "UPS", "Redes", "Otro"]
        cb_cat = ctk.CTkComboBox(form_frame, values=categorias, variable=self.var_cat, command=self._actualizar_tipos)
        cb_cat.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Tipo:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.cb_tipo = ctk.CTkComboBox(form_frame, values=[], variable=self.var_tipo)
        self.cb_tipo.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        self._actualizar_tipos(self.var_cat.get())
        
        ctk.CTkLabel(form_frame, text="Estado:").grid(row=1, column=4, padx=5, pady=5, sticky="e")
        estados = ["Activo", "Inactivo", "En Reparacion", "De Baja"]
        ctk.CTkComboBox(form_frame, values=estados, variable=self.var_estado).grid(row=1, column=5, padx=5, pady=5, sticky="ew")
        
        # Fila 3
        ctk.CTkLabel(form_frame, text="MAC/IP:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(form_frame, textvariable=self.var_mac).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Asignado a:").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(form_frame, textvariable=self.var_asignado).grid(row=2, column=3, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Fecha Adq:").grid(row=2, column=4, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(form_frame, textvariable=self.var_fecha, placeholder_text="YYYY-MM-DD").grid(row=2, column=5, padx=5, pady=5, sticky="ew")
        
        # Fila 4
        ctk.CTkLabel(form_frame, text="Notas:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        ctk.CTkEntry(form_frame, textvariable=self.var_notas).grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        
        # Botones de Acción
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=6, pady=10)
        
        self.btn_guardar = ctk.CTkButton(btn_frame, text="Guardar Nuevo", command=self._guardar)
        self.btn_guardar.pack(side="left", padx=10)
        
        self.btn_limpiar = ctk.CTkButton(btn_frame, text="Limpiar Formulario", fg_color="gray", command=self._limpiar)
        self.btn_limpiar.pack(side="left", padx=10)
        
        self.btn_eliminar = ctk.CTkButton(btn_frame, text="Eliminar", fg_color="#d32f2f", hover_color="#b71c1c", command=self._eliminar)
        self.btn_eliminar.pack(side="left", padx=10)

    def _actualizar_tipos(self, categoria):
        opciones = {"PC Hardware": ["Desktop", "Laptop", "Servidor", "Mini PC"],
                    "Accesorios": ["Teclado", "Raton", "Audifonos", "Cables"],
                    "Monitores": ["19\"", "22\"", "24\"", "27\""],
                    "UPS": ["500VA", "1000VA", "1500VA"],
                    "Redes": ["Router", "Switch", "Access Point"],
                    "Otro": ["Otro"]}
        self.cb_tipo.configure(values=opciones.get(categoria, ["Otro"]))
        self.var_tipo.set(opciones.get(categoria, ["Otro"])[0])

    def _crear_filtros(self):
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        
        self.var_search = ctk.StringVar()
        self.var_search.trace_add("write", lambda *args: self.cargar_datos())
        
        ctk.CTkLabel(filter_frame, text="Buscar:").pack(side="left", padx=5)
        entry_search = ctk.CTkEntry(filter_frame, textvariable=self.var_search, width=200, placeholder_text="Cód, Serie, Nombre...")
        entry_search.pack(side="left", padx=5)
        
        ctk.CTkButton(filter_frame, text="Exportar CSV", width=100, command=self._exportar_csv).pack(side="right", padx=5)

    def _crear_tabla(self):
        # Estilo para el Treeview (adaptado a claro/oscuro)
        style = ttk.Style()
        style.theme_use("default")
        
        # Determinar si estamos en modo oscuro o claro
        bg_color = "#ffffff" if ctk.get_appearance_mode() == "Light" else "#2b2b2b"
        fg_color = "#000000" if ctk.get_appearance_mode() == "Light" else "#ffffff"
        field_bg = "#ffffff" if ctk.get_appearance_mode() == "Light" else "#333333"
        header_bg = "#e0e0e0" if ctk.get_appearance_mode() == "Light" else "#1f1f1f"
        
        style.configure("Treeview", background=bg_color, foreground=fg_color, rowheight=25, fieldbackground=field_bg, borderwidth=0)
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background=header_bg, foreground=fg_color)
        style.map('Treeview', background=[('selected', '#1f538d')], foreground=[('selected', '#ffffff')])
        
        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        columnas = ("id", "codigo", "serie", "nombre", "categoria", "estado", "asignado")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        self.tabla.heading("id", text="ID")
        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("serie", text="No. Serie")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("categoria", text="Categoría")
        self.tabla.heading("estado", text="Estado")
        self.tabla.heading("asignado", text="Asignado a")
        
        self.tabla.column("id", width=30)
        self.tabla.column("codigo", width=100)
        self.tabla.column("serie", width=120)
        self.tabla.column("nombre", width=150)
        self.tabla.column("categoria", width=100)
        self.tabla.column("estado", width=100)
        self.tabla.column("asignado", width=120)
        
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tabla.bind("<Double-1>", self._seleccionar_registro)

    def cargar_datos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        busqueda = self.var_search.get()
        datos = self.db.get_equipos(search_query=busqueda)
        
        for d in datos:
            # Insertar solo algunas columnas en la tabla principal
            self.tabla.insert("", "end", values=(d[0], d[1], d[2], d[3], d[4], d[6], d[8]))
            
        self.callback_dashboard()

    def _guardar(self):
        datos = (
            self.var_codigo.get(), self.var_serie.get(), self.var_nombre.get(),
            self.var_cat.get(), self.var_tipo.get(), self.var_estado.get(),
            self.var_mac.get(), self.var_asignado.get(), self.var_fecha.get(),
            self.var_notas.get()
        )
        
        if not all([datos[0], datos[2]]):
            messagebox.showwarning("Aviso", "Código y Nombre son obligatorios.")
            return

        if self.equipo_seleccionado_id:
            exito, msj = self.db.actualizar_equipo(self.equipo_seleccionado_id, datos)
        else:
            exito, msj = self.db.agregar_equipo(datos)
            
        if exito:
            messagebox.showinfo("Éxito", msj)
            self._limpiar()
            self.cargar_datos()
        else:
            messagebox.showerror("Error", msj)

    def _seleccionar_registro(self, event):
        seleccion = self.tabla.selection()
        if not seleccion: return
        
        item_id = self.tabla.item(seleccion[0], "values")[0]
        # Buscar todos los detalles del equipo en BD
        self.db.cursor.execute("SELECT * FROM equipos WHERE id=?", (item_id,))
        equipo = self.db.cursor.fetchone()
        
        if equipo:
            self.equipo_seleccionado_id = equipo[0]
            self.var_codigo.set(equipo[1])
            self.var_serie.set(equipo[2] if equipo[2] else "")
            self.var_nombre.set(equipo[3])
            self.var_cat.set(equipo[4])
            self._actualizar_tipos(equipo[4])
            self.var_tipo.set(equipo[5])
            self.var_estado.set(equipo[6])
            self.var_mac.set(equipo[7] if equipo[7] else "")
            self.var_asignado.set(equipo[8] if equipo[8] else "")
            self.var_fecha.set(equipo[9] if equipo[9] else "")
            self.var_notas.set(equipo[10] if equipo[10] else "")
            
            self.btn_guardar.configure(text="Actualizar Equipo")

    def _eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Seleccione un equipo para eliminar.")
            return
            
        if messagebox.askyesno("Confirmar", "¿Eliminar el equipo seleccionado?"):
            item_id = self.tabla.item(seleccion[0], "values")[0]
            exito, msj = self.db.eliminar_equipo(item_id)
            if exito:
                self._limpiar()
                self.cargar_datos()
                messagebox.showinfo("Éxito", msj)
            else:
                messagebox.showerror("Error", msj)

    def _limpiar(self):
        self.equipo_seleccionado_id = None
        self.var_codigo.set("")
        self.var_serie.set("")
        self.var_nombre.set("")
        self.var_mac.set("")
        self.var_asignado.set("")
        self.var_fecha.set("")
        self.var_notas.set("")
        self.btn_guardar.configure(text="Guardar Nuevo")

    def _exportar_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivos CSV", "*.csv")])
        if not path: return
        
        try:
            with open(path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Escribir cabeceras
                writer.writerow(["ID", "Código", "No. Serie", "Nombre", "Categoría", "Tipo", "Estado", "MAC", "Asignado", "Fecha", "Notas"])
                # Obtener la data actual filtrada
                busqueda = self.var_search.get()
                datos = self.db.get_equipos(search_query=busqueda)
                for d in datos:
                    writer.writerow(d)
            messagebox.showinfo("Éxito", "Datos exportados correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")
