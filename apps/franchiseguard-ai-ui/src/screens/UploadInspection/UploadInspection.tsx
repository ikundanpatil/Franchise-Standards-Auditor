// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

import React, { useMemo, useState } from 'react';
import {
	Button,
	ChecklistGroup,
	LoadingOverlay,
	PageHeader,
	Screen,
	StoreSelector,
	TextArea,
	UploadCard,
} from '../../components';
import { useNav } from '../../app/navigation';
import { useToast } from '../../app/ToastHost';
import { CHECKLIST } from '../../data/checklist';
import { storeById } from '../../data/stores';
import { MANAGER } from '../../data/manager';
import { ANALYZE_STEPS, composeAnalysis } from '../../lib/ai';
import type { Store } from '../../types';
import styles from './UploadInspection.module.css';

export const UploadInspection: React.FC = () => {
	const nav = useNav();
	const { flash } = useToast();

	const [store, setStore] = useState<Store | null>(
		() => storeById(nav.params.storeId ?? 's-204') ?? null,
	);
	const [counts, setCounts] = useState({ camera: 2, gallery: 1, video: 0 });
	const [complaint, setComplaint] = useState(
		'Two guest complaints this week about slow line and a wet floor near the fryer. Please verify prep-zone hygiene.',
	);
	const [checked, setChecked] = useState<Set<string>>(() => new Set(['kitchen', 'hygiene', 'storage']));
	const [analyzing, setAnalyzing] = useState(false);

	const evidenceCount = counts.camera + counts.gallery + counts.video;
	const ready = !!store && evidenceCount > 0;

	const toggle = (id: string) =>
		setChecked((prev) => {
			const next = new Set(prev);
			next.has(id) ? next.delete(id) : next.add(id);
			return next;
		});

	const bump = (k: keyof typeof counts) => {
		setCounts((c) => ({ ...c, [k]: c[k] + 1 }));
		flash(`${k === 'video' ? 'Walk-through' : k === 'camera' ? 'Photo' : 'Image'} added to evidence.`, 'check');
	};

	const focusLabel = useMemo(() => {
		const on = CHECKLIST.filter((c) => checked.has(c.id)).map((c) => c.label);
		return on.length ? `Focus · ${on[0]}${on.length > 1 ? ` +${on.length - 1}` : ''}` : 'Full brand-standard sweep';
	}, [checked]);

	const runAnalysis = () => {
		if (!ready) return;
		setAnalyzing(true);
	};

	const finish = () => {
		if (!store) return;
		const analysis = composeAnalysis(store, focusLabel);
		nav.navigate('analysis', { analysis });
	};

	if (analyzing) {
		return (
			<LoadingOverlay
				steps={ANALYZE_STEPS}
				title="Analyzing Inspection with AI"
				icon="brain"
				stepMs={780}
				onDone={finish}
			/>
		);
	}

	return (
		<Screen
			header={<PageHeader title="New Inspection" icon="camera" onBack={nav.back} />}
			footer={
				<Button variant="primary" size="lg" block icon="sparkles" disabled={!ready} onClick={runAnalysis}>
					Analyze Inspection with AI
				</Button>
			}
		>
			<div className={styles.block}>
				<p className={styles.lede}>
					{MANAGER.name} · {new Date().toLocaleDateString('en-US', { weekday: 'long', day: 'numeric', month: 'long' })}
				</p>
				<StoreSelector value={store} onChange={setStore} />
			</div>

			<div className={styles.block}>
				<h3 className={styles.h}>Evidence</h3>
				<div className={styles.uploads}>
					<UploadCard kind="camera" count={counts.camera} onAdd={() => bump('camera')} />
					<UploadCard kind="gallery" count={counts.gallery} onAdd={() => bump('gallery')} />
					<UploadCard kind="video" count={counts.video} onAdd={() => bump('video')} />
				</div>
				<p className={styles.note}>
					{evidenceCount} item{evidenceCount === 1 ? '' : 's'} attached · AI scores each frame against the Brand
					Standards Manual.
				</p>
			</div>

			<div className={styles.block}>
				<h3 className={styles.h}>Complaint / context</h3>
				<TextArea
					value={complaint}
					max={400}
					onChange={(e) => setComplaint(e.target.value)}
					placeholder="Add guest complaints or anything the model should pay attention to…"
					hint="Optional — feeds the model's attention prompt."
				/>
			</div>

			<div className={styles.block}>
				<h3 className={styles.h}>Checklist</h3>
				<ChecklistGroup checked={checked} onToggle={toggle} />
			</div>
		</Screen>
	);
};
