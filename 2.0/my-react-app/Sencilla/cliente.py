import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from cache import Cache
import logging
from logging.handlers import RotatingFileHandler

def configurar_logger():
    logger = logging.getLogger('sistema_tarifas')
    logger.setLevel(logging.INFO)
    
    # Configurar el manejador de archivo rotativo
    handler = RotatingFileHandler('sistema_tarifas.log', maxBytes=1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger

# Crear una instancia del logger
logger = configurar_logger()

def log_mensaje(mensaje, nivel='info'):
    """
    Registra un mensaje en el archivo de log.
    
    :param mensaje: El mensaje a registrar
    :param nivel: El nivel de log (info, warning, error, critical)
    """
    if nivel == 'info':
        logger.info(mensaje)
    elif nivel == 'warning':
        logger.warning(mensaje)
    elif nivel == 'error':
        logger.error(mensaje)
    elif nivel == 'critical':
        logger.critical(mensaje)
    else:
        logger.info(mensaje)

class TarifasApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestión de Tarifas")
        self.geometry("1000x600")
        self.configure(bg='#f7f7f7')
        self.cache = Cache()
        self.selected_cliente_id = None

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, relief="flat", background="#2196F3", foreground="white", font=('Helvetica', 10, 'bold'))
        self.style.configure("TLabel", background='#f7f7f7', font=('Helvetica', 10))
        self.style.configure("TEntry", font=('Helvetica', 10))
        self.style.configure("Treeview", font=('Helvetica', 9), rowheight=25)
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

        self.login_frame = ttk.Frame(self)
        self.main_frame = ttk.Frame(self)

        self.create_login_widgets()

    def create_login_widgets(self):
        self.login_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ttk.Label(self.login_frame, text="Usuario:").pack(pady=5)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.pack(pady=5)

        ttk.Label(self.login_frame, text="Contraseña:").pack(pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self.login_frame, text="Iniciar Sesión", command=self.login).pack(pady=10)

    def login(self):
        if self.username_entry.get() == "admin" and self.password_entry.get() == "admin":
            self.login_frame.pack_forget()
            self.create_main_widgets()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def create_main_widgets(self):
        self.main_frame.pack(expand=True, fill="both")

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.home_frame = ttk.Frame(self.notebook)
        self.tarifas_frame = ttk.Frame(self.notebook)
        self.items_frame = ttk.Frame(self.notebook)
        self.unidades_frame = ttk.Frame(self.notebook)
        self.clientes_frame = ttk.Frame(self.notebook)
        self.aumentos_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.home_frame, text="Inicio")
        self.notebook.add(self.tarifas_frame, text="Tarifas")
        self.notebook.add(self.items_frame, text="Items")
        self.notebook.add(self.unidades_frame, text="Unidades")
        self.notebook.add(self.clientes_frame, text="Clientes")
        self.notebook.add(self.aumentos_frame, text="Aumentos")

        self.create_home_widgets()
        self.create_tarifas_widgets()
        self.create_items_widgets()
        self.create_unidades_widgets()
        self.create_clientes_widgets()
        self.create_aumentos_widgets()

    def create_home_widgets(self):
        self.tarifas_vencimiento_tree = ttk.Treeview(self.home_frame, columns=("ID", "Item", "Unidad", "Cliente", "Precio", "Fecha"), show="headings")
        self.tarifas_vencimiento_tree.heading("ID", text="ID")
        self.tarifas_vencimiento_tree.heading("Item", text="Item")
        self.tarifas_vencimiento_tree.heading("Unidad", text="Unidad")
        self.tarifas_vencimiento_tree.heading("Cliente", text="Cliente")
        self.tarifas_vencimiento_tree.heading("Precio", text="Precio")
        self.tarifas_vencimiento_tree.heading("Fecha", text="Fecha")
        self.tarifas_vencimiento_tree.pack(expand=True, fill="both")
        
        button_frame = ttk.Frame(self.home_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Actualizar", command=self.refresh_tarifas).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refrescar", command=self.refresh_home_data).pack(side=tk.LEFT, padx=5)
            

    def create_tarifas_widgets(self):
        self.tarifas_tree = ttk.Treeview(self.tarifas_frame, columns=("ID", "Item", "Unidad", "Cliente", "Precio", "Fecha Inicio", "Fecha Final"), show="headings")
        self.tarifas_tree.heading("ID", text="ID")
        self.tarifas_tree.heading("Item", text="Item")
        self.tarifas_tree.heading("Unidad", text="Unidad")
        self.tarifas_tree.heading("Cliente", text="Cliente")
        self.tarifas_tree.heading("Precio", text="Precio")
        self.tarifas_tree.heading("Fecha Inicio", text="Fecha Inicio")
        self.tarifas_tree.heading("Fecha Final", text="Fecha Final")
        self.tarifas_tree.pack(expand=True, fill="both")

        button_frame = ttk.Frame(self.tarifas_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Agregar", command=self.show_add_tarifa_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", command=self.show_edit_tarifa_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_tarifa).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.refresh_tarifas).pack(side=tk.LEFT, padx=5)

    def create_items_widgets(self):
        self.items_tree = ttk.Treeview(self.items_frame, columns=("ID", "Nombre"), show="headings")
        self.items_tree.heading("ID", text="ID")
        self.items_tree.heading("Nombre", text="Nombre")
        self.items_tree.pack(expand=True, fill="both")

        button_frame = ttk.Frame(self.items_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Agregar", command=self.show_add_item_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", command=self.show_edit_item_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.refresh_items).pack(side=tk.LEFT, padx=5)

    def create_unidades_widgets(self):
        self.unidades_tree = ttk.Treeview(self.unidades_frame, columns=("ID", "Nombre"), show="headings")
        self.unidades_tree.heading("ID", text="ID")
        self.unidades_tree.heading("Nombre", text="Nombre")
        self.unidades_tree.pack(expand=True, fill="both")

        button_frame = ttk.Frame(self.unidades_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Agregar", command=self.show_add_unidad_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", command=self.show_edit_unidad_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_unidad).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.refresh_unidades).pack(side=tk.LEFT, padx=5)

    def create_clientes_widgets(self):
        self.clientes_tree = ttk.Treeview(self.clientes_frame, columns=("ID", "Nombre"), show="headings")
        self.clientes_tree.heading("ID", text="ID")
        self.clientes_tree.heading("Nombre", text="Nombre")
        self.clientes_tree.pack(expand=True, fill="both")

        button_frame = ttk.Frame(self.clientes_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Agregar", command=self.show_add_cliente_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", command=self.show_edit_cliente_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.refresh_clientes).pack(side=tk.LEFT, padx=5)

    def create_aumentos_widgets(self):
        ttk.Label(self.aumentos_frame, text="Cliente:").pack(pady=5)
        self.cliente_combobox = ttk.Combobox(self.aumentos_frame)
        self.cliente_combobox.pack(pady=5)
        self.cliente_combobox.bind("<<ComboboxSelected>>", self.on_cliente_selected)

        ttk.Label(self.aumentos_frame, text="Número de Tarifa:").pack(pady=5)
        self.tarifa_entry = ttk.Entry(self.aumentos_frame)
        self.tarifa_entry.pack(pady=5)

        ttk.Label(self.aumentos_frame, text="Porcentaje de Aumento:").pack(pady=5)
        self.porcentaje_entry = ttk.Entry(self.aumentos_frame)
        self.porcentaje_entry.pack(pady=5)

        ttk.Label(self.aumentos_frame, text="Nueva Fecha de Vencimiento (YYYY-MM-DD):").pack(pady=5)
        self.nueva_fecha_entry = ttk.Entry(self.aumentos_frame)
        self.nueva_fecha_entry.pack(pady=5)

        self.aumentos_tree = ttk.Treeview(self.aumentos_frame, columns=("ID", "Item", "Unidad", "Cliente", "Precio Actual", "Nuevo Precio", "Fecha Actual", "Nueva Fecha"), show="headings")
        self.aumentos_tree.heading("ID", text="ID")
        self.aumentos_tree.heading("Item", text="Item")
        self.aumentos_tree.heading("Unidad", text="Unidad")
        self.aumentos_tree.heading("Cliente", text="Cliente")
        self.aumentos_tree.heading("Precio Actual", text="Precio Actual")
        self.aumentos_tree.heading("Nuevo Precio", text="Nuevo Precio")
        self.aumentos_tree.heading("Fecha Actual", text="Fecha Actual")
        self.aumentos_tree.heading("Nueva Fecha", text="Nueva Fecha")
        self.aumentos_tree.pack(expand=True, fill="both", pady=10)

        button_frame = ttk.Frame(self.aumentos_frame)
        button_frame.pack(pady=10)

        self.buscar_button = ttk.Button(button_frame, text="Buscar", command=self.buscar_tarifas)
        self.buscar_button.pack(side=tk.LEFT, padx=5)

        self.calcular_button = ttk.Button(button_frame, text="Calcular Aumento", command=self.calcular_aumento)
        self.calcular_button.pack(side=tk.LEFT, padx=5)

        self.aplicar_button = ttk.Button(button_frame, text="Aplicar Aumento", command=self.apply_increase)
        self.aplicar_button.pack(side=tk.LEFT, padx=5)

        self.cancelar_button = ttk.Button(button_frame, text="Cancelar", command=self.cancel_increase)
        self.cancelar_button.pack(side=tk.LEFT, padx=5)

        self.populate_cliente_combobox()

    def refresh_tarifas_vencimiento(self):
        tarifas = self.get_data('tarifario')
        items = self.get_dict_from_data('items')
        unidades = self.get_dict_from_data('unidades')
        clientes = self.get_dict_from_data('clientes')
        
        self.tarifas_vencimiento_tree.delete(*self.tarifas_vencimiento_tree.get_children())
        fecha_actual = datetime.now()
        for tarifa in tarifas:
            fecha_vigencia_final = datetime.strptime(tarifa.get('fecha_vigencia_final', '2099-12-31'), '%Y-%m-%d')
            if (fecha_vigencia_final - fecha_actual).days <= 30:
                self.tarifas_vencimiento_tree.insert("", "end", values=(
                    tarifa.get('id', ''),
                    items.get(tarifa.get('item_id'), tarifa.get('item_id', '')),
                    unidades.get(tarifa.get('unidad_id'), tarifa.get('unidad_id', '')),
                    clientes.get(tarifa.get('cliente_id'), tarifa.get('cliente_id', '')),
                    tarifa.get('precio', ''),
                    tarifa.get('fecha_vigencia_final', '')
                ))

    def refresh_tarifas(self):
        tarifas = self.get_data('tarifario')
        items = self.get_dict_from_data('items')
        unidades = self.get_dict_from_data('unidades')
        clientes = self.get_dict_from_data('clientes')
        
        self.tarifas_tree.delete(*self.tarifas_tree.get_children())
        for tarifa in tarifas:
            self.tarifas_tree.insert("", "end", values=(
                tarifa.get('id', ''),
                items.get(tarifa.get('item_id'), tarifa.get('item_id', '')),
                unidades.get(tarifa.get('unidad_id'), tarifa.get('unidad_id', '')),
                clientes.get(tarifa.get('cliente_id'), tarifa.get('cliente_id', '')),
                tarifa.get('precio', ''),
                tarifa.get('fecha_vigencia_inicio', ''),
                tarifa.get('fecha_vigencia_final', '')
            ))

    def refresh_items(self):
        items = self.get_data('items')
        self.items_tree.delete(*self.items_tree.get_children())
        for item in items:
            self.items_tree.insert("", "end", values=(item['id'], item['nombre']))

    def refresh_unidades(self):
        unidades = self.get_data('unidades')
        self.unidades_tree.delete(*self.unidades_tree.get_children())
        for unidad in unidades:
            self.unidades_tree.insert("", "end", values=(unidad['id'], unidad['nombre']))

    def refresh_clientes(self):
        clientes = self.get_data('clientes')
        self.clientes_tree.delete(*self.clientes_tree.get_children())
        for cliente in clientes:
            self.clientes_tree.insert("", "end", values=(cliente['id'], cliente['nombre']))

    def get_data(self, endpoint):
        cached_data = self.cache.get(endpoint)
        if cached_data:
            return cached_data

        try:
            response = requests.get(f'http://127.0.0.1:5000/api/{endpoint}')
            response.raise_for_status()
            data = response.json()
            self.cache.set(endpoint, data)
            return data
        except requests.RequestException as e:
            messagebox.showerror("Error", f"No se pudo obtener los datos: {str(e)}")
            return []

    def get_dict_from_data(self, endpoint):
        data = self.get_data(endpoint)
        return {item['id']: item['nombre'] for item in data}

    def show_add_tarifa_dialog(self):
        self.show_tarifa_dialog()

    def show_edit_tarifa_dialog(self):
        selected_item = self.tarifas_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una tarifa para editar.")
            return
        
        values = self.tarifas_tree.item(selected_item)['values']
        self.show_tarifa_dialog(values)

    def show_tarifa_dialog(self, values=None):
        dialog = tk.Toplevel(self)
        dialog.title("Añadir/Editar Tarifa")
        dialog.geometry("400x400")

        ttk.Label(dialog, text="ID:").pack(pady=5)
        id_entry = ttk.Entry(dialog)
        id_entry.pack(pady=5)

        ttk.Label(dialog, text="Item:").pack(pady=5)
        item_combobox = ttk.Combobox(dialog)
        item_combobox.pack(pady=5)

        ttk.Label(dialog, text="Unidad:").pack(pady=5)
        unidad_combobox = ttk.Combobox(dialog)
        unidad_combobox.pack(pady=5)

        ttk.Label(dialog, text="Cliente:").pack(pady=5)
        cliente_combobox = ttk.Combobox(dialog)
        cliente_combobox.pack(pady=5)

        ttk.Label(dialog, text="Precio:").pack(pady=5)
        precio_entry = ttk.Entry(dialog)
        precio_entry.pack(pady=5)

        ttk.Label(dialog, text="Fecha Vigencia Inicio (YYYY-MM-DD):").pack(pady=5)
        fecha_vigencia_inicio_entry = ttk.Entry(dialog)
        fecha_vigencia_inicio_entry.pack(pady=5)

        ttk.Label(dialog, text="Fecha Vigencia Final (YYYY-MM-DD):").pack(pady=5)
        fecha_vigencia_final_entry = ttk.Entry(dialog)
        fecha_vigencia_final_entry.pack(pady=5)

        items = self.get_dict_from_data('items')
        unidades = self.get_dict_from_data('unidades')
        clientes = self.get_dict_from_data('clientes')

        item_combobox['values'] = list(items.values())
        unidad_combobox['values'] = list(unidades.values())
        cliente_combobox['values'] = list(clientes.values())

        if values:
            id_entry.insert(0, values[0])
            item_combobox.set(values[1])
            unidad_combobox.set(values[2])
            cliente_combobox.set(values[3])
            precio_entry.insert(0, values[4])
            fecha_vigencia_inicio_entry.insert(0, values[5])
            fecha_vigencia_final_entry.insert(0, values[6])

        def guardar_tarifa():
            nueva_tarifa = {
                'item_id': next((id for id, nombre in items.items() if nombre == item_combobox.get()), None),
                'unidad_id': next((id for id, nombre in unidades.items() if nombre == unidad_combobox.get()), None),
                'cliente_id': next((id for id, nombre in clientes.items() if nombre == cliente_combobox.get()), None),
                'precio': precio_entry.get(),
                'fecha_vigencia_inicio': fecha_vigencia_inicio_entry.get(),
                'fecha_vigencia_final': fecha_vigencia_final_entry.get()
            }
            
            if values:  # Si estamos editando una tarifa existente
                nueva_tarifa['id'] = id_entry.get()
                response = requests.put(f'http://127.0.0.1:5000/api/tarifario/{nueva_tarifa["id"]}', json=nueva_tarifa)
            else:  # Si estamos creando una nueva tarifa
                response = requests.post('http://127.0.0.1:5000/api/tarifario', json=nueva_tarifa)
            
            if response.status_code in [200, 201]:
                messagebox.showinfo("Éxito", "La tarifa ha sido guardada correctamente.")
                self.refresh_tarifas()
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"No se pudo guardar la tarifa: {response.text}")

        ttk.Button(dialog, text="Guardar", command=guardar_tarifa).pack(pady=10)

    def delete_tarifa(self):
        selected_item = self.tarifas_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una tarifa para eliminar.")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar esta tarifa?"):
            tarifa_id = self.tarifas_tree.item(selected_item)['values'][0]
            response = requests.delete(f'http://127.0.0.1:5000/api/tarifario/{tarifa_id}')
            if response.status_code == 200:
                messagebox.showinfo("Éxito", "La tarifa ha sido eliminada correctamente.")
                self.refresh_tarifas()
            else:
                messagebox.showerror("Error", f"No se pudo eliminar la tarifa: {response.text}")

    def show_add_item_dialog(self):
        self.show_item_dialog()

    def show_edit_item_dialog(self):
        selected_item = self.items_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un item para editar.")
            return
        
        values = self.items_tree.item(selected_item)['values']
        self.show_item_dialog(values)

    def show_item_dialog(self, values=None):
        dialog = tk.Toplevel(self)
        dialog.title("Añadir/Editar Item")
        dialog.geometry("300x150")

        ttk.Label(dialog, text="Nombre:").pack(pady=5)
        nombre_entry = ttk.Entry(dialog)
        nombre_entry.pack(pady=5)

        if values:
            nombre_entry.insert(0, values[1])

        def guardar_item():
            nuevo_item = {'nombre': nombre_entry.get()}
            
            if values:  # Si estamos editando un item existente
                nuevo_item['id'] = values[0]
                response = requests.put(f'http://127.0.0.1:5000/api/items/{nuevo_item["id"]}', json=nuevo_item)
            else:  # Si estamos creando un nuevo item
                response = requests.post('http://127.0.0.1:5000/api/items', json=nuevo_item)
            
            if response.status_code in [200, 201]:
                messagebox.showinfo("Éxito", "El item ha sido guardado correctamente.")
                self.refresh_items()
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"No se pudo guardar el item: {response.text}")

        ttk.Button(dialog, text="Guardar", command=guardar_item).pack(pady=10)

    def delete_item(self):
        selected_item = self.items_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un item para eliminar.")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este item?"):
            item_id = self.items_tree.item(selected_item)['values'][0]
            response = requests.delete(f'http://127.0.0.1:5000/api/items/{item_id}')
            if response.status_code == 200:
                messagebox.showinfo("Éxito", "El item ha sido eliminado correctamente.")
                self.refresh_items()
            else:
                messagebox.showerror("Error", f"No se pudo eliminar el item: {response.text}")

    def show_add_unidad_dialog(self):
        self.show_unidad_dialog()

    def show_edit_unidad_dialog(self):
        selected_unidad = self.unidades_tree.selection()
        if not selected_unidad:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una unidad para editar.")
            return
        
        values = self.unidades_tree.item(selected_unidad)['values']
        self.show_unidad_dialog(values)

    def show_unidad_dialog(self, values=None):
        dialog = tk.Toplevel(self)
        dialog.title("Añadir/Editar Unidad")
        dialog.geometry("300x150")

        ttk.Label(dialog, text="Nombre:").pack(pady=5)
        nombre_entry = ttk.Entry(dialog)
        nombre_entry.pack(pady=5)

        if values:
            nombre_entry.insert(0, values[1])

        def guardar_unidad():
            nueva_unidad = {'nombre': nombre_entry.get()}
            
            if values:  # Si estamos editando una unidad existente
                nueva_unidad['id'] = values[0]
                response = requests.put(f'http://127.0.0.1:5000/api/unidades/{nueva_unidad["id"]}', json=nueva_unidad)
            else:  # Si estamos creando una nueva unidad
                response = requests.post('http://127.0.0.1:5000/api/unidades', json=nueva_unidad)
            
            if response.status_code in [200, 201]:
                messagebox.showinfo("Éxito", "La unidad ha sido guardada correctamente.")
                self.refresh_unidades()
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"No se pudo guardar la unidad: {response.text}")

        ttk.Button(dialog, text="Guardar", command=guardar_unidad).pack(pady=10)

    def delete_unidad(self):
        selected_unidad = self.unidades_tree.selection()
        if not selected_unidad:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una unidad para eliminar.")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar esta unidad?"):
            unidad_id = self.unidades_tree.item(selected_unidad)['values'][0]
            response = requests.delete(f'http://127.0.0.1:5000/api/unidades/{unidad_id}')
            if response.status_code == 200:
                messagebox.showinfo("Éxito", "La unidad ha sido eliminada correctamente.")
                self.refresh_unidades()
            else:
                messagebox.showerror("Error", f"No se pudo eliminar la unidad: {response.text}")

    def show_add_cliente_dialog(self):
        self.show_cliente_dialog()

    def show_edit_cliente_dialog(self):
        selected_cliente = self.clientes_tree.selection()
        if not selected_cliente:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cliente para editar.")
            return
        
        values = self.clientes_tree.item(selected_cliente)['values']
        self.show_cliente_dialog(values)

    def show_cliente_dialog(self, values=None):
        dialog = tk.Toplevel(self)
        dialog.title("Añadir/Editar Cliente")
        dialog.geometry("300x150")

        ttk.Label(dialog, text="Nombre:").pack(pady=5)
        nombre_entry = ttk.Entry(dialog)
        nombre_entry.pack(pady=5)

        if values:
            nombre_entry.insert(0, values[1])

        def guardar_cliente():
            nuevo_cliente = {'nombre': nombre_entry.get()}
            
            if values:  # Si estamos editando un cliente existente
                nuevo_cliente['id'] = values[0]
                response = requests.put(f'http://127.0.0.1:5000/api/clientes/{nuevo_cliente["id"]}', json=nuevo_cliente)
            else:  # Si estamos creando un nuevo cliente
                response = requests.post('http://127.0.0.1:5000/api/clientes', json=nuevo_cliente)
            
            if response.status_code in [200, 201]:
                messagebox.showinfo("Éxito", "El cliente ha sido guardado correctamente.")
                self.refresh_clientes()
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"No se pudo guardar el cliente: {response.text}")

        ttk.Button(dialog, text="Guardar", command=guardar_cliente).pack(pady=10)

    def delete_cliente(self):
        selected_cliente = self.clientes_tree.selection()
        if not selected_cliente:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cliente para eliminar.")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este cliente?"):
            cliente_id = self.clientes_tree.item(selected_cliente)['values'][0]
            response = requests.delete(f'http://127.0.0.1:5000/api/clientes/{cliente_id}')
            if response.status_code == 200:
                messagebox.showinfo("Éxito", "El cliente ha sido eliminado correctamente.")
                self.refresh_clientes()
            else:
                messagebox.showerror("Error", f"No se pudo eliminar el cliente: {response.text}")

    def populate_cliente_combobox(self):
        clientes = self.get_dict_from_data('clientes')
        self.cliente_combobox['values'] = list(clientes.values())

    def on_cliente_selected(self, event):
        self.selected_cliente_id = None
        clientes = self.get_dict_from_data('clientes')
        selected_cliente = self.cliente_combobox.get()
        for cliente_id, cliente_nombre in clientes.items():
            if cliente_nombre == selected_cliente:
                self.selected_cliente_id = cliente_id
                break

    def buscar_tarifas(self):
        if not self.selected_cliente_id:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cliente.")
            return
        
        tarifa_id = self.tarifa_entry.get()
        if not tarifa_id:
            messagebox.showwarning("Advertencia", "Por favor, ingrese un número de tarifa.")
            return
        
        tarifas = self.get_data('tarifario')
        items = self.get_dict_from_data('items')
        unidades = self.get_dict_from_data('unidades')
        clientes = self.get_dict_from_data('clientes')
        
        self.aumentos_tree.delete(*self.aumentos_tree.get_children())
        for tarifa in tarifas:
            if tarifa.get('cliente_id') == self.selected_cliente_id and tarifa.get('id') == int(tarifa_id):
                self.aumentos_tree.insert("", "end", values=(
                    tarifa.get('id', ''),
                    items.get(tarifa.get('item_id'), tarifa.get('item_id', '')),
                    unidades.get(tarifa.get('unidad_id'), tarifa.get('unidad_id', '')),
                    clientes.get(tarifa.get('cliente_id'), tarifa.get('cliente_id', '')),
                    tarifa.get('precio', ''),
                    '',  # Nuevo precio (vacío por ahora)
                    tarifa.get('fecha_vigencia', ''),
                    ''  # Nueva fecha (vacía por ahora)
                ))

    def calcular_aumento(self):
        porcentaje = self.porcentaje_entry.get()
        nueva_fecha = self.nueva_fecha_entry.get()
        
        if not porcentaje or not nueva_fecha:
            messagebox.showwarning("Advertencia", "Por favor, ingrese un porcentaje de aumento y una nueva fecha de vencimiento.")
            return
        
        try:
            porcentaje = float(porcentaje)
            datetime.strptime(nueva_fecha, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Porcentaje de aumento inválido o formato de fecha incorrecto.")
            return
        
        for item in self.aumentos_tree.get_children():
            values = self.aumentos_tree.item(item)['values']
            precio_actual = float(values[4])
            nuevo_precio = precio_actual * (1 + porcentaje / 100)
            self.aumentos_tree.item(item, values=(values[0], values[1], values[2], values[3], values[4], f"{nuevo_precio:.2f}", values[6], nueva_fecha))

    def apply_increase(self):
        for item in self.aumentos_tree.get_children():
            values = self.aumentos_tree.item(item)['values']
            tarifa_id = values[0]
            nuevo_precio = values[5]
            nueva_fecha = values[7]
            
            nueva_tarifa = {
                'precio': nuevo_precio,
                'fecha_vigencia': nueva_fecha
            }
            
            response = requests.put(f'http://127.0.0.1:5000/api/tarifario/{tarifa_id}', json=nueva_tarifa)
            if response.status_code != 200:
                messagebox.showerror("Error", f"No se pudo aplicar el aumento para la tarifa {tarifa_id}: {response.text}")
                return
        
        messagebox.showinfo("Éxito", "El aumento ha sido aplicado correctamente.")
        self.refresh_tarifas()

    def cancel_increase(self):
        self.aumentos_tree.delete(*self.aumentos_tree.get_children())
        self.tarifa_entry.delete(0, tk.END)
        self.porcentaje_entry.delete(0, tk.END)
        self.nueva_fecha_entry.delete(0, tk.END)

    def refresh_home_data(self):
        # Limpiar la caché para obtener datos frescos
        self.cache.clear()
        
        # Refrescar los datos de las tarifas próximas a vencer
        self.refresh_tarifas_vencimiento()
        
        messagebox.showinfo("Éxito", "Los datos han sido refrescados correctamente.")

if __name__ == "__main__":
    app = TarifasApp()
    app.mainloop()

class TarifasApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestión de Tarifas")
        self.geometry("1000x600")
        self.configure(bg='#f7f7f7')
        self.cache = Cache()
        self.selected_cliente_id = None

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, relief="flat", background="#2196F3", foreground="white", font=('Helvetica', 10, 'bold'))
        self.style.configure("TLabel", background='#f7f7f7', font=('Helvetica', 10))
        self.style.configure("TEntry", font=('Helvetica', 10))
        self.style.configure("Treeview", font=('Helvetica', 9), rowheight=25)
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

        self.login_frame = ttk.Frame(self)
        self.main_frame = ttk.Frame(self)

        self.create_login_widgets()

    def create_login_widgets(self):
        self.login_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ttk.Label(self.login_frame, text="Usuario:").pack(pady=5)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.pack(pady=5)

        ttk.Label(self.login_frame, text="Contraseña:").pack(pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self.login_frame, text="Iniciar Sesión", command=self.login).pack(pady=10)

    def login(self):
        if self.username_entry.get() == "admin" and self.password_entry.get() == "admin":
            self.login_frame.pack_forget()
            self.create_main_widgets()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def create_main_widgets(self):
        self.main_frame.pack(expand=True, fill="both")

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.home_frame = ttk.Frame(self.notebook)
        self.tarifas_frame = ttk.Frame(self.notebook)
        self.items_frame = ttk.Frame(self.notebook)
        self.unidades_frame = ttk.Frame(self.notebook)
        self.clientes_frame = ttk.Frame(self.notebook)
        self.aumentos_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.home_frame, text="Inicio")
        self.notebook.add(self.tarifas_frame, text="Tarifas")
        self.notebook.add(self.items_frame, text="Items")
        self.notebook.add(self.unidades_frame, text="Unidades")
        self.notebook.add(self.clientes_frame, text="Clientes")
        self.notebook.add(self.aumentos_frame, text="Aumentos")

        self.create_home_widgets()
        self.create_tarifas_widgets()
        self.create_items_widgets()
        self.create_unidades_widgets()
        self.create_clientes_widgets()
        self.create_aumentos_widgets()

    def create_home_widgets(self):
        ttk.Label(self.home_frame, text="Tarifas próximas a vencer:", font=('Helvetica', 12, 'bold')).pack(pady=10)

        self.tarifas_vencimiento_tree = ttk.Treeview(self.home_frame, columns=("ID", "Item", "Unidad", "Cliente", "Precio", "Fecha"), show="headings")
        self.tarifas_vencimiento_tree.heading("ID", text="ID")
        self.tarifas_vencimiento_tree.heading("Item", text="Item")
        self.tarifas_vencimiento_tree.heading("Unidad", text="Unidad")
        self.tarifas_vencimiento_tree.heading("Cliente", text="Cliente")
        self.tarifas_vencimiento_tree.heading("Precio", text="Precio")
        self.tarifas_vencimiento_tree.heading("Fecha", text="Fecha")
        self.tarifas_vencimiento_tree.pack(expand=True, fill="both", padx=10, pady=10)

        self.refresh_tarifas_vencimiento()

    def create_tarifas_widgets(self):
        self.tarifas_tree = ttk.Treeview(self.tarifas_frame, columns=("ID", "Item", "Unidad", "Cliente", "Precio", "Fecha Inicio", "Fecha Final"), show="headings")
        self.tarifas_tree.heading("ID", text="ID")
        self.tarifas_tree.heading("Item", text="Item")
        self.tarifas_tree.heading("Unidad", text="Unidad")
        self.tarifas_tree.heading("Cliente", text="Cliente")
        self.tarifas_tree.heading("Precio", text="Precio")
        self.tarifas_tree.heading("Fecha Inicio", text="Fecha Inicio")
        self.tarifas_tree.heading("Fecha Final", text="Fecha Final")
        self.tarifas_tree.pack(expand=True, fill="both")

        button_frame = ttk.Frame(self.tarifas_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Agregar", command=self.show_add_tarifa_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", command=self.show_edit_tarifa_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_tarifa).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.refresh_tarifas).pack(side=tk.LEFT, padx=5)

    def create_items_widgets(self):
        self.items_tree = ttk.Treeview(self.items_frame, columns=("ID", "Nombre"), show="headings")
        self.items_tree.heading("ID", text="ID")
        self.items_tree.heading("Nombre", text="Nombre")
        self.items_tree.pack(expand=True, fill="both")

        button_frame = ttk.Frame(self.items_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Agregar", command=self.show_add_item_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", command=self.show_edit_item_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.refresh_items).pack(side=tk.LEFT, padx=5)

    def create_unidades_widgets(self):
        self.unidades_tree = ttk.Treeview(self.unidades_frame, columns=("ID", "Nombre"), show="headings")
        self.unidades_tree.heading("ID", text="ID")
        self.unidades_tree.heading("Nombre", text="Nombre")
        self.unidades_tree.pack(expand=True, fill="both")

        button_frame = ttk.Frame(self.unidades_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Agregar", command=self.show_add_unidad_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", command=self.show_edit_unidad_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_unidad).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.refresh_unidades).pack(side=tk.LEFT, padx=5)

    def create_clientes_widgets(self):
        self.clientes_tree = ttk.Treeview(self.clientes_frame, columns=("ID", "Nombre"), show="headings")
        self.clientes_tree.heading("ID", text="ID")
        self.clientes_tree.heading("Nombre", text="Nombre")
        self.clientes_tree.pack(expand=True, fill="both")

        button_frame = ttk.Frame(self.clientes_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Agregar", command=self.show_add_cliente_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", command=self.show_edit_cliente_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.refresh_clientes).pack(side=tk.LEFT, padx=5)

    def create_aumentos_widgets(self):
        ttk.Label(self.aumentos_frame, text="Cliente:").pack(pady=5)
        self.cliente_combobox = ttk.Combobox(self.aumentos_frame)
        self.cliente_combobox.pack(pady=5)
        self.cliente_combobox.bind("<<ComboboxSelected>>", self.on_cliente_selected)

        ttk.Label(self.aumentos_frame, text="Número de Tarifa:").pack(pady=5)
        self.tarifa_entry = ttk.Entry(self.aumentos_frame)
        self.tarifa_entry.pack(pady=5)

        ttk.Label(self.aumentos_frame, text="Porcentaje de Aumento:").pack(pady=5)
        self.porcentaje_entry = ttk.Entry(self.aumentos_frame)
        self.porcentaje_entry.pack(pady=5)

        ttk.Label(self.aumentos_frame, text="Nueva Fecha de Vencimiento (YYYY-MM-DD):").pack(pady=5)
        self.nueva_fecha_entry = ttk.Entry(self.aumentos_frame)
        self.nueva_fecha_entry.pack(pady=5)

        self.aumentos_tree = ttk.Treeview(self.aumentos_frame, columns=("ID", "Item", "Unidad", "Cliente", "Precio Actual", "Nuevo Precio", "Fecha Actual", "Nueva Fecha"), show="headings")
        self.aumentos_tree.heading("ID", text="ID")
        self.aumentos_tree.heading("Item", text="Item")
        self.aumentos_tree.heading("Unidad", text="Unidad")
        self.aumentos_tree.heading("Cliente", text="Cliente")
        self.aumentos_tree.heading("Precio Actual", text="Precio Actual")
        self.aumentos_tree.heading("Nuevo Precio", text="Nuevo Precio")
        self.aumentos_tree.heading("Fecha Actual", text="Fecha Actual")
        self.aumentos_tree.heading("Nueva Fecha", text="Nueva Fecha")
        self.aumentos_tree.pack(expand=True, fill="both", pady=10)

        button_frame = ttk.Frame(self.aumentos_frame)
        button_frame.pack(pady=10)

        self.buscar_button = ttk.Button(button_frame, text="Buscar", command=self.buscar_tarifas)
        self.buscar_button.pack(side=tk.LEFT, padx=5)

        self.calcular_button = ttk.Button(button_frame, text="Calcular Aumento", command=self.calcular_aumento)
        self.calcular_button.pack(side=tk.LEFT, padx=5)

        self.aplicar_button = ttk.Button(button_frame, text="Aplicar Aumento", command=self.apply_increase)
        self.aplicar_button.pack(side=tk.LEFT, padx=5)

        self.cancelar_button = ttk.Button(button_frame, text="Cancelar", command=self.cancel_increase)
        self.cancelar_button.pack(side=tk.LEFT, padx=5)

        self.populate_cliente_combobox()

    def refresh_tarifas_vencimiento(self):
        tarifas = self.get_data('tarifario')
        items = self.get_dict_from_data('items')
        unidades = self.get_dict_from_data('unidades')
        clientes = self.get_dict_from_data('clientes')
        
        self.tarifas_vencimiento_tree.delete(*self.tarifas_vencimiento_tree.get_children())
        fecha_actual = datetime.now()
        for tarifa in tarifas:
            fecha_vigencia = datetime.strptime(tarifa.get('fecha_vigencia', '2099-12-31'), '%Y-%m-%d')
            if (fecha_vigencia - fecha_actual).days <= 30:
                self.tarifas_vencimiento_tree.insert("", "end", values=(
                    tarifa.get('id', ''),
                    items.get(tarifa.get('item_id'), tarifa.get('item_id', '')),
                    unidades.get(tarifa.get('unidad_id'), tarifa.get('unidad_id', '')),
                    clientes.get(tarifa.get('cliente_id'), tarifa.get('cliente_id', '')),
                    tarifa.get('precio', ''),
                    tarifa.get('fecha_vigencia', '')
                ))

    def refresh_tarifas(self):
        tarifas = self.get_data('tarifario')
        items = self.get_dict_from_data('items')
        unidades = self.get_dict_from_data('unidades')
        clientes = self.get_dict_from_data('clientes')
        
        self.tarifas_tree.delete(*self.tarifas_tree.get_children())
        for tarifa in tarifas:
            self.tarifas_tree.insert("", "end", values=(
                tarifa.get('id', ''),
                items.get(tarifa.get('item_id'), tarifa.get('item_id', '')),
                unidades.get(tarifa.get('unidad_id'), tarifa.get('unidad_id', '')),
                clientes.get(tarifa.get('cliente_id'), tarifa.get('cliente_id', '')),
                tarifa.get('precio', ''),
                tarifa.get('fecha_vigencia_inicio', ''),
                tarifa.get('fecha_vigencia_final', '')
            ))

    def refresh_items(self):
        items = self.get_data('items')
        self.items_tree.delete(*self.items_tree.get_children())
        for item in items:
            self.items_tree.insert("", "end", values=(item['id'], item['nombre']))

    def refresh_unidades(self):
        unidades = self.get_data('unidades')
        self.unidades_tree.delete(*self.unidades_tree.get_children())
        for unidad in unidades:
            self.unidades_tree.insert("", "end", values=(unidad['id'], unidad['nombre']))

    def refresh_clientes(self):
        clientes = self.get_data('clientes')
        self.clientes_tree.delete(*self.clientes_tree.get_children())
        for cliente in clientes:
            self.clientes_tree.insert("", "end", values=(cliente['id'], cliente['nombre']))

    def get_data(self, endpoint):
        cached_data = self.cache.get(endpoint)
        if cached_data:
            return cached_data

        try:
            response = requests.get(f'http://127.0.0.1:5000/api/{endpoint}')
            response.raise_for_status()
            data = response.json()
            self.cache.set(endpoint, data)
            return data
        except requests.RequestException as e:
            messagebox.showerror("Error", f"No se pudo obtener los datos: {str(e)}")
            return []

    def get_dict_from_data(self, endpoint):
        data = self.get_data(endpoint)
        return {item['id']: item['nombre'] for item in data}

    def show_add_tarifa_dialog(self):
        self.show_tarifa_dialog()

    def show_edit_tarifa_dialog(self):
        selected_item = self.tarifas_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una tarifa para editar.")
            return
        
        values = self.tarifas_tree.item(selected_item)['values']
        self.show_tarifa_dialog(values)

    def show_tarifa_dialog(self, values=None):
        dialog = tk.Toplevel(self)
        dialog.title("Añadir/Editar Tarifa")
        dialog.geometry("400x400")

        ttk.Label(dialog, text="ID:").pack(pady=5)
        id_entry = ttk.Entry(dialog)
        id_entry.pack(pady=5)

        ttk.Label(dialog, text="Item:").pack(pady=5)
        item_combobox = ttk.Combobox(dialog)
        item_combobox.pack(pady=5)

        ttk.Label(dialog, text="Unidad:").pack(pady=5)
        unidad_combobox = ttk.Combobox(dialog)
        unidad_combobox.pack(pady=5)

        ttk.Label(dialog, text="Cliente:").pack(pady=5)
        cliente_combobox = ttk.Combobox(dialog)
        cliente_combobox.pack(pady=5)

        ttk.Label(dialog, text="Precio:").pack(pady=5)
        precio_entry = ttk.Entry(dialog)
        precio_entry.pack(pady=5)

        ttk.Label(dialog, text="Fecha Vigencia Inicio (YYYY-MM-DD):").pack(pady=5)
        fecha_vigencia_inicio_entry = ttk.Entry(dialog)
        fecha_vigencia_inicio_entry.pack(pady=5)

        ttk.Label(dialog, text="Fecha Vigencia Final (YYYY-MM-DD):").pack(pady=5)
        fecha_vigencia_final_entry = ttk.Entry(dialog)
        fecha_vigencia_final_entry.pack(pady=5)

        items = self.get_dict_from_data('items')
        unidades = self.get_dict_from_data('unidades')
        clientes = self.get_dict_from_data('clientes')

        item_combobox['values'] = list(items.values())
        unidad_combobox['values'] = list(unidades.values())
        cliente_combobox['values'] = list(clientes.values())

        if values:
            id_entry.insert(0, values[0])
            item_combobox.set(values[1])
            unidad_combobox.set(values[2])
            cliente_combobox.set(values[3])
            precio_entry.insert(0, values[4])
            fecha_vigencia_inicio_entry.insert(0, values[5])
            fecha_vigencia_final_entry.insert(0, values[6])

        def guardar_tarifa():
            nueva_tarifa = {
                'item_id': next(id for id, nombre in items.items() if nombre == item_combobox.get()),
                'unidad_id': next(id for id, nombre in unidades.items() if nombre == unidad_combobox.get()),
                'cliente_id': next(id for id, nombre in clientes.items() if nombre == cliente_combobox.get()),
                'precio': precio_entry.get(),
                'fecha_vigencia_inicio': fecha_vigencia_inicio_entry.get(),
                'fecha_vigencia_final': fecha_vigencia_final_entry.get()
            }
            
            if values:  # Si estamos editando una tarifa existente
                nueva_tarifa['id'] = id_entry.get()
                response = requests.put(f'http://127.0.0.1:5000/api/tarifario/{nueva_tarifa["id"]}', json=nueva_tarifa)
            else:  # Si estamos creando una nueva tarifa
                response = requests.post('http://127.0.0.1:5000/api/tarifario', json=nueva_tarifa)
            
            if response.status_code in [200, 201]:
                messagebox.showinfo("Éxito", "La tarifa ha sido guardada correctamente.")
                self.refresh_tarifas()
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"No se pudo guardar la tarifa: {response.text}")

        ttk.Button(dialog, text="Guardar", command=guardar_tarifa).pack(pady=10)

    def delete_tarifa(self):
        selected_item = self.tarifas_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una tarifa para eliminar.")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar esta tarifa?"):
            tarifa_id = self.tarifas_tree.item(selected_item)['values'][0]
            response = requests.delete(f'http://127.0.0.1:5000/api/tarifario/{tarifa_id}')
            if response.status_code == 200:
                messagebox.showinfo("Éxito", "La tarifa ha sido eliminada correctamente.")
                self.refresh_tarifas()
            else:
                messagebox.showerror("Error", f"No se pudo eliminar la tarifa: {response.text}")

    def show_add_item_dialog(self):
        self.show_item_dialog()

    def show_edit_item_dialog(self):
        selected_item = self.items_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un item para editar.")
            return
        
        values = self.items_tree.item(selected_item)['values']
        self.show_item_dialog(values)

    def show_item_dialog(self, values=None):
        dialog = tk.Toplevel(self)
        dialog.title("Añadir/Editar Item")
        dialog.geometry("300x150")

        ttk.Label(dialog, text="Nombre:").pack(pady=5)
        nombre_entry = ttk.Entry(dialog)
        nombre_entry.pack(pady=5)

        if values:
            nombre_entry.insert(0, values[1])

        def guardar_item():
            nuevo_item = {'nombre': nombre_entry.get()}
            
            if values:  # Si estamos editando un item existente
                nuevo_item['id'] = values[0]
                response = requests.put(f'http://127.0.0.1:5000/api/items/{nuevo_item["id"]}', json=nuevo_item)
            else:  # Si estamos creando un nuevo item
                response = requests.post('http://127.0.0.1:5000/api/items', json=nuevo_item)
            
            if response.status_code in [200, 201]:
                messagebox.showinfo("Éxito", "El item ha sido guardado correctamente.")
                self.refresh_items()
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"No se pudo guardar el item: {response.text}")

        ttk.Button(dialog, text="Guardar", command=guardar_item).pack(pady=10)

    def delete_item(self):
        selected_item = self.items_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un item para eliminar.")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este item?"):
            item_id = self.items_tree.item(selected_item)['values'][0]
            response = requests.delete(f'http://127.0.0.1:5000/api/items/{item_id}')
            if response.status_code == 200:
                messagebox.showinfo("Éxito", "El item ha sido eliminado correctamente.")
                self.refresh_items()
            else:
                messagebox.showerror("Error", f"No se pudo eliminar el item: {response.text}")

    def show_add_unidad_dialog(self):
        self.show_unidad_dialog()

    def show_edit_unidad_dialog(self):
        selected_unidad = self.unidades_tree.selection()
        if not selected_unidad:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una unidad para editar.")
            return
        
        values = self.unidades_tree.item(selected_unidad)['values']
        self.show_unidad_dialog(values)

    def show_unidad_dialog(self, values=None):
        dialog = tk.Toplevel(self)
        dialog.title("Añadir/Editar Unidad")
        dialog.geometry("300x150")

        ttk.Label(dialog, text="Nombre:").pack(pady=5)
        nombre_entry = ttk.Entry(dialog)
        nombre_entry.pack(pady=5)

        if values:
            nombre_entry.insert(0, values[1])

        def guardar_unidad():
            nueva_unidad = {'nombre': nombre_entry.get()}
            
            if values:  # Si estamos editando una unidad existente
                nueva_unidad['id'] = values[0]
                response = requests.put(f'http://127.0.0.1:5000/api/unidades/{nueva_unidad["id"]}', json=nueva_unidad)
            else:  # Si estamos creando una nueva unidad
                response = requests.post('http://127.0.0.1:5000/api/unidades', json=nueva_unidad)
            
            if response.status_code in [200, 201]:
                messagebox.showinfo("Éxito", "La unidad ha sido guardada correctamente.")
                self.refresh_unidades()
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"No se pudo guardar la unidad: {response.text}")

        ttk.Button(dialog, text="Guardar", command=guardar_unidad).pack(pady=10)

    def delete_unidad(self):
        selected_unidad = self.unidades_tree.selection()
        if not selected_unidad:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una unidad para eliminar.")
            return
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar esta unidad?"):
            unidad_id = self.unidades_tree.item(selected_unidad)['values'][0]
            response = requests.delete(f'http://127.0.0.1:5000/api/unidades/{unidad_id}')
            if response.status_code == 200:
                messagebox.showinfo("Éxito", "La unidad ha sido eliminada correctamente.")
                self.refresh_unidades()
            else:
                messagebox.showerror("Error", f"No se pudo eliminar la unidad: {response.text}")

    def show_add_cliente_dialog(self):
        self.show_cliente_dialog()

    def show_edit_cliente_dialog(self):
        selected_cliente = self.clientes_tree.selection()
        if not selected_cliente:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cliente para editar.")
            return
        values = self.clientes_tree.item(selected_cliente)['values']
        self.show_cliente_dialog(values)

    def show_cliente_dialog(self, values=None):
        dialog = tk.Toplevel(self)
        dialog.title("Añadir/Editar Cliente")
        dialog.geometry("300x150")

        ttk.Label(dialog, text="Nombre:").pack(pady=5)
        nombre_entry = ttk.Entry(dialog)
        nombre_entry.pack(pady=5)

        if values:
            nombre_entry.insert(0, values[1])

        def guardar_cliente():
            nuevo_cliente = {'nombre': nombre_entry.get()}
            if values:  # Si estamos editando un cliente existente
                nuevo_cliente['id'] = values[0]
                response = requests.put(f'http://127.0.0.1:5000/api/clientes/{nuevo_cliente["id"]}', json=nuevo_cliente)
            else:  # Si estamos creando un nuevo cliente
                response = requests.post('http://127.0.0.1:5000/api/clientes', json=nuevo_cliente)
            
            if response.status_code in [200, 201]:
                messagebox.showinfo("Éxito", "El cliente ha sido guardado correctamente.")
                self.refresh_clientes()
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"No se pudo guardar el cliente: {response.text}")

        ttk.Button(dialog, text="Guardar", command=guardar_cliente).pack(pady=10)

    def delete_cliente(self):
        selected_cliente = self.clientes_tree.selection()
        if not selected_cliente:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cliente para eliminar.")
            return
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este cliente?"):
            cliente_id = self.clientes_tree.item(selected_cliente)['values'][0]
            response = requests.delete(f'http://127.0.0.1:5000/api/clientes/{cliente_id}')
            if response.status_code == 200:
                messagebox.showinfo("Éxito", "El cliente ha sido eliminado correctamente.")
                self.refresh_clientes()
            else:
                messagebox.showerror("Error", f"No se pudo eliminar el cliente: {response.text}")

    def populate_cliente_combobox(self):
        clientes = self.get_dict_from_data('clientes')
        self.cliente_combobox['values'] = list(clientes.values())

    def on_cliente_selected(self, event):
        selected_cliente = self.cliente_combobox.get()
        clientes = self.get_dict_from_data('clientes')
        self.selected_cliente_id = next((id for id, nombre in clientes.items() if nombre == selected_cliente), None)

    def buscar_tarifas(self):
        cliente_id = self.selected_cliente_id
        tarifa_id = self.tarifa_entry.get()
        if cliente_id:
            tarifas = self.get_data(f'tarifario?cliente_id={cliente_id}')
        elif tarifa_id:
            tarifas = [self.get_data(f'tarifario/{tarifa_id}')]
        else:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cliente o ingrese un número de tarifa.")
            return

        items = self.get_dict_from_data('items')
        unidades = self.get_dict_from_data('unidades')
        clientes = self.get_dict_from_data('clientes')
        
        self.aumentos_tree.delete(*self.aumentos_tree.get_children())
        for tarifa in tarifas:
            self.aumentos_tree.insert("", "end", values=(
                tarifa.get('id', ''),
                items.get(tarifa.get('item_id'), tarifa.get('item_id', '')),
                unidades.get(tarifa.get('unidad_id'), tarifa.get('unidad_id', '')),
                clientes.get(tarifa.get('cliente_id'), tarifa.get('cliente_id', '')),
                tarifa.get('precio', ''),
                '',
                tarifa.get('fecha_vigencia_inicio', ''),
                tarifa.get('fecha_vigencia_final', '')
            ))

    def calcular_aumento(self):
        try:
            porcentaje = float(self.porcentaje_entry.get()) / 100
            nueva_fecha = self.nueva_fecha_entry.get()
            for item in self.aumentos_tree.get_children():
                valores = self.aumentos_tree.item(item)['values']
                precio_actual = float(valores[4])
                nuevo_precio = precio_actual * (1 + porcentaje)
                self.aumentos_tree.item(item, values=(
                    valores[0], valores[1], valores[2], valores[3],
                    valores[4], f"{nuevo_precio:.2f}", valores[6], nueva_fecha
                ))
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese un porcentaje válido y una fecha en formato YYYY-MM-DD.")

    def apply_increase(self):
        result = messagebox.askyesno("Confirmar", "¿Está seguro de que desea aplicar el aumento?")
        if result:
            tarifas_actualizadas = []
            for item in self.aumentos_tree.get_children():
                valores = self.aumentos_tree.item(item)['values']
                if valores[5] and valores[7]:  # Si hay un nuevo precio y una nueva fecha calculados
                    tarifas_actualizadas.append({
                        'id': valores[0],
                        'precio': float(valores[5]),
                        'fecha_vigencia_inicio': valores[6],
                        'fecha_vigencia_final': valores[7]
                    })
            
            for tarifa in tarifas_actualizadas:
                response = requests.put(f'http://127.0.0.1:5000/api/tarifario/{tarifa["id"]}', json=tarifa)
                if response.status_code != 200:
                    messagebox.showerror("Error", f"No se pudo actualizar la tarifa {tarifa['id']}: {response.text}")
                    return
            
            messagebox.showinfo("Éxito", "Los aumentos han sido aplicados correctamente.")
            self.refresh_tarifas()
            self.buscar_tarifas()  # Actualizar la vista de aumentos

    def cancel_increase(self):
        self.cliente_combobox.set('')
        self.tarifa_entry.delete(0, tk.END)
        self.porcentaje_entry.delete(0, tk.END)
        self.nueva_fecha_entry.delete(0, tk.END)
        self.aumentos_tree.delete(*self.aumentos_tree.get_children())
        messagebox.showinfo("Cancelar", "El aumento ha sido cancelado.")

if __name__ == "__main__":
    app = TarifasApp()
    app.mainloop()