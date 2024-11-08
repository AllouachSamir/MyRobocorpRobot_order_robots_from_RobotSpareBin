from robocorp.tasks import task
from robocorp import browser
from Functions import get_orders, close_annoying_modal, fill_the_form, preview_the_robot, submit_the_order, initialize_the_form, store_receipt_as_pdf, get_screenshot, embed_screenshot_to_receipt, archive_receipts


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    """_________________________Variables_________________________"""
    str_url = "https://robotsparebinindustries.com/#/robot-order"
    str_csvFileUrl = "https://robotsparebinindustries.com/orders.csv"
    dt_table =''
    receipt_locator = "xpath=//div[@id='receipt']" 
    alert_locator = "//div[contains(@class, 'alert alert-danger')]" 
    directory_path = "output/receipts"  # Répertoire à archiver
    output_zip_path = "output/receipts_archive.zip"  # Chemin du fichier ZIP
    try :

        browser.configure(

            screenshot = "only-on-failure",
            headless = False,
            slowmo = 100,
            browser_engine = "chromium",

        )
        page = browser.goto(str_url)

        dt_table = get_orders(str_csvFileUrl)

        for row in dt_table:
            print(row)
            close_annoying_modal(page)
            fill_the_form(row, page)
            preview_the_robot(page)
            pathpdffile = store_receipt_as_pdf(row["Order number"])
            if submit_the_order(page) is None :
                
                screenshot = get_screenshot(page, receipt_locator)
                embed_screenshot_to_receipt(screenshot, pathpdffile)
                
            else :
                
                screenshot = get_screenshot(page, alert_locator)
                embed_screenshot_to_receipt(screenshot, pathpdffile)
            initialize_the_form(page)
            

    finally :
        
        archive_receipts(directory_path, output_zip_path)
        print("done")



