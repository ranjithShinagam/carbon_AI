import React, { useEffect, useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

import {
  Factory,
  Truck,
  Building2,
  Zap,
  Package,
  Users,
  Fuel,
  TrendingDown,
  BarChart3,
  Leaf,
  Database,
  AlertCircle,
} from 'lucide-react';

import { getSectorInsights, formatApiError } from '../api/api';

const getSectorIcon = (sectorName) => {
  const name = String(sectorName || '').toLowerCase();

  if (name.includes('logistic') || name.includes('transport')) {
    return <Truck className="w-8 h-8" />;
  }
  if (
    name.includes('cement') ||
    name.includes('building') ||
    name.includes('construction')
  ) {
    return <Building2 className="w-8 h-8" />;
  }
  if (
    name.includes('energy') ||
    name.includes('power') ||
    name.includes('electric')
  ) {
    return <Zap className="w-8 h-8" />;
  }
  if (
    name.includes('automotive') ||
    name.includes('vehicle') ||
    name.includes('car')
  ) {
    return <Truck className="w-8 h-8" />;
  }
  return <Factory className="w-8 h-8" />;
};

const getSectorGradient = (index) => {
  const gradients = [
    'from-blue-500 to-blue-700',
    'from-emerald-500 to-emerald-700',
    'from-purple-500 to-purple-700',
    'from-orange-500 to-orange-700',
    'from-cyan-500 to-cyan-700',
    'from-indigo-500 to-indigo-700',
  ];
  return gradients[index % gradients.length];
};

const getNumericValue = (item, keys, fallback = 0) => {
  for (const key of keys) {
    const value = item?.[key];
    if (
      value !== undefined &&
      value !== null &&
      Number.isFinite(Number(value))
    ) {
      return Number(value);
    }
  }
  return fallback;
};

const formatNumber = (value, decimals = 2) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return number.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

const formatInteger = (value) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return number.toLocaleString(undefined, { maximumFractionDigits: 0 });
};

const formatPercentage = (value, decimals = 1) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return `${(number * 100).toFixed(decimals)}%`;
};

const MetricCard = ({ icon, label, value, unit, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay, duration: 0.3 }}
    className="bg-white/5 border border-white/10 rounded-xl p-4 flex items-center space-x-4 hover:bg-white/10 transition-colors"
  >
    <div className="p-3 bg-white/5 rounded-lg text-neon-green">{icon}</div>
    <div>
      <p className="text-sm text-gray-400">{label}</p>
      <p className="text-xl font-bold text-white tracking-wide">
        {formatNumber(value)}
        {unit && <span className="text-sm text-gray-400 ml-1">{unit}</span>}
      </p>
    </div>
  </motion.div>
);

