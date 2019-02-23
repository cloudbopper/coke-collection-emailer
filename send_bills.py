"""Script to send emails for collecting coke money"""

import argparse
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from getpass import getpass
import smtplib

# csv fields
NAME = "Name"
EMAIL = "Email"
BALANCE = "Current balance"
UNKNOWN = "???"

# czar info
CZAR_USERNAME = "sacm.coke.czar"
CZAR_EMAIL = "{0}@gmail.com".format(CZAR_USERNAME)
CZAR_NAME = "Akshay Sood"
CZAR_OFFICE = "MSC 4715"
CZAR_MAILROOM = "MSC 4730"

# email body
SUBJECT = "MSC Coke Balance"
CLOSE_ACCOUNT = "If you would like to close your account (and stop receiving these emails), reply and let me know."
PAYMENT_DETAILS = ("Cash payments can be brought to my office ({0}). Please be sure to indicate your name in case "
                   "you're not handing over the payment personally. Alternatively, checks can be left in my mailbox "
                   "in {1}. Checks should be written to SACM. I cannot provide change for cash payments, "
                   "but I can carry over any excess payment as a system credit.".format(CZAR_OFFICE, CZAR_MAILROOM))
THANKS = "Thank you, and please let me know if you believe I've made any error.\n\n- {0}, MSC Coke Czar".format(CZAR_NAME)
DEADLINE = "two weeks"
SUCCESSOR_ADVERTISEMENT = ("P.S.: the time has come for me to pass on the envied title of Coke Head to another. "
                           "If you're a graduate student in the Computer Sciences department with an office in MSC, "
                           "here are some reasons you might consider taking the position:\n\n"
                           "1. Refer to yourself either as the Coke Head or Coke Czar depending on whether or not "
                           "you are talking with someone who appreciates drug-related humor!\n"
                           "2. You'll have total, uncontested control over what is ordered and when. Want the whole "
                           "fridge packed with Sprite and nothing but Sprite? Your wish is everyone else's "
                           "begruding acceptance! (So please don't do that.)\n"
                           "3. If you can figure out the logistics involved in the cans being different sizes and "
                           "costing more than regular cans, you could be the hero who brings energy drinks to the "
                           "MSC Coke fridge!\n"
                           "4. Stocking cans is even more fun than whitewashing Tom Sawyer's fence!\n"
                           "5. Very low rate of mutiny.\n"
                           "6. Embezzlement opportunities?\n"
                           "7. Someone's gotta.\n\n"
                           "If you meet the criteria and would like to hold this honor and bear this burden, "
                           "let me know you're interested. If nobody is, someone will be drafted or something. "
                           "The Coke-brand soft drinks must flow!")


def main():
    """Main"""
    parser = argparse.ArgumentParser()
    parser.add_argument("balance_filename", help="file containing balances")
    parser.add_argument("-advertise_successor", action="store_true")
    args = parser.parse_args()

    server = setup()

    with open(args.balance_filename, "r") as balance_file:
        reader = csv.DictReader(balance_file)
        for row in reader:
            name, destination_email, amount = (row[key] for key in [NAME, EMAIL, BALANCE])
            if not destination_email or not name or name == "???":
                continue
            amount = float(amount.replace("$", ""))
            body = "Hi {0},\n\n".format(name)
            if amount < 0.00:
                # system credit
                body += ("You have a credit of ${0:.2f} for MSC Coke (you do not owe anything).\n\n{1}\n\n{2}"
                         .format(-amount, CLOSE_ACCOUNT, THANKS))
            elif amount == 0.00:
                # zero balance
                body += "Your MSC Coke balance is $0.00 (you do not owe anything).\n\n{0}\n\n{1}".format(CLOSE_ACCOUNT, THANKS)
            elif amount < 5.00:
                # low charge, can pay later
                body += ("You owe ${0:.2f} for your MSC Coke. Because your balance is small, you may wait to pay "
                         "until the next collection if you prefer.\n\n{1}\n\n{2}".format(amount, PAYMENT_DETAILS, THANKS))
            else:
                # please pay soon
                body += ("You owe ${0:.2f} for your MSC Coke. Please make your payment in {3}.\n\n{1}\n\n{2}"
                         .format(amount, PAYMENT_DETAILS, THANKS, DEADLINE))
            if args.advertise_successor:
                body += "\n\n\n\n{0}".format(SUCCESSOR_ADVERTISEMENT)

            print("Mailing {0} at {1}...".format(name, destination_email))
            send_email(server, destination_email, SUBJECT, body)


def setup():
    """Email Setup"""
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(CZAR_USERNAME, getpass("Enter password for {0}:".format(CZAR_EMAIL)))
    return server


def send_email(server, destination_email, subject, body):
    """Sends email"""
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()

    server.sendmail(CZAR_EMAIL, destination_email, text)

if __name__ == "__main__":
    main()
