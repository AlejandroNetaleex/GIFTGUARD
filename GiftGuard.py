import os
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog, Toplevel
from PIL import Image, ImageTk
import psutil
import shutil
import threading
import webbrowser

# Ruta del directorio del script actual o directorio de ejecución si está empaquetado
if getattr(sys, 'frozen', False):
    ruta_script = sys._MEIPASS  # Directorio temporal de PyInstaller
else:
    ruta_script = os.path.dirname(os.path.abspath(__file__))

# Carpeta de cuarentena en el mismo directorio que el script
carpeta_cuarentena = os.path.join(ruta_script, "cuarentena")
if not os.path.exists(carpeta_cuarentena):
    os.makedirs(carpeta_cuarentena)

# Lista de extensiones sospechosas y carpetas críticas
extensiones_sospechosas = ['.exe', '.bat', '.vbs', '.scr', '.cmd']
carpetas_criticas = [
    os.path.expanduser("~\\Downloads"),
    os.path.expanduser("~\\Documents"),
    os.path.expanduser("~\\Music"),
    os.path.expanduser("~\\Videos"),
    os.path.expanduser("~\\Pictures")
]

# Colores definidos
color_azul_fondo = "#42C0FB"
color_verde = "#7EBF3B"
color_naranja = "#FFA500"
color_rojo = "#FF6347"
color_gris = "#A9A9A9"
color_azul_claro = "#349ACD"
color_texto = "#FFFFFF"


def ruta_recurso(rel_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, rel_path)
    return rel_path



# Rutas de imágenes para logo y GIF de carga
logo_path = ruta_recurso("logo.png")
gif_path = ruta_recurso("cargando.gif")

# Función para mostrar una ventana de carga con el GIF animado
def mostrar_cargando():
    ventana_carga = Toplevel(ventana)
    ventana_carga.title("Cargando...")
    ventana_carga.geometry("200x200")
    ventana_carga.resizable(False, False)
    ventana_carga.grab_set()

    gif_img = Image.open(gif_path)
    frames = []
    try:
        while True:
            frames.append(ImageTk.PhotoImage(gif_img.copy()))
            gif_img.seek(len(frames))
    except EOFError:
        pass

    spinner = tk.Label(ventana_carga)
    spinner.pack()

    def animar_gif(ind):
        frame = frames[ind]
        spinner.config(image=frame)
        ventana_carga.update_idletasks()
        ventana_carga.after(100, animar_gif, (ind + 1) % len(frames))

    animar_gif(0)
    return ventana_carga

# Función para ejecutar y mostrar comandos con ventana de carga
def ejecutar_con_carga(func, *args):
    ventana_carga = mostrar_cargando()

    def wrapper():
        func(*args)
        ventana_carga.destroy()
    
    threading.Thread(target=wrapper).start()

# Función para ejecutar comandos en el área de salida
def ejecutar_comando(comando, descripcion):
    output_area.insert(tk.END, f"{descripcion}:\n")
    resultado = os.popen(comando).read()
    output_area.insert(tk.END, resultado + "\n")
    output_area.see(tk.END)

# Función para escanear archivos sospechosos
def escaneo_archivos_sospechosos():
    archivos_sospechosos = []
    for carpeta in carpetas_criticas:
        for root, dirs, files in os.walk(carpeta):
            for file in files:
                if any(file.endswith(ext) for ext in extensiones_sospechosas):
                    archivo_sospechoso = os.path.join(root, file)
                    
                    respuesta = messagebox.askyesno(
                        "Archivo Sospechoso Encontrado",
                        f"Se encontró un archivo sospechoso:\n{archivo_sospechoso}\n\n¿Deseas moverlo a la cuarentena?"
                    )
                    if respuesta:
                        mover_a_cuarentena(archivo_sospechoso)
                    else:
                        output_area.insert(tk.END, f"Archivo no movido a cuarentena: {archivo_sospechoso}\n")
                        output_area.see(tk.END)

# Función para mover archivos sospechosos a la carpeta de cuarentena
def mover_a_cuarentena(filepath):
    try:
        filename = os.path.basename(filepath)
        shutil.move(filepath, os.path.join(carpeta_cuarentena, filename))
        messagebox.showinfo("Cuarentena", f"Archivo movido a cuarentena: {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo mover el archivo a cuarentena: {e}")

# Función para abrir el formulario de Google para generar un ticket
def generar_ticket():
    url_formulario = "https://forms.gle/xsMBrsNkps5m9ttAA"
    webbrowser.open(url_formulario)

# Función para limpiar el área de salida
def limpiar_pantalla():
    output_area.delete('1.0', tk.END)

# Función para mostrar el menú de opciones de mantenimiento preventivo
def mostrar_menu_mantenimiento():
    limpiar_frame()
    btn_mantenimiento.pack(fill="x", pady=5)
    btn_informacion.pack(fill="x", pady=5)
    btn_red.pack(fill="x", pady=5)
    btn_mantenimiento_red.pack(fill="x", pady=5)
    btn_regresar.pack(fill="x", pady=5)
    btn_limpiar.pack(fill="x", pady=5)

