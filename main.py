import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from plyer import notification

# สร้าง scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# ฟังก์ชันเพิ่มงาน
def add_task():
    task = entry_list.get()
    date = reminder_entry_date.get()
    time = reminder_entry_time.get()
    print(date, time)
    
    if date == "" and time == "":
        if task:
            conn = sqlite3.connect("todo.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (task,reminder_time, status) VALUES (?, ?, ?)", (task, "-", "pending"))
            conn.commit()
            conn.close()
            entry_list.delete(0, tk.END)
            # reminder_entry.delete(0, tk.END)
            load_tasks()

            # ตั้งค่าแจ้งเตือน
            # scheduler.add_job(set_reminder, 'date', run_date=reminder_dt, args=[task])
        else:
            messagebox.showwarning("คำเตือน", "กรุณาป้อนงาน")
    else:
        # messagebox.showwarning("คำเตือน", "กรุณากรอกวันที่และเวลา")
        try:
            reminder_time = f"{date} {time}"
            reminder_dt = datetime.strptime(reminder_time, "%d-%m-%Y %H:%M")
            print("Reminder datetime:", reminder_dt)
        except ValueError:
            messagebox.showwarning("คำเตือน", "กรุณากรอกวันที่และเวลา YYYY-MM-DD HH:MM")
            return
        
        if task:
            conn = sqlite3.connect("todo.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (task, reminder_time, status) VALUES (?, ?, ?)", (task, reminder_time, "pending"))
            conn.commit()
            conn.close()
            entry_list.delete(0, tk.END)
            reminder_entry_date.delete(0, tk.END)
            reminder_entry_time.delete(0, tk.END)
            load_tasks()

            # ตั้งค่าแจ้งเตือน
            scheduler.add_job(set_reminder, 'date', run_date=reminder_dt, args=[task])
        else:
            messagebox.showwarning("คำเตือน", "กรุณาป้อนงาน")




# ฟังก์ชันโหลดงาน
def load_tasks():
    todo_listbox.delete(0, tk.END)
    done_listbox.delete(0, tk.END)

    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()

    for task in tasks:
        text = f"{task[0]}. {task[1]} ({task[2]})"
        if task[3] == "done":
            done_listbox.insert(tk.END, text)
        else:
            todo_listbox.insert(tk.END, text)

# ฟังก์ชันทำเครื่องหมายว่า "เสร็จแล้ว"
def mark_as_done():
    selected_task = todo_listbox.curselection()
    if selected_task:
        task_text = todo_listbox.get(selected_task)
        task_id = task_text.split(".")[0]

        conn = sqlite3.connect("todo.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = 'done' WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

        load_tasks()
    else:
        messagebox.showwarning("คำเตือน", "กรุณาเลือกงานที่ต้องการทำเสร็จ")

# ฟังก์ชันลบงาน
def delete_task():
    selected_task = None
    task_listbox = None

    # Check for selected task in done_listbox
    if done_listbox.curselection():
        selected_task = done_listbox.curselection()
        task_listbox = done_listbox
    # Check for selected task in todo_listbox
    elif todo_listbox.curselection():
        selected_task = todo_listbox.curselection()
        task_listbox = todo_listbox
    print("selected_task= ", selected_task, task_listbox)
    
    if selected_task:
        task_text = task_listbox.get(selected_task)
        task_id = task_text.split(".")[0]

        conn = sqlite3.connect("todo.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

        load_tasks()
    else:
        messagebox.showwarning("คำเตือน", "กรุณาเลือกงานที่ต้องการลบ")

# ฟังก์ชันแจ้งเตือน
def set_reminder(task):
    notification.notify(
        title="To-Do List Reminder",
        message=f"ถึงเวลาทำงาน: {task}",
        timeout=10
    )

# สร้างฐานข้อมูล (ถ้ายังไม่มี)
conn = sqlite3.connect("todo.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        reminder_time TEXT NOT NULL,
        status TEXT NOT NULL
    )
""")
conn.commit()
conn.close()
main_font = ("TH Sarabun New", 16, "bold")
sub_font = ("TH Sarabun New", 12)
button_font = ("TH Sarabun New", 14, "bold")
root = tk.Tk()
root.title("ToDo")
root.iconbitmap("icon.ico")

frame_create = tk.Frame(root)
frame_create.grid()

create_frame_info = tk.LabelFrame(frame_create, text="สร้างรายการใหม่", font=main_font, bg="#ADB2D4")
create_frame_info.grid(row=0, column=0, padx=10, pady=10)

list_label = tk.Label(create_frame_info, text="รายการ", font=sub_font).grid(row=0, column=0)
date_label = tk.Label(create_frame_info, text="วัน-เดือน-ปี", font=sub_font).grid(row=0, column=1)
time_label = tk.Label(create_frame_info, text="เวลา (ตัวอย่าง 15:30)", font=sub_font).grid(row=0, column=2)

entry_list = tk.Entry(create_frame_info, width=50, font=sub_font)
entry_list.grid(row=1, column=0, padx=5)
reminder_entry_date = tk.Entry(create_frame_info,width=20, font=sub_font)
reminder_entry_date.grid(row=1, column=1, padx=5)
reminder_entry_time = tk.Entry(create_frame_info, width=20, font=sub_font)
reminder_entry_time.grid(row=1, column=2, padx=5)

add_button = tk.Button(create_frame_info, text="เพิ่มงาน", width=10, font=button_font, bg="#8D77AB", command=add_task)
add_button.grid(row=1, column=3, padx=5, pady=5)

frame_display_list = tk.Frame(root)
frame_display_list.grid(row=1, column=0)
create_frame_display_list = tk.LabelFrame(frame_display_list, text="แสดงรายการทั้งหมด", font=main_font, bg="#FFF2C2" )
create_frame_display_list.grid(row=0, column=0)

to_do_label = tk.Label(create_frame_display_list, text="📌 ต้องทำ", font=sub_font)
to_do_label.grid(row=0, column=0)
done_label = tk.Label(create_frame_display_list, text="✔ ทำแล้ว", font=sub_font)
done_label.grid(row=0, column=1)

# Create the listboxes
todo_listbox = tk.Listbox(create_frame_display_list, width=50, height=10, font=sub_font, bg="#C7D9DD")
todo_listbox.grid(padx=10, pady=10)
done_listbox = tk.Listbox(create_frame_display_list, width=50, height=10, font=sub_font, bg="#D5E5D5")
done_listbox.grid(padx=10, pady=10)

# Place them in the grid
todo_listbox.grid(row=1, column=0)
done_listbox.grid(row=1, column=1)

frame_button = tk.Frame(root)
frame_button.grid(row=2, column=0, pady=10)  # Added padding for spacing

# LabelFrame to group the buttons
create_frame_button = tk.LabelFrame(frame_button)  # Added a title
create_frame_button.grid(row=0, column=0, padx=10, pady=5)  # Ensure it appears in the layout

# Buttons inside the LabelFrame
done_button = tk.Button(create_frame_button, text="✔ ทำแล้ว", command=mark_as_done, font=button_font, bg="#A4B465")
done_button.grid(row=0, column=0, padx=100, pady=5)

delete_button = tk.Button(create_frame_button, text="🗑 ลบงาน", command=delete_task, font=button_font, bg="#F0A04B")
delete_button.grid(row=0, column=1, padx=100, pady=5)
# โหลดงานจากฐานข้อมูล
load_tasks()

root.mainloop()
