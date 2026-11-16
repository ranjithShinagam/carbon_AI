import React, { createContext, useContext, useState } from 'react';

const PredictionContext = createContext({
  currentPrediction: null,
  setCurrentPrediction: () => {},
});

export const usePrediction = () => useContext(PredictionContext);

export const PredictionProvider = ({ children }) => {
  const [currentPrediction, setCurrentPrediction] = useState(null);

  return (
    <PredictionContext.Provider value={{ currentPrediction, setCurrentPrediction }}>
      {children}
    </PredictionContext.Provider>
  );
};