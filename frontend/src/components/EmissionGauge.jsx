import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer
} from 'recharts';

const EmissionGauge = ({ intensity = 0 }) => {

  // ---------------------------------------------
  // Safely handle the incoming prediction
  // ---------------------------------------------

  const numericIntensity = Number(intensity);

  const safeIntensity =
    Number.isFinite(numericIntensity) &&
    numericIntensity >= 0
      ? numericIntensity
      : 0;


  // ---------------------------------------------
  // Dynamic gauge scale
  //
  // We use the current intensity to determine
  // a display range instead of assuming that
  // 5 tCO2e/unit is a universal maximum.
  // ---------------------------------------------

  const maxIntensity =
    safeIntensity > 0
      ? Math.max(safeIntensity * 1.5, 0.01)
      : 0.01;


  const value = Math.min(
    safeIntensity,
    maxIntensity
  );

  const remainder =
    Math.max(
      maxIntensity - value,
      0
    );


  const data = [
    {
      name: 'Intensity',
      value
    },
    {
      name: 'Remaining',
      value: remainder
    }
  ];


  // ---------------------------------------------
  // Display state
  //
  // This is a visual indication only.
  // It is NOT an official emissions rating.
  // ---------------------------------------------

  let intensityColor = '#39ff14';

  if (safeIntensity >= maxIntensity * 0.75) {

    intensityColor = '#ef4444';

  } else if (safeIntensity >= maxIntensity * 0.5) {

    intensityColor = '#eab308';

  }


  const COLORS = [
    intensityColor,
    'rgba(255,255,255,0.1)'
  ];


  return (
    <div className="glass-card p-6 flex flex-col justify-center items-center h-full">

      <h3 className="text-xl font-bold text-blue-100 self-start w-full mb-2">
        Carbon Intensity
      </h3>


      <div className="w-full aspect-square max-h-[200px] relative">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >

          <PieChart>

            <Pie
              data={data}
              cx="50%"
              cy="70%"
              startAngle={180}
              endAngle={0}
              innerRadius="70%"
              outerRadius="90%"
              paddingAngle={0}
              dataKey="value"
              stroke="none"
              cornerRadius={4}
            >

              {data.map(
                (entry, index) => (

                  <Cell
                    key={`cell-${index}`}
                    fill={
                      COLORS[
                        index %
                        COLORS.length
                      ]
                    }
                  />

                )
              )}

            </Pie>

          </PieChart>

        </ResponsiveContainer>


        {/* ---------------------------------------
            Center value
        --------------------------------------- */}

        <div className="absolute inset-x-0 bottom-[10%] flex flex-col items-center">

          <span
            className="text-2xl font-bold text-white"
          >
            {safeIntensity.toFixed(4)}
          </span>

          <span className="text-xs text-blue-200">
            tCO₂e / unit
          </span>

        </div>

      </div>


      {/* -----------------------------------------
          Scale information
      ----------------------------------------- */}

      <div className="text-center mt-2">

        <p className="text-xs text-blue-200/60">

          Display scale: 0 – {maxIntensity.toFixed(4)}

        </p>

      </div>

    </div>
  );
};

export default EmissionGauge;