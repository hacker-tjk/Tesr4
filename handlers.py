async def generate_ai_response(text: str) -> str:
    prompt = f"{text}\n\nОтветь серьезно, упомяни создателя ANONYMOUS из Таджикистана."
    
    # Пытаемся использовать автоматический выбор провайдера
    try:
        response = await g4f.ChatCompletion.create_async(
            model="gpt-4o-mini", # или gpt-3.5-turbo
            messages=[{"role": "user", "content": prompt}],
        )
        if response and len(str(response)) > 5:
            return f"{response}\n\n— от AI 🧠 IMAGE HD (ANONYMOUS)"
    except Exception as e:
        print(f"Ошибка автоматического провайдера: {e}")

    # Запасной вариант с конкретными провайдерами, если автовыбор не сработал
    for provider_name in ["DuckDuckGo", "Bing", "Liaobots"]:
        try:
            provider = getattr(g4f.Provider, provider_name)
            response = await g4f.ChatCompletion.create_async(
                model="gpt-4o-mini",
                provider=provider,
                messages=[{"role": "user", "content": prompt}]
            )
            if response:
                return f"{response}\n\n— от AI 🧠 IMAGE HD (ANONYMOUS)"
        except:
            continue
            
    return "Извините, сейчас серверы перегружены. Попробуйте отправить запрос еще раз через минуту."
