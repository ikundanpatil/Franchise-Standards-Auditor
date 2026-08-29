// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useMemo, useRef, useState } from 'react';
import {
	Button,
	Card,
	DetectionOverlay,
	Icon,
	LoadingOverlay,
	PageHeader,
	RiskMeter,
	Screen,
	SeverityChip,
	VisionScene,
	ViolationCard,
} from '../../components';
import { useNav } from '../../app/navigation';
import { composeAnalysis, composeReport, REPORT_STEPS } from '../../lib/ai';
import { MANAGER } from '../../data/manager';
import { storeById, STORES } from '../../data/stores';
import type { AnalysisResult, Severity } from '../../types';
import styles from './AiAnalysis.module.css';

export const AiAnalysis: React.FC = () => {
	const nav = useNav();

	const analysis: AnalysisResult = useMemo(
		() => nav.params.analysis ?? composeAnalysis(storeById('s-204') ?? STORES[1]),
		[nav.params.analysis],
	);

	const [activeId, setActiveId] = useState<string | null>(null);
	const [expandedId, setExpandedId] = useState<string | null>(analysis.detections[0]?.id ?? null);
	const [generating, setGenerating] = useState(false);
	const startedAt = useRef(Date.now());

	const counts = useMemo(() => {
		const c: Record<Severity, number> = { minor: 0, major: 0, critical: 0 };
		analysis.detections.forEach((d) => {
			c[d.severity] += 1;
		});
		return c;
	}, [analysis]);

	const select = (id: string) => {
		setActiveId((cur) => (cur === id ? null : id));
		setExpandedId(id);
	};

	if (generating) {
		return (
			<LoadingOverlay
				steps={REPORT_STEPS}
				title="Generating Compliance Report"
				icon="file-text"
				stepMs={720}
				onDone={() => {
					const store = storeById(analysis.storeId) ?? STORES[1];
					nav.navigate('report', { report: composeReport(analysis, store, MANAGER.name) });
				}}
			/>
		);
	}

	const elapsed = ((Date.now() - startedAt.current) / 1000 + 18).toFixed(1);

	return (
		<Screen
			header={
				<PageHeader
					title="AI Analysis"
					subtitle={`${analysis.storeName} · ${analysis.storeCode} · ${analysis.modelVersion}`}
					icon="brain"
					onBack={nav.back}
				/>
			}
			footer={
				<Button variant="primary" size="lg" block icon="file-text" onClick={() => setGenerating(true)}>
					Generate Compliance Report
				</Button>
			}
		>
			<div className={styles.visionWrap}>
				<VisionScene caption={analysis.imageLabel}>
					<DetectionOverlay detections={analysis.detections} activeId={activeId} onSelect={select} />
				</VisionScene>
				<div className={styles.frameMeta}>
					<span>
						<Icon name="layers" size={12} /> {analysis.frameCount} frame
						{analysis.frameCount > 1 ? 's' : ''}
					</span>
					<span>
						<Icon name="eye" size={12} /> {analysis.detections.length} detections
					</span>
					<span>
						<Icon name="clock" size={12} /> {elapsed}s
					</span>
				</div>
			</div>

			<Card padding="lg" className={styles.summaryCard}>
				<p className={styles.headline}>{analysis.headline}</p>
				<div className={styles.chips}>
					{(['critical', 'major', 'minor'] as Severity[]).map((s) =>
						counts[s] ? (
							<span key={s} className={styles.chipCount}>
								<SeverityChip severity={s} />
								<b>{counts[s]}</b>
							</span>
						) : null,
					)}
					{!analysis.detections.length && <SeverityChip severity="minor" />}
				</div>
				<RiskMeter score={analysis.riskScore} className={styles.meter} />
				<p className={styles.narrative}>{analysis.narrative}</p>
			</Card>

			<section className={styles.violations}>
				<h3 className={styles.h}>
					Detected violations
					<span className={styles.hint}>tap a card to highlight it on the frame</span>
				</h3>
				{analysis.detections.length ? (
					analysis.detections.map((d, i) => (
						<ViolationCard
							key={d.id}
							detection={d}
							active={activeId === d.id}
							expanded={expandedId === d.id}
							onToggle={() => select(d.id)}
							className={styles.vcard}
							style={{ animationDelay: `${i * 60}ms` }}
						/>
					))
				) : (
					<Card padding="lg">
						<p className={styles.clean}>
							<Icon name="check-circle" size={18} /> No violations detected — {analysis.storeName} is within
							brand standard on every checked area.
						</p>
					</Card>
				)}
			</section>
		</Screen>
	);
};
