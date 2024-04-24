import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { AppContext } from '../AppContext';

function Navbar() {
  const { user_id } = useContext(AppContext);

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component={Link} to="/profile" style={{ textDecoration: 'none', color: 'inherit' }}>
          Heymax.ai Book Exchange
        </Typography>
        <Box sx={{ marginLeft: 'auto' }}>
          {(user_id !== '' || user_id != undefined) ? (
            <>
              <Typography variant="h6">
                Hello, User {user_id}
              </Typography>
              <Button component={Link} to="/profile" color="inherit">Profile</Button>
            </>
          ) : (
            <>
              <Button component={Link} to="/login" color="inherit">Login</Button>
              <Button component={Link} to="/signup" color="inherit">Sign Up</Button>
            </>
          )}
          <Button component={Link} to="/books" color="inherit">Books</Button>
          <Button component={Link} to="/explore" color="inherit">Explore</Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
