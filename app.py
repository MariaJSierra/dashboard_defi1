import streamlit as st
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import json
import pandas_datareader.data as web
import statsmodels.api as sm
from funciones import *

activos_finales = {
    'IXC': 0.0444,
    'XLE': 0.0563,
    'CAR': 0.2334,
    'AMZN': 0.1735,
    'BHVN': 0.2340,
    'HTZ': 0.1890,
    'CVX': 0.0354,
    'AMX': 0.0141,
    'SI=F': 0.0100,
    'HG=F': 0.0100
}


# Configuración de página y estilos personalizados
st.set_page_config(layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #f0f2f6;
        }
        .titulo {
            text-align: center;
            font-size: 40px;
            color: #203c6c;
            margin-bottom: 40px;
        }
        .contenedor-derecho {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            width: 100%;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        .stApp {
            background-color: #f0f2f6;
        }
        /* Selectbox fondo blanco */
        div[data-baseweb="select"] > div {
            background-color: white !important;
            border-radius: 5px;
        }

        /* Opcional: Cambiar el color del texto dentro del select */
        div[data-baseweb="select"] span {
            color: black;
        }
            header, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
#
# Cargar datos
with open('simulations1.json', 'r') as f:
    all_simulations1 = json.load(f)

# Cargar datos
with open('simulations2.json', 'r') as f:
    all_simulations2 = json.load(f)



all_simulations1 = convertir_a_ndarray(all_simulations1)
all_simulations2 = convertir_a_ndarray(all_simulations2)
all_simulations1.update(all_simulations2)
all_simulations = all_simulations1.copy()

all_simulations = {k: v for k, v in all_simulations.items() if k in activos_finales}
returns = pd.read_excel('retornos.xlsx', index_col=0, parse_dates=True)

activos_finales_lst = list(activos_finales.keys())
activos_finales_lst.append('^GSPC')
returns = returns[activos_finales_lst]
tbill_data = web.DataReader('TB3MS', 'fred', "2023-04-15", "2025-04-15")

# --- TÍTULO CENTRADO ---
st.markdown('<div class="titulo">Portafolio de Inversión para El Inversionauta (Rentabilidad de 11.8029% a 6 meses)</div>', unsafe_allow_html=True)

# --- DISTRIBUCIÓN 50-50 ENTRE GRÁFICAS Y CONTENEDOR DERECHO ---
col_izq, col_der = st.columns(2)

with col_izq:
    # Filtros
    activos = list(all_simulations.keys())
    horizontes = ['Diario', 'Semanal', 'Mensual']

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        activo_seleccionado = st.selectbox('Seleccionar Activo:', activos)
    with col_f2:
        horizonte = st.selectbox('Seleccionar Horizonte:', horizontes)

    # Gráfica de Bandas
    sim_array = all_simulations[activo_seleccionado][horizonte]
    fig_bandas = generar_figura_bandas(sim_array, activo_seleccionado, horizonte)
    st.plotly_chart(fig_bandas, use_container_width=True)

    # Gráfica de Regresión
    st.plotly_chart(grafica_regresion(returns, activo_seleccionado, tbill_data), use_container_width=True)

with col_der:
    st.plotly_chart(grafica_regresion(returns, 'portafolio', tbill_data, activos_finales), use_container_width=True)

    st.plotly_chart(barras(activos_finales), use_container_width=True)

    # --- Cuadro de Primas Black-Scholes ---
    st.markdown("""
        <div style="background-color: white; padding: 10px; border-radius: 10px; margin-top: 5px;">
            <h4 style="color:#203c6c;">Primas de las Opciones (Black-Scholes) y VaR Paramétrico del Portafolio</h4>
            <table style="width:100%; text-align:left; font-size:16px;">
              <tr>
                <th>Opción</th>
                <th>Prima</th>
                <th style="border-bottom: 1px solid #ccc;">VaR 95%</th>
                <th style="border-bottom: 1px solid #ccc;">VaR 99%</th>
              </tr>
              <tr>
                <td>Call sobre IXC</td>
                <td>3.45 USD</td>
                <td rowspan="2" style="text-align:center;">-0.0864%</td>
                <td rowspan="2" style="text-align:center;">-0.1221%</td>
              </tr>
              <tr>
                <td>Put sobre AMZN</td>
                <td>5.10 USD</td>
              </tr>
            </table>
        </div>
    """, unsafe_allow_html=True)

    