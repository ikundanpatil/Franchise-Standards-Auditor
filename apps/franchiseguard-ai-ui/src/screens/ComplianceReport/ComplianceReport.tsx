// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useMemo, useState } from 'react';
import {
	Button,
	Card,
	EvidenceGallery,
	Icon,
	PageHeader,
	ProgressRing,
	RecommendationCard,
	Screen,
	SectionHeader,
	TimelineList,
	ViolationCard,
} from '../../components';
import { useNav } from '../../app/navigation';
import { useToast } from '../../app/ToastHost';
import { reportForStore } from '../../data/reports';
import { longDate, clockTime } from '../../lib/format';
import { SEVERITY_LABEL, SEVERITY_TONE } from '../../utils/risk';
import type { ComplianceReport as Report, Severity } from '../../types';
import styles from './ComplianceReport.module.css';

const ORDER: Severity[] = ['critical', 'major', 'minor'];

export const ComplianceReport: React.FC = () => {
	const nav = useNav();
	const { flash } = useToast();

	const report: Report | null = useMemo(
		() => nav.params.report ?? reportForStore(nav.params.storeId ?? 's-204'),
		[nav.params.report, nav.params.storeId],
	);

	const [expanded, setExpanded] = useState<string | null>(null);

	if (!report) {
		return (
			<Screen header={<PageHeader title="Compliance Report" icon="file-text" onBack={nav.back} />}>
				<Card padding="lg">Report unavailable.</Card>
			</Screen>
		);
	}

	const compliance = Math.max(4, 100 - report.riskScore);

	return (
		<Screen
			header={
				<PageHeader
					title="Compliance Report"
					subtitle={`${report.ref} · ${report.storeName}`}
					icon="file-text"
					onBack={nav.back}
					action={{ icon: 'share', label: 'Share report', onClick: () => flash('Report link copied — sent to franchisee.', 'share') }}
				/>
			}
			footer={
				<div className={styles.actions}>
					<Button variant="ghost" size="lg" icon="share" onClick={() => flash('Shared with the franchise owner + region lead.', 'share')}>
						Share
					</Button>
					<Button variant="primary" size="lg" icon="download" onClick={() => flash('Generating PDF… saved to Reports.', 'download')}>
						Download PDF
					</Button>
				</div>
			}
		>
			<Card padding="lg" className={styles.hero}>
				<ProgressRing value={compliance} label="Compliance" sublabel={`Grade ${report.grade}`} size={128} />
				<div className={styles.heroBody}>
					<span className={styles.heroTag} data-fg-tone={report.risk === 'low' ? 'good' : report.risk === 'medium' ? 'warn' : 'critical'}>
						{report.risk.toUpperCase()} RISK · index {report.riskScore}/100
					</span>
					<p className={styles.heroLine}>{report.summary}</p>
					<p className={styles.heroMeta}>
						<Icon name="user" size={11} /> {report.inspector} · {longDate(report.generatedAt)} {clockTime(report.generatedAt)}
					</p>
				</div>
			</Card>

			<section className={styles.counts}>
				{ORDER.map((s) => (
					<div key={s} className={styles.countCard} data-fg-tone={SEVERITY_TONE[s]}>
						<b>{report.counts[s]}</b>
						<span>{SEVERITY_LABEL[s]}</span>
					</div>
				))}
			</section>

			<div>
				<SectionHeader title="Findings" count={report.detections.length} />
				<div className={styles.list}>
					{report.detections.length ? (
						report.detections.map((d) => (
							<ViolationCard
								key={d.id}
								detection={d}
								expanded={expanded === d.id}
								onToggle={() => setExpanded((c) => (c === d.id ? null : d.id))}
							/>
						))
					) : (
						<Card padding="lg">
							<p className={styles.clean}>
								<Icon name="check-circle" size={16} /> Zero findings this cycle — full pass.
							</p>
						</Card>
					)}
				</div>
			</div>

			<div>
				<SectionHeader title="Evidence" count={report.evidence.length} />
				<EvidenceGallery shots={report.evidence} />
			</div>

			<Card padding="lg">
				<SectionHeader title="Remediation timeline" />
				<TimelineList events={report.timeline} />
			</Card>

			<div>
				<SectionHeader title="Recommendations" count={report.recommendations.length} />
				<div className={styles.list}>
					{report.recommendations.map((rec, i) => (
						<RecommendationCard key={rec.id} rec={rec} style={{ animationDelay: `${i * 55}ms` }} className={styles.rec} />
					))}
				</div>
			</div>

			<div className={styles.followRow}>
				<Button variant="secondary" block icon="refresh" onClick={() => { flash('Re-inspection booked in 72h.', 'calendar'); nav.navigate('alerts'); }}>
					Schedule re-inspection
				</Button>
			</div>
		</Screen>
	);
};
