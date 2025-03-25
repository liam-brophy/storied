import React from "react";
import NavBar from "./NavBar.jsx";

const Layout = () => {
  return (
    <>
      <NavBar />
      <main>
        <div className="homepage">
          <h1>Welcome to the E-Reader App</h1>
          <p>
            Explore our collection of books, manage your notes, and enjoy a truly engaging reading experience.
          </p>
          {/* Add additional homepage content or links as needed */}
        </div>
      </main>
    </>
  );
};

export default Layout;