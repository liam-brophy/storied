import React from 'react';


const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <p>© {currentYear} E-Reader App. All Rights Reserved.</p>
      {/* You could add links here if needed */}
      {/* <p>
        <a href="/privacy">Privacy Policy</a> | <a href="/terms">Terms of Service</a>
      </p> */}
    </footer>
  );
};

export default Footer;