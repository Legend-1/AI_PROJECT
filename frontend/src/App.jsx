import React, { useState } from 'react';
import axios from 'axios';
import './styles/App.css';
import Header from './components/Header';
import SearchForm from './components/SearchForm';
import ArticlesGrid from './components/ArticlesGrid';
import SummaryModal from './components/SummaryModal';
import EmptyState from './components/EmptyState';

const API_BASE = process.env.REACT_APP_API_URL || '';

function App() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [summary, setSummary] = useState([]);
  const [summaryLoading, setSummaryLoading] = useState(false);

  const handleSearch = async (searchData) => {
    setLoading(true);
    setError('');
    setArticles([]);

    try {
      const apiResponse = await axios.get(`${API_BASE}/api/search`, {
        params: searchData
      });
      
      setArticles(apiResponse.data.articles || []);
    } catch (err) {
      if (err.response) {
        setError(err.response.data?.error || 'The server rejected the request.');
      } else if (err.request) {
        setError('Cannot reach backend. Start Flask on port 5000 and try again.');
      } else {
        setError('Unexpected error while fetching news.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async (text) => {
    setModalOpen(true);
    setSummaryLoading(true);
    setSummary([]);

    try {
      const response = await axios.post(`${API_BASE}/summarize`, { text });
      setSummary(response.data.summary || []);
    } catch (err) {
      setSummary(['Failed to generate summary. Please try again.']);
    } finally {
      setSummaryLoading(false);
    }
  };

  return (
    <div className="app">
      <Header />
      
      <div className="container">
        <SearchForm onSearch={handleSearch} loading={loading} error={error} />
        
        {loading && (
          <div className="loading-state">
            <div className="spinner-large"></div>
            <p>Searching for articles...</p>
          </div>
        )}
        
        {!loading && articles.length > 0 && (
          <ArticlesGrid articles={articles} onSummarize={handleSummarize} />
        )}
        
        {!loading && !error && articles.length === 0 && (
          <EmptyState />
        )}
      </div>

      <SummaryModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        summary={summary}
        loading={summaryLoading}
      />
    </div>
  );
}

export default App;