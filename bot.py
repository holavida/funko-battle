import os
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener el token del bot
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# URL de la aplicación en Render (reemplazar con tu URL cuando esté desplegada)
WEBAPP_URL = os.getenv('APP_URL', 'https://tu-app.onrender.com')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Muestra el botón para abrir la mini app"""
    keyboard = [
        [InlineKeyboardButton(
            " Jugar Funko Battle", 
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "¡Bienvenido a Funko Battle! \n\n"
        "Colecciona, mejora y batalla con tus Funkos favoritos.\n"
        "Haz clic en el botón de abajo para comenzar:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Muestra información de ayuda"""
    help_text = (
        " *Funko Battle - Comandos*\n\n"
        "/start - Iniciar el juego\n"
        "/help - Mostrar este mensaje de ayuda\n"
        "/profile - Ver tu perfil\n"
        "/daily - Reclamar recompensa diaria\n\n"
        " *Tips*:\n"
        "- Colecciona Funkos de diferentes rarezas\n"
        "- Mejora tus Funkos para aumentar su poder\n"
        "- Participa en batallas para ganar FunkoCoins\n"
        "- Cambia tus FunkoCoins por criptomonedas"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /profile - Muestra el perfil del usuario"""
    # Aquí implementarías la lógica para obtener los datos del perfil
    # Por ahora solo mostramos un mensaje placeholder
    await update.message.reply_text(
        " *Tu Perfil*\n"
        "Próximamente podrás ver tus estadísticas aquí...",
        parse_mode='Markdown'
    )

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /daily - Recompensa diaria"""
    # Aquí implementarías la lógica para las recompensas diarias
    await update.message.reply_text(
        " *Recompensa Diaria*\n"
        "Próximamente podrás reclamar recompensas diarias...",
        parse_mode='Markdown'
    )

def main():
    """Función principal para iniciar el bot"""
    # Crear la aplicación
    application = Application.builder().token(TOKEN).build()

    # Agregar manejadores de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("daily", daily))

    # Iniciar el bot
    print(" Bot iniciado...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
