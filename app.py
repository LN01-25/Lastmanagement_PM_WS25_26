import pandas as pd
import plotly.graph_objects as go
import numpy as np
import streamlit as st


# --- Daten einlesen ---
def daten():
    df = pd.read_excel("Lastmanagement.xlsx")
    return df


# --- PLOT: Wasserstoff ---
def plot_Wasserstoff(df):
    df_clean = df[[
        "Tag",
        "Uhrzeit",
        "Speicherveränderung [kg]",
        "Speicherstand kummuliert [kg]",
        "SOC [%]",
        "Sperrzeiten_weil_Tanken",
        "Sperrzeiten_weil_Nachtruhe",
        "Zeit für Elektrolyseur"
    ]].copy()

    df_clean["SOC [%]"] = pd.to_numeric(df_clean["SOC [%]"], errors="coerce")
    df_clean["Startzeit"] = df_clean["Uhrzeit"].str.split("–").str[0]
    df_clean["Zeitstempel"] = pd.to_datetime(df_clean["Tag"].astype(str) + " " + df_clean["Startzeit"],
                                             dayfirst=True, errors="coerce")

    df_clean["Bar_Farbe"] = np.where(
        df_clean["Speicherveränderung [kg]"] >= 0,
        "rgba(0,180,0,0.7)",
        "rgba(220,0,0,0.7)"
    )

    def lade_farbe(status):
        status_str = str(status).lower()
        if "darf" in status_str and "nicht" not in status_str:
            return "rgba(0,180,0,0.25)"
        else:
            return "rgba(220,0,0,0.25)"

    df_clean["Lade_Farbe"] = df_clean["Zeit für Elektrolyseur"].apply(lade_farbe)

    fig = go.Figure()

    # Hauptbalken
    fig.add_trace(go.Bar(
        x=df_clean["Zeitstempel"],
        y=df_clean["Speicherveränderung [kg]"],
        name="Speicherveränderung [kg]",
        marker_color=df_clean["Bar_Farbe"],
        opacity=0.8,
        hovertemplate=(
            "Zeit: %{x|%d.%m %H:%M}<br>"
            "ΔSpeicher: %{y} kg<br>"
            "SOC: %{customdata[0]:.3f}<br>"
            "Elektrolyseur: %{customdata[1]}"
        ),
        customdata=df_clean[["SOC [%]", "Zeit für Elektrolyseur"]]
    ))

    # SOC-Linie
    fig.add_trace(go.Scatter(
        x=df_clean["Zeitstempel"],
        y=df_clean["SOC [%]"],
        mode="lines+markers",
        name="SOC (0–1)",
        line=dict(color="royalblue", width=3),
        yaxis="y2",
        hovertemplate="Zeit: %{x|%d.%m %H:%M}<br>SOC: %{y:.3f}"
    ))

    # Ladefreigabe-Band (leicht über 0)
    band_height = max(abs(df_clean["Speicherveränderung [kg]"])) * 0.05
    fig.add_trace(go.Bar(
        x=df_clean["Zeitstempel"],
        y=[band_height] * len(df_clean),
        marker_color=df_clean["Lade_Farbe"],
        name="Ladefreigabe",
        showlegend=False,
        base=[-band_height],
        hovertemplate="Zeit: %{x|%d.%m %H:%M}<br>%{customdata}",
        customdata=df_clean["Zeit für Elektrolyseur"],
        opacity=0.9
    ))

    # Layout
    ymin = df_clean["Speicherveränderung [kg]"].min()
    ymax = df_clean["Speicherveränderung [kg]"].max()

    fig.update_layout(
        title="Speicherverlauf über mehrere Tage, SOC (0–1) und Ladefreigabe (Elektrolyseur)",
        xaxis_title="Datum & Uhrzeit",
        yaxis=dict(
            title="Speicherveränderung [kg]",
            range=[ymin - abs(ymin)*0.1, ymax * 1.2],
            zeroline=True,
            zerolinecolor="black",
            showgrid=False,
            fixedrange=True
        ),
        yaxis2=dict(
            title="SOC (0–1)",
            overlaying="y",
            side="right",
            showgrid=False,
            autorange=True,
            fixedrange=True
        ),
        template="plotly_white",
        barmode="overlay",
        bargap=0.15,
        height=550,
        margin=dict(t=80, b=100),
        xaxis=dict(
            tickformat="%d.%m %H:%M",
            tickangle=45,
            dtick=10800000,
            fixedrange=True
        ),
        legend=dict(
            x=0.5, y=1.1, xanchor="center", yanchor="bottom", orientation="h"
        )
    )

    st.plotly_chart(fig, use_container_width=True)


