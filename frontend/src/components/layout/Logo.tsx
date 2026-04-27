export function Logo({ size = 32 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Background circle */}
      <circle cx="20" cy="20" r="20" fill="#007A5E"/>
      {/* Chart bars - data visualization icon */}
      <rect x="8" y="22" width="5" height="10" rx="1" fill="#FCD116"/>
      <rect x="15" y="16" width="5" height="16" rx="1" fill="white"/>
      <rect x="22" y="12" width="5" height="20" rx="1" fill="#CE1126"/>
      <rect x="29" y="18" width="5" height="14" rx="1" fill="#FCD116"/>
      {/* Trend line */}
      <path d="M10 21 L17 15 L24 11 L31 17" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
      {/* Dot on trend */}
      <circle cx="31" cy="17" r="2" fill="white"/>
    </svg>
  )
}
