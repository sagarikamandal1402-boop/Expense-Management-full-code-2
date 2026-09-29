import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date
import matplotlib.pyplot as plt


conn = sqlite3.connect("expenses.db")

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    payment_method TEXT NOT NULL,
    description TEXT
)
""")

conn.commit()


def display_expenses():

    for item in expense_table.get_children():
        expense_table.delete(item)

    cursor.execute(
        "SELECT * FROM expenses ORDER BY date DESC"
    )

    records = cursor.fetchall()

    total = 0

    for record in records:

        expense_table.insert(
            "",
            tk.END,
            values=record
        )

        total += record[3]

    total_label.config(
        text=f"Total Expense: ₹{total:.2f}"
    )


def add_expense():

    expense_date = date_entry.get()
    category = category_combo.get()
    amount = amount_entry.get()
    payment = payment_combo.get()
    description = description_entry.get()

    if (
        expense_date == ""
        or category == ""
        or amount == ""
        or payment == ""
    ):
        messagebox.showwarning(
            "Input Error",
            "Please fill all required fields."
        )
        return

    try:
        amount = float(amount)

    except ValueError:
        messagebox.showerror(
            "Error",
            "Amount must be a number."
        )
        return

    if amount <= 0:
        messagebox.showerror(
            "Error",
            "Amount must be greater than zero."
        )
        return

    cursor.execute("""
    INSERT INTO expenses
    (date, category, amount, payment_method, description)
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        expense_date,
        category,
        amount,
        payment,
        description
    ))

    conn.commit()

    messagebox.showinfo(
        "Success",
        "Expense added successfully."
    )

    clear_fields()

    display_expenses()


def delete_expense():

    selected = expense_table.selection()

    if not selected:

        messagebox.showwarning(
            "Selection Error",
            "Please select an expense to delete."
        )

        return

    item = expense_table.item(selected[0])

    expense_id = item["values"][0]

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()

    messagebox.showinfo(
        "Success",
        "Expense deleted successfully."
    )

    display_expenses()


def clear_fields():

    date_entry.delete(0, tk.END)

    date_entry.insert(
        0,
        str(date.today())
    )

    category_combo.set("")

    amount_entry.delete(0, tk.END)

    payment_combo.set("UPI")

    description_entry.delete(0, tk.END)


def monthly_chart():

    cursor.execute("""
    SELECT substr(date, 1, 7), SUM(amount)
    FROM expenses
    GROUP BY substr(date, 1, 7)
    ORDER BY substr(date, 1, 7)
    """)

    data = cursor.fetchall()

    if not data:

        messagebox.showinfo(
            "No Data",
            "No expenses available."
        )

        return

    months = []
    amounts = []

    for row in data:

        months.append(row[0])
        amounts.append(row[1])

    plt.figure(figsize=(8, 5))

    plt.plot(
        months,
        amounts,
        marker="o"
    )

    plt.title(
        "Monthly UPI Expenses"
    )

    plt.xlabel(
        "Month"
    )

    plt.ylabel(
        "Amount (₹)"
    )

    plt.xticks(
        rotation=45
    )

    plt.grid(True)

    plt.tight_layout()

    plt.show()


def category_chart():

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)

    data = cursor.fetchall()

    if not data:

        messagebox.showinfo(
            "No Data",
            "No expenses available."
        )

        return

    categories = []
    amounts = []

    for row in data:

        categories.append(row[0])
        amounts.append(row[1])

    plt.figure(figsize=(7, 7))

    plt.pie(
        amounts,
        labels=categories,
        autopct="%1.1f%%"
    )

    plt.title(
        "Expenses by Category"
    )

    plt.show()


def payment_chart():

    cursor.execute("""
    SELECT payment_method, SUM(amount)
    FROM expenses
    GROUP BY payment_method
    """)

    data = cursor.fetchall()

    if not data:

        messagebox.showinfo(
            "No Data",
            "No expenses available."
        )

        return

    payment_methods = []
    amounts = []

    for row in data:

        payment_methods.append(row[0])
        amounts.append(row[1])

    plt.figure(figsize=(7, 7))

    plt.pie(
        amounts,
        labels=payment_methods,
        autopct="%1.1f%%"
    )

    plt.title(
        "Expenses by Payment Method"
    )

    plt.show()


