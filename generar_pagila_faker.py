from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from decimal import Decimal

try:
    from faker import Faker
except ModuleNotFoundError as exc:
    raise SystemExit(
        "No se encontro la libreria Faker. Instalacion: python -m pip install Faker"
    ) from exc


FILM_COUNT = 5_000
OUTPUT_FILE = "pagila-faker-test.sql"
INVENTORY_COUNT = 8_000
CUSTOMER_COUNT = 7_000
RENTAL_COUNT = 30_000
ACTOR_COUNT = 400
STAFF_COUNT = 12
STORE_COUNT = 4
COUNTRY_COUNT = 35
CITY_COUNT = 250
CATEGORY_NAMES = [
    "Action",
    "Animation",
    "Children",
    "Classics",
    "Comedy",
    "Documentary",
    "Drama",
    "Family",
    "Foreign",
    "Games",
    "Horror",
    "Music",
    "New",
    "Sci-Fi",
    "Sports",
    "Travel",
    "Thriller",
    "Romance",
    "Mystery",
    "Adventure",
]
MAIN_LANGUAGE_CODES = ("en", "es", "fr", "de", "it", "pt")
PAYMENT_METHODS = ("Mercado Pago", "Efectivo", "Debito", "Credito")


fake = Faker("es_AR")
Faker.seed(20260615)
random.seed(20260615)


def sql_text(value: object) -> str:
    if value is None:
        return "NULL"
    text = str(value).replace("\\", "\\\\").replace("'", "''")
    return f"'{text}'"


def sql_bool(value: bool) -> str:
    return "true" if value else "false"


def sql_ts(value: datetime) -> str:
    return sql_text(value.strftime("%Y-%m-%d %H:%M:%S"))


def money(min_value: str = "1.99", max_value: str = "19.99") -> Decimal:
    cents = random.randint(int(Decimal(min_value) * 100), int(Decimal(max_value) * 100))
    return Decimal(cents) / Decimal(100)


def write_insert(handle, table: str, columns: tuple[str, ...], rows) -> None:
    handle.write(f"INSERT INTO public.{table} ({', '.join(columns)}) VALUES\n")
    rendered_rows = []
    for row in rows:
        rendered_rows.append("    (" + ", ".join(row) + ")")
    handle.write(",\n".join(rendered_rows))
    handle.write(";\n\n")


def sql_int_or_null(value: str) -> str:
    value = value.strip()
    return str(int(value)) if value else "NULL"


