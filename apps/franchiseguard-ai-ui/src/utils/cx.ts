// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Join truthy class names — a tiny `classnames` stand-in. */
export const cx = (...parts: Array<string | false | null | undefined>): string =>
	parts.filter(Boolean).join(' ');