# Función para desplegar botones individuales para cada comando de mantenimiento
def mostrar_mantenimiento():
    limpiar_frame()
    comandos_mantenimiento = [
        ("Escaneo y reparación de archivos del sistema", "sfc /scannow"),
        ("Comprobar disco en C", "chkdsk C:"),
        ("Desfragmentar disco en C", "defrag C: /O"),
        ("Liberador de espacio en disco", "cleanmgr /sagerun:1"),
        ("Eliminar archivos temporales", "del /q/f/s %TEMP%\\*"),
        ("Reparar imagen del sistema", "DISM /Online /Cleanup-Image /RestoreHealth"),
        ("Borrar archivos de Prefetch", "del /s /q C:\\Windows\\Prefetch\\*"),
        ("Liberar memoria en uso", "EmptyStandbyList.exe workingsets"),
        ("Vaciar Papelera de reciclaje", "rd /s /q %systemdrive%\\$Recycle.bin"),
        ("Reiniciar sistema", "shutdown /r /t 1")
    ]
    for descripcion, comando in comandos_mantenimiento:
        btn = tk.Button(frame_nav, text=descripcion, command=lambda cmd=comando, desc=descripcion: ejecutar_con_carga(ejecutar_comando, cmd, desc), fg=color_texto, bg=color_verde)
        btn.pack(fill="x", pady=2)
    btn_regresar_mantenimiento.pack(fill="x", pady=5)
    btn_limpiar.pack(fill="x", pady=5)

# Función para desplegar botones individuales para cada comando de información
def mostrar_informacion():
    limpiar_frame()
    comandos_informacion = [
        ("Información general del sistema", "systeminfo"),
        ("Espacio en disco", "wmic logicaldisk get size,freespace,caption"),
        ("Procesos activos", "tasklist"),
        ("Memoria física total y disponible", 'systeminfo | findstr /C:"Total Physical Memory" /C:"Available Physical Memory"'),
        ("Modelo y velocidad del procesador", "wmic cpu get name,CurrentClockSpeed"),
        ("Detalles del sistema operativo", "wmic os get Caption,OSArchitecture,Version"),
        ("Unidades de disco", "wmic diskdrive get model,name,size"),
        ("Eventos recientes del sistema", "wevtutil qe System /f:text /c:10 /rd:true"),
        ("Controladores instalados", "driverquery"),
        ("Historial de comandos", "doskey /history")
    ]
    for descripcion, comando in comandos_informacion:
        btn = tk.Button(frame_nav, text=descripcion, command=lambda cmd=comando, desc=descripcion: ejecutar_con_carga(ejecutar_comando, cmd, desc), fg=color_texto, bg=color_azul_claro)
        btn.pack(fill="x", pady=2)
    btn_regresar_mantenimiento.pack(fill="x", pady=5)
    btn_limpiar.pack(fill="x", pady=5)

# Función para desplegar botones individuales para cada comando de red
def mostrar_red():
    limpiar_frame()
    comandos_red = [
        ("Configuración de red completa", "ipconfig /all"),
        ("Adaptadores de red", "netsh interface show interface"),
        ("Tabla de rutas de red", "route print"),
        ("Tabla ARP", "arp -a"),
        ("Conexiones de red activas", "netstat -an"),
        ("Perfiles de Wi-Fi", "netsh wlan show profiles"),
        ("Detalles de conexión Wi-Fi", "netsh wlan show interfaces"),
        ("Probar conectividad (ping)", "ping google.com"),
        ("Ruta a Google (tracert)", "tracert google.com"),
        ("Estadísticas de NetBIOS", "nbtstat -n")
    ]
    for descripcion, comando in comandos_red:
        btn = tk.Button(frame_nav, text=descripcion, command=lambda cmd=comando, desc=descripcion: ejecutar_con_carga(ejecutar_comando, cmd, desc), fg=color_texto, bg=color_naranja)
        btn.pack(fill="x", pady=2)
    btn_regresar_mantenimiento.pack(fill="x", pady=5)
    btn_limpiar.pack(fill="x", pady=5)

# Función para desplegar botones individuales para cada comando de mantenimiento de red
def mostrar_mantenimiento_red():
    limpiar_frame()
    comandos_mantenimiento_red = [
        ("Limpiar caché de DNS", "ipconfig /flushdns"),
        ("Renovar dirección IP", "ipconfig /renew"),
        ("Liberar dirección IP", "ipconfig /release"),
        ("Reiniciar Winsock", "netsh winsock reset"),
        ("Reiniciar TCP/IP", "netsh int ip reset"),
        ("Restaurar firewall a predeterminado", "netsh advfirewall reset"),
        ("Limpiar caché ARP", "netsh interface ip delete arpcache"),
        ("Deshabilitar heurística de TCP", "netsh int tcp set heuristics disabled"),
        ("Restablecer ajuste automático de TCP", "netsh int tcp set global autotuninglevel=normal"),
        ("Habilitar TCP Chimney", "netsh int tcp set global chimney=enabled")
    ]
    for descripcion, comando in comandos_mantenimiento_red:
        btn = tk.Button(frame_nav, text=descripcion, command=lambda cmd=comando, desc=descripcion: ejecutar_con_carga(ejecutar_comando, cmd, desc), fg=color_texto, bg=color_rojo)
        btn.pack(fill="x", pady=2)
    btn_regresar_mantenimiento.pack(fill="x", pady=5)
    btn_limpiar.pack(fill="x", pady=5)

