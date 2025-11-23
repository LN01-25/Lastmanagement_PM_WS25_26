import pandas as pd
import plotly.graph_objects as go
import numpy as np
import streamlit as st

# -------------------------
# DATEN EINLESEN
# -------------------------
def daten():
    return pd.read_excel("Lastmanagement.xlsx")


# -------------------------
# PLOT: WASSERSTOFF
# -------------------------
def plot_wasserstoff(df):
    df_clean = df[[
        "Tag",
        "Uhrzeit",
        "Speicherveränderung [kg]",
        "externe Belieferung",
        "Speicherstand kummuliert [kg]",
        "SOC [%]",
        "Sperrzeiten_weil_Tanken",
        "Zeit für Elektrolyseur"
    ]].copy()

    df_clean["SOC [%]"] = pd.to_numeric(df_clean["SOC [%]"], errors="coerce")

    df_clean["Startzeit"] = df_clean["Uhrzeit"].str.split("–").str[0]
    df_clean["Zeitstempel"] = pd.to_datetime(
        df_clean["Tag"].astype(str) + " " + df_clean["Startzeit"],
        dayfirst=True, errors="coerce"
    )

    df_clean["Bar_Farbe"] = np.where(
        df_clean["Speicherveränderung [kg]"] >= 0,
        "rgba(0,180,0,0.7)",
        "rgba(220,0,0,0.7)"
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_clean["Zeitstempel"],
        y=df_clean["Speicherveränderung [kg]"],
        name="Speicherveränderung [kg]",
        marker_color=df_clean["Bar_Farbe"],
        opacity=0.85
    ))

    fig.add_trace(go.Scatter(
        x=df_clean["Zeitstempel"],
        y=df_clean["SOC [%]"],
        mode="lines+markers",
        name="SOC (0–1)",
        line=dict(color="royalblue", width=3),
        yaxis="y2"
    ))

    fig.add_trace(go.Bar(
        x=df_clean["Zeitstempel"],
        y=df_clean["externe Belieferung"],
        name="Externe Belieferung [kg]",
        opacity=0.6,
        marker_color="rgba(0,120,255,0.6)"
    ))

    fig.update_layout(
        title="Speicherverlauf Wasserstoff",
        xaxis=dict(title="Zeit"),
        yaxis=dict(title="kg"),
        yaxis2=dict(overlaying="y", side="right", title="SOC"),
        template="plotly_white",
        barmode="overlay",
        height=550
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# PLOT: WASSER
# -------------------------
def plot_wasser(df):
    df_clean = df[["Tag", "Uhrzeit", "Wasserbedarf [Liter]"]].copy()

    df_clean["Startzeit"] = df_clean["Uhrzeit"].str.split("–").str[0]
    df_clean["Zeitstempel"] = pd.to_datetime(
        df_clean["Tag"].astype(str) + " " + df_clean["Startzeit"],
        dayfirst=True, errors="coerce"
    )

    df_clean["Tag"] = pd.to_datetime(df_clean["Tag"], dayfirst=True)
    df_clean["Wasser kumuliert Tagesweise [Liter]"] = df_clean.groupby("Tag")["Wasserbedarf [Liter]"].cumsum()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_clean["Zeitstempel"],
        y=df_clean["Wasserbedarf [Liter]"],
        name="Wasserbedarf [Liter]",
        opacity=0.7
    ))

    fig.add_trace(go.Scatter(
        x=df_clean["Zeitstempel"],
        y=df_clean["Wasser kumuliert Tagesweise [Liter]"],
        mode="lines+markers",
        name="Kumulierter Tagesverbrauch [Liter]",
        yaxis="y2",
        line=dict(width=3)
    ))

    fig.update_layout(
        title="Wasserverbrauch",
        yaxis=dict(title="Wasserbedarf [Liter]"),
        yaxis2=dict(title="Kumuliert [Liter]", overlaying="y", side="right"),
        template="plotly_white",
        height=550
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# PLOT: STROMBEZUG (STACK)
# -------------------------
def plot_strom(df):
    kwh_cols = [
        "Elektrolyseur [kWh]",
        "Verdichter [kWh]",
        "Dispenser [kWh]",
        "Druckluftkompressor [kWh]",
        "Wasseraufbereitung [kWh]"
    ]

    df_clean = df[["Tag", "Uhrzeit"] + kwh_cols + ["SUMME [kWh]"]].copy()

    df_clean["Startzeit"] = df_clean["Uhrzeit"].str.split("–").str[0]
    df_clean["Zeitstempel"] = pd.to_datetime(
        df_clean["Tag"].astype(str) + " " + df_clean["Startzeit"],
        dayfirst=True, errors="coerce"
    )

    df_clean["Tag"] = pd.to_datetime(df_clean["Tag"], dayfirst=True)
    df_clean["Kumuliert Tagesweise [kWh]"] = df_clean.groupby("Tag")["SUMME [kWh]"].cumsum()

    fig = go.Figure()

    for col in kwh_cols:
        fig.add_trace(go.Bar(
            x=df_clean["Zeitstempel"],
            y=df_clean[col],
            name=col,
            opacity=0.85
        ))

    fig.add_trace(go.Scatter(
        x=df_clean["Zeitstempel"],
        y=df_clean["Kumuliert Tagesweise [kWh]"],
        mode="lines+markers",
        name="Kumuliert Tagesweise [kWh]",
        yaxis="y2",
        line=dict(width=3, dash="dot")
    ))

    fig.update_layout(
        title="Strombezug Komponenten",
        barmode="stack",
        yaxis=dict(title="kWh"),
        yaxis2=dict(title="Kumuliert [kWh]", overlaying="y", side="right"),
        template="plotly_white",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# KOSTEN: STROM
# -------------------------
def plot_kosten_strom(df):
    df_clean = df[["Tag", "Uhrzeit", "Strombeschaffungskosten [€]"]].copy()

    df_clean["Startzeit"] = df_clean["Uhrzeit"].str.split("–").str[0]
    df_clean["Zeitstempel"] = pd.to_datetime(
        df_clean["Tag"].astype(str) + " " + df_clean["Startzeit"],
        dayfirst=True, errors="coerce"
    )

    df_clean["Tag"] = pd.to_datetime(df_clean["Tag"], dayfirst=True)
    df_clean["Kumuliert Tagesweise [€]"] = df_clean.groupby("Tag")["Strombeschaffungskosten [€]"].cumsum()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_clean["Zeitstempel"],
        y=df_clean["Strombeschaffungskosten [€]"],
        name="Strombeschaffungskosten [€]",
        opacity=0.85
    ))

    fig.add_trace(go.Scatter(
        x=df_clean["Zeitstempel"],
        y=df_clean["Kumuliert Tagesweise [€]"],
        mode="lines+markers",
        name="Kumuliert [€]",
        yaxis="y2",
        line=dict(width=3, dash="dot")
    ))

    fig.update_layout(
        title="Kosten Strombeschaffung",
        barmode="stack",
        yaxis=dict(title="Kosten [€]"),
        yaxis2=dict(title="Kumuliert [€]", overlaying="y", side="right"),
        template="plotly_white",
        height=550
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# KOSTEN: WASSER
# -------------------------
def plot_kosten_wasser(df):
    df_clean = df[["Tag", "Uhrzeit", "Wasserkosten [€]"]].copy()

    df_clean["Startzeit"] = df_clean["Uhrzeit"].str.split("–").str[0]
    df_clean["Zeitstempel"] = pd.to_datetime(
        df_clean["Tag"].astype(str) + " " + df_clean["Startzeit"],
        dayfirst=True, errors="coerce"
    )

    df_clean["Tag"] = pd.to_datetime(df_clean["Tag"], dayfirst=True)
    df_clean["Kumuliert Tagesweise [€]"] = df_clean.groupby("Tag")["Wasserkosten [€]"].cumsum()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_clean["Zeitstempel"],
        y=df_clean["Wasserkosten [€]"],
        name="Wasserkosten [€]",
        opacity=0.85
    ))

    fig.add_trace(go.Scatter(
        x=df_clean["Zeitstempel"],
        y=df_clean["Kumuliert Tagesweise [€]"],
        mode="lines+markers",
        name="Kumuliert [€]",
        yaxis="y2",
        line=dict(width=3, dash="dot")
    ))

    fig.update_layout(
        title="Kosten Wasser",
        barmode="stack",
        yaxis=dict(title="Kosten [€]"),
        yaxis2=dict(title="Kumuliert [€]", overlaying="y", side="right"),
        template="plotly_white",
        height=550
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# KOSTEN: GESAMT
# -------------------------
def plot_kosten_gesamt(df):
    df_clean = df[[
        "Tag",
        "Uhrzeit",
        "Strombeschaffungskosten [€]",
        "Wasserkosten [€]",
        "Summe kosten [€]"
    ]].copy()

    df_clean["Startzeit"] = df_clean["Uhrzeit"].str.split("–").str[0]
    df_clean["Zeitstempel"] = pd.to_datetime(
        df_clean["Tag"].astype(str) + " " + df_clean["Startzeit"],
        dayfirst=True, errors="coerce"
    )

    df_clean["Tag"] = pd.to_datetime(df_clean["Tag"], dayfirst=True)
    df_clean["Kumuliert Tagesweise [€]"] = df_clean.groupby("Tag")["Summe kosten [€]"].cumsum()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_clean["Zeitstempel"],
        y=df_clean["Strombeschaffungskosten [€]"],
        name="Strombeschaffungskosten [€]",
        opacity=0.85
    ))

    fig.add_trace(go.Bar(
        x=df_clean["Zeitstempel"],
        y=df_clean["Wasserkosten [€]"],
        name="Wasserkosten [€]",
        opacity=0.85
    ))

    fig.add_trace(go.Scatter(
        x=df_clean["Zeitstempel"],
        y=df_clean["Kumuliert Tagesweise [€]"],
        mode="lines+markers",
        name="Gesamtkosten kumuliert [€]",
        yaxis="y2",
        line=dict(width=3, dash="dot")
    ))

    fig.update_layout(
        title="Gesamtkosten",
        barmode="stack",
        yaxis=dict(title="Kosten [€]"),
        yaxis2=dict(title="Kumuliert [€]", overlaying="y", side="right"),
        template="plotly_white",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# HAUPTPROGRAMM
# -------------------------
def main():
    st.set_page_config(page_title="Dashboard", layout="wide")

    st.sidebar.title("📊 Navigation")
    auswahl = st.sidebar.radio("Wähle eine Ansicht:", ["Lastmanagement", "Kostenfunktionen"])

    df = daten()

    tage = pd.to_datetime(df["Tag"], dayfirst=True).dt.date.unique()
    tage_auswahl = ["Gesamter Zeitraum"] + [str(t) for t in tage]

    ausgewählt = st.sidebar.selectbox("Zeitraum auswählen:", tage_auswahl)

    if ausgewählt != "Gesamter Zeitraum":
        df_filtered = df[df["Tag"] == ausgewählt]
    else:
        df_filtered = df.copy()

    if auswahl == "Lastmanagement":
        st.header("Lastmanagement Wasserstoff")
        plot_wasserstoff(df_filtered)

        st.header("Lastmanagement Strom")
        plot_strom(df_filtered)

        st.header("Lastmanagement Wasser")
        plot_wasser(df_filtered)

    elif auswahl == "Kostenfunktionen":
        st.header("Kosten – Strom")
        plot_kosten_strom(df_filtered)

        st.header("Kosten – Wasser")
        plot_kosten_wasser(df_filtered)

        st.header("Kosten – Gesamt")
        plot_kosten_gesamt(df_filtered)


if __name__ == "__main__":
    main()
