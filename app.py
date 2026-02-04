from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask import send_from_directory
import os, hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = "medseal_super_secret_key"  # Required for sessions

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------
# ROUTE: LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["email"] = request.form["email"]
        session["phone"] = request.form["phone"]
        return redirect(url_for("dashboard"))
    return render_template("login.html")


# -----------------------------
# ROUTE: DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect("/login")
    return render_template(
        "dashboard.html",
        email=session["email"],
        phone=session["phone"]
    )


# -----------------------------
# ROUTE: UPLOAD
# -----------------------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "email" not in session:
        return redirect("/login")

    if request.method == "POST":
        file = request.files.get("report")
        if not file:
            return jsonify({"error": "No file selected"})

        email = session["email"]
        phone = session["phone"]

        # generate hash
        file_hash = hashlib.sha256(file.read()).hexdigest()
        file.seek(0)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if os.path.exists("hashes.txt"):
            with open("hashes.txt", "r") as f:
                for line in f:
                   mail, fone,fname, h, time = line.strip().split("|")
                   if h == file_hash and fone==phone:
                       return jsonify({
                           "status": "⚠️ File already exists",
                           "uploaded_at": time})
        # store in hashes.txt
        with open("hashes.txt", "a") as f:
            f.write(f"{email}|{phone}|{file.filename}|{file_hash}|{timestamp}\n")

        # save file
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))

        return jsonify({
            "status": "✅ Report sealed successfully",
            "hash": file_hash,
            "uploaded_at": timestamp,
            "filename": file.filename
        })

    return render_template("upload.html")


# -----------------------------
# ROUTE: VIEW UPLOADED REPORTS
# -----------------------------
@app.route("/view")
def view():
    if "email" not in session:
        return redirect("/login")

    records = []
    email = session["email"]

    if os.path.exists("hashes.txt"):
        with open("hashes.txt") as f:
            for line in f:
                e, phone, fname, h, t = line.strip().split("|")
                if e == email:
                    records.append({
                        "file": fname,
                        "hash": h,
                        "time": t
                    })

    return render_template("view.html", records=records)
@app.route("/file/<filename>")
def serve_file(filename):
    if "email" not in session:
        return redirect("/login")

    email = session["email"]

    # SECURITY CHECK: ensure user owns this file
    allowed = False
    if os.path.exists("hashes.txt"):
        with open("hashes.txt") as f:
            for line in f:
                e, phone, fname, h, t = line.strip().split("|")
                if e == email and fname == filename:
                    allowed = True
                    break

    if not allowed:
        return "Unauthorized access", 403

    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)

# -----------------------------
# ROUTE: LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
