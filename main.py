import requests
import time

BOT_TOKEN = "8927441067:AAEX0w6QrLQTfgkFekBTfYk_L27NwNAKKzA"

GET_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
SEND_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    response = requests.post(
        SEND_URL,
        json=payload
    )

    return response.json()


def process_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    print("Received:", text)

    if text == "/start":
        send_message(
            chat_id,
            "Welcome! 🤖\nBot is working."
        )

    elif text == ["/help", "help"]:
        send_message(
            chat_id,
            "Available commands:\n"
            "/start - Start the bot\n"
            "/hello - Say hello\n"
            "/help - Show commands"
        )

    elif text.lower() in ["/hello", "hello", "hi"]:
        send_message(
            chat_id,
            "Hello! 👋"
        )

    else:
        send_message(
            chat_id,
            "I don't understand that command."
        )


def main():
    offset = 0
    
    app.add_handler(
    CommandHandler("calc", calc)
)
    while True:

        try:
            response = requests.get(
                GET_URL,
                params={
                    "offset": offset,
                    "timeout": 10
                },
                timeout=15
            )

            data = response.json()
            print("Telegram response:")
            print(data)
            for update in data["result"]:

                offset = update["update_id"] + 1

                if "message" in update:
                    process_message(update["message"])

        except Exception as e:
            print("ERROR:", e)
            time.sleep(3)


main()