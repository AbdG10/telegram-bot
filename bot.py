import os
import ast
import operator

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

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

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

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

        if isinstance(node, ast.BinOp):

            left = solve(node.left)
            right = solve(node.right)

            operation = operators.get(type(node.op))

            if operation:
                return operation(left, right)

        if isinstance(node, ast.UnaryOp):

            value = solve(node.operand)

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

        raise ValueError()

    return solve(tree.body)


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
        "Welcome! 🤖\nChoose an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Hello! 👋"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/hello - Say hello\n"
        "/help - Show commands\n"
        "/calc 25 + 10 - Calculator"
    )


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:

        await update.message.reply_text(
            "Usage:\n/calc 25 + 10"
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


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    if query.data == "hello":

        await query.message.reply_text(
            "Hello! 👋"
        )

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

    elif query.data == "help":

        await query.message.reply_text(
            "Available commands:\n\n"
            "/start - Start the bot\n"
            "/hello - Say hello\n"
            "/help - Show commands\n"
            "/calc 25 + 10 - Calculator"
        )


async def normal_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    if text.lower() in ["hello", "hi"]:

        await update.message.reply_text(
            "Hello! 👋"
        )

        return

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


def main():

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .build()
    )

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

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

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