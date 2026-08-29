// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React from 'react';
import { cx } from '../../utils/cx';
import styles from './VisionScene.module.css';

export interface VisionSceneProps {
	/** Show the animated scan line + grid (during analysis). */
	scanning?: boolean;
	/** Detection boxes / HUD rendered over the scene. */
	children?: React.ReactNode;
	className?: string;
	caption?: string;
}

/**
 * A stylised "inspection photo" — an abstract commercial-kitchen scene drawn
 * in SVG so the demo needs no binary assets. Detection overlays are layered
 * on top via `children`, positioned in the same 0–1 space.
 */
export const VisionScene: React.FC<VisionSceneProps> = ({
	scanning,
	children,
	className,
	caption,
}) => (
	<div className={cx(styles.frame, className)}>
		<svg
			viewBox="0 0 400 300"
			className={styles.scene}
			preserveAspectRatio="xMidYMid slice"
			aria-hidden="true"
		>
			<defs>
				<linearGradient id="fg-vs-wall" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0%" stopColor="#33507a" />
					<stop offset="100%" stopColor="#22374f" />
				</linearGradient>
				<linearGradient id="fg-vs-counter" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0%" stopColor="#c9d3e0" />
					<stop offset="55%" stopColor="#9aa7b8" />
					<stop offset="100%" stopColor="#7c8a9c" />
				</linearGradient>
				<linearGradient id="fg-vs-floor" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0%" stopColor="#4a5568" />
					<stop offset="100%" stopColor="#2f3948" />
				</linearGradient>
				<radialGradient id="fg-vs-vign" cx="50%" cy="42%" r="72%">
					<stop offset="55%" stopColor="#000000" stopOpacity="0" />
					<stop offset="100%" stopColor="#04070d" stopOpacity="0.55" />
				</radialGradient>
				<filter id="fg-vs-grain">
					<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" />
					<feColorMatrix type="saturate" values="0" />
					<feComponentTransfer>
						<feFuncA type="linear" slope="0.06" />
					</feComponentTransfer>
					<feComposite operator="over" in2="SourceGraphic" />
				</filter>
			</defs>

			{/* room */}
			<rect x="0" y="0" width="400" height="196" fill="url(#fg-vs-wall)" />
			<rect x="0" y="196" width="400" height="104" fill="url(#fg-vs-floor)" />

			{/* floor tile seams (perspective-ish) */}
			<g stroke="#1b232e" strokeOpacity="0.55" strokeWidth="1.5">
				<path d="M0 214 L400 214" />
				<path d="M0 238 L400 238" />
				<path d="M0 268 L400 268" />
				<path d="M70 196 L20 300" />
				<path d="M170 196 L150 300" />
				<path d="M250 196 L270 300" />
				<path d="M340 196 L385 300" />
			</g>

			{/* extraction hood */}
			<path d="M232 0 L392 0 L372 54 L252 54 Z" fill="#2b3d52" />
			<rect x="252" y="54" width="120" height="8" fill="#1f2c3c" />

			{/* wall shelving */}
			<rect x="26" y="44" width="150" height="9" rx="2" fill="#5b6f86" />
			<rect x="26" y="92" width="150" height="9" rx="2" fill="#5b6f86" />
			<g fill="#7d8ea3">
				<rect x="34" y="20" width="18" height="24" rx="2" />
				<rect x="58" y="16" width="14" height="28" rx="2" />
				<rect x="80" y="24" width="20" height="20" rx="2" />
				<rect x="112" y="18" width="16" height="26" rx="2" />
				<rect x="140" y="26" width="22" height="18" rx="2" />
				<rect x="40" y="66" width="16" height="26" rx="2" />
				<rect x="66" y="70" width="22" height="22" rx="2" />
				<rect x="100" y="64" width="14" height="28" rx="2" />
			</g>

			{/* main counter */}
			<rect x="0" y="150" width="400" height="52" fill="url(#fg-vs-counter)" />
			<rect x="0" y="150" width="400" height="6" fill="#e6ecf3" opacity="0.7" />
			<rect x="0" y="198" width="400" height="6" fill="#5b6675" />

			{/* under-counter cabinets */}
			<g fill="#8996a8" stroke="#6a7688" strokeWidth="1.5">
				<rect x="10" y="204" width="70" height="52" rx="3" />
				<rect x="90" y="204" width="70" height="52" rx="3" />
				<rect x="300" y="204" width="70" height="52" rx="3" />
			</g>

			{/* prep items on the counter */}
			<g>
				<rect x="120" y="120" width="46" height="30" rx="3" fill="#d7dde6" stroke="#aab4c2" />
				<rect x="176" y="126" width="30" height="24" rx="3" fill="#cf5b52" />
				<ellipse cx="250" cy="146" rx="26" ry="9" fill="#b9c3d0" />
				<rect x="300" y="118" width="34" height="32" rx="3" fill="#c3ccd8" stroke="#aab4c2" />
			</g>

			{/* a crew figure silhouette */}
			<g fill="#1c2836">
				<circle cx="70" cy="112" r="15" />
				<path d="M48 150 q22 -34 44 0 l-4 40 l-36 0 Z" />
			</g>

			{/* rear service door */}
			<rect x="352" y="96" width="40" height="100" fill="#28384c" stroke="#1c2836" strokeWidth="2" />
			<rect x="352" y="188" width="40" height="5" fill="#e7b64a" opacity="0.85" />

			{/* grain + vignette */}
			<rect x="0" y="0" width="400" height="300" filter="url(#fg-vs-grain)" opacity="0.5" />
			<rect x="0" y="0" width="400" height="300" fill="url(#fg-vs-vign)" />
		</svg>

		{scanning && (
			<>
				<span className={styles.scanGrid} aria-hidden="true" />
				<span className={styles.scanLine} aria-hidden="true" />
			</>
		)}

		<div className={styles.hud}>
			<span className={styles.hudTag}>
				<span className={styles.rec} /> LIVE VISION
			</span>
			{caption && <span className={styles.hudCaption}>{caption}</span>}
		</div>

		<span className={cx(styles.corner, styles.tl)} aria-hidden="true" />
		<span className={cx(styles.corner, styles.tr)} aria-hidden="true" />
		<span className={cx(styles.corner, styles.bl)} aria-hidden="true" />
		<span className={cx(styles.corner, styles.br)} aria-hidden="true" />

		<div className={styles.overlay}>{children}</div>
	</div>
);
