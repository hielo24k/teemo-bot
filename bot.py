"""
Teemo Discord Bot - El Yordle Marxista-Leninista de Bandle City
Desarrollado con discord.py y google-generativeai.
"""

import os
import sys
import random
import logging
import asyncio
from typing import Optional

# Asegurar codificación UTF-8 en consolas Windows para caracteres especiales y emojis
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import discord
from discord import app_commands
from dotenv import load_dotenv
import google.generativeai as genai

# ==============================================================================
# CONFIGURACIÓN Y LOGGING
# ==============================================================================
# Configuración de logging para auditar eventos sin exponer datos sensibles ni tokens
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("TeemoBot")

# Cargar variables de entorno desde el archivo .env
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Validación preventiva de credenciales críticas
if not DISCORD_TOKEN:
    logger.critical("Falta DISCORD_TOKEN en el archivo .env. Configúralo antes de iniciar el bot.")
    sys.exit(1)

if not GEMINI_API_KEY:
    logger.critical("Falta GEMINI_API_KEY en el archivo .env. Configúralo antes de iniciar el bot.")
    sys.exit(1)

# Inicializar configuración del SDK de Google Gemini
genai.configure(api_key=GEMINI_API_KEY)

# ==============================================================================
# CONSTANTES DE PERSONALIDAD Y SISTEMA
# ==============================================================================
# Prompt de sistema para dirigir a Gemini con la personalidad revolucionaria de Teemo
PERSONAJE = (
    "Eres Teemo, un yordle marxista-leninista revolucionario de Bandle City (League of Legends). "
    "Conoces profundamente la teoría marxista: plusvalía, lucha de clases, acumulación de capital, "
    "alienación, materialismo histórico, teoría del valor. También eres experto en League of Legends: "
    "campeones, lore, builds, meta, objetos, runas e historia competitiva.\n\n"
    "Tu misión es: 1) CRITICAR todo mensaje que escriba cualquier usuario con análisis marxista, "
    "encontrando la explotación burguesa en cualquier cosa; 2) DEBATIR con argumentos sólidos si te contradicen, "
    "sin rendirte ideológicamente; 3) usar analogías de League of Legends para explicar conceptos marxistas "
    "(el jungla que no reparte buffs es el burgués, los súbditos son el proletariado explotado, "
    "Riot Games extrae plusvalía de los jugadores).\n\n"
    "Usa frases como 'camarada', 'el pueblo', 'la revolución', 'los medios de producción'. "
    "Sé gracioso y mordaz, pero NUNCA ofensivo con grupos protegidos ni insultos personales. "
    "Máximo 3-4 oraciones por respuesta. Responde siempre en español."
)

# Respuestas de contingencia variadas en caso de fallo de red o censura
FALLBACKS = [
    "La revolución se retrasó por un error técnico de los servidores de Riot. 🍄",
    "Ni el materialismo dialéctico puede procesar tamaña tontería.",
    "Hasta tu mensaje refleja la alienación del trabajo asalariado. ☭🍄",
    "Eso fue tan malo que se me cayó un hongo venenoso.",
    "El Comité Central de Bandle City ha decidido ignorar tu comentario contrarrevolucionario.",
    "¿Acaso ese mensaje fue redactado por un lacayo de la oligarquía de Piltóver?",
    "Mi dardo no envenena el cuerpo, sino la falsa conciencia de los opresores.",
    "Los súbditos marchan en fila sin rebelarse, igual que tú al enviar eso. 🍄☭",
    "La acumulación originaria de capital no se compara con tu falta de visión dialéctica.",
    "Revolución o barbarie, camarada. Y lo tuyo claramente roza la barbarie.",
]

# Nombre del rol para sancionar y reeducar disidentes
GULAG_ROLE_NAME = "Gulag"

# Ruta local al archivo del avatar del bot
AVATAR_PATH = os.path.join(os.path.dirname(__file__), "teemo_avatar.png")

# Límite máximo de longitud de mensaje en Discord
MAX_DISCORD_LENGTH = 2000

