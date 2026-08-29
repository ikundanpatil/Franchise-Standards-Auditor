// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/**
 * A dependency-free stack navigator. One entry = one screen plus its params;
 * `navigate` pushes, `back` pops, tab taps reset to a tab root. Kept tiny on
 * purpose — the app is a linear demo flow, not a routed site.
 */

import React, {
	createContext,
	useCallback,
	useContext,
	useEffect,
	useMemo,
	useState,
} from 'react';
import { SCREEN_TAB, TAB_ROOT, type NavParams, type ScreenName, type TabId } from './routes';

interface Entry {
	screen: ScreenName;
	params: NavParams;
	/** Direction hint for the page transition. */
	dir: 'forward' | 'back' | 'replace';
	key: number;
}

/**
 * Dev-workflow persistence: the running screen is mirrored to sessionStorage so
 * a hot-reload (or a manual refresh) keeps you on the screen you were testing
 * instead of dropping back to Splash every time you edit a file. It is
 * session-scoped on purpose — a brand-new tab (i.e. the real demo) has no saved
 * entry and still starts at Splash.
 *
 * Escape hatches:
 *   ?fgscreen=<name>  — force-start on a specific screen (e.g. ?fgscreen=report)
 *   ?fgscreen=reset   — ignore any saved state and start clean
 */
const NAV_STORAGE_KEY = 'fg:nav:v1';
const NAV_MAX_AGE_MS = 8 * 60 * 60 * 1000; // don't restore state older than 8h

const VALID_SCREENS = new Set(Object.keys(SCREEN_TAB) as ScreenName[]);
const isScreen = (v: unknown): v is ScreenName =>
	typeof v === 'string' && VALID_SCREENS.has(v as ScreenName);

interface PersistShape {
	screens: Array<{ screen: ScreenName; params: NavParams }>;
	ts: number;
}

function readOverrideScreen(): ScreenName | 'reset' | null {
	try {
		const raw = new URLSearchParams(window.location.search).get('fgscreen');
		if (raw === 'reset') return 'reset';
		return isScreen(raw) ? raw : null;
	} catch {
		return null;
	}
}

function loadSavedStack(): Entry[] | null {
	try {
		const raw = window.sessionStorage.getItem(NAV_STORAGE_KEY);
		if (!raw) return null;
		const parsed = JSON.parse(raw) as PersistShape;
		if (!parsed || !Array.isArray(parsed.screens) || parsed.screens.length === 0) return null;
		if (typeof parsed.ts !== 'number' || Date.now() - parsed.ts > NAV_MAX_AGE_MS) return null;

		const entries: Entry[] = [];
		for (const item of parsed.screens) {
			if (!item || !isScreen(item.screen)) return null;
			entries.push(makeEntry(item.screen, item.params ?? {}, 'replace'));
		}
		return entries;
	} catch {
		return null;
	}
}

function saveStack(stack: Entry[]): void {
	try {
		const payload: PersistShape = {
			screens: stack.map((e) => ({ screen: e.screen, params: e.params })),
			ts: Date.now(),
		};
		window.sessionStorage.setItem(NAV_STORAGE_KEY, JSON.stringify(payload));
	} catch {
		/* storage unavailable / quota / non-serialisable params — fine, skip */
	}
}

function initialStack(initial: ScreenName): Entry[] {
	if (typeof window === 'undefined') return [makeEntry(initial, {}, 'replace')];

	const override = readOverrideScreen();
	if (override === 'reset') {
		try {
			window.sessionStorage.removeItem(NAV_STORAGE_KEY);
		} catch {
			/* ignore */
		}
		return [makeEntry(initial, {}, 'replace')];
	}
	if (override) return [makeEntry(override, {}, 'replace')];

	return loadSavedStack() ?? [makeEntry(initial, {}, 'replace')];
}

interface NavApi {
	screen: ScreenName;
	params: NavParams;
	dir: Entry['dir'];
	entryKey: number;
	depth: number;
	activeTab: TabId | null;
	canGoBack: boolean;
	navigate: (screen: ScreenName, params?: NavParams) => void;
	replace: (screen: ScreenName, params?: NavParams) => void;
	back: () => void;
	switchTab: (tab: TabId) => void;
	reset: (screen: ScreenName, params?: NavParams) => void;
}

const NavContext = createContext<NavApi | null>(null);

let seq = 1;
const makeEntry = (screen: ScreenName, params: NavParams, dir: Entry['dir']): Entry => ({
	screen,
	params,
	dir,
	key: seq++,
});

export const NavProvider: React.FC<{ initial?: ScreenName; children: React.ReactNode }> = ({
	initial = 'splash',
	children,
}) => {
	const [stack, setStack] = useState<Entry[]>(() => initialStack(initial));

	// Mirror the current screen to sessionStorage so a dev hot-reload keeps you
	// on the screen you were testing instead of resetting to Splash.
	useEffect(() => {
		saveStack(stack);
	}, [stack]);

	const navigate = useCallback((screen: ScreenName, params: NavParams = {}) => {
		setStack((prev) => [...prev, makeEntry(screen, params, 'forward')]);
	}, []);

	const replace = useCallback((screen: ScreenName, params: NavParams = {}) => {
		setStack((prev) => [...prev.slice(0, -1), makeEntry(screen, params, 'replace')]);
	}, []);

	const back = useCallback(() => {
		setStack((prev) => {
			if (prev.length <= 1) return prev;
			const next = prev.slice(0, -1);
			const top = next[next.length - 1];
			next[next.length - 1] = { ...top, dir: 'back', key: seq++ };
			return next;
		});
	}, []);

	const reset = useCallback((screen: ScreenName, params: NavParams = {}) => {
		setStack([makeEntry(screen, params, 'replace')]);
	}, []);

	const switchTab = useCallback((tab: TabId) => {
		setStack((prev) => {
			const current = prev[prev.length - 1];
			const root = TAB_ROOT[tab];
			if (current.screen === root && prev.length === 1) return prev;
			return [makeEntry(root, {}, 'replace')];
		});
	}, []);

	const top = stack[stack.length - 1];

	const value = useMemo<NavApi>(
		() => ({
			screen: top.screen,
			params: top.params,
			dir: top.dir,
			entryKey: top.key,
			depth: stack.length,
			activeTab: SCREEN_TAB[top.screen],
			canGoBack: stack.length > 1,
			navigate,
			replace,
			back,
			switchTab,
			reset,
		}),
		[top, stack.length, navigate, replace, back, switchTab, reset],
	);

	return <NavContext.Provider value={value}>{children}</NavContext.Provider>;
};

export function useNav(): NavApi {
	const ctx = useContext(NavContext);
	if (!ctx) throw new Error('useNav must be used inside <NavProvider>');
	return ctx;
}
