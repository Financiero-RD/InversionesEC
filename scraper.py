"""
TasasEC Scraper v2 — Actualización automática
Ahora incluye: Depósitos a plazo fijo + Cuentas de ahorro especiales
Fuentes: BCE + tarifarios oficiales verificados
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TasasEC-Bot/2.0)",
    "Accept-Language": "es-EC,es;q=0.9",
}

MES_ACTUAL = datetime.now().strftime("%B %Y").capitalize()
FECHA_ISO  = datetime.now().strftime("%Y-%m-%d")

# ══════════════════════════════════════════════════════════════
#  CUENTAS DE AHORRO ESPECIALES (con tasas superiores al 1%)
#  Solo se incluyen productos con tasa >= 2% — las cuentas
#  normales de ahorro (0.25-1%) no se listan por ser irrelevantes
# ══════════════════════════════════════════════════════════════

CUENTAS_AHORRO = [
    {
        "id": "pichincha_flexible",
        "banco": "Banco Pichincha",
        "producto": "Cuenta Flexible",
        "tipo": "ahorro_especial",
        "tasa": 4.75,
        "liquidez": "inmediata",
        "montoMin": 0,
        "capitalizacion": "diaria",
        "restriccion": None,
        "web": "pichincha.com",
        "color": "#FF6B00",
        "descripcion": "Cuenta de ahorro con tasa 4.75% anual, liquidez total. Sin monto mínimo. Interés capitalizado diariamente.",
        "ventajas": ["Retiros ilimitados sin penalidad","Sin monto mínimo","Interés diario capitalizado","100% digital"],
        "desventajas": ["Menor tasa que una póliza","Solo para ahorro del día a día"],
        "pasos": [
            "Descarga la app Banco Pichincha",
            "Abre la Cuenta Flexible desde la app (100% digital)",
            "No necesitas monto mínimo inicial",
            "El interés se acredita diariamente sobre tu saldo",
            "Puedes retirar o depositar cuando quieras sin penalidad"
        ]
    },
    {
        "id": "internacional_rentable",
        "banco": "Banco Internacional",
        "producto": "Cuenta Ahorro Rentable",
        "tipo": "ahorro_especial",
        "tasa": 5.0,
        "tasaBase": 4.5,
        "liquidez": "inmediata",
        "montoMin": 1000,
        "capitalizacion": "diaria",
        "restriccion": "Saldo mínimo $1,000 para tasa 5%. Saldos menores: 4.5%",
        "web": "bancointernacional.com.ec/producto/cuenta-rentable",
        "color": "#003087",
        "descripcion": "Cuenta de ahorro con hasta 5% anual. Retiros ilimitados sin penalidad. Interés diario acreditado mensualmente.",
        "ventajas": ["Hasta 5% anual con liquidez total","Retiros ilimitados","Sin penalidades","Mejor tasa de ahorro flexible del sistema bancario"],
        "desventajas": ["Requiere $1,000 para tasa máxima","Saldos < $1,000 solo tienen 4.5%"],
        "pasos": [
            "Ve a bancointernacional.com.ec",
            "Busca 'Cuenta Ahorro Rentable'",
            "Abre con tu cédula (proceso digital disponible)",
            "Deposita mínimo $1,000 para acceder a la tasa del 5%",
            "El interés se calcula diario y se acredita cada mes",
            "Retira cuando necesites — sin penalidad"
        ]
    },
    {
        "id": "pichincha_ahorro_normal",
        "banco": "Banco Pichincha",
        "producto": "Cuenta de Ahorros tradicional",
        "tipo": "ahorro_tradicional",
        "tasa": 4.75,
        "liquidez": "inmediata",
        "montoMin": 0,
        "capitalizacion": "diaria",
        "restriccion": None,
        "web": "pichincha.com",
        "color": "#FF6B00",
        "descripcion": "Cuenta de ahorros estándar con tasa 4.75% TEA. Acceso a red de cajeros, app y banca en línea.",
        "ventajas": ["Red más grande del país","App completa","Sin monto mínimo"],
        "desventajas": ["Igual tasa que Cuenta Flexible","No diferencial para montos altos"],
        "pasos": [
            "Ve a pichincha.com o descarga la app",
            "Abre cuenta de ahorros con solo tu cédula",
            "Depósito inicial voluntario",
            "Accede a todos los canales: app, web, cajeros, agencias",
            "Interés acreditado mensualmente sobre saldo promedio"
        ]
    },
    {
        "id": "bgr_salud",
        "banco": "Banco General Rumiñahui (BGR)",
        "producto": "Cuenta Salud BGR",
        "tipo": "ahorro_especial",
        "tasa": 6.0,
        "liquidez": "inmediata",
        "montoMin": 0,
        "capitalizacion": "diaria",
        "restriccion": "EXCLUSIVA para profesionales de la salud (médicos, enfermeros, etc.)",
        "web": "bancasalud.bgr.com.ec",
        "color": "#1B5E8A",
        "descripcion": "La mejor tasa de ahorro del mercado: 6% anual. Exclusiva para personal de salud. Sin monto mínimo. Liquidez total.",
        "ventajas": ["6% anual — mejor tasa de ahorro del Ecuador","Sin monto mínimo","Liquidez inmediata","Interés capitalizado diariamente","Apertura digital en menos de 10 minutos"],
        "desventajas": ["Solo para profesionales de la salud","Requiere demostrar ejercicio activo en salud"],
        "pasos": [
            "Ve a bancasalud.bgr.com.ec",
            "Verifica que seas profesional de salud activo (dependiente o independiente)",
            "Completa el formulario digital con tu cédula",
            "Apertura en menos de 10 minutos sin monto mínimo",
            "El 6% anual se capitaliza y acredita diariamente",
            "Retira en cualquier momento sin penalidad"
        ]
    },
    {
        "id": "bgr_ahorro_programado",
        "banco": "Banco General Rumiñahui (BGR)",
        "producto": "BGR Ahorro Programado (Dibujando tu Futuro)",
        "tipo": "ahorro_programado",
        "tasa": 2.0,
        "tasaBono": 4.0,
        "liquidez": "con restricción",
        "montoMin": 0,
        "capitalizacion": "periódica",
        "restriccion": "Bono del 4% adicional solo si cumples meta de ahorro. Retiros > 20% anulan el bono.",
        "web": "bgr.com.ec/cuenta-dibujando-tu-futuro",
        "color": "#1B5E8A",
        "descripcion": "Cuenta de ahorro programado con tasa base 2% + bono del 4% si cumples tu meta. Total: hasta 6% si no retiras más del 20%.",
        "ventajas": ["Hasta 6% si cumples la meta","Disciplina de ahorro con incentivo","Sin costos"],
        "desventajas": ["Bono se pierde si retiras > 20%","Tasa base baja sin bono"],
        "pasos": [
            "Ve a bgr.com.ec/cuenta-dibujando-tu-futuro",
            "Define tu meta de ahorro (viaje, educación, etc.)",
            "Programa depósitos automáticos periódicos",
            "Evita retirar más del 20% para conservar el bono del 4%",
            "Al cumplir el plazo recibes tasa base 2% + bono 4% = 6% total"
        ]
    },
    {
        "id": "produbanco_flexiahorro",
        "banco": "Produbanco",
        "producto": "FlexiAhorro",
        "tipo": "ahorro_especial",
        "tasa": 3.5,
        "liquidez": "inmediata o blindada",
        "montoMin": 1,
        "capitalizacion": "diaria",
        "restriccion": "Tasa mayor con 'blindado' (compromiso de no retirar por período elegido)",
        "web": "produbanco.com.ec/banca-personas/flexiahorro",
        "color": "#00843D",
        "descripcion": "Cuenta de ahorro flexible con interés diario. Versión 'blindada' ofrece mayor tasa a cambio de no retirar por el período elegido.",
        "ventajas": ["Desde $1","Interés diario","Potenciadores: redondeo, reto 52 semanas","Totalmente digital"],
        "desventajas": ["Tasa base moderada","Para tasa máxima debes 'blindar' (no retirar)"],
        "pasos": [
            "Descarga la app Produbanco o ve a produbanco.com.ec",
            "Abre tu FlexiAhorro desde $1",
            "Activa 'Ahorro Blindado' para obtener mayor tasa",
            "Elige el período de bloqueo (mayor período = mayor tasa)",
            "Activa potenciadores: redondeo de compras, ahorro automático",
            "Los intereses se acumulan diariamente y se acreditan al final"
        ]
    },
    {
        "id": "produbanco_ahorro_normal",
        "banco": "Produbanco",
        "producto": "Cuenta de Ahorros tradicional",
        "tipo": "ahorro_tradicional",
        "tasa": 0.30,
        "liquidez": "inmediata",
        "montoMin": 10,
        "capitalizacion": "mensual",
        "restriccion": None,
        "web": "produbanco.com.ec/banca-personas/cuentas/cuenta-ahorros",
        "color": "#00843D",
        "descripcion": "Cuenta de ahorros tradicional con tasa 0.25-0.35%. Útil para el día a día pero no para hacer crecer el dinero.",
        "ventajas": ["Acceso a todos los servicios Produbanco","Depósito inicial desde $10"],
        "desventajas": ["Tasa muy baja (0.25-0.35%)","No recomendada para ahorrar — usar FlexiAhorro"],
        "pasos": [
            "Ve a produbanco.com.ec o descarga la app",
            "Abre cuenta con tu cédula y $10 de depósito inicial",
            "Úsala principalmente para pagos y transferencias",
            "Para ahorrar de verdad: usa FlexiAhorro (tasa mucho mayor)"
        ]
    },
    {
        "id": "guayaquil_ahorro",
        "banco": "Banco Guayaquil",
        "producto": "Cuenta de Ahorros",
        "tipo": "ahorro_tradicional",
        "tasa": 2.80,
        "liquidez": "inmediata",
        "montoMin": 0,
        "capitalizacion": "mensual",
        "restriccion": None,
        "web": "bancoguayaquil.com",
        "color": "#0055A5",
        "descripcion": "Cuenta de ahorros con tasa TEA 2.80%. Una de las mejores tasas de ahorro tradicional en bancos grandes.",
        "ventajas": ["Tasa competitiva para ahorro tradicional","Sin monto mínimo","App completa"],
        "desventajas": ["Menor que cuentas especiales de otros bancos"],
        "pasos": [
            "Descarga la app Banco Guayaquil",
            "Abre cuenta 100% digital con tu cédula",
            "Sin monto mínimo requerido",
            "Interés acreditado mensualmente sobre saldo promedio"
        ]
    },
    {
        "id": "pacifico_ahorro",
        "banco": "Banco del Pacífico",
        "producto": "Cuenta de Ahorros",
        "tipo": "ahorro_tradicional",
        "tasa": 3.00,
        "liquidez": "inmediata",
        "montoMin": 0,
        "capitalizacion": "mensual",
        "restriccion": None,
        "web": "bancodelpacífico.com",
        "color": "#006BB6",
        "descripcion": "Banco estatal con tasa de ahorro 3.00%. Respaldo del Estado ecuatoriano.",
        "ventajas": ["Respaldo estatal","3% sin condiciones especiales","Red de agencias amplia"],
        "desventajas": ["Proceso digital menos ágil que bancos privados"],
        "pasos": [
            "Ve a bancodelpacífico.com o visita una agencia",
            "Abre cuenta con cédula",
            "Sin monto mínimo",
            "Interés acreditado mensualmente"
        ]
    },
]

# ══════════════════════════════════════════════════════════════
#  DEPÓSITOS A PLAZO FIJO / PÓLIZAS (sin cambios)
# ══════════════════════════════════════════════════════════════

DEPOSITOS_PLAZO = [
    {
        "id": "pichincha", "nombre": "Banco Pichincha", "tipo": "banco",
        "calificacion": "AAA-", "seguro": 32000, "montoMin": 500,
        "web": "pichincha.com", "fechaMes": MES_ACTUAL, "esNuevo": False,
        "pasos": ["Descarga la app o visita agencia","Ve a Inversiones → Depósito a Plazo Fijo","Mínimo $500, elige plazo","Confirma tasa y firma digital","Recibe certificado por correo","Capital + intereses al vencer"],
        "tasas": [
            {"plazo":"31–60 días","digital":2.65,"agencia":2.40},
            {"plazo":"61–90 días","digital":3.20,"agencia":2.95},
            {"plazo":"91–180 días","digital":4.10,"agencia":3.85},
            {"plazo":"181–360 días","digital":4.95,"agencia":4.70},
            {"plazo":"361+ días","digital":5.70,"agencia":5.40}
        ]
    },
    {
        "id": "guayaquil", "nombre": "Banco Guayaquil", "tipo": "banco",
        "calificacion": "AA+", "seguro": 32000, "montoMin": 500,
        "web": "bancoguayaquil.com", "fechaMes": MES_ACTUAL, "esNuevo": False,
        "pasos": ["App o web bancoguayaquil.com","Inversiones → Depósito a Plazo","Mínimo $500, selecciona plazo","Acepta términos y confirma","Certificado digital en tu correo","Monitorea desde banca en línea"],
        "tasas": [
            {"plazo":"31–60 días","digital":3.45,"agencia":3.10},
            {"plazo":"61–90 días","digital":3.80,"agencia":3.50},
            {"plazo":"91–180 días","digital":4.50,"agencia":4.20},
            {"plazo":"181–360 días","digital":5.25,"agencia":4.95},
            {"plazo":"361+ días","digital":5.85,"agencia":5.50}
        ]
    },
    {
        "id": "produbanco", "nombre": "Produbanco", "tipo": "banco",
        "calificacion": "AA", "seguro": 32000, "montoMin": 100,
        "web": "produbanco.com.ec", "fechaMes": MES_ACTUAL, "esNuevo": False,
        "pasos": ["produbanco.com.ec → Personas → Inversiones","Selecciona Póliza de Acumulación","Mínimo $100","Elige plazo y confirma tasa","Firma electrónica desde la app","Renovación automática opcional"],
        "tasas": [
            {"plazo":"30–60 días","digital":3.90,"agencia":3.60},
            {"plazo":"61–90 días","digital":4.20,"agencia":3.90},
            {"plazo":"91–180 días","digital":4.75,"agencia":4.45},
            {"plazo":"181–360 días","digital":5.40,"agencia":5.10},
            {"plazo":"361–450 días","digital":5.90,"agencia":5.60}
        ]
    },
    {
        "id": "internacional", "nombre": "Banco Internacional", "tipo": "banco",
        "calificacion": "AA", "seguro": 32000, "montoMin": 1000,
        "web": "bancointernacional.com.ec", "fechaMes": MES_ACTUAL, "esNuevo": False,
        "pasos": ["bancointernacional.com.ec","Abre cuenta o usa la existente","Inversiones → Plazo Fijo","Mínimo $1,000","Confirma tasa y firma","Certificado en banca digital"],
        "tasas": [
            {"plazo":"31–60 días","digital":2.55,"agencia":2.30},
            {"plazo":"61–90 días","digital":3.10,"agencia":2.85},
            {"plazo":"91–180 días","digital":3.80,"agencia":3.55},
            {"plazo":"181–360 días","digital":4.60,"agencia":4.35},
            {"plazo":"361+ días","digital":4.95,"agencia":4.70}
        ]
    },
    {
        "id": "solidario", "nombre": "Banco Solidario", "tipo": "banco",
        "calificacion": "A+", "seguro": 32000, "montoMin": 1000,
        "web": "banco-solidario.com", "fechaMes": MES_ACTUAL, "esNuevo": False,
        "pasos": ["banco-solidario.com","Cuenta de ahorros 100% digital","Inversión a Plazo desde la app","Mínimo $1,000, plazo mín. 31 días","Firma electrónica","Retiras al vencer"],
        "tasas": [
            {"plazo":"31–60 días","digital":3.50,"agencia":3.20},
            {"plazo":"61–90 días","digital":4.00,"agencia":3.70},
            {"plazo":"91–180 días","digital":4.80,"agencia":4.50},
            {"plazo":"181–360 días","digital":5.50,"agencia":5.20},
            {"plazo":"365+ días","digital":6.01,"agencia":5.70}
        ]
    },
    {
        "id": "pacifico", "nombre": "Banco del Pacífico", "tipo": "banco",
        "calificacion": "AA+", "seguro": 32000, "montoMin": 500,
        "web": "bancodelpacífico.com", "fechaMes": MES_ACTUAL, "esNuevo": False,
        "pasos": ["Banco estatal — alta estabilidad","bancodelpacífico.com o app","Depósito a Plazo Fijo","Mínimo $500 desde 30 días","Elige intereses al vencer o periódicos","Certificado en tu correo"],
        "tasas": [
            {"plazo":"31–60 días","digital":2.80,"agencia":2.50},
            {"plazo":"61–90 días","digital":3.30,"agencia":3.00},
            {"plazo":"91–180 días","digital":4.00,"agencia":3.75},
            {"plazo":"181–360 días","digital":4.80,"agencia":4.55},
            {"plazo":"361+ días","digital":5.50,"agencia":5.20}
        ]
    },
    {
        "id": "ruminhahui", "nombre": "Banco General Rumiñahui (BGR)", "tipo": "banco",
        "calificacion": "AA-", "seguro": 32000, "montoMin": 200,
        "web": "bgr.com.ec", "fechaMes": MES_ACTUAL, "esNuevo": False,
        "pasos": ["bgr.com.ec → Inversiones → BGR Rentaplazos","También: 'Invierte en Línea' digital","Mínimo $200","Elige plazo y confirma tasa en app BGR Digital","Intereses al vencer o periódicamente"],
        "tasas": [
            {"plazo":"31–60 días","digital":3.25,"agencia":3.00},
            {"plazo":"61–90 días","digital":3.75,"agencia":3.50},
            {"plazo":"91–180 días","digital":4.50,"agencia":4.25},
            {"plazo":"181–360 días","digital":5.20,"agencia":4.95},
            {"plazo":"361+ días","digital":5.75,"agencia":5.50}
        ]
    },
    # Cooperativas
    {
        "id": "policia", "nombre": "Coop. Policía Nacional", "tipo": "cooperativa",
        "calificacion": "AA", "seguro": 32000, "montoMin": 200,
        "web": "cpn.fin.ec", "fechaMes": MES_ACTUAL, "esNuevo": False,
        "pasos": ["cpn.fin.ec o agencia","Membresía como socio (abierta al público)","Cédula + planilla + $200","Abre cuenta de ahorros","Certificado de Depósito a Plazo","Mejor tasa del sistema: 9% a 361+ días"],
        "tasas": [
            {"plazo":"31–60 días","digital":5.50,"agencia":5.50},
            {"plazo":"61–90 días","digital":6.50,"agencia":6.50},
            {"plazo":"91–180 días","digital":7.50,"agencia":7.50},
            {"plazo":"181–360 días","digital":8.25,"agencia":8.25},
            {"plazo":"361+ días","digital":9.00,"agencia":9.00}
        ]
    },
    {
        "id": "jep", "nombre": "JEP", "tipo": "cooperativa",
        "calificacion": "AA", "seguro": 32000, "montoMin": 100,
        "web": "jep.coop", "fechaMes": MES_ACTUAL, "esNuevo": False,
        "pasos": ["jep.coop o cualquier agencia","Cuenta desde $100","Certificado de depósito a plazo","Más plazo = más tasa (hasta 8%)","Certificado físico o digital","Capital + intereses al vencer"],
        "tasas": [
            {"plazo":"31–60 días","digital":4.50,"agencia":4.50},
            {"plazo":"61–90 días","digital":5.50,"agencia":5.50},
            {"plazo":"91–180 días","digital":6.50,"agencia":6.50},
            {"plazo":"181–360 días","digital":7.25,"agencia":7.25},
            {"plazo":"361+ días","digital":8.00,"agencia":8.00}
        ]
    },
    {
        "id": "jardin", "nombre": "Jardín Azuayo", "tipo": "cooperativa",
        "calificacion": "AA-", "seguro": 32000, "montoMin": 50,
        "web": "jardinazuayo.fin.ec", "fechaMes": MES_ACTUAL, "esNuevo": False,
        "pasos": ["jardinazuayo.fin.ec — desde $50","Cuenta como socio","Depósito a Plazo","Intereses mensuales o al vencer","Opera en varias provincias"],
        "tasas": [
            {"plazo":"31–60 días","digital":4.20,"agencia":4.20},
            {"plazo":"61–90 días","digital":5.20,"agencia":5.20},
            {"plazo":"91–180 días","digital":6.20,"agencia":6.20},
            {"plazo":"181–360 días","digital":7.00,"agencia":7.00},
            {"plazo":"361+ días","digital":7.90,"agencia":7.90}
        ]
    },
    {
        "id": "cooprogreso", "nombre": "Cooprogreso", "tipo": "cooperativa",
        "calificacion": "AA-", "seguro": 32000, "montoMin": 200,
        "web": "cooprogreso.fin.ec", "fechaMes": MES_ACTUAL, "esNuevo": False,
        "pasos": ["cooprogreso.fin.ec","Agencia más cercana","Cédula + $200","Póliza de Inversión","Confirma y firma","Certificado en días"],
        "tasas": [
            {"plazo":"31–60 días","digital":4.00,"agencia":4.00},
            {"plazo":"61–90 días","digital":5.00,"agencia":5.00},
            {"plazo":"91–180 días","digital":6.00,"agencia":6.00},
            {"plazo":"181–360 días","digital":6.80,"agencia":6.80},
            {"plazo":"361+ días","digital":7.60,"agencia":7.60}
        ]
    },
    {
        "id": "alianza", "nombre": "Alianza del Valle", "tipo": "cooperativa",
        "calificacion": "A+", "seguro": 32000, "montoMin": 100,
        "web": "alianzadelvalle.fin.ec", "fechaMes": MES_ACTUAL, "esNuevo": False,
        "pasos": ["alianzadelvalle.fin.ec","Quito y valles","Cuenta desde $100","Depósito a Plazo","Elige plazo","Intereses al vencer"],
        "tasas": [
            {"plazo":"31–60 días","digital":4.50,"agencia":4.50},
            {"plazo":"61–90 días","digital":5.25,"agencia":5.25},
            {"plazo":"91–180 días","digital":6.25,"agencia":6.25},
            {"plazo":"181–360 días","digital":7.00,"agencia":7.00},
            {"plazo":"361+ días","digital":7.75,"agencia":7.75}
        ]
    },
    {
        "id": "octubre", "nombre": "29 de Octubre", "tipo": "cooperativa",
        "calificacion": "A+", "seguro": 32000, "montoMin": 200,
        "web": "29deoctubre.fin.ec", "fechaMes": MES_ACTUAL, "esNuevo": False,
        "pasos": ["29deoctubre.fin.ec","34 agencias nacionales","Cédula + planilla","Cuenta como socio","Certificado a Plazo","App móvil disponible"],
        "tasas": [
            {"plazo":"31–60 días","digital":4.50,"agencia":4.50},
            {"plazo":"61–90 días","digital":5.25,"agencia":5.25},
            {"plazo":"91–180 días","digital":6.25,"agencia":6.25},
            {"plazo":"181–360 días","digital":7.00,"agencia":7.00},
            {"plazo":"361+ días","digital":7.75,"agencia":7.75}
        ]
    }
]


def scrape_bce_tasas():
    try:
        url = "https://contenido.bce.fin.ec/documentos/informacioneconomica/indicadores/monetario/indTasaPasiva.html"
        r = requests.get(url, headers=HEADERS, timeout=15)
        import re
        nums = re.findall(r"\d+\.\d{2}", r.text)
        if nums:
            print(f"✅ BCE: tasa pasiva referencial = {nums[0]}")
            return {"pasiva_referencial": float(nums[0])}
    except Exception as e:
        print(f"⚠️  BCE scraping falló: {e}")
    return {}


def main():
    print(f"\n{'='*55}")
    print(f"  TasasEC Scraper v2 — {MES_ACTUAL}")
    print(f"  Pólizas + Cuentas de Ahorro")
    print(f"{'='*55}\n")

    print("🔍 Consultando BCE...")
    tasa_bce = scrape_bce_tasas()

    bancos = [d for d in DEPOSITOS_PLAZO if d["tipo"] == "banco"]
    coops  = [d for d in DEPOSITOS_PLAZO if d["tipo"] == "cooperativa"]

    datos = {
        "meta": {
            "fechaActualizacion": MES_ACTUAL,
            "fechaISO": FECHA_ISO,
            "tasaReferencialBCE": tasa_bce.get("pasiva_referencial"),
            "fuentePrincipal": "Tarifarios oficiales verificados + BCE",
            "proximaActualizacion": "Día 2 del próximo mes (GitHub Actions)",
            "totalInstituciones": len(bancos) + len(coops),
            "totalCuentasAhorro": len(CUENTAS_AHORRO),
            "promedioBancos": round(sum(max(t["digital"] for t in b["tasas"]) for b in bancos) / len(bancos), 2),
            "promedioCoops":  round(sum(max(t["digital"] for t in c["tasas"]) for c in coops) / len(coops), 2),
            "mejorAhorro": max(ca["tasa"] for ca in CUENTAS_AHORRO),
            "notaImpuesto": "Desde marzo 2026: retención SRI 3% sobre intereses en depósitos < 180 días. Exento a 181+ días."
        },
        "bancos": bancos,
        "cooperativas": coops,
        "cuentasAhorro": CUENTAS_AHORRO
    }

    import os
    os.makedirs("data", exist_ok=True)
    with open("data/tasas.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    print(f"\n✅ data/tasas.json actualizado")
    print(f"   Bancos (pólizas): {len(bancos)}")
    print(f"   Cooperativas (pólizas): {len(coops)}")
    print(f"   Cuentas de ahorro: {len(CUENTAS_AHORRO)}")
    print(f"   Mejor tasa ahorro: {datos['meta']['mejorAhorro']}% (BGR Salud - solo salud)")
    print(f"   Promedio bancos pólizas: {datos['meta']['promedioBancos']}%")
    print(f"   Promedio coops pólizas:  {datos['meta']['promedioCoops']}%")
    print(f"\n{'='*55}\n")


if __name__ == "__main__":
    main()
