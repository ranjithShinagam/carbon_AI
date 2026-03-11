import React, { useState } from 'react';
import { motion } from 'framer-motion';

const defaultValues = {
  total_energy: 50000,
  nonrenewable_energy: 35000,
  production_output: 10000,
  transport_distance: 500,
  raw_material_usage: 20000,
  employment_count: 50
};

const labels = {
  total_energy: { label: "Total Energy (kWh)", max: 200000 },
  nonrenewable_energy: { label: "Non-Renewable Energy (kWh)", max: 200000 },
  production_output: { label: "Production Output (Units)", max: 50000 },
  transport_distance: { label: "Transport Distance (km)", max: 5000 },
  raw_material_usage: { label: "Raw Material Usage (kg)", max: 100000 },
  employment_count: { label: "Employees", max: 500 }
};

const PredictionForm = ({ onPredict, isLoading, onChange }) => {
  const [formData, setFormData] = useState(defaultValues);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const newData = { ...formData, [name]: parseFloat(value) };
    setFormData(newData);
    // Real-time propagation for scenario simulation
    if (onChange) onChange(newData);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onPredict(formData);
  };

  return (
    <motion.form 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      onSubmit={handleSubmit} 
      className="glass-card p-6 h-full flex flex-col justify-between"
    >
      <div>
        <h3 className="text-xl font-bold mb-6 text-neon-green">Operational Inputs</h3>
        
        <div className="space-y-6">
          {Object.entries(labels).map(([key, config]) => (
            <div key={key}>
              <div className="flex justify-between mb-2">
                <label className="text-sm font-medium text-blue-100">{config.label}</label>
                <span className="text-sm text-neon-green font-mono bg-white/5 px-2 py-0.5 rounded">
                  {formData[key].toLocaleString()}
                </span>
              </div>
              <input
                type="range"
                name={key}
                min="0"
                max={config.max}
                value={formData[key]}
                onChange={handleChange}
                className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-neon-green"
              />
            </div>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className={`w-full mt-8 py-3 px-4 rounded-xl font-bold transition-all ${
          isLoading 
            ? 'bg-blue-500/50 cursor-not-allowed text-white' 
            : 'bg-neon-green text-deep-blue hover:scale-[1.02] shadow-[0_0_20px_rgba(57,255,20,0.2)] hover:shadow-[0_0_30px_rgba(57,255,20,0.4)]'
        }`}
      >
        {isLoading ? 'Simulating...' : 'Predict Emissions'}
      </button>
    </motion.form>
  );
};

export default PredictionForm;
