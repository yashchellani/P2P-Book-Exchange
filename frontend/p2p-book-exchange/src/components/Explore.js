import React, { useContext, useEffect, useState } from 'react';
import { Typography, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Box } from '@mui/material';
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

function Explore() {
    const classes = useStyles();
    const { user_id } = useContext(AppContext);
    const [recommendations, setRecommendations] = useState([]);

    const fetchRecommendations = async () => {
        try {
            const requestOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user_id })
            };
            const response = await fetch('http://127.0.0.1:5000/books/recommendations', requestOptions);
            if (response.ok) {
                const data = await response.json();
                setRecommendations(data);
            } else {
                throw new Error('Error fetching recommendations');
            }
        } catch (error) {
            console.error('Error fetching recommendations:', error);
        }
    };

    useEffect(() => {
        fetchRecommendations();
    }, [user_id]);

    const handleRefresh = () => {
        fetchRecommendations();
    };

    const handleAddToWishlist = async (isbn) => {
        try {
            const requestOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user_id })
            };
            const response = await fetch(`http://127.0.0.1:5000/users/${isbn}/wishlist`, requestOptions);
            if (response.ok) {
                console.log('Book added to wishlist successfully');
                // Refresh recommendations after adding to the wishlist
                // show alert message that the book has been added
                alert('Book added to wishlist successfully');

            } else {
                throw new Error('Error adding book to wishlist');
            }
        } catch (error) {
            console.error('Error adding book to wishlist:', error);
        }
    };

    return (
        <div>
            <Typography variant="h4">Smart Recommendations</Typography>
            <Typography variant="h6">Based on your reading history and preferences</Typography>
            <Button onClick={handleRefresh} variant="contained" color="primary" style={{ marginTop: 10 }}>Refresh</Button>
            <Box mt={4}>
                <TableContainer component={Paper}>
                    <div className={classes.scrollableTable}>
                        <Table className={classes.table} aria-label="simple table">
                            <TableHead className={classes.tableHead}>
                                <TableRow>
                                    <TableCell className={classes.tableCell}>Title</TableCell>
                                    <TableCell className={classes.tableCell}>Author</TableCell>
                                    <TableCell className={classes.tableCell}>ISBN</TableCell>
                                    <TableCell className={classes.tableCell}>Actions</TableCell> {/* Add Actions column */}
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {recommendations.map((book, index) => (
                                    <TableRow key={index} className={classes.tableRow}>
                                        <TableCell className={classes.tableCell}>{book.title}</TableCell>
                                        <TableCell className={classes.tableCell}>{book.author}</TableCell>
                                        <TableCell className={classes.tableCell}>{book.isbn}</TableCell>
                                        <TableCell className={classes.tableCell}>
                                            <Button
                                                variant="outlined"
                                                color="primary"
                                                onClick={() => handleAddToWishlist(book.isbn)} // Call handleAddToWishlist function on button click
                                            >
                                                Add to Wishlist
                                            </Button>
                                        </TableCell>
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

export default Explore;
