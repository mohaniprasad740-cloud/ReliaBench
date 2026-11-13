import React from 'react';
import { useGuidedTour } from './GuidedTourProvider';
import { ChevronRight, ChevronLeft, X, Sparkles, Compass } from 'lucide-react';

export const GuidedTourOverlay: React.FC = () => {
  const {
    isActive,
    currentStep,
    currentStepIndex,
    totalSteps,
    nextStep,
    prevStep,
    skipTour,
    finishTour,
    targetRect,
  } = useGuidedTour();

  if (!isActive || !currentStep) return null;

  const isFinalStep = currentStepIndex === totalSteps - 1;
  const padding = currentStep.highlightPadding ?? 8;

  // Tooltip positioning
  let tooltipStyle: React.CSSProperties = {};

  if (targetRect) {
    const spaceBelow = window.innerHeight - targetRect.bottom;
    const spaceAbove = targetRect.top;
    const placement = currentStep.placement || (spaceBelow > 260 ? 'bottom' : 'top');

    if (placement === 'bottom') {
      tooltipStyle = {
        top: Math.min(window.innerHeight - 300, targetRect.bottom + padding + 12),
        left: Math.max(16, Math.min(window.innerWidth - 380, targetRect.left)),
      };
    } else if (placement === 'top') {
      tooltipStyle = {
        top: Math.max(16, targetRect.top - padding - 220),
        left: Math.max(16, Math.min(window.innerWidth - 380, targetRect.left)),
      };
    } else if (placement === 'left') {
      tooltipStyle = {
        top: Math.max(16, Math.min(window.innerHeight - 260, targetRect.top)),
        left: Math.max(16, targetRect.left - padding - 380),
      };
    } else {
      // right or default
      tooltipStyle = {
        top: Math.max(16, Math.min(window.innerHeight - 260, targetRect.top)),
        left: Math.min(window.innerWidth - 380, targetRect.right + padding + 12),
      };
    }
  } else {
    // Centered fallback if element not yet rendered
    tooltipStyle = {
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
    };
  }

  return (
    <div className="fixed inset-0 z-50 pointer-events-auto">
      {/* Dimmed Overlay with cutout if targetRect exists */}
      <svg className="w-full h-full absolute inset-0 pointer-events-none">
        <defs>
          <mask id="tour-mask">
            <rect x="0" y="0" width="100%" height="100%" fill="white" />
            {targetRect && (
              <rect
                x={targetRect.left - padding}
                y={targetRect.top - padding}
                width={targetRect.width + padding * 2}
                height={targetRect.height + padding * 2}
                rx="6"
                fill="black"
              />
            )}
          </mask>
        </defs>
        <rect
          x="0"
          y="0"
          width="100%"
          height="100%"
          fill="rgba(16, 18, 15, 0.78)"
          mask="url(#tour-mask)"
        />
      </svg>

      {/* Target Focus Border Glow */}
      {targetRect && (
        <div
          className="fixed pointer-events-none border-2 border-[#C7D94C] rounded shadow-[0_0_24px_rgba(199,217,76,0.35)] transition-all duration-300"
          style={{
            top: targetRect.top - padding,
            left: targetRect.left - padding,
            width: targetRect.width + padding * 2,
            height: targetRect.height + padding * 2,
          }}
        />
      )}

      {/* Tooltip Card */}
      <div
        className="fixed z-50 w-88 max-w-[calc(100vw-32px)] bg-[#171A16] border border-[#2D332B] shadow-[4px_4px_0px_0px_#10120F] rounded-lg p-5 font-sans transition-all duration-200"
        style={tooltipStyle}
      >
        {/* Header */}
        <div className="flex justify-between items-start gap-2 mb-2 pb-2 border-b border-[#2D332B]">
          <div className="flex items-center gap-2">
            <Sparkles size={16} className="text-[#C7D94C] shrink-0" />
            <h3 className="font-bold text-sm text-[#E8DDC8] font-mono leading-tight">
              {currentStep.title}
            </h3>
          </div>
          <button
            onClick={skipTour}
            className="text-[#89977A] hover:text-[#E8DDC8] transition-colors p-1"
            title="Skip tour (Esc)"
          >
            <X size={15} />
          </button>
        </div>

        {/* Content */}
        <p className="text-xs text-[#A7A393] leading-relaxed mb-4">
          {currentStep.content}
        </p>

        {/* Progress & Controls */}
        <div className="flex justify-between items-center pt-2 border-t border-[#2D332B]">
          <div className="text-[11px] font-mono text-[#89977A]">
            <span className="text-[#C7D94C] font-bold">{currentStepIndex + 1}</span> of {totalSteps}
          </div>

          <div className="flex items-center gap-2">
            {currentStepIndex > 0 && (
              <button
                onClick={prevStep}
                className="px-2.5 py-1 text-xs font-mono font-bold text-[#A7A393] hover:text-[#E8DDC8] border border-[#2D332B] rounded bg-[#141713] transition-colors flex items-center gap-1 cursor-pointer"
              >
                <ChevronLeft size={13} />
                <span>Prev</span>
              </button>
            )}

            {!isFinalStep ? (
              <button
                onClick={nextStep}
                className="px-3 py-1 text-xs font-mono font-bold text-[#10120F] bg-[#C7D94C] hover:bg-[#d5e855] rounded transition-colors flex items-center gap-1 cursor-pointer"
              >
                <span>Next</span>
                <ChevronRight size={13} />
              </button>
            ) : (
              <button
                onClick={finishTour}
                className="px-3 py-1 text-xs font-mono font-bold text-[#10120F] bg-[#F06B45] hover:bg-[#fa7751] rounded transition-colors flex items-center gap-1 cursor-pointer"
              >
                <span>Finish</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
