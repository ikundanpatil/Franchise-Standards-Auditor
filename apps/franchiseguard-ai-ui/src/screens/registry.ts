// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Screen name → component. Consumed by the app shell. */

import type React from 'react';
import type { ScreenName } from '../app/routes';
import { Splash } from './Splash/Splash';
import { Login } from './Login/Login';
import { HomeDashboard } from './HomeDashboard/HomeDashboard';
import { Inspections } from './Inspections/Inspections';
import { UploadInspection } from './UploadInspection/UploadInspection';
import { AiAnalysis } from './AiAnalysis/AiAnalysis';
import { ComplianceReport } from './ComplianceReport/ComplianceReport';
import { LocationMemory } from './LocationMemory/LocationMemory';
import { ManagerAlerts } from './ManagerAlerts/ManagerAlerts';
import { Reports } from './Reports/Reports';
import { Profile } from './Profile/Profile';

export interface ScreenProps {
	managerName: string;
}

export const SCREENS: Record<ScreenName, React.FC<ScreenProps>> = {
	splash: Splash,
	login: Login,
	home: HomeDashboard,
	inspections: Inspections,
	upload: UploadInspection,
	analysis: AiAnalysis,
	report: ComplianceReport,
	memory: LocationMemory,
	alerts: ManagerAlerts,
	reports: Reports,
	profile: Profile,
};
