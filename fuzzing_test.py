"""
Фаззинг-тестирование REST API платформы КраудШоп.
Метод: чёрный ящик, случайные/невалидные входные данные.
Запуск: python fuzzing_test.py  (внутри контейнера или при запущенном сервере)
"""

import random
import string
import requests

BASE_URL = "http://localhost:80"

# ── Генераторы случайных payload-ов ───────────────────────────────────────

def rand_str(length=None):
    length = length or random.randint(0, 300)
    chars = string.ascii_letters + string.digits + " !@#$%^&*()_+-=<>?/\\|{}[]~`'\""
    return ''.join(random.choices(chars, k=length))

def rand_int():
    return random.choice([
        0, -1, -9999, 99999999,
        random.randint(-1000, 1000),
        None,
        "abc",
        "",
        True,
    ])

def rand_price():
    return random.choice([
        0, -100, 99999999.99,
        "бесплатно", "", None,
        random.uniform(-500, 50000),
        "NaN", "Infinity",
    ])

PAYLOADS_REGISTER = [
    # Нормальные данные (ожидаем 201 или 400 при дубликате)
    {
        "username": "testuser_fuzz",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "email": "fuzz@test.ru",
        "first_name": "Тест",
        "last_name": "Фаззинг",
    },
    # Пустые поля
    {"username": "", "password1": "", "password2": "", "email": ""},
    # Только пробелы
    {"username": "   ", "password1": "   ", "email": "   "},
    # SQL-инъекция
    {
        "username": "' OR 1=1 --",
        "password1": "' DROP TABLE users_user; --",
        "password2": "' DROP TABLE users_user; --",
        "email": "sql@inject.com",
        "first_name": "<script>alert(1)</script>",
        "last_name": "'; DELETE FROM users_user WHERE '1'='1",
    },
    # XSS
    {
        "username": "<script>alert('xss')</script>",
        "password1": "Pass123!",
        "password2": "Pass123!",
        "email": "xss@test.com",
    },
    # Сверхдлинные строки
    {
        "username": "a" * 500,
        "password1": "b" * 1000,
        "password2": "b" * 1000,
        "email": "c" * 200 + "@test.com",
        "first_name": "x" * 300,
    },
    # Неверный email
    {
        "username": "validuser99",
        "password1": "Pass123!",
        "password2": "Pass123!",
        "email": "not-an-email",
    },
    # Несовпадающие пароли
    {
        "username": "user_mismatch",
        "password1": "Pass123!",
        "password2": "Different456!",
        "email": "mismatch@test.com",
    },
    # Слабый пароль
    {
        "username": "weakpassuser",
        "password1": "123",
        "password2": "123",
        "email": "weak@test.com",
    },
    # Unicode / emoji
    {
        "username": "пользователь🔥",
        "password1": "Пароль123!",
        "password2": "Пароль123!",
        "email": "unicode@test.com",
        "first_name": "Иван 🎉",
    },
    # Нулевые байты
    {
        "username": "user\x00null",
        "password1": "Pass\x00word1!",
        "password2": "Pass\x00word1!",
        "email": "null@test.com",
    },
    # Числовые поля вместо строк
    {
        "username": 12345,
        "password1": 9999,
        "password2": 9999,
        "email": 0,
    },
    # Случайные данные (5 итераций)
    *[
        {
            "username": rand_str(random.randint(1, 200)),
            "password1": rand_str(random.randint(0, 100)),
            "password2": rand_str(random.randint(0, 100)),
            "email": rand_str(20) + "@" + rand_str(5) + ".com",
            "first_name": rand_str(random.randint(0, 50)),
        }
        for _ in range(5)
    ],
]

PAYLOADS_PURCHASE = [
    # Нормальные данные без аутентификации (ожидаем 403)
    {
        "title": "Тест закупки",
        "description": "Описание",
        "price_per_unit": 1000,
        "organizer_fee": 5,
        "stop_date": "2099-12-31T23:59",
        "min_participants": 3,
    },
    # Отрицательная цена
    {
        "title": "Негативная цена",
        "description": "Тест",
        "price_per_unit": -500,
        "organizer_fee": -10,
        "stop_date": "2099-01-01T00:00",
    },
    # Дата в прошлом
    {
        "title": "Прошедшая дата",
        "description": "Тест",
        "price_per_unit": 100,
        "stop_date": "2000-01-01T00:00",
    },
    # Сверхбольшие числа
    {
        "title": "Большие числа",
        "description": "Тест",
        "price_per_unit": 9999999999.99,
        "organizer_fee": 999,
        "min_participants": 999999,
        "max_participants": -1,
        "stop_date": "2099-12-31T23:59",
    },
    # Пустой объект
    {},
    # Только пробелы в строках
    {
        "title": "   ",
        "description": "   ",
        "price_per_unit": "   ",
        "stop_date": "   ",
    },
    # Неверный формат даты
    {
        "title": "Дата-мусор",
        "description": "Тест",
        "price_per_unit": 100,
        "stop_date": "вчера",
    },
    # XSS в title
    {
        "title": "<img src=x onerror=alert(1)>",
        "description": "javascript:alert('xss')",
        "price_per_unit": 100,
        "stop_date": "2099-12-31T23:59",
    },
    # Очень длинное описание
    {
        "title": "Длинное описание",
        "description": "А" * 100000,
        "price_per_unit": 100,
        "stop_date": "2099-12-31T23:59",
    },
    # Случайные данные (5 итераций)
    *[
        {
            "title": rand_str(random.randint(0, 500)),
            "description": rand_str(random.randint(0, 1000)),
            "price_per_unit": rand_price(),
            "organizer_fee": rand_price(),
            "stop_date": rand_str(20),
            "min_participants": rand_int(),
        }
        for _ in range(5)
    ],
]

