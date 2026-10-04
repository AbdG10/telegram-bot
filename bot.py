import os
import ast
import operator
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
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
    ast.Mod: operator.mod
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

        # +number / -number
        if isinstance(node, ast.UnaryOp):
            value = solve(node.operand)

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

        raise ValueError()

    return solve(tree.body)


# =========================
# HTTP HEALTH SERVER
# =========================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        pass


def start_health_server():

    port = int(os.environ.get("PORT", 10000))

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    server.serve_forever()


# =========================
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "👋 Hello",
                callback_data="hello"
            ),
            InlineKeyboardButton(
                "🧮 Calculator",
                callback_data="calculator"
            )
        ],
        [
            InlineKeyboardButton(
                "ℹ️ Help",
                callback_data="help"
            )
        ]
    ]

    await update.message.reply_text(
        "Welcome! 🤖\n\n"
        "Choose an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# /HELLO
# =========================

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Hello! 👋"
    )


# =========================
# /HELP
# =========================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/hello - Say hello\n"
        "/help - Show commands\n"
        "/calc 25 + 10 - Calculator"
    )


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
# BUTTON HANDLER
# =========================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    # Hello button
    if query.data == "hello":

        await query.message.reply_text(
            "Hello! 👋"
        )

    # Calculator button
    elif query.data == "calculator":

        await query.message.reply_text(
            "🧮 Calculator\n\n"
            "Type your calculation directly:\n\n"
            "25 + 10\n"
            "100 / 4\n"
            "20 - 7\n"
            "5 * 8\n\n"
            "You can also use × and ÷."
        )

    # Help button
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

    # Hello / Hi
    if text.lower() in ["hello", "hi"]:

        await update.message.reply_text(
            "Hello! 👋"
        )

        return

    # Try calculator
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

    # Start HTTP health server for Render
    threading.Thread(
        target=start_health_server,
        daemon=True
    ).start()

    # Create Telegram application
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # Commands
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

    # Inline buttons
    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    # Normal messages
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            normal_message
        )
    )

    print("Token loaded:", BOT_TOKEN is not None)
    print("Bot is running...")


    app.run_polling(
        timeout=30,
        bootstrap_retries=-1
    )


if __name__ == "__main__":
    main()