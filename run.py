from flask import Flask, request, jsonify

# Pastikan Anda sudah menginstal requests jika belum: pip install requests
import requests
import json

app = Flask(__name__)

# --- Fungsi deposit_payment yang sudah ada ---
def deposit_payment(api_key, amount, payment_option):
    url = f"https://backend.saweria.co/donations/{api_key}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; 23053RN02A Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.158 Mobile Safari/537.36",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Android WebView\";v=\"138\"",
        "Content-Type": "application/json",
        "sec-ch-ua-mobile": "?1",
        "accept": "*/*",
        "origin": "https://saweria.co",
        "x-requested-with": "mark.via.gp",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://saweria.co/",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "priority": "u=1, i"
    }

    payment_type = ""
    if payment_option == '1':
        payment_type = "gcash"
    elif payment_option == '2':
        payment_type = "paymaya"
    elif payment_option == '3':
        payment_type = "shopeepay"
    else:
        return {"error": "Opsi pembayaran tidak valid."}

    payload = {
        "agree": True,
        "notUnderage": True,
        "message": "VIP",
        "amount": amount,
        "payment_type": payment_type,
        "vote": "",
        "currency": "PHP",
        "customer_info": {
            "first_name": "Forapps",
            "email": "teamforapps@gmail.com",
            "phone": ""
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()

        if data and "data" in data:
            donation_data = data["data"]
            donation_id = donation_data.get("id")
            redirect_url = donation_data.get("redirect_url")
            
            if donation_id and redirect_url:
                return {"id": donation_id, "redirect_url": redirect_url, "payment_type_used": payment_type}
            else:
                return {"error": "Tidak dapat menemukan 'id' atau 'redirect_url' dalam respons."}
        else:
            return {"error": "Format respons tidak terduga dari Saweria API.", "response": data}

    except requests.exceptions.RequestException as e:
        return {"error": f"Kesalahan jaringan atau permintaan: {e}"}
    except json.JSONDecodeError:
        return {"error": "Gagal mendekode respons JSON dari Saweria API."}
    except Exception as e:
        return {"error": f"Terjadi kesalahan tak terduga: {e}"}

# --- Endpoint /deposit ---
@app.route('/deposit', methods=['GET'])
def deposit_endpoint():
    api_key = request.args.get('apikey')
    amount = request.args.get('amount')
    payment_option = request.args.get('payment_option')

    if not api_key:
        return jsonify({"error": "Parameter 'apikey' diperlukan."}), 400
    if not amount:
        return jsonify({"error": "Parameter 'amount' diperlukan."}), 400
    if not payment_option:
        return jsonify({"error": "Parameter 'payment_option' diperlukan."}), 400

    try:
        amount = int(amount)
        if amount <= 0:
            return jsonify({"error": "Jumlah harus bilangan bulat positif."}), 400
    except ValueError:
        return jsonify({"error": "Jumlah harus berupa angka."}), 400

    result = deposit_payment(api_key, amount, payment_option)

    if "error" in result:
        status_code = 500
        if "Opsi pembayaran tidak valid." in result["error"]:
            status_code = 400
        return jsonify(result), status_code
    else:
        # Hanya mengembalikan id dan redirect_url seperti yang diminta
        return jsonify({"id": result["id"], "redirect_url": result["redirect_url"]})

# --- Endpoint / (root) untuk menampilkan cara penggunaan ---
@app.route('/', methods=['GET'])
def index():
    usage_instructions = """
    <h1>Selamat Datang di API Deposit Saweria</h1>
    <p>Gunakan endpoint <code>/deposit</code> untuk melakukan pembayaran deposit.</p>

    <h2>Cara Penggunaan Endpoint /deposit:</h2>
    <p>Lakukan permintaan <strong>GET</strong> ke URL berikut:</p>
    <pre><code>/deposit?apikey={YOUR_API_KEY}&amount={AMOUNT}&payment_option={PAYMENT_OPTION}</code></pre>

    <h3>Parameter Query:</h3>
    <ul>
        <li><code>apikey</code> (wajib): Kunci API Saweria Anda.</li>
        <li><code>amount</code> (wajib): Jumlah deposit dalam PHP (bilangan bulat).</li>
        <li><code>payment_option</code> (wajib): Pilihan metode pembayaran.
            <ul>
                <li><code>1</code>: GCASH</li>
                <li><code>2</code>: MAYA</li>
                <li><code>3</code>: ShopeePay</li>
            </ul>
        </li>
    </ul>

    <h3>Contoh Permintaan:</h3>
    <pre><code>http://127.0.0.1:5000/deposit?apikey=421fcc76-fb5b-43c6-a22d-8a707b83a143&amount=100&payment_option=1</code></pre>

    <h3>Contoh Respons Berhasil (JSON):</h3>
    <pre><code>
{
    "id": "svrcd-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "redirect_url": "https://saweria.co/payment/redirect?id=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
    </code></pre>

    <h3>Contoh Respons Error (JSON):</h3>
    <pre><code>
{
    "error": "Parameter 'apikey' diperlukan."
}
    </code></pre>
    <pre><code>
{
    "error": "Opsi pembayaran tidak valid. Gunakan '1' untuk GCASH, '2' untuk MAYA, atau '3' untuk ShopeePay."
}
    </code></pre>
    <p>Pastikan untuk mengganti <code>{YOUR_API_KEY}</code> dengan kunci API Saweria Anda yang sebenarnya.</p>
    """
    return usage_instructions

if __name__ == '__main__':
    app.run(debug=True)
