import React, { useContext, useEffect, useState } from 'react';
import { 
  Typography, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper, 
  Button,
  Box,
  TextField
} from '@mui/material';
import { makeStyles } from '@mui/styles';
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

function Books() {
  const classes = useStyles();
  const { user_id } = useContext(AppContext);
  const [books, setBooks] = useState([]);
  const [wishlist, setWishlist] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/books');
        if (response.ok) {
          const data = await response.json();
          // Filter out the books owned by the user
          const filteredBooks = data.filter(book => book.owner_id !== user_id);
          setBooks(filteredBooks);
        } else {
          throw new Error('Error fetching books');
        }
      } catch (error) {
        console.error('Error fetching books:', error);
      }
    };

    fetchBooks();
  }, [user_id]);

  useEffect(() => {
    const fetchWishlist = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:5000/users/${user_id}/wishlist`);
        if (response.ok) {
          const data = await response.json();
          setWishlist(data);
        } else {
          throw new Error('Error fetching wishlist');
        }
      } catch (error) {
        console.error('Error fetching wishlist:', error);
      }
    };

    fetchWishlist();
  }, [user_id]);

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
        // Fetch the books again to update the list after the exchange
        const updatedResponse = await fetch('http://127.0.0.1:5000/books');
        if (updatedResponse.ok) {
          const updatedData = await updatedResponse.json();
          // Filter out the books owned by the user
          const filteredBooks = updatedData.filter(book => book.owner_id !== user_id);
          setBooks(filteredBooks);
        } else {
          throw new Error('Error fetching books after exchange');
        }
      } else {
        throw new Error('Error exchanging book');
      }
    } catch (error) {
      console.error('Error exchanging book:', error);
    }
  };

  const handleWishlist = async (bookId) => {
    try {
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user_id, book_id: bookId })
      };
      const response = await fetch(`http://127.0.0.1:5000/users/${user_id}/wishlist`, requestOptions);
      if (response.ok) {
        const data = await response.json();
        console.log(data);
        // Fetch the wishlist again to update the list after adding the book
        const updatedResponse = await fetch(`http://127.0.0.1:5000/users/${user_id}/wishlist`);
        if (updatedResponse.ok) {
          const updatedData = await updatedResponse.json();
          setWishlist(updatedData);
        } else {
          throw new Error('Error fetching wishlist after adding book');
        }
      } else {
        throw new Error('Error adding book to wishlist');
      }
    } catch (error) {
      console.error('Error adding book to wishlist:', error);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const filteredBooks = searchTerm
    ? books.filter(book => book.title.toLowerCase().includes(searchTerm.toLowerCase()))
    : books;

  return (
    <div>
      <Typography variant="h4">Available Books</Typography>

      <Box mt={2} mb={2}>
        <TextField
          label="Search by Title"
          variant="outlined"
          value={searchTerm}
          onChange={handleSearch}
        />
      </Box>

      <Box mt={4}>
        <TableContainer component={Paper}>
          <div className={classes.scrollableTable}>
            <Table className={classes.table} aria-label="simple table">
              <TableHead className={classes.tableHead}>
                <TableRow>
                  <TableCell className={classes.tableCell}>Title</TableCell>
                  <TableCell className={classes.tableCell}>Author</TableCell>
                  <TableCell className={classes.tableCell}>ISBN</TableCell>
                  <TableCell className={classes.tableCell}>Owner ID</TableCell>
                  <TableCell className={classes.tableCell}>Quantity</TableCell>
                  <TableCell className={classes.tableCell}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredBooks.map((book, index) => (
                  <TableRow key={index} className={classes.tableRow}>
                    <TableCell className={classes.tableCell}>{book.title}</TableCell>
                    <TableCell className={classes.tableCell}>{book.author}</TableCell>
                    <TableCell className={classes.tableCell}>{book.isbn}</TableCell>
                    <TableCell className={classes.tableCell}>{book.owner_id}</TableCell>
                    <TableCell className={classes.tableCell}>{book.quantity}</TableCell>
                    <TableCell className={classes.tableCell}>
                      <Button variant="outlined" color="primary" onClick={() => handleExchangeRequest(book.isbn)}>
                        Borrow
                      </Button>
                      <Button variant="outlined" color="secondary" onClick={() => handleWishlist(book.isbn)}>
                        Wishlist
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </TableContainer>
      </Box>

      <Box mt={4}>
        <Typography variant="h4">Wishlist</Typography>
        <TableContainer component={Paper}>
          <div className={classes.scrollableTable}>
            <Table className={classes.table} aria-label="simple table">
              <TableHead className={classes.tableHead}>
                <TableRow>
                  {/* <TableCell className={classes.tableCell}>Title</TableCell>
                  <TableCell className={classes.tableCell}>Author</TableCell> */}
                  <TableCell className={classes.tableCell}>ISBN</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {wishlist.map((book) => (
                  <TableRow className={classes.tableRow}>
                    {/* <TableCell className={classes.tableCell}>{book.title}</TableCell>
                    <TableCell className={classes.tableCell}>{book.author}</TableCell> */}
                    <TableCell className={classes.tableCell}>{book.isbn}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </TableContainer>
      </Box>
    </div>
  );
}

export default Books;
