import { CornerTicks } from "./CornerTicks";

export const Panel = ({ title, children, className = "", testId }) => (
  <div
    data-testid={testId}
    className={`relative border border-white/15 bg-black/80 backdrop-blur-md p-5 sm:p-6 transition-all duration-200 hover:border-white/30 hover:shadow-[0_0_20px_rgba(255,255,255,0.05)] h-full ${className}`}
  >
    <CornerTicks />
    {title && (
      <h2 className="text-xl sm:text-2xl font-bold tracking-tight uppercase font-mono text-white mb-4">
        {title}
      </h2>
    )}
    {children}
  </div>
);
