import React from 'react';
import { FaNewspaper } from 'react-icons/fa';
import { motion } from 'framer-motion';

const EmptyState = () => {
  return (
    <motion.div
      className="empty-state"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <FaNewspaper />
      <h3>Start Your Search</h3>
      <p>Enter a topic above to discover the latest news articles</p>
    </motion.div>
  );
};

export default EmptyState;