def load_languages(path: str) -> list[tuple[str, str]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        languages = [
            (row["alpha2"].upper(), row["English"])
            for row in csv.DictReader(handle)
            if row["alpha2"].strip() and row["English"].strip()
        ]

    rows = {code.lower(): name for code, name in languages}
    missing = [code for code in MAIN_LANGUAGE_CODES if code not in rows]
    if missing:
        raise SystemExit(
            f"Faltan codigos de lenguaje en {path}: {', '.join(missing)}"
        )

    return languages


def main_languages(languages: list[tuple[str, str]]) -> list[tuple[str, str]]:
    language_by_code = {code: name for code, name in languages}
    return [
        (code.upper(), language_by_code[code.upper()])
        for code in MAIN_LANGUAGE_CODES
    ]


def load_countries(path: str) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        countries = list(csv.DictReader(handle))

    if len(countries) < COUNTRY_COUNT:
        raise SystemExit(
            f"{path} tiene {len(countries)} paises, se necesitan {COUNTRY_COUNT}."
        )

    return countries[:COUNTRY_COUNT]


def make_countries(source_rows: list[dict[str, str]]):
    countries = []
    for row in source_rows:
        countries.append(
            (
                sql_int_or_null(row["country-code"]),
                sql_text(row["name"][:40]),
                sql_text(row["alpha-2"][:2]),
                sql_text(row["alpha-3"][:3]),
                sql_text(row["region"][:40]),
                sql_text(row["sub-region"][:40]),
                sql_text(row["intermediate-region"][:40])
                if row["intermediate-region"].strip()
                else "NULL",
                sql_int_or_null(row["region-code"]),
                sql_int_or_null(row["sub-region-code"]),
                sql_int_or_null(row["intermediate-region-code"]),
            )
        )
    return countries


def main() -> None:
    output = OUTPUT_FILE
    languages = load_languages("language-codes.csv")
    film_languages = main_languages(languages)
    source_countries = load_countries("maestra_paises.csv")
    country_ids = [int(row["country-code"]) for row in source_countries]
    city_ids = list(range(1, CITY_COUNT + 1))
    address_count = CUSTOMER_COUNT + STAFF_COUNT + STORE_COUNT
    address_ids = list(range(1, address_count + 1))
    customer_address_ids = address_ids[:CUSTOMER_COUNT]
    staff_address_ids = address_ids[CUSTOMER_COUNT : CUSTOMER_COUNT + STAFF_COUNT]
    store_address_ids = address_ids[CUSTOMER_COUNT + STAFF_COUNT :]

    rental_customer_ids = []
    rental_staff_ids = []
    rental_dates = []
    rental_inventory_ids = []

    with open(output, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("-- Datos generados por generar_pagila_faker.py para pagila-schema.sql\n")
        handle.write("-- Ejecutar luego de crear el esquema.\n\n")
        handle.write("BEGIN;\n\n")

        write_insert(
            handle,
            "language",
            ("language_id", "name"),
            [(sql_text(code), sql_text(name)) for code, name in languages],
        )

        write_insert(
            handle,
            "country",
            (
                "country_code",
                "name",
                "alpha_2",
                "alpha_3",
                "region",
                "sub_region",
                "intermediate_region",
                "region_code",
                "sub_region_code",
                "intermediate_region_code",
            ),
            make_countries(source_countries),
        )

        write_insert(
            handle,
            "city",
            ("city_id", "city", "country_code"),
            (
                (
                    str(city_id),
                    sql_text(fake.city()[:50]),
                    str(random.choice(country_ids)),
                )
                for city_id in city_ids
            ),
        )

        write_insert(
            handle,
            "address",
            ("address_id", "address", "district", "postal_code", "city_id"),
            (
                (
                    str(address_id),
                    sql_text(fake.street_address()[:70]),
                    sql_text(fake.province()[:40]),
                    sql_text(fake.postcode()[:30]),
                    str(random.choice(city_ids)),
                )
                for address_id in address_ids
            ),
        )

        handle.write("ALTER TABLE public.staff DISABLE TRIGGER ALL;\n")
        handle.write("ALTER TABLE public.store DISABLE TRIGGER ALL;\n\n")

        write_insert(
            handle,
            "staff",
            (
                "staff_id",
                "first_name",
                "last_name",
                "email",
                "active",
                "username",
                "password",
                "picture",
                "address_id",
                "store_id",
            ),
            (
                (
                    str(staff_id),
                    sql_text(fake.first_name()[:30]),
                    sql_text(fake.last_name()[:30]),
                    sql_text(fake.unique.email()[:60]),
                    sql_bool(True),
                    sql_text(f"staff{staff_id:02d}"),
                    sql_text(fake.password(length=18)[:70]),
                    "NULL",
                    str(staff_address_ids[staff_id - 1]),
                    str(((staff_id - 1) % STORE_COUNT) + 1),
                )
                for staff_id in range(1, STAFF_COUNT + 1)
            ),
        )

        write_insert(
            handle,
            "store",
            ("store_id", "address_id", "manager_id"),
            (
                (
                    str(store_id),
                    str(store_address_ids[store_id - 1]),
                    str(((store_id - 1) % STAFF_COUNT) + 1),
                )
                for store_id in range(1, STORE_COUNT + 1)
            ),
        )

        handle.write("ALTER TABLE public.store ENABLE TRIGGER ALL;\n")
        handle.write("ALTER TABLE public.staff ENABLE TRIGGER ALL;\n\n")

        write_insert(
            handle,
            "customer",
            ("customer_id", "first_name", "last_name", "email", "active", "address_id"),
            (
                (
                    str(customer_id),
                    sql_text(fake.first_name()[:30]),
                    sql_text(fake.last_name()[:30]),
                    sql_text(fake.unique.email()[:60]),
                    sql_bool(random.random() > 0.04),
                    str(customer_address_ids[customer_id - 1]),
                )
                for customer_id in range(1, CUSTOMER_COUNT + 1)
            ),
        )

        write_insert(
            handle,
            "category",
            ("category_id", "name"),
            (
                (str(category_id), sql_text(name))
                for category_id, name in enumerate(CATEGORY_NAMES, start=1)
            ),
        )

        write_insert(
            handle,
            "actor",
            ("actor_id", "first_name", "last_name"),
            (
                (
                    str(actor_id),
                    sql_text(fake.first_name()[:30]),
                    sql_text(fake.last_name()[:30]),
                )
                for actor_id in range(1, ACTOR_COUNT + 1)
            ),
        )

        film_category_rows = []
        film_actor_rows = []
        film_rows = []
        for film_id in range(1, FILM_COUNT + 1):
            words = fake.words(nb=random.randint(2, 4), unique=True)
            title = " ".join(word.capitalize() for word in words)
            film_rows.append(
                (
                    str(film_id),
                    sql_text(title[:200]),
                    sql_text(fake.paragraph(nb_sentences=3)),
                    str(random.randint(1980, 2026)),
                    str(random.randint(60, 185)),
                    sql_text(random.choice(film_languages)[0]),
                )
            )
            film_category_rows.append(
                (str(film_id), str(random.randint(1, len(CATEGORY_NAMES))))
            )
            for actor_id in random.sample(range(1, ACTOR_COUNT + 1), random.randint(2, 6)):
                film_actor_rows.append((str(actor_id), str(film_id)))

        write_insert(
            handle,
            "film",
            ("film_id", "title", "description", "release_year", "length_minutes", "language_id"),
            film_rows,
        )

        write_insert(
            handle,
            "film_category",
            ("film_id", "category_id"),
            film_category_rows,
        )

        write_insert(
            handle,
            "film_actor",
            ("actor_id", "film_id"),
            film_actor_rows,
        )

        write_insert(
            handle,
            "inventory",
            ("inventory_id", "unit_price", "film_id", "store_id"),
            (
                (
                    str(inventory_id),
                    f"{money('2.99', '29.99'):.2f}",
                    str(random.randint(1, FILM_COUNT)),
                    str(random.randint(1, STORE_COUNT)),
                )
                for inventory_id in range(1, INVENTORY_COUNT + 1)
            ),
        )

        payment_rows = []
        rental_rows = []
        rental_inventory_rows = []
        start_date = datetime(2023, 1, 1, 9, 0, 0)
        for rental_id in range(1, RENTAL_COUNT + 1):
            customer_id = random.randint(1, CUSTOMER_COUNT)
            staff_id = random.randint(1, STAFF_COUNT)
            rental_date = start_date + timedelta(
                minutes=random.randint(0, 60 * 24 * 365 * 3)
            )
            return_date = rental_date + timedelta(days=random.randint(1, 14))
            inventory_id = random.randint(1, INVENTORY_COUNT)
            rental_customer_ids.append(customer_id)
            rental_staff_ids.append(staff_id)
            rental_dates.append(rental_date)
            rental_inventory_ids.append(inventory_id)
            payment_rows.append(
                (
                    str(rental_id),
                    f"{money('2.99', '29.99'):.2f}",
                    sql_ts(rental_date + timedelta(minutes=random.randint(0, 90))),
                    sql_text(random.choice(PAYMENT_METHODS)),
                    str(staff_id),
                )
            )
            rental_rows.append(
                (
                    str(rental_id),
                    sql_ts(rental_date),
                    sql_ts(return_date),
                    str(customer_id),
                    str(rental_id),
                    str(staff_id),
                )
            )
            rental_inventory_rows.append((str(inventory_id), str(rental_id)))

        write_insert(
            handle,
            "payment",
            ("payment_id", "amount", "payment_date", "payment_method", "staff_id"),
            payment_rows,
        )

        write_insert(
            handle,
            "rental",
            ("rental_id", "rental_date", "return_date", "customer_id", "payment_id", "staff_id"),
            rental_rows,
        )

        write_insert(
            handle,
            "rental_inventory",
            ("inventory_id", "rental_id"),
            rental_inventory_rows,
        )

        for table, column, value in (
            ("city", "city_id", CITY_COUNT),
            ("address", "address_id", address_count),
            ("staff", "staff_id", STAFF_COUNT),
            ("store", "store_id", STORE_COUNT),
            ("customer", "customer_id", CUSTOMER_COUNT),
            ("category", "category_id", len(CATEGORY_NAMES)),
            ("actor", "actor_id", ACTOR_COUNT),
            ("film", "film_id", FILM_COUNT),
            ("inventory", "inventory_id", INVENTORY_COUNT),
            ("payment", "payment_id", RENTAL_COUNT),
            ("rental", "rental_id", RENTAL_COUNT),
        ):
            handle.write(
                f"SELECT setval(pg_get_serial_sequence('public.{table}', '{column}'), {value}, true);\n"
            )

        handle.write("\nCOMMIT;\n")

    print(f"SQL generado en {output}")
    print(f"Peliculas: {FILM_COUNT}")
    print(f"Inventario: {INVENTORY_COUNT}")
    print(f"Clientes: {CUSTOMER_COUNT}")
    print(f"Rentas: {RENTAL_COUNT}")
    print(f"Payments: {RENTAL_COUNT} (uno por renta)")

main()
