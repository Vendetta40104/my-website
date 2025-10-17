# qrcode_route.py
import os
import qrcode
from io import BytesIO
from flask import Blueprint, send_file

qr_bp = Blueprint('qr_bp', __name__)

# استخدم الرابط العام إن وُجد متغير بيئي أو افتراضي localhost
BASE_URL = os.getenv("BASE_URL", "https://mmgamecenter.com")

@qr_bp.route('/qrcode')
def generate_qr():
    booking_url = BASE_URL + '/'
    qr = qrcode.make(booking_url)
    img_io = BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')
