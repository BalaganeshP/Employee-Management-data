import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import re

# MySQL connection setup
def connect_to_db():
    conn = mysql.connector.connect(
        host="localhost",  
        user="root",       
        password="Bala@2002",
        database="employee_management"  
    )
    return conn

# Function to validate login credentials
def validate_login():
    conn = connect_to_db()
    cursor = conn.cursor()

    username = username_entry.get()
    password = password_entry.get()


    # Validate from MySQL users table
    query = "SELECT * FROM users WHERE username=%s AND password=%s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    query = "INSERT INTO employees (id, name, phone, role, gender, salary) VALUES (%s, %s, %s, %s, %s, %s)"


    if user:
        messagebox.showinfo("Login Success", f"Welcome, {username}")
        open_employee_management_system()  # Open employee management window
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password")

    cursor.close()
    conn.close()

# Function to open the employee management window
def open_employee_management_system():
    login_window.destroy()  
    window.deiconify()
    update_treeview()  

def validate_phone_number(phone):
    pattern = re.compile(r'^\d{10}$')  #  exactly 10 digits
    return bool(pattern.match(phone))


def validate_name(name):
    pattern = re.compile(r'^[A-Z][a-zA-Z\s]*$')  #  Name starting with an uppercase letter
    return bool(pattern.match(name))

# Function to add a new employee
def add_employee():
    conn = connect_to_db()
    cursor = conn.cursor()
    employee_id = identry.get()
    name = nameentry.get()
    phone = phoneentry.get()
    role = rolebox.get()
    gender = genderbox.get()
    salary = salaryentry.get()

    if employee_id and name and phone and role and gender and salary:
        if not validate_phone_number(phone):
            messagebox.showwarning("INPUT ERROR","pleasse enter a valid 10-digit phone number.")
            return
        
        if not validate_name(name):
            messagebox.showwarning("INPUT ERROR","Name should start with a Capital letter")
            return

        query = "INSERT INTO employees (id, name, phone, role, gender, salary) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (employee_id, name, phone, role, gender, salary))
        conn.commit()

        # Insert into Treeview
        tree.insert("", tk.END, values=(employee_id, name, phone, role, gender, salary))

        # Clear the input fields
        clear_input_fields()

        messagebox.showinfo("Success", "Employee added successfully.")
    else:
        messagebox.showwarning("Input Error", "Please fill all fields.")

    cursor.close()
    conn.close()

# Function to update an employee's details
def update_employee():
    conn = connect_to_db()
    cursor = conn.cursor()
    selected_item = tree.selection()
    if selected_item:
        employee_id = identry.get()
        name = nameentry.get()
        phone = phoneentry.get()
        role = rolebox.get()
        gender = genderbox.get()
        salary = salaryentry.get()

        if not validate_phone_number(phone):
            messagebox.showwarning("INPUT ERROR","pleasse enter a valid 10-digit phone number.")
            return
        
        if not validate_name(name):
            messagebox.showwarning("INPUT ERROR","Name should start with a Capital letter")
            return

        # Update in MySQL database
        query = "UPDATE employees SET name=%s, phone=%s, role=%s, gender=%s, salary=%s WHERE id=%s"
        cursor.execute(query, (name, phone, role, gender, salary, employee_id))
        conn.commit()

        # Update Treeview
        tree.item(selected_item, values=(employee_id, name, phone, role, gender, salary))

        # Clear the input fields
        clear_input_fields()

        messagebox.showinfo("Success", "Employee updated successfully.")
    else:
        messagebox.showwarning("Selection Error", "Please select an employee to update.")

    cursor.close()
    conn.close()

# Function to delete an employee
def delete_employee():
    conn = connect_to_db()
    cursor = conn.cursor()

    selected_item = tree.selection()
    if selected_item:
        employee_id = tree.item(selected_item, 'values')[0]

        # Delete from MySQL database
        query = "DELETE FROM employees WHERE id=%s"
        cursor.execute(query, (employee_id,))
        conn.commit()

        # Delete from Treeview
        tree.delete(selected_item)

        messagebox.showinfo("Success", "Employee deleted successfully.")
    else:
        messagebox.showwarning("Selection Error", "Please select an employee to delete.")

    cursor.close()
    conn.close()

# Function to delete all employees
def delete_all_employees():
    conn = connect_to_db()
    cursor = conn.cursor()

    # Delete from MySQL database
    query = "DELETE FROM employees"
    cursor.execute(query)
    conn.commit()

    # Clear the Treeview
    for row in tree.get_children():
        tree.delete(row)

    messagebox.showinfo("Success", "All employees deleted successfully.")

    cursor.close()
    conn.close()

# Function to update the Treeview with data from the MySQL database
def update_treeview():
    conn = connect_to_db()
    cursor = conn.cursor()

    # Clear current Treeview data
    for row in tree.get_children():
        tree.delete(row)

    # Fetch data from MySQL database
    query = "SELECT * FROM employees"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Insert data into Treeview
    for row in rows:
        tree.insert("", tk.END, values=row)

    cursor.close()
    conn.close()

