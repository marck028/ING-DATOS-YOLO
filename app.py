import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import base64
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="Detección de Perros - Dashboard",
    page_icon="🐕",
    layout="wide"
)

# Custom CSS to improve the design
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #E5E7EB;
    }
    .subheader {
        font-size: 1.5rem;
        color: #1E3A8A;
        padding-top: 1rem;
        padding-bottom: 0.5rem;
    }
    .card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #F3F4F6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 1rem;
        color: #6B7280;
    }
    .stButton > button {
        background-color: #1E3A8A;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.3rem;
    }
    .stButton > button:hover {
        background-color: #2563EB;
    }
    .upload-section {
        text-align: center;
        padding: 2rem;
        border: 2px dashed #E5E7EB;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
    .footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #E5E7EB;
        font-size: 0.9rem;
        color: #6B7280;
    }
    .contact-info {
        margin-top: 0.5rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Function to get base64 encoded image - Placeholder if image is not found
def get_base64_placeholder_image(width, height, text="YOLO + Streamlit"):
    """Create a placeholder image when the real image is not available"""
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Create a blank image with blue background
    img = Image.new('RGB', (width, height), color=(30, 58, 138))
    d = ImageDraw.Draw(img)
    
    # Try to use a font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    
    # Add text
    text_width, text_height = d.textsize(text, font=font) if hasattr(d, 'textsize') else (100, 20)
    d.text(((width-text_width)/2, (height-text_height)/2), text, fill=(255, 255, 255), font=font)
    
    # Save to bytes
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    
    # Encode
    return base64.b64encode(buffered.getvalue()).decode()

# Function to check if image exists and return appropriate image
def get_image_data(image_path, width=200, height=150, alt_text="YOLO + Streamlit"):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        # Return placeholder if image not found
        return get_base64_placeholder_image(width, height, alt_text)

# Header with app title and description
st.markdown('<h1 class="main-header">📹 Detección de Perros en el Parque</h1>', unsafe_allow_html=True)

col_intro1, col_intro2 = st.columns([1, 3])
with col_intro1:
    # Try to display the image, fallback to placeholder if not found
    try:
        # Check if the directory exists
        img_dir = "img"
        if not os.path.exists(img_dir):
            os.makedirs(img_dir, exist_ok=True)
            
        # Path to logo image
        logo_path = os.path.join(img_dir, "img1.png")
        
        # If file exists, display it; otherwise, show placeholder
        if os.path.isfile(logo_path):
            st.image(logo_path, caption="YOLO + Streamlit")
        else:
            # Display base64 encoded placeholder
            logo_base64 = get_base64_placeholder_image(200, 150)
            st.markdown(f"""
                <div style="text-align: center;">
                    <img src="data:image/png;base64,{logo_base64}" width="200" alt="YOLO + Streamlit">
                    <p style="font-size:0.8rem; color:gray;">YOLO + Streamlit</p>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"No se pudo cargar la imagen: {e}")

with col_intro2:
    st.markdown("""
    Este dashboard interactivo presenta un análisis detallado de las detecciones de perros 
    capturadas por nuestro sistema de videovigilancia inteligente basado en YOLO. 
    Visualiza patrones temporales, niveles de confianza y estadísticas relevantes para 
    comprender mejor la presencia canina en el área monitoreada.
    """)

# File upload section
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown('<h2 class="subheader">📁 Carga de Datos</h2>', unsafe_allow_html=True)
archivo = st.file_uploader("Sube tu archivo Excel con detecciones de perros", type=["xlsx"])
st.markdown('</div>', unsafe_allow_html=True)

# Function to classify confidence levels
def clasificar_confianza(c):
    if c < 0.7:
        return "Baja"
    elif c < 0.9:
        return "Media"
    else:
        return "Alta"

# Function to export dataframe to Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')
    processed_data = output.getvalue()
    return processed_data

# Sample data option for demo purposes
use_sample_data = st.checkbox("¿Deseas usar datos de ejemplo para demo?", False)

# Process data if uploaded or sample data is selected
if archivo is not None or use_sample_data:
    
    # Create sample data if selected
    if use_sample_data:
        # Generate sample data
        import numpy as np
        dates = pd.date_range(start='2023-01-01', periods=100, freq='30min')
        
        # Create sample dataframe
        data = {
            'Hora': [d.strftime('%H:%M:%S') for d in dates],
            'confidence': np.random.uniform(0.5, 1.0, 100),
            'Dia': [d.strftime('%A') for d in dates]
        }
        df = pd.DataFrame(data)
        
        # Translate days to Spanish
        day_translation = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miércoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        df['Dia'] = df['Dia'].replace(day_translation)
        
    else:
        try:
            # Read uploaded Excel file
            df = pd.read_excel(archivo)
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
            st.stop()
    
    # Data cleanup and transformations
    try:
        # Handle different formats of confidence values
        if 'confidence' in df.columns:
            if df["confidence"].dtype == object:
                df["confidence"] = df["confidence"].astype(str).str.replace(",", ".").astype(float)
            
        # Create hour from time
        if 'Hora' in df.columns:
            try:
                df["Hora (hora)"] = pd.to_datetime(df["Hora"], format="%H:%M:%S").dt.hour
            except:
                try:
                    # Try another format if the first one fails
                    df["Hora (hora)"] = pd.to_datetime(df["Hora"]).dt.hour
                except:
                    st.warning("No se pudo convertir la columna 'Hora' al formato esperado. Se utilizará la hora actual para demostraciones.")
                    df["Hora (hora)"] = datetime.now().hour
        else:
            st.warning("No se encontró la columna 'Hora'. Se creará una columna de demo.")
            df["Hora"] = [f"{h:02d}:00:00" for h in range(24) for _ in range(len(df)//24 + 1)][:len(df)]
            df["Hora (hora)"] = [h for h in range(24) for _ in range(len(df)//24 + 1)][:len(df)]
            
        # Check for Dia column
        if 'Dia' not in df.columns:
            st.warning("No se encontró la columna 'Dia'. Se creará una columna de demo.")
            days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            df["Dia"] = [days[i % 7] for i in range(len(df))]
            
        # Create confidence level categories
        df["Confianza Nivel"] = df["confidence"].apply(clasificar_confianza)
        
        # Create timestamp
        try:
            df["Timestamp"] = pd.to_datetime(df["Hora"])
        except:
            current_date = datetime.now().strftime('%Y-%m-%d')
            df["Timestamp"] = pd.to_datetime(current_date + ' ' + df["Hora"])
            
    except Exception as e:
        st.error(f"Error en el procesamiento de datos: {e}")
        # Continue with minimal functionality
    
    # Dashboard sections
    st.markdown('<h2 class="subheader">📊 Panel de Control</h2>', unsafe_allow_html=True)
    
    # Key metrics in cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(df)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total de Detecciones</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{df["confidence"].mean():.2f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Confianza Promedio</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{df["confidence"].max():.2f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Confianza Máxima</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{df["Dia"].value_counts().idxmax()}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Día con Más Detecciones</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Temporal analysis section
    st.markdown('<h2 class="subheader">📅 Análisis Temporal</h2>', unsafe_allow_html=True)
    
    temporal_tab1, temporal_tab2, temporal_tab3 = st.tabs(["Por Hora", "Por Día", "Mapa de Calor"])
    
    with temporal_tab1:
        # Detections by hour
        detecciones_por_hora = df["Hora (hora)"].value_counts().reset_index()
        detecciones_por_hora.columns = ["Hora", "Cantidad"]
        detecciones_por_hora = detecciones_por_hora.sort_values("Hora")
        
        fig_hour = px.bar(detecciones_por_hora, x="Hora", y="Cantidad", text="Cantidad",
                        labels={"Hora": "Hora del Día", "Cantidad": "Cantidad de Detecciones"},
                        color="Cantidad", color_continuous_scale="Blues")
        fig_hour.update_traces(textposition="outside")
        fig_hour.update_layout(
            title="Detecciones por Hora del Día",
            title_x=0.5,
            xaxis_title="Hora del Día",
            yaxis_title="Cantidad de Detecciones",
            height=500
        )
        st.plotly_chart(fig_hour, use_container_width=True)
    
    with temporal_tab2:
        # Detections by day
        detecciones_dia = df["Dia"].value_counts().reset_index()
        detecciones_dia.columns = ["Día", "Cantidad"]
        
        # Order days of week correctly
        day_order = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        detecciones_dia["Día"] = pd.Categorical(detecciones_dia["Día"], categories=day_order, ordered=True)
        detecciones_dia = detecciones_dia.sort_values("Día")
        
        fig_day = px.bar(detecciones_dia, x="Día", y="Cantidad", text="Cantidad",
                        labels={"Día": "Día de la Semana", "Cantidad": "Cantidad de Detecciones"},
                        color="Cantidad", color_continuous_scale="Greens")
        fig_day.update_traces(textposition="outside")
        fig_day.update_layout(
            title="Detecciones por Día de la Semana",
            title_x=0.5,
            xaxis_title="Día de la Semana",
            yaxis_title="Cantidad de Detecciones",
            height=500
        )
        st.plotly_chart(fig_day, use_container_width=True)
    
    with temporal_tab3:
        try:
            # Heat map by day and hour
            pivot = pd.pivot_table(df, 
                                index="Dia", 
                                columns="Hora (hora)", 
                                values="confidence", 
                                aggfunc="count", 
                                fill_value=0)
            
            # Make sure days are properly ordered
            if all(day in day_order for day in pivot.index):
                pivot = pivot.reindex(day_order)
            
            fig_heatmap = px.imshow(pivot, 
                                    color_continuous_scale="Viridis",
                                    labels=dict(color="Cantidad"),
                                    height=500)
            fig_heatmap.update_layout(
                title="Mapa de Calor: Detecciones por Día y Hora",
                title_x=0.5,
                xaxis_title="Hora del Día",
                yaxis_title="Día de la Semana"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        except Exception as e:
            st.error(f"Error al generar el mapa de calor: {e}")
    
    # Confidence analysis section
    st.markdown('<h2 class="subheader">✅ Análisis de Confianza</h2>', unsafe_allow_html=True)

    conf_col1, conf_col2 = st.columns(2)
    
    with conf_col1:
        # Confidence distribution histogram
        fig_hist = px.histogram(df, x="confidence", nbins=20,
                            title="Distribución de Confianza de Detección",
                            labels={"confidence": "Nivel de Confianza"},
                            color_discrete_sequence=["#4B8BBE"])
        fig_hist.update_layout(
            title_x=0.5,
            xaxis_title="Nivel de Confianza",
            yaxis_title="Frecuencia",
            height=400
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with conf_col2:
        # Confidence categories pie chart
        fig_pie = px.pie(df, names="Confianza Nivel", 
                        title="Distribución de Niveles de Confianza",
                        color_discrete_map={
                            "Baja": "#FFC107", 
                            "Media": "#2196F3", 
                            "Alta": "#4CAF50"
                        })
        fig_pie.update_layout(
            title_x=0.5,
            height=400
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Temporal evolution
    st.markdown('<h2 class="subheader">📈 Evolución Temporal</h2>', unsafe_allow_html=True)
    
    try:
        detecciones_tiempo = df.groupby("Timestamp").size().reset_index(name="Cantidad")
        fig_tiempo = px.line(detecciones_tiempo, x="Timestamp", y="Cantidad", markers=True,
                            labels={"Timestamp": "Hora", "Cantidad": "Detecciones"})
        fig_tiempo.update_layout(
            title="Evolución Temporal de Detecciones",
            title_x=0.5,
            xaxis_title="Hora",
            yaxis_title="Cantidad de Detecciones",
            height=500
        )
        st.plotly_chart(fig_tiempo, use_container_width=True)
    except Exception as e:
        st.error(f"Error al generar el gráfico de evolución temporal: {e}")
    
    # Data table section
    st.markdown('<h2 class="subheader">📄 Datos</h2>', unsafe_allow_html=True)
    
    data_tab1, data_tab2 = st.tabs(["Vista de Tabla", "Estadísticas"])
    
    with data_tab1:
        # Show original data with sorting and filtering
        st.dataframe(df, height=300, use_container_width=True)
        
        # Export options
        export_col1, export_col2 = st.columns(2)
        with export_col1:
            if st.button("📥 Exportar a CSV"):
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar CSV", 
                    data=csv,
                    file_name='detecciones_perros.csv',
                    mime='text/csv',
                )
        with export_col2:
            if st.button("📥 Exportar a Excel"):
                try:
                    excel_data = to_excel(df)
                    st.download_button(
                        label="Descargar Excel",
                        data=excel_data,
                        file_name='detecciones_perros.xlsx',
                        mime='application/vnd.ms-excel'
                    )
                except Exception as e:
                    st.error(f"Error al exportar a Excel: {e}")
                    st.info("Funcionalidad de exportación a Excel en desarrollo.")
    
    with data_tab2:
        # Show statistical summary
        st.write("Estadísticas descriptivas de la confianza de detección:")
        st.dataframe(df['confidence'].describe().reset_index(), height=300, use_container_width=True)
    
    # Footer with additional information
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("""
    *Dashboard desarrollado con Streamlit y Plotly. Para más información sobre el sistema de 
    detección YOLO utilizado, contacte al equipo de desarrollo.*
    """)
    st.markdown('<div class="contact-info">', unsafe_allow_html=True)
    st.markdown("Marco Salvatierra: +591 63860980 | Fabio Mavric: +591 70710301")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Show instructions when no file is uploaded
    st.markdown("""
    ## 📋 Instrucciones

    Para comenzar a analizar las detecciones de perros:
    
    1. Sube un archivo Excel (.xlsx) con los datos de las detecciones
    2. El archivo debe contener las columnas: `Hora`, `confidence` y `Dia`
    3. También puedes usar los datos de ejemplo marcando la casilla correspondiente
    
    El dashboard generará automáticamente visualizaciones interactivas para analizar patrones
    y tendencias en las detecciones de perros registradas por el sistema YOLO.
    """)
    
    # Show sample dashboard structure
    try:
        # Path to preview image
        preview_path = os.path.join("img", "img2.png")
        
        # If file exists, display it; otherwise, show placeholder
        if os.path.isfile(preview_path):
            st.image(preview_path, caption="Vista previa del dashboard")
        else:
            # Display base64 encoded placeholder
            preview_base64 = get_base64_placeholder_image(200, 200, "Vista previa del dashboard")
            st.markdown(f"""
                <div style="text-align: center;">
                    <img src="data:image/png;base64,{preview_base64}" width="800" alt="Vista previa del dashboard">
                    <p style="font-size:0.8rem; color:gray;">Vista previa del dashboard</p>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"No se pudo cargar la imagen de vista previa: {e}")
