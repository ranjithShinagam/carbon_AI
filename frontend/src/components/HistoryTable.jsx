import React from 'react';
import { History } from 'lucide-react';

const HistoryTable = ({ history }) => {
  if (!history || history.length === 0) return null;

  return (
    <div className="glass-card p-6 mt-6">
      <div className="flex items-center mb-4">
        <History className="w-5 h-5 text-neon-green mr-2" />
        <h3 className="text-lg font-bold text-white">Recent Predictions</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left text-gray-300">
          <thead className="text-xs text-gray-400 uppercase bg-black/30 border-b border-white/10">
            <tr>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Sector / Details</th>
              <th className="px-4 py-3 text-right">Energy (kWh)</th>
              <th className="px-4 py-3 text-right">Production</th>
              <th className="px-4 py-3 text-right">Renewable</th>
              <th className="px-4 py-3 text-right">Predicted CO₂</th>
            </tr>
          </thead>

          <tbody>
            {history.map((item) => {
              const sectorLabel = [item.sector, item.industry_sector, item.transport_mode]
                .filter(Boolean)
                .join(' · ');

              return (
                <tr key={item.id} className="border-b border-white/5 hover:bg-white/5">
                  <td className="px-4 py-3 text-xs text-gray-400 whitespace-nowrap">
                    {new Date(item.created_at).toLocaleString()}
                  </td>

                  <td className="px-4 py-3 text-xs text-blue-200">
                    {sectorLabel || <span className="text-gray-500">General</span>}
                  </td>

                  <td className="px-4 py-3 text-right">
                    {Number(item.total_energy).toLocaleString()}
                  </td>

                  <td className="px-4 py-3 text-right">
                    {Number(item.production_output).toLocaleString()}
                  </td>

                  <td className="px-4 py-3 text-right text-neon-green">
                    {(Number(item.renewable_energy_ratio) * 100).toFixed(1)}%
                  </td>

                  <td className="px-4 py-3 text-right font-bold text-white">
                    {Number(item.predicted_co2_emission).toFixed(2)} tCO₂e
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default HistoryTable;