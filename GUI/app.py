# app.py
import customtkinter as ctk
from tkinter import ttk  # We need this for the Treeview widget
from tkinter import messagebox
import mysql.connector
from db_config import DB_CONFIG  # Import your database configuration
import re  # For email and contact validation

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Startup Incubator Management System")
        self.geometry("1100x750") # Increased window size
        
        # --- Set default font ---
        self.default_font = ("Arial", 18)
        
        # Set theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # --- Configure ttk.Treeview style ---
        self.style = ttk.Style()
        self.style.theme_use("default")
        
        # Style for selected items
        self.style.map("Treeview", 
                       background=[("selected", "#347083")], 
                       foreground=[("selected", "white")])
        
        # Configure the font and padding for table headings
        self.style.configure("Treeview.Heading", 
                             font=("Arial", 18, "bold"), 
                             padding=5)
        
        # Configure the font, row height, and alignment for table cells
        self.style.configure("Treeview", 
                             rowheight=30,  # Increase row height
                             font=("Arial", 18), 
                             padding=5)

        # --- Create a Tabbed Interface ---
        # FIXED: Removed the problematic font argument to support older customtkinter versions
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(expand=True, fill="both", padx=10, pady=10)

        # Add tabs
        self.tab_view.add("View All Data (Read)")
        self.tab_view.add("Manage Startups (CRUD)")
        self.tab_view.add("Procedures & Functions")
        self.tab_view.add("Complex Queries & Triggers")

        # --- Populate each tab ---
        self.create_tab_1_view_data()
        self.create_tab_2_manage_startups()
        self.create_tab_3_proc_func()
        self.create_tab_4_queries_triggers()

    # --- Database Connection Helper ---
    def get_db_connection(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
            return None

    # --- Generic Function to Display Query Results in a Treeview ---
    def display_in_treeview(self, tree, query, params=()):
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)
        
        # Clear existing columns (FIXED)
        tree["displaycolumns"] = ()
        tree["columns"] = ()

        conn = self.get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            if not rows:
                messagebox.showinfo("Query Info", "Query executed, but returned no results.")
                return

            # --- Define Treeview Columns ---
            column_names = [desc[0] for desc in cursor.description]
            tree["columns"] = column_names
            tree["displaycolumns"] = column_names
            
            for col in column_names:
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor="center") # Centered
            
            tree.heading("#0", text="Row")
            tree.column("#0", width=40, anchor="center")
            
            # --- Insert Data into Treeview ---
            for i, row in enumerate(rows):
                tree.insert("", "end", text=str(i+1), values=row)

        except mysql.connector.Error as err:
            messagebox.showerror("Query Error", f"Error executing query: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    # ===================================================================
    # TAB 1: VIEW ALL DATA (Read Operation)
    # ===================================================================
    def create_tab_1_view_data(self):
        tab = self.tab_view.tab("View All Data (Read)")
        
        # Frame for buttons
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill="x", padx=10, pady=10)

        # Treeview to display data
        self.view_tree = ttk.Treeview(tab, show="headings")
        self.view_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Buttons to load data for each table ---
        tables = ["startups", "founders", "mentors", "investors", "funding", "startup_mentors", "audit_log"]
        for i, table in enumerate(tables):
            btn = ctk.CTkButton(button_frame, text=f"Load {table}", 
                                font=self.default_font,
                                command=lambda t=table: self.display_in_treeview(self.view_tree, f"SELECT * FROM {t}"))
            btn.grid(row=0, column=i, padx=5, pady=5)

    # ===================================================================
    # TAB 2: MANAGE STARTUPS (Create, Update, Delete Operations)
    # ===================================================================
    def create_tab_2_manage_startups(self):
        tab = self.tab_view.tab("Manage Startups (CRUD)")
        
        # --- Form for C-U-D ---
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        self.startup_id_var = ctk.StringVar() # To hold the ID of the selected startup

        # Name
        ctk.CTkLabel(form_frame, text="Name:", font=self.default_font).grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ctk.CTkEntry(form_frame, width=200, font=self.default_font)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Domain
        ctk.CTkLabel(form_frame, text="Domain:", font=self.default_font).grid(row=0, column=2, padx=5, pady=5)
        self.domain_entry = ctk.CTkEntry(form_frame, width=200, font=self.default_font)
        self.domain_entry.grid(row=0, column=3, padx=5, pady=5)

        # Stage
        ctk.CTkLabel(form_frame, text="Stage:", font=self.default_font).grid(row=1, column=0, padx=5, pady=5)
        self.stage_entry = ctk.CTkEntry(form_frame, width=200, font=self.default_font)
        self.stage_entry.grid(row=1, column=1, padx=5, pady=5)

        # --- CRUD Buttons ---
        self.add_btn = ctk.CTkButton(form_frame, text="Add New Startup (Create)", font=self.default_font, command=self.add_startup)
        self.add_btn.grid(row=2, column=0, padx=5, pady=10)

        self.update_btn = ctk.CTkButton(form_frame, text="Update Selected (Update)", font=self.default_font, command=self.update_startup)
        self.update_btn.grid(row=2, column=1, padx=5, pady=10)

        self.delete_btn = ctk.CTkButton(form_frame, text="Delete Selected (Delete)", font=self.default_font, fg_color="red", command=self.delete_startup)
        self.delete_btn.grid(row=2, column=2, padx=5, pady=10)
        
        self.clear_btn = ctk.CTkButton(form_frame, text="Clear Form", font=self.default_font, fg_color="grey", command=self.clear_startup_form)
        self.clear_btn.grid(row=2, column=3, padx=5, pady=10)

        # --- Treeview to show startups and select them ---
        self.startup_tree = ttk.Treeview(tab, show="headings")
        self.startup_tree.pack(expand=True, fill="both", padx=10, pady=10)
        self.startup_tree.bind("<<TreeviewSelect>>", self.on_startup_select)
        
        self.refresh_startup_tree() # Load data on start

    def refresh_startup_tree(self):
        self.display_in_treeview(self.startup_tree, "SELECT * FROM startups")

    def on_startup_select(self, event):
        try:
            selected_item = self.startup_tree.selection()[0]
            values = self.startup_tree.item(selected_item, "values")
            
            # Populate form with selected data
            self.startup_id_var.set(values[0])
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, values[1])
            self.domain_entry.delete(0, "end")
            self.domain_entry.insert(0, values[2])
            self.stage_entry.delete(0, "end")
            self.stage_entry.insert(0, values[3])
        except IndexError:
            pass # No item selected

    def clear_startup_form(self):
        self.startup_id_var.set("")
        self.name_entry.delete(0, "end")
        self.domain_entry.delete(0, "end")
        self.stage_entry.delete(0, "end")
        self.startup_tree.selection_remove(self.startup_tree.selection())

    def add_startup(self):
        query = "INSERT INTO startups (name, domain, stage, registration_date) VALUES (%s, %s, %s, CURDATE())"
        params = (self.name_entry.get(), self.domain_entry.get(), self.stage_entry.get())
        
        conn = self.get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Success", "New startup added successfully.")
            self.refresh_startup_tree()
            self.clear_startup_form()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to add startup: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def update_startup(self):
        startup_id = self.startup_id_var.get()
        if not startup_id:
            messagebox.showerror("Error", "Please select a startup from the list to update.")
            return

        query = "UPDATE startups SET name = %s, domain = %s, stage = %s WHERE startup_id = %s"
        params = (self.name_entry.get(), self.domain_entry.get(), self.stage_entry.get(), startup_id)
        
        conn = self.get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Success", "Startup updated successfully.")
            self.refresh_startup_tree()
            self.clear_startup_form()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to update startup: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def delete_startup(self):
        startup_id = self.startup_id_var.get()
        if not startup_id:
            messagebox.showerror("Error", "Please select a startup from the list to delete.")
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this startup? This may also delete related founders and funding (ON DELETE CASCADE)."):
            return

        query = "DELETE FROM startups WHERE startup_id = %s"
        params = (startup_id,)
        
        conn = self.get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Success", "Startup deleted successfully.")
            self.refresh_startup_tree()
            self.clear_startup_form()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to delete startup: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    # ===================================================================
    # TAB 3: PROCEDURES & FUNCTIONS (Review 3 Requirement)
    # ===================================================================
    def create_tab_3_proc_func(self):
        tab = self.tab_view.tab("Procedures & Functions")
        
        # --- Function 1 Demo: fn_GetTotalFunding ---
        func_frame = ctk.CTkFrame(tab)
        func_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(func_frame, text="Run Function: Get Total Funding", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, pady=5)
        
        ctk.CTkLabel(func_frame, text="Enter Startup ID:", font=self.default_font).grid(row=1, column=0, padx=5, pady=5)
        self.func_startup_id_entry = ctk.CTkEntry(func_frame, width=100, font=self.default_font)
        self.func_startup_id_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.func_btn = ctk.CTkButton(func_frame, text="Calculate", font=self.default_font, command=self.call_get_funding_function)
        self.func_btn.grid(row=1, column=2, padx=5, pady=5)
        
        self.func_result_label = ctk.CTkLabel(func_frame, text="Result: ", font=ctk.CTkFont(size=14))
        self.func_result_label.grid(row=2, column=0, columnspan=3, pady=5)

        # --- Function 2 Demo: fn_GetMentorCount ---
        func2_frame = ctk.CTkFrame(tab)
        func2_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(func2_frame, text="Run Function: Get Mentor Count", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, pady=5)
        
        ctk.CTkLabel(func2_frame, text="Enter Startup ID:", font=self.default_font).grid(row=1, column=0, padx=5, pady=5)
        self.func2_startup_id_entry = ctk.CTkEntry(func2_frame, width=100, font=self.default_font)
        self.func2_startup_id_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.func2_btn = ctk.CTkButton(func2_frame, text="Calculate", font=self.default_font, command=self.call_get_mentor_count_function)
        self.func2_btn.grid(row=1, column=2, padx=5, pady=5)
        
        self.func2_result_label = ctk.CTkLabel(func2_frame, text="Result: ", font=ctk.CTkFont(size=14))
        self.func2_result_label.grid(row=2, column=0, columnspan=3, pady=5)


        # --- Procedure 1 Demo: sp_AddNewStartupAndFounder ---
        proc_frame = ctk.CTkFrame(tab)
        proc_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(proc_frame, text="Run Procedure: Add New Startup & Founder", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, pady=10)
        
        # Inputs
        ctk.CTkLabel(proc_frame, text="Startup Name:", font=self.default_font).grid(row=1, column=0, padx=5, pady=5)
        self.proc_s_name = ctk.CTkEntry(proc_frame, font=self.default_font)
        self.proc_s_name.grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(proc_frame, text="Startup Domain:", font=self.default_font).grid(row=1, column=2, padx=5, pady=5)
        self.proc_s_domain = ctk.CTkEntry(proc_frame, font=self.default_font)
        self.proc_s_domain.grid(row=1, column=3, padx=5, pady=5)

        ctk.CTkLabel(proc_frame, text="Startup Stage:", font=self.default_font).grid(row=2, column=0, padx=5, pady=5)
        self.proc_s_stage = ctk.CTkEntry(proc_frame, font=self.default_font)
        self.proc_s_stage.grid(row=2, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(proc_frame, text="Founder Name:", font=self.default_font).grid(row=3, column=0, padx=5, pady=5)
        self.proc_f_name = ctk.CTkEntry(proc_frame, font=self.default_font)
        self.proc_f_name.grid(row=3, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(proc_frame, text="Founder Email:", font=self.default_font).grid(row=3, column=2, padx=5, pady=5)
        self.proc_f_email = ctk.CTkEntry(proc_frame, font=self.default_font)
        self.proc_f_email.grid(row=3, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(proc_frame, text="Founder Contact:", font=self.default_font).grid(row=4, column=0, padx=5, pady=5)
        self.proc_f_contact = ctk.CTkEntry(proc_frame, font=self.default_font)
        self.proc_f_contact.grid(row=4, column=1, padx=5, pady=5)

        # Button
        self.proc_btn = ctk.CTkButton(proc_frame, text="Run Procedure", font=self.default_font, command=self.call_add_startup_procedure)
        self.proc_btn.grid(row=5, column=0, columnspan=4, pady=10)

        # --- Procedure 2 Demo: sp_AssignMentorToStartup ---
        proc2_frame = ctk.CTkFrame(tab)
        proc2_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(proc2_frame, text="Run Procedure: Assign Mentor to Startup", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, pady=5)
        
        ctk.CTkLabel(proc2_frame, text="Enter Startup ID:", font=self.default_font).grid(row=1, column=0, padx=5, pady=5)
        self.proc2_startup_id = ctk.CTkEntry(proc2_frame, width=100, font=self.default_font)
        self.proc2_startup_id.grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(proc2_frame, text="Enter Mentor ID:", font=self.default_font).grid(row=1, column=2, padx=5, pady=5)
        self.proc2_mentor_id = ctk.CTkEntry(proc2_frame, width=100, font=self.default_font)
        self.proc2_mentor_id.grid(row=1, column=3, padx=5, pady=5)

        self.proc2_btn = ctk.CTkButton(proc2_frame, text="Run Procedure", font=self.default_font, command=self.call_assign_mentor_procedure)
        self.proc2_btn.grid(row=2, column=0, columnspan=4, pady=10)


    def call_get_funding_function(self):
        startup_id = self.func_startup_id_entry.get()
        if not startup_id:
            self.func_result_label.configure(text="Result: Please enter a Startup ID.")
            return
        
        conn = self.get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = "SELECT fn_GetTotalFunding(%s)"
            cursor.execute(query, (startup_id,))
            result = cursor.fetchone()
            
            if result:
                self.func_result_label.configure(text=f"Result: Total Funding = ₹{result[0]:,.2f}")
            else:
                self.func_result_label.configure(text="Result: Error or no data.")
                
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to call function: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def call_get_mentor_count_function(self):
        startup_id = self.func2_startup_id_entry.get()
        if not startup_id:
            self.func2_result_label.configure(text="Result: Please enter a Startup ID.")
            return
        
        conn = self.get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            query = "SELECT fn_GetMentorCount(%s)"
            cursor.execute(query, (startup_id,))
            result = cursor.fetchone()
            
            if result:
                self.func2_result_label.configure(text=f"Result: This startup has {result[0]} mentors.")
            else:
                self.func2_result_label.configure(text="Result: Error or no data.")
                
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to call function: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def call_add_startup_procedure(self):
        # Get all parameters
        s_name = self.proc_s_name.get()
        s_domain = self.proc_s_domain.get()
        s_stage = self.proc_s_stage.get()
        f_name = self.proc_f_name.get()
        f_email = self.proc_f_email.get()
        f_contact = self.proc_f_contact.get()

        params = (s_name, s_domain, s_stage, f_name, f_email, f_contact)

        # --- VALIDATION ---
        if not all(params):
            messagebox.showerror("Error", "Please fill in all fields for the procedure.")
            return

        if not f_email.endswith('@gmail.com'):
            messagebox.showerror("Validation Error", "Invalid email. Email must end with '@gmail.com'.")
            return

        if not (f_contact.isdigit() and len(f_contact) == 10):
            messagebox.showerror("Validation Error", "Invalid contact. Must be exactly 10 digits.")
            return
        # --- END VALIDATION ---

        conn = self.get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.callproc('sp_AddNewStartupAndFounder', params)
            conn.commit()
            
            messagebox.showinfo("Success", "Procedure 'sp_AddNewStartupAndFounder' executed successfully. Startup and founder added.")
            self.refresh_startup_tree()
            
            # Clear procedure form
            self.proc_s_name.delete(0, "end")
            self.proc_s_domain.delete(0, "end")
            self.proc_s_stage.delete(0, "end")
            self.proc_f_name.delete(0, "end")
            self.proc_f_email.delete(0, "end")
            self.proc_f_contact.delete(0, "end")

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to call procedure: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def call_assign_mentor_procedure(self):
        startup_id = self.proc2_startup_id.get()
        mentor_id = self.proc2_mentor_id.get()

        if not startup_id or not mentor_id:
            messagebox.showerror("Error", "Please enter both a Startup ID and a Mentor ID.")
            return

        conn = self.get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.callproc('sp_AssignMentorToStartup', (startup_id, mentor_id))
            
            # Get the 'Status' message returned by the procedure
            for result in cursor.stored_results():
                status_message = result.fetchone()[0]
            
            messagebox.showinfo("Procedure Status", status_message)

            # Clear inputs
            self.proc2_startup_id.delete(0, "end")
            self.proc2_mentor_id.delete(0, "end")
            
            # Refresh the table in Tab 1 (in case the user is viewing it)
            if self.view_tree:
                 self.display_in_treeview(self.view_tree, "SELECT * FROM startup_mentors")


        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to call procedure: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    # ===================================================================
    # TAB 4: COMPLEX QUERIES & TRIGGERS (Review 3/4 Requirement)
    # ===================================================================
    def create_tab_4_queries_triggers(self):
        tab = self.tab_view.tab("Complex Queries & Triggers")

        # --- Trigger 1 Demo: trg_AuditFundingChanges ---
        trigger_frame = ctk.CTkFrame(tab)
        trigger_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(trigger_frame, text="Fire Trigger 1: Update Funding Amount", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, pady=5)
        
        ctk.CTkLabel(trigger_frame, text="Funding ID:", font=self.default_font).grid(row=1, column=0, padx=5, pady=5)
        self.trigger_funding_id = ctk.CTkEntry(trigger_frame, width=100, font=self.default_font)
        self.trigger_funding_id.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(trigger_frame, text="New Amount:", font=self.default_font).grid(row=1, column=2, padx=5, pady=5)
        self.trigger_new_amount = ctk.CTkEntry(trigger_frame, width=150, font=self.default_font)
        self.trigger_new_amount.grid(row=1, column=3, padx=5, pady=5)
        
        self.trigger_btn = ctk.CTkButton(trigger_frame, text="Run Update (Fires Trigger 1)", font=self.default_font, command=self.fire_funding_update_trigger)
        self.trigger_btn.grid(row=2, column=0, columnspan=4, pady=10)
        
        
        # --- Trigger 2 Demo: trg_LogNewFounder ---
        trigger2_frame = ctk.CTkFrame(tab)
        trigger2_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(trigger2_frame, text="Fire Trigger 2: Add New Founder", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, pady=5)
        
        ctk.CTkLabel(trigger2_frame, text="Name:", font=self.default_font).grid(row=1, column=0, padx=5, pady=5)
        self.trg2_f_name = ctk.CTkEntry(trigger2_frame, font=self.default_font)
        self.trg2_f_name.grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(trigger2_frame, text="Email:", font=self.default_font).grid(row=1, column=2, padx=5, pady=5)
        self.trg2_f_email = ctk.CTkEntry(trigger2_frame, font=self.default_font)
        self.trg2_f_email.grid(row=1, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(trigger2_frame, text="Contact:", font=self.default_font).grid(row=2, column=0, padx=5, pady=5)
        self.trg2_f_contact = ctk.CTkEntry(trigger2_frame, font=self.default_font)
        self.trg2_f_contact.grid(row=2, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(trigger2_frame, text="Startup ID:", font=self.default_font).grid(row=2, column=2, padx=5, pady=5)
        self.trg2_s_id = ctk.CTkEntry(trigger2_frame, font=self.default_font)
        self.trg2_s_id.grid(row=2, column=3, padx=5, pady=5)

        self.trigger2_btn = ctk.CTkButton(trigger2_frame, text="Run Insert (Fires Trigger 2)", font=self.default_font, command=self.fire_add_founder_trigger)
        self.trigger2_btn.grid(row=3, column=0, columnspan=4, pady=10)

        # --- ADD NEW MENTOR ---
        mentor_frame = ctk.CTkFrame(tab)
        mentor_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(mentor_frame, text="Add New Mentor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, pady=5)
        
        ctk.CTkLabel(mentor_frame, text="Name:", font=self.default_font).grid(row=1, column=0, padx=5, pady=5)
        self.mentor_name_entry = ctk.CTkEntry(mentor_frame, font=self.default_font)
        self.mentor_name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(mentor_frame, text="Expertise Area:", font=self.default_font).grid(row=1, column=2, padx=5, pady=5)
        self.mentor_expertise_entry = ctk.CTkEntry(mentor_frame, font=self.default_font)
        self.mentor_expertise_entry.grid(row=1, column=3, padx=5, pady=5)
        
        self.add_mentor_btn = ctk.CTkButton(mentor_frame, text="Add Mentor", font=self.default_font, command=self.add_new_mentor)
        self.add_mentor_btn.grid(row=2, column=0, columnspan=4, pady=10)


        # --- Audit Log Viewer (For both triggers) ---
        ctk.CTkLabel(tab, text="Audit Log (Shows Trigger Results)", font=self.default_font).pack(pady=(10, 0))
        self.audit_log_btn = ctk.CTkButton(tab, text="Refresh Audit Log", font=self.default_font, command=self.refresh_audit_log_tree)
        self.audit_log_btn.pack(pady=5)
        
        self.audit_log_tree = ttk.Treeview(tab, show="headings", height=5)
        self.audit_log_tree.pack(expand=True, fill="x", padx=10, pady=(0, 10))
        self.refresh_audit_log_tree() # Load on start

        # --- Complex Queries Demo ---
        query_frame = ctk.CTkFrame(tab)
        query_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(query_frame, text="Run Complex Queries (Join, Aggregate, Nested)", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        btn_frame = ctk.CTkFrame(query_frame)
        btn_frame.pack(fill="x", pady=5)

        self.join_btn = ctk.CTkButton(btn_frame, text="JOIN Query", font=self.default_font, command=self.run_join_query)
        self.join_btn.pack(side="left", expand=True, padx=5)
        
        self.agg_btn = ctk.CTkButton(btn_frame, text="AGGREGATE Query", font=self.default_font, command=self.run_aggregate_query)
        self.agg_btn.pack(side="left", expand=True, padx=5)

        self.nested_btn = ctk.CTkButton(btn_frame, text="NESTED Query", font=self.default_font, command=self.run_nested_query)
        self.nested_btn.pack(side="left", expand=True, padx=5)

        self.query_result_tree = ttk.Treeview(query_frame, show="headings")
        self.query_result_tree.pack(expand=True, fill="both", pady=5)
        
    def fire_funding_update_trigger(self):
        funding_id = self.trigger_funding_id.get()
        new_amount = self.trigger_new_amount.get()

        if not funding_id or not new_amount:
            messagebox.showerror("Error", "Please enter a Funding ID and a new Amount.")
            return

        query = "UPDATE funding SET amount = %s WHERE funding_id = %s"
        params = (new_amount, funding_id)
        
        conn = self.get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if cursor.rowcount == 0:
                 messagebox.showwarning("Warning", f"No funding record found with ID = {funding_id}. No update was made.")
            else:
                conn.commit()
                messagebox.showinfo("Success", f"Update successful. Check the 'Audit Log' table (refresh it) to see the trigger's output.")
                self.trigger_funding_id.delete(0, "end")
                self.trigger_new_amount.delete(0, "end")
                self.refresh_audit_log_tree() # Auto-refresh the log
        
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to run update: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def fire_add_founder_trigger(self):
        name = self.trg2_f_name.get()
        email = self.trg2_f_email.get()
        contact = self.trg2_f_contact.get()
        startup_id = self.trg2_s_id.get()

        # --- VALIDATION ---
        if not all((name, email, contact, startup_id)):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if not email.endswith('@gmail.com'):
            messagebox.showerror("Validation Error", "Invalid email. Email must end with '@gmail.com'.")
            return

        if not (contact.isdigit() and len(contact) == 10):
            messagebox.showerror("Validation Error", "Invalid contact. Must be exactly 10 digits.")
            return
        # --- END VALIDATION ---

        query = "INSERT INTO founders (name, email, contact, startup_id) VALUES (%s, %s, %s, %s)"
        params = (name, email, contact, startup_id)

        conn = self.get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Success", "Founder added! Refresh the 'Audit Log' to see the trigger's output.")
            
            # Clear inputs
            self.trg2_f_name.delete(0, "end")
            self.trg2_f_email.delete(0, "end")
            self.trg2_f_contact.delete(0, "end")
            self.trg2_s_id.delete(0, "end")
            
            self.refresh_audit_log_tree() # Auto-refresh the log
            self.refresh_startup_tree() # Also refresh the main startup tree

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to add founder: {err}. (Check if Startup ID exists or Email is unique)")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def add_new_mentor(self):
        name = self.mentor_name_entry.get()
        expertise = self.mentor_expertise_entry.get()

        if not name or not expertise:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        query = "INSERT INTO mentors (name, expertise_area) VALUES (%s, %s)"
        params = (name, expertise)

        conn = self.get_db_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Success", "New mentor added successfully!")
            
            # Clear inputs
            self.mentor_name_entry.delete(0, "end")
            self.mentor_expertise_entry.delete(0, "end")
            
            # Refresh mentors table in Tab 1
            if self.view_tree:
                self.display_in_treeview(self.view_tree, "SELECT * FROM mentors")

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to add mentor: {err}. (Check if Name is unique)")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()


    def refresh_audit_log_tree(self):
        self.display_in_treeview(self.audit_log_tree, "SELECT * FROM audit_log ORDER BY action_timestamp DESC")
    
    # --- Complex Query Methods ---
    def run_join_query(self):
        # JOIN: Get all startups and their assigned mentors
        query = """
        SELECT 
            s.name AS 'Startup', 
            m.name AS 'Mentor', 
            m.expertise_area AS 'Expertise'
        FROM startups s
        JOIN startup_mentors sm ON s.startup_id = sm.startup_id
        JOIN mentors m ON sm.mentor_id = m.mentor_id
        ORDER BY s.name;
        """
        self.display_in_treeview(self.query_result_tree, query)

    def run_aggregate_query(self):
        # AGGREGATE: Get total funding per startup (using the function)
        query = """
        SELECT 
            s.name AS 'Startup',
            COUNT(f.funding_id) AS 'FundingRounds',
            fn_GetTotalFunding(s.startup_id) AS 'TotalFunding',
            fn_GetMentorCount(s.startup_id) AS 'MentorCount'
        FROM startups s
        LEFT JOIN funding f ON s.startup_id = f.startup_id
        GROUP BY s.startup_id, s.name -- Group by both ID and name
        ORDER BY TotalFunding DESC;
        """
        self.display_in_treeview(self.query_result_tree, query)

    def run_nested_query(self):
        # NESTED: Get founders of startups that are in the 'Growth' stage
        query = """
        SELECT name, email, contact
        FROM founders
        WHERE startup_id IN (
            SELECT startup_id
            FROM startups
            WHERE stage = 'Growth'
        );
        """
        self.display_in_treeview(self.query_result_tree, query)


# --- Run the Application ---
if __name__ == "__main__":
    app = App()
    app.mainloop()