# Function to clear input fields
def clear_input_fields():
    identry.delete(0, tk.END)
    nameentry.delete(0, tk.END)
    phoneentry.delete(0, tk.END)
    rolebox.set('Select Role')
    genderbox.set('Select Gender')
    salaryentry.delete(0, tk.END)

# Function to search employee by selected criteria
def search_employee():
    search_term = searchentry.get().lower()
    search_by = searchbox.get()
    conn = connect_to_db()
    cursor = conn.cursor()


    if search_by == 'Id':
        query = "SELECT * FROM employees WHERE id LIKE %s"
    elif search_by == 'Name':
        query = "SELECT * FROM employees WHERE LOWER(name) LIKE %s"
    elif search_by == 'Phone Number':
        query = "SELECT * FROM employees WHERE phone LIKE %s"
    elif search_by == 'Role':
        query = "SELECT * FROM employees WHERE LOWER(role) LIKE %s"
    elif search_by == 'Gender':
        query = "SELECT * FROM employees WHERE LOWER(gender) LIKE %s"
    elif search_by == 'Salary':
        query = "SELECT * FROM employees WHERE salary LIKE %s"

    cursor.execute(query, (f"%{search_term}%",))
    rows = cursor.fetchall()

    # Clear the treeview
    for row in tree.get_children():
        tree.delete(row)
    for row in rows:
        tree.insert("", tk.END, values=row)

    cursor.close()
    conn.close()

# Function to load selected employee data into input fields
def load_employee_data(event):
    selected_item = tree.selection()
    if selected_item:
        values = tree.item(selected_item, 'values')
        identry.delete(0, tk.END)
        identry.insert(0, values[0])
        nameentry.delete(0, tk.END)
        nameentry.insert(0, values[1])
        phoneentry.delete(0, tk.END)
        phoneentry.insert(0, values[2])
        rolebox.set(values[3])
        genderbox.set(values[4])
        salaryentry.delete(0, tk.END)
        salaryentry.insert(0, values[5])


window = tk.Tk()
window.geometry('1400x600')  
window.title("Employee Management System")
window.withdraw() 

# Login Window
login_window = tk.Toplevel(window)
login_window.geometry('400x300')
login_window.title("Login")

# Labels and Entry boxes for login
login_label = tk.Label(login_window, text="Login", font=("Arial", 18, "bold"))
login_label.pack(pady=20)

user_label = tk.Label(login_window, text="Username", font=("Arial", 12))
user_label.pack(pady=5)
username_entry = tk.Entry(login_window, font=("Arial", 12), width=25)
username_entry.pack(pady=5)

pass_label = tk.Label(login_window, text="Password", font=("Arial", 12))
pass_label.pack(pady=5)
password_entry = tk.Entry(login_window, font=("Arial", 12), show="*", width=25)
password_entry.pack(pady=5)

# Login button
login_button = tk.Button(login_window, text="Login", font=("Arial", 12), bg="green", fg="white", command=validate_login)
login_button.pack(pady=20)

# LEFT Frame for employee information input
paned_window = tk.PanedWindow(window, orient=tk.HORIZONTAL, bg='pink')
paned_window.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

LEFTframe = tk.Frame(paned_window, bg='pink')
paned_window.add(LEFTframe, minsize=300)

left_title = tk.Label(LEFTframe, text="Employee Information", font=("Arial", 18, "bold"), bg="pink", fg="#343a40")
left_title.grid(row=0, column=0, columnspan=2, pady=10, sticky="nsew")


idlabel = tk.Label(LEFTframe, text='Id', font=('Arial', 14, 'bold'), bg='pink')
idlabel.grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)
identry = tk.Entry(LEFTframe, font=('Arial', 13), width=30)
identry.grid(row=1, column=1, padx=20, pady=10, sticky=tk.W)

namelabel = tk.Label(LEFTframe, text='Name', font=('Arial', 14, 'bold'), bg='pink')
namelabel.grid(row=2, column=0, padx=20, pady=10, sticky=tk.W)
nameentry = tk.Entry(LEFTframe, font=('Arial', 13), width=30)
nameentry.grid(row=2, column=1, padx=20, pady=10, sticky=tk.W)

phonelabel = tk.Label(LEFTframe, text='Phone Number', font=('Arial', 14, 'bold'), bg='pink')
phonelabel.grid(row=3, column=0, padx=20, pady=10, sticky=tk.W)
phoneentry = tk.Entry(LEFTframe, font=('Arial', 13), width=30)
phoneentry.grid(row=3, column=1, padx=20, pady=10, sticky=tk.W)

rolelabel = tk.Label(LEFTframe, text='Role', font=('Arial', 14, 'bold'), bg='pink')
rolelabel.grid(row=4, column=0, padx=20, pady=10, sticky=tk.W)
rolebox = ttk.Combobox(LEFTframe, font=('Arial', 13), state='readonly', width=28)
rolebox['values'] = ['Data Analyst','Data Scientist','Developer','Designer','IT Consultant','Manager','Network Engineer','Tester', 'Technical Writer',  'UX/UI Designer', 'Web Developer']
rolebox.set('Select Role')
rolebox.grid(row=4, column=1, padx=20, pady=10, sticky=tk.W)

