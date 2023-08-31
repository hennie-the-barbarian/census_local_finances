import os
import csv

county_sql_header = """CREATE TABLE IF NOT EXISTS fips_county_info (
    county_code char(3),
    county_name text,
    state_code char(2),
    CONSTRAINT fk_state_code
        FOREIGN KEY(state_code) 
	        REFERENCES fips_state_info(state_code)
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

places_sql_header = """CREATE TABLE IF NOT EXISTS fips_places_info (
    place_code char(5),
    place_name text,
    counties text[],
    state_code char(2),
    CONSTRAINT fk_state_code
        FOREIGN KEY(state_code) 
	        REFERENCES fips_state_info(state_code)
);

INSERT INTO fips_places_info (state_code, counties, place_code, place_name)
VALUES
"""

### Data connecting places to county are in a different set of files
base_dir = 'fips_place_county_data'
with open('2020-fips-places.sql', 'w') as places_sql:
    places_sql.write(places_sql_header)
    for filename in os.listdir(base_dir):
        with open(base_dir + "/" + filename, 'r') as curr_file:
            for line in curr_file.readlines()[1:]:
                line_data = line.split('|')
                if len(line_data) < 9:
                    print(line_data)
                    continue
                counties_list = line_data[8].strip().split('~~~')
                counties_string = '{{"{}"'.format(counties_list[0].replace("'", "''"))
                for county in counties_list[1:]:
                    counties_string += ', "{}"'.format(county.replace("'", "''"))
                counties_string += "}"
                places_sql.write("    ('{}', '{}', '{}', '{}'),\n".format(
                    line_data[1],
                    counties_string,
                    line_data[2],
                    line_data[4].replace("'", "''")
                ))

expense_item_sql_header = """CREATE TABLE IF NOT EXISTS expense_item_info (
    expense_code char(3),
    expense_description text
);

INSERT INTO expense_item_info (expense_code, expense_description)
VALUES
"""
with open('expense_item_codes.csv', 'r') as expense_items_csv:
    with open('expense_item_codes.sql', 'w') as expense_items_sql:
        expense_items_sql.write(expense_item_sql_header)
        items_csv_reader = csv.reader(expense_items_csv.readlines())
        for expense in items_csv_reader:
            expense_items_sql.write("    ('{}', '{}'),\n".format(
                expense[0].replace("'", "''"), 
                expense[1].replace("'", "''")))

