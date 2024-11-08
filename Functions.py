
from RPA.HTTP import HTTP
import csv
import io
from fpdf import FPDF
import os
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
import zipfile


def get_orders(str_inUrl):

    http = HTTP()
    response = http.download(str_inUrl, stream=True)
    csv_data = io.StringIO(response.text)
    table = csv.reader(csv_data)
    
    # Get headers from the first row
    headers = next(table)
    
    # Convert each row to a dictionary using the headers as keys
    orders = [dict(zip(headers, row)) for row in table]

    return orders


def close_annoying_modal(br_page):
    try:

        br_page.wait_for_selector("xpath=//button[contains(.,'OK')]")
        br_page.locator("xpath=//button[contains(.,'OK')]").click()

    except TimeoutError:        

        print("The modal did not appear, or the elements were not found.")

    finally:

        print("close annoying modal done")


def fill_the_form(rw_row, br_page):
    try :
        
        br_page.wait_for_selector("#head")
        br_page.locator("#head").select_option(rw_row["Head"])
        body_selector = f"#id-body-{rw_row['Body']}"
        br_page.locator(body_selector).click()
        br_page.locator("xpath=//div[@id='root']/div/div/div/div/form/div[3]/input").fill(rw_row["Legs"])
        br_page.locator("#address").fill(rw_row["Address"])
        br_page.locator("#preview").click()
    
    except Exception as e:
        print(f"Error while filling the form: {e}")
    finally:
        print("Form filled with:", rw_row)


def preview_the_robot(br_page):
    try :

        br_page.locator("#preview").click()

    except Exception as e:
        print(f"Preview the robot : {e}")
    finally:
        print("Preview the robot done")


def submit_the_order(br_page):
    err = None  # Initialize err to None
    
    try:
        br_page.locator("#order").click()  # Attempt to submit the order
        br_page.locator("xpath=//div[@id='receipt']/h3").wait_for()  # Wait for the receipt to confirm submission

    except Exception as e:
        print(f"Submit the order error: {e}")
        err = get_error_message(br_page)  # Capture the error message, if available
    
    finally:
        if err:
            print("Error:", err)
            return err
        else:
            print("Submit the order done")
            return None  # Indicating successful order submission


def initialize_the_form(br_page):
    try :
        br_page.locator("xpath=//a[contains(.,'Home')]").click()

        br_page.locator("xpath=//a[contains(.,'Order your robot!')]").click()

        
    except Exception as e:
        print(f"Initialize the form : {e}")
    finally:
        print("Initialize the form done")


def store_receipt_as_pdf(order_number):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Order Receipt", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Order Number: {order_number}", ln=True)

    # Define the output directory and create it if it doesn't exist
    output_dir = os.path.join("output", "receipts")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"receipt_{order_number}.pdf")
    
    pdf.output(file_path)
    return file_path


def get_error_message(br_page):
    text = ""
    
    try:
        # Locate the error message by its class name and check if it's visible
        alert_locator = br_page.locator("//div[contains(@class, 'alert alert-danger')]")
        
        if alert_locator.is_visible():
            # Retrieve the text content directly from the alert element
            text = alert_locator.inner_text()
        
        return text
    
    finally:
        # Only print the error message if text is not empty
        if text:
            print("Error:", text)
        else:
            print("No error message found.")


def get_screenshot(br_page,locator):

    """ui_element = br_page.locator("xpath=//div[@id='receipt']")"""

    screenshot = br_page.locator(locator).screenshot()

    return screenshot


def embed_screenshot_to_receipt(screenshot_data, pdf_file):

    
    # Charger l'image en mémoire
    if isinstance(screenshot_data, bytes):
        img = Image.open(io.BytesIO(screenshot_data))
    else:
        img = Image.open(screenshot_data)  # Si `screenshot_data` est un chemin de fichier

    # Créer une nouvelle page PDF avec l'image à l'aide de fpdf
    pdf_with_image = FPDF()
    pdf_with_image.add_page()

    # Redimensionner l'image pour s'adapter à la page PDF
    img_width, img_height = img.size
    aspect_ratio = img_height / img_width
    pdf_img_width = 180  # Largeur souhaitée de l'image dans le PDF
    pdf_img_height = pdf_img_width * aspect_ratio

    # Sauvegarder temporairement l'image dans un fichier pour fpdf
    temp_image_path = "temp_image.png"
    img.save(temp_image_path)

    # Ajouter l'image à la page PDF
    pdf_with_image.image(temp_image_path, x=10, y=50, w=pdf_img_width, h=pdf_img_height)

    # Sauvegarder la page PDF avec l'image dans un fichier temporaire
    temp_pdf_path = "temp_page_with_image.pdf"
    pdf_with_image.output(temp_pdf_path)

    # Charger le PDF d'origine et le PDF temporaire contenant l'image
    reader = PdfReader(pdf_file)
    writer = PdfWriter()

    # Ajouter les pages du PDF d'origine
    for page in reader.pages:
        writer.add_page(page)

    # Ajouter la page avec l'image comme dernière page
    with open(temp_pdf_path, "rb") as f:
        image_pdf_reader = PdfReader(f)
        writer.add_page(image_pdf_reader.pages[0])

    # Enregistrer le résultat dans le même fichier PDF d'origine
    with open(pdf_file, "wb") as f:
        writer.write(f)

    # Supprimer les fichiers temporaires
    os.remove(temp_image_path)
    os.remove(temp_pdf_path)

    print(f"L'image a été ajoutée à {pdf_file}")
    return pdf_file


def archive_receipts(directory_path, output_zip_path):
    # Crée un fichier ZIP
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Parcourt tous les fichiers et sous-dossiers du répertoire
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                # Calcule le chemin complet du fichier
                file_path = os.path.join(root, file)
                # Ajoute le fichier au ZIP avec un chemin relatif
                arcname = os.path.relpath(file_path, start=directory_path)
                zipf.write(file_path, arcname)