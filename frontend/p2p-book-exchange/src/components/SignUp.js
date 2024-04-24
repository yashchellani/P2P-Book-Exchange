import React, { useContext, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Typography, Button, TextField, Container, Grid, Paper } from '@mui/material';
import { AppContext } from '../AppContext'; // Adjust the import path as necessary

function SignUp() {
 const { setUser_id } = useContext(AppContext);
 const navigate = useNavigate();
 const [username, setUsername] = useState('');
 const [email, setEmail] = useState('');
 const [password, setPassword] = useState('');
 // Add other necessary states here

 const handleSubmit = async (e) => {
    e.preventDefault();
    // Prepare the data to be sent to the backend
    const userData = {
      username,
      email,
      password,
      // Include other necessary fields here
    };

    // Send the sign-up data to the backend
    const response = await fetch('http://127.0.0.1:5000/users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (response.ok) {
      const data = await response.json();
      // Assuming the response contains a user_id
      const userId = data.message.split('UserID: ')[1];
      setUser_id(userId); // Set the user_id in the context
      navigate('/profile'); // Redirect to the profile page
    } else {
      // Handle error
      console.error('Sign-up failed');
    }
 };

 return (
    <Container component="main" maxWidth="xs">
      <Paper elevation={3} style={{ padding: 20, marginTop: 50 }}>
        <Typography variant="h5">Sign Up</Typography>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                variant="outlined"
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email Address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                variant="outlined"
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                variant="outlined"
                required
              />
            </Grid>
            {/* Add other necessary fields here */}
          </Grid>
          <Button type="submit" fullWidth variant="contained" color="primary" style={{ marginTop: 20 }}>
            Sign Up
          </Button>
          <Grid container justifyContent="flex-end">
            <Grid item>
              <Typography variant="body2">
                Already have an account? <Link to="/login">Sign in</Link>
              </Typography>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
 );
}

export default SignUp;