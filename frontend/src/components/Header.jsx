import React from 'react';
import { FaNewspaper, FaRobot } from 'react-icons/fa';
import { motion } from 'framer-motion';

const Header = () => {
  return (
    <motion.header 
      className="header"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="header-content">
        <div className="logo">
          <FaNewspaper className="logo-icon" />
          <div>
            <div className="logo-text">AI News Aggregator</div>
            <div className="tagline">
              <FaRobot style={{ marginRight: '0.5rem' }} />
              Powered by Local Gemma 4
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;