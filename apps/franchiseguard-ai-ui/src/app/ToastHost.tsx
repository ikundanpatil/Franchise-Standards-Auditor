// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** App-wide transient status pill. `useToast().flash('…')` from anywhere. */

import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { Icon } from '../components/Icon/Icon';
import type { IconName } from '../types';
import styles from './ToastHost.module.css';

interface ToastPayload {
	message: string;
	icon: IconName;
	key: number;
}

interface ToastApi {
	flash: (message: string, icon?: IconName) => void;
}

const ToastContext = createContext<ToastApi | null>(null);
const VISIBLE_MS = 2400;

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
	const [toast, setToast] = useState<ToastPayload | null>(null);
	const [shown, setShown] = useState(false);
	const hideTimer = useRef<ReturnType<typeof setTimeout>>();
	const clearTimer = useRef<ReturnType<typeof setTimeout>>();
	const seq = useRef(0);

	const flash = useCallback((message: string, icon: IconName = 'sparkle') => {
		seq.current += 1;
		clearTimeout(hideTimer.current);
		clearTimeout(clearTimer.current);
		setToast({ message, icon, key: seq.current });
		setShown(true);
		hideTimer.current = setTimeout(() => setShown(false), VISIBLE_MS);
		clearTimer.current = setTimeout(() => setToast(null), VISIBLE_MS + 400);
	}, []);

	useEffect(
		() => () => {
			clearTimeout(hideTimer.current);
			clearTimeout(clearTimer.current);
		},
		[],
	);

	return (
		<ToastContext.Provider value={{ flash }}>
			{children}
			<div className={styles.layer} aria-live="polite" role="status">
				{toast && (
					<div className={`${styles.toast} ${shown ? styles.show : ''}`} key={toast.key}>
						<Icon name={toast.icon} size={14} />
						<span>{toast.message}</span>
					</div>
				)}
			</div>
		</ToastContext.Provider>
	);
};

export function useToast(): ToastApi {
	const ctx = useContext(ToastContext);
	if (!ctx) throw new Error('useToast must be used inside <ToastProvider>');
	return ctx;
}