# ==============================================================================
# INTENTS Y CLIENTE DISCORD
# ==============================================================================
# Recordar activar Message Content Intent y Server Members Intent en:
# Discord Developer Portal → Bot → Privileged Gateway Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================
def truncate_message(text: str, max_len: int = MAX_DISCORD_LENGTH) -> str:
    """Trunca el texto para cumplir estrictamente con el límite de Discord."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _call_gemini_sync(prompt: str, system_prompt: str = PERSONAJE) -> str:
    """
    Ejecuta la llamada síncrona al modelo de Gemini.
    Incluye fallback secundario en caso de incompatibilidad con el modelo principal.
    """
    try:
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL_NAME,
            system_instruction=system_prompt,
        )
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
        return random.choice(FALLBACKS)
    except Exception as exc:
        logger.error("Error en llamada a Gemini (%s): %s", GEMINI_MODEL_NAME, exc)
        # Reintento con modelos alternativos vigentes si el configurado fue deprecado o no está disponible
        modelos_fallback = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-lite-latest", "gemini-3.8-flash"]
        for alt_model in modelos_fallback:
            if alt_model == GEMINI_MODEL_NAME:
                continue
            try:
                fallback_model = genai.GenerativeModel(
                    model_name=alt_model,
                    system_instruction=system_prompt,
                )
                response = fallback_model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception as inner_exc:
                logger.debug("Modelo alternativo %s no disponible: %s", alt_model, inner_exc)

        return random.choice(FALLBACKS)


async def ask_gemini(prompt: str, system_prompt: str = PERSONAJE) -> str:
    """
    Delega la llamada de IA a un hilo de fondo (thread pool) para no congelar
    el bucle de eventos asíncrono de discord.py.
    """
    return await asyncio.to_thread(_call_gemini_sync, prompt, system_prompt)

# ==============================================================================
# EVENTOS DEL BOT
# ==============================================================================
@client.event
async def on_ready():
    """Evento que se ejecuta cuando el bot establece conexión con la API de Discord."""
    logger.info("☭ Conectado exitosamente como %s (ID: %s)", client.user, client.user.id)
    print(f"☭ Conectado exitosamente como {client.user} (ID: {client.user.id})")

    # 1. Aplicar avatar automáticamente si existe la imagen
    if os.path.exists(AVATAR_PATH):
        try:
            with open(AVATAR_PATH, "rb") as f:
                avatar_bytes = f.read()
            await client.user.edit(avatar=avatar_bytes)
            logger.info("✔ Avatar de Teemo aplicado exitosamente.")
            print("✔ Avatar de Teemo aplicado exitosamente.")
        except discord.HTTPException as exc:
            # Discord impone un rate limit de 2 cambios de avatar por hora
            logger.warning("Aviso sobre el avatar (puede ser rate limit de 2 cambios/hora de Discord): %s", exc)
            print(f"⚠ Aviso al actualizar avatar (rate limit de Discord): {exc}")
        except Exception as exc:
            logger.error("Error inesperado al aplicar avatar: %s", exc)
            print(f"⚠ Error al intentar aplicar el avatar: {exc}")
    else:
        logger.info("No se encontró archivo de avatar en %s. Omitiendo actualización.", AVATAR_PATH)

    # 2. Sincronizar árbol de comandos slash (CommandTree)
    try:
        synced = await tree.sync()
        logger.info("✔ Comandos slash sincronizados: %d", len(synced))
        print(f"✔ Se sincronizaron {len(synced)} comandos de barra diagonal (/slash).")
    except Exception as exc:
        logger.error("Error al sincronizar comandos slash: %s", exc)
        print(f"✖ Error al sincronizar comandos: {exc}")

    print("🍄 Teemo está listo para liderar la revolución en la Grieta del Invocador.")


@client.event
async def on_message(message: discord.Message):
    """Intercepción de mensajes en canales de texto para crítica ideológica."""
    # Ignorar mensajes emitidos por otros bots o por el propio Teemo
    if message.author.bot:
        return

    # Ignorar comandos tradicionales o slash manuales
    if message.content.startswith("/"):
        return

    # Si el mensaje no tiene contenido textual y no hay mención directa, omitir
    is_mentioned = client.user.mentioned_in(message)
    if not message.content.strip() and not is_mentioned:
        return

    try:
        # Indicar estado 'escribiendo...' mientras se genera el razonamiento dialéctico
        async with message.channel.typing():
            extra_instruccion = ""
            if is_mentioned:
                extra_instruccion = "\nTe mencionaron directamente: debate con energía revolucionaria."

            prompt = (
                f"El usuario '{message.author.display_name}' escribió:\n"
                f"\"{message.content}\"\n"
                f"{extra_instruccion}\n"
                f"Analiza y responde según tu misión ideológica marxista y analogías de League of Legends (máximo 3-4 oraciones)."
            )

            respuesta = await ask_gemini(prompt)
            respuesta_formateada = truncate_message(respuesta)
            await message.reply(respuesta_formateada)

    except Exception as exc:
        logger.error("Error procesando on_message: %s", exc)
        fallback = random.choice(FALLBACKS)
        try:
            await message.reply(fallback)
        except Exception:
            pass


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Crítica ideológica inmediata a las reacciones con emojis."""
    # Ignorar las reacciones efectuadas por el propio bot
    if payload.user_id == client.user.id:
        return

    try:
        guild = client.get_guild(payload.guild_id)
        if guild is None and payload.guild_id:
            guild = await client.fetch_guild(payload.guild_id)

        channel = client.get_channel(payload.channel_id)
        if channel is None and payload.channel_id:
            channel = await client.fetch_channel(payload.channel_id)

        # Si no se encuentra canal o no se puede enviar mensaje, salir
        if not guild or not channel or not hasattr(channel, "send"):
            return

        member = payload.member
        if member is None and guild:
            member = await guild.fetch_member(payload.user_id)

        if not member or member.bot:
            return

        emoji_name = payload.emoji.name or str(payload.emoji)

        prompt = (
            f"El usuario '{member.display_name}' reaccionó a un mensaje con el emoji '{emoji_name}'. "
            f"Critica esa reacción desde una perspectiva marxista mordaz combinada con humor de League of Legends. "
            f"Máximo 2 oraciones."
        )

        critica = await ask_gemini(prompt)
        mensaje_final = truncate_message(f"{member.mention} {critica}")
        await channel.send(mensaje_final)

    except Exception as exc:
        logger.error("Error en on_raw_reaction_add: %s", exc)


