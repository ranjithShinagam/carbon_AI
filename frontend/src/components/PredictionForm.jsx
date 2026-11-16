import React, { useEffect, useState } from 'react';
import { Sliders, Zap, Factory, Truck, Package, Users, Layers } from 'lucide-react';
import { getPredictionOptions } from '../api/api';

const PredictionForm = ({ onPredict, isLoading, onChange }) => {
  const [formData, setFormData] = useState({
    total_energy: 250000,
    renewable_energy: 50000,
    nonrenewable_energy: 200000,
    production_output: 1500,
    transport_distance: 400,
    raw_material_usage: 4000,
    employment_count: 150,
    sector: '',
    industry_sector: '',
    transport_mode: '',
  });

  const [options, setOptions] = useState({
    sectors: ['Agriculture', 'Energy', 'IT', 'Manufacturing', 'Transport'],
    industry_sectors: ['Automotive Industry', 'Cement Production', 'Logistics', 'Steel Manufacturing'],
    transport_modes: ['Air', 'Rail', 'Ship', 'Truck'],
  });

  useEffect(() => {
    getPredictionOptions()
      .then((data) => {
        if (data && (data.sectors || data.industry_sectors || data.transport_modes)) {
          setOptions({
            sectors: data.sectors || [],
            industry_sectors: data.industry_sectors || [],
            transport_modes: data.transport_modes || [],
          });
        }
      })
      .catch((err) => console.warn('Using default prediction options:', err));
  }, []);

  const handleNumericChange = (name, rawValue) => {
    const numValue = Math.max(0, Number(rawValue));
    const updated = { ...formData };

    if (name === 'total_energy') {
      updated.total_energy = numValue;
      const clampedRenewable = Math.min(updated.renewable_energy, numValue);
      updated.renewable_energy = clampedRenewable;
      updated.nonrenewable_energy = Math.max(0, numValue - clampedRenewable);
    } else if (name === 'renewable_energy') {
      const clamped = Math.min(numValue, updated.total_energy);
      updated.renewable_energy = clamped;
      updated.nonrenewable_energy = Math.max(0, updated.total_energy - clamped);
    } else if (name === 'nonrenewable_energy') {
      const clamped = Math.min(numValue, updated.total_energy);
      updated.nonrenewable_energy = clamped;
      updated.renewable_energy = Math.max(0, updated.total_energy - clamped);
    } else {
      updated[name] = numValue;
    }

    setFormData(updated);
    if (onChange) onChange(updated);
  };

  const handleSelectChange = (name, value) => {
    const updated = { ...formData, [name]: value };
    setFormData(updated);
    if (onChange) onChange(updated);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!onPredict) return;
    onPredict({
      ...formData,
      sector: formData.sector || null,
      industry_sector: formData.industry_sector || null,
      transport_mode: formData.transport_mode || null,
    });
  };

  const renewableRatio =
    formData.total_energy > 0
      ? ((formData.renewable_energy / formData.total_energy) * 100).toFixed(1)
      : '0.0';

  const nonRenewableRatio =
    formData.total_energy > 0
      ? ((formData.nonrenewable_energy / formData.total_energy) * 100).toFixed(1)
      : '0.0';

  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <h3 className="text-xl font-bold text-white mb-6 flex items-center">
        <Sliders className="w-5 h-5 mr-2 text-neon-green" />
        Operational Inputs
      </h3>

      <form onSubmit={handleSubmit} className="space-y-5 flex-1 flex flex-col justify-between">
        <div className="space-y-5">
          {/* Optional Sector-Wise Details */}
          <div className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-neon-green flex items-center">
                <Layers className="w-3.5 h-3.5 mr-1.5" />
                Sector Details (Optional)
              </span>
              <span className="text-[11px] text-gray-400">Leave blank if general</span>
            </div>

            <div>
              <label className="text-xs text-gray-300 block mb-1">Sector</label>
              <select
                value={formData.sector}
                onChange={(e) => handleSelectChange('sector', e.target.value)}
                className="w-full bg-deep-blue border border-white/15 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-neon-green"
              >
                <option value="">-- Any / Not Specified --</option>
                {options.sectors.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs text-gray-300 block mb-1">Industry Sector</label>
              <select
                value={formData.industry_sector}
                onChange={(e) => handleSelectChange('industry_sector', e.target.value)}
                className="w-full bg-deep-blue border border-white/15 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-neon-green"
              >
                <option value="">-- Any / Not Specified --</option>
                {options.industry_sectors.map((ind) => (
                  <option key={ind} value={ind}>{ind}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs text-gray-300 block mb-1">Supply Chain Transport Mode</label>
              <select
                value={formData.transport_mode}
                onChange={(e) => handleSelectChange('transport_mode', e.target.value)}
                className="w-full bg-deep-blue border border-white/15 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-neon-green"
              >
                <option value="">-- Any / Not Specified --</option>
                {options.transport_modes.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Total Energy */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <label className="text-gray-300 flex items-center">
                <Zap className="w-4 h-4 mr-2 text-yellow-400" />
                Total Energy Consumption
              </label>
              <span className="text-white font-mono">
                {formData.total_energy.toLocaleString()} kWh
              </span>
            </div>
            <input
              type="range"
              min="1000"
              max="500000"
              step="1000"
              value={formData.total_energy}
              onChange={(e) => handleNumericChange('total_energy', e.target.value)}
              className="w-full accent-neon-green"
            />
          </div>

          {/* Renewable Energy */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <label className="text-gray-300">
                Renewable Energy ({renewableRatio}%)
              </label>
              <span className="text-neon-green font-mono">
                {formData.renewable_energy.toLocaleString()} kWh
              </span>
            </div>
            <input
              type="range"
              min="0"
              max={formData.total_energy}
              step="1000"
              value={formData.renewable_energy}
              onChange={(e) => handleNumericChange('renewable_energy', e.target.value)}
              className="w-full accent-neon-green"
            />
          </div>

          {/* Non-Renewable Energy */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <label className="text-gray-300">
                Non-Renewable Energy ({nonRenewableRatio}%)
              </label>
              <span className="text-orange-400 font-mono">
                {formData.nonrenewable_energy.toLocaleString()} kWh
              </span>
            </div>
            <input
              type="range"
              min="0"
              max={formData.total_energy}
              step="1000"
              value={formData.nonrenewable_energy}
              onChange={(e) => handleNumericChange('nonrenewable_energy', e.target.value)}
              className="w-full accent-orange-400"
            />
          </div>

          {/* Production Output */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <label className="text-gray-300 flex items-center">
                <Factory className="w-4 h-4 mr-2 text-blue-400" />
                Production Output
              </label>
              <span className="text-white font-mono">
                {formData.production_output.toLocaleString()} units
              </span>
            </div>
            <input
              type="range"
              min="10"
              max="10000"
              step="10"
              value={formData.production_output}
              onChange={(e) => handleNumericChange('production_output', e.target.value)}
              className="w-full accent-blue-400"
            />
          </div>

          {/* Transport Distance */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <label className="text-gray-300 flex items-center">
                <Truck className="w-4 h-4 mr-2 text-purple-400" />
                Supply Chain Transport
              </label>
              <span className="text-white font-mono">
                {formData.transport_distance.toLocaleString()} km
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="5000"
              step="10"
              value={formData.transport_distance}
              onChange={(e) => handleNumericChange('transport_distance', e.target.value)}
              className="w-full accent-purple-400"
            />
          </div>

          {/* Raw Material Usage */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <label className="text-gray-300 flex items-center">
                <Package className="w-4 h-4 mr-2 text-emerald-400" />
                Raw Material Usage
              </label>
              <span className="text-white font-mono">
                {formData.raw_material_usage.toLocaleString()} kg
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="20000"
              step="50"
              value={formData.raw_material_usage}
              onChange={(e) => handleNumericChange('raw_material_usage', e.target.value)}
              className="w-full accent-emerald-400"
            />
          </div>

          {/* Employment Count */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <label className="text-gray-300 flex items-center">
                <Users className="w-4 h-4 mr-2 text-cyan-400" />
                Employment Count
              </label>
              <span className="text-white font-mono">
                {formData.employment_count.toLocaleString()}
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="2000"
              step="5"
              value={formData.employment_count}
              onChange={(e) => handleNumericChange('employment_count', e.target.value)}
              className="w-full accent-cyan-400"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className={`w-full py-3 mt-6 rounded-xl font-bold transition-all ${
            isLoading
              ? 'bg-white/10 text-gray-400 cursor-not-allowed'
              : 'bg-neon-green text-deep-blue hover:bg-green-400 shadow-[0_0_20px_rgba(57,255,20,0.3)]'
          }`}
        >
          {isLoading ? 'Predicting...' : 'Predict Emissions'}
        </button>
      </form>
    </div>
  );
};

export default PredictionForm;