# Limpia los botones de frame_nav
def limpiar_frame():
    for widget in frame_nav.winfo_children():
        widget.pack_forget()

# Función para activar modo de mantenimiento preventivo y desplegar opciones
def activar_mantenimiento():
    clave = simpledialog.askstring("Clave de Acceso", "Ingrese la clave para acceder al modo de Mantenimiento:")
    if clave == "4159":
        output_area.delete('1.0', tk.END)
        output_area.insert(tk.END, "Modo Mantenimiento Preventivo y Correctivo Activado.\n")
        mostrar_menu_mantenimiento()
    else:
        messagebox.showerror("Error", "Clave incorrecta.")

# Función para regresar al modo Antivirus
def regresar_a_antivirus():
    limpiar_frame()
    btn_escaneo_archivos_sospechosos.pack(fill="x", pady=10, ipadx=20, ipady=10)
    btn_generar_ticket.pack(fill="x", pady=5)
    btn_activar_mantenimiento.pack(fill="x", pady=5)
    btn_limpiar.pack(fill="x", pady=5)
    output_area.delete('1.0', tk.END)
    output_area.insert(tk.END, "Modo Antivirus Activado.\n")

# Interfaz gráfica
ventana = tk.Tk()
ventana.title("GiftGuard - Antivirus Ligero")
ventana.geometry("800x600")
ventana.configure(bg=color_azul_fondo)

# Logo y título
frame_header = tk.Frame(ventana, bg=color_azul_fondo)
frame_header.pack(side="top", fill="x", padx=10, pady=10)
logo_img = Image.open(logo_path)
logo_img = logo_img.resize((100, 100), Image.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo_img)
logo_label = tk.Label(frame_header, image=logo_photo, bg=color_azul_fondo)
logo_label.pack(side="left", padx=5)
title_label = tk.Label(frame_header, text="GiftGuard", font=("Arial", 20, "bold"), bg=color_azul_fondo, fg="white")
title_label.pack(side="left", padx=10)

# Área de salida
output_area = scrolledtext.ScrolledText(ventana, width=50, height=20, wrap="word", bg="white", fg="black")
output_area.pack(side="right", fill="both", expand=True)

# Botones de funcionalidades de antivirus y mantenimiento
frame_nav = tk.Frame(ventana, width=200, bg=color_azul_fondo)
frame_nav.pack(side="left", fill="y")

# Configuración de botones principales
btn_escaneo_archivos_sospechosos = tk.Button(frame_nav, text="Escaneo de Archivos Sospechosos", command=lambda: ejecutar_con_carga(escaneo_archivos_sospechosos), fg=color_texto, bg=color_verde, font=("Arial", 14, "bold"))
btn_generar_ticket = tk.Button(frame_nav, text="Generar Ticket", command=generar_ticket, fg=color_texto, bg=color_azul_claro, font=("Arial", 10))
btn_activar_mantenimiento = tk.Button(frame_nav, text="Mantenimiento Preventivo y Correctivo", command=activar_mantenimiento, fg=color_texto, bg=color_naranja)
btn_limpiar = tk.Button(frame_nav, text="Limpiar Pantalla", command=limpiar_pantalla, fg=color_texto, bg=color_gris)

# Empaquetado de los botones principales
btn_escaneo_archivos_sospechosos.pack(fill="x", pady=10, ipadx=20, ipady=10)
btn_generar_ticket.pack(fill="x", pady=5)
btn_activar_mantenimiento.pack(fill="x", pady=5)
btn_limpiar.pack(fill="x", pady=5)

# Botones de opciones de mantenimiento (ocultos inicialmente)
btn_mantenimiento = tk.Button(frame_nav, text="Ejecutar Mantenimiento", command=mostrar_mantenimiento, fg=color_texto, bg=color_rojo)
btn_informacion = tk.Button(frame_nav, text="Consulta de Información", command=mostrar_informacion, fg=color_texto, bg=color_azul_claro)
btn_red = tk.Button(frame_nav, text="Consulta de Red", command=mostrar_red, fg=color_texto, bg=color_naranja)
btn_mantenimiento_red = tk.Button(frame_nav, text="Mantenimiento de Red", command=mostrar_mantenimiento_red, fg=color_texto, bg=color_rojo)
btn_regresar = tk.Button(frame_nav, text="Regresar al Antivirus", command=regresar_a_antivirus, fg=color_texto, bg=color_gris)
btn_regresar_mantenimiento = tk.Button(frame_nav, text="Regresar a Mantenimiento", command=mostrar_menu_mantenimiento, fg=color_texto, bg=color_gris)

ventana.mainloop()