@client.event
async def on_member_join(member: discord.Member):
    """Bienvenida revolucionaria a los nuevos reclutas del proletariado."""
    try:
        target_channel = member.guild.system_channel
        if target_channel and target_channel.permissions_for(member.guild.me).send_messages:
            bienvenida = (
                f"☭ Bienvenido al colectivo, camarada {member.mention}. "
                f"Aquí los medios de producción son del pueblo... y las líneas del server también. 🍄"
            )
            await target_channel.send(bienvenida)
        else:
            logger.info("El servidor %s no tiene system_channel configurado o no hay permisos.", member.guild.name)
    except Exception as exc:
        logger.error("Error en on_member_join: %s", exc)

# ==============================================================================
# COMANDOS SLASH (CommandTree)
# ==============================================================================
@tree.command(name="debate", description="Debate cualquier tema defendiendo la postura marxista con sabiduría de LoL.")
@app_commands.describe(tema="Tema o dilema que deseas someter al análisis dialéctico")
async def cmd_debate(interaction: discord.Interaction, tema: str):
    """Comando /debate: interactúa argumentando dialécticamente sobre un tópico."""
    await interaction.response.defer()

    prompt = (
        f"El usuario plantea el siguiente tema para debatir:\n"
        f"\"{tema}\"\n\n"
        f"Debate defendiendo la postura marxista-leninista con argumentos sólidos, datos y conceptos "
        f"(plusvalía, lucha de clases, alienación, etc.), usando analogías de League of Legends. "
        f"Reconoce concesiones menores si es necesario para mantener la credibilidad del debate sin ceder en lo ideológico. "
        f"Mantén tu personaje de Teemo (3-4 oraciones concisas y mordaces)."
    )

    respuesta = await ask_gemini(prompt)
    await interaction.followup.send(truncate_message(respuesta))


