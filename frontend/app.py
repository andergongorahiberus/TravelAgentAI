import json
import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

# Carga .env y añade backend al path ANTES de los imports del proyecto
load_dotenv(Path(__file__).parents[1] / ".env", override=True)
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

import streamlit as st  # noqa: E402
from agents.orchestrator import create_travel_graph  # noqa: E402
from tools.config.destinations_schema import UserTravelQuery  # noqa: E402


# ── Grafo instanciado una sola vez por sesión de Streamlit ────────────────────
@st.cache_resource
def get_graph():
    return create_travel_graph()


# ── UI ────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Travel Planner AI", page_icon="✈️", layout="wide")
st.title("✈️ Travel Planner AI")
st.write("Rellena los datos de tu viaje y los agentes buscarán destinos, clima, precios e itinerario.")

with st.form("travel_input_form"):
    col1, col2 = st.columns(2)
    with col1:
        origin = st.text_input("Ciudad de origen", placeholder="ej. Madrid")
        theme = st.selectbox(
            "Temática del viaje",
            ["playa", "montaña", "ciudad", "rural", "aventura"],
        )
        budget = st.number_input(
            "Presupuesto total (€)",
            min_value=100,
            max_value=20000,
            value=1500,
            step=100,
        )
    with col2:
        departure_date = st.date_input(
            "Fecha de salida", value=date.today() + timedelta(days=30)
        )
        return_date = st.date_input(
            "Fecha de regreso", value=date.today() + timedelta(days=37)
        )

    submit = st.form_submit_button("🚀 Planificar viaje", use_container_width=True)

# ── Ejecución del grafo ───────────────────────────────────────────────────────
if submit:
    if not origin:
        st.warning("Indica una ciudad de origen.")
    elif return_date <= departure_date:
        st.error("La fecha de regreso debe ser posterior a la de salida.")
    else:
        try:
            query = UserTravelQuery(
                origin=origin,
                theme=theme,
                budget_eur=float(budget),
                departure_date=departure_date,
                return_date=return_date,
            )
        except Exception as e:
            st.error(f"Error de validación: {e}")
            st.stop()

        state = query.model_dump(mode="json")

        prompt = (
            f"Planifica un viaje de {state['theme']} desde {state['origin']} "
            f"del {state['departure_date']} al {state['return_date']} "
            f"con un presupuesto de {state['budget_eur']}€."
        )

        with st.spinner("Los agentes están trabajando… esto puede tardar unos minutos."):
            try:
                graph = get_graph()
                result = graph(prompt, invocation_state=state)
                raw = str(result.message) if hasattr(result, "message") else str(result)
            except Exception as e:
                st.error(f"Error durante la ejecución: {e}")
                st.stop()

        st.success("¡Plan generado!")
        st.divider()

        # Intenta parsear como JSON y mostrarlo bonito; si no, texto plano
        try:
            data = json.loads(raw)
            st.json(data)
        except (json.JSONDecodeError, TypeError):
            st.markdown(raw)

        st.download_button(
            "⬇️ Descargar resultado",
            data=raw,
            file_name="travel_plan.json",
            mime="application/json",
        )
