import React, { useContext, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Typography, Button, TextField, Box } from '@mui/material';
import { AppContext } from '../AppContext';

function SignIn() {
  const { setUser_id } = useContext(AppContext);
  const [loggedIn, setLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Send a POST request to backend to verify user's credentials
//     fetch('http://localhost:5000/users/login', {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json'
//       },
//       body: JSON.stringify({
//         email: username,
//         password: password
//       })
//     })
//     .then(response => {
//       if (response.ok) {
//         return response.json();
//       } else {
//         console.log(response)
//         throw new Error('Invalid credentials');
//       }
//     })
//     .then(data => {
//       // If login is successful, set the user_id in context
//       setUser_id(data.user_id);
//       setLoggedIn(true);
//     })
//     .catch(error => {
//       console.error('Login error:', error);
//       setError('Invalid username or password');
//     });
//   };

    const response = await fetch('http://127.0.0.1:5000/users/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: username,
        password: password
      }),
    });

    if (response.ok) {
      const data = await response.json();
      // Assuming the response contains a user_id
      const userId = data['user_id'];
      console.log(data);
      setUser_id(userId); // Set the user_id in the context
      navigate('/profile'); // Redirect to the profile page
    } else {
      // Handle error
      console.error('Sign-in failed');
    }
 };

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="30vh"
    >
      {/* {loggedIn && <Navigate to="/profile" />} */}
      <Typography variant="h4">Login</Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Email"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          margin="normal"
          required
        />
        <TextField
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          margin="normal"
          required
        />
        {error && <Typography variant="body2" color="error">{error}</Typography>}
        <br />
        <Button type="submit" variant="contained" color="primary">Login</Button>
      </form>
      <br />
      <Typography>Don't have an account? <Link to="/signup">Sign Up</Link></Typography>
    </Box>
  );
}

export default SignIn;
