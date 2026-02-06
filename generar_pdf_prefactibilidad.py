import json
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generar_pdf(json_path: str):
    path = Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))

    pdf_path = path.with_suffix(".pdf")

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Titulo",
        fontSize=16,
        leading=20,
        spaceAfter=14,
        alignment=1  # centrado
    ))
    styles.add(ParagraphStyle(
        name="Subtitulo",
        fontSize=12,
        leading=14,
        spaceBefore=12,
        spaceAfter=6,
        fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="Texto",
        fontSize=10,
        leading=14,
        spaceAfter=4
    ))

    story = []

    # --- TÍTULO ---
    story.append(Paragraph("INFORME DE PREFACTIBILIDAD URBANÍSTICA", styles["Titulo"]))
    story.append(Spacer(1, 12))

    # --- DATOS GENERALES ---
    story.append(Paragraph("DATOS GENERALES", styles["Subtitulo"]))
    story.append(Paragraph(f"Dirección: {data.get('direccion')}", styles["Texto"]))
    story.append(Paragraph(f"SMP: {data.get('smp')}", styles["Texto"]))
    story.append(Paragraph(
        f"Comuna / Barrio: {data.get('comuna')} – {data.get('barrio')}",
        styles["Texto"]
    ))

    # --- PARCELA ---
    story.append(Spacer(1, 8))
    story.append(Paragraph("DATOS DE PARCELA", styles["Subtitulo"]))
    story.append(Paragraph(
        f"Superficie del lote: {data.get('superficie_parcela_m2')} m²",
        styles["Texto"]
    ))
    story.append(Paragraph(
        f"Altura máxima permitida: {data.get('altura_max_plano_limite_m')} m",
        styles["Texto"]
    ))
    story.append(Paragraph(
        f"FOT: {data.get('fot', {}).get('medianera')}",
        styles["Texto"]
    ))
    story.append(Paragraph(
        f"Superficie estimada construible: {data.get('m2_estimados_por_fot')} m²",
        styles["Texto"]
    ))

    # --- CONDICIONES ---
    story.append(Spacer(1, 8))
    story.append(Paragraph("CONDICIONES URBANÍSTICAS", styles["Subtitulo"]))
    story.append(Paragraph(
        f"Distrito (CPU histórico): {data.get('distrito_cpu_historico')}",
        styles["Texto"]
    ))

    afect = data.get("afectaciones", {})
    story.append(Paragraph(
        f"Afectaciones relevantes: "
        f"Riesgo hídrico={afect.get('riesgo_hidrico')}, "
        f"Ensanche={afect.get('ensanche')}, "
        f"Apertura={afect.get('apertura')}",
        styles["Texto"]
    ))

    # --- OBSERVACIÓN ---
    story.append(Spacer(1, 10))
    story.append(Paragraph("OBSERVACIONES", styles["Subtitulo"]))
    story.append(Paragraph(
        "La presente información constituye una estimación preliminar de "
        "prefactibilidad urbanística, sujeta a verificación ante los organismos "
        "competentes de la Ciudad Autónoma de Buenos Aires.",
        styles["Texto"]
    ))

    doc.build(story)
    print("PDF generado:", pdf_path.resolve())


if __name__ == "__main__":
    generar_pdf("salida_prefactibilidad/prefactibilidad_044-097A-032A_RESUMEN.json")
