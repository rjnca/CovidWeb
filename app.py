import pymysql
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy as sa
from sqlalchemy import create_engine as ce
from flask_wtf import FlaskForm
from wtforms import SelectField
from mapdata import mapdata, create_hover_tool, bokehchart
import os


app = Flask(__name__)

# db = sa(app)

# print(db.session)

# flask-mysql config
# app.config["MYSQL_DATABASE_HOST"] = os.environ.get("DB_IP")
# app.config["MYSQL_DATABASE_USER"] = os.environ.get("DB_USER")
# app.config["MYSQL_DATABASE_PASSWORD"] = os.environ.get("DB_PASS")
# app.config["MYSQL_DATABASE_DB"] = os.environ.get("DB_NAME")
# app.config["MYSQL_DATABASE_CHARSET"] = "utf-8"
# app.config["MYSQL_DATABASE_CURSORCLASS"] = "DictCursor"
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")


connection = pymysql.connect(
    host=os.environ.get("DB_IP"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASS"),
    charset="utf8mb4",
    db=os.environ.get("DB_NAME"),
    cursorclass=pymysql.cursors.DictCursor,
)
cursor = connection.cursor()


sql = """select c.province, c.city, c.citycode from cityinfo c
order by c.province, c.city asc"""

cursor.execute(sql)
fetchlist = cursor.fetchall()

states = set()
for fetchdata in fetchlist:
    stateadd = fetchdata["province"]
    states.add(stateadd)

statelist = []
for n in states:
    statetuple = (n, n)
    statelist.append(statetuple)

statelist.sort()


sql = f"""select c.city, c.citycode from cityinfo c
where c.province = 'Alabama'"""

cursor.execute(sql)
fetchlist = cursor.fetchall()

cities = set()
for fetchdata in fetchlist:
    cityadd = (fetchdata["citycode"], fetchdata["city"])
    cities.add(cityadd)

citylist = list(cities)
citylist.sort()


class Form(FlaskForm):
    state = SelectField("state", choices=statelist)
    city = SelectField("city", choices=citylist)
    days_to_show = SelectField(
        "days to show",
        choices=[
            ("14", "Last 14 Days"),
            ("30", "Last 30 Days"),
            ("60", "Last 60 Days"),
        ],
    )


@app.route("/", methods=["GET", "POST"])
def hello():

    form = Form()
    if request.method == "POST":

        city = form.city.data
        days = form.days_to_show.data
        sql = f"""SELECT province, city, lat, lon, c2.confirmed, c2.deaths, c2.report_date
                FROM covid.cityinfo c
                join coviddata c2 on c.citycode = c2.citycode
                where c.citycode = {city} and c2.report_date >= DATE_ADD(Now(), INTERVAL - {days} DAY)"""
        cursor.execute(sql)
        fetchlist = cursor.fetchall()
        # mapdata(fetchlist)
        # hover = create_hover_tool()
        # plot = create_bar_chart(data, "Bugs found per day", "days", "bugs", hover)
        # script, div = components(plot)
        return render_template(
            "showdata.html", fetchlist=fetchlist, api_key=os.environ.get("MAP_KEY")
        )

    return render_template("index.html", form=form)


@app.route("/city/<state>")
def cityroute(state):
    connection = pymysql.connect(
        host=os.environ.get("DB_IP"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        charset="utf8mb4",
        db=os.environ.get("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
    )
    cursor = connection.cursor()

    sql = f"""select c.city, c.citycode from cityinfo c
    where c.province = '{state}'"""

    cursor.execute(sql)
    fetchlist = cursor.fetchall()
    cursor.close()

    cityArray = []

    for cityl in fetchlist:
        cityObj = {}
        cityObj["id"] = cityl["citycode"]
        cityObj["name"] = cityl["city"]
        cityArray.append(cityObj)
    return jsonify({"cities": cityArray})


if __name__ == "__main__":
    app.run(debug=True)