# --- PLOT: Wasser ---
def plot_wasser(df):
    df_clean = df[["Tag", "Uhrzeit", "Wasserbedarf [Liter]"]].copy()
    df_clean["Startzeit"] = df_clean["Uhrzeit"].str.split("–").str[0]
    df_clean["Zeitstempel"] = pd.to_datetime(df_clean["Tag"].astype(str) + " " + df_clean["Startzeit"],
                                             dayfirst=True, errors="coerce")

    df_clean["Tag"] = pd.to_datetime(df_clean["Tag"], dayfirst=True)
    df_clean["Wasser kumuliert Tagesweise [Liter]"] = df_clean.groupby("Tag")["Wasserbedarf [Liter]"].cumsum()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_clean["Zeitstempel"],
        y=df_clean["Wasserbedarf [Liter]"],
        name="Wasserbedarf [Liter] pro Intervall",
        marker_color="rgba(0,123,255,0.5)",
        opacity=0.7,
        hovertemplate="Zeit: %{x|%d.%m %H:%M}<br>Wasserbedarf: %{y} Liter"
    ))

    fig.add_trace(go.Scatter(
        x=df_clean["Zeitstempel"],
        y=df_clean["Wasser kumuliert Tagesweise [Liter]"],
        mode="lines+markers",
        name="Kumulierter Tagesverbrauch [Liter]",
        line=dict(color="darkblue", width=3),
        yaxis="y2",
        hovertemplate="Zeit: %{x|%d.%m %H:%M}<br>Kumuliert heute: %{y} Liter"
    ))

    fig.update_layout(
        title="Wasserverbrauch pro Intervall und kumuliert pro Tag",
        xaxis_title="Datum & Uhrzeit",
        yaxis=dict(title="Wasserbedarf [Liter] pro Intervall", showgrid=False),
        yaxis2=dict(title="Kumulierter Tagesverbrauch [Liter]", overlaying="y", side="right", showgrid=False),
        template="plotly_white",
        height=550,
        margin=dict(t=80, b=100),
        barmode="overlay",
        xaxis=dict(tickformat="%d.%m %H:%M",dtick=10800000, tickangle=45),
        legend=dict(
            x=0.5, y=1.1, orientation="h", xanchor="center", yanchor="bottom"
        )
    )

    st.plotly_chart(fig, use_container_width=True)


# --- PLOT: Leistung ---
def plot_leistung(df):
    cols = ["Tag", "Uhrzeit", "Elektrolyseur [kWh]", "Verdichter [kWh]", "Speicherung [kWh]", "Tankstelle [kWh]", "SUMME [kWh]"]
    df_clean = df[cols].copy()
    df_clean["Startzeit"] = df_clean["Uhrzeit"].str.split("–").str[0]
    df_clean["Zeitstempel"] = pd.to_datetime(df_clean["Tag"].astype(str) + " " + df_clean["Startzeit"],
                                             dayfirst=True, errors="coerce")

    fig = go.Figure()

    fig.add_trace(go.Bar(x=df_clean["Zeitstempel"], y=df_clean["Elektrolyseur [kWh]"], name="Elektrolyseur [kWh]", opacity=0.8))
    fig.add_trace(go.Bar(x=df_clean["Zeitstempel"], y=df_clean["Verdichter [kWh]"], name="Verdichter [kWh]", opacity=0.8))
    fig.add_trace(go.Bar(x=df_clean["Zeitstempel"], y=df_clean["Speicherung [kWh]"], name="Speicherung [kWh]", opacity=0.8))
    fig.add_trace(go.Bar(x=df_clean["Zeitstempel"], y=df_clean["Tankstelle [kWh]"], name="Tankstelle [kWh]", opacity=0.8))

    fig.add_trace(go.Scatter(
        x=df_clean["Zeitstempel"],
        y=df_clean["SUMME [kWh]"],
        mode="lines+markers",
        name="Gesamtleistung [kWh]",
        line=dict(color="black", width=3),
        yaxis="y2",
        hovertemplate="Zeit: %{x|%d.%m %H:%M}<br>Gesamt: %{y} kWh"
    ))

    fig.update_layout(
        title="Strombezug über Zeit",
        xaxis_title="Datum & Uhrzeit",
        yaxis=dict(title="Energie [kWh] pro Komponente", showgrid=False),
        yaxis2=dict(title="Energie [kWh]", overlaying="y", side="right", showgrid=False),
        template="plotly_white",
        height=600,
        margin=dict(t=80, b=100),
        barmode="stack",
        xaxis=dict(tickformat="%d.%m %H:%M",dtick=10800000, tickangle=45),
        legend=dict(
            x=0.5, y=1.1, orientation="h", xanchor="center", yanchor="bottom"
        )
    )

    st.plotly_chart(fig, use_container_width=True)


# --- Hauptprogramm ---
def main():
    st.set_page_config(page_title="Dashboard", layout="wide")

    # Sidebar Navigation
    st.sidebar.title("📊 Navigation")
    auswahl = st.sidebar.radio("Wähle eine Ansicht:", ["Lastmanagement", "Kostenfunktionen"])

    df = daten()

    if auswahl == "Lastmanagement":
        st.header("Lastmanagement Wasserstoff")
        st.info("Am 01.11.2025 wird von morgens bis 21 Uhr ein Wartungstag simuliert. Innerhalb des Zeitfensters findet keine Wasserstoffproduktion statt.")
        plot_Wasserstoff(df)

        st.header("Lastmanagement Strombezug")
        plot_leistung(df)

        st.header("Lastmanagement Wasser")
        plot_wasser(df)

    elif auswahl == "Kostenfunktionen":
        st.header("Kostenfunktionen & Energieeinkauf (in Vorbereitung)")
        st.info("")


if __name__ == "__main__":
    main()
