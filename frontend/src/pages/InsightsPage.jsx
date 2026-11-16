import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';

import {
  Database,
  TrendingUp,
  BarChart3,
  Activity,
  Zap,
  Factory,
  Users,
  Leaf,
} from 'lucide-react';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

import { getDatasetInsights, formatApiError } from '../api/api';

const getGroupName = (item, fallback) =>
  item?.sector ??
  item?.Sector ??
  item?.industry ??
  item?.Industry ??
  item?.name ??
  fallback;

const getRecords = (item) =>
  item?.records ?? item?.count ?? item?.total_records ?? 0;

const getEmissions = (item) =>
  item?.average_emissions ??
  item?.avg_emissions ??
  item?.average_predicted_co2 ??
  item?.average_carbon_emission ??
  item?.total_emissions ??
  0;

const getRenewableShare = (item) =>
  item?.average_renewable_share ??
  item?.avg_renewable_share ??
  item?.renewable_energy_ratio ??
  0;

const getNonRenewableShare = (item) =>
  item?.average_nonrenewable_share ??
  item?.avg_nonrenewable_share ??
  item?.nonrenewable_energy_ratio ??
  0;

const getProduction = (item) =>
  item?.average_production ?? item?.avg_production ?? 0;

const getCarbonIntensity = (item) =>
  item?.average_carbon_intensity ?? item?.carbon_intensity ?? 0;

