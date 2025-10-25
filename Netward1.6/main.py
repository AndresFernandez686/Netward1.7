import streamlit as st
import json
import sys
import os
from datetime import datetime, timedelta

# Añadir el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Importar módulos locales
from auth import login
from persistencia import cargar_inventario, guardar_inventario, cargar_historial, guardar_historial, cargar_catalogo_delivery, guardar_venta_delivery, cargar_ventas_delivery
from ui_empleado import empleado_inventario_ui, empleado_delivery_ui
from ui_admin import admin_inventario_ui, admin_historial_ui
from config_tiendas import cargar_config_tiendas, obtener_nombre_tienda, mostrar_panel_configuracion_tiendas

def inicializar_estructura_datos():
    """Inicializa la estructura de datos para multi-tienda"""
    try:
        with open('inventario.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    
    # Verificar si ya tiene estructura multi-tienda
    if "inventario_por_tienda" not in data:
        # Migrar datos existentes a estructura multi-tienda
        inventario_existente = {}
        for key, value in data.items():
            if key in ["Impulsivo", "Por Kilos", "Extras"] and isinstance(value, dict):
                inventario_existente[key] = value
        
        # Crear nueva estructura
        data = {
            "inventario_por_tienda": {
                "T001": inventario_existente if inventario_existente else {
                    "Impulsivo": {},
                    "Por Kilos": {},
                    "Extras": {}
                },
                "T002": {
                    "Impulsivo": {},
                    "Por Kilos": {},
                    "Extras": {}
                }
            },
            "configuracion": {
                "tienda_default": "T001",
                "version": "1.6",
                "tiendas": {
                    "T001": {
                        "id": "T001",
                        "nombre": "Seminario",
                        "direccion": "Dirección no especificada",
                        "activa": True,
                        "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
                    },
                    "T002": {
                        "id": "T002",
                        "nombre": "Mcal Lopez",
                        "direccion": "Dirección no especificada",
                        "activa": True,
                        "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
                    }
                }
            }
        }
        
        # Guardar nueva estructura
        with open('inventario.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    
    else:
        # Verificar y agregar tiendas si no existen en la configuración
        configuracion = data.get("configuracion", {})
        tiendas = configuracion.get("tiendas", {})
        
        # Asegurar que T001 esté configurada como Seminario
        if "T001" not in tiendas:
            tiendas["T001"] = {
                "id": "T001",
                "nombre": "Seminario",
                "direccion": "Dirección no especificada",
                "activa": True,
                "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
            }
        
        # Asegurar que T002 esté configurada como Mcal Lopez
        if "T002" not in tiendas:
            tiendas["T002"] = {
                "id": "T002",
                "nombre": "Mcal Lopez",
                "direccion": "Dirección no especificada",
                "activa": True,
                "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
            }
        
        # Actualizar configuración
        configuracion["tiendas"] = tiendas
        data["configuracion"] = configuracion
        
        # Guardar cambios
        with open('inventario.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    
    return data

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="Sistema Netward",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personalizado para mejorar la apariencia
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            color: #1f77b4;
            margin-bottom: 2rem;
        }
        .stAlert > div {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .metric-container {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        
        /* Spinner de carga personalizado */
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-container {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #1f77b4;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin-right: 15px;
        }
        
        .loading-text {
            font-size: 1.2rem;
            color: #1f77b4;
            font-weight: 500;
        }
        
        /* Animación de pulso para el carrito */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .cart-badge {
            animation: pulse 2s ease-in-out infinite;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Inicializar estructura de datos
    inicializar_estructura_datos()
    
    # Inicializar estado de sesión
    if 'usuario_actual' not in st.session_state:
        st.session_state.usuario_actual = None
        st.session_state.rol_actual = None
        st.session_state.tienda_actual = None
    
    # Panel de login
    if st.session_state.usuario_actual is None:
        st.markdown('<div class="main-header">🏪 Sistema Netward - Gestión de Inventarios</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Iniciar Sesión")
            
            # Mensaje de modo beta
            st.info("🚧 **MODO BETA** - Cualquier contraseña es válida para testing")
            
            # Mostrar usuarios disponibles
            st.markdown("**Usuarios disponibles:**")
            st.markdown("• `empleado1` - Empleado Seminario")
            st.markdown("• `empleado2` - Empleado Mcal Lopez") 
            st.markdown("• `empleado3` - Empleado Seminario")
            st.markdown("• `admin1` - Administrador")
            st.markdown("• `admin` - Administrador")
            st.markdown("• `empleado` - Empleado genérico")
            
            # Formulario de login
            with st.form("login_form"):
                usuario = st.text_input("Usuario:", placeholder="Ingresa tu usuario")
                contrasena = st.text_input("Contraseña:", type="password", placeholder="Cualquier contraseña (modo beta)")
                submit_button = st.form_submit_button("Ingresar", use_container_width=True)
                
                if submit_button:
                    if usuario and contrasena:
                        resultado_login = login(usuario, contrasena)
                        if resultado_login["exito"]:
                            st.session_state.usuario_actual = usuario
                            st.session_state.rol_actual = resultado_login["rol"]
                            st.session_state.tienda_actual = resultado_login["tienda"]
                            st.success(f"¡Bienvenido, {usuario}! - {resultado_login['mensaje']}")
                            st.rerun()
                        else:
                            st.error(resultado_login["mensaje"])
                    else:
                        st.warning("Por favor, completa todos los campos")
        
        # Información del sistema
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("**👥 Empleados**\nGestión rápida de inventario")
        with col2:
            st.info("**👨‍💼 Administradores**\nGestión y control total")
        with col3:
            st.info("**🏪 Multi-tienda**\nDatos independientes por sucursal")
    
    else:
        # Panel principal después del login
        usuario = st.session_state.usuario_actual
        rol = st.session_state.rol_actual
        tienda_id = st.session_state.tienda_actual
        
        # Header con información del tienda
        col1, col2 = st.columns([2, 0.5])
        with col1:
            tienda_nombre = obtener_nombre_tienda(tienda_id)
            st.markdown(f"## 🏪 Sistema Netward - {tienda_nombre}")
        with col2:
            # Botón de salida con icono de flecha
            if st.button("➜", help="Cerrar sesión", use_container_width=True, key="logout_btn"):
                st.session_state.mostrar_confirmacion_logout = True
        
        # Modal de confirmación de logout
        if st.session_state.get("mostrar_confirmacion_logout", False):
            col_modal1, col_modal2, col_modal3 = st.columns([1, 2, 1])
            with col_modal2:
                st.warning("⚠️ ¿Seguro que desea salir?")
                col_aceptar, col_cancelar = st.columns(2)
                with col_aceptar:
                    if st.button("✅ ACEPTAR", use_container_width=True):
                        st.session_state.usuario_actual = None
                        st.session_state.rol_actual = None
                        st.session_state.tienda_actual = None
                        st.session_state.mostrar_confirmacion_logout = False
                        st.rerun()
                with col_cancelar:
                    if st.button("❌ CANCELAR", use_container_width=True):
                        st.session_state.mostrar_confirmacion_logout = False
                        st.rerun()
        
        st.markdown("---")
        
        # Interfaz según el rol
        if rol == "empleado":
            st.markdown("### 📦 Panel de Empleado")
            
            # Pestañas para empleado
            tab_inventario, tab_delivery = st.tabs(["📦 Inventario", "🚚 Delivery"])
            
            with tab_inventario:
                try:
                    # Cargar inventario de la tienda del empleado
                    inventario = cargar_inventario(tienda_id)
                    opciones_valde = ["500g", "1kg", "2kg", "5kg"]
                    
                    empleado_inventario_ui(
                        inventario=inventario,
                        usuario=usuario,
                        opciones_valde=opciones_valde,
                        guardar_inventario=lambda inv: guardar_inventario(inv, tienda_id),
                        guardar_historial=guardar_historial,
                        tienda_id=tienda_id
                    )
                except Exception as e:
                    st.error(f"Error en interfaz de inventario: {str(e)}")
            
            with tab_delivery:
                try:
                    empleado_delivery_ui(
                        usuario=usuario,
                        cargar_catalogo_delivery=cargar_catalogo_delivery,
                        guardar_venta_delivery=guardar_venta_delivery,
                        cargar_ventas_delivery=cargar_ventas_delivery
                    )
                except Exception as e:
                    st.error(f"Error en interfaz de delivery: {str(e)}")
            
        elif rol == "administrador":
            if "admin_menu_option" not in st.session_state:
                st.session_state.admin_menu_option = "tiendas"
            
            menu_opciones = {
                "Tiendas": "tiendas",
                "Historial": "historial",
                "Configuraciones": "configuraciones"
            }
            
            col_menu = st.columns([1])[0]
            with col_menu:
                opcion_seleccionada = st.selectbox(
                    "Seleccionar opcion:",
                    options=list(menu_opciones.keys()),
                    index=list(menu_opciones.values()).index(st.session_state.admin_menu_option),
                    key="admin_menu_select"
                )
                st.session_state.admin_menu_option = menu_opciones[opcion_seleccionada]
            
            # Cargar configuracion de tiendas
            config_tiendas = cargar_config_tiendas()
            tiendas_opciones = {tid: info["nombre"] for tid, info in config_tiendas.items()}
            
            # VISTA PRINCIPAL: TIENDAS - Inventario (por defecto)
            if st.session_state.admin_menu_option == "tiendas":
                st.markdown("### 📦 Tiendas - Inventario")
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    tienda_admin_id = st.selectbox(
                        "Seleccionar tienda:",
                        options=list(tiendas_opciones.keys()),
                        format_func=lambda x: tiendas_opciones[x],
                        key="admin_tienda_selector_tiendas"
                    )
                
                with col2:
                    st.info(f"📍 Visualizando datos de: **{tiendas_opciones[tienda_admin_id]}**")
                
                try:
                    inventario_admin = cargar_inventario(tienda_admin_id)
                    admin_inventario_ui(inventario_admin, tienda_admin_id)
                except Exception as e:
                    st.error(f"Error al cargar inventario: {str(e)}")
                    st.info("Verifica que el archivo de inventario esté correctamente configurado")
            
            # OPCIÓN DEL MENÚ: HISTORIAL
            elif st.session_state.admin_menu_option == "historial":
                st.markdown("### 📊 Historial")
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    tienda_admin_id = st.selectbox(
                        "Seleccionar tienda:",
                        options=list(tiendas_opciones.keys()),
                        format_func=lambda x: tiendas_opciones[x],
                        key="admin_tienda_selector_historial"
                    )
                
                with col2:
                    st.info(f"📍 Visualizando datos de: **{tiendas_opciones[tienda_admin_id]}**")
                
                try:
                    historial_data = cargar_historial(tienda_admin_id)
                    admin_historial_ui(historial_data)
                except Exception as e:
                    st.error(f"Error al cargar historial: {str(e)}")
                    st.info("Verifica que el archivo de historial esté correctamente configurado")
            
            # OPCIÓN DEL MENÚ: CONFIGURACIONES
            elif st.session_state.admin_menu_option == "configuraciones":
                st.markdown("### ⚙️ Configuraciones de Tiendas")
                try:
                    mostrar_panel_configuracion_tiendas()
                except Exception as e:
                    st.error(f"Error en configuración de tiendas: {str(e)}")
                    st.info("Verifica que el archivo de inventario esté correctamente configurado")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Se ha producido un error: {str(e)}")
        if st.button("Reintentar"):
            st.rerun()