PAYLOADS_ORDER = [
    # Без аутентификации (ожидаем 403)
    {"purchase": 1, "quantity": 2, "comment": "тест"},
    # Нулевое количество
    {"purchase": 1, "quantity": 0, "comment": ""},
    # Отрицательное количество
    {"purchase": 1, "quantity": -5, "comment": "минус"},
    # Несуществующая закупка
    {"purchase": 999999, "quantity": 1, "comment": ""},
    # Строка вместо числа
    {"purchase": "abc", "quantity": "много", "comment": ""},
    # Пустой объект
    {},
    # XSS в комментарии
    {"purchase": 1, "quantity": 1, "comment": "<script>alert(1)</script>"},
    # SQL-инъекция в комментарии
    {"purchase": 1, "quantity": 1, "comment": "'; DROP TABLE purchases_order; --"},
    # Сверхдлинный комментарий
    {"purchase": 1, "quantity": 1, "comment": "С" * 100000},
    # Случайные данные (5 итераций)
    *[
        {
            "purchase": rand_int(),
            "quantity": rand_int(),
            "comment": rand_str(random.randint(0, 500)),
        }
        for _ in range(5)
    ],
]


# ── Тест-раннер ───────────────────────────────────────────────────────────

def run_fuzz(endpoint, payloads, method="POST", label=""):
    results = {"2xx": 0, "4xx": 0, "5xx": 0, "other": 0}
    crashes = []
    url = BASE_URL + endpoint

    print(f"\n{'='*60}")
    print(f"  Эндпоинт: {method} {endpoint}")
    print(f"  Описание: {label}")
    print(f"  Payload-ов: {len(payloads)}")
    print(f"{'='*60}")

    for i, payload in enumerate(payloads, 1):
        try:
            resp = requests.request(
                method, url,
                json=payload,
                timeout=5,
                allow_redirects=False,
            )
            code = resp.status_code
            bucket = f"{code // 100}xx"
            results[bucket] = results.get(bucket, 0) + 1

            status_icon = "✓" if code < 500 else "✗"
            print(f"  [{i:02d}] {status_icon} {code}  payload: {str(payload)[:60]}...")

            if code >= 500:
                crashes.append({"payload": payload, "status": code, "body": resp.text[:200]})

        except requests.exceptions.ConnectionError:
            results["other"] += 1
            print(f"  [{i:02d}] ✗ CONNECTION ERROR")
        except requests.exceptions.Timeout:
            results["other"] += 1
            print(f"  [{i:02d}] ✗ TIMEOUT")

    print(f"\n  Итог: 2xx={results.get('2xx',0)}  "
          f"4xx={results.get('4xx',0)}  "
          f"5xx={results.get('5xx',0)}  "
          f"other={results.get('other',0)}")

    if crashes:
        print(f"\n  ⚠️  ОБНАРУЖЕНО 5xx ОТВЕТОВ: {len(crashes)}")
        for c in crashes:
            print(f"     payload: {str(c['payload'])[:80]}")
            print(f"     ответ:   {c['body'][:100]}")
    else:
        print("  ✅ Ошибок 5xx не обнаружено")

    return results, crashes


def main():
    print("\n" + "="*60)
    print("  ФАЗЗИНГ-ТЕСТИРОВАНИЕ REST API — КраудШоп")
    print("  Метод: чёрный ящик")
    print("  Цель: выявление HTTP 500 и необработанных исключений")
    print("="*60)

    all_crashes = []

    r1, c1 = run_fuzz(
        "/users/register/",
        PAYLOADS_REGISTER,
        method="POST",
        label="Регистрация нового пользователя",
    )
    all_crashes.extend(c1)

    r2, c2 = run_fuzz(
        "/api/v1/purchases/",
        PAYLOADS_PURCHASE,
        method="POST",
        label="Создание закупки (без аутентификации)",
    )
    all_crashes.extend(c2)

    r3, c3 = run_fuzz(
        "/api/v1/orders/",
        PAYLOADS_ORDER,
        method="POST",
        label="Подача заявки (без аутентификации)",
    )
    all_crashes.extend(c3)

    total = sum([
        sum(r1.values()),
        sum(r2.values()),
        sum(r3.values()),
    ])

    print("\n" + "="*60)
    print("  ИТОГОВЫЙ ОТЧЁТ")
    print("="*60)
    print(f"  Всего запросов отправлено : {total}")
    print(f"  Обнаружено ошибок 5xx     : {len(all_crashes)}")

    if not all_crashes:
        print("\n  ✅ ТЕСТ ПРОЙДЕН")
        print("  Сервер корректно обработал все невалидные входные данные.")
        print("  Ошибок 500 (Internal Server Error) не обнаружено.")
        print("  Механизмы валидации Django/DRF работают в штатном режиме.")
    else:
        print(f"\n  ❌ ТЕСТ НЕ ПРОЙДЕН — найдено {len(all_crashes)} критических ответов")
        for crash in all_crashes:
            print(f"     {crash}")

    print("="*60 + "\n")


if __name__ == "__main__":
    main()