import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { TourStep, TOUR_STEPS } from './tourSteps';

interface GuidedTourContextType {
  isActive: boolean;
  currentStepIndex: number;
  currentStep: TourStep | null;
  totalSteps: number;
  startTour: (stepIndex?: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  skipTour: () => void;
  finishTour: () => void;
  targetRect: DOMRect | null;
}

const GuidedTourContext = createContext<GuidedTourContextType | null>(null);

const STORAGE_KEY = 'reliabench_tour_completed';

export const GuidedTourProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isActive, setIsActive] = useState<boolean>(false);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);

  const location = useLocation();
  const navigate = useNavigate();

  const currentStep = isActive && TOUR_STEPS[currentStepIndex] ? TOUR_STEPS[currentStepIndex] : null;

  // Check target element position
  const updateTargetRect = useCallback(() => {
    if (!currentStep) {
      setTargetRect(null);
      return;
    }

    const el = document.querySelector(currentStep.targetSelector);
    if (el) {
      const rect = el.getBoundingClientRect();
      setTargetRect(rect);
    } else {
      // Graceful fallback: centered if target not immediately found
      setTargetRect(null);
    }
  }, [currentStep]);

  // Navigate to step's route if different from current path
  useEffect(() => {
    if (!isActive || !currentStep) return;

    if (location.pathname !== currentStep.route) {
      navigate(currentStep.route);
    }
  }, [isActive, currentStep, location.pathname, navigate]);

  // When step or route changes, locate target element
  useEffect(() => {
    if (!isActive || !currentStep) return;

    let timeoutId: any;
    let attempts = 0;

    const findAndScroll = () => {
      const el = document.querySelector(currentStep.targetSelector);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        updateTargetRect();
      } else if (attempts < 8) {
        attempts += 1;
        timeoutId = setTimeout(findAndScroll, 120);
      } else {
        // Target missing: fallback to center placement gracefully without breaking tour
        setTargetRect(null);
      }
    };

    findAndScroll();

    window.addEventListener('resize', updateTargetRect);
    window.addEventListener('scroll', updateTargetRect, true);

    return () => {
      clearTimeout(timeoutId);
      window.removeEventListener('resize', updateTargetRect);
      window.removeEventListener('scroll', updateTargetRect, true);
    };
  }, [isActive, currentStep, location.pathname, updateTargetRect]);

  // Handle keyboard controls (Escape to close, Left/Right for prev/next)
  useEffect(() => {
    if (!isActive) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        skipTour();
      } else if (e.key === 'ArrowRight') {
        nextStep();
      } else if (e.key === 'ArrowLeft') {
        prevStep();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isActive, currentStepIndex]);

  const startTour = (stepIndex = 0) => {
    setCurrentStepIndex(stepIndex);
    setIsActive(true);
  };

  const nextStep = () => {
    if (currentStepIndex < TOUR_STEPS.length - 1) {
      setCurrentStepIndex((prev) => prev + 1);
    } else {
      finishTour();
    }
  };

  const prevStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex((prev) => prev - 1);
    }
  };

  const skipTour = () => {
    setIsActive(false);
    localStorage.setItem(STORAGE_KEY, 'true');
  };

  const finishTour = () => {
    setIsActive(false);
    localStorage.setItem(STORAGE_KEY, 'true');
  };

  return (
    <GuidedTourContext.Provider
      value={{
        isActive,
        currentStepIndex,
        currentStep,
        totalSteps: TOUR_STEPS.length,
        startTour,
        nextStep,
        prevStep,
        skipTour,
        finishTour,
        targetRect,
      }}
    >
      {children}
    </GuidedTourContext.Provider>
  );
};

export const useGuidedTour = () => {
  const ctx = useContext(GuidedTourContext);
  if (!ctx) {
    throw new Error('useGuidedTour must be used within GuidedTourProvider');
  }
  return ctx;
};
