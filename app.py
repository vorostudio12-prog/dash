from flask import Flask, jsonify, request, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)

# Google Sheets setup
import os
import json

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = json.loads(os.environ.get("GOOGLE_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)
sheet = client.open("Dental Bot")
bookings_sheet = sheet.worksheet("Bookings")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/bookings")
def get_bookings():
    records = bookings_sheet.get_all_records()
    return jsonify(records)

@app.route("/api/update", methods=["POST"])
def update_status():
    data = request.json
    row = int(data["row"]) + 2  # +2 because row 1 is header, and list is 0-indexed
    status = data["status"]
    bookings_sheet.update_cell(row, 6, status)  # Column F is Status
    return jsonify({"success": True})

@app.route("/api/revenue")
def get_revenue():
    records = bookings_sheet.get_all_records()
    total = 0
    done_count = 0
    missed_count = 0
    pending_count = 0
    monthly = {}

    for record in records:
        status = record.get("Status", "")
        price = 0
        try:
            price = int(str(record.get("Price", 0)).replace("₹", "").replace(",", "").strip())
        except:
            price = 0

        if status == "Done":
            total += price
            done_count += 1
            date = str(record.get("Date", ""))
            month = date[:7] if len(date) >= 7 else "Unknown"
            monthly[month] = monthly.get(month, 0) + price
        elif status == "Missed":
            missed_count += 1
        elif status == "Pending":
            pending_count += 1

    return jsonify({
        "total_revenue": total,
        "done": done_count,
        "missed": missed_count,
        "pending": pending_count,
        "monthly": monthly
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
