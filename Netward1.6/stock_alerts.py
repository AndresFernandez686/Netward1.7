# Sistema de Alertas Visuales (Semáforo de Stock)
# Netw@rd 1.6 - Control de Stock por Producto Individual

import streamlit as st
import json
import os
from typing import Dict, Tuple, Any

class StockAlertSystem:
    """
    Sistema de alertas visuales para control de stock por producto individual
    Implementa códigos de colores tipo semáforo (Rojo/Amarillo/Verde)
    """
    
    def __init__(self, config_file="stock_thresholds.json"):
        self.config_file = config_file
        self.thresholds = self._load_thresholds()
    
    def _load_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Cargar umbrales de stock desde archivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_thresholds()
        except Exception as e:
            st.warning(f"Error cargando umbrales: {e}. Usando valores por defecto.")
            return self._get_default_thresholds()
    
    def _get_default_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Umbrales por defecto para productos comunes"""
        return {
            # Helados por kilos
            "Vainilla": {"critico": 5.0, "medio": 15.0},
            "Chocolate": {"critico": 10.0, "medio": 25.0},
            "Fresa": {"critico": 8.0, "medio": 20.0},
            "Dulce de Leche": {"critico": 12.0, "medio": 30.0},
            "Crema Americana": {"critico": 10.0, "medio": 25.0},
            "Granizado": {"critico": 8.0, "medio": 20.0},
            
            # Productos impulsivos (unidades)
            "Caja almendrado": {"critico": 5, "medio": 15},
            "Unidad Almendrado": {"critico": 10, "medio": 30},
            "Caja Bombon Crocante": {"critico": 3, "medio": 10},
            "Unidad Bombon Crocante": {"critico": 8, "medio": 25},
            "Tentacion Chocolate": {"critico": 15, "medio": 40},
            "Tentacion Dulce de Leche": {"critico": 20, "medio": 50},
            "Crocantino": {"critico": 25, "medio": 60},
            "Delicia": {"critico": 20, "medio": 50},
            "Pizza": {"critico": 10, "medio": 30},
            
            # Extras y suministros
            "Cucurucho Nacional x54": {"critico": 50, "medio": 200},
            "Cucurucho Biscoito Dulce x300": {"critico": 300, "medio": 800},
            "Vaso capuccino": {"critico": 100, "medio": 500},
            "Cucharita Grido": {"critico": 200, "medio": 800},
            "Servilleta Grido": {"critico": 500, "medio": 2000},
            "Cobertura Chocolate": {"critico": 2, "medio": 8},
            "Cobertura Frutilla": {"critico": 2, "medio": 8},
            "Cobertura Dulce de Leche": {"critico": 3, "medio": 10},
        }
    
    def save_thresholds(self):
        """Guardar umbrales en archivo JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.thresholds, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error guardando umbrales: {e}")
            return False
    
    def get_stock_status(self, producto: str, cantidad: float) -> Tuple[str, str, str]:
        """
        Determinar el estado del stock para un producto
        
        Args:
            producto: Nombre del producto
            cantidad: Cantidad actual en stock
            
        Returns:
            Tuple con (emoji, color, descripción)
        """
        if producto not in self.thresholds:
            # Si no hay configuración específica, usar umbrales genéricos
            if cantidad <= 0:
                return "🔴", "critical", "SIN STOCK"
            elif cantidad <= 5:
                return "🟡", "warning", "STOCK BAJO"
            else:
                return "🟢", "success", "STOCK OK"
        
        thresholds = self.thresholds[producto]
        critico = thresholds.get("critico", 0)
        medio = thresholds.get("medio", critico * 2)
        
        if cantidad <= critico:
            return "🔴", "critical", "CRÍTICO"
        elif cantidad <= medio:
            return "🟡", "warning", "MEDIO"
        else:
            return "🟢", "success", "SUFICIENTE"
    
    def get_stock_color_css(self, status_color: str) -> str:
        """Retornar CSS class para el color de fondo según estado"""
        colors = {
            "critical": "background: linear-gradient(90deg, #ff6b6b, #ee5a52); color: white; font-weight: bold;",
            "warning": "background: linear-gradient(90deg, #feca57, #ff9ff3); color: #333; font-weight: bold;",
            "success": "background: linear-gradient(90deg, #48cab2, #2dd4bf); color: white; font-weight: bold;"
        }
        return colors.get(status_color, "background: #f8f9fa; color: #333;")
    
    def update_threshold(self, producto: str, critico: float, medio: float):
        """Actualizar umbrales para un producto específico"""
        if critico >= medio:
            raise ValueError("El umbral crítico debe ser menor que el umbral medio")
        
        self.thresholds[producto] = {
            "critico": critico,
            "medio": medio
        }
    
    def get_products_by_status(self, inventario: Dict) -> Dict[str, list]:
        """Agrupar productos por estado de stock"""
        status_groups = {
            "critical": [],
            "warning": [], 
            "success": []
        }
        
        for categoria, productos in inventario.items():
            for producto, cantidad in productos.items():
                if isinstance(cantidad, (int, float)) and cantidad >= 0:
                    emoji, status, desc = self.get_stock_status(producto, cantidad)
                    status_groups[status].append({
                        "producto": producto,
                        "categoria": categoria,
                        "cantidad": cantidad,
                        "emoji": emoji,
                        "descripcion": desc
                    })
        
        return status_groups
    
    def render_stock_alert_badge(self, producto: str, cantidad: float, 
                                show_details: bool = True) -> str:
        """
        Renderizar badge de alerta para un producto
        
        Args:
            producto: Nombre del producto
            cantidad: Cantidad actual
            show_details: Si mostrar detalles del umbral
            
        Returns:
            HTML string con el badge
        """
        emoji, status, desc = self.get_stock_status(producto, cantidad)
        css_style = self.get_stock_color_css(status)
        
        details = ""
        if show_details and producto in self.thresholds:
            thresholds = self.thresholds[producto]
            details = f" (Crítico: ≤{thresholds['critico']}, Medio: ≤{thresholds['medio']})"
        
        return f"""
        <div style="{css_style} padding: 0.25rem 0.5rem; border-radius: 15px; 
                    display: inline-block; margin: 0.1rem; font-size: 0.85rem;">
            {emoji} {desc}{details}
        </div>
        """
    
    def render_dashboard_summary(self, inventario: Dict):
        """Renderizar resumen de alertas en dashboard"""
        status_groups = self.get_products_by_status(inventario)
        
        st.markdown("### 🚨 Estado General del Stock")
        
        # Métricas de resumen con proporciones optimizadas
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            critical_count = len(status_groups["critical"])
            delta = f"-{critical_count}" if critical_count > 0 else "OK"
            st.metric(
                "🔴 Críticos", 
                critical_count,
                delta=delta,
                delta_color="inverse"
            )
        
        with col2:
            warning_count = len(status_groups["warning"])
            st.metric(
                "🟡 Atención", 
                warning_count,
                delta=f"Revisar {warning_count}" if warning_count > 0 else "OK"
            )
        
        with col3:
            success_count = len(status_groups["success"])
            st.metric(
                "🟢 Suficientes", 
                success_count,
                delta=f"+{success_count}" if success_count > 0 else "0"
            )
        
        # Alertas críticas expandidas
        if status_groups["critical"]:
            st.markdown("#### 🆘 **ALERTAS CRÍTICAS - Acción Inmediata Requerida**")
            for item in status_groups["critical"]:
                st.markdown(
                    self.render_stock_alert_badge(
                        item["producto"], 
                        item["cantidad"], 
                        show_details=True
                    ) + f" **{item['producto']}**: {item['cantidad']} restantes",
                    unsafe_allow_html=True
                )
        
        # Productos en atención
        if status_groups["warning"]:
            with st.expander(f"⚠️ Productos en Atención ({len(status_groups['warning'])})"):
                for item in status_groups["warning"]:
                    st.markdown(
                        self.render_stock_alert_badge(
                            item["producto"], 
                            item["cantidad"]
                        ) + f" {item['producto']}: {item['cantidad']}",
                        unsafe_allow_html=True
                    )
    
    def get_priority_order(self, producto: str, cantidad: float) -> int:
        """
        Obtener orden de prioridad para ordenamiento (menor = mayor prioridad)
        
        Args:
            producto: Nombre del producto
            cantidad: Cantidad actual
            
        Returns:
            int: 0=crítico, 1=medio, 2=suficiente
        """
        emoji, status, desc = self.get_stock_status(producto, cantidad)
        priority_map = {
            "critical": 0,  # Mayor prioridad (se muestra primero)
            "warning": 1,   # Prioridad media
            "success": 2    # Menor prioridad (se muestra último)
        }
        return priority_map.get(status, 2)
    
    def sort_products_by_priority(self, productos_dict: Dict, categoria: str = "") -> list:
        """
        Ordenar productos por prioridad de alerta (críticos primero)
        
        Args:
            productos_dict: Diccionario de productos {nombre: cantidad}
            categoria: Nombre de la categoría (opcional, para contexto)
            
        Returns:
            list: Lista de nombres de productos ordenados por prioridad
        """
        productos_con_prioridad = []
        
        for producto, cantidad in productos_dict.items():
            # Para productos por kilos (listas de baldes), calcular total
            if isinstance(cantidad, list):
                cantidad_total = sum(cantidad) if cantidad else 0
            else:
                cantidad_total = cantidad if isinstance(cantidad, (int, float)) else 0
            
            prioridad = self.get_priority_order(producto, cantidad_total)
            emoji, status, desc = self.get_stock_status(producto, cantidad_total)
            
            productos_con_prioridad.append({
                'nombre': producto,
                'cantidad': cantidad_total,
                'prioridad': prioridad,
                'status': status,
                'emoji': emoji,
                'descripcion': desc
            })
        
        # Ordenar por prioridad (0=crítico primero) y luego alfabéticamente
        productos_ordenados = sorted(
            productos_con_prioridad, 
            key=lambda x: (x['prioridad'], x['nombre'].lower())
        )
        
        return [p['nombre'] for p in productos_ordenados]
    
    def get_product_display_name(self, producto: str, productos_dict: Dict, show_alerts: bool = True) -> str:
        """
        Obtener nombre de producto con indicador de alerta para mostrar en selectbox
        
        Args:
            producto: Nombre del producto
            productos_dict: Diccionario de productos
            show_alerts: Si mostrar los emojis de alerta
            
        Returns:
            str: Nombre formateado para mostrar
        """
        if not show_alerts:
            return producto
        
        cantidad = productos_dict.get(producto, 0)
        
        # Para productos por kilos (listas de baldes), calcular total
        if isinstance(cantidad, list):
            cantidad_total = sum(cantidad) if cantidad else 0
        else:
            cantidad_total = cantidad if isinstance(cantidad, (int, float)) else 0
        
        emoji, status, desc = self.get_stock_status(producto, cantidad_total)
        
        # Formato: "🔴 Helado Chocolate" para críticos, etc.
        return f"{emoji} {producto}"
    
    def render_priority_toggle_button(self, key_suffix: str = "") -> bool:
        """
        Renderizar botón toggle para activar/desactivar ordenamiento por prioridad
        
        Args:
            key_suffix: Sufijo para la key del botón (evitar duplicados)
            
        Returns:
            bool: Estado del toggle (True = ordenamiento activado)
        """
        # Estado del toggle en session_state
        toggle_key = f"priority_sort_enabled_{key_suffix}"
        
        if toggle_key not in st.session_state:
            st.session_state[toggle_key] = False
        
        # Columnas para el toggle
        col_toggle, col_info = st.columns([3, 7])
        
        with col_toggle:
            enabled = st.checkbox(
                "🎯 Ordenar por prioridad",
                value=st.session_state[toggle_key],
                key=toggle_key,
                help="Muestra productos críticos (rojos) primero, luego amarillos y por último verdes"
            )
        
        with col_info:
            if enabled:
                st.markdown("""
                <div style="background: linear-gradient(90deg, #ff6b6b, #feca57, #48cab2); 
                           color: white; padding: 0.3rem 0.8rem; border-radius: 15px; 
                           font-size: 0.8rem; text-align: center;">
                    🔴 Críticos → 🟡 Medios → 🟢 Suficientes
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: #f8f9fa; color: #6c757d; padding: 0.3rem 0.8rem; 
                           border-radius: 15px; font-size: 0.8rem; text-align: center;">
                    📝 Orden alfabético normal
                </div>
                """, unsafe_allow_html=True)
        
        return enabled

# Instancia global del sistema de alertas

# Instancia global del sistema de alertas
stock_alert_system = StockAlertSystem()