const SectorAnalysisPage = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeSector, setActiveSector] = useState(null);

  useEffect(() => {
    const fetchSectorInsights = async () => {
      try {
        const response = await getSectorInsights();
        setInsights(response);
      } catch (err) {
        console.error('Failed to load sector insights:', err);
        setError(formatApiError(err, 'Failed to load sector analytics.'));
      } finally {
        setLoading(false);
      }
    };

    fetchSectorInsights();
  }, []);

  const sectors = useMemo(() => {
    if (!insights) return [];
    const rawSectors = insights.sectors;
    if (Array.isArray(rawSectors)) return rawSectors;
    if (rawSectors && typeof rawSectors === 'object') {
      return Object.entries(rawSectors).map(([name, data]) => ({
        sector: name,
        ...(data || {}),
      }));
    }
    return [];
  }, [insights]);

  useEffect(() => {
    if (sectors.length > 0 && activeSector === null) {
      setActiveSector(0);
    }
  }, [sectors, activeSector]);

  if (loading) {
    return (
      <div className="min-h-screen bg-deep-blue flex items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-neon-green" />
          <p className="text-gray-400 mt-4">Loading sector analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-deep-blue flex items-center justify-center px-4">
        <div className="glass-card max-w-lg w-full p-8 text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">
            Unable to Load Sector Analytics
          </h2>
          <p className="text-red-300 text-sm">{error}</p>
          <p className="text-gray-500 text-sm mt-3">
            Make sure the Carbon AI backend is running and the dataset is
            available.
          </p>
        </div>
      </div>
    );
  }

  if (!insights || sectors.length === 0) {
    return (
      <div className="min-h-screen bg-deep-blue flex items-center justify-center">
        <div className="text-center">
          <Database className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white">
            No Sector Data Available
          </h2>
          <p className="text-gray-500 mt-2">
            The backend did not return sector analytics.
          </p>
        </div>
      </div>
    );
  }

  const activeData = sectors[activeSector];
  const activeSectorName =
    activeData?.sector ??
    activeData?.Sector ??
    activeData?.name ??
    `Sector ${activeSector + 1}`;

  const records = getNumericValue(activeData, [
    'records',
    'count',
    'total_records',
  ]);
  const averageEnergy = getNumericValue(activeData, [
    'average_energy',
    'avg_energy',
    'average_total_energy',
    'avg_total_energy',
  ]);
  const averageProduction = getNumericValue(activeData, [
    'average_production',
    'avg_production',
  ]);
  const averageTransport = getNumericValue(activeData, [
    'average_transport',
    'avg_transport',
    'average_transport_distance',
  ]);
  const averageRawMaterial = getNumericValue(activeData, [
    'average_raw_material',
    'avg_raw_material',
  ]);
  const averageEmployment = getNumericValue(activeData, [
    'average_employment',
    'avg_employment',
  ]);
  const averageRenewableShare = getNumericValue(activeData, [
    'average_renewable_share',
    'avg_renewable_share',
    'renewable_energy_ratio',
  ]);
  const averageNonRenewableShare = getNumericValue(activeData, [
    'average_nonrenewable_share',
    'avg_nonrenewable_share',
    'nonrenewable_energy_ratio',
  ]);
  const averageCarbonIntensity = getNumericValue(activeData, [
    'average_carbon_intensity',
    'carbon_intensity',
  ]);
  const averageEmissions = getNumericValue(activeData, [
    'average_emissions',
    'avg_emissions',
    'average_predicted_co2',
    'average_carbon_emission',
  ]);

  return (
    <div className="min-h-screen bg-deep-blue text-soft-white py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-extrabold mb-4">
            Sector <span className="text-neon-green">Analytics</span>
          </h1>
          <p className="text-xl text-blue-200/80 max-w-3xl mx-auto">
            Explore real emission, energy, production and operational metrics
            calculated from the Carbon AI dataset.
          </p>
        </motion.div>

        <div className="flex flex-wrap justify-center gap-4 mb-12">
          {sectors.map((sector, index) => {
            const name =
              sector?.sector ??
              sector?.Sector ??
              sector?.name ??
              `Sector ${index + 1}`;
            const icon = getSectorIcon(name);

            return (
              <button
                key={`${name}-${index}`}
                type="button"
                onClick={() => setActiveSector(index)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-full font-semibold transition-all duration-300 ${
                  activeSector === index
                    ? 'bg-neon-green text-deep-blue shadow-[0_0_20px_rgba(57,255,20,0.4)] scale-105'
                    : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10'
                }`}
              >
                {React.cloneElement(icon, { className: 'w-5 h-5' })}
                <span>{name}</span>
              </button>
            );
          })}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={activeSector}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.4 }}
            className="grid lg:grid-cols-3 gap-8"
          >
            <div className="lg:col-span-2 space-y-6">
              <div
                className={`p-6 rounded-2xl bg-gradient-to-br ${getSectorGradient(
                  activeSector
                )} border border-white/20 relative overflow-hidden`}
              >
                <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" />
                <div className="relative z-10 flex items-center space-x-4">
                  <div className="p-4 rounded-xl bg-white/20 text-white">
                    {getSectorIcon(activeSectorName)}
                  </div>
                  <div>
                    <h2 className="text-3xl font-extrabold text-white">
                      {activeSectorName}
                    </h2>
                    <p className="text-gray-200">Real dataset analytics</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <MetricCard
                  icon={<BarChart3 />}
                  label="Average CO₂ Emissions"
                  value={averageEmissions}
                  unit="tCO₂e"
                  delay={0.1}
                />
                <MetricCard
                  icon={<Zap />}
                  label="Average Energy"
                  value={averageEnergy}
                  unit="kWh"
                  delay={0.2}
                />
                <MetricCard
                  icon={<Package />}
                  label="Average Production"
                  value={averageProduction}
                  delay={0.3}
                />
                <MetricCard
                  icon={<Truck />}
                  label="Average Transport"
                  value={averageTransport}
                  unit="km"
                  delay={0.4}
                />
                <MetricCard
                  icon={<Fuel />}
                  label="Non-Renewable Share"
                  value={averageNonRenewableShare * 100}
                  unit="%"
                  delay={0.5}
                />
                <MetricCard
                  icon={<Leaf />}
                  label="Renewable Share"
                  value={averageRenewableShare * 100}
                  unit="%"
                  delay={0.6}
                />
                <MetricCard
                  icon={<TrendingDown />}
                  label="Raw Material Usage"
                  value={averageRawMaterial}
                  unit="kg"
                  delay={0.7}
                />
                <MetricCard
                  icon={<Users />}
                  label="Average Employment"
                  value={averageEmployment}
                  delay={0.8}
                />
              </div>

              <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-white">
                      Carbon Intensity
                    </h3>
                    <p className="text-sm text-gray-400">
                      Average predicted emissions per production unit
                    </p>
                  </div>
                  <BarChart3 className="w-7 h-7 text-neon-green" />
                </div>
                <p className="text-3xl font-bold text-neon-green">
                  {formatNumber(averageCarbonIntensity, 6)}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  tCO₂e / production unit
                </p>
              </div>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-neon-green/10 rounded-full blur-3xl -mr-10 -mt-10" />
              <div className="flex items-center space-x-3 mb-6 relative z-10">
                <Factory className="w-8 h-8 text-neon-green" />
                <h3 className="text-2xl font-bold text-white">
                  Sector Summary
                </h3>
              </div>

              <div className="space-y-6 relative z-10">
                <div>
                  <p className="text-sm text-gray-400 mb-1">
                    Records in Dataset
                  </p>
                  <p className="text-2xl font-bold text-white">
                    {formatInteger(records)}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-400 mb-1">
                    Average Predicted CO₂
                  </p>
                  <p className="text-2xl font-bold text-neon-green">
                    {formatNumber(averageEmissions)} tCO₂e
                  </p>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <p className="text-sm text-gray-400">Renewable Energy</p>
                    <p className="text-sm font-semibold text-neon-green">
                      {formatPercentage(averageRenewableShare)}
                    </p>
                  </div>
                  <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-neon-green rounded-full transition-all"
                      style={{
                        width: `${Math.min(
                          Math.max(averageRenewableShare * 100, 0),
                          100
                        )}%`,
                      }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <p className="text-sm text-gray-400">
                      Non-Renewable Energy
                    </p>
                    <p className="text-sm font-semibold text-white">
                      {formatPercentage(averageNonRenewableShare)}
                    </p>
                  </div>
                  <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-orange-400 rounded-full transition-all"
                      style={{
                        width: `${Math.min(
                          Math.max(averageNonRenewableShare * 100, 0),
                          100
                        )}%`,
                      }}
                    />
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10">
                  <div className="flex items-start">
                    <Database className="w-5 h-5 text-blue-400 mr-3 mt-0.5" />
                    <div>
                      <p className="text-sm font-semibold text-white">
                        Data Source
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Metrics are calculated from the dataset processed by the
                        Carbon AI analytics pipeline.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default SectorAnalysisPage;