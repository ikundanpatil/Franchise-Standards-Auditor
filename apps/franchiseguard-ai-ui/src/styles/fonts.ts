// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/**
 * Lazily attach the brand webfonts (Sora + IBM Plex) once per document.
 * If the request is blocked or offline the CSS fallback stacks in
 * `tokens.css` take over, so this is purely an enhancement.
 */
const LINK_ID = 'fg-webfonts';
const HREF =
	'https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Sora:wght@400;500;600;700&display=swap';

export function ensureFonts(): void {
	if (typeof document === 'undefined') return;
	if (document.getElementById(LINK_ID)) return;

	const link = document.createElement('link');
	link.id = LINK_ID;
	link.rel = 'stylesheet';
	link.href = HREF;
	document.head.appendChild(link);
}
