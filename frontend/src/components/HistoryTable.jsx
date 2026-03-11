import React from 'react';
import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';

const HistoryTable = ({ history }) => {
  if (!history || history.length === 0) return null;

  return (
    <div className="glass-card mt-8 p-6 overflow-hidden">
      <h3 className="text-xl font-bold mb-6 text-white flex items-center">
        <Clock className="w-5 h-5 mr-3 text-neon-green" /> 
        Your Prediction History
      </h3>
      <div className="overflow-x-auto relative">
        <table className="w-full text-sm text-left text-blue-100">
          <thead className="text-xs text-blue-200 uppercase bg-white/5">
            <tr>
              <th scope="col" className="py-3 px-4">Date</th>
              <th scope="col" className="py-3 px-4">Energy (kWh)</th>
              <th scope="col" className="py-3 px-4">Production</th>
              <th scope="col" className="py-3 px-4 font-bold text-neon-green">Predicted CO₂</th>
              <th scope="col" className="py-3 px-4 text-white">Intensity</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item, index) => (
              <motion.tr 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.1 }}
                key={item.id} 
                className="border-b border-white/5 hover:bg-white/5 transition-colors"
              >
                <td className="py-4 px-4 whitespace-nowrap">
                  {new Date(item.created_at).toLocaleDateString()}
                </td>
                <td className="py-4 px-4">{(item.total_energy + item.nonrenewable_energy).toLocaleString()}</td>
                <td className="py-4 px-4">{item.production_output.toLocaleString()}</td>
                <td className="py-4 px-4 font-bold text-neon-green">{item.predicted_co2_emission?.toFixed(2)} t</td>
                <td className="py-4 px-4 text-white">{item.carbon_intensity?.toFixed(3)}</td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default HistoryTable;
