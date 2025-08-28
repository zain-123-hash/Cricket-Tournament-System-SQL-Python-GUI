import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pyodbc

# Database connection function
def get_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'
        'DATABASE=Tournament;'
        'Trusted_Connection=yes;'
    )

# Show table list with additional buttons
def show_tables():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Select a Table", font=("Arial", 16)).pack(pady=10)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row.TABLE_NAME for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return

    table_var.set(tables[0])
    table_menu = ttk.OptionMenu(root, table_var, tables[0], *tables)
    table_menu.pack(pady=5)

    # Buttons frame
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="View Data", command=show_table_data).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Search", command=show_search_dialog).pack(side=tk.LEFT, padx=5)

def show_tables():
    for widget in root.winfo_children():
        widget.destroy()

    # Main container frame
    main_frame = tk.Frame(root)
    main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

    # Title
    tk.Label(main_frame, text="Select a Table", font=("Arial", 16)).pack(pady=10)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row.TABLE_NAME for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return

    # Table selection
    table_var.set(tables[0])
    table_menu = ttk.OptionMenu(main_frame, table_var, tables[0], *tables)
    table_menu.pack(pady=10)

    # Button container
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=20)

    # Buttons arranged horizontally
    tk.Button(button_frame, text="View Data", command=show_table_data, width=12).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Search", command=show_search_dialog, width=12).pack(side=tk.LEFT, padx=5)

def show_table_data():
    table_name = table_var.get()
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        # Clean the data by removing tuple representation
        cleaned_rows = []
        for row in rows:
            cleaned_rows.append([str(item).strip("()") if isinstance(item, tuple) else str(item) for item in row])
        
    except Exception as e:
        messagebox.showerror("Query Error", str(e))
        return

    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text=f"Table: {table_name}", font=("Arial", 16)).pack(pady=10)

    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")
    for row in cleaned_rows:  # Use cleaned rows here
        tree.insert("", "end", values=row)
    tree.pack(expand=True, fill="both")

    tk.Button(root, text="Back", command=show_tables).pack(pady=10)

def show_search_dialog():
    table_name = table_var.get()
    
    # Define important columns for each table
    search_columns = {
        'Standings': ['Team_ID', 'Wins', 'Points'],
        'Teams': ['TeamName', 'Abbreviation'],
        'Player': ['Name', 'Role'],
        'Matches': ['Team1_ID', 'Team2_ID', 'WinnerID'],
        # Add other tables as needed
    }
    
    columns = search_columns.get(table_name, [])
    
    if not columns:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT TOP 1 * FROM {table_name}")
            columns = [column[0] for column in cursor.description][:3]  # Get first 3 columns if no specific config
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get columns: {str(e)}")
            return
    
    search_dialog = tk.Toplevel(root)
    search_dialog.title(f"Search in {table_name}")
    
    search_frame = tk.Frame(search_dialog)
    search_frame.pack(padx=10, pady=10)
    
    search_vars = {}
    for i, col in enumerate(columns):
        tk.Label(search_frame, text=col).grid(row=i, column=0, padx=5, pady=5)
        search_vars[col] = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_vars[col]).grid(row=i, column=1, padx=5, pady=5)
    
    def perform_search():
        conditions = []
        params = []
        for col in columns:
            value = search_vars[col].get()
            if value:
                conditions.append(f"{col} LIKE ?")
                params.append(f"%{value}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE {where_clause}", params)
            rows = cursor.fetchall()
            conn.close()
            
            # Clean the data
            cleaned_rows = []
            for row in rows:
                cleaned_rows.append([str(item).strip("()") if isinstance(item, tuple) else str(item) for item in row])
            
            # Display results
            result_window = tk.Toplevel(root)
            result_window.title(f"Search Results in {table_name}")
            
            tree = ttk.Treeview(result_window, columns=columns, show="headings")
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            for row in cleaned_rows:
                tree.insert("", "end", values=row)
            
            tree.pack(expand=True, fill="both")
            
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search: {str(e)}")
    
    tk.Button(search_dialog, text="Search", command=perform_search).pack(pady=10)

