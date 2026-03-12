from flask import Flask,render_template,request,redirect,session
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key="pcstore"

def db():
    return sqlite3.connect("store.db")

# HOME
@app.route("/")
def index():

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")

    per_page = 8
    offset = (page - 1) * per_page

    con = db()
    cur = con.cursor()

    # nếu có tìm kiếm
    if search:

        cur.execute(
        "SELECT * FROM products WHERE name LIKE ?",
        ('%' + search + '%',)
        )

        products = cur.fetchall()
        total = len(products)

    # nếu không tìm kiếm
    else:

        cur.execute(
        "SELECT * FROM products LIMIT ? OFFSET ?",
        (per_page, offset)
        )

        products = cur.fetchall()

        cur.execute("SELECT COUNT(*) FROM products")
        total = cur.fetchone()[0]

    con.close()

    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "index.html",
        products=products,
        page=page,
        total_pages=total_pages
    )


# REGISTER
@app.route("/register",methods=["GET","POST"])
def register():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]
        confirm=request.form["confirm"]

        if password!=confirm:
            return "Password not match"

        con=db()
        cur=con.cursor()

        cur.execute(
        "INSERT INTO users(username,password,role) VALUES(?,?,?)",
        (username,password,"user"))

        con.commit()
        con.close()

        return redirect("/login")

    return render_template("register.html")


# LOGIN
@app.route("/login",methods=["GET","POST"])
def login():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        con=db()
        cur=con.cursor()

        cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password))

        user=cur.fetchone()

        con.close()

        if user:

            session["user_id"]=user[0]
            session["username"]=user[1]
            session["role"]=user[3]

            return redirect("/")

        else:
            return "Sai tài khoản hoặc mật khẩu"

    return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ADD TO CART
@app.route("/add_to_cart/<int:id>")
def add_cart(id):

    con = db()
    cur = con.cursor()

    cur.execute("SELECT stock FROM products WHERE id=?", (id,))
    stock = cur.fetchone()[0]

    con.close()

    if "cart" not in session:
        session["cart"] = {}

    cart = session["cart"]

    current_qty = cart.get(str(id), 0)

    # kiểm tra tồn kho
    if current_qty >= stock:
        return redirect("/cart")

    cart[str(id)] = current_qty + 1

    session["cart"] = cart

    return redirect("/")
# INCREASE QUANTITY
@app.route("/increase/<int:id>")
def increase(id):

    if "cart" not in session:
        return redirect("/cart")

    con = db()
    cur = con.cursor()

    cur.execute("SELECT stock FROM products WHERE id=?", (id,))
    stock = cur.fetchone()[0]

    con.close()

    cart = session["cart"]
    qty = cart.get(str(id), 0)

    # nếu đạt stock thì không tăng nữa
    if qty >= stock:
        return redirect("/cart")

    cart[str(id)] = qty + 1
    session["cart"] = cart

    return redirect("/cart")


# DECREASE QUANTITY
@app.route("/decrease/<int:id>")
def decrease(id):

    if "cart" in session:

        cart=session["cart"]

        if str(id) in cart:

            cart[str(id)]-=1

            if cart[str(id)]<=0:
                del cart[str(id)]

        session["cart"]=cart

    return redirect("/cart")


# CART
@app.route("/cart")
def cart():

    if "cart" not in session:
        return render_template("cart.html",items=[],total=0)

    con=db()
    cur=con.cursor()

    items=[]
    total=0

    for pid,qty in session["cart"].items():

        cur.execute("SELECT * FROM products WHERE id=?",(pid,))
        p=cur.fetchone()

        subtotal=p[3]*qty
        total+=subtotal

        items.append((p,qty,subtotal))

    con.close()

    return render_template("cart.html",items=items,total=total)


# CHECKOUT
@app.route("/checkout",methods=["GET","POST"])
def checkout():

    if "user_id" not in session:
        return redirect("/login")

    if "cart" not in session:
        return redirect("/")

    # HIỂN THỊ TRANG CHỌN THANH TOÁN
    if request.method=="GET":
        return render_template("checkout.html")

    payment = request.form["payment"]

    con=db()
    cur=con.cursor()

    total=0

    for pid,qty in session["cart"].items():

        cur.execute("SELECT price FROM products WHERE id=?",(pid,))
        price=cur.fetchone()[0]

        total+=price*qty

    cur.execute(
    "INSERT INTO orders(user_id,total,date,payment) VALUES(?,?,?,?)",
    (session["user_id"],total,datetime.now(),payment))

    order_id=cur.lastrowid

    for pid,qty in session["cart"].items():

        cur.execute(
        "INSERT INTO order_items(order_id,product_id,quantity) VALUES(?,?,?)",
        (order_id,pid,qty))

        cur.execute(
        "UPDATE products SET stock = stock - ? WHERE id=?",
        (qty,pid))

    con.commit()
    con.close()

    session.pop("cart")

    return redirect("/invoice/"+str(order_id))


# INVOICE
@app.route("/invoice/<int:id>")
def invoice(id):

    con=db()
    cur=con.cursor()

    cur.execute("""
    SELECT p.name,p.price,oi.quantity
    FROM order_items oi
    JOIN products p ON p.id=oi.product_id
    WHERE oi.order_id=?
    """,(id,))

    items=cur.fetchall()

    total=sum(i[1]*i[2] for i in items)

    con.close()

    return render_template("invoice.html",items=items,total=total)


# ADMIN
@app.route("/admin")
def admin():

    if session.get("role")!="admin":
        return redirect("/")

    con=db()
    cur=con.cursor()

    # Lấy đơn hàng + username
    cur.execute("""
    SELECT orders.id, users.username, orders.total, orders.date
    FROM orders
    JOIN users ON users.id = orders.user_id
    """)
    orders=cur.fetchall()

    # doanh thu
    cur.execute("SELECT SUM(total) FROM orders")
    year=cur.fetchone()[0] or 0

    cur.execute("SELECT SUM(total) FROM orders WHERE date>=date('now','-30 day')")
    month=cur.fetchone()[0] or 0

    cur.execute("SELECT SUM(total) FROM orders WHERE date>=date('now','-1 day')")
    day=cur.fetchone()[0] or 0

    con.close()

    return render_template("admin.html",orders=orders,day=day,month=month,year=year)

if __name__=="__main__":
    app.run(debug=True)