import sqlite3


def initialize_database():
  """Initializes the SQLite database and creates tables with relationships."""
  conn = sqlite3.connect("library.db")
  cursor = conn.cursor()

  # Enable foreign key support
  cursor.execute("PRAGMA foreign_keys = ON;")

  # 1. Users Table (Authentication & Roles)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

  # 2. Books Table (Inventory / CRUD)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)

  # 3. Transactions Table (Foreign Keys & Relationships)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            book_id INTEGER,
            borrow_date TEXT,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (book_id) REFERENCES books(book_id)
        )
    """)

  conn.commit()
  conn.close()


def register_user(conn):
  """Handles user registration with input validation and duplicate checks."""
  cursor = conn.cursor()
  print("\n--- User Registration ---")
  username = input("Enter username: ").strip()
  if not username:
    print("Error: Username cannot be empty.")
    return

  password = input("Enter password: ").strip()
  if not password:
    print("Error: Password cannot be empty.")
    return

  print("Select Role: 1. Admin 2. Member")
  role_choice = input("Enter choice (1/2): ").strip()
  role = "admin" if role_choice == "1" else "member"

  try:
    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, password, role),
    )
    conn.commit()
    print("Registration successful! You can now log in.")
  except sqlite3.IntegrityError:
    print("Error: Username already exists. Choose a different one.")


def login_user(conn):
  """Handles user login."""
  cursor = conn.cursor()
  print("\n--- User Login ---")
  username = input("Enter username: ").strip()
  password = input("Enter password: ").strip()

  cursor.execute(
      "SELECT user_id, username, role FROM users WHERE username = ? AND"
      " password = ?",
      (username, password),
  )
  user = cursor.fetchone()

  if user:
    print(f"\nWelcome back, {user[1]} ({user[2].upper()})!")
    return {"user_id": user[0], "username": user[1], "role": user[2]}
  else:
    print("Invalid username or password.")
    return None


def admin_menu(conn, current_user):
  """Admin menu with full CRUD operations."""
  cursor = conn.cursor()
  while True:
    print("\n--- Admin Dashboard ---")
    print("1. Add New Book (Create)")
    print("2. View All Books (Read)")
    print("3. Update Book Quantity (Update)")
    print("4. Delete Book (Delete)")
    print("5. View All Borrow Transactions")
    print("6. Logout")

    choice = input("Enter choice (1-6): ").strip()

    if choice == "1":
      title = input("Enter book title: ").strip()
      author = input("Enter author name: ").strip()
      if not title or not author:
        print("Error: Title and Author cannot be empty.")
        continue
      try:
        qty = int(input("Enter quantity: ").strip())
        cursor.execute(
            "INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)",
            (title, author, qty),
        )
        conn.commit()
        print("Book added successfully!")
      except ValueError:
        print("Invalid input: Quantity must be a valid number.")

    elif choice == "2":
      cursor.execute("SELECT * FROM books")
      books = cursor.fetchall()
      print("\nID | Title | Author | Quantity")
      print("-" * 40)
      for b in books:
        print(f"{b[0]} | {b[1]} | {b[2]} | {b[3]}")

    elif choice == "3":
      try:
        book_id = int(input("Enter Book ID to update: ").strip())
        new_qty = int(input("Enter new quantity: ").strip())
        cursor.execute(
            "UPDATE books SET quantity = ? WHERE book_id = ?", (new_qty, book_id)
        )
        conn.commit()
        print("Book quantity updated successfully!")
      except ValueError:
        print("Invalid ID or quantity format.")

    elif choice == "4":
      try:
        book_id = int(input("Enter Book ID to delete: ").strip())
        cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
        conn.commit()
        print("Book deleted successfully!")
      except ValueError:
        print("Invalid Book ID format.")

    elif choice == "5":
      cursor.execute("""
                SELECT t.transaction_id, u.username, b.title, t.borrow_date, t.status 
                FROM transactions t
                JOIN users u ON t.user_id = u.user_id
                JOIN books b ON t.book_id = b.book_id
            """)
      records = cursor.fetchall()
      print("\nTx ID | User | Book | Date | Status")
      print("-" * 45)
      for r in records:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")

    elif choice == "6":
      print("Logging out...")
      break
    else:
      print("Invalid choice. Please select between 1 and 6.")


def member_menu(conn, current_user):
  """Member menu to view books and borrow items."""
  cursor = conn.cursor()
  while True:
    print("\n--- Member Dashboard ---")
    print("1. View Available Books")
    print("2. Borrow a Book")
    print("3. View My Borrowing History")
    print("4. Logout")

    choice = input("Enter choice (1-4): ").strip()

    if choice == "1":
      cursor.execute("SELECT * FROM books WHERE quantity > 0")
      books = cursor.fetchall()
      print("\nID | Title | Author | Available Quantity")
      print("-" * 45)
      for b in books:
        print(f"{b[0]} | {b[1]} | {b[2]} | {b[3]}")

    elif choice == "2":
      try:
        book_id = int(input("Enter Book ID you want to borrow: ").strip())
        cursor.execute(
            "SELECT quantity, title FROM books WHERE book_id = ?", (book_id,)
        )
        book = cursor.fetchone()

        if book and book[0] > 0:
          cursor.execute(
              "UPDATE books SET quantity = quantity - 1 WHERE book_id = ?",
              (book_id,),
          )
          cursor.execute(
              """INSERT INTO transactions (user_id, book_id, borrow_date, status) 
                         VALUES (?, ?, datetime('current_timestamp'), 'Borrowed')""",
              (current_user["user_id"], book_id),
          )
          conn.commit()
          print(f"Successfully borrowed '{book[1]}'!")
        else:
          print("Error: Book is either out of stock or invalid ID.")
      except ValueError:
        print("Invalid Book ID format.")

    elif choice == "3":
      cursor.execute(
          """
                SELECT t.transaction_id, b.title, t.borrow_date, t.status 
                FROM transactions t
                JOIN books b ON t.book_id = b.book_id
                WHERE t.user_id = ?
            """,
          (current_user["user_id"],),
      )
      history = cursor.fetchall()
      print("\nTx ID | Book Title | Borrow Date | Status")
      print("-" * 45)
      for h in history:
        print(f"{h[0]} | {h[1]} | {h[2]} | {h[3]}")

    elif choice == "4":
      print("Logging out...")
      break
    else:
      print("Invalid choice. Please select between 1 and 4.")


def main():
  initialize_database()
  conn = sqlite3.connect("library.db")
  conn.execute("PRAGMA foreign_keys = ON;")

  try:
    while True:
      print("\n=== LIBRARY MANAGEMENT SYSTEM ===")
      print("1. Register Account")
      print("2. Login")
      print("3. Exit Application")

      choice = input("Choose an option (1-3): ").strip()

      if choice == "1":
        register_user(conn)
      elif choice == "2":
        user = login_user(conn)
        if user:
          if user["role"] == "admin":
            admin_menu(conn, user)
          else:
            member_menu(conn, user)
      elif choice == "3":
        print("Exiting application. Goodbye!")
        break
      else:
        print("Invalid choice. Please select 1, 2, or 3.")
  except Exception as e:
    print(f"An unexpected error occurred: {e}")
  finally:
    conn.close()


if __name__ == "__main__":
  main()