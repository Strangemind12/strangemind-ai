short_url = monetize_link(long_url)
reply = (
    "🔗 Here's your link (we get a tiny cent to keep Strangemind AI alive):\n"
    f"{short_url}"
)
send_message(user_phone, reply)