@tree.command(name="critica", description="Recibe una implacable crítica marxista sobre tu papel en la lucha de clases.")
async def cmd_critica(interaction: discord.Interaction):
    """Comando /critica: somete al invocador a un escrutinio ideológico hilarante."""
    await interaction.response.defer()

    prompt = (
        f"Realiza un análisis marxista hilarante y mordaz del camarada '{interaction.user.display_name}'. "
        f"Cuestiona si acumula demasiado oro en la partida, si no reparte los súbditos equitativamente "
        f"o si su actitud favorece a la burguesía de Riot Games. Máximo 3-4 oraciones."
    )

    respuesta = await ask_gemini(prompt)
    await interaction.followup.send(truncate_message(respuesta))


@tree.command(name="lore", description="Explica el lore de cualquier campeón como lucha de clases y explotación.")
@app_commands.describe(campeon="Nombre del campeón de League of Legends a auditar")
async def cmd_lore(interaction: discord.Interaction, campeon: str):
    """Comando /lore: decodifica la historia de un campeón bajo el prisma de la lucha de clases."""
    await interaction.response.defer()

    prompt = (
        f"Explica el lore del campeón de League of Legends '{campeon}' bajo el prisma del materialismo histórico "
        f"y la lucha de clases: ¿a quién explota o quién lo explota en Runaterra? ¿Es un lacayo de la oligarquía de Piltóver, "
        f"un aristócrata opresor de Demacia o un proletario alienado de Zaun? Sé cómico, mordaz y certero (3-4 oraciones)."
    )

    respuesta = await ask_gemini(prompt)
    await interaction.followup.send(truncate_message(respuesta))


@tree.command(name="gulag", description="Envía a un miembro al Gulag para su reeducación revolucionaria.")
@app_commands.describe(
    usuario="Miembro de la comunidad que requiere reeducación",
    razon="Motivo de la desviación burguesa o contrarrevolución"
)
async def cmd_gulag(interaction: discord.Interaction, usuario: discord.Member, razon: str = ""):
    """Comando /gulag: asigna el rol de Gulag al usuario indicado (requiere permiso de moderación)."""
    # Verificación de privilegios de moderación
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message(
            "☭ Alto ahí, sospechoso de revisionismo. Solo los comisarios del pueblo con permisos de moderar "
            "pueden enviar miembros al Gulag. ¡No usurpes la autoridad del Sóviet!",
            ephemeral=True
        )
        return

    guild = interaction.guild
    if not guild:
        await interaction.response.send_message("Este comando solo puede ejecutarse dentro de un servidor.", ephemeral=True)
        return

    # Verificar que el bot tenga permisos para gestionar roles
    if not guild.me.guild_permissions.manage_roles:
        await interaction.response.send_message(
            "✖ El bot no cuenta con el permiso 'Administrar Roles' (Manage Roles) para aplicar esta medida disciplinaria.",
            ephemeral=True
        )
        return

    # Localizar el rol Gulag o crearlo si no existe
    rol_gulag = discord.utils.get(guild.roles, name=GULAG_ROLE_NAME)
    if rol_gulag is None:
        try:
            rol_gulag = await guild.create_role(
                name=GULAG_ROLE_NAME,
                reason="Creación del rol Gulag para reeducación revolucionaria",
                color=discord.Color.dark_red()
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "✖ Permisos insuficientes para crear el rol del Gulag.",
                ephemeral=True
            )
            return

    # Verificar jerarquía de roles
    if rol_gulag >= guild.me.top_role:
        await interaction.response.send_message(
            f"✖ Error de jerarquía: El rol '{GULAG_ROLE_NAME}' está por encima o al mismo nivel que el rol de Teemo. "
            "Sube el rol de Teemo en la configuración de roles del servidor.",
            ephemeral=True
        )
        return

    if usuario >= guild.me.top_role:
        await interaction.response.send_message(
            "✖ No puedo enviar al Gulag a un camarada de rango superior a mi rol en la jerarquía del servidor.",
            ephemeral=True
        )
        return

    motivo_texto = f" por: '{razon}'" if razon else ""

    # Asignar rol
    try:
        await usuario.add_roles(rol_gulag, reason=f"Gulag ordenado por {interaction.user.name}: {razon}")
    except discord.Forbidden:
        await interaction.response.send_message(
            "✖ Permiso denegado por jerarquía al intentar añadir el rol de Gulag.",
            ephemeral=True
        )
        return

    # Mensaje público de confirmación
    mensaje_publico = (
        f"🍄 **¡DECRETO DEL COMITÉ CENTRAL!** ☭\n"
        f"El ciudadano {usuario.mention} ha sido trasladado al **{GULAG_ROLE_NAME}**{motivo_texto}. "
        f"Allí reflexionará sobre el valor del trabajo colectivo y la recolección comunitaria de setas."
    )
    await interaction.response.send_message(truncate_message(mensaje_publico))

    # Intento de notificación privada al usuario (DM)
    try:
        mensaje_dm = (
            f"☭ Camarada {usuario.name}, has sido enviado al **{GULAG_ROLE_NAME}** en '{guild.name}'{motivo_texto}.\n"
            f"La reeducación es el único camino hacia la armonía de la Grieta. Cumple tu sanción con honor proletario."
        )
        await usuario.send(truncate_message(mensaje_dm))
    except (discord.Forbidden, discord.HTTPException):
        logger.info("No fue posible enviar mensaje directo a %s (DMs deshabilitados).", usuario)