genderlabel = tk.Label(LEFTframe, text='Gender', font=('Arial', 14, 'bold'), bg='pink')
genderlabel.grid(row=5, column=0, padx=20, pady=10, sticky=tk.W)
genderbox = ttk.Combobox(LEFTframe, font=('Arial', 13), state='readonly', width=28)
genderbox['values'] = ['Male', 'Female', 'Other']
genderbox.set('Select Gender')
genderbox.grid(row=5, column=1, padx=20, pady=10, sticky=tk.W)

salarylabel = tk.Label(LEFTframe, text='Salary', font=('Arial', 14, 'bold'), bg='pink')
salarylabel.grid(row=6, column=0, padx=20, pady=10, sticky=tk.W)
salaryentry = tk.Entry(LEFTframe, font=('Arial', 13), width=30)
salaryentry.grid(row=6, column=1, padx=20, pady=10, sticky=tk.W)

# Add, Update, Delete, and Clear Buttons
addbutton = tk.Button(LEFTframe, text='Add Employee', bg='Green', fg='white', font=('Arial', 13, 'bold'), command=add_employee)
addbutton.grid(row=7, column=0, padx=20, pady=10, sticky=tk.W)

updatebutton = tk.Button(LEFTframe, text='Update Employee', bg='Blue', fg='white', font=('Arial', 13, 'bold'), command=update_employee)
updatebutton.grid(row=7, column=1, padx=20, pady=10, sticky=tk.W)

deletebutton = tk.Button(LEFTframe, text='Delete Employee', bg='Red', fg='white', font=('Arial', 13, 'bold'), command=delete_employee)
deletebutton.grid(row=8, column=0, padx=20, pady=10, sticky=tk.W)

deleteallbutton = tk.Button(LEFTframe, text='Delete All', bg='Red', fg='white', font=('Arial', 13, 'bold'), command=delete_all_employees)
deleteallbutton.grid(row=8, column=1, padx=20, pady=10, sticky=tk.W)

clearbutton = tk.Button(LEFTframe, text='Clear Fields', bg='Grey', fg='white', font=('Arial', 13, 'bold'), command=clear_input_fields)
clearbutton.grid(row=9, column=0, columnspan=2, padx=20, pady=10, sticky=tk.W)

# RIGHT Frame for Treeview and search
RIGHTframe = tk.Frame(paned_window, bg="pink")
paned_window.add(RIGHTframe, minsize=800)

# Title for RIGHT Frame
right_title = tk.Label(RIGHTframe, text="Employee Records", font=("Arial", 18, "bold"), bg="pink", fg="#343a40")
right_title.grid(row=0, column=0, columnspan=2, pady=10, sticky="nsew")

# Search bar
searchbox = ttk.Combobox(RIGHTframe, values=['Id', 'Name', 'Phone Number', 'Role', 'Gender', 'Salary'], font=('Arial', 13), state='readonly')
searchbox.set('Search By')
searchbox.grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)

searchentry = tk.Entry(RIGHTframe, font=('Arial', 13), width=30)
searchentry.grid(row=1, column=1, padx=20, pady=10, sticky=tk.W)

searchbutton = tk.Button(RIGHTframe, text='Search', bg='Green', fg='white', font=('Arial', 13, 'bold'), command=search_employee)
searchbutton.grid(row=1, column=2, padx=20, pady=10, sticky=tk.W)

showallbutton = tk.Button(RIGHTframe, text='Show All', bg="Green", fg='white', font=('Arial', 13, 'bold'), command=update_treeview)
showallbutton.grid(row=1, column=3, padx=20, pady=10, sticky=tk.W)

# Treeview for Employee Data
tree = ttk.Treeview(RIGHTframe, height=13)
tree.grid(row=2, column=0, columnspan=4, padx=20, pady=20)
tree['columns'] = ('Id', 'Name', 'Phone Number', 'Role', 'Gender', 'Salary')
tree.heading('Id', text='Id')
tree.heading('Name', text='Name')
tree.heading('Phone Number', text='Phone Number')
tree.heading('Role', text='Role')
tree.heading('Gender', text='Gender')
tree.heading('Salary', text='Salary')
tree.config(show='headings')

# Set column widths
tree.column('Id', width=110)
tree.column('Name', width=110)
tree.column('Phone Number', width=110)
tree.column('Role', width=150)
tree.column('Gender', width=110)
tree.column('Salary', width=110)
# Load employee data when item is clicked
tree.bind("<ButtonRelease-1>", load_employee_data)
# Close the application if login window is closed
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.quit()

login_window.protocol("WM_DELETE_WINDOW", on_closing)

# Run the Tkinter loop
window.mainloop()