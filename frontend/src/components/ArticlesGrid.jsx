import React from 'react';
import ArticleCard from './ArticleCard';

const ArticlesGrid = ({ articles, onSummarize }) => {
  return (
    <div className="articles-grid">
      {articles.map((article, index) => (
        <ArticleCard
          key={index}
          article={article}
          onSummarize={onSummarize}
          index={index}
        />
      ))}
    </div>
  );
};

export default ArticlesGrid;