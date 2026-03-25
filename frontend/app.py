import json
import re
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
from tools.config.planification_schema import TravelReport  # noqa: E402


# ── Grafo instanciado una sola vez por sesión de Streamlit ────────────────────
@st.cache_resource
def get_graph():
    return create_travel_graph()


# Nombres de los tools de structured_output_model por nodo
_STRUCTURED_TOOL_NAMES = {
    "planner": "TravelReport",
    "financial": "FinancialAgentResponse",
    "weather": "ListaWeather",
    "destinations": "ListaDestinos",
}


# ── Extracción del texto final del GraphResult ────────────────────────────────
def extract_final_text(graph_result) -> str:
    """Navega el GraphResult buscando primero el toolUse del structured_output_model
    (que es donde Strands mete el JSON validado), y si no, el último bloque de texto."""
    for node_name in ("planner", "financial", "weather", "destinations"):
        node = getattr(graph_result, "results", {}).get(node_name)
        if node is None:
            continue
        message = getattr(getattr(node, "result", None), "message", None)
        if not isinstance(message, dict):
            continue
        content = message.get("content", [])

        # 1. Busca el toolUse del schema estructurado (TravelReport, etc.)
        target_tool = _STRUCTURED_TOOL_NAMES.get(node_name)
        for block in content:
            if (isinstance(block, dict)
                    and "toolUse" in block
                    and block["toolUse"].get("name") == target_tool):
                return json.dumps(block["toolUse"].get("input", {}))

        # 2. Fallback: último bloque de texto no vacío
        for block in reversed(content):
            if isinstance(block, dict) and "text" in block:
                text = block["text"].strip()
                if text:
                    return text

    return str(graph_result)


def extract_json_from_text(text: str) -> dict | None:
    """Extrae el primer bloque JSON válido del texto aunque venga con prosa."""
    # Intento directo
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass
    # Busca bloque ```json ... ```
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # Busca el primer { ... } de nivel raíz
    m = re.search(r"(\{.*\})", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    return None


# ── Renderizado de TravelReport ───────────────────────────────────────────────
def render_travel_report(data: dict):
    report = TravelReport(**data)

    st.header(f"Destino: {report.destination}")
    st.info(report.summary_report)
    st.divider()

    # Itinerario
    st.subheader("Itinerario")
    for day in report.itinerary:
        with st.expander(f"Día {day.day} — {day.title}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Mañana:** {day.morning}")
                st.markdown(f"**Mediodía:** {day.lunch}")
            with col2:
                st.markdown(f"**Tarde:** {day.afternoon}")
                st.markdown(f"**Noche:** {day.evening}")
            if day.rain_plan:
                st.caption(f"Plan lluvia: {day.rain_plan}")

    st.divider()

    # Presupuesto
    st.subheader("Desglose de presupuesto")
    rows = [{"Concepto": b.item, "Precio (€)": b.price_eur, "Detalle": b.details}
            for b in report.budget_breakdown]
    st.table(rows)
    st.metric("Total estimado", f"{report.total_estimated_price:.0f} €")

    st.divider()

    # Consejos
    st.subheader("Consejos generales")
    for tip in report.general_tips:
        st.markdown(f"- {tip}")


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

    submit = st.form_submit_button("Planificar viaje", use_container_width=True)

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
                result = get_graph()(prompt, invocation_state=state)
                raw = extract_final_text(result)
            except Exception as e:
                st.error(f"Error durante la ejecución: {e}")
                st.stop()

        st.success("¡Plan generado!")
        st.divider()

        data = extract_json_from_text(raw)
        if data and "itinerary" in data:
            try:
                render_travel_report(data)
            except Exception:
                st.markdown(raw)
        elif data:
            st.json(data)
        else:
            st.markdown(raw)

        st.download_button(
            "Descargar resultado",
            data=raw,
            file_name="travel_plan.json",
            mime="application/json",
        )
