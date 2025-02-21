import imaplib
import email
import os
from config import GMAIL_USER, APP_PASS

# Adjust these:
GMAIL_USER = GMAIL_USER
APP_PASS = APP_PASS  # or your normal password if 2FA is off
OUTPUT_DIR = "../receipts/pdfs"  # Folder where we save PDFs


def download_pdfs_from_gmail():
    # Ensure the output folder exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1) Connect to Gmail IMAP (on port 993 with SSL)
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(GMAIL_USER, APP_PASS)

    # 2) Select the mailbox. For Gmail, normally "INBOX" works,
    #    but if your interface is German and "Posteingang" is recognized, try that:
    mail.select("INBOX")  # or "INBOX" if needed

    # 3) Search for messages from "noreply@app.edeka.de"
    #    with subject "EDEKA - Vielen Dank für Ihren Einkauf".
    #    We combine them in a single search command using IMAP syntax:
    #    (FROM "..." SUBJECT "...")
    #    Make sure to put them in parentheses.
    status, msg_ids = mail.search(None, '(FROM "noreply@app.edeka.de" SUBJECT "EDEKA - Vielen Dank")')
    if status != "OK":
        print("No matching emails found or an error occurred.")
        return

    # msg_ids is a space-separated string of email IDs
    id_list = msg_ids[0].split()
    print(f"Found {len(id_list)} matching emails in the mailbox.")

    for email_id in id_list:
        # 4) Fetch the entire email
        typ, msg_data = mail.fetch(email_id, "(RFC822)")
        if typ != "OK":
            print(f"Failed to fetch email ID {email_id}")
            continue

        # 5) Parse the email content
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # 6) Check each part of the email to find PDF attachments
        for part in msg.walk():
            # Check for attachment via content disposition
            content_disposition = str(part.get("Content-Disposition") or "")
            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename and filename.lower().endswith(".pdf"):
                    # 7) Save the PDF
                    file_path = os.path.join(OUTPUT_DIR, filename)
                    if not os.path.isfile(file_path):
                        with open(file_path, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        print(f"Downloaded: {file_path}")
                    else:
                        print(f"File already exists, skipped: {file_path}")

    # 8) Logout
    mail.close()
    mail.logout()


if __name__ == "__main__":
    download_pdfs_from_gmail()
