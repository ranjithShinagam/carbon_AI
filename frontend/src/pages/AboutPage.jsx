import React from 'react';
import { motion } from 'framer-motion';
import { Globe, Shield, TrendingDown } from 'lucide-react';

const AboutPage = () => {
  return (
    <div className="pt-24 pb-16 min-h-screen bg-deep-blue text-soft-white max-w-7xl mx-auto px-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center max-w-3xl mx-auto mb-16"
      >
        <h1 className="text-4xl md:text-5xl font-extrabold mb-6">Pioneering the Future of Carbon Analytics</h1>
        <p className="text-xl text-blue-200/80">
          Our mission is to help heavy industries transition to net-zero through powerful AI models, real-time insights, and predictive tracking.
        </p>
      </motion.div>

      <div className="grid md:grid-cols-3 gap-8 mb-16">
        {[
            { icon: Globe, title: "Global Scale", desc: "Designed to ingest supply chain data from all corners of the world, providing a unified carbon footprint." },
            { icon: Shield, title: "Enterprise Grade", desc: "Highly secure architecture ensuring your proprietary operational data never leaks." },
            { icon: TrendingDown, title: "Actionable AI", desc: "Not just reporting, but predicting. Our XGBoost models simulate scenarios to literally lower emissions." }
        ].map((feat, i) => (
          <motion.div 
            key={i}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.2 }}
            className="glass-card p-8 flex flex-col items-center text-center"
          >
             <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-6">
                <feat.icon className="w-8 h-8 text-neon-green" />
             </div>
             <h3 className="text-xl font-bold mb-4">{feat.title}</h3>
             <p className="text-blue-200/70">{feat.desc}</p>
          </motion.div>
        ))}
      </div>
      
      <div className="glass-card p-12 text-center border border-neon-green/30">
        <h2 className="text-3xl font-bold mb-4">Our Technology</h2>
        <p className="max-w-4xl mx-auto text-blue-100">
          At the core of CarbonAI lies a robust XGBoost Machine Learning pipeline trained on thousands of industrial data points. 
          It rapidly assesses Non-Renewable Energy Ratios against Production Output and Supply Chain Transport to determine accurate Carbon Intensity metrics.
        </p>
      </div>
    </div>
  );
};

export default AboutPage;
