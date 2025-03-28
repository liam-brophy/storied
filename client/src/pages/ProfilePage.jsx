import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import FriendList from '../components/friends/FriendList';
import FriendRequests from '../components/friends/FriendRequests';
import FriendSearch from '../components/friends/FriendSearch';
import './ProfilePage.css';

const ProfilePage = () => {
  const { user, logout, updateUserProfile, deleteUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    password: '',
  });
  const [updateStatus, setUpdateStatus] = useState({ message: '', error: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);

  React.useEffect(() => {
    if (user) {
      setFormData((prev) => ({ ...prev, username: user.username, email: user.email }));
    }
  }, [user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
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
    if (formData.password) {
      dataToUpdate.password = formData.password;
    }

    if (Object.keys(dataToUpdate).length === 0) {
      setUpdateStatus({ message: 'No changes detected.', error: '' });
      setIsLoading(false);
      setIsEditing(false);
      return;
    }

    try {
      const result = await updateUserProfile(dataToUpdate);
      setUpdateStatus({ message: result.message || 'Profile updated successfully!', error: '' });
      setIsEditing(false);
      setFormData((prev) => ({ ...prev, password: '' }));
    } catch (err) {
      setUpdateStatus({ message: '', error: err.response?.data?.error || 'Failed to update profile.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAccount = () => {
    setShowDeleteConfirmation(true);
  };

  const confirmDeleteAccount = async () => {
    setIsDeleting(true);
    try {
      await deleteUser();
    } catch (error) {
      setUpdateStatus({ message: '', error: error.response?.data?.error || 'Failed to delete account.' });
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirmation(false);
    }
  };

  const cancelDeleteAccount = () => {
    setShowDeleteConfirmation(false);
  };

  if (!user) {
    return <p>Loading user profile or not logged in...</p>;
  }

  return (
    <div className="profile-page">
      <div className="profile-container">
        <h1 className="profile-title">Your Account</h1>
        {updateStatus.message && <p style={{ color: 'green' }}>{updateStatus.message}</p>}
        {updateStatus.error && <p style={{ color: 'red' }}>{updateStatus.error}</p>}

        {!isEditing ? (
          <div>
            <div className="profile-info">
              <strong>Username:</strong> {user.username}
            </div>
            <div className="profile-info">
              <strong>Email:</strong> {user.email}
            </div>
            <div className="profile-info">
              <strong>Joined:</strong> {new Date(user.created_at).toLocaleDateString()}
            </div>

            <div className="profile-buttons">
              <button className="profile-button profile-button--edit" onClick={() => setIsEditing(true)}>
                Edit Profile
              </button>
              <button className="profile-button profile-button--logout" onClick={logout}>
                Logout
              </button>
              <button className="profile-button profile-button--delete" onClick={handleDeleteAccount}>
                Delete Account
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleUpdateProfile} className="profile-edit-form">
            <h3>Edit Profile</h3>
            <div className="profile-form-group">
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
            <div className="profile-form-group">
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
            <div className="profile-form-group">
              <label htmlFor="profile-password">New Password (optional):</label>
              <input
                type="password"
                id="profile-password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Leave blank to keep current password"
                minLength={formData.password ? 8 : undefined}
                disabled={isLoading}
              />
              {formData.password && formData.password.length < 8 && (
                <p>Password must be at least 8 characters</p>
              )}
            </div>
            <div className="profile-form-actions">
              <button type="submit" className="profile-form-button profile-form-button--save" disabled={isLoading}>
                {isLoading ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                type="button"
                className="profile-form-button profile-form-button--cancel"
                onClick={() => {
                  setIsEditing(false);
                  setUpdateStatus({ message: '', error: '' });
                }}
                disabled={isLoading}
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        {/* Friend Functionality Module */}
        <div className="profile-friends-module">
          <h2>Friends</h2>
          <div className="profile-friend-search-container">
            <FriendSearch />
          </div>
          <div className="profile-friends-columns">
            <div className="profile-friends-column">
              <h3>My Friends</h3>
              <FriendList />
            </div>
            <div className="profile-friends-column">
              <h3>Friend Requests</h3>
              <FriendRequests />
            </div>
          </div>
        </div>

        {showDeleteConfirmation && (
          <div className="profile-delete-modal">
            <div className="profile-delete-modal-content">
              <p>Are you sure you want to delete your account? This action cannot be undone.</p>
              <div className="profile-delete-modal-buttons">
                <button
                  className="profile-delete-modal-button profile-delete-modal-button--confirm"
                  onClick={confirmDeleteAccount}
                  disabled={isDeleting}
                >
                  {isDeleting ? 'Deleting...' : 'Yes, Delete My Account'}
                </button>
                <button
                  className="profile-delete-modal-button profile-delete-modal-button--cancel"
                  onClick={cancelDeleteAccount}
                  disabled={isDeleting}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfilePage;