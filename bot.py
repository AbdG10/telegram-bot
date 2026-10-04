import os
import ast
import operator
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# =========================
# ENVIRONMENT
# =========================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


# =========================
# CALCULATOR
# =========================

operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
}


def calculate(expression):

    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")

    tree = ast.parse(expression, mode="eval")

    def solve(node):

        # Numbers
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

        # Binary operations
        if isinstance(node, ast.BinOp):

            left = solve(node.left)
            right = solve(node.right)

            operation = operators.get(type(node.op))

            if operation:
                return operation(left, right)

        # Positive / negative numbers
        if isinstance(node, ast.UnaryOp):

            value = solve(node.operand)

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

        raise ValueError()

    return solve(tree.body)


# =========================
# RENDER HEALTH SERVER
# =========================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.end_headers()

        self.wfile.write(
            b"Telegram bot is running!"
        )

    def log_message(self, format, *args):
        pass


def start_health_server():

    port = int(
        os.environ.get("PORT", 10000)
    )

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    server.serve_forever()


# =========================
# INLINE KEYBOARD
# =========================

def get_inline_keyboard():

    keyboard = [
        [
            InlineKeyboardButton(
                "👋 Hello",
                callback_data="hello"
            ),
            InlineKeyboardButton(
                "🧮 Calculator",
                callback_data="calculator"
            ),
        ],
        [
            InlineKeyboardButton(
                "ℹ️ Help",
                callback_data="help"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# REPLY KEYBOARD
# =========================

def get_reply_keyboard():

    keyboard = [
        [
            "👋 Hello",
            "🧮 Calculator",
        ],
        [
            "ℹ️ Help",
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )


# =========================
# HELLO
# =========================

async def send_hello(update, context):

    await update.message.reply_text(
        "Hello! 👋"
    )


# =========================
# CALCULATOR HELP
# =========================

async def send_calculator_help(update, context):

    await update.message.reply_text(
        "🧮 Calculator\n\n"
        "Type your calculation:\n\n"
        "25 + 10\n"
        "100 / 4\n"
        "125 * 37\n"
        "20 - 7\n\n"
        "You can also use × and ÷."
    )


# =========================
# HELP
# =========================

async def send_help(update, context):

    await update.message.reply_text(
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/hello - Say hello\n"
        "/help - Show commands\n"
        "/calc 25 + 10 - Calculator"
    )


# =========================
# START
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Inline buttons
    await update.message.reply_text(
        "Welcome! 🤖\n\n"
        "Choose an option:",
        reply_markup=get_inline_keyboard(),
    )

    # Reply keyboard
    await update.message.reply_text(
        "You can also use the buttons below 👇",
        reply_markup=get_reply_keyboard(),
    )


# =========================
# /HELLO
# =========================

async def hello(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await send_hello(update, context)


# =========================
# /HELP
# =========================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await send_help(update, context)


# =========================
# /CALC
# =========================

async def calc(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not context.args:

        await update.message.reply_text(
            "Usage:\n"
            "/calc 25 + 10"
        )

        return

    expression = " ".join(context.args)

    try:

        result = calculate(expression)

        await update.message.reply_text(
            f"Result: {result}"
        )

    except ZeroDivisionError:

        await update.message.reply_text(
            "❌ Cannot divide by zero."
        )

    except Exception:

        await update.message.reply_text(
            "❌ Invalid calculation."
        )


# =========================
# INLINE BUTTON HANDLER
# =========================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    # Hello
    if query.data == "hello":

        await query.message.reply_text(
            "Hello! 👋"
        )

    # Calculator
    elif query.data == "calculator":

        await query.message.reply_text(
            "🧮 Calculator\n\n"
            "Type your calculation:\n\n"
            "25 + 10\n"
            "100 / 4\n"
            "125 * 37\n"
            "20 - 7\n\n"
            "You can also use × and ÷."
        )

    # Help
    elif query.data == "help":

        await query.message.reply_text(
            "Available commands:\n\n"
            "/start - Start the bot\n"
            "/hello - Say hello\n"
            "/help - Show commands\n"
            "/calc 25 + 10 - Calculator"
        )


# =========================
# NORMAL MESSAGES
# =========================

async def normal_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text.strip()

    lower_text = text.lower()

    # =========================
    # HELLO
    # =========================

    if "hello" in lower_text or lower_text == "hi":

        await update.message.reply_text(
            "Hello! 👋"
        )

        return

    # =========================
    # CALCULATOR BUTTON
    # =========================

    if "calculator" in lower_text:

        await send_calculator_help(
            update,
            context
        )

        return

    # =========================
    # HELP BUTTON
    # =========================

    if "help" in lower_text:

        await send_help(
            update,
            context
        )

        return

    # =========================
    # CALCULATOR INPUT
    # =========================

    try:

        result = calculate(text)

        await update.message.reply_text(
            f"Result: {result}"
        )

    except ZeroDivisionError:

        await update.message.reply_text(
            "❌ Cannot divide by zero."
        )

    except Exception:

        await update.message.reply_text(
            "I don't understand that message.\n\n"
            "Example:\n"
            "25 + 10"
        )


# =========================
# MAIN
# =========================

def main():

    # Render health server
    threading.Thread(
        target=start_health_server,
        daemon=True
    ).start()

    # Telegram application
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # =========================
    # COMMANDS
    # =========================

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("hello", hello)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        CommandHandler("calc", calc)
    )

    # =========================
    # INLINE BUTTONS
    # =========================

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    # =========================
    # REPLY KEYBOARD + TEXT
    # =========================

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            normal_message
        )
    )

    print(
        "Token loaded:",
        BOT_TOKEN is not None
    )

    print(
        "Bot is running..."
    )

    # =========================
    # POLLING
    # =========================

    app.run_polling(
        timeout=30,
        bootstrap_retries=-1
    )


# =========================
# RUN
# =========================

if __name__ == "__main__":
    main()