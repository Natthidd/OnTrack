import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ---------------- DATABASE ----------------
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")

# sample user for testing
cursor.execute("INSERT OR IGNORE INTO users(email,password) VALUES(?,?)",
               ("admin@gmail.com","1234"))
conn.commit()


# ---------------- LOGIN FUNCTION ----------------
def login():
    email = email_entry.get()
    password = password_entry.get()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )

    user = cursor.fetchone()

    if user:
        messagebox.showinfo("Success","Login successful")
    else:
        messagebox.showerror("Error","Invalid email or password")


# ---------------- UI ----------------
root = tk.Tk()
root.title("OnTrack Login")
root.geometry("420x620")
root.configure(bg="#F8FAFC")

# -------- Title --------
tk.Label(
    root,
    text="OnTrack",
    font=("Inter",28,"bold"),
    fg="#1E293B",
    bg="#F8FAFC"
).pack(pady=(40,5))

tk.Label(
    root,
    text="Stay on track, stay on time.",
    font=("Prompt",11),
    bg="#F8FAFC",
    fg="black"
).pack(pady=(0,30))


tk.Label(
    root,
    text="Login Here!",
    font=("Prompt",14,"bold"),
    bg="#F8FAFC"
).pack(anchor="w", padx=40)


# -------- Email --------
tk.Label(
    root,
    text="Email",
    font=("Prompt",11),
    bg="#F8FAFC"
).pack(anchor="w", padx=40, pady=(20,5))

email_frame = tk.Frame(root,bg="#F8FAFC")
email_frame.pack(fill="x", padx=40)

email_entry = ttk.Entry(email_frame)
email_entry.pack(fill="x", ipady=8)


# -------- Password --------
tk.Label(
    root,
    text="Password",
    font=("Prompt",11),
    bg="#F8FAFC"
).pack(anchor="w", padx=40, pady=(20,5))

password_frame = tk.Frame(root,bg="#F8FAFC")
password_frame.pack(fill="x", padx=40)

password_entry = ttk.Entry(password_frame, show="*")
password_entry.pack(side="left", fill="x", expand=True, ipady=8)


# show password
show = False
def toggle_password():
    global show
    show = not show
    password_entry.config(show="" if show else "*")

tk.Button(
    password_frame,
    text="👁",
    command=toggle_password,
    bg="#F8FAFC",
    bd=0
).pack(side="right")


# -------- Forgot password --------
tk.Label(
    root,
    text="Forgot password?",
    fg="#3B82F6",
    bg="#F8FAFC",
    cursor="hand2",
    font=("Prompt",10)
).pack(anchor="e", padx=40, pady=5)


# -------- Login Button --------
tk.Button(
    root,
    text="Login",
    font=("Inter",12,"bold"),
    bg="#1E293B",
    fg="white",
    activebackground="#1E293B",
    activeforeground="white",
    relief="flat",
    height=2,
    width=22,
    command=login
).pack(pady=40)


# -------- Divider --------
tk.Frame(root,height=1,bg="#D1D5DB").pack(fill="x", padx=40, pady=10)


# -------- Bottom --------
bottom = tk.Frame(root,bg="#F8FAFC")
bottom.pack()

tk.Label(
    bottom,
    text="Don't have an account?",
    bg="#F8FAFC",
    font=("Prompt",10)
).pack(side="left")

tk.Label(
    bottom,
    text=" Create account",
    fg="#3B82F6",
    bg="#F8FAFC",
    cursor="hand2",
    font=("Prompt",10)
).pack(side="left")


root.mainloop()