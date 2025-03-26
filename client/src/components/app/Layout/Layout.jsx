import React from "react";
import NavBar from "./NavBar.jsx";

const Layout = () => {
  return (
    <>
      <NavBar />
      <main>
        <div className="homepage">
          <h1>Home Page</h1>
          <p>
            Books yet to be rendered.
          </p>
          {/* Add additional homepage content or links as needed */}
        </div>
      </main>
    </>
  );
};

export default Layout;