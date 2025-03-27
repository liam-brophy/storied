import { BooksContext } from '../contexts/BookContext';
import { createContext, useContext, useReducer } from 'react';

export const useBooks = () => {
    const context = useContext(BooksContext);
    if (context === undefined) {
        throw new Error('useBooks must be used within a BooksProvider');
    }
    return context;
};