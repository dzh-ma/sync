/**
 * App Component
 *
 * The root component of the application. It sets up React Router for navigation
 * and includes the main layout components: Header, Footer, and the various pages.
 *
 * @component
 * @example
 * return (
 *   <App />
 * )
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './components/Home';
import About from './components/About';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import AddEnergyDataPage from './pages/AddEnergyDataPage';
import ReportPage from './pages/ReportPage';

function App() {
  return (
    <Router>
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/add-energy-data" element={<AddEnergyDataPage />} />
          <Route path="/report" element={<ReportPage />} />
        </Routes>
      </main>
      <Footer />
    </Router>
  )
}

export default App;
