/*******************************************************************************
   Create Tables
********************************************************************************/

-- CUSTOMER
CREATE TABLE public.customer (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(30) NOT NULL, 
    last_name VARCHAR(30) NOT NULL,
    email VARCHAR(60),
    active boolean DEFAULT true NOT NULL,
    address_id INT NOT NULL
);

-- STAFF
CREATE TABLE public.staff (
    staff_id SERIAL PRIMARY KEY,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    email VARCHAR(60),
    active boolean DEFAULT true NOT NULL,
    username VARCHAR(30), 
    password VARCHAR(70),
    picture bytea,
    address_id INT NOT NULL,
    store_id INT NOT NULL
);

-- ACTOR
CREATE TABLE public.actor (
    actor_id SERIAL PRIMARY KEY, 
    first_name varchar(30) NOT NULL,
    last_name varchar(30) NOT NULL
);

-- FILM
CREATE TABLE public.film (
    film_id SERIAL PRIMARY KEY,
    title varchar(200) NOT NULL,
    description text,
    release_year INT,
    length_minutes INT,
    language_id varchar(2) NOT NULL
);

-- CATEGORY
CREATE TABLE public.category (
    category_id SERIAL PRIMARY KEY,
    name varchar(120) NOT NULL
);

-- LANGUAGE
CREATE TABLE public.language (
    language_id varchar(2) PRIMARY KEY,
    name text NOT NULL
);

-- STORE
CREATE TABLE public.store (
    store_id SERIAL PRIMARY KEY,
    address_id INT NOT NULL,
    manager_id INT NOT NULL,
    email VARCHAR(60)
);

-- INVENTORY
CREATE TABLE public.inventory (
    inventory_id SERIAL PRIMARY KEY,
    unit_price NUMERIC(10,2) NOT NULL,
    film_id INT NOT NULL,
    store_id INT NOT NULL
    );

-- PAYMENT
CREATE TABLE public.payment (
    payment_id SERIAL PRIMARY KEY,
    amount numeric(10,2) NOT NULL,
    payment_date timestamp NOT NULL,
    staff_id INT NOT NULL,
    pay_method_id INT NOT NULL

);

