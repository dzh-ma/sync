/**
 * Header Component
 *
 * Renders the header section of the Sync Smart Home application. This includes the application
 * title and a navigation menu with links to various pages such as Home, Login, Register, Dashboard,
 * Add Energy Data, and Report.
 *
 * @component
 * @example
 * return (
 *   <Header />
 * )
 */

import React from "react";
import { Link } from "react-router-dom";

const Header = () => (
  <header>
    <h1>Sync Smart Home</h1>
    <nav>
      <ul>
        <li><Link to="/">Home</Link></li>
        <li><Link to="/login">Login</Link></li>
        <li><Link to="/register">Register</Link></li>
        <li><Link to="/dashboard">Dashboard</Link></li>
        <li><Link to="/add-energy-data">Add Energy Data</Link></li>
        <li><Link to="/report">Report</Link></li>
      </ul>
    </nav>
  </header>
);

export default Header;
