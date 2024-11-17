from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
@app.route("/login")
def index():
	return render_template("index.html")

@app.route("/dashboard")
def dashboard():
	return render_template("dashboard.html")

@app.route("/dashboard/result")
def result():
	return render_template("result.html")

if __name__ == '__main__':
	app.run(debug=True)