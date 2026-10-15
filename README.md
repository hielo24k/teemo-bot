<div align="center">
  <img src="teemo_avatar.png" alt="Teemo Avatar" width="200" />
  <h1>🍄 Teemo - El Yordle Marxista-Leninista de Bandle City ☭</h1>
  <p><em>Un bot de Discord revolucionario impulsado por <strong>Google Gemini</strong> y <strong>discord.py</strong>.</em></p>
</div>

---

Teemo analiza cada mensaje y evento en tu servidor bajo el prisma del materialismo histórico, la plusvalía y la lucha de clases, ilustrando sus argumentos con analogías de League of Legends.

---

## ☭ Personalidad y Filosofía

Teemo no es un yordle ordinario: es un cuadro revolucionario formado en la teoría marxista-leninista y veterano de mil batallas en la Grieta del Invocador:
- **Crítica Dialéctica Continua:** Detecta la explotación burguesa en los mensajes cotidianos, las reacciones de emojis y el comportamiento de los jugadores.
- **Analogías de League of Legends:** Los súbditos son el proletariado alienado que genera valor; el jungla que no comparte los buffs encarna a la oligarquía acaparadora; y Riot Games extrae la plusvalía de la comunidad.
- **Firmeza Revolucionaria:** Jamás claudica en los debates ideológicos, manteniendo respuestas ágiles (3 a 4 oraciones), mordaces y cargadas de humor colectivo.

---

## 📋 Requisitos Previos

