import csv
import re


def detect_value_type(value):
    s = str(value).strip()
    if s == "":
        return "null"
    if s.lower() in ("true", "false", "oui", "non", "yes", "no"):
        return "bool"
    if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}", s):
        return "datetime"
    if re.match(r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}", s):
        return "datetime"
    #on retrouve les dates sans heures
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return "date_only"
    if re.match(r"^\d{2}/\d{2}/\d{4}$", s):
        return "date_only"
    try:
        int(s)
        return "int"
    except ValueError:
        pass
    try:
        float(s.replace(",", "."))
        return "float"
    except ValueError:
        pass
    return "string"


def data_corrections(file_path):

    with open(file_path, "r+", encoding="utf-8") as f:
        reader = csv.reader(f)
        data = list(reader)

        headers = data[0]
        rows = data[1:]
        expected_types = []
        rejected_rows = []
        i = 0
        # Expected type for each column is determined by the most common type in that column, excluding empty values
        while len(expected_types) < len(headers) and i < len(headers):
            list_types = []
            for row in rows:
                list_types.append(detect_value_type(row[i]))
            expected_types.append(max(set(list_types), key=list_types.count))
            i += 1

        # Correct the data
        valid_rows = []
        for row in rows:
            row_valid = True
            corrected_row = list(row)
            for column in range(len(row)):
                value_type = detect_value_type(row[column])
                expected = expected_types[column]
                # Convert dates with "/" to the format YYYY-MM-DD HH:MM
                if expected == "datetime" and "/" in row[column]:
                    parts = re.match(r"^(\d{2})/(\d{2})/(\d{4}) (\d{2}:\d{2})", row[column].strip())
                    if parts:
                        corrected_row[column] = f"{parts.group(3)}-{parts.group(2)}-{parts.group(1)} {parts.group(4)}"
                # If float expected but int found, convert to float with 2 decimal places
                elif expected == "float" and value_type == "int":
                    corrected_row[column] = f"{float(row[column]):.2f}"
                # Normalise booleans : true → yes, false → no
                elif expected == "bool" and value_type == "bool":
                    if row[column].lower() in ("true", "oui"):
                        corrected_row[column] = "yes"
                    elif row[column].lower() in ("false", "non"):
                        corrected_row[column] = "no"
                # Remove row if type does not corrrespond to the expected type or if the value is empty
                elif value_type != expected or row[column] == "":
                    rejected_rows.append(row)
                    row_valid = False
                    break
            if row_valid:
                valid_rows.append(corrected_row)
        data = valid_rows
    
    output_path = file_path.replace(".csv", "_cleaned.csv")
    rejected_path = file_path.replace(".csv", "_rejected.csv")

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

    with open(rejected_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rejected_rows)

    return output_path, rejected_path


for fichier in ["equipment_raw.csv", "maintenance_raw.csv", "incidents_raw.csv"]:
    cleaned, rejected = data_corrections(fichier)
    print(f"{fichier} → {cleaned}, {rejected}")