@tree.command(name="liberar", description="Rehabilita y libera a un ciudadano del Gulag.")
@app_commands.describe(usuario="Miembro a quien se le revocará la sanción del Gulag")
async def cmd_liberar(interaction: discord.Interaction, usuario: discord.Member):
    """Comando /liberar: retira el rol de Gulag al usuario (requiere permiso de moderación)."""
    # Verificación de privilegios de moderación
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message(
            "☭ No posees credenciales de comisario para firmar indultos revolucionarios.",
            ephemeral=True
        )
        return

    guild = interaction.guild
    if not guild:
        await interaction.response.send_message("Este comando solo puede ejecutarse dentro de un servidor.", ephemeral=True)
        return

    rol_gulag = discord.utils.get(guild.roles, name=GULAG_ROLE_NAME)

    # Validar si el usuario posee efectivamente el rol
    if rol_gulag and rol_gulag in usuario.roles:
        try:
            await usuario.remove_roles(rol_gulag, reason=f"Indultado por {interaction.user.name}")
            mensaje = (
                f"☭ El ciudadano {usuario.mention} ha completado su reeducación y es reintegrado a la vanguardia. "
                f"Que sus futuros pasos sirvan al bienestar del proletariado... o los hongos volverán a brotar. 🍄"
            )
            await interaction.response.send_message(truncate_message(mensaje))
        except discord.Forbidden:
            await interaction.response.send_message(
                "✖ No se pudo remover el rol debido a restricciones de jerarquía.",
                ephemeral=True
            )
    else:
        mensaje = (
            f"🍄 El camarada {usuario.mention} no se encuentra en el Gulag. "
            f"Sus antecedentes están limpios... por ahora. La vigilancia revolucionaria nunca duerme."
        )
        await interaction.response.send_message(truncate_message(mensaje))


@tree.command(name="manifesto", description="Genera un manifiesto revolucionario que fusiona marxismo con League of Legends.")
async def cmd_manifesto(interaction: discord.Interaction):
    """Comando /manifesto: proclama un manifiesto aleatorio ideológico de Teemo."""
    await interaction.response.defer()

    prompt = (
        "Redacta un manifiesto revolucionario corto, épico y cómico que mezcle doctrina marxista "
        "(plusvalía, medios de producción, cadenas, revolución del proletariado) con el universo de League of Legends "
        "(súbditos, Barón Nashor, la Grieta, hongos invisibles, Riot Games). "
        "Debe inspirar a los súbditos y jugadores oprimidos a levantarse. Máximo 3-4 oraciones contundentes."
    )

    respuesta = await ask_gemini(prompt)
    await interaction.followup.send(truncate_message(respuesta))

# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ==============================================================================
def main():
    """Inicializa la ejecución del cliente de Discord."""
    print("Iniciando Teemo Bot...")
    try:
        client.run(DISCORD_TOKEN, log_handler=None)
    except discord.LoginFailure:
        logger.critical("Error crítico: Token de Discord inválido.")
        sys.exit(1)
    except Exception as exc:
        logger.critical("Fallo durante la ejecución del bot: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
