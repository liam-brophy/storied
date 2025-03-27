import React, { useState } from 'react';
import { useAuth, } from '../../contexts/AuthContext';
import axios from 'axios';


const FriendSearch = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const {addFriendtoUser} = useAuth()

    const handleSearch = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`/api/users/search?q=${searchQuery}`);
            setSearchResults(response.data);
        } catch (error) {
            setError(error.response?.data?.error || 'Failed to perform search.');
        } finally {
            setLoading(false);
        }
    };


const handleSend = async (friend_id) => {
   addFriendtoUser(friend_id)
}



    return (
        <div>
            <input
                type="text"
                placeholder="Search for users..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button onClick={handleSearch} disabled={loading}>
                {loading ? 'Searching...' : 'Search'}
            </button>

            {error && <p style={{ color: 'red' }}>Error: {error}</p>}

            {loading && <p>Searching...</p>}

            {searchResults.length > 0 && (
                <ul>
                    {searchResults.map(user => (
                        <li key={user.id}>
                            {user.username}
                            <button onClick={() => handleSend(user.id)} >Send Request</button>
                            {/* if friend */}
                            {/* ternary button */}
                            {/* Add a button here to send a friend request */}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default FriendSearch;