import sqlite3

# Connect to the database
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Create Books table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Books (
        BookID INTEGER PRIMARY KEY,
        Title TEXT,
        Author TEXT,
        ISBN TEXT,
        Status TEXT
    )
''')

# Create Users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        UserID INTEGER PRIMARY KEY,
        Name TEXT,
        Email TEXT
    )
''')

# Create Reservations table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservations (
        ReservationID INTEGER PRIMARY KEY,
        BookID INTEGER,
        UserID INTEGER,
        ReservationDate TEXT,
        FOREIGN KEY (BookID) REFERENCES Books(BookID),
        FOREIGN KEY (UserID) REFERENCES Users(UserID)
    )
''')

# Add a new book to the Books table
def add_book(title, author, isbn, status):
    cursor.execute('''
        INSERT INTO Books (Title, Author, ISBN, Status)
        VALUES (?, ?, ?, ?)
    ''', (title, author, isbn, status))
    conn.commit()
    print('Book added successfully.')

# Find a book's detail based on BookID
def find_book_details(book_id):
    cursor.execute('''
        SELECT 
            Books.Title, Books.Author, Books.ISBN, Books.Status,
            Users.Name, Users.Email,
            Reservations.ReservationDate
        FROM Books
        LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
        LEFT JOIN Users ON Reservations.UserID = Users.UserID
        WHERE Books.BookID = ?
    ''', (book_id,))
    result = cursor.fetchone()
    if result:
        title, author, isbn, status, user_name, user_email, reservation_date = result
        print('Book Details:')
        print('Title:', title)
        print('Author:', author)
        print('ISBN:', isbn)
        print('Status:', status)
        if user_name:
            print('Reserved by:', user_name)
            print('User email:', user_email)
            print('Reservation date:', reservation_date)
        else:
            print('Not reserved by any user.')
    else:
        print('Book not found.')

# Find a book's reservation status based on BookID, Title, UserID, and ReservationID
def find_reservation_status(query):
    if query.startswith('LB'):  # BookID
        cursor.execute('''
            SELECT Books.Status
            FROM Books
            WHERE Books.BookID = ?
        ''', (query[2:],))
    elif query.startswith('LU'):  # UserID
        cursor.execute('''
            SELECT 
                Books.Title, Books.Status
            FROM Books
            JOIN Reservations ON Books.BookID = Reservations.BookID
            WHERE Reservations.UserID = ?
        ''', (query[2:],))
    elif query.startswith('LR'):  # ReservationID
        cursor.execute('''
            SELECT 
                Books.Title, Books.Status,
                Users.Name, Users.Email
            FROM Books
            JOIN Reservations ON Books.BookID = Reservations.BookID
            JOIN Users ON Reservations.UserID = Users.UserID
            WHERE Reservations.ReservationID = ?
        ''', (query[2:],))
    else:
        print('Invalid input.')
        return
    
    result = cursor.fetchone()
    if result:
        if query.startswith('LB'):  # BookID
            status = result[0]
            print('Book Status:', status)
        elif query.startswith('LU'):  # UserID
            title, status = result
            print('Book Title:', title)
            print('Book Status:', status)
        elif query.startswith('LR'):  # ReservationID
            title, status, user_name, user_email = result
            print('Book Title:', title)
            print('Book Status:', status)
            print('Reserved by:', user_name)
            print('User email:', user_email)
    else:
        print('Book or Reservation not found.')

# Find all the books in the database
def find_all_books():
    cursor.execute('''
        SELECT 
            Books.BookID, Books.Title, Books.Author, Books.ISBN, Books.Status,
            Users.Name, Users.Email,
            Reservations.ReservationDate
        FROM Books
        LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
        LEFT JOIN Users ON Reservations.UserID = Users.UserID
    ''')
    results = cursor.fetchall()
    for result in results:
        book_id, title, author, isbn, status, user_name, user_email, reservation_date = result
        print('Book ID:', book_id)
        print('Title:', title)
        print('Author:', author)
        print('ISBN:', isbn)
        print('Status:', status)
        if user_name:
            print('Reserved by:', user_name)
            print('User email:', user_email)
            print('Reservation date:', reservation_date)
        else:
            print('Not reserved by any user.')
        print('---')

# Modify/update book details based on its BookID
def modify_book_details(book_id, title=None, author=None, isbn=None, status=None):
    if title or author or isbn or status:
        update_values = []
        if title:
            update_values.append(('Title', title))
        if author:
            update_values.append(('Author', author))
        if isbn:
            update_values.append(('ISBN', isbn))
        if status:
            update_values.append(('Status', status))

        update_query = '''
            UPDATE Books
            SET {}
            WHERE BookID = ?
        '''.format(', '.join('{} = ?'.format(field) for field, _ in update_values))

        values = [value for _, value in update_values]
        values.append(book_id)

        cursor.execute(update_query, tuple(values))
        conn.commit()

        # Update the status in Reservations table if Status is modified
        if status:
            cursor.execute('''
                UPDATE Reservations
                SET Status = ?
                WHERE BookID = ?
            ''', (status, book_id))
            conn.commit()

        print('Book details updated successfully.')
    else:
        print('No modifications provided.')

# Delete a book based on its BookID
def delete_book(book_id):
    cursor.execute('''
        DELETE FROM Books
        WHERE BookID = ?
    ''', (book_id,))
    conn.commit()
    cursor.execute('''
        DELETE FROM Reservations
        WHERE BookID = ?
    ''', (book_id,))
    conn.commit()
    print('Book deleted successfully.')

# Main program loop
while True:
    print('Library Management System')
    print('-------------------------')
    print('1. Add a new book')
    print('2. Find a book\'s detail based on BookID')
    print('3. Find a book\'s reservation status')
    print('4. Find all the books in the database')
    print('5. Modify/update book details')
    print('6. Delete a book')
    print('7. Exit')

    choice = input('Enter your choice (1-7): ')

    if choice == '1':
        title = input('Enter book title: ')
        author = input('Enter book author: ')
        isbn = input('Enter book ISBN: ')
        status = input('Enter book status: ')
        add_book(title, author, isbn, status)
    elif choice == '2':
        book_id = input('Enter BookID: ')
        find_book_details(book_id)
    elif choice == '3':
        query = input('Enter BookID, Title, UserID, or ReservationID: ')
        find_reservation_status(query)
    elif choice == '4':
        find_all_books()
    elif choice == '5':
        book_id = input('Enter BookID: ')
        title = input('Enter new title (leave empty to skip): ')
        author = input('Enter new author (leave empty to skip): ')
        isbn = input('Enter new ISBN (leave empty to skip): ')
        status = input('Enter new status (leave empty to skip): ')
        modify_book_details(book_id, title, author, isbn, status)
    elif choice == '6':
        book_id = input('Enter BookID: ')
        delete_book(book_id)
    elif choice == '7':
        print('Exiting...')
        break
    else:
        print('Invalid choice. Please try again.')

# Close the connection
conn.close()