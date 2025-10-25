# Lógica y datos de usuarios con asignación de tiendas - MODO BETA
import streamlit as st

# CONFIGURACIÓN BETA: Acepta cualquier contraseña
MODO_BETA = True

# Estructura: usuario -> {'rol': str, 'tienda': str}
usuarios = {
    'empleado1': {'rol': 'empleado', 'tienda': 'T001'},  # Seminario
    'empleado2': {'rol': 'empleado', 'tienda': 'T002'},  # Mcal Lopez
    'empleado3': {'rol': 'empleado', 'tienda': 'T001'},  # Seminario
    'admin1': {'rol': 'administrador', 'tienda': 'ALL'},  # Acceso a todas las tiendas
    'admin': {'rol': 'administrador', 'tienda': 'ALL'},   # Usuario admin adicional
    'empleado': {'rol': 'empleado', 'tienda': 'T001'},   # Usuario empleado genérico
}

def login(usuario, contrasena):
    """
    Función de login que acepta usuario y contraseña.
    En modo BETA, cualquier contraseña es válida.
    
    Returns:
        dict: {"exito": bool, "rol": str, "tienda": str, "mensaje": str}
    """
    if not usuario:
        return {
            "exito": False,
            "rol": None,
            "tienda": None,
            "mensaje": "Debe ingresar un usuario"
        }
    
    if not contrasena:
        return {
            "exito": False,
            "rol": None,
            "tienda": None,
            "mensaje": "Debe ingresar una contraseña"
        }
    
    # Verificar si el usuario existe
    if usuario in usuarios:
        user_info = usuarios[usuario]
        
        # En modo BETA, cualquier contraseña es válida
        if MODO_BETA:
            return {
                "exito": True,
                "rol": user_info['rol'],
                "tienda": user_info['tienda'],
                "mensaje": f"Login exitoso - MODO BETA (cualquier contraseña válida)"
            }
        else:
            # Aquí iría la verificación real de contraseña cuando no esté en beta
            # Por ahora, como estamos en beta, siempre es válida
            return {
                "exito": True,
                "rol": user_info['rol'],
                "tienda": user_info['tienda'],
                "mensaje": "Login exitoso"
            }
    else:
        return {
            "exito": False,
            "rol": None,
            "tienda": None,
            "mensaje": f"Usuario '{usuario}' no reconocido. Usuarios disponibles: {', '.join(usuarios.keys())}"
        }

def logout():
    """Función para cerrar sesión"""
    # Limpiar todas las variables de sesión relacionadas con autenticación
    keys_to_clear = [
        'usuario_autenticado',
        'rol_usuario', 
        'tienda_usuario',
        'usuario_actual',
        'rol_actual',
        'tienda_actual'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            st.session_state[key] = None