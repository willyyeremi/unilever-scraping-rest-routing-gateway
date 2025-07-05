from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import requests


##############################
# common used variable
##############################

API_MAP = {
    "v1": "http://localhost:5011",
    "v2": "http://localhost:5012"
}

versioning_bp = Blueprint("versioning", __name__)


##############################
# routing function
##############################

@versioning_bp.route("/<path:path>", methods = ["POST", "GET", "PUT", "PATCH", "DELETE"])
@jwt_required()
def route_to_version(path):
    try:
        version = request.headers.get("X-API-Version") # ambil version api dari header X-API-Version
        if version not in API_MAP:
            return {"error": "API version not supported"}, 404
        method = request.method
        target_url = f"{API_MAP[version]}/{path}"
        headers = dict(request.headers)
        headers.pop("Host", None) # hilangkan header Host supaya nanti diganti dengan host tempat tujuan saat sampai
        resp = requests.request(
            method = method,
            url = target_url,   
            params = request.args.to_dict(),
            headers = headers, # kirim informasi client ke backend untuk autentikasi berbasis JWT (RBAC, logging)
            data = request.get_data() # data dari client yang ingin diproses
        )
        return (resp.content, resp.status_code, resp.headers.items())
    except Exception as e:
        return jsonify({"error": str(e)}), 500