import React, { useState } from 'react';
import axios from 'axios';
import Header from './components/header';
import SearchForm from './components/SearchForm';
import ArticlesGrid from './components/ArticlesGrid';
import SummaryModal from './components/SummaryModal';
import EmptyState from './components/EmptyState';

const API_URL = 'http://localhost:5000';

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
      const formData = new FormData();
      formData.append('topic', searchData.topic);
      if (searchData.date) formData.append('date', searchData.date);
      if (searchData.country) formData.append('country', searchData.country);

      const response = await axios.post(`${API_URL}/search`, formData);
      
      // Parse HTML response to extract articles
      const parser = new DOMParser();
      const doc = parser.parseFromString(response.data, 'text/html');
      
      // Check for error message
      const errorDiv = doc.querySelector('.alert-error');
      if (errorDiv) {
        setError(errorDiv.textContent.trim());
        return;
      }

      // Extract articles (we'll use the API directly instead)
      const apiResponse = await axios.get(`${API_URL}/api/search`, {
        params: searchData
      });
      
      setArticles(apiResponse.data.articles || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch news. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async (text) => {
    setModalOpen(true);
    setSummaryLoading(true);
    setSummary([]);

    try {
      const response = await axios.post(`${API_URL}/summarize`, { text });
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