import React from 'react';
import { motion } from 'framer-motion';
import { Cloud, Zap, Users } from 'lucide-react';

const DashboardCards = ({ results }) => {
  if (!results) return null;

  const cards = [
    {
      title: "Predicted CO₂ Emission",
      value: `${results.predicted_co2_emission.toFixed(2)} tCO₂e`,
      icon: <Cloud className="w-8 h-8 text-neon-green" />,
      delay: 0.1
    },
    {
      title: "Carbon Intensity",
      value: `${results.carbon_intensity.toFixed(4)} tCO₂e / unit`,
      icon: <Zap className="w-8 h-8 text-blue-400" />,
      delay: 0.2
    },
    {
      title: "Energy per Employee",
      value: `${results.energy_per_employee.toFixed(2)} kWh`,
      icon: <Users className="w-8 h-8 text-purple-400" />,
      delay: 0.3
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      {cards.map((card, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: card.delay }}
          className="glass-card p-6 flex flex-col justify-between relative overflow-hidden group hover:border-neon-green/30 transition-colors"
        >
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            {React.cloneElement(card.icon, { className: "w-24 h-24" })}
          </div>
          
          <div className="mb-4">
            <div className="bg-white/10 p-3 rounded-xl inline-block mb-4">
              {card.icon}
            </div>
            <h4 className="text-gray-400 text-sm font-medium uppercase tracking-wider">{card.title}</h4>
          </div>
          
          <div>
            <span className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-blue-200">
              {card.value}
            </span>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default DashboardCards;
