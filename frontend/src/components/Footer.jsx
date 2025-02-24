/**
 * Footer Component
 *
 * Renders the footer section of the Sync Smart Home application.
 * It displays the current year and a copyright notice.
 *
 * @component
 * @example
 * return (
 *   <Footer />
 * )
 */

import React from "react";

const Footer = () => (
  <footer>
    <p>&copy; {new Date().getFullYear()} Sync Smart Home</p>
  </footer>
);

export default Footer;