const InsightsPage = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        const response = await getDatasetInsights();
        setInsights(response);
      } catch (err) {
        console.error('Failed to load dataset insights:', err);
        setError(formatApiError(err, 'Failed to load dataset insights.'));
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, []);

  const analytics = insights?.analytics || insights || {};
  const overall = analytics.overall || {};
  const sectors = Array.isArray(analytics.sectors) ? analytics.sectors : [];
  const industries = Array.isArray(analytics.industries)
    ? analytics.industries
    : [];

  const sectorChartData = useMemo(() => {
    return sectors
      .map((sector, index) => ({
        name: getGroupName(sector, `Sector ${index + 1}`),
        emissions: Number(getEmissions(sector)),
        records: Number(getRecords(sector)),
      }))
      .filter((item) => Number.isFinite(item.emissions))
      .sort((a, b) => b.emissions - a.emissions);
  }, [sectors]);

  const industryChartData = useMemo(() => {
    return industries
      .map((industry, index) => ({
        name: getGroupName(industry, `Industry ${index + 1}`),
        emissions: Number(getEmissions(industry)),
        records: Number(getRecords(industry)),
      }))
      .filter((item) => Number.isFinite(item.emissions))
      .sort((a, b) => b.emissions - a.emissions);
  }, [industries]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[calc(100vh-80px)]">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-neon-green" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-[calc(100vh-80px)]">
        <div className="glass-card p-8 text-center">
          <p className="text-red-400">{error}</p>
          <p className="text-gray-500 text-sm mt-2">
            Make sure the backend is running and the dataset is available.
          </p>
        </div>
      </div>
    );
  }

  if (!insights) {
    return null;
  }

  const getNumber = (value, decimals = 2) => {
    const number = Number(value);
    if (!Number.isFinite(number)) return '—';
    return number.toLocaleString(undefined, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  };

  const getInteger = (value) => {
    const number = Number(value);
    if (!Number.isFinite(number)) return '—';
    return number.toLocaleString(undefined, { maximumFractionDigits: 0 });
  };

  const getPercentage = (value, decimals = 1) => {
    const number = Number(value);
    if (!Number.isFinite(number)) return '—';
    return `${(number * 100).toFixed(decimals)}%`;
  };

  const totalRecords = Number(
    analytics.total_records ??
      overall.total_records ??
      overall.records ??
      insights.metadata?.final_rows ??
      sectors.reduce(
        (sum, s) => sum + Number(s?.records ?? s?.count ?? s?.total_records ?? 0),
        0
      )
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-extrabold text-white mb-4">
          Dataset <span className="text-neon-green">Insights</span>
        </h1>
        <p className="text-xl text-gray-300 mb-10">
          Analytics generated from the carbon emission dataset and the XGBoost
          prediction pipeline.
        </p>
      </motion.div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl"
        >
          <div className="flex items-center text-neon-green mb-4">
            <Database className="w-8 h-8 mr-3" />
            <h3 className="text-lg font-semibold text-white">Total Records</h3>
          </div>
          <p className="text-3xl font-bold text-white">
            {getInteger(totalRecords)}
          </p>
          <p className="text-sm text-gray-400 mt-2">Dataset records processed</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl"
        >
          <div className="flex items-center text-blue-400 mb-4">
            <TrendingUp className="w-8 h-8 mr-3" />
            <h3 className="text-lg font-semibold text-white">Average CO₂</h3>
          </div>
          <p className="text-3xl font-bold text-white">
            {getNumber(
              overall.average_emissions ?? overall.average_predicted_co2
            )}
          </p>
          <p className="text-sm text-gray-400 mt-2">Average predicted tCO₂e</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl"
        >
          <div className="flex items-center text-purple-400 mb-4">
            <Activity className="w-8 h-8 mr-3" />
            <h3 className="text-lg font-semibold text-white">Average Output</h3>
          </div>
          <p className="text-3xl font-bold text-white">
            {getNumber(overall.average_production, 0)}
          </p>
          <p className="text-sm text-gray-400 mt-2">Production units</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl"
        >
          <div className="flex items-center text-yellow-400 mb-4">
            <BarChart3 className="w-8 h-8 mr-3" />
            <h3 className="text-lg font-semibold text-white">
              Carbon Intensity
            </h3>
          </div>
          <p className="text-3xl font-bold text-white">
            {getNumber(overall.average_carbon_intensity, 6)}
          </p>
          <p className="text-sm text-gray-400 mt-2">
            tCO₂e per production unit
          </p>
        </motion.div>
      </div>

      {/* Energy / Sustainability Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-5">
          <div className="flex items-center mb-3">
            <Zap className="w-5 h-5 text-yellow-400 mr-2" />
            <span className="text-sm text-gray-400">Average Energy</span>
          </div>
          <p className="text-2xl font-bold text-white">
            {getNumber(overall.average_energy)}{' '}
            <span className="text-sm text-gray-400">kWh</span>
          </p>
        </div>

        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-5">
          <div className="flex items-center mb-3">
            <Leaf className="w-5 h-5 text-neon-green mr-2" />
            <span className="text-sm text-gray-400">Renewable Share</span>
          </div>
          <p className="text-2xl font-bold text-neon-green">
            {getPercentage(overall.average_renewable_share)}
          </p>
        </div>

        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-5">
          <div className="flex items-center mb-3">
            <Zap className="w-5 h-5 text-orange-400 mr-2" />
            <span className="text-sm text-gray-400">Non-Renewable Share</span>
          </div>
          <p className="text-2xl font-bold text-white">
            {getPercentage(overall.average_nonrenewable_share)}
          </p>
        </div>

        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-5">
          <div className="flex items-center mb-3">
            <Users className="w-5 h-5 text-purple-400 mr-2" />
            <span className="text-sm text-gray-400">Average Employment</span>
          </div>
          <p className="text-2xl font-bold text-white">
            {getNumber(overall.average_employment, 0)}
          </p>
        </div>
      </div>

      {/* Sector Emissions Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-8"
      >
        <div className="flex items-center mb-6">
          <Factory className="w-6 h-6 text-neon-green mr-3" />
          <div>
            <h2 className="text-2xl font-bold text-white">Sector Emissions</h2>
            <p className="text-sm text-gray-400">
              Average predicted emissions by sector
            </p>
          </div>
        </div>

        <div className="h-[380px] w-full">
          {sectorChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={sectorChartData}
                margin={{ top: 10, right: 30, left: 10, bottom: 70 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.08)"
                />
                <XAxis
                  dataKey="name"
                  stroke="#ccc"
                  angle={-35}
                  textAnchor="end"
                  interval={0}
                  tick={{ fill: '#ccc', fontSize: 11 }}
                />
                <YAxis stroke="#ccc" tick={{ fill: '#ccc' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                    color: '#fff',
                  }}
                  formatter={(value) => [
                    `${getNumber(value)} tCO₂e`,
                    'Average Emissions',
                  ]}
                />
                <Bar dataKey="emissions" radius={[4, 4, 0, 0]}>
                  {sectorChartData.map((_, index) => (
                    <Cell key={`sector-${index}`} fill="#39FF14" />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500">
              No sector analytics available.
            </div>
          )}
        </div>
      </motion.div>

      {/* Sector Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 mb-8"
      >
        <h2 className="text-2xl font-bold text-white mb-6">Sector Analytics</h2>

        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-300">
            <thead className="text-xs text-gray-400 uppercase bg-black/20 border-b border-white/10">
              <tr>
                <th className="px-4 py-3">Sector</th>
                <th className="px-4 py-3 text-right">Records</th>
                <th className="px-4 py-3 text-right">Avg CO₂</th>
                <th className="px-4 py-3 text-right">Renewable</th>
                <th className="px-4 py-3 text-right">Non-Renewable</th>
                <th className="px-4 py-3 text-right">Production</th>
                <th className="px-4 py-3 text-right">Intensity</th>
              </tr>
            </thead>
            <tbody>
              {sectors.map((sector, index) => {
                const name = getGroupName(sector, `Sector ${index + 1}`);
                return (
                  <tr
                    key={`${name}-${index}`}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors"
                  >
                    <td className="px-4 py-4 font-medium text-white">
                      {name}
                    </td>
                    <td className="px-4 py-4 text-right">
                      {getInteger(getRecords(sector))}
                    </td>
                    <td className="px-4 py-4 text-right font-bold text-neon-green">
                      {getNumber(getEmissions(sector))}
                    </td>
                    <td className="px-4 py-4 text-right">
                      {getPercentage(getRenewableShare(sector))}
                    </td>
                    <td className="px-4 py-4 text-right">
                      {getPercentage(getNonRenewableShare(sector))}
                    </td>
                    <td className="px-4 py-4 text-right">
                      {getNumber(getProduction(sector))}
                    </td>
                    <td className="px-4 py-4 text-right">
                      {getNumber(getCarbonIntensity(sector), 6)}
                    </td>
                  </tr>
                );
              })}

              {sectors.length === 0 && (
                <tr>
                  <td
                    colSpan="7"
                    className="px-4 py-8 text-center text-gray-500"
                  >
                    No sector analytics available.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Industry Emissions Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6"
      >
        <div className="flex items-center mb-6">
          <Factory className="w-6 h-6 text-blue-400 mr-3" />
          <div>
            <h2 className="text-2xl font-bold text-white">
              Industry Analytics
            </h2>
            <p className="text-sm text-gray-400">
              Average predicted emissions across industries
            </p>
          </div>
        </div>

        <div className="h-[380px] w-full">
          {industryChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={industryChartData}
                margin={{ top: 10, right: 30, left: 10, bottom: 70 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.08)"
                />
                <XAxis
                  dataKey="name"
                  stroke="#ccc"
                  angle={-35}
                  textAnchor="end"
                  interval={0}
                  tick={{ fill: '#ccc', fontSize: 11 }}
                />
                <YAxis stroke="#ccc" tick={{ fill: '#ccc' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                    color: '#fff',
                  }}
                  formatter={(value) => [
                    `${getNumber(value)} tCO₂e`,
                    'Average Emissions',
                  ]}
                />
                <Bar dataKey="emissions" radius={[4, 4, 0, 0]}>
                  {industryChartData.map((_, index) => (
                    <Cell key={`industry-${index}`} fill="#60a5fa" />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500">
              No industry analytics available.
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default InsightsPage;