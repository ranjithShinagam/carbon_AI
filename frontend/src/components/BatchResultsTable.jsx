import React, { useMemo, useState } from 'react';
import {
  Download,
  AlertTriangle,
  CheckCircle,
  Database,
  Factory,
  BarChart3
} from 'lucide-react';

const BatchResultsTable = ({ results }) => {
  const [view, setView] = useState('overview');

  if (!results || typeof results !== 'object') {
    return null;
  }

  const predictionSummary =
    results.prediction_summary || {};

  const analytics =
    results.sector_analytics || {};

  const overall =
    analytics.overall || {};

  const sectors =
    analytics.sectors || [];

  const industries =
    analytics.industries || [];

  const metadata =
    results.metadata || {};

  const energyValidation =
    results.energy_validation || {};

  const mapping =
    results.mapping || {};

  const warnings =
    results.warnings || [];

  const errors =
    results.errors || [];


  // --------------------------------------------------
  // Helper
  // --------------------------------------------------

  const number = (value, digits = 2) => {

    const parsed = Number(value);

    if (!Number.isFinite(parsed)) {
      return '—';
    }

    return parsed.toLocaleString(undefined, {
      maximumFractionDigits: digits,
      minimumFractionDigits: digits
    });

  };


  const percentage = (value, digits = 1) => {

    const parsed = Number(value);

    if (!Number.isFinite(parsed)) {
      return '—';
    }

    return `${(parsed * 100).toFixed(digits)}%`;

  };


  // --------------------------------------------------
  // Sector / industry rows
  // --------------------------------------------------

  const sectorRows = useMemo(() => {

    if (Array.isArray(sectors)) {
      return sectors;
    }

    if (
      sectors &&
      typeof sectors === 'object'
    ) {

      return Object.entries(sectors).map(
        ([name, value]) => ({
          sector: name,
          ...(value || {})
        })
      );

    }

    return [];

  }, [sectors]);


  const industryRows = useMemo(() => {

    if (Array.isArray(industries)) {
      return industries;
    }

    if (
      industries &&
      typeof industries === 'object'
    ) {

      return Object.entries(industries).map(
        ([name, value]) => ({
          industry: name,
          ...(value || {})
        })
      );

    }

    return [];

  }, [industries]);


  // --------------------------------------------------
  // CSV export
  // --------------------------------------------------

  const escapeCSV = (value) => {

    if (value === null || value === undefined) {
      return '';
    }

    const stringValue = String(value);

    if (
      stringValue.includes(',') ||
      stringValue.includes('"') ||
      stringValue.includes('\n')
    ) {

      return `"${stringValue.replace(/"/g, '""')}"`;

    }

    return stringValue;

  };


  const downloadCSV = () => {

    let headers = [];
    let rows = [];


    // ----------------------------------------------
    // Sector export
    // ----------------------------------------------

    if (view === 'sectors') {

      headers = [
        'Sector',
        'Records',
        'Average Emissions (tCO2e)',
        'Average Energy (kWh)',
        'Renewable Share',
        'Non-Renewable Share',
        'Production',
        'Transport (km)',
        'Raw Material (kg)',
        'Employment',
        'Carbon Intensity'
      ];


      rows = sectorRows.map((item) => [

        item.sector ??
        item.Sector ??
        item.name ??
        '',

        item.records ??
        item.count ??
        item.total_records ??
        '',

        item.average_emissions ??
        item.avg_emissions ??
        item.average_predicted_co2 ??
        '',

        item.average_total_energy ??
        item.avg_total_energy ??
        '',

        item.average_renewable_share ??
        item.avg_renewable_share ??
        '',

        item.average_nonrenewable_share ??
        item.avg_nonrenewable_share ??
        '',

        item.average_production ??
        item.avg_production ??
        '',

        item.average_transport ??
        item.avg_transport ??
        '',

        item.average_raw_material ??
        item.avg_raw_material ??
        '',

        item.average_employment ??
        item.avg_employment ??
        '',

        item.average_carbon_intensity ??
        item.carbon_intensity ??
        ''

      ]);

    }

    // ----------------------------------------------
    // Industry export
    // ----------------------------------------------

    else if (view === 'industries') {

      headers = [
        'Industry',
        'Records',
        'Average Emissions (tCO2e)',
        'Renewable Share',
        'Non-Renewable Share',
        'Production',
        'Carbon Intensity'
      ];


      rows = industryRows.map((item) => [

        item.industry ??
        item.Industry ??
        item.name ??
        '',

        item.records ??
        item.count ??
        item.total_records ??
        '',

        item.average_emissions ??
        item.avg_emissions ??
        item.average_predicted_co2 ??
        '',

        item.average_renewable_share ??
        item.avg_renewable_share ??
        '',

        item.average_nonrenewable_share ??
        item.avg_nonrenewable_share ??
        '',

        item.average_production ??
        item.avg_production ??
        '',

        item.average_carbon_intensity ??
        item.carbon_intensity ??
        ''

      ]);

    }

    // ----------------------------------------------
    // Overview export
    // ----------------------------------------------

    else {

      headers = [
        'Metric',
        'Value'
      ];


      rows = [

        [
          'Records Processed',
          predictionSummary.records ??
          metadata.final_rows ??
          ''
        ],

        [
          'Average Predicted CO2 (tCO2e)',
          predictionSummary.average_predicted_co2 ??
          ''
        ],

        [
          'Total Predicted CO2 (tCO2e)',
          predictionSummary.total_predicted_co2 ??
          ''
        ],

        [
          'Minimum Predicted CO2 (tCO2e)',
          predictionSummary.minimum_predicted_co2 ??
          ''
        ],

        [
          'Maximum Predicted CO2 (tCO2e)',
          predictionSummary.maximum_predicted_co2 ??
          ''
        ],

        [
          'Average Carbon Intensity',
          overall.average_carbon_intensity ??
          ''
        ],

        [
          'Average Renewable Share',
          overall.average_renewable_share ??
          ''
        ],

        [
          'Average Non-Renewable Share',
          overall.average_nonrenewable_share ??
          ''
        ]

      ];

    }


    const csvContent = [

      headers.map(escapeCSV).join(','),

      ...rows.map(
        row =>
          row.map(escapeCSV).join(',')
      )

    ].join('\n');


    const blob = new Blob(
      [csvContent],
      {
        type: 'text/csv;charset=utf-8;'
      }
    );


    const url =
      URL.createObjectURL(blob);

    const link =
      document.createElement('a');

    link.href = url;

    link.download =
      `carbon_batch_${view}_results.csv`;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    URL.revokeObjectURL(url);

  };


  // --------------------------------------------------
  // Empty result protection
  // --------------------------------------------------

  if (
    !results.success &&
    errors.length > 0
  ) {

    return (

      <div className="glass-card mt-6 p-6">

        <div className="flex items-start">

          <AlertTriangle
            className="w-6 h-6 text-red-400 mr-3"
          />

          <div>

            <h3 className="text-lg font-bold text-white">

              Dataset Processing Failed

            </h3>

            <div className="mt-2 space-y-1">

              {errors.map((error, index) => (

                <p
                  key={index}
                  className="text-sm text-red-300"
                >
                  {typeof error === 'string'
                    ? error
                    : JSON.stringify(error)}
                </p>

              ))}

            </div>

          </div>

        </div>

      </div>

    );

  }


  return (

    <div className="glass-card mt-6 p-6 overflow-hidden">


      {/* ==========================================
          HEADER
      ========================================== */}

      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-6">

        <div>

          <h3 className="text-xl font-bold text-white mb-1">

            Batch Prediction Results

          </h3>

          <p className="text-sm text-gray-400">

            Processed{' '}

            <span className="text-white font-medium">

              {Number(
                metadata.final_rows ??
                predictionSummary.records ??
                0
              ).toLocaleString()}

            </span>{' '}

            operational rows using the XGBoost model.

          </p>

        </div>


        <button
          onClick={downloadCSV}
          className="mt-4 lg:mt-0 flex items-center text-sm bg-white/10 hover:bg-white/20 text-white font-medium py-2 px-4 rounded-lg transition-colors border border-white/5"
        >

          <Download className="w-4 h-4 mr-2" />

          Export CSV

        </button>

      </div>


      {/* ==========================================
          VIEW TABS
      ========================================== */}

      <div className="flex flex-wrap gap-2 mb-6">

        <button
          onClick={() => setView('overview')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center

            ${
              view === 'overview'
                ? 'bg-neon-green text-deep-blue'
                : 'bg-white/5 text-gray-300 hover:bg-white/10'
            }

          `}
        >

          <BarChart3 className="w-4 h-4 mr-2" />

          Overview

        </button>


        <button
          onClick={() => setView('sectors')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center

            ${
              view === 'sectors'
                ? 'bg-neon-green text-deep-blue'
                : 'bg-white/5 text-gray-300 hover:bg-white/10'
            }

          `}
        >

          <Factory className="w-4 h-4 mr-2" />

          Sectors

        </button>


        <button
          onClick={() => setView('industries')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center

            ${
              view === 'industries'
                ? 'bg-neon-green text-deep-blue'
                : 'bg-white/5 text-gray-300 hover:bg-white/10'
            }

          `}
        >

          <Database className="w-4 h-4 mr-2" />

          Industries

        </button>

      </div>


      {/* ==========================================
          OVERVIEW
      ========================================== */}

      {view === 'overview' && (

        <>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">


            <div className="bg-black/20 border border-white/10 rounded-xl p-4">

              <p className="text-xs text-gray-400 uppercase">
                Records
              </p>

              <p className="text-2xl font-bold text-white mt-2">

                {Number(
                  predictionSummary.records ??
                  metadata.final_rows ??
                  0
                ).toLocaleString()}

              </p>

            </div>


            <div className="bg-black/20 border border-white/10 rounded-xl p-4">

              <p className="text-xs text-gray-400 uppercase">
                Average CO₂
              </p>

              <p className="text-2xl font-bold text-neon-green mt-2">

                {number(
                  predictionSummary.average_predicted_co2
                )}

              </p>

              <p className="text-xs text-gray-500 mt-1">
                tCO₂e
              </p>

            </div>


            <div className="bg-black/20 border border-white/10 rounded-xl p-4">

              <p className="text-xs text-gray-400 uppercase">
                Total CO₂
              </p>

              <p className="text-2xl font-bold text-white mt-2">

                {number(
                  predictionSummary.total_predicted_co2
                )}

              </p>

              <p className="text-xs text-gray-500 mt-1">
                tCO₂e
              </p>

            </div>


            <div className="bg-black/20 border border-white/10 rounded-xl p-4">

              <p className="text-xs text-gray-400 uppercase">
                CO₂ Range
              </p>

              <p className="text-lg font-bold text-white mt-2">

                {number(
                  predictionSummary.minimum_predicted_co2
                )}

                {' – '}

                {number(
                  predictionSummary.maximum_predicted_co2
                )}

              </p>

              <p className="text-xs text-gray-500 mt-1">
                tCO₂e
              </p>

            </div>

          </div>


          {/* Overall analytics */}

          <div className="overflow-x-auto rounded-xl border border-white/10">

            <table className="w-full text-sm text-left text-gray-300">

              <thead className="text-xs text-gray-400 uppercase bg-black/40 border-b border-white/10">

                <tr>

                  <th className="px-4 py-3">
                    Metric
                  </th>

                  <th className="px-4 py-3 text-right">
                    Value
                  </th>

                </tr>

              </thead>


              <tbody>

                <tr className="border-b border-white/5">

                  <td className="px-4 py-3">
                    Average Energy
                  </td>

                  <td className="px-4 py-3 text-right">
                    {number(
                      overall.average_energy
                    )} kWh
                  </td>

                </tr>


                <tr className="border-b border-white/5">

                  <td className="px-4 py-3">
                    Average Renewable Share
                  </td>

                  <td className="px-4 py-3 text-right text-neon-green">
                    {percentage(
                      overall.average_renewable_share
                    )}
                  </td>

                </tr>


                <tr className="border-b border-white/5">

                  <td className="px-4 py-3">
                    Average Non-Renewable Share
                  </td>

                  <td className="px-4 py-3 text-right">
                    {percentage(
                      overall.average_nonrenewable_share
                    )}
                  </td>

                </tr>


                <tr className="border-b border-white/5">

                  <td className="px-4 py-3">
                    Average Production
                  </td>

                  <td className="px-4 py-3 text-right">
                    {number(
                      overall.average_production
                    )}
                  </td>

                </tr>


                <tr className="border-b border-white/5">

                  <td className="px-4 py-3">
                    Average Transport
                  </td>

                  <td className="px-4 py-3 text-right">
                    {number(
                      overall.average_transport
                    )} km
                  </td>

                </tr>


                <tr className="border-b border-white/5">

                  <td className="px-4 py-3">
                    Average Raw Material
                  </td>

                  <td className="px-4 py-3 text-right">
                    {number(
                      overall.average_raw_material
                    )} kg
                  </td>

                </tr>


                <tr>

                  <td className="px-4 py-3">
                    Average Carbon Intensity
                  </td>

                  <td className="px-4 py-3 text-right text-neon-green">
                    {number(
                      overall.average_carbon_intensity,
                      6
                    )}
                  </td>

                </tr>

              </tbody>

            </table>

          </div>

        </>

      )}


      {/* ==========================================
          SECTOR TABLE
      ========================================== */}

      {view === 'sectors' && (

        <div className="overflow-x-auto rounded-xl border border-white/10">

          <table className="w-full text-sm text-left text-gray-300">

            <thead className="text-xs text-gray-400 uppercase bg-black/40 border-b border-white/10">

              <tr>

                <th className="px-4 py-3">
                  Sector
                </th>

                <th className="px-4 py-3 text-right">
                  Records
                </th>

                <th className="px-4 py-3 text-right">
                  Avg CO₂
                </th>

                <th className="px-4 py-3 text-right">
                  Renewable
                </th>

                <th className="px-4 py-3 text-right">
                  Non-Renewable
                </th>

                <th className="px-4 py-3 text-right">
                  Production
                </th>

                <th className="px-4 py-3 text-right">
                  Carbon Intensity
                </th>

              </tr>

            </thead>


            <tbody>

              {sectorRows.map((item, index) => {

                const name =
                  item.sector ??
                  item.Sector ??
                  item.name ??
                  `Sector ${index + 1}`;

                const records =
                  item.records ??
                  item.count ??
                  item.total_records ??
                  0;

                const emissions =
                  item.average_emissions ??
                  item.avg_emissions ??
                  item.average_predicted_co2;

                const renewable =
                  item.average_renewable_share ??
                  item.avg_renewable_share;

                const nonrenewable =
                  item.average_nonrenewable_share ??
                  item.avg_nonrenewable_share;

                const production =
                  item.average_production ??
                  item.avg_production;

                const intensity =
                  item.average_carbon_intensity ??
                  item.carbon_intensity;


                return (

                  <tr
                    key={`${name}-${index}`}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors"
                  >

                    <td className="px-4 py-4 font-medium text-white">
                      {name}
                    </td>

                    <td className="px-4 py-4 text-right">
                      {Number(records).toLocaleString()}
                    </td>

                    <td className="px-4 py-4 text-right text-neon-green font-bold">
                      {number(emissions)}
                    </td>

                    <td className="px-4 py-4 text-right">
                      {percentage(renewable)}
                    </td>

                    <td className="px-4 py-4 text-right">
                      {percentage(nonrenewable)}
                    </td>

                    <td className="px-4 py-4 text-right">
                      {number(production)}
                    </td>

                    <td className="px-4 py-4 text-right">
                      {number(intensity, 6)}
                    </td>

                  </tr>

                );

              })}


              {sectorRows.length === 0 && (

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

      )}


      {/* ==========================================
          INDUSTRY TABLE
      ========================================== */}

      {view === 'industries' && (

        <div className="overflow-x-auto rounded-xl border border-white/10">

          <table className="w-full text-sm text-left text-gray-300">

            <thead className="text-xs text-gray-400 uppercase bg-black/40 border-b border-white/10">

              <tr>

                <th className="px-4 py-3">
                  Industry
                </th>

                <th className="px-4 py-3 text-right">
                  Records
                </th>

                <th className="px-4 py-3 text-right">
                  Avg CO₂
                </th>

                <th className="px-4 py-3 text-right">
                  Renewable
                </th>

                <th className="px-4 py-3 text-right">
                  Non-Renewable
                </th>

                <th className="px-4 py-3 text-right">
                  Production
                </th>

                <th className="px-4 py-3 text-right">
                  Carbon Intensity
                </th>

              </tr>

            </thead>


            <tbody>

              {industryRows.map((item, index) => {

                const name =
                  item.industry ??
                  item.Industry ??
                  item.name ??
                  `Industry ${index + 1}`;

                const records =
                  item.records ??
                  item.count ??
                  item.total_records ??
                  0;

                const emissions =
                  item.average_emissions ??
                  item.avg_emissions ??
                  item.average_predicted_co2;

                const renewable =
                  item.average_renewable_share ??
                  item.avg_renewable_share;

                const nonrenewable =
                  item.average_nonrenewable_share ??
                  item.avg_nonrenewable_share;

                const production =
                  item.average_production ??
                  item.avg_production;

                const intensity =
                  item.average_carbon_intensity ??
                  item.carbon_intensity;


                return (

                  <tr
                    key={`${name}-${index}`}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors"
                  >

                    <td className="px-4 py-4 font-medium text-white">
                      {name}
                    </td>

                    <td className="px-4 py-4 text-right">
                      {Number(records).toLocaleString()}
                    </td>

                    <td className="px-4 py-4 text-right text-neon-green font-bold">
                      {number(emissions)}
                    </td>

                    <td className="px-4 py-4 text-right">
                      {percentage(renewable)}
                    </td>

                    <td className="px-4 py-4 text-right">
                      {percentage(nonrenewable)}
                    </td>

                    <td className="px-4 py-4 text-right">
                      {number(production)}
                    </td>

                    <td className="px-4 py-4 text-right">
                      {number(intensity, 6)}
                    </td>

                  </tr>

                );

              })}


              {industryRows.length === 0 && (

                <tr>

                  <td
                    colSpan="7"
                    className="px-4 py-8 text-center text-gray-500"
                  >

                    No industry analytics available.

                  </td>

                </tr>

              )}

            </tbody>

          </table>

        </div>

      )}


      {/* ==========================================
          DATA VALIDATION
      ========================================== */}

      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">


        <div className="bg-black/20 border border-white/10 rounded-xl p-4">

          <div className="flex items-center mb-2">

            {energyValidation.valid ? (

              <CheckCircle className="w-5 h-5 text-neon-green mr-2" />

            ) : (

              <AlertTriangle className="w-5 h-5 text-yellow-400 mr-2" />

            )}

            <h4 className="text-sm font-semibold text-white">

              Energy Validation

            </h4>

          </div>


          <p className="text-xs text-gray-400">

            {energyValidation.checked
              ? energyValidation.valid
                ? 'Renewable + non-renewable energy is consistent with total energy.'
                : 'Some rows contain energy consistency differences.'
              : 'Energy consistency was not checked.'}

          </p>

        </div>


        <div className="bg-black/20 border border-white/10 rounded-xl p-4">

          <h4 className="text-sm font-semibold text-white mb-2">

            Dataset Mapping

          </h4>


          <p className="text-xs text-gray-400">

            {Object.keys(mapping).length}{' '}

            column mappings were successfully identified.

          </p>


          {warnings.length > 0 && (

            <p className="text-xs text-yellow-300 mt-2">

              {warnings.length} warning(s) reported.

            </p>

          )}

        </div>

      </div>

    </div>

  );

};

export default BatchResultsTable;