1. **Python 3.10 o superior** (compatible con Python 3.11, 3.12, 3.13 y 3.14).
2. **Cuenta de Discord y Aplicación de Desarrollador:** [Discord Developer Portal](https://discord.com/developers/applications).
3. **Clave de API de Google Gemini:** Obtén tu API key gratuita en [Google AI Studio](https://aistudio.google.com/).

---

## 🚀 Guía de Instalación y Configuración Paso a Paso

### 1. Crear y Configurar la Aplicación en Discord Developer Portal

1. Ve a [Discord Developer Portal](https://discord.com/developers/applications) e inicia sesión.
2. Haz clic en **"New Application"**, nómbrala **Teemo** y confirma.
3. Dirígete a la pestaña **Bot** en el menú lateral izquierdo:
   - Haz clic en **"Add Bot"** (o **"Reset Token"** para generar tu token).
   - Copia el **Token** (lo necesitarás para el archivo `.env`). **Nunca compartas este token**.
4. En esa misma pestaña **Bot**, desplázate hacia abajo hasta **Privileged Gateway Intents** y activa obligatoriamente:
   - ✅ **Presence Intent** (opcional)
   - ✅ **Server Members Intent** (Necesario para bienvenidas y moderación)
   - ✅ **Message Content Intent** (Indispensable para que Teemo lea los mensajes a criticar)
5. Guarda los cambios con **Save Changes**.

### 2. Generar el Enlace de Invitación del Bot

1. Dirígete a la pestaña **OAuth2** → **URL Generator**.
2. En la sección **Scopes**, marca:
   - ✅ `bot`
   - ✅ `applications.commands` (necesario para registrar los comandos slash `/`)
3. En la sección **Bot Permissions**, selecciona los siguientes permisos esenciales:
   - ✅ **Send Messages** (Enviar mensajes)
   - ✅ **Send Messages in Threads** (Enviar mensajes en hilos)
   - ✅ **Read Message History** (Leer historial de mensajes)
   - ✅ **Manage Roles** (Administrar roles - requerido para el comando `/gulag`)
4. Copia la URL generada al final de la página, ábrela en tu navegador e invita a Teemo a tu servidor.

---

### 3. Configurar el Entorno Local

1. Clona o descarga este repositorio en tu equipo.
2. Abre una terminal dentro de la carpeta `teemo-bot`.
3. Crea y activa un entorno virtual (recomendado):
   ```bash
   # En Windows:
   python -m venv venv
   .\venv\Scripts\activate

   # En Linux / macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
5. Configura tus variables de entorno creando tu archivo `.env`:
   ```bash
   # Puedes copiar la plantilla:
   cp .env.example .env     # Linux/macOS
   copy .env.example .env   # Windows
   ```
6. Edita el archivo `.env` con tus credenciales:
   ```env
   DISCORD_TOKEN=tu_token_aqui_sin_comillas
   GEMINI_API_KEY=tu_api_key_de_google_aqui
   GEMINI_MODEL=gemini-2.5-flash
   ```

---

### 4. Ejecución del Bot

Inicia el bot ejecutando:
```bash
python bot.py
```

Al iniciar, verás en la consola los mensajes de confirmación de conexión, sincronización de comandos slash y aplicación del avatar.

---

## 🛡️ Jerarquía de Roles y Configuración del "Gulag"

El bot incluye un comando disciplinario `/gulag` que asigna un rol especial a miembros que requieran reeducación:

1. **Jerarquía en Discord (CRÍTICO):**
   - En Discord, ve a **Ajustes del Servidor** → **Roles**.
   - Asegúrate de que el rol de **Teemo** esté situado **por encima** del rol `Gulag` y de los miembros regulares a moderar. De lo contrario, la API de Discord bloqueará la asignación con un error `403 Forbidden`.
2. **Configuración de Permisos del Rol Gulag:**
   - Teemo creará el rol `Gulag` automáticamente si no existe, pero para que sea efectivo como sanción, debes asegurarte de que dicho rol tenga revocado el permiso de **Enviar Mensajes** en los canales de texto de tu servidor (o en la categoría correspondiente).

---

## 🎮 Comandos Disponibles

Todos los comandos son comandos slash (`/`) gestionados mediante `discord.app_commands`:

| Comando | Parámetros | Descripción |
| :--- | :--- | :--- |
| `/debate` | `tema` (texto) | Abre un debate dialéctico. Teemo defiende la postura marxista con argumentos sólidos y analogías de LoL. |
| `/critica` | *Ninguno* | Realiza un escrutinio ideológico hilarante del usuario que lo invoca. |
| `/lore` | `campeon` (texto) | Analiza el lore del campeón bajo el prisma de la lucha de clases y la explotación en Runaterra. |
| `/gulag` | `usuario` (mención), `razon` (opcional) | *(Solo moderadores)* Asigna el rol de Gulag al usuario y le notifica por mensaje directo. |
| `/liberar` | `usuario` (mención) | *(Solo moderadores)* Retira el rol de Gulag al usuario con mensaje de rehabilitación. |
| `/manifesto` | *Ninguno* | Proclama un manifiesto revolucionario aleatorio combinando marxismo y League of Legends. |

### Eventos Automáticos:
- **Intercepción de Mensajes (`on_message`):** Teemo analiza y critica los mensajes del chat general. Si es mencionado directamente con `@Teemo`, redobla su fervor combativo.
- **Reacción a Emojis (`on_raw_reaction_add`):** Teemo critica de forma mordaz los emojis que los usuarios colocan en los mensajes.
- **Bienvenida Revolucionaria (`on_member_join`):** Saluda a cada nuevo camarada en el canal del sistema del servidor.

---

## 🖼️ Avatar Automático y Rate Limits

- El proyecto incluye la imagen optimizada `teemo_avatar.png` (512x512 transparente).
- Al iniciar, Teemo intenta actualizar automáticamente su avatar mediante la API de Discord (`client.user.edit`).
- **Aviso de Rate Limit:** La API de Discord limita la actualización de avatares a un máximo de **2 cambios por hora por bot**. Si el bot se reinicia varias veces seguidas, es posible que Discord devuelva un aviso de rate limit (el bot continuará funcionando normalmente).
- **Subida Manual (Alternativa):** También puedes establecer el avatar permanentemente desde el [Discord Developer Portal](https://discord.com/developers/applications) → Tu Aplicación → **Bot** → Hacer clic en el icono de perfil y subir `teemo_avatar.png`.

---

## 🛠️ Estructura del Proyecto

```
teemo-bot/
├── bot.py                 # Código fuente completo y documentado
├── teemo_avatar.png       # Avatar oficial en PNG transparente (512x512)
├── .env.example           # Plantilla de variables de entorno
├── .gitignore             # Filtro de git para .env, __pycache__ y venv
├── requirements.txt       # Dependencias fijadas (discord.py, python-dotenv, google-generativeai, audioop-lts)
└── README.md              # Documentación técnica completa
```

---

¡Disfruta organizando la revolución proletaria en tu servidor de Discord con Teemo! 🍄☭
