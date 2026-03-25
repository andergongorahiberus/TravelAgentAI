from strands import tool


@tool
def calculate_climate_score(
    avg_temp_max: float,
    avg_temp_min: float,
    avg_precipitation_mm: float,
    avg_sun_hours: float,
    avg_wind_speed_kmh: float,
    theme: str,
) -> str:
    """Calcula un score climático (0-100) para un destino según la temática del viaje.

    El score indica cuán favorable es el clima para el tipo de viaje elegido.
    Un score >= 70 es bueno, >= 50 es aceptable, < 40 se descarta.

    Args:
        avg_temp_max: Temperatura máxima media diaria en °C
        avg_temp_min: Temperatura mínima media diaria en °C
        avg_precipitation_mm: Precipitación media diaria en mm
        avg_sun_hours: Horas de sol medias por día
        avg_wind_speed_kmh: Velocidad media del viento en km/h
        theme: Temática del viaje: playa, montaña, ciudad o rural

    Returns:
        Score climático con desglose detallado de cada factor
    """
    theme = theme.lower().strip()
    avg_temp = (avg_temp_max + avg_temp_min) / 2

    # --- Score por temperatura (0-30 puntos) ---
    temp_score = 0
    if theme == "playa":
        if 26 <= avg_temp_max <= 35:
            temp_score = 30
        elif 22 <= avg_temp_max < 26:
            temp_score = 20
        elif 35 < avg_temp_max <= 40:
            temp_score = 15  # demasiado calor
        else:
            temp_score = 5
    elif theme == "montaña":
        if 15 <= avg_temp_max <= 28:
            temp_score = 30
        elif 10 <= avg_temp_max < 15:
            temp_score = 20
        elif 5 <= avg_temp_max < 10:
            temp_score = 15  # frío pero viable
        else:
            temp_score = 5
    elif theme == "ciudad":
        if 18 <= avg_temp_max <= 30:
            temp_score = 30
        elif 14 <= avg_temp_max < 18:
            temp_score = 20
        elif 30 < avg_temp_max <= 35:
            temp_score = 15  # calor pero se aguanta
        else:
            temp_score = 5
    elif theme == "rural":
        if 18 <= avg_temp_max <= 30:
            temp_score = 30
        elif 14 <= avg_temp_max < 18:
            temp_score = 20
        else:
            temp_score = 10

    # --- Score por lluvia (0-30 puntos) ---
    rain_score = 0
    if theme == "playa":
        # Playa: muy sensible a la lluvia
        if avg_precipitation_mm < 1:
            rain_score = 30
        elif avg_precipitation_mm < 3:
            rain_score = 20
        elif avg_precipitation_mm < 6:
            rain_score = 10
        elif avg_precipitation_mm < 10:
            rain_score = 0
        else:
            rain_score = -15  # lluvia intensa es un descarte para playa
    elif theme == "montaña":
        # Montaña: algo más tolerante
        if avg_precipitation_mm < 3:
            rain_score = 30
        elif avg_precipitation_mm < 8:
            rain_score = 20
        elif avg_precipitation_mm < 15:
            rain_score = 10
        else:
            rain_score = 0
    else:
        # Ciudad / Rural: tolerancia media
        if avg_precipitation_mm < 2:
            rain_score = 30
        elif avg_precipitation_mm < 5:
            rain_score = 20
        elif avg_precipitation_mm < 10:
            rain_score = 10
        else:
            rain_score = 0

    # --- Score por sol (0-20 puntos) ---
    sun_score = 0
    if theme == "playa":
        # Playa: necesita mucho sol (< 7h no compensa para día de playa)
        if avg_sun_hours >= 10:
            sun_score = 20
        elif avg_sun_hours >= 7:
            sun_score = 15
        else:
            sun_score = 0
    else:
        if avg_sun_hours >= 8:
            sun_score = 20
        elif avg_sun_hours >= 5:
            sun_score = 15
        elif avg_sun_hours >= 3:
            sun_score = 10
        else:
            sun_score = 5

    # --- Score por viento (0-20 puntos) ---
    wind_score = 0
    if theme == "playa":
        # Playa: el viento molesta mucho
        if avg_wind_speed_kmh < 15:
            wind_score = 20
        elif avg_wind_speed_kmh < 25:
            wind_score = 12
        elif avg_wind_speed_kmh < 35:
            wind_score = 5
        else:
            wind_score = 0
    elif theme == "montaña":
        # Montaña: viento fuerte es peligroso
        if avg_wind_speed_kmh < 20:
            wind_score = 20
        elif avg_wind_speed_kmh < 30:
            wind_score = 12
        else:
            wind_score = 3
    else:
        # Ciudad/Rural: menos relevante
        if avg_wind_speed_kmh < 25:
            wind_score = 20
        elif avg_wind_speed_kmh < 40:
            wind_score = 12
        else:
            wind_score = 5

    # --- Total ---
    total = temp_score + rain_score + sun_score + wind_score
    total = max(0, min(100, total))

    return (
        f"Score climático: {total}/100\n"
        f"  Temperatura: {temp_score}/30 (max={avg_temp_max:.1f}°C, min={avg_temp_min:.1f}°C, media={avg_temp:.1f}°C)\n"
        f"  Lluvia: {rain_score}/30 (media={avg_precipitation_mm:.1f}mm/día)\n"
        f"  Sol: {sun_score}/20 ({avg_sun_hours:.1f}h/día)\n"
        f"  Viento: {wind_score}/20 ({avg_wind_speed_kmh:.1f}km/h)\n"
        f"  Temática: {theme}"
    )
