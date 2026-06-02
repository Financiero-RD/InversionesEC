# 🇪🇨 TasasEC — Tasas de inversión Ecuador

> Sitio web con actualización **automática mensual** via GitHub Actions.  
> Sin tokens, sin APIs de pago, completamente gratis para siempre.

---

## 🤖 Cómo funciona

```
Día 2 de cada mes
      ↓
GitHub Actions ejecuta scraper.py
      ↓
scraper.py actualiza data/tasas.json
      ↓
GitHub hace commit automático
      ↓
El sitio web lee el JSON actualizado
      ↓
¡Usuarios ven tasas del mes actual!
```

---

## 🚀 Cómo publicarlo (5 pasos)

### Paso 1 — Crear cuenta en GitHub
Ve a [github.com](https://github.com) y crea una cuenta gratuita.

### Paso 2 — Crear un repositorio nuevo
1. Haz clic en **"New repository"**
2. Nombre: `tasasec` (o el que quieras)
3. Marca **"Public"**
4. Haz clic en **"Create repository"**

### Paso 3 — Subir estos archivos
Sube los archivos con esta estructura exacta:
```
tasasec/
├── .github/
│   └── workflows/
│       └── scraper.yml       ← el robot
├── data/
│   └── tasas.json            ← los datos (se actualiza automáticamente)
├── docs/
│   └── index.html            ← el sitio web
├── scraper.py                ← el script Python
└── README.md                 ← este archivo
```

### Paso 4 — Activar GitHub Pages
1. En tu repositorio, ve a **Settings** → **Pages**
2. En "Source" selecciona **Deploy from a branch**
3. Branch: **main**, Folder: **/docs**
4. Guarda — en 2 minutos tu sitio estará en:
   `https://TU-USUARIO.github.io/tasasec`

### Paso 5 — Verificar que el robot funciona
1. Ve a la pestaña **Actions** en tu repositorio
2. Verás el workflow "Actualizar Tasas Ecuador"
3. Haz clic en **"Run workflow"** para probarlo manualmente
4. Deberías ver un nuevo commit en `data/tasas.json`

---

## 📅 Calendario automático

| Cuándo | Qué pasa |
|--------|----------|
| Día 2 de cada mes, 8:00 AM Ecuador | Robot corre automáticamente |
| Cualquier momento | Puedes correrlo manualmente desde Actions |

---

## 📁 Estructura de archivos

### `data/tasas.json`
El archivo de datos. GitHub Actions lo actualiza cada mes.
No necesitas tocarlo manualmente.

### `scraper.py`
El robot. Contiene:
- Datos base verificados de los 13 bancos y cooperativas
- Lógica para intentar scraping del BCE
- Genera el JSON actualizado con metadatos del mes

### `.github/workflows/scraper.yml`
Configura cuándo y cómo corre el robot.
Actualmente: día 2 de cada mes a las 13:00 UTC (8:00 AM Ecuador).

### `docs/index.html`
El sitio web completo. Lee `data/tasas.json` con `fetch('../data/tasas.json')`.

---

## 🏦 Instituciones incluidas

**Bancos (7):**
- Banco Pichincha (AAA-)
- Banco Guayaquil (AA+)
- Produbanco (AA)
- Banco Internacional (AA)
- Banco Solidario (A+)
- Banco del Pacífico (AA+)
- **Banco General Rumiñahui — BGR (AA-)** ← nuevo

**Cooperativas Segmento 1 (6):**
- Coop. Policía Nacional (AA) — mejor tasa del sistema: 9%
- JEP (AA)
- Jardín Azuayo (AA-)
- Cooprogreso (AA-)
- Alianza del Valle (A+)
- 29 de Octubre (A+)

---

## ✏️ Cómo actualizar las tasas manualmente

Si quieres corregir una tasa antes del ciclo automático:

1. Abre `data/tasas.json`
2. Encuentra la institución por su `"id"`
3. Modifica los valores `"digital"` y `"agencia"` del plazo correspondiente
4. Guarda y haz commit

---

## ⚠️ Aviso legal

Las tasas son **referenciales**. Siempre verifica en el sitio oficial de cada
institución antes de invertir. Regulado por Superbancos y SEPS.
Seguro COSEDE cubre hasta $32,000 por depositante por institución.

**Fuentes oficiales:**
- BCE: https://bce.fin.ec
- Superbancos: https://superbancos.gob.ec
- SEPS: https://seps.gob.ec
