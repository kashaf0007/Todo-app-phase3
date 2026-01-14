import { useState, useEffect } from 'react';

// Custom hook for responsive design
export const useMediaQuery = (width) => {
  const [targetReached, setTargetReached] = useState(false);

  useEffect(() => {
    const updateTarget = (e) => {
      setTargetReached(e.matches);
    };

    const media = window.matchMedia(`(max-width: ${width}px)`);

    media.addEventListener('change', updateTarget);
    setTargetReached(media.matches);

    return () => media.removeEventListener('change', updateTarget);
  }, [width]);

  return targetReached;
};