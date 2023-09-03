import os
import csv

county_sql_header = """CREATE TABLE IF NOT EXISTS fips_county_info (
    county_code char(3),
    county_name text,
    state_code char(2),
    FOREIGN KEY(state_code) REFERENCES fips_state_info(state_code),
    PRIMARY KEY(state_code, county_code)
);

INSERT INTO fips_county_info (state_code, county_code, county_name)
VALUES
"""

state_sql_header = """CREATE TABLE IF NOT EXISTS fips_state_info (
    state_code char(2) UNIQUE PRIMARY KEY,
    state_name text
);

INSERT INTO fips_state_info (state_code, state_name)
VALUES
"""

## Generate .sql code for state + county level information
with open('2019-geocodes-raw.csv', 'r') as raw_geocodes:
    states_sql = open('2019-fips-states.sql', 'w')
    states_sql.write(state_sql_header)
    counties_sql = open('2019-fips-counties.sql', 'w')
    counties_sql.write(county_sql_header)
    for line in raw_geocodes.readlines():
        line_data = line.split(',')
        ### If line is for a state
        if line_data[0] == '040':
            states_sql.write("    ('{}', '{}'),\n".format(
                line_data[1],
                line_data[6].strip()
            ))
        ### If line is for a county
        if line_data[0] == '050':
            counties_sql.write("    ('{}', '{}', '{}'),\n".format(
                line_data[1],
                line_data[2],
                line_data[6].strip().replace("'", "''")
            ))

govt_units_sql_header = """CREATE TABLE IF NOT EXISTS govt_units_info_2021 (
    pid6_id_code char(6) UNIQUE PRIMARY KEY,
    place_name text,
    fips_place_code char(5),
    population int,
    county_code char(3),
    state_code char(2),
    FOREIGN KEY(county_code, state_code) REFERENCES fips_county_info(county_code, state_code)
);

INSERT INTO govt_units_info_2021 (state_code, county_code, pid6_id_code, fips_place_code, place_name, population)
VALUES
"""

with open('2021-govt-units.sql', 'w') as govt_units_sql:
    govt_units_sql.write(govt_units_sql_header)
    govt_units_sql_stub = "    ('{state_code}', '{county_code}', '{pid6_id_code}', '{fips_place_code}', '{place_name}', '{population}'),\n"
    with open('Govt_Units_2021_Final.csv', 'r') as govt_units_csv:
        govt_units_csv_reader = csv.reader(govt_units_csv.readlines())
        next(govt_units_csv_reader, None)
        for govt_unit in govt_units_csv_reader:
            state_code = govt_unit[14]
            county_code = govt_unit[15]
            pid6 = govt_unit[0]
            place_name = govt_unit[2]
            fips_place_code = govt_unit[16]
            population = int(govt_unit[12].replace(",", ""))
            sql_to_write = govt_units_sql_stub.format(
                state_code=state_code, 
                county_code=county_code,
                pid6_id_code=pid6,
                fips_place_code=fips_place_code,
                place_name=place_name.replace("'", "''"),
                population=population
            )
            govt_units_sql.write(sql_to_write)

expense_item_sql_header = """CREATE TABLE IF NOT EXISTS expense_item_info (
    expense_code char(3) UNIQUE PRIMARY KEY,
    expense_description text
);

INSERT INTO expense_item_info (expense_code, expense_description)
VALUES
"""
with open('expense_codes_2006_manual.txt', 'r') as expense_items_txt:
    with open('expense_item_codes.sql', 'w') as expense_items_sql:
        expense_items_sql.write(expense_item_sql_header)
        for line in expense_items_txt.readlines():
            expense = line.strip().split('|')
            expense_items_sql.write("    ('{}', '{}'),\n".format(
                expense[0].replace("'", "''"), 
                expense[1].strip().replace("'", "''")))

local_state_govt_expenses_sql_header = """CREATE TABLE IF NOT EXISTS local_state_govt_expenses (
    expense_code char(3),
    FOREIGN KEY(expense_code) REFERENCES expense_item_info(expense_code),
    county_code char(3),
    state_code char(2),
    FOREIGN KEY(county_code, state_code) REFERENCES fips_county_info(county_code, state_code),
    pid6_place char(6),
    FOREIGN KEY(pid6_place) REFERENCES govt_units_info_2021(pid6_id_code),
    amount integer
);

INSERT INTO local_state_govt_expenses (state_code, county_code, pid6_place, expense_code, amount)
VALUES
"""
local_state_govt_expenses_stub = "    ('{state_code}', '{county_code}', '{pid6_place}', '{expense_code}', '{amount}'),\n"
with open('2021_fin_est_dat.txt', 'r') as local_state_govt_expenses_txt:
    with open('2021_fin_est_dat.sql', 'w') as local_state_govt_expenses_sql:
        local_state_govt_expenses_sql.write(local_state_govt_expenses_sql_header)
        for line in local_state_govt_expenses_txt.readlines():
            if line[2] != "0":
                state_code = line[:2].strip()
                if len(state_code) > 2:
                    print(state_code)
                county_code = line[3:6]
                pid6_place = line[6:12]
                expense_code = line[12:15]
                amount = int(line[15:27])
                local_state_govt_expenses_sql.write(local_state_govt_expenses_stub.format(
                    state_code=state_code,
                    county_code=county_code,
                    pid6_place=pid6_place,
                    expense_code=expense_code,
                    amount=amount
                ))