def insert_data():
    if not messagebox.askyesno("Confirm", "This will reset all database data. Continue?"):
        return
        
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Clear existing data in proper order
        tables_to_clear = [
            'PlayerPerformance', 'TeamPerformance', 'MatchDetails',
            'Standings', 'Matches', 'Player', 'Teams',
            'Tournament_Groups', 'Venues', 'Tournament'
        ]
        
        for table in tables_to_clear:
            try:
                cursor.execute(f"DELETE FROM {table}")
                conn.commit()
            except Exception as e:
                print(f"Error clearing {table}: {e}")
                conn.rollback()
        
        # Insert data in proper order
        # 1. Tournament
        cursor.execute("""
            INSERT INTO Tournament (T_ID, Years, Host_country, Formats)
            VALUES (1, 2025, 'Pakistan', 'ODI')
        """)
        
        # 2. Venues
        cursor.execute("""
            INSERT INTO Venues (VenueName, City, Country)
            VALUES 
                ('Gaddafi', 'Lahore', 'Pakistan'),
                ('National', 'Karachi', 'Pakistan'),
                ('Rawal-S', 'Rawalpindi', 'Pakistan')
        """)
        
        # 3. Tournament Groups
        cursor.execute("""
            INSERT INTO Tournament_Groups (GroupName, T_ID)
            VALUES ('Group A', 1), ('Group B', 1)
        """)
        
        # 4. Teams
        cursor.execute("""
            INSERT INTO Teams (TeamName, G_ID, Abbreviation)
            VALUES 
                ('Pakistan', 1, 'PAK'), ('India', 1, 'IND'), 
                ('Australia', 1, 'AUS'), ('England', 1, 'ENG'), 
                ('New Zealand', 1, 'NZ'), ('South Africa', 2, 'SA'), 
                ('Sri Lanka', 2, 'SL'), ('Bangladesh', 2, 'BAN'), 
                ('Afghanistan', 2, 'AFG'), ('West Indies', 2, 'WI')
        """)
        
        # 5. Players
        cursor.execute("""
            INSERT INTO Player (Team_ID, Name, KitNumber, Role)
            VALUES
                (1, 'Babar Azam', 56, 'Batsman'), 
                (1, 'Shaheen Afridi', 10, 'Bowler'),
                (1, 'Mohammad Rizwan', 16, 'Wicketkeeper'),
                (2, 'Rohit Sharma', 45, 'Batsman'),
                (2, 'Virat Kohli', 18, 'Batsman'),
                (2, 'Jasprit Bumrah', 93, 'Bowler'),
                (3, 'Pat Cummins', 30, 'All-rounder'),
                (3, 'Steve Smith', 49, 'Batsman'),
                (3, 'Glenn Maxwell', 32, 'All-rounder'),
                (4, 'Jos Buttler', 63, 'Wicketkeeper'),
                (4, 'Ben Stokes', 55, 'All-rounder'),
                (4, 'Jofra Archer', 22, 'Bowler'),
                (5, 'Kane Williamson', 22, 'Batsman'),
                (5, 'Trent Boult', 18, 'Bowler'),
                (5, 'Devon Conway', 3, 'Wicketkeeper')
        """)
        
        # 6. Matches
        cursor.execute("""
            INSERT INTO Matches (T_ID, Team1_ID, Team2_ID, Date, VenueID, Stage)
            VALUES
                (1, 1, 2, '2025-10-10 14:30:00', 1, 'Group'),
                (1, 3, 4, '2025-10-11 14:30:00', 2, 'Group'),
                (1, 1, 5, '2025-10-13 14:30:00', 3, 'Group'),
                (1, 2, 3, '2025-10-15 14:30:00', 1, 'Group'),
                (1, 6, 7, '2025-10-10 09:30:00', 2, 'Group'),
                (1, 8, 9, '2025-10-12 09:30:00', 3, 'Group')
        """)
        
        # 7. Update Match Winners
        cursor.execute("""
            UPDATE Matches SET WinnerID = 1 WHERE MatchID = 1
            UPDATE Matches SET WinnerID = 3 WHERE MatchID = 2
            UPDATE Matches SET WinnerID = 1 WHERE MatchID = 3
            UPDATE Matches SET WinnerID = 2 WHERE MatchID = 4
            UPDATE Matches SET WinnerID = 6 WHERE MatchID = 5
            UPDATE Matches SET WinnerID = 9 WHERE MatchID = 6
        """)
        
        # 8. Match Details
        cursor.execute("""
            INSERT INTO MatchDetails (Match_ID, TossWinner, TossDecision, 
                                   FirstInningsScore, SecondInningsScore, Result, PlayerOfMatch)
            VALUES
                (1, 1, 'Bat', '315/7', '290/9', 'Pakistan won by 25 runs', 1),
                (2, 3, 'Bowl', '280/9', '281/6', 'Australia won by 4 wickets', 7),
                (3, 1, 'Bat', '342/6', '300/8', 'Pakistan won by 42 runs', 2),
                (4, 2, 'Bowl', '320/8', '324/5', 'India won by 5 wickets', 5),
                (5, 6, 'Bat', '298/7', '250/10', 'South Africa won by 48 runs', 17),
                (6, 8, 'Bowl', '240/10', '241/7', 'Afghanistan won by 3 wickets', 26)
        """)
        
        # 9. Team Performance
        cursor.execute("""
            INSERT INTO TeamPerformance (Team_ID, Match_ID, RunsScored, WicketsLost, Fours, Sixes, Extras)
            VALUES
                (1, 1, 315, 7, 28, 8, 12),
                (2, 1, 290, 9, 25, 6, 10),
                (3, 2, 280, 9, 22, 5, 15),
                (4, 2, 281, 6, 24, 7, 8),
                (1, 3, 342, 6, 30, 10, 14),
                (5, 3, 300, 8, 26, 8, 12)
        """)
        
        # 10. Player Performance
        cursor.execute("""
            INSERT INTO PlayerPerformance (Player_ID, Match_ID, RunsScored, BallsFaced, 
                                        Fours, Sixes, WicketsTaken, RunsConceded, OversBowled, Catches)
            VALUES
                (1, 1, 112, 120, 10, 2, 0, 0, 0, 1),
                (2, 1, 45, 30, 3, 2, 3, 45, 10, 0),
                (4, 1, 85, 90, 8, 1, 0, 0, 0, 0),
                (7, 2, 60, 45, 5, 1, 2, 38, 8, 1),
                (10, 2, 78, 65, 6, 3, 0, 0, 0, 2),
                (1, 3, 98, 110, 9, 3, 0, 0, 0, 0)
        """)
        
        # 11. Standings
        cursor.execute("""
            INSERT INTO Standings (T_ID, Team_ID, MatchesPlayed, Wins, Losses, Points, NRR)
            VALUES
                (1, 1, 2, 2, 0, 4, 1.25),
                (1, 2, 2, 1, 1, 2, 0.50),
                (1, 3, 2, 1, 1, 2, 0.20),
                (1, 4, 1, 0, 1, 0, -0.40),
                (1, 5, 1, 0, 1, 0, -0.80),
                (1, 6, 1, 1, 0, 2, 0.60),
                (1, 7, 1, 0, 1, 0, -0.30),
                (1, 9, 1, 1, 0, 2, 0.40)
        """)
        
        conn.commit()
        messagebox.showinfo("Success", "Database initialized successfully!")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to initialize database: {str(e)}")
        conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

# Welcome screen
def show_welcome():
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root, text="Champions Trophy", font=("Arial", 24, "bold")).pack(pady=50)
    tk.Button(root, text="Enter", font=("Arial", 14), command=show_tables).pack(pady=20)
    tk.Button(root, text="Initialize Database", font=("Arial", 12), 
              command=insert_data).pack(pady=10)

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Champions Trophy")
    root.geometry("800x600")
    table_var = tk.StringVar()
    
    show_welcome()
    root.mainloop()