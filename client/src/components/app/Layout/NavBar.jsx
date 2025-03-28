import React, { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom"; // Use NavLink for all links needing active state
import HomeIcon from '@mui/icons-material/Home'; // Represents 'Books' page after login
import DescriptionIcon from '@mui/icons-material/Description'; // Notes
import AccountCircleIcon from '@mui/icons-material/AccountCircle'; // Profile
import LoginIcon from '@mui/icons-material/Login'; // Login
import PersonAddIcon from '@mui/icons-material/PersonAdd'; // Register
import LogoutIcon from '@mui/icons-material/Logout'; // Logout
import UploadIcon from '@mui/icons-material/Upload'; // Upload
import BedtimeIcon from '@mui/icons-material/Bedtime';
import WbSunnyIcon from '@mui/icons-material/WbSunny';
import { useTheme } from "../../../contexts/ThemeContext"; // Adjust path if needed
import { useAuth } from "../../../contexts/AuthContext"; // Adjust path if needed
import './NavBar.css'

function NavBar() {
  const [isCollapsed, setIsCollapsed] = useState(true);
  const { theme, toggleTheme } = useTheme();
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate(); // Keep for potential future use

  const toggleNav = () => setIsCollapsed(!isCollapsed);

  const handleLogout = async () => {
    await logout();
    // AuthContext should handle redirect
  };

  // Helper for NavLink active class styling
  const getNavLinkClass = ({ isActive }) => (isActive ? "active-link" : "");

  return (
    <div className={`navbar-container ${isCollapsed ? "collapsed" : ""}`}>
      <button className="toggle-btn" onClick={toggleNav}>
        ☰
      </button>
      <nav className={`nav ${isCollapsed ? "collapsed" : "expanded"}`}>
        <ul>
          {isAuthenticated ? (
            // --- Authenticated Links ---
            <>
              <li>
                {/* Link to Books page */}
                <NavLink to="/books" className={getNavLinkClass}>
                  <HomeIcon />
                </NavLink>
              </li>
              <li>
                {/* Link to Notes page */}
                <NavLink to="/notes" className={getNavLinkClass}>
                  <DescriptionIcon />
                </NavLink>
              </li>
              <li>
                {/* Link to Upload page */}
                <NavLink to="/upload" className={getNavLinkClass}>
                  <UploadIcon />
                </NavLink>
              </li>
              <li>
                {/* Link to Profile page */}
                <NavLink to="/profile" className={getNavLinkClass}>
                  <AccountCircleIcon />
                </NavLink>
              </li>
            </>
          ) : (
            // --- Unauthenticated Links ---
            <>
              <li>
                <NavLink to="/login" className={getNavLinkClass}>
                  <LoginIcon />
                   {!isCollapsed && <span className="nav-text">Login</span>}
                </NavLink>
              </li>
              <li>
                <NavLink to="/register" className={getNavLinkClass}>
                  <PersonAddIcon />
                   {!isCollapsed && <span className="nav-text">Register</span>}
                </NavLink>
              </li>
              {/* Optional: Link Home icon to Login when logged out? Or remove? */}
              {/* <li>
                 <NavLink to="/login" className={getNavLinkClass}>
                   <HomeIcon />
                 </NavLink>
              </li> */}
            </>
          )}

          {/* Theme Toggle - Always Visible */}
          <li className="theme-toggle-item"> {/* Added class for potential specific styling */}
            <button className="theme-toggle nav-button" onClick={toggleTheme}> {/* Added nav-button class */}
              {theme === "light" ? <BedtimeIcon /> : <WbSunnyIcon />}
               {!isCollapsed && <span className="nav-text">Theme</span>}
            </button>
          </li>
        </ul>
      </nav>
    </div>
  );
}

export default NavBar;