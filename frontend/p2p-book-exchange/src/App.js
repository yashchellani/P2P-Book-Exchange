import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container, CssBaseline } from '@mui/material';
import { AppProvider } from './AppContext';
import Navbar from './components/Navbar';
import SignIn from './components/SignIn';
import Profile from './components/Profile';
import SignUp from './components/SignUp';
import Books from './components/Books';
import Explore from './components/Explore'; // New import

function App() {
  return (
    <Router>
      <CssBaseline />
      <AppProvider>
        <Navbar />
        <Container style={{ marginTop: 20 }}>
          <Routes>
            <Route path="/signup" element={<SignUp />} />
            <Route path="/login" element={<SignIn />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/books" element={<Books />} />
            <Route path="/explore" element={<Explore />} /> {/* New route */}
          </Routes>
        </Container>
      </AppProvider>
    </Router>
  );
}

export default App;
