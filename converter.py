from bs4 import BeautifulSoup
import datetime
import boto3
import json
import csv
import os


# Esta es la función principal. Llama a las demás funciones para extraer
# el documento html, convertirlo a .csv y subirlo al bucket de destino
def convert():

    # Objetos
    s3 = boto3.client('s3')

    # Variables
    today = datetime.date.today()
    source_file_name = today.strftime("%Y-%m-%d") + ".html"
    csv_file_name = f'{today}.csv'
    source_bucket = 'landing-casas-salazar-bermudez'
    destination_bucket = 'csv-casas-salazar-bermudez'
    csv_key = f"{today}.csv"
    try:
        # Descarga del documento html
        s3.download_file(source_bucket, source_file_name, source_file_name)
        # Lectura del archivo
        html_doc = read_file(source_file_name)
        # Conversión a JSON
        json_file = extract_json(html_doc)
        # Creación del .csv
        make_csv(csv_file_name, json_file)

        # Upload del archivo .csv al bucket de destino
        with open(csv_file_name, 'rb') as csvfile:
            s3.upload_fileobj(csvfile, destination_bucket, csv_key)

        # Se remueven los archivos descargados
        os.remove(source_file_name)
        os.remove('/tmp/' + csv_file_name)

    except Exception as e:
        # Handle the exception
        print(f"Ocurrió un error: {e}")

    return {
        'statusCode': 200
    }


# Este método descarga el archivo del bucket fuente.
def read_file(source_file_name):

    with open(source_file_name, 'r') as f:
        html_doc = f.read()
    return html_doc


# Este método convierte una dección del html y lo convierte en formato JSON
def extract_json(html_doc):

    soup = BeautifulSoup(html_doc, 'html.parser')
    div_tag_script = soup.find('script', type='application/ld+json')
    json_text = div_tag_script.string.strip()
    json_file = json.loads(json_text)
    return json_file


# Este método recibe el archivo JSON y lo convierte en .csv
def make_csv(csv_file_name, data):

    fields = ["date", "@type", "name", "numberOfBathroomsTotal",
              "address.addressRegion", "address.addressLocality",
              "address.addressCountry.name"]
    header_row = dict((field, field) for field in fields)
    with open('/tmp/' + csv_file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writerow(header_row)

        for item in data['about']:
            row = {
                "date":
                    datetime.date.today().strftime("%Y-%m-%d"),
                "@type":
                    item.get('@type', ''),
                "name":
                    item.get('name', ''),
                "numberOfBathroomsTotal":
                    item.get('numberOfBathroomsTotal', ''),
                "address.addressRegion":
                    item.get('address', {}).get('addressRegion', ''),
                "address.addressLocality":
                    item.get('address', {}).get('addressLocality', ''),
                "address.addressCountry.name":
                    item.get('address', {})
                    .get('addressCountry', {}).get('name', '')
            }
            writer.writerow(row)
