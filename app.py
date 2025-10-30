import pandas as pd
import plotly.graph_objects as go
import numpy as np
import streamlit as st






def daten():
    # --- Excel einlesen ---
    df = pd.read_excel("Lastmanagement.xlsx")
    return df

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

    # --- SOC [%] bereinigen ---
    df_clean["SOC [%]"] = pd.to_numeric(df_clean["SOC [%]"], errors="coerce")

    # --- Startzeit aus Uhrzeit-Intervall extrahieren ---
    df_clean["Startzeit"] = df_clean["Uhrzeit"].str.split("–").str[0]

    # --- Zeitstempel aus Tag + Startzeit erstellen ---
    df_clean["Zeitstempel"] = pd.to_datetime(
        df_clean["Tag"].astype(str) + " " + df_clean["Startzeit"],
        dayfirst=True,  
        errors="coerce"
    )

    # --- Farben für Speicherveränderung ---
    df_clean["Bar_Farbe"] = np.where(
        df_clean["Speicherveränderung [kg]"] >= 0,
        "rgba(0,180,0,0.7)",   # grün
        "rgba(220,0,0,0.7)"    # rot
    )

    # --- Farben für Ladefreigabe (Elektrolyseur darf/nicht darf) ---
    def lade_farbe(status):
        status_str = str(status).lower()
        if "darf" in status_str and "nicht" not in status_str:
            return "rgba(0,180,0,0.3)"   # darf laden → grün
        else:
            return "rgba(220,0,0,0.3)"   # darf nicht → rot

    df_clean["Lade_Farbe"] = df_clean["Zeit für Elektrolyseur"].apply(lade_farbe)

    # --- Plot erstellen ---
    fig = go.Figure()

    # Balken: Speicherveränderung
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

    # Linie: SOC (rechte Achse)
    fig.add_trace(go.Scatter(
        x=df_clean["Zeitstempel"],
        y=df_clean["SOC [%]"],
        mode="lines+markers",
        name="SOC (0–1)",
        line=dict(color="royalblue", width=3),
        yaxis="y2",
        hovertemplate="Zeit: %{x|%d.%m %H:%M}<br>SOC: %{y:.3f}"
    ))

    # Band: Lade/Nichtlade-Zeiten
    band_height = max(abs(df_clean["Speicherveränderung [kg]"])) * 0.1
    fig.add_trace(go.Bar(
        x=df_clean["Zeitstempel"],
        y=[-band_height] * len(df_clean),
        marker_color=df_clean["Lade_Farbe"],
        name="Ladefreigabe",
        showlegend=False,
        base=[-band_height * 1.5],
        hovertemplate="Zeit: %{x|%d.%m %H:%M}<br>%{customdata}",
        customdata=df_clean["Zeit für Elektrolyseur"],
        opacity=0.9
    ))

    # --- Layout ---
    fig.update_layout(
        title="Speicherverlauf über mehrere Tage, SOC (0–1) und Ladefreigabe (Elektrolyseur)",
        xaxis_title="Datum & Uhrzeit",
        yaxis=dict(
            title="Speicherveränderung [kg]",
            zeroline=True,
            zerolinecolor="black",
            showgrid=False
        ),
        yaxis2=dict(
            title="SOC (0–1)",
            overlaying="y",
            side="right",
            showgrid=False,
            autorange=True
        ),
        template="plotly_white",
        barmode="overlay",
        bargap=0.15,
        height=650,
        #legend=dict(x=0.01, y=0.99),
        margin=dict(t=80, b=100),
        xaxis=dict(
            tickformat="%d.%m %H:%M",  # zeigt Datum + Zeit
            tickangle=45
        )
    )

    # --- Achsenbereich leicht erweitern ---
    ymin = df_clean["Speicherveränderung [kg]"].min()
    ymax = df_clean["Speicherveränderung [kg]"].max()
    fig.update_yaxes(range=[ymin - abs(ymin) * 0.4, ymax * 1.2])

    st.plotly_chart(fig, use_container_width=True)
def plot_wasser(df):
    # --- Relevante Spalten auswählen ---
    df_clean = df[["Tag", "Uhrzeit", "Wasserbedarf [Liter]"]].copy()

    # --- Startzeit aus Uhrzeit-Intervall extrahieren ---
    df_clean["Startzeit"] = df_clean["Uhrzeit"].str.split("–").str[0]

    # --- Zeitstempel aus Tag + Startzeit erstellen ---
    df_clean["Zeitstempel"] = pd.to_datetime(
        df_clean["Tag"].astype(str) + " " + df_clean["Startzeit"],
        dayfirst=True,
        errors="coerce"
    )

    # --- Tagesweise kumulierten Wasserverbrauch berechnen ---
    df_clean["Tag"] = pd.to_datetime(df_clean["Tag"], dayfirst=True)
    df_clean["Wasser kumuliert Tagesweise [Liter]"] = df_clean.groupby("Tag")["Wasserbedarf [Liter]"].cumsum()

    # --- Plot erstellen ---
    fig = go.Figure()

    # Balken: Wasserverbrauch pro Intervall (linke Achse)
    fig.add_trace(go.Bar(
        x=df_clean["Zeitstempel"],
        y=df_clean["Wasserbedarf [Liter]"],
        name="Wasserbedarf [Liter] pro Intervall",
        marker_color="rgba(0,123,255,0.5)",
        opacity=0.7,
        hovertemplate="Zeit: %{x|%d.%m %H:%M}<br>Wasserbedarf: %{y} Liter"
    ))

    # Linie: kumulierter Wasserverbrauch pro Tag (rechte Achse)
    fig.add_trace(go.Scatter(
        x=df_clean["Zeitstempel"],
        y=df_clean["Wasser kumuliert Tagesweise [Liter]"],
        mode="lines+markers",
        name="Kumulierter Tagesverbrauch [Liter]",
        line=dict(color="darkblue", width=3),
        yaxis="y2",
        hovertemplate="Zeit: %{x|%d.%m %H:%M}<br>Kumuliert heute: %{y} Liter"
    ))

    # --- Layout ---
    fig.update_layout(
        title="Wasserverbrauch pro Intervall und kumuliert pro Tag",
        xaxis_title="Datum & Uhrzeit",
        yaxis=dict(
            title="Wasserbedarf [Liter] pro Intervall",
            showgrid=False
        ),
        yaxis2=dict(
            title="Kumulierter Tagesverbrauch [Liter]",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        template="plotly_white",
        height=550,
        margin=dict(t=80, b=100),
        barmode="overlay",
        xaxis=dict(
            tickformat="%d.%m %H:%M",
            tickangle=45
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def main():
    
    st.set_page_config(page_title="Dashboard", layout="wide")

    st.header("Lastmanagement Wasserstoff")
    df = daten()
    plot_Wasserstoff(df)


    st.header("Lastmanagement Leistung")
    st.info("kommt noch")
    st.header("Lastmanagement Wasser")
    plot_wasser(df)
    
if __name__ == "__main__":
    main()