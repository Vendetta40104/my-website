# server.py
import os
import json
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS

# import qr blueprint
from qrcode_route import qr_bp

app = Flask(__name__)
CORS(app)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.join(BASE_PATH, "bookings.json")

# Default admin credentials (يمكن تغييراتها عبر المتغيرات البيئية)
ADMIN_USERNAME = os.getenv("ADMIN_USER", "mmgamecenter")
ADMIN_PASSWORD = os.getenv("ADMIN_PASS", "Wwwxsw22!")

def load_bookings():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_bookings(bk):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(bk, f, ensure_ascii=False, indent=4)

# Basic auth helpers
def check_auth(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def authenticate():
    return Response(
        'غير مصرح لك بالدخول', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Register QR blueprint
app.register_blueprint(qr_bp)

# ROUTES
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/bookings', methods=['POST'])
def add_booking():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data received"}), 400

    bookings = load_bookings()
    new_booking = {
        "name": data.get("name", ""),
        "number": data.get("phone", ""),
        "date": data.get("date", ""),
        "time": data.get("time", ""),
        "desc": data.get("desc", ""),
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    bookings.append(new_booking)
    save_bookings(bookings)
    return jsonify({"message": "تم إضافة الحجز بنجاح!"}), 200

# Admin page protected
@app.route('/admin')
@requires_auth
def admin_page():
    bookings = load_bookings()   # always read fresh to show latest
    return render_template('admin.html', bookings=bookings)

# Edit booking by index (PUT)
@app.route('/api/edit_booking/<int:index>', methods=['PUT'])
@requires_auth
def edit_booking(index):
    bookings = load_bookings()
    if 0 <= index < len(bookings):
        data = request.get_json() or {}
        bookings[index].update({
            "name": data.get("name", bookings[index].get("name", "")),
            "number": data.get("number", bookings[index].get("number", "")),
            "date": data.get("date", bookings[index].get("date", "")),
            "time": data.get("time", bookings[index].get("time", "")),
            "desc": data.get("desc", bookings[index].get("desc", "")),
            "edited": True
        })
        save_bookings(bookings)
        return jsonify({"message": "تم تعديل الحجز بنجاح ✅"}), 200
    return jsonify({"error": "الحجز غير موجود"}), 404

# Delete booking by index (DELETE)
@app.route('/api/delete_booking/<int:index>', methods=['DELETE'])
@requires_auth
def delete_booking(index):
    bookings = load_bookings()
    if 0 <= index < len(bookings):
        bookings.pop(index)
        save_bookings(bookings)
        return jsonify({"message": "تم حذف الحجز بنجاح ✅"}), 200
    return jsonify({"error": "الحجز غير موجود"}), 404

if __name__ == '__main__':
    # استعمل 0.0.0.0 إذا أردت جعل السيرفر متاحًا من الشبكة (أو استخدم استضافة لاحقًا)
    app.run(host='0.0.0.0', port=5000, debug=False)
