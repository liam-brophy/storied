import { Outlet } from "react-router-dom";
import NavBar from "./NavBar";

const Layout = () => {
  return (
    <>
      <NavBar />
      <main>
        <Outlet /> {/* This renders the current route’s content */}
      </main>
    </>
  );
};

export default Layout;