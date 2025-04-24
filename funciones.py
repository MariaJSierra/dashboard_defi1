import numpy as np
import plotly.graph_objs as go
import statsmodels.api as sm
import pandas as pd

# Función para generar la figura de bandas
def generar_figura_bandas(sim_array, activo, horizonte):
    pasos = {
        'Diario': np.arange(120),
        'Semanal': np.arange(21),
        'Mensual': np.arange(6)
    }
    sum_val = {
        'Diario': 4.5,
        'Semanal': 1,
        'Mensual': 0.25
    }

    x = pasos[horizonte]
    sim = np.array(sim_array)

    mean = np.mean(sim, axis=1)
    p005 = np.percentile(sim, 0.5, axis=1)
    p025 = np.percentile(sim, 2.5, axis=1)
    p975 = np.percentile(sim, 97.5, axis=1)
    p995 = np.percentile(sim, 99.5, axis=1)

    fig = go.Figure()

    # Banda 99% (gris)
    fig.add_trace(go.Scatter(
        x=x, y=p995,
        mode='lines',
        line=dict(width=0),
        name='Banda 99%',
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=x, y=p005,
        mode='lines',
        fill='tonexty',
        fillcolor='lightgrey',
        line=dict(width=0),
        name='Banda 99%'
    ))

    # Banda 95% (azul claro)
    fig.add_trace(go.Scatter(
        x=x, y=p975,
        mode='lines',
        line=dict(width=0),
        name='Banda 95%',
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=x, y=p025,
        mode='lines',
        fill='tonexty',
        fillcolor='lightblue',
        line=dict(width=0),
        name='Banda 95%'
    ))

    # Media (línea azul)
    fig.add_trace(go.Scatter(
        x=x, y=mean,
        mode='lines',
        line=dict(color='blue', width=2),
        name='Media'
    ))

    # Anotaciones finales
    fig.add_annotation(x=x[-1]+sum_val[horizonte], y=p005[-1], text=f'{p005[-1]:.2f}', showarrow=False, font=dict(color='grey'))
    fig.add_annotation(x=x[-1]+sum_val[horizonte], y=p025[-1], text=f'{p025[-1]:.2f}', showarrow=False, font=dict(color='deepskyblue'))
    fig.add_annotation(x=x[-1]+sum_val[horizonte], y=mean[-1], text=f'{mean[-1]:.2f}', showarrow=False, font=dict(color='blue'))
    fig.add_annotation(x=x[-1]+sum_val[horizonte], y=p975[-1], text=f'{p975[-1]:.2f}', showarrow=False, font=dict(color='deepskyblue'))
    fig.add_annotation(x=x[-1]+sum_val[horizonte], y=p995[-1], text=f'{p995[-1]:.2f}', showarrow=False, font=dict(color='grey'))

    fig.update_layout(
        title=f'Bandas de Confianza de {activo} ({horizonte})',
        xaxis_title=horizonte,
        yaxis_title='Precio simulado',
        template='plotly_white',
        width=1300,
        height=400
    )

    return fig

def convertir_a_ndarray(obj):
    if isinstance(obj, list):
        try:
            return np.array(obj)
        except:
            return [convertir_a_ndarray(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convertir_a_ndarray(v) for k, v in obj.items()}
    return obj

# Gráfica de Regresión
def grafica_regresion(returns, activo_seleccionado, tbill_data, activos_finales = []):
    returns_capm = returns.copy()
    tbill_rate = tbill_data.dropna() / 100 / 360
    tbill_rate = tbill_rate.reindex(returns_capm.index, method='ffill')

    if activo_seleccionado == 'portafolio':
        activos_seleccionados = list(activos_finales.keys())
        pesos_optimos = list(activos_finales.values())

        retornos_portafolio = np.log((returns_capm[activos_seleccionados] @ pesos_optimos).dropna() + 1)
        Y = retornos_portafolio - tbill_rate['TB3MS']
    else:
        Y = returns_capm[activo_seleccionado] - tbill_rate['TB3MS']
    X = returns_capm['^GSPC'] - tbill_rate['TB3MS']
    X = sm.add_constant(X)

    datos_regresion = pd.concat([Y, X], axis=1).dropna()

    Y = datos_regresion.iloc[:, 0]      # Primera columna es Y
    X = datos_regresion.iloc[:, 1:]     # Las demás son X (incluye constante)

    modelo = sm.OLS(Y, X).fit()
    alpha = modelo.params['const']
    beta = modelo.params[0]
    
    y_reg = returns_capm[activo_seleccionado] if activo_seleccionado != 'portafolio' else retornos_portafolio
    fig_regresion = go.Figure()
    fig_regresion.add_trace(go.Scatter(x=returns_capm['^GSPC'], y=y_reg,
                                       mode='markers', marker=dict(opacity=0.5), name='Datos'))

    x_vals = np.linspace(returns_capm['^GSPC'].min(), returns_capm['^GSPC'].max(), 100)
    y_vals = alpha + beta * x_vals

    fig_regresion.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', line=dict(color='grey'), name='Línea Ajustada'))

    fig_regresion.update_layout(title=f'Relación entre {activo_seleccionado} y S&P 500 (Beta: {beta:.2f}, Alpha: {alpha:.4f})',
                                xaxis_title='S&P 500 Returns', yaxis_title=f'{activo_seleccionado} Returns', template='plotly_white', height=400)
    return fig_regresion

def barras(datos):
    # Ordenar el diccionario de mayor a menor
    datos_ordenados = dict(sorted(datos.items(), key=lambda item: item[1], reverse=True))

    # Convertimos las claves y valores, y multiplicamos por 100 para porcentaje
    nombres = list(datos_ordenados.keys())
    valores = [v * 100 for v in datos_ordenados.values()]

    # Crear gráfica de barras con etiquetas de porcentaje
    fig = go.Figure(data=[go.Bar(
        x=nombres,
        y=valores,
        text=[f'{v:.2f}%' for v in valores],  # Mostrar valores con dos decimales y símbolo %
        textposition='outside'  # Coloca las etiquetas fuera de las barras
    )])

    # Personalizar el layout
    fig.update_layout(
        title='Porcentaje de Inversión por Activo',
        xaxis_title='Activos',
        yaxis_title='Porcentaje (%)',
        template='plotly_white',
        height=260
    )

    # Opcional: Ajustar separación si las etiquetas son largas
    fig.update_traces(marker_color='skyblue')  # Color opcional
    fig.update_yaxes(range=[0, max(valores) * 1.2])  # Espacio para las etiquetas

    return fig
