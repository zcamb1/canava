export default function RunningLine({ svg_props, circle_props }) {
  return (
    <svg className={svg_props} viewBox="0 0 32 32">
      <circle
        cx="16"
        cy="16"
        r="14" // Center and radius, slightly smaller to fit within 32x32
        fill="none"
        stroke="#3B82F6" // Light blue from bot icon
        strokeWidth="2"
        strokeDasharray="20 68" /* Dash length 20, gap 68 (circumference 2*pi*r approx 88) */
        strokeDashoffset="0"
        className={circle_props}
      />
    </svg>
  );
}
