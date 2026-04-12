import React, { useState } from 'react';
import { FaSearch, FaTag, FaCalendar, FaGlobe } from 'react-icons/fa';
import { motion } from 'framer-motion';

const SearchForm = ({ onSearch, loading, error }) => {
  const [formData, setFormData] = useState({
    topic: '',
    date: '',
    country: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.topic.trim()) {
      onSearch(formData);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const today = new Date().toISOString().split('T')[0];

  return (
    <motion.div 
      className="search-section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <h2 className="search-title">
        <FaSearch /> Discover News
      </h2>

      {error && (
        <motion.div 
          className="alert alert-error"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <i className="fas fa-exclamation-circle"></i>
          {error}
        </motion.div>
      )}

      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-row">
          <div className="form-group">
            <label>
              <FaTag /> Topic
            </label>
            <input
              type="text"
              name="topic"
              placeholder="e.g., Artificial Intelligence, Climate Change..."
              value={formData.topic}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>
              <FaCalendar /> From Date
            </label>
            <input
              type="date"
              name="date"
              max={today}
              value={formData.date}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>
              <FaGlobe /> Country
            </label>
            <select name="country" value={formData.country} onChange={handleChange}>
              <option value="">All Countries</option>
              <option value="USA">USA</option>
              <option value="UK">UK</option>
              <option value="India">India</option>
              <option value="Canada">Canada</option>
              <option value="Australia">Australia</option>
            </select>
          </div>
        </div>

        <motion.button
          type="submit"
          className="btn"
          disabled={loading}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <FaSearch />
          {loading ? 'Searching...' : 'Search News'}
        </motion.button>
      </form>
    </motion.div>
  );
};

export default SearchForm;