def description_chart():

    cursor.execute("""
    SELECT description, SUM(amount)
    FROM expenses
    WHERE description != ''
    GROUP BY description
    """)

    data = cursor.fetchall()

    if not data:

        messagebox.showinfo(
            "No Data",
            "No descriptions available."
        )

        return

    descriptions = []
    amounts = []

    for row in data:

        descriptions.append(row[0])
        amounts.append(row[1])

    plt.figure(figsize=(7, 7))

    plt.pie(
        amounts,
        labels=descriptions,
        autopct="%1.1f%%"
    )

    plt.title(
        "Expenses by Description"
    )

    plt.show()


root = tk.Tk()

root.title(
    "Payment Expense Tracker"
)

root.geometry(
    "950x700"
)

root.resizable(
    False,
    False
)


title_label = tk.Label(
    root,
    text="UPI PAYMENT EXPENSE TRACKER",
    font=("Arial", 20, "bold")
)

title_label.pack(
    pady=15
)


input_frame = tk.Frame(
    root
)

input_frame.pack(
    pady=10
)


tk.Label(
    input_frame,
    text="Date:"
).grid(
    row=0,
    column=0,
    padx=10,
    pady=8
)


date_entry = tk.Entry(
    input_frame,
    width=20
)

date_entry.grid(
    row=0,
    column=1
)

date_entry.insert(
    0,
    str(date.today())
)


tk.Label(
    input_frame,
    text="Category:"
).grid(
    row=0,
    column=2,
    padx=10
)


category_combo = ttk.Combobox(
    input_frame,
    values=[
        "Food",
        "Shopping",
        "Travel",
        "Bills",
        "Entertainment",
        "Education",
        "Medical",
        "Other"
    ],
    width=18,
    state="readonly"
)

category_combo.grid(
    row=0,
    column=3
)


tk.Label(
    input_frame,
    text="Amount:"
).grid(
    row=1,
    column=0,
    padx=10,
    pady=8
)


amount_entry = tk.Entry(
    input_frame,
    width=20
)

amount_entry.grid(
    row=1,
    column=1
)


tk.Label(
    input_frame,
    text="Payment Method:"
).grid(
    row=1,
    column=2,
    padx=10
)


payment_combo = ttk.Combobox(
    input_frame,
    values=[
        "UPI",
        "Cash",
        "Card"
    ],
    width=18,
    state="readonly"
)

payment_combo.grid(
    row=1,
    column=3
)

payment_combo.set(
    "UPI"
)


tk.Label(
    input_frame,
    text="Description:"
).grid(
    row=2,
    column=0,
    padx=10,
    pady=8
)


description_entry = tk.Entry(
    input_frame,
    width=20
)

description_entry.grid(
    row=2,
    column=1
)


button_frame = tk.Frame(
    root
)

button_frame.pack(
    pady=10
)


add_button = tk.Button(
    button_frame,
    text="Add Expense",
    command=add_expense,
    width=15
)

add_button.grid(
    row=0,
    column=0,
    padx=5
)


delete_button = tk.Button(
    button_frame,
    text="Delete Selected",
    command=delete_expense,
    width=15
)

delete_button.grid(
    row=0,
    column=1,
    padx=5
)


clear_button = tk.Button(
    button_frame,
    text="Clear",
    command=clear_fields,
    width=15
)

clear_button.grid(
    row=0,
    column=2,
    padx=5
)


monthly_button = tk.Button(
    button_frame,
    text="Monthly Line",
    command=monthly_chart,
    width=15
)

monthly_button.grid(
    row=0,
    column=3,
    padx=5
)


category_button = tk.Button(
    button_frame,
    text="Category Pie",
    command=category_chart,
    width=15
)

category_button.grid(
    row=0,
    column=4,
    padx=5
)


payment_button = tk.Button(
    button_frame,
    text="Payment Pie",
    command=payment_chart,
    width=15
)

payment_button.grid(
    row=1,
    column=3,
    padx=5,
    pady=5
)


description_button = tk.Button(
    button_frame,
    text="Description Pie",
    command=description_chart,
    width=15
)

description_button.grid(
    row=1,
    column=4,
    padx=5,
    pady=5
)


table_frame = tk.Frame(
    root
)

table_frame.pack(
    pady=10
)


columns = (
    "ID",
    "Date",
    "Category",
    "Amount",
    "Payment",
    "Description"
)


expense_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=10
)


for column in columns:

    expense_table.heading(
        column,
        text=column
    )

    expense_table.column(
        column,
        width=130
    )


expense_table.pack()


total_label = tk.Label(
    root,
    text="Total Expense: ₹0.00",
    font=("Arial", 14, "bold")
)

total_label.pack(
    pady=10
)


display_expenses()


root.mainloop()


conn.close()
