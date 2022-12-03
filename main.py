from flask import Flask, render_template, url_for, request, redirect, flash, session
from datetime import timedelta
import requests
import base64
import json
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.permanent_session_lifetime = timedelta(days=5)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        params = {
            "username": username,
            "password": password
        }
        response = requests.post(url="https://backend.lohanalagna.com/api/login", json=params)
        if response.text == "Login Successful":
            session.permanent = True
            session["user"] = username
            return redirect(url_for("home"))
        else:
            flash("Incorrect username or password")
    else:
        if "user" in session:
            return redirect(url_for("home"))
    return render_template("login.html")


@app.route('/home')
def home():
    if "user" in session:
        return render_template("js1.html")
    else:
        return redirect(url_for("login"))


@app.route('/editUser/<id>')
def edit(id):
    response = requests.get("https://backend.lohanalagna.com/api/getAllUsers")
    data = response.json()
    current_user = None
    for user in data:
        if user['mobileNumber'] == id:
            current_user = user

    return render_template("editUser.html", user=current_user)


# Edit premium
@app.route("/update", methods=["POST"])
def patch_new_price():
    mobile_no = request.form["mobile"]
    checkbox = request.form.get("premium")
    print(mobile_no)
    print(checkbox)
    if checkbox is None:
        params = {
            "makePremium": False,
            "mobileNumber": mobile_no
        }
    else:
        params = {
            "makePremium": True,
            "mobileNumber": mobile_no
        }
    response = requests.post(url="https://backend.lohanalagna.com/api/changePremiumStatus", json=params)
    print(response.text)
    return redirect(url_for('home'))


@app.route("/delete/<mob>")
def delete_user(mob):
    params = {
        "mobileNumber": mob
    }
    response = requests.post(url="https://backend.lohanalagna.com/api/deleteUser", json=params)
    print(response.text)
    print(params)
    return redirect(url_for('home'))


@app.route("/add_advert")
def add_advert():
    response = requests.get('http://backend.lohanalagna.com/api/getAdImage')
    response.raise_for_status()
    data = response.json()
    return render_template("advertisement.html", img_scr=data['adUrl'])


@app.route("/uploadImg", methods=["POST"])
def upload_img():
    img = request.files["image"]
    if not img:
        return "No image uploaded", 400

    ENCODING = 'utf-8'
    img_to_b64 = base64.encodebytes(img.read())
    base64_string = img_to_b64.decode(ENCODING)
    params = {
        "image": base64_string
    }
    response = requests.post(url="https://backend.lohanalagna.com/api/setAdImage", json=params)
    print(response.text)
    print("image uploaded successfully")
    return redirect(url_for("home"))


@app.route("/remove_img")
def remove_img():
    response = requests.post(url="https://backend.lohanalagna.com/api/removeAdImage")
    print(response.text)
    return redirect(url_for("home"))


@app.route("/page")
def page():
    if session["data"] != None and session["data"] == 'yes':
        print("get from local storage")
        return render_template("pagination.html", users=1)
    else:  # if not request.get_json()['user']:
        print(request.get_json())
        print(session["data"])
        # if "getdata" in session:
        #     data = session["getdata"]
        #     print("getting from session")
        #     return render_template("pagination.html", users=data)
        response = requests.get("https://backend.lohanalagna.com/api/getAllUsers")
        response.raise_for_status()
        data = response.json()
        print("get-data-to session")
        session["data"] = "yes"
        return render_template("pagination.html", users=json.dumps(data))


@app.route("/p")
def new_user():
    # return render_template("newUser.html")
    a = datetime.datetime.now()
    year = a.year
    month = a.month
    day = a.day - 4
    hour = a.hour
    minute = a.minute
    second = a.second
    date = f"{year}-{month}-{day} {hour}:{minute}:{second}"
    api_url = "http://backend.lohanalagna.com/api/getNewUsers/?date=" + date
    response = requests.get(api_url)
    print(response.status_code)
    data = response.json()
    return render_template("newUser.html", users=json.dumps(data))


@app.route("/new_user")
def p():
    return render_template("js.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
