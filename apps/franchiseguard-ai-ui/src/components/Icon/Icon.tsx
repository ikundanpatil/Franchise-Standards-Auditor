// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import type { IconName } from '../../types';

export interface IconProps extends Omit<React.SVGProps<SVGSVGElement>, 'name'> {
	name: IconName;
	/** Pixel size for width + height. Defaults to 20. */
	size?: number;
}

/** Icons drawn filled rather than stroked. */
const FILLED: ReadonlySet<IconName> = new Set<IconName>(['sparkle', 'sparkles', 'star', 'flag']);

/** Single source of truth for every glyph, on a 24×24 grid. */
const SHAPES: Record<IconName, React.ReactNode> = {
	'shield-check': (
		<>
			<path d="M12 3l7 3v5c0 4.6-3 7.7-7 9-4-1.3-7-4.4-7-9V6l7-3z" />
			<path d="M9 12l2 2 4-4" />
		</>
	),
	shield: <path d="M12 3l7 3v5c0 4.6-3 7.7-7 9-4-1.3-7-4.4-7-9V6l7-3z" />,
	bell: (
		<>
			<path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6z" />
			<path d="M10 20a2 2 0 0 0 4 0" />
		</>
	),
	'alert-triangle': (
		<>
			<path d="M12 4l9 15H3l9-15z" />
			<path d="M12 10v4" />
			<path d="M12 17h.01" />
		</>
	),
	'alert-octagon': (
		<>
			<path d="M8 3h8l5 5v8l-5 5H8l-5-5V8l5-5z" />
			<path d="M12 8v5" />
			<path d="M12 16h.01" />
		</>
	),
	'clipboard-clock': (
		<>
			<path d="M15 4h3v16H6V4h3" />
			<path d="M9 3h6v3H9z" />
			<circle cx="12" cy="13" r="3.6" />
			<path d="M12 11.4v1.8l1.3.9" />
		</>
	),
	'clipboard-check': (
		<>
			<path d="M15 4h3v16H6V4h3" />
			<path d="M9 3h6v3H9z" />
			<path d="M9 13l2 2 4-4" />
		</>
	),
	storefront: (
		<>
			<path d="M4 20V9l8-5 8 5v11" />
			<path d="M3 20h18" />
			<path d="M9 20v-5h6v5" />
			<path d="M9 10h.01M15 10h.01" />
		</>
	),
	camera: (
		<>
			<path d="M4 8h3l1.8-2h6.4L17 8h3v11H4z" />
			<circle cx="12" cy="13" r="3.6" />
		</>
	),
	image: (
		<>
			<rect x="4" y="5" width="16" height="14" rx="2" />
			<circle cx="9" cy="10" r="1.6" />
			<path d="M5 17l4.5-4.5 3 3L16 11l3 3.2" />
		</>
	),
	video: (
		<>
			<rect x="3" y="6" width="12" height="12" rx="2" />
			<path d="M15 10l6-3v10l-6-3z" />
		</>
	),
	sparkle: <path d="M12 3l1.8 4.7L18.5 9.5 13.8 11.3 12 16l-1.8-4.7L5.5 9.5l4.7-1.8z" />,
	sparkles: (
		<>
			<path d="M11 3l1.4 3.6L16 8l-3.6 1.4L11 13l-1.4-3.6L6 8l3.6-1.4z" />
			<path d="M18 13l.8 2 2 .8-2 .8L18 19l-.8-2-2-.8 2-.8z" />
		</>
	),
	home: (
		<>
			<path d="M4 11l8-7 8 7" />
			<path d="M6 10v9h12v-9" />
		</>
	),
	'clipboard-list': (
		<>
			<rect x="6" y="4" width="12" height="16" rx="2" />
			<path d="M9 3h6v3.5H9z" />
			<path d="M9 12h6M9 15.5h4" />
		</>
	),
	chart: (
		<>
			<path d="M5 19V5M5 19h14" />
			<rect x="8" y="11" width="3" height="5" />
			<rect x="14" y="7" width="3" height="9" />
		</>
	),
	'chart-line': (
		<>
			<path d="M5 19V5M5 19h14" />
			<path d="M7 15l3.5-4 3 2L20 7" />
		</>
	),
	user: (
		<>
			<circle cx="12" cy="8" r="3.6" />
			<path d="M5.5 20c1.6-4 11.4-4 13 0" />
		</>
	),
	users: (
		<>
			<circle cx="9" cy="8" r="3.2" />
			<path d="M3.5 20c1.4-3.6 9.6-3.6 11 0" />
			<path d="M16 5.2a3.2 3.2 0 0 1 0 5.6M17.5 20c-.3-1.6-1-2.9-2-3.8" />
		</>
	),
	'chevron-right': <path d="M9 6l6 6-6 6" />,
	'chevron-left': <path d="M15 6l-6 6 6 6" />,
	'chevron-down': <path d="M6 9l6 6 6-6" />,
	'arrow-up-right': (
		<>
			<path d="M7 17L17 7" />
			<path d="M8 7h9v9" />
		</>
	),
	droplet: <path d="M12 3s6.5 7.5 6.5 12a6.5 6.5 0 0 1-13 0C5.5 10.5 12 3 12 3z" />,
	glove: (
		<path d="M7 11V7a1.6 1.6 0 0 1 3.2 0v3M10.2 10V5a1.6 1.6 0 0 1 3.2 0v5M13.4 10V6.5a1.6 1.6 0 0 1 3.2 0V13a6 6 0 0 1-6 6h-.4a5 5 0 0 1-4.4-2.6L4.2 14c-.5-.9.4-1.9 1.4-1.5l1.4.6" />
	),
	'price-tag': (
		<>
			<path d="M4 13l7-7 8.5 8.5-7 7L4 13z" />
			<circle cx="9.5" cy="9.5" r="1.3" />
		</>
	),
	broom: (
		<>
			<path d="M15 4l-6 6" />
			<path d="M8.5 9.5l6 6" />
			<path d="M14.5 15.5L9 21c-2 .5-4-1.5-3.5-3.5l5.5-5.5" />
		</>
	),
	thermometer: (
		<>
			<path d="M12 4a2 2 0 0 1 2 2v8a4 4 0 1 1-4 0V6a2 2 0 0 1 2-2z" />
			<path d="M12 10v5" />
		</>
	),
	bug: (
		<>
			<rect x="8" y="7" width="8" height="12" rx="4" />
			<path d="M9 4l1.5 2M15 4l-1.5 2M4 10h4M16 10h4M4 15h4M16 15h4M4 19l4-2M20 19l-4-2" />
		</>
	),
	fingerprint: (
		<>
			<path d="M6 11a6 6 0 0 1 12 0v2" />
			<path d="M9 12a3 3 0 0 1 6 0c0 3-.5 5-1 6.5" />
			<path d="M12 12v4.5" />
			<path d="M6.5 15.5c.4 1.6.4 3.2 0 4.5M17.5 16c-.3 1.4-.8 2.7-1.4 3.8" />
		</>
	),
	mail: (
		<>
			<rect x="3" y="5" width="18" height="14" rx="2" />
			<path d="M4 7l8 6 8-6" />
		</>
	),
	lock: (
		<>
			<rect x="5" y="10" width="14" height="10" rx="2" />
			<path d="M8 10V8a4 4 0 0 1 8 0v2" />
			<path d="M12 14v2.5" />
		</>
	),
	check: <path d="M5 12l4.5 4.5L19 7" />,
	'check-circle': (
		<>
			<circle cx="12" cy="12" r="9" />
			<path d="M8 12l2.5 2.5L16 9" />
		</>
	),
	x: <path d="M6 6l12 12M18 6L6 18" />,
	'x-circle': (
		<>
			<circle cx="12" cy="12" r="9" />
			<path d="M9 9l6 6M15 9l-6 6" />
		</>
	),
	clock: (
		<>
			<circle cx="12" cy="12" r="8.5" />
			<path d="M12 7v5.3l3.4 2" />
		</>
	),
	calendar: (
		<>
			<rect x="4" y="5" width="16" height="16" rx="2" />
			<path d="M4 9h16M9 3v4M15 3v4" />
		</>
	),
	'map-pin': (
		<>
			<path d="M12 21c4.5-4.3 7-7.6 7-11a7 7 0 1 0-14 0c0 3.4 2.5 6.7 7 11z" />
			<circle cx="12" cy="10" r="2.6" />
		</>
	),
	download: (
		<>
			<path d="M12 4v11" />
			<path d="M7 11l5 5 5-5" />
			<path d="M5 20h14" />
		</>
	),
	share: (
		<>
			<circle cx="6" cy="12" r="2.4" />
			<circle cx="17" cy="6" r="2.4" />
			<circle cx="17" cy="18" r="2.4" />
			<path d="M8.2 10.8l6.6-3.6M8.2 13.2l6.6 3.6" />
		</>
	),
	scale: (
		<>
			<path d="M12 4v16M7 20h10" />
			<path d="M6 7h12M6 7l-3 6a3 3 0 0 0 6 0zM18 7l3 6a3 3 0 0 1-6 0z" />
		</>
	),
	gavel: (
		<>
			<path d="M9 11l4-4M7.5 9.5l4 4" />
			<path d="M12.5 6.5l5 5M14 5l5 5" />
			<path d="M10 13l-5 5M4 21h7" />
		</>
	),
	flag: <path d="M6 3v18M6 4h11l-2 4 2 4H6z" />,
	refresh: (
		<>
			<path d="M20 11a8 8 0 0 0-14-4.5L4 8" />
			<path d="M4 4v4h4" />
			<path d="M4 13a8 8 0 0 0 14 4.5L20 16" />
			<path d="M20 20v-4h-4" />
		</>
	),
	search: (
		<>
			<circle cx="11" cy="11" r="6.5" />
			<path d="M16 16l4 4" />
		</>
	),
	filter: <path d="M4 6h16l-6 7v6l-4-2v-4z" />,
	plus: <path d="M12 5v14M5 12h14" />,
	settings: (
		<>
			<circle cx="12" cy="12" r="3.2" />
			<path d="M12 3l1.4 2.6 2.9-.6 .6 2.9L21 12l-2.1 1.1-.6 2.9-2.9-.6L12 21l-1.4-2.6-2.9.6-.6-2.9L3 12l2.1-1.1.6-2.9 2.9.6z" />
		</>
	),
	logout: (
		<>
			<path d="M15 5H6a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h9" />
			<path d="M11 12h9M17 8l4 4-4 4" />
		</>
	),
	'trending-up': (
		<>
			<path d="M4 16l5-5 3.5 3.5L20 7" />
			<path d="M14 7h6v6" />
		</>
	),
	'trending-down': (
		<>
			<path d="M4 8l5 5 3.5-3.5L20 17" />
			<path d="M14 17h6v-6" />
		</>
	),
	target: (
		<>
			<circle cx="12" cy="12" r="8.5" />
			<circle cx="12" cy="12" r="4.5" />
			<circle cx="12" cy="12" r="1" />
		</>
	),
	layers: (
		<>
			<path d="M12 3l9 5-9 5-9-5z" />
			<path d="M3 13l9 5 9-5" />
		</>
	),
	'file-text': (
		<>
			<path d="M7 3h7l4 4v14H7z" />
			<path d="M14 3v4h4" />
			<path d="M10 12h6M10 16h6" />
		</>
	),
	brain: (
		<>
			<path d="M9.5 5A3 3 0 0 0 6 8a2.6 2.6 0 0 0-1 5 3 3 0 0 0 4.5 3.5V5z" />
			<path d="M14.5 5A3 3 0 0 1 18 8a2.6 2.6 0 0 1 1 5 3 3 0 0 1-4.5 3.5V5z" />
			<path d="M12 5v14" />
		</>
	),
	eye: (
		<>
			<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z" />
			<circle cx="12" cy="12" r="3" />
		</>
	),
	zap: <path d="M13 3L5 13h6l-1 8 8-10h-6z" />,
	star: <path d="M12 3.5l2.6 5.3 5.9.9-4.2 4.1 1 5.9-5.3-2.8-5.3 2.8 1-5.9L4.5 9.7l5.9-.9z" />,
	award: (
		<>
			<circle cx="12" cy="9" r="5" />
			<path d="M8.5 13.5L7 21l5-2.5L17 21l-1.5-7.5" />
		</>
	),
	'chef-hat': (
		<>
			<path d="M7 13a4 4 0 1 1 1.3-7.8A4.5 4.5 0 0 1 17 5.5 4 4 0 1 1 17 13" />
			<path d="M7 13v6h10v-6" />
			<path d="M9 16h6" />
		</>
	),
	package: (
		<>
			<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z" />
			<path d="M4 7.5l8 4.5 8-4.5M12 12v9" />
		</>
	),
	wifi: (
		<>
			<path d="M4 9a13 13 0 0 1 16 0M7 12.5a8 8 0 0 1 10 0M9.5 15.8a4 4 0 0 1 5 0" />
			<path d="M12 19h.01" />
		</>
	),
	battery: (
		<>
			<rect x="3" y="8" width="16" height="9" rx="2" />
			<path d="M21 11v3" />
			<rect x="5" y="10" width="9" height="5" rx="1" fill="currentColor" stroke="none" />
		</>
	),
	signal: (
		<>
			<path d="M5 18v-3M10 18v-6M15 18v-9M20 18V6" />
		</>
	),
};

/** Inline SVG icon. Decorative by default; pass `aria-label` to expose it. */
export const Icon: React.FC<IconProps> = ({ name, size = 20, ...rest }) => {
	const filled = FILLED.has(name);
	return (
		<svg
			{...rest}
			width={size}
			height={size}
			viewBox="0 0 24 24"
			fill={filled ? 'currentColor' : 'none'}
			stroke={filled ? 'none' : 'currentColor'}
			strokeWidth={1.8}
			strokeLinecap="round"
			strokeLinejoin="round"
			focusable="false"
			aria-hidden={rest['aria-label'] ? undefined : true}
		>
			{SHAPES[name]}
		</svg>
	);
};
