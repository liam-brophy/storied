import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const ProfilePage = () => {
  const { user, logout, updateUserProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    password: '', // Only for changing password
  });
  const [updateStatus, setUpdateStatus] = useState({ message: '', error: '' });
  const [isLoading, setIsLoading] = useState(false);


  // Update form data if user context changes (e.g., after initial load)
  React.useEffect(() => {
    if(user) {
      setFormData(prev => ({ ...prev, username: user.username, email: user.email }));
    }
  }, [user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleUpdateProfile = async (e) => {
     e.preventDefault();
     setUpdateStatus({ message: '', error: '' });
     setIsLoading(true);

     const dataToUpdate = {};
     if (formData.username !== user.username) {
       dataToUpdate.username = formData.username;
     }
     if (formData.email !== user.email) {
        dataToUpdate.email = formData.email;
     }
     if (formData.password) { // Only include password if user entered something
        dataToUpdate.password = formData.password;
     }

     if (Object.keys(dataToUpdate).length === 0) {
        setUpdateStatus({ message: 'No changes detected.', error: '' });
        setIsLoading(false);
        setIsEditing(false); // Close edit mode if no changes
        return;
     }

     try {
        const result = await updateUserProfile(dataToUpdate);
        setUpdateStatus({ message: result.message || 'Profile updated successfully!', error: '' });
        setIsEditing(false); // Exit edit mode on success
        setFormData(prev => ({ ...prev, password: '' })); // Clear password field after update
     } catch (err) {
        setUpdateStatus({ message: '', error: err.response?.data?.error || 'Failed to update profile.' });
     } finally {
        setIsLoading(false);
     }
  };


  if (!user) {
    // This shouldn't typically happen if ProtectedRoute is working, but good fallback
    return <p>Loading user profile or not logged in...</p>;
  }

  return (
    <div>
      <h1>User Profile</h1>
       {updateStatus.message && <p style={{ color: 'green' }}>{updateStatus.message}</p>}
       {updateStatus.error && <p style={{ color: 'red' }}>{updateStatus.error}</p>}

      {!isEditing ? (
        <div>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Joined:</strong> {new Date(user.created_at).toLocaleDateString()}</p>
          {/* Display other user details from user.to_dict() as needed */}
          <button onClick={() => setIsEditing(true)}>Edit Profile</button>
          <button onClick={logout} style={{ marginLeft: '10px', backgroundColor: 'salmon' }}>Logout</button>
        </div>
      ) : (
        <form onSubmit={handleUpdateProfile}>
           <h3>Edit Profile</h3>
           <div>
             <label htmlFor="profile-username">Username:</label>
             <input
               type="text"
               id="profile-username"
               name="username"
               value={formData.username}
               onChange={handleInputChange}
               disabled={isLoading}
               required
             />
           </div>
           <div>
             <label htmlFor="profile-email">Email:</label>
             <input
               type="email"
               id="profile-email"
               name="email"
               value={formData.email}
               onChange={handleInputChange}
               disabled={isLoading}
               required
             />
           </div>
           <div>
             <label htmlFor="profile-password">New Password (optional):</label>
             <input
               type="password"
               id="profile-password"
               name="password"
               value={formData.password}
               onChange={handleInputChange}
               placeholder="Leave blank to keep current password"
               minLength={formData.password ? 8 : undefined} // Require length only if changing
               disabled={isLoading}
             />
           {formData.password && formData.password.length < 8 && <p style={{color: 'orange', fontSize: '0.8em'}}>Password must be at least 8 characters</p>}
           </div>
           <button type="submit" disabled={isLoading}>
             {isLoading ? 'Saving...' : 'Save Changes'}
           </button>
           <button type="button" onClick={() => { setIsEditing(false); setUpdateStatus({message: '', error: ''}); /* Reset form if desired */ }} disabled={isLoading} style={{ marginLeft: '10px' }}>
             Cancel
           </button>
        </form>
      )}

       {/* Placeholder for Friend Functionality - Add later */}
       {/* <div>
            <h2>Friends</h2>
            <p>(Friend list, requests, search will go here)</p>
       </div> */}
    </div>
  );
};

export default ProfilePage;