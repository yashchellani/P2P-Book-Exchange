import React, { useContext, useEffect, useState } from 'react';
import { 
 Typography, 
 Button, 
 Table, 
 TableBody, 
 TableCell, 
 TableContainer, 
 TableHead, 
 TableRow, 
 Paper, 
 TextField, 
 Grid,
 Box,
 Rating
} from '@mui/material';
import { makeStyles } from '@mui/styles';
import { Link, Navigate } from 'react-router-dom';
import { AppContext } from '../AppContext';

const useStyles = makeStyles({
    table: {
       minWidth: 650,
    },
    tableHead: {
       backgroundColor: '#f5f5f5',
       position: 'sticky', 
       top: 0, 
       zIndex: 100, 
    },
    tableCell: {
       fontSize: 14,
    },
    tableRow: {
       '&:nth-of-type(odd)': {
         backgroundColor: '#fafafa',
       },
    },
    scrollableTable: {
       maxHeight: 440,
       overflowY: 'auto',
    },
   });
   const exchangeStatus = ["", "pending", "rejected", "completed"]
   
   function Profile() {
    const classes = useStyles();
    const { user_id, setUser_id } = useContext(AppContext);
    const [books, setBooks] = useState([]);
    const [borrowedBooks, setBorrowedBooks] = useState([]);
    const [formData, setFormData] = useState({ title: '', author: '', isbn: '' });

    const handleLogout = () => {
        // Clear user_id on logout
        setUser_id(null);
    };

    useEffect(() => {
        const fetchBooks = async () => {
            try {
                if (user_id) {
                    const response = await fetch(`http://127.0.0.1:5000/users/${user_id}/books`);
                    if (response.ok) {
                        const data = await response.json();
                        setBooks(data);
                    } else {
                        throw new Error('Error fetching books');
                    }
                }
            } catch (error) {
                console.error('Error fetching books:', error);
            }
        };

        const fetchBorrowedBooks = async () => {
            try {
                if (user_id) {
                    const response = await fetch(`http://127.0.0.1:5000/users/${user_id}/books/borrowed`);
                    if (response.ok) {
                        const data = await response.json();
                        setBorrowedBooks(data);
                    } else {
                        throw new Error('Error fetching borrowed books');
                    }
                }
            } catch (error) {
                console.error('Error fetching borrowed books:', error);
            }
        };

        fetchBooks();
        fetchBorrowedBooks();
    }, [user_id]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...formData, owner_id: user_id })
        };
        try {
            const response = await fetch('http://127.0.0.1:5000/books', requestOptions);
            if (response.ok) {
                const data = await response.json();
                console.log(data);
                setFormData({ title: '', author: '', isbn: '' });

                const booksResponse = await fetch(`http://127.0.0.1:5000/users/${user_id}/books`);
                if (booksResponse.ok) {
                    const booksData = await booksResponse.json();
                    setBooks(booksData);
                } else {
                    throw new Error('Error fetching books');
                }
            } else {
                throw new Error('Error creating book');
            }
        } catch (error) {
            console.error(error);
        }
    };

    const handleExchangeRequest = async (bookId) => {
        try {
            const requestOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user_id })
            };
            const response = await fetch(`http://127.0.0.1:5000/books/${bookId}/exchange`, requestOptions);
            if (response.ok) {
                const data = await response.json();
                console.log(data);
                const borrowedBooksResponse = await fetch(`http://127.0.0.1:5000/users/${user_id}/books/borrowed`);
                if (borrowedBooksResponse.ok) {
                    const borrowedBooksData = await borrowedBooksResponse.json();
                    setBorrowedBooks(borrowedBooksData);
                } else {
                    throw new Error('Error fetching borrowed books after exchange');
                }
            } else {
                throw new Error('Error exchanging book');
            }
        } catch (error) {
            console.error('Error exchanging book:', error);
        }
    };

    const handleCompleteExchange = async (bookId) => {
        try {
            const requestOptions = {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: 1 })
            };
            const response = await fetch(`http://127.0.0.1:5000/books/${bookId}/exchange/${user_id}`, requestOptions);
            if (response.ok) {
                const data = await response.json();
                console.log(data);
                // Fetch the borrowed books again to update the list after the exchange
                const borrowedBooksResponse = await fetch(`http://127.0.0.1:5000/users/${user_id}/books/borrowed`);
                if (borrowedBooksResponse.ok) {
                    const borrowedBooksData = await borrowedBooksResponse.json();
                    setBorrowedBooks(borrowedBooksData);
                } else {
                    throw new Error('Error fetching borrowed books after exchange');
                }
            } else {
                throw new Error('Error completing exchange');
            }
        } catch (error) {
            console.error('Error completing exchange:', error);
        }
    };

    const handleRateBook = async (bookId, rating) => {
        try {
            const requestOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user_id, book_id: bookId, rating: rating })
            };
            const response = await fetch(`http://127.0.0.1:5000/books/rate`, requestOptions);
            if (response.ok) {
                const data = await response.json();
                console.log(data);
            } else {
                throw new Error('Error rating book');
            }
        } catch (error) {
            console.error('Error rating book:', error);
        }
    };
    const handleRelistBook = async (bookId) => {
        try {
            const requestOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify([{ ...borrowedBooks.find(b => b.isbn === bookId), owner_id: user_id }])
            };
            const response = await fetch(`http://127.0.0.1:5000/books/add`, requestOptions);
            if (response.ok) {
                console.log('Book relisted successfully');
                // Fetch the borrowed books again to update the list after relisting
                const borrowedBooksResponse = await fetch(`http://127.0.0.1:5000/users/${user_id}/books/borrowed`);
                if (borrowedBooksResponse.ok) {
                    const borrowedBooksData = await borrowedBooksResponse.json();
                    setBorrowedBooks(borrowedBooksData);
                } else {
                    throw new Error('Error fetching borrowed books after relisting');
                }
            } else {
                throw new Error('Error relisting book');
            }
        } catch (error) {
            console.error('Error relisting book:', error);
        }
    };


    // Redirect to login if user is not logged in
    if (!user_id) {
        return <Navigate to="/login" />;
    }

    return (
        <div>
            <Typography variant="h4">Dashboard</Typography>
            {/* <Typography variant="body1">User ID: {user_id}</Typography> */}
            {/* <Button onClick={handleLogout} variant="contained" color="primary">Logout</Button> */}

            <Box mt={4}>
                <Typography variant="h5">Your Books</Typography>
                <TableContainer component={Paper}>
                    {/* Wrap the Table in a div with the scrollableTable class */}
                    <div className={classes.scrollableTable}>
                        <Table className={classes.table} aria-label="simple table">
                            <TableHead className={classes.tableHead}>
                                <TableRow>
                                    <TableCell className={classes.tableCell}>Title</TableCell>
                                    <TableCell className={classes.tableCell}>Author</TableCell>
                                    <TableCell className={classes.tableCell}>ISBN</TableCell>
                                    <TableCell className={classes.tableCell}>Rating</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {books.map((book, index) => (
                                    <TableRow key={index} className={classes.tableRow}>
                                        <TableCell className={classes.tableCell}>{book.title}</TableCell>
                                        <TableCell className={classes.tableCell}>{book.author}</TableCell>
                                        <TableCell className={classes.tableCell}>{book.isbn}</TableCell>
                                        <TableCell className={classes.tableCell}>
                                            <Rating
                                                name={`book-rating-${index}`}
                                                value={book.rating}
                                                onChange={(event, newValue) => {
                                                    handleRateBook(book.isbn, newValue);
                                                }}
                                            />
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </TableContainer>
            </Box>

            <Box mt={4}>
                <Typography variant="h5">Borrowed Books</Typography>
                <TableContainer component={Paper}>
                    <div className={classes.scrollableTable}>
                        <Table className={classes.table} aria-label="simple table">
                            <TableHead className={classes.tableHead}>
                                <TableRow>
                                    <TableCell className={classes.tableCell}>Title</TableCell>
                                    <TableCell className={classes.tableCell}>Author</TableCell>
                                    <TableCell className={classes.tableCell}>ISBN</TableCell>
                                    <TableCell className={classes.tableCell}>Status</TableCell>
                                    <TableCell className={classes.tableCell}>Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {borrowedBooks.map((book, index) => (
                                    <TableRow key={index} className={classes.tableRow}>
                                        <TableCell className={classes.tableCell}>{book.title}</TableCell>
                                        <TableCell className={classes.tableCell}>{book.author}</TableCell>
                                        <TableCell className={classes.tableCell}>{book.isbn}</TableCell>
                                        <TableCell className={classes.tableCell}>{exchangeStatus[book.status]}</TableCell>
                                        <TableCell className={classes.tableCell}>
                                            {book.status === 1 && (
                                                <Button
                                                    variant="outlined"
                                                    color="primary"
                                                    onClick={() => handleCompleteExchange(book.isbn)}
                                                >
                                                    Complete Exchange
                                                </Button>
                                            )}
                                            {book.status === 3 && (
                                                <Button
                                                    variant="outlined"
                                                    color="primary"
                                                    onClick={() => handleRelistBook(book.isbn)}
                                                >
                                                    Relist
                                                </Button>
                                            )}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </TableContainer>
            </Box>

            <Box mt={4}>
                <Typography variant="h5">Add a New Book</Typography>
                <form onSubmit={handleSubmit}>
                    <Grid container spacing={2} mt={2}>
                        <Grid item xs={4}>
                            <TextField
                                fullWidth
                                label="Title"
                                variant="outlined"
                                value={formData.title}
                                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                required
                            />
                        </Grid>
                        <Grid item xs={4}>
                            <TextField
                                fullWidth
                                label="Author"
                                variant="outlined"
                                value={formData.author}
                                onChange={(e) => setFormData({ ...formData, author: e.target.value })}
                                required
                            />
                        </Grid>
                        <Grid item xs={4}>
                            <TextField
                                fullWidth
                                label="ISBN"
                                variant="outlined"
                                value={formData.isbn}
                                onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
                                required
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <Button type="submit" variant="contained" color="primary">Add Book</Button>
                        </Grid>
                    </Grid>
                </form>
            </Box>
        </div>
    );
}

export default Profile;
