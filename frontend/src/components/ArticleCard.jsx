import React from 'react';
import { FaClock, FaUser, FaMagic, FaExternalLinkAlt, FaImage } from 'react-icons/fa';
import { motion } from 'framer-motion';

const ArticleCard = ({ article, onSummarize, index }) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    return dateString.split('T')[0];
  };

  return (
    <motion.article
      className="article-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      whileHover={{ y: -5 }}
    >
      {article.urlToImage ? (
        <img
          src={article.urlToImage}
          alt={article.title}
          className="article-image"
          onError={(e) => {
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'flex';
          }}
        />
      ) : null}
      
      <div
        className="article-image-placeholder"
        style={{ display: article.urlToImage ? 'none' : 'flex' }}
      >
        <FaImage />
      </div>

      <div className="article-content">
        <div className="article-source">
          {article.source?.name || 'Unknown Source'}
        </div>

        <h3 className="article-title">{article.title}</h3>

        <p className="article-description">
          {article.description || 'No description available.'}
        </p>

        <div className="article-meta">
          <span>
            <FaClock /> {formatDate(article.publishedAt)}
          </span>
          {article.author && (
            <span>
              <FaUser /> {article.author}
            </span>
          )}
        </div>

        <div className="article-actions">
          <motion.button
            className="btn-secondary"
            onClick={() => onSummarize(article.description || article.title)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <FaMagic /> AI Summary
          </motion.button>
          <motion.a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <FaExternalLinkAlt /> Read More
          </motion.a>
        </div>
      </div>
    </motion.article>
  );
};

export default ArticleCard;