-- PAY METHOD
CREATE TABLE public.pay_method (
    pay_method_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- RENTAL
CREATE TABLE public.rental (
    rental_id SERIAL PRIMARY KEY,
    rental_date timestamp NOT NULL,
    return_date timestamp,
    customer_id INT NOT NULL,
    payment_id INT NOT NULL,
    staff_id INT NOT NULL
);

-- ADDRESS
CREATE TABLE public.address (
    address_id SERIAL PRIMARY KEY,
    postal_code VARCHAR(30) NOT NULL,
    number INT,
    floor INT, 
    unit_number varchar(10),
    street_id INT NOT NULL
);

-- STREET
CREATE TABLE public.street (
    street_id SERIAL PRIMARY KEY,
    name varchar(70) NOT NULL,
    city_id int NOT NULL
);

-- CITY
CREATE TABLE public.city (
    city_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    country_code INT NOT NULL
);

-- COUNTRY
CREATE TABLE public.country (
    country_code INT PRIMARY KEY,
    name VARCHAR(40) NOT NULL,
    alpha_2 character(2),
    alpha_3 character(3),
    region_code INT

);

-- REGION
CREATE TABLE public.region (
    region_code INT PRIMARY KEY,
    region VARCHAR(40)
);

-- FILM_ACTOR
CREATE TABLE public.film_actor(
    actor_id INT NOT NULL,
    film_id INT NOT NULL,
    CONSTRAINT film_actor_pkey PRIMARY KEY  (film_id, actor_id)
);

-- FILM_CATEGORY
CREATE TABLE public.film_category(
    film_id INT NOT NULL,
    category_id INT NOT NULL,
    CONSTRAINT film_category_pkey PRIMARY KEY  (film_id, category_id)
);


-- RENTAL_INVENTORY
CREATE TABLE public.rental_inventory(
    inventory_id INT NOT NULL,
    rental_id INT NOT NULL,
    CONSTRAINT rental_inventory_pkey PRIMARY KEY  (rental_id,inventory_id)
);


/*******************************************************************************
    Create Foreign Keys and associated Indexes
********************************************************************************/

-- FILM_ACTOR
ALTER TABLE film_actor ADD CONSTRAINT film_actor_actor_id_fkey FOREIGN KEY (actor_id) REFERENCES actor (actor_id);
CREATE INDEX idx_fk_film_actor_actor_id ON public.film_actor(actor_id);
ALTER TABLE film_actor ADD CONSTRAINT film_actor_film_id_fkey FOREIGN KEY (film_id) REFERENCES film (film_id);
CREATE INDEX idx_fk_film_actor_film_id ON public.film_actor(film_id);

-- FILM_CATEGORY
ALTER TABLE film_category ADD CONSTRAINT film_category_category_id_fkey FOREIGN KEY (category_id) REFERENCES category (category_id);
CREATE INDEX idx_fk_film_category_category_id ON public.film_category(category_id);
ALTER TABLE film_category ADD CONSTRAINT film_category_film_id_fkey FOREIGN KEY (film_id) REFERENCES film (film_id);
CREATE INDEX idx_fk_film_category_film_id ON public.film_category(film_id);

-- RENTAL_INVENTORY
ALTER TABLE rental_inventory ADD CONSTRAINT rental_inventory_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES inventory (inventory_id);
CREATE INDEX idx_fk_rental_inventory_inventory_id ON public.rental_inventory(inventory_id);
ALTER TABLE rental_inventory ADD CONSTRAINT rental_inventory_rental_id_fkey FOREIGN KEY (rental_id) REFERENCES rental (rental_id);
CREATE INDEX idx_fk_rental_inventory_rental_id ON public.rental_inventory(rental_id);

-- CUSTOMER
ALTER TABLE customer ADD CONSTRAINT customer_address_id_fkey FOREIGN KEY (address_id) REFERENCES address (address_id);
CREATE INDEX idx_fk_customer_address_id ON public.customer(address_id);

-- RENTAL
ALTER TABLE rental ADD CONSTRAINT rental_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES payment (payment_id);
CREATE INDEX idx_fk_rental_payment_id ON public.rental(payment_id);
ALTER TABLE rental ADD CONSTRAINT rental_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES staff (staff_id);
CREATE INDEX idx_fk_rental_staff_id ON public.rental(staff_id);
ALTER TABLE rental ADD CONSTRAINT rental_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES customer (customer_id);
CREATE INDEX idx_fk_rental_customer_id ON public.rental(customer_id);

-- INVENTORY
ALTER TABLE inventory ADD CONSTRAINT inventory_store_id_fkey FOREIGN KEY (store_id) REFERENCES store (store_id);
CREATE INDEX idx_fk_inventory_store_id ON public.inventory(store_id);
ALTER TABLE inventory ADD CONSTRAINT inventory_film_id_fkey FOREIGN KEY (film_id) REFERENCES film (film_id);
CREATE INDEX idx_fk_inventory_film_id ON public.inventory(film_id);

-- STAFF
ALTER TABLE staff ADD CONSTRAINT staff_address_id_fkey FOREIGN KEY (address_id) REFERENCES address (address_id);
CREATE INDEX idx_fk_staff_address_id ON public.staff(address_id);
ALTER TABLE staff ADD CONSTRAINT staff_store_id_fkey FOREIGN KEY (store_id) REFERENCES store (store_id);
CREATE INDEX idx_fk_staff_store_id ON public.staff(store_id);

-- PAYMENT
ALTER TABLE payment ADD CONSTRAINT payment_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES staff (staff_id);
CREATE INDEX idx_fk_payment_staff_id ON public.payment(staff_id);
ALTER TABLE payment ADD CONSTRAINT payment_pay_method_id_fkey FOREIGN KEY (pay_method_id) REFERENCES pay_method (pay_method_id);
CREATE INDEX idx_fk_payment_pay_method_id ON public.payment(pay_method_id);

-- STORE
ALTER TABLE store ADD CONSTRAINT store_address_id_fkey FOREIGN KEY (address_id) REFERENCES address (address_id);
CREATE INDEX idx_fk_store_address_id ON public.store(address_id);
ALTER TABLE store ADD CONSTRAINT store_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES staff (staff_id);
CREATE INDEX idx_fk_store_manager_id ON public.store(manager_id);

-- ADDRESS
ALTER TABLE address ADD CONSTRAINT address_street_id_fkey FOREIGN KEY (street_id) REFERENCES street (street_id);
CREATE INDEX idx_fk_address_street_id ON public.address(street_id);

-- STREET
ALTER TABLE street ADD CONSTRAINT street_city_id_fkey FOREIGN KEY (city_id) REFERENCES city (city_id);
CREATE INDEX idx_fk_street_city_id ON public.street(city_id);

-- CITY
ALTER TABLE city ADD CONSTRAINT city_country_code_fkey FOREIGN KEY (country_code) REFERENCES country (country_code);
CREATE INDEX idx_fk_city_country_code ON public.city(country_code);

-- COUNTRY
ALTER TABLE country ADD CONSTRAINT country_region_code_fkey FOREIGN KEY (region_code) REFERENCES region (region_code);
CREATE INDEX idx_fk_country_region_code ON public.country(region_code);

-- FILM
ALTER TABLE film ADD CONSTRAINT film_language_id_fkey FOREIGN KEY (language_id) REFERENCES language (language_id);
CREATE INDEX idx_fk_film_language_id ON public